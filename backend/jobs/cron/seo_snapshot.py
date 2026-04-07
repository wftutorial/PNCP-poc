"""S14: Weekly SEO metrics snapshot cron job."""

import asyncio
import logging

logger = logging.getLogger(__name__)

SEO_SNAPSHOT_INTERVAL = 7 * 24 * 60 * 60  # 7 days


async def run_seo_snapshot() -> dict:
    """Run GSC extraction for the last 7 days."""
    try:
        from scripts.gsc_metrics import fetch_and_store

        result = await fetch_and_store(days=7)
        logger.info("SEO snapshot completed: %s", result)
        return result
    except Exception as exc:
        logger.error("SEO snapshot failed: %s", exc)
        return {"status": "error", "error": str(exc)}


async def _seo_snapshot_loop():
    """Background loop: run weekly."""
    while True:
        await asyncio.sleep(SEO_SNAPSHOT_INTERVAL)
        await run_seo_snapshot()


async def start_seo_snapshot_task() -> asyncio.Task:
    """Create and return the background task."""
    return asyncio.create_task(_seo_snapshot_loop())
