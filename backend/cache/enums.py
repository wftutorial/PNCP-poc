"""cache/enums.py — Enums, constants, hash utilities, and priority logic.

All pure (no I/O) — safe to import anywhere without circular deps.
"""
import hashlib
import json
import logging
import os
import platform
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# TTL boundaries (hours) — STORY-306 AC8/AC9: single source of truth
CACHE_FRESH_HOURS = 4  # STORY-306: was 6, aligned with REDIS_CACHE_TTL_SECONDS
CACHE_STALE_HOURS = 24  # L2 Supabase / L3 Local file — SWR window

# Local cache directory (platform-aware)
LOCAL_CACHE_DIR = Path(
    os.getenv("SMARTLIC_CACHE_DIR", "/tmp/smartlic_cache")
    if platform.system() != "Windows"
    else os.getenv("SMARTLIC_CACHE_DIR", os.path.join(os.environ.get("TEMP", "C:\\Temp"), "smartlic_cache"))
)
LOCAL_CACHE_TTL_HOURS = 24  # Max age for local cache files
LOCAL_CACHE_MAX_SIZE_MB = 200  # HARDEN-018: max dir size before eviction
LOCAL_CACHE_TARGET_SIZE_MB = 100  # HARDEN-018: evict until below this
REDIS_CACHE_TTL_SECONDS = 14400  # 4 hours


class CacheLevel(str, Enum):
    """Cache storage level for tracking hit metrics."""
    SUPABASE = "supabase"
    REDIS = "redis"
    LOCAL = "local"
    MISS = "miss"


class CacheStatus(str, Enum):
    """Cache age classification per SWR policy."""
    FRESH = "fresh"
    STALE = "stale"
    EXPIRED = "expired"


class CachePriority(str, Enum):
    """B-02 AC1: Cache entry priority classification for hot/warm/cold tiering."""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


# B-02 AC6: Redis TTL by priority (seconds)
REDIS_TTL_BY_PRIORITY = {
    CachePriority.HOT: 7200,    # 2h
    CachePriority.WARM: 21600,  # 6h
    CachePriority.COLD: 3600,   # 1h
}


def classify_priority(
    access_count: int,
    last_accessed_at: Optional[datetime],
    is_saved_search: bool = False,
) -> CachePriority:
    """B-02 AC2: Deterministic priority classification."""
    now = datetime.now(timezone.utc)

    recent_access = False
    if last_accessed_at:
        if last_accessed_at.tzinfo is None:
            last_accessed_at = last_accessed_at.replace(tzinfo=timezone.utc)
        age_hours = (now - last_accessed_at).total_seconds() / 3600
        recent_access = age_hours <= 24

    if recent_access and access_count >= 3:
        return CachePriority.HOT
    if is_saved_search and recent_access:
        return CachePriority.HOT
    if recent_access and access_count >= 1:
        return CachePriority.WARM

    return CachePriority.COLD


def _normalize_date(value) -> "str | None":
    """STORY-306 AC2: Normalize date to ISO 8601 (YYYY-MM-DD) for cache key stability."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%d/%m/%Y"):
        try:
            return datetime.strptime(s[:10] if "T" in s and fmt == "%Y-%m-%d" else s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    return s


def compute_search_hash(params: dict) -> str:
    """STORY-306 AC1-AC4: Deterministic hash including ALL params that affect results."""
    normalized = {
        "setor_id": params.get("setor_id"),
        "ufs": sorted(params.get("ufs", [])),
        "status": params.get("status"),
        "modalidades": sorted(params.get("modalidades") or []) or None,
        "modo_busca": params.get("modo_busca"),
        "date_from": _normalize_date(params.get("date_from") or params.get("data_inicio") or params.get("data_inicial")),
        "date_to": _normalize_date(params.get("date_to") or params.get("data_fim") or params.get("data_final")),
        "termos_busca": params.get("termos_busca") or None,
        "valor_minimo": params.get("valor_minimo"),
        "valor_maximo": params.get("valor_maximo"),
        "esferas": sorted(params.get("esferas") or []) or None,
        "municipios": sorted(params.get("municipios") or []) or None,
        "exclusion_terms": sorted(params.get("exclusion_terms") or []) or None,
        "show_all_matches": params.get("show_all_matches") or False,
    }
    params_json = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(params_json.encode()).hexdigest()


def compute_search_hash_without_dates(params: dict) -> str:
    """STORY-306 AC12: Legacy hash WITHOUT dates for dual-read thundering herd mitigation."""
    normalized = {
        "setor_id": params.get("setor_id"),
        "ufs": sorted(params.get("ufs", [])),
        "status": params.get("status"),
        "modalidades": sorted(params.get("modalidades") or []) or None,
        "modo_busca": params.get("modo_busca"),
    }
    params_json = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(params_json.encode()).hexdigest()


def compute_search_hash_per_uf(params: dict, uf: str) -> str:
    """CRIT-051 AC1: Deterministic hash for a SINGLE UF (composable cache)."""
    normalized = {
        "setor_id": params.get("setor_id"),
        "ufs": [uf],
        "status": params.get("status"),
        "modalidades": sorted(params.get("modalidades") or []) or None,
        "modo_busca": params.get("modo_busca"),
        "date_from": _normalize_date(params.get("date_from") or params.get("data_inicio") or params.get("data_inicial")),
        "date_to": _normalize_date(params.get("date_to") or params.get("data_fim") or params.get("data_final")),
        "termos_busca": params.get("termos_busca") or None,
        "valor_minimo": params.get("valor_minimo"),
        "valor_maximo": params.get("valor_maximo"),
        "esferas": sorted(params.get("esferas") or []) or None,
        "municipios": sorted(params.get("municipios") or []) or None,
        "exclusion_terms": sorted(params.get("exclusion_terms") or []) or None,
        "show_all_matches": params.get("show_all_matches") or False,
    }
    params_json = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(params_json.encode()).hexdigest()


def compute_global_hash(params: dict) -> str:
    """GTM-ARCH-002 AC2: Global cache hash — setor + ufs + dates, WITHOUT user_id."""
    normalized = {
        "setor_id": params.get("setor_id"),
        "ufs": sorted(params.get("ufs", [])),
        "data_inicio": params.get("data_inicio") or params.get("data_inicial"),
        "data_fim": params.get("data_fim") or params.get("data_final"),
    }
    params_json = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(params_json.encode()).hexdigest()


def calculate_backoff_minutes(fail_streak: int) -> int:
    """B-03 AC4: Exponential backoff for cache key degradation."""
    if fail_streak <= 0:
        return 0
    backoff_schedule = [1, 5, 15, 30]
    idx = min(fail_streak - 1, len(backoff_schedule) - 1)
    return backoff_schedule[idx]


def get_cache_status(fetched_at) -> CacheStatus:
    """Classify cache age into Fresh/Stale/Expired (AC4)."""
    if isinstance(fetched_at, str):
        fetched_at = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))

    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)

    age_hours = (datetime.now(timezone.utc) - fetched_at).total_seconds() / 3600

    if age_hours <= CACHE_FRESH_HOURS:
        return CacheStatus.FRESH
    elif age_hours <= CACHE_STALE_HOURS:
        return CacheStatus.STALE
    else:
        return CacheStatus.EXPIRED
