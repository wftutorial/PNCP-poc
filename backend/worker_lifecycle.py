"""CRIT-034: Worker timeout tracking and structured logging.

Tracks the active request in each gunicorn/uvicorn worker process and installs
a SIGABRT signal handler to capture structured diagnostics when the gunicorn
arbiter kills a worker that exceeded its timeout.

Process-global dict `_active_request` is updated by CorrelationIDMiddleware
on every request start/end. The SIGABRT handler reads it on timeout.

Usage:
    # In gunicorn.conf.py post_worker_init hook:
    from worker_lifecycle import install_timeout_handler
    install_timeout_handler(worker.pid)

    # In middleware (automatic via CorrelationIDMiddleware):
    from worker_lifecycle import set_active_request, clear_active_request
    set_active_request("/v1/buscar", "search-123")
    # ... handle request ...
    clear_active_request()
"""

import logging
import os
import signal
import sys
import time

logger = logging.getLogger(__name__)

# Process-global: tracks the current active request in this worker.
# Updated by CorrelationIDMiddleware on every request start/end.
# Read by the SIGABRT handler when gunicorn kills the worker.
_active_request: dict = {}


def set_active_request(endpoint: str, search_id: str | None = None) -> None:
    """Record the current active request for timeout diagnostics."""
    _active_request["endpoint"] = endpoint
    _active_request["search_id"] = search_id or "-"
    _active_request["start_time"] = time.time()
    _active_request["pid"] = os.getpid()


def clear_active_request() -> None:
    """Clear the active request tracking after request completes."""
    _active_request.clear()


def get_active_request() -> dict:
    """Return a copy of the active request info (for testing/inspection)."""
    return _active_request.copy()


def build_timeout_info(worker_pid: int) -> dict:
    """Build structured timeout diagnostic data from current active request.

    Extracted as a standalone function for testability (signal handlers
    are hard to unit-test directly).
    """
    start = _active_request.get("start_time")
    return {
        "worker_pid": worker_pid,
        "request_duration_s": round(time.time() - start, 2) if start else -1,
        "endpoint": _active_request.get("endpoint", "idle"),
        "search_id": _active_request.get("search_id", "-"),
    }


def install_timeout_handler(worker_pid: int) -> None:
    """Install SIGABRT handler for structured timeout logging.

    Called by gunicorn post_worker_init hook. Only works on Unix (Linux/Mac).
    Gracefully skips on Windows since gunicorn is Linux-only in production.

    The handler:
    1. Logs structured data (AC7): worker_pid, duration, endpoint, search_id
    2. Increments Prometheus metric (AC6): WORKER_TIMEOUT counter
    3. Captures to Sentry (AC5): with request context tags
    4. Re-raises SIGABRT with default handler (process termination)
    """
    if sys.platform == "win32":
        logger.debug("CRIT-034: Skipping SIGABRT handler on Windows")
        return

    def _handle_sigabrt(signum, frame):
        """Log structured timeout info and re-raise SIGABRT."""
        info = build_timeout_info(worker_pid)

        # AC7: Structured log with all required fields
        logger.critical(
            "WORKER KILLED BY TIMEOUT | "
            f"pid={info['worker_pid']} "
            f"duration={info['request_duration_s']}s "
            f"endpoint={info['endpoint']} "
            f"search_id={info['search_id']}"
        )

        # AC6: Increment Prometheus metric
        try:
            from metrics import WORKER_TIMEOUT
            WORKER_TIMEOUT.labels(reason="gunicorn_timeout").inc()
        except Exception:
            pass

        # AC5: Capture to Sentry with request context
        try:
            import sentry_sdk
            with sentry_sdk.new_scope() as scope:
                scope.set_tag("worker.pid", str(worker_pid))
                scope.set_tag("endpoint", info["endpoint"])
                scope.set_tag("search_id", info["search_id"])
                scope.set_extra("request_duration_s", info["request_duration_s"])
                scope.set_level("fatal")
                sentry_sdk.capture_message(
                    f"WORKER TIMEOUT (pid:{worker_pid}) on {info['endpoint']}",
                )
        except Exception:
            pass

        # Re-raise default SIGABRT behavior (process termination)
        signal.signal(signal.SIGABRT, signal.SIG_DFL)
        os.abort()

    signal.signal(signal.SIGABRT, _handle_sigabrt)
    logger.info(f"CRIT-034: SIGABRT timeout handler installed (pid={worker_pid})")
