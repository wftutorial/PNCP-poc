"""startup/app_factory.py — FastAPI app factory (DEBT-107).

Single entry point: call create_app() to get a fully-configured FastAPI instance.
"""

import logging
import os

from fastapi import FastAPI

from config import setup_logging, log_feature_flags
from startup.sentry import init_sentry
from startup.lifespan import lifespan
from startup.middleware_setup import setup_middleware, setup_metrics_endpoint, DOCS_ACCESS_TOKEN
from startup.routes import register_routes
from startup.exception_handlers import register_exception_handlers
from startup.endpoints import register_endpoints, APP_VERSION

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Build and return the configured SmartLic FastAPI application."""
    # Logging
    setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
    log_feature_flags()

    # Sentry
    _env = os.getenv("ENVIRONMENT", os.getenv("ENV", "development")).lower()
    init_sentry(env=_env, version=APP_VERSION)

    # OTel tracing — before app creation
    from telemetry import init_tracing as _init_tracing
    _init_tracing()

    # FastAPI instance
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

    # Middleware (CORS, custom, inline HTTP middlewares)
    setup_middleware(app)

    # Routes
    register_routes(app)

    # OTel instrumentation — after all middleware
    from telemetry import instrument_fastapi_app
    instrument_fastapi_app(app)

    # Exception handlers
    register_exception_handlers(app)

    # Root endpoints (/, /v1/setores, /debug/pncp-test)
    register_endpoints(app)

    # Prometheus /metrics (conditional)
    setup_metrics_endpoint(app)

    logger.info(
        "FastAPI application initialized — PORT=%s, docs=%s",
        os.getenv("PORT", "8000"),
        "protected" if DOCS_ACCESS_TOKEN else "open",
    )

    return app
