"""cache/redis.py — Redis/InMemory cache layer (L2, 4h TTL).

redis_pool imports are lazy (inside functions) for testability.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from cache.enums import CachePriority, REDIS_TTL_BY_PRIORITY, REDIS_CACHE_TTL_SECONDS

logger = logging.getLogger(__name__)


def _save_to_redis(
    cache_key: str, results: list, sources: list,
    *, priority: CachePriority = CachePriority.COLD,
) -> None:
    """Save to Redis/InMemory cache (Level 2).

    B-02 AC6: Uses priority-based TTL instead of fixed 4h.
    """
    from redis_pool import get_fallback_cache
    cache = get_fallback_cache()

    ttl = REDIS_TTL_BY_PRIORITY.get(priority, REDIS_CACHE_TTL_SECONDS)
    cache_data = json.dumps({
        "results": results,
        "sources_json": sources,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    })
    cache.setex(f"search_cache:{cache_key}", ttl, cache_data)


def _get_from_redis(cache_key: str) -> Optional[dict]:
    """Read from Redis/InMemory cache (Level 2)."""
    from redis_pool import get_fallback_cache
    cache = get_fallback_cache()

    cached = cache.get(f"search_cache:{cache_key}")
    if not cached:
        return None

    return json.loads(cached)
