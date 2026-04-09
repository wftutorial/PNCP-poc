"""CRIT-052/056: Thread-safe global PNCP cron canary status."""

import logging
import threading
import time as _time_mod

logger = logging.getLogger(__name__)

_pncp_cron_status_lock = threading.Lock()
_pncp_cron_status: dict = {"status": "unknown", "latency_ms": None, "updated_at": None}

# CRIT-056 AC4: Recovery epoch — increments on degraded/down -> healthy transition.
_pncp_recovery_epoch: int = 0


def get_pncp_cron_status() -> dict:
    """Return last known PNCP status from cron canary (CRIT-052 AC3)."""
    with _pncp_cron_status_lock:
        return dict(_pncp_cron_status)


def get_pncp_recovery_epoch() -> int:
    """CRIT-056 AC4: Return current PNCP recovery epoch (thread-safe)."""
    with _pncp_cron_status_lock:
        return _pncp_recovery_epoch


def update_pncp_cron_status(status: str, latency_ms: int | None) -> None:
    """Update global PNCP cron status (CRIT-052 AC3).

    CRIT-056 AC4: If transitioning from degraded/down -> healthy, increment recovery epoch.
    """
    global _pncp_recovery_epoch
    with _pncp_cron_status_lock:
        old_status = _pncp_cron_status["status"]
        _pncp_cron_status["status"] = status
        _pncp_cron_status["latency_ms"] = latency_ms
        _pncp_cron_status["updated_at"] = _time_mod.time()
        if old_status in ("degraded", "down") and status == "healthy":
            _pncp_recovery_epoch += 1
            logger.info(
                "CRIT-056: PNCP recovered (epoch=%d) — "
                "degraded cache entries will be revalidated on next read",
                _pncp_recovery_epoch,
            )
