"""STORY-351 AC3: Public discard rate metrics endpoint.

GET /v1/metrics/discard-rate — Returns 30-day moving average of filter discard rate.
Public (no auth required) — used by landing page StatsSection.
"""

import logging

from fastapi import APIRouter, Query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/discard-rate")
async def get_discard_rate(days: int = Query(30, ge=1, le=90)):
    """Return the moving-average filter discard rate.

    Public endpoint (no authentication required). Used by the landing page
    to display a verified discard rate instead of a hardcoded number.
    """
    from filter_stats import discard_rate_tracker

    data = discard_rate_tracker.get_discard_rate(days=days)
    logger.debug(
        f"discard-rate requested: {data['discard_rate_pct']}% "
        f"({data['sample_size']} searches, {data['period_days']}d window)"
    )
    return data
