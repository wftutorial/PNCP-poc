"""Generic cron loop runner and shared helpers for all cron modules."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Callable, Awaitable, Any

logger = logging.getLogger(__name__)


def is_cb_or_connection_error(e: Exception) -> bool:
    """SHIP-003 AC3: Check if exception is CB or connection error."""
    err_name = type(e).__name__
    err_str = str(e)
    return (
        "CircuitBreaker" in err_name
        or "ConnectionError" in err_name
        or "ConnectError" in err_str
        or "PGRST205" in err_str
    )


async def cron_loop(
    name: str,
    func: Callable[..., Awaitable[Any]],
    interval_seconds: int | float,
    *,
    initial_delay: float = 0,
    error_retry_seconds: float = 300,
    func_kwargs: dict | None = None,
) -> None:
    """Run *func* in a loop with uniform error handling."""
    if initial_delay > 0:
        await asyncio.sleep(initial_delay)

    kwargs = func_kwargs or {}

    while True:
        try:
            result = await func(**kwargs)
            logger.info("%s: %s at %s", name, result, datetime.now(timezone.utc).isoformat())
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("%s: task cancelled", name)
            break
        except Exception as e:
            if is_cb_or_connection_error(e):
                logger.warning("%s: skipped (infra unavailable): %s", name, e)
            else:
                logger.error("%s: error: %s", name, e, exc_info=True)
            await asyncio.sleep(error_retry_seconds)


async def daily_loop(
    name: str,
    func: Callable[..., Awaitable[Any]],
    target_hour_utc: int,
    *,
    error_retry_seconds: float = 300,
    func_kwargs: dict | None = None,
) -> None:
    """Run *func* daily at *target_hour_utc* with uniform error handling."""
    now = datetime.now(timezone.utc)
    next_run = now.replace(hour=target_hour_utc, minute=0, second=0, microsecond=0)
    if now.hour >= target_hour_utc:
        next_run += timedelta(days=1)
    initial_delay = max(60, min((next_run - now).total_seconds(), 86400))
    logger.info("%s: first run in %.0fs (target: %s)", name, initial_delay, next_run.isoformat())
    await asyncio.sleep(initial_delay)

    kwargs = func_kwargs or {}

    while True:
        try:
            result = await func(**kwargs)
            logger.info("%s: %s at %s", name, result, datetime.now(timezone.utc).isoformat())
            await asyncio.sleep(24 * 60 * 60)
        except asyncio.CancelledError:
            logger.info("%s: task cancelled", name)
            break
        except Exception as e:
            if is_cb_or_connection_error(e):
                logger.warning("%s: skipped (infra unavailable): %s", name, e)
            else:
                logger.error("%s: error: %s", name, e, exc_info=True)
            await asyncio.sleep(error_retry_seconds)


async def acquire_redis_lock(key: str, ttl: int) -> bool:
    """Try to acquire a Redis NX lock. Returns True if acquired or Redis unavailable."""
    try:
        from redis_pool import get_redis_pool
        redis = await get_redis_pool()
        if redis:
            acquired = await redis.set(
                key, datetime.now(timezone.utc).isoformat(), nx=True, ex=ttl,
            )
            if not acquired:
                return False
    except Exception as e:
        logger.warning("Redis lock check failed for %s (proceeding): %s", key, e)
    return True


async def release_redis_lock(key: str) -> None:
    """Release a Redis lock (best-effort)."""
    try:
        from redis_pool import get_redis_pool
        redis = await get_redis_pool()
        if redis:
            await redis.delete(key)
    except Exception:
        pass
