# CRIT-SIGSEGV: Enable faulthandler BEFORE any imports.
# Prints Python-level traceback to stderr on SIGSEGV/SIGFPE/SIGABRT,
# giving visibility into which C extension is crashing.
import faulthandler
faulthandler.enable()

"""
SmartLic - Backend API

FastAPI application entry point.  All initialization logic lives in the
``startup/`` package; this module is intentionally thin so that
``uvicorn main:app`` and ``from main import app`` keep working.

SYS-020: Completed startup/ module extraction — main.py < 200 LOC.
"""

from dotenv import load_dotenv
load_dotenv()

from startup.app_factory import create_app  # noqa: E402

# The one and only FastAPI instance — referenced by uvicorn, gunicorn, and tests.
app = create_app()


# DEBT-SYS-012: Backward-compat shims removed. Tests now import from correct modules:
#   - startup.state (startup_time, process_start_time)
#   - startup.middleware_setup (track_legacy_routes, _ALLOWED_ROOT_PATHS)
#   - startup.lifespan (_check_cache_schema, _mark_inflight_sessions_timed_out, etc.)
