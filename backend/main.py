# CRIT-SIGSEGV: Enable faulthandler BEFORE any imports.
import faulthandler
faulthandler.enable()

"""SmartLic - Backend API

DEBT-015 SYS-005: Decomposed to <300 lines. Extracted to:
  - startup/sentry.py (PII scrubbing, noise filtering, init)
  - startup/lifespan.py (startup/shutdown orchestration)
  - startup/state.py (shared process state)
  - routes/health_core.py (health/live, health/ready, health, sources/health)

SYS-036: OpenAPI docs enabled in production, protected by DOCS_ACCESS_TOKEN.
CROSS-003: Feature flags admin API at /v1/admin/feature-flags.
"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import setup_logging, ENABLE_NEW_PRICING, get_cors_origins, log_feature_flags, METRICS_TOKEN
from pncp_client import PNCPClient
from sectors import list_sectors
from schemas import RootResponse, SetoresResponse, DebugPNCPResponse
from middleware import CorrelationIDMiddleware, SecurityHeadersMiddleware, DeprecationMiddleware, RateLimitMiddleware
import startup.state as _state

# Routers
from admin import router as admin_router
from routes.subscriptions import router as subscriptions_router
from routes.features import router as features_router
from routes.messages import router as messages_router
from routes.analytics import router as analytics_router
from routes.auth_oauth import router as oauth_router
from routes.export_sheets import router as export_sheets_router
from webhooks.stripe import router as stripe_webhook_router
from routes.search import router as search_router
from routes.user import router as user_router
from routes.billing import router as billing_router
from routes.sessions import router as sessions_router
from routes.plans import router as plans_router
from routes.emails import router as emails_router
from routes.pipeline import router as pipeline_router
from routes.onboarding import router as onboarding_router
from routes.auth_email import router as auth_email_router
from routes.health import router as cache_health_router
from routes.health_core import router as health_core_router
from routes.feedback import router as feedback_router
from routes.admin_trace import router as admin_trace_router
from routes.auth_check import router as auth_check_router
from routes.bid_analysis import router as bid_analysis_router
from routes.slo import router as slo_router
from routes.alerts import router as alerts_router
from routes.trial_emails import router as trial_emails_router
from routes.mfa import router as mfa_router
from routes.organizations import router as org_router
from routes.partners import router as partners_router
from routes.sectors_public import router as sectors_public_router
from routes.reports import router as reports_router
from routes.blog_stats import router as blog_stats_router
from routes.metrics_api import router as metrics_api_router
from routes.feature_flags import router as feature_flags_router

# Configure logging
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
log_feature_flags()

# Sentry initialization
_env = os.getenv("ENVIRONMENT", os.getenv("ENV", "development")).lower()
_is_production = _env in ("production", "prod")
APP_VERSION = os.getenv("APP_VERSION", "dev")

from startup.sentry import init_sentry
init_sentry(env=_env, version=APP_VERSION)

# OTel tracing — before app creation
from telemetry import init_tracing as _init_tracing
_init_tracing()

# Lifespan
from startup.lifespan import lifespan

# SYS-036: DOCS_ACCESS_TOKEN — when set, protects /docs and /redoc in production
DOCS_ACCESS_TOKEN = os.getenv("DOCS_ACCESS_TOKEN", "")

# SYS-036: Always expose OpenAPI endpoints (protected by middleware in production)
app = FastAPI(
    title="SmartLic API",
    description=(
        "API para busca e analise de licitacoes em fontes oficiais brasileiras.\n\n"
        "## Data Sources\n"
        "- **PNCP** (Portal Nacional de Contratacoes Publicas) - primary\n"
        "- **PCP v2** (Portal de Compras Publicas) - secondary\n"
        "- **ComprasGov v3** (Dados Abertos de Compras Governamentais) - tertiary\n\n"
        "## Authentication\n"
        "All endpoints require a Supabase JWT Bearer token unless noted otherwise.\n\n"
        "## Contact\n"
        "CONFENGE Avaliacoes e Inteligencia Artificial LTDA\n"
        "- Website: https://smartlic.tech\n"
        "- Email: suporte@smartlic.tech"
    ),
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "search", "description": "Multi-source procurement search with AI classification"},
        {"name": "pipeline", "description": "Opportunity pipeline (kanban board)"},
        {"name": "billing", "description": "Stripe billing, subscriptions, and plan management"},
        {"name": "admin", "description": "Admin-only user management and system operations"},
        {"name": "feature-flags", "description": "Runtime feature flag management (admin only)"},
        {"name": "analytics", "description": "Usage analytics and dashboards"},
        {"name": "health", "description": "Health checks and readiness probes"},
    ],
)

# CORS
cors_origins = get_cors_origins()
logger.info(f"CORS configured for origins: {cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With", "X-Request-ID"],
)
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(DeprecationMiddleware)
app.add_middleware(RateLimitMiddleware)


# ============================================================================
# SYS-036: Protect /docs and /redoc with DOCS_ACCESS_TOKEN in production
# ============================================================================
# /openapi.json is also gated because Swagger UI fetches it automatically.
# If DOCS_ACCESS_TOKEN is not set, docs are open (development default).
_DOCS_PATHS = frozenset({"/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"})


@app.middleware("http")
async def docs_access_guard(request: Request, call_next):
    """SYS-036: Gate OpenAPI docs behind DOCS_ACCESS_TOKEN bearer in production."""
    path = request.url.path
    if path in _DOCS_PATHS and DOCS_ACCESS_TOKEN:
        # Allow access via Bearer token in Authorization header
        auth_header = request.headers.get("Authorization", "")
        # Also allow via ?token= query param (convenient for browser access)
        query_token = request.query_params.get("token", "")

        if auth_header == f"Bearer {DOCS_ACCESS_TOKEN}" or query_token == DOCS_ACCESS_TOKEN:
            return await call_next(request)

        return JSONResponse(
            status_code=401,
            content={"detail": "API docs access requires DOCS_ACCESS_TOKEN. Use Authorization: Bearer <token> header or ?token=<token> query param."},
        )
    return await call_next(request)


# HTTP response counter middleware
@app.middleware("http")
async def http_response_counter(request, call_next):
    """STORY-299 AC2: Track HTTP responses for SLO availability metric."""
    response = await call_next(request)
    path = request.url.path
    if not path.startswith("/metrics") and not path.startswith("/health"):
        try:
            from metrics import HTTP_RESPONSES_TOTAL
            status_class = f"{response.status_code // 100}xx"
            HTTP_RESPONSES_TOTAL.labels(status_class=status_class, method=request.method).inc()
        except Exception:
            pass
    return response


# OTel instrumentation — after all middleware
from telemetry import instrument_fastapi_app
instrument_fastapi_app(app)

# ============================================================================
# Router registration
# ============================================================================
# Health core at root (not /v1/) for container probes
app.include_router(health_core_router)

# All API routers at /v1/
_v1_routers = [
    admin_router, subscriptions_router, features_router, messages_router,
    analytics_router, oauth_router, export_sheets_router, stripe_webhook_router,
    search_router, user_router, billing_router, sessions_router, plans_router,
    emails_router, pipeline_router, onboarding_router, auth_email_router,
    cache_health_router, feedback_router, auth_check_router, bid_analysis_router,
    alerts_router, trial_emails_router, mfa_router, org_router, partners_router,
    sectors_public_router, reports_router, blog_stats_router, metrics_api_router,
    feature_flags_router,
]
for r in _v1_routers:
    app.include_router(r, prefix="/v1")

# Self-prefixed routers
app.include_router(admin_trace_router)
app.include_router(slo_router)

# Stripe webhook at root (callback URL already configured)
app.include_router(stripe_webhook_router)

# TD-004: Legacy route tracking
_ALLOWED_ROOT_PATHS = frozenset({
    "/", "/health", "/health/live", "/health/ready", "/sources/health",
    "/docs", "/redoc", "/openapi.json", "/metrics",
    "/debug/pncp-test", "/v1/setores",
})


@app.middleware("http")
async def track_legacy_routes(request: Request, call_next):
    """TD-004 AC4: Track calls to removed legacy (non-/v1/) routes."""
    path = request.url.path
    if (
        not path.startswith("/v1/")
        and not path.startswith("/metrics")
        and not path.startswith("/webhooks/")
        and path not in _ALLOWED_ROOT_PATHS
    ):
        try:
            from metrics import LEGACY_ROUTE_CALLS
            segments = path.strip("/").split("/")[:2]
            truncated = "/" + "/".join(segments)
            LEGACY_ROUTE_CALLS.labels(method=request.method, path=truncated).inc()
        except Exception:
            pass
    return await call_next(request)


# ============================================================================
# Exception handlers
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """AC9: Validation errors in Portuguese."""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(status_code=422, content={"detail": "Dados inválidos. Verifique os campos e tente novamente."})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """STORY-300 AC5-AC7: Catch-all — NEVER returns stack traces."""
    import sentry_sdk
    from middleware import correlation_id_var, request_id_var

    error_msg = str(exc).lower()
    corr_id = correlation_id_var.get("-")
    req_id = request_id_var.get("-")

    if "rls" in error_msg or "row-level security" in error_msg or ("policy" in error_msg and "permission" in error_msg):
        logger.error(f"RLS error on {request.url.path}: {exc}")
        sentry_sdk.capture_exception(exc)
        return JSONResponse(status_code=403, content={"detail": "Erro de permissão. Faça login novamente.", "correlation_id": corr_id})

    if "stripe" in error_msg or "stripeerror" in type(exc).__name__.lower():
        logger.error(f"Unhandled Stripe error on {request.url.path}: {exc}")
        sentry_sdk.capture_exception(exc)
        return JSONResponse(status_code=500, content={"detail": "Erro ao processar pagamento. Tente novamente.", "correlation_id": corr_id})

    logger.exception(f"Unhandled error on {request.url.path}")
    sentry_sdk.capture_exception(exc)
    return JSONResponse(status_code=500, content={"detail": "Erro interno do servidor. Tente novamente.", "correlation_id": corr_id, "request_id": req_id})


# ============================================================================
# Prometheus metrics endpoint
# ============================================================================
from metrics import get_metrics_app

_metrics_app = get_metrics_app()
if _metrics_app:
    from starlette.responses import JSONResponse as StarletteJSONResponse

    @app.middleware("http")
    async def metrics_auth(request, call_next):
        """Protect /metrics with Bearer token."""
        if request.url.path == "/metrics" or request.url.path.startswith("/metrics/"):
            if METRICS_TOKEN:
                token = request.headers.get("Authorization", "")
                if token != f"Bearer {METRICS_TOKEN}":
                    return StarletteJSONResponse(status_code=401, content={"detail": "Unauthorized"})
        return await call_next(request)

    app.mount("/metrics", _metrics_app)
    logger.info("Prometheus /metrics endpoint mounted (auth=%s)", "enabled" if METRICS_TOKEN else "open")

logger.info(
    "FastAPI application initialized — PORT=%s, docs=%s",
    os.getenv("PORT", "8000"),
    "protected" if DOCS_ACCESS_TOKEN else "open",
)

@app.get("/", response_model=RootResponse)
async def root():
    """API root — navigation and version info."""
    return {"name": "SmartLic API", "version": APP_VERSION, "api_version": "v1",
            "description": "API para busca e análise de licitações em fontes oficiais",
            "endpoints": {"docs": "/docs", "redoc": "/redoc", "health": "/health", "openapi": "/openapi.json", "v1_api": "/v1"},
            "versioning": {"current": "v1", "supported": ["v1"], "deprecated": [], "note": "All endpoints at /v1/<endpoint>. Legacy root paths removed (TD-004)."},
            "status": "operational"}


@app.get("/v1/setores", response_model=SetoresResponse)
async def listar_setores():
    """Return available procurement sectors for frontend dropdown."""
    return {"setores": list_sectors()}


# Backward-compatible re-exports for test imports (DEBT-015)
from startup.sentry import _before_send, scrub_pii, _fingerprint_transients, _traces_sampler  # noqa: F401
from startup.lifespan import (  # noqa: F401
    _check_cache_schema, _log_registered_routes, _mark_inflight_sessions_timed_out,
    _periodic_saturation_metrics, _SATURATION_INTERVAL,
)
from startup.state import startup_time as _startup_time, process_start_time as _process_start_time  # noqa: F401
from routes.health_core import _READINESS_REDIS_TIMEOUT_S, _READINESS_SUPABASE_TIMEOUT_S  # noqa: F401

from admin import require_admin as _require_admin


@app.get("/debug/pncp-test", response_model=DebugPNCPResponse)
async def debug_pncp_test(admin: dict = Depends(_require_admin)):
    """Diagnostic: test if PNCP API is reachable. Admin only."""
    import time as t
    from datetime import date, timedelta

    start = t.time()
    try:
        import asyncio as _asyncio
        client = PNCPClient()
        hoje = date.today()
        tres_dias = hoje - timedelta(days=3)
        response = await _asyncio.to_thread(
            client.fetch_page,
            data_inicial=tres_dias.strftime("%Y-%m-%d"),
            data_final=hoje.strftime("%Y-%m-%d"),
            modalidade=6, pagina=1, tamanho=10,
        )
        elapsed = int((t.time() - start) * 1000)
        return {"success": True, "total_registros": response.get("totalRegistros", 0), "items_returned": len(response.get("data", [])), "elapsed_ms": elapsed}
    except Exception as e:
        elapsed = int((t.time() - start) * 1000)
        return {"success": False, "error": str(e), "error_type": type(e).__name__, "elapsed_ms": elapsed}
