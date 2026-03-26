"""ARQ cron job definitions for PNCP data lake ingestion.

These jobs are registered in job_queue.WorkerSettings when DATALAKE_ENABLED=true.
They are intentionally thin wrappers — all logic lives in crawler.py / loader.py.

Schedule (default, all UTC):
  - Full crawl:         05:00 daily  (2am BRT)
  - Incremental crawl: 11:00, 17:00, 23:00  (8am, 2pm, 8pm BRT)
  - Purge:             07:00 daily  (4am BRT, 2h after full crawl)

Timeouts (ARQ-enforced):
  - Full crawl:    4h  (14400s) — 30-60 min expected, safety margin for retries
  - Incremental:   1h  (3600s)  — 10-20 min expected
  - Purge:        10m  (600s)   — simple DELETE, no heavy I/O
"""

import logging
import time

from ingestion.config import DATALAKE_ENABLED

logger = logging.getLogger(__name__)


async def ingestion_full_crawl_job(ctx: dict) -> dict:
    """ARQ job: Full PNCP crawl. Daily at 2am BRT (5am UTC).

    Feature flag: DATALAKE_ENABLED must be true.
    Expected runtime: 30-60 min. Timeout: 4h safety.

    Returns:
        dict with status, ufs_processed, records_upserted, duration_s.
    """
    if not DATALAKE_ENABLED:
        logger.info("[Ingestion:FullCrawl] Skipped — DATALAKE_ENABLED=false")
        return {"status": "skipped", "reason": "DATALAKE_ENABLED=false"}

    start = time.monotonic()
    logger.info("[Ingestion:FullCrawl] Starting full PNCP crawl")

    try:
        from ingestion.crawler import crawl_full
        result = await crawl_full()
    except Exception as e:
        duration_s = round(time.monotonic() - start, 1)
        logger.error(
            f"[Ingestion:FullCrawl] Failed after {duration_s}s: {type(e).__name__}: {e}",
            exc_info=True,
        )
        return {
            "status": "failed",
            "error": str(e),
            "duration_s": duration_s,
        }

    duration_s = round(time.monotonic() - start, 1)
    logger.info(
        f"[Ingestion:FullCrawl] Completed in {duration_s}s — "
        f"records={result.get('records_upserted', 0)}"
    )
    return {**result, "duration_s": duration_s}


async def ingestion_incremental_job(ctx: dict) -> dict:
    """ARQ job: Incremental PNCP crawl. 3x/day (11:00, 17:00, 23:00 UTC).

    Feature flag: DATALAKE_ENABLED must be true.
    Expected runtime: 10-20 min. Timeout: 1h safety.

    Returns:
        dict with status, ufs_processed, records_upserted, duration_s.
    """
    if not DATALAKE_ENABLED:
        logger.info("[Ingestion:Incremental] Skipped — DATALAKE_ENABLED=false")
        return {"status": "skipped", "reason": "DATALAKE_ENABLED=false"}

    start = time.monotonic()
    logger.info("[Ingestion:Incremental] Starting incremental PNCP crawl")

    try:
        from ingestion.crawler import crawl_incremental
        result = await crawl_incremental()
    except Exception as e:
        duration_s = round(time.monotonic() - start, 1)
        logger.error(
            f"[Ingestion:Incremental] Failed after {duration_s}s: {type(e).__name__}: {e}",
            exc_info=True,
        )
        return {
            "status": "failed",
            "error": str(e),
            "duration_s": duration_s,
        }

    duration_s = round(time.monotonic() - start, 1)
    logger.info(
        f"[Ingestion:Incremental] Completed in {duration_s}s — "
        f"records={result.get('records_upserted', 0)}"
    )
    return {**result, "duration_s": duration_s}


async def ingestion_purge_job(ctx: dict) -> dict:
    """ARQ job: Purge old bids older than retention_days from pncp_raw_bids.

    Runs daily 2h after full crawl (07:00 UTC = 4am BRT).
    Feature flag: DATALAKE_ENABLED must be true.
    Expected runtime: < 1 min. Timeout: 10 min safety.

    Returns:
        dict with status, deleted, retention_days, duration_s.
    """
    if not DATALAKE_ENABLED:
        logger.info("[Ingestion:Purge] Skipped — DATALAKE_ENABLED=false")
        return {"status": "skipped", "reason": "DATALAKE_ENABLED=false"}

    start = time.monotonic()

    from ingestion.config import INGESTION_RETENTION_DAYS
    logger.info(
        f"[Ingestion:Purge] Starting purge — retention_days={INGESTION_RETENTION_DAYS}"
    )

    try:
        from ingestion.loader import purge_old_bids
        deleted = await purge_old_bids(INGESTION_RETENTION_DAYS)
    except Exception as e:
        duration_s = round(time.monotonic() - start, 1)
        logger.error(
            f"[Ingestion:Purge] Failed after {duration_s}s: {type(e).__name__}: {e}",
            exc_info=True,
        )
        return {
            "status": "failed",
            "error": str(e),
            "retention_days": INGESTION_RETENTION_DAYS,
            "duration_s": duration_s,
        }

    duration_s = round(time.monotonic() - start, 1)
    logger.info(
        f"[Ingestion:Purge] Completed in {duration_s}s — deleted={deleted} rows "
        f"(retention={INGESTION_RETENTION_DAYS} days)"
    )
    return {
        "status": "completed",
        "deleted": deleted,
        "retention_days": INGESTION_RETENTION_DAYS,
        "duration_s": duration_s,
    }
