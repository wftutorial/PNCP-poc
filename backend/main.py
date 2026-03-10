# DEBT-101 AC3: faulthandler disabled in production to allow uvloop (uvicorn[standard]).
# faulthandler + uvloop caused SIGSEGV crash loops on Railway Linux (CRIT-SIGSEGV).
# In production, Sentry + gunicorn worker_exit hooks provide equivalent crash diagnostics.
# In development/test, faulthandler remains enabled for local debugging.
import os as _os_early
_env_early = _os_early.getenv("ENVIRONMENT", _os_early.getenv("ENV", "development")).lower()
if _env_early not in ("production", "prod"):
    import faulthandler
    faulthandler.enable()

"""SmartLic - Backend API — App factory pattern (DEBT-107)

Decomposed to <100 lines. Extracted to:
  - startup/sentry.py            (PII scrubbing, noise filtering, init)
  - startup/lifespan.py          (startup/shutdown orchestration)
  - startup/state.py             (shared process state)
  - startup/app_factory.py       (FastAPI app factory — create_app())
  - startup/middleware_setup.py  (CORS, custom & inline HTTP middlewares, /metrics)
  - startup/routes.py            (router imports & registration)
  - startup/exception_handlers.py (validation + global exception handlers)
  - startup/endpoints.py         (/, /v1/setores)
  - routes/health_core.py        (health/live, health/ready, health, sources/health)

SYS-036: OpenAPI docs enabled in production, protected by DOCS_ACCESS_TOKEN.
CROSS-003: Feature flags admin API at /v1/admin/feature-flags.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from startup.app_factory import create_app

app = create_app()

# /debug/pncp-test kept here so tests can monkeypatch ``main.PNCPClient`` (DEBT-015).
from pncp_client import PNCPClient  # noqa: E402 — intentional late import for monkeypatching
from fastapi import Depends
from schemas import DebugPNCPResponse
from admin import require_admin as _require_admin


@app.get("/debug/pncp-test", response_model=DebugPNCPResponse)
async def debug_pncp_test(admin: dict = Depends(_require_admin)):
    """Diagnostic: test if PNCP API is reachable. Admin only."""
    import time as t
    import asyncio as _asyncio
    from datetime import date, timedelta

    start = t.time()
    try:
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
        return {"success": True, "total_registros": response.get("totalRegistros", 0),
                "items_returned": len(response.get("data", [])), "elapsed_ms": elapsed}
    except Exception as e:
        elapsed = int((t.time() - start) * 1000)
        return {"success": False, "error": str(e), "error_type": type(e).__name__, "elapsed_ms": elapsed}


# ============================================================================
# Backward-compatible re-exports for test imports (DEBT-015)
# ============================================================================
from startup.sentry import _before_send, scrub_pii, _fingerprint_transients, _traces_sampler  # noqa: F401
from startup.lifespan import (  # noqa: F401
    _check_cache_schema, _log_registered_routes, _mark_inflight_sessions_timed_out,
    _periodic_saturation_metrics, _SATURATION_INTERVAL,
)
from startup.state import startup_time as _startup_time, process_start_time as _process_start_time  # noqa: F401
from routes.health_core import _READINESS_REDIS_TIMEOUT_S, _READINESS_SUPABASE_TIMEOUT_S  # noqa: F401
