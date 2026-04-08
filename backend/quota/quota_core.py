"""Plan capabilities, types, and in-memory cache infrastructure.

TD-007: Extracted from quota.py as part of DEBT-07 module split.
Contains plan definitions, capability system, and status cache helpers.
"""

import logging
import threading
import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, TypedDict

from pydantic import BaseModel
from log_sanitizer import mask_user_id

logger = logging.getLogger(__name__)

# STORY-203 SYS-M04: Plan capabilities cache
_plan_capabilities_cache: Optional[dict[str, "PlanCapabilities"]] = None
_plan_capabilities_cache_time: float = 0
PLAN_CAPABILITIES_CACHE_TTL = 300  # 5 minutes in seconds

# STORY-291 AC3: In-memory plan status cache (fallback when Supabase CB open)
# Key: user_id, Value: (plan_id, cached_at)
# DEBT-323: Bounded to prevent unbounded memory growth under high-cardinality user IDs.
# When maxsize is exceeded, the oldest entry (by insertion order) is evicted.
PLAN_STATUS_CACHE_MAXSIZE = 1000
_plan_status_cache: dict[str, tuple[str, float]] = {}
_plan_status_cache_lock = threading.Lock()
PLAN_STATUS_CACHE_TTL = 300  # 5 minutes


def _cache_plan_status(user_id: str, plan_id: str) -> None:
    """Cache plan status for fallback when Supabase is unavailable.

    DEBT-323: Enforces maxsize — evicts oldest entries when full.
    """
    with _plan_status_cache_lock:
        _plan_status_cache.pop(user_id, None)
        _plan_status_cache[user_id] = (plan_id, time.monotonic())
        while len(_plan_status_cache) > PLAN_STATUS_CACHE_MAXSIZE:
            _plan_status_cache.pop(next(iter(_plan_status_cache)))


def _get_cached_plan_status(user_id: str) -> Optional[str]:
    """Get cached plan status. Returns None if expired or missing."""
    with _plan_status_cache_lock:
        entry = _plan_status_cache.get(user_id)
        if entry is None:
            return None
        plan_id, cached_at = entry
        if time.monotonic() - cached_at > PLAN_STATUS_CACHE_TTL:
            del _plan_status_cache[user_id]
            return None
        return plan_id


def invalidate_plan_status_cache(user_id: str) -> None:
    """Remove a specific user from the plan status cache.

    HARDEN-008: Called by Stripe webhook handlers after plan_type updates
    to prevent stale quota bypass (up to 5 min window).
    """
    with _plan_status_cache_lock:
        removed = _plan_status_cache.pop(user_id, None)
    if removed:
        logger.info(f"Plan status cache invalidated for user {mask_user_id(user_id)}")
    else:
        logger.debug(f"Plan status cache miss (no entry) for user {mask_user_id(user_id)}")


# ============================================================================
# Plan Capabilities System
# ============================================================================

class PlanPriority(str, Enum):
    """Processing priority for background jobs (future use)."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class PlanCapabilities(TypedDict):
    """Immutable plan capabilities - DO NOT modify without PR review."""
    max_history_days: int
    allow_excel: bool
    allow_pipeline: bool  # STORY-250: Pipeline de Oportunidades
    max_requests_per_month: int
    max_requests_per_min: int
    max_summary_tokens: int
    priority: str  # PlanPriority value


# Hardcoded plan definitions (secure, version-controlled)
PLAN_CAPABILITIES: dict[str, PlanCapabilities] = {
    "free_trial": {
        "max_history_days": 365,  # GTM-003: 1 year (same as smartlic_pro)
        "allow_excel": True,  # GTM-003: Full product during trial
        "allow_pipeline": True,  # GTM-003: Full product during trial
        "max_requests_per_month": 1000,  # STORY-264 AC1: Full access (same as smartlic_pro)
        "max_requests_per_min": 2,  # STORY-264 AC2: Anti-abuse rate limit kept
        "max_summary_tokens": 10000,  # GTM-003: Full AI analysis (same as smartlic_pro)
        "priority": PlanPriority.NORMAL.value,  # GTM-003: Normal speed (same as smartlic_pro)
    },
    "consultor_agil": {
        "max_history_days": 30,
        "allow_excel": False,
        "allow_pipeline": False,  # STORY-250
        "max_requests_per_month": 50,
        "max_requests_per_min": 10,
        "max_summary_tokens": 200,
        "priority": PlanPriority.NORMAL.value,
    },
    "maquina": {
        "max_history_days": 365,
        "allow_excel": True,
        "allow_pipeline": True,  # STORY-250
        "max_requests_per_month": 300,
        "max_requests_per_min": 30,
        "max_summary_tokens": 500,
        "priority": PlanPriority.HIGH.value,
    },
    "sala_guerra": {
        "max_history_days": 1825,  # 5 years
        "allow_excel": True,
        "allow_pipeline": True,  # STORY-250
        "max_requests_per_month": 1000,
        "max_requests_per_min": 60,
        "max_summary_tokens": 10000,
        "priority": PlanPriority.CRITICAL.value,
    },
    "smartlic_pro": {
        "max_history_days": 1825,  # 5 years
        "allow_excel": True,
        "allow_pipeline": True,
        "max_requests_per_month": 1000,
        "max_requests_per_min": 60,
        "max_summary_tokens": 10000,
        "priority": PlanPriority.NORMAL.value,
    },
    # MAYDAY-A2: Founding Member — same capabilities as smartlic_pro, 50% off price
    "founding_member": {
        "max_history_days": 1825,  # 5 years
        "allow_excel": True,
        "allow_pipeline": True,
        "max_requests_per_month": 1000,
        "max_requests_per_min": 60,
        "max_summary_tokens": 10000,
        "priority": PlanPriority.NORMAL.value,
    },
    # STORY-322: Plano Consultoria — multi-user org plan
    "consultoria": {
        "max_history_days": 1825,  # 5 years
        "allow_excel": True,
        "allow_pipeline": True,
        "max_requests_per_month": 5000,  # 1000 x 5 members
        "max_requests_per_min": 10,  # Rate limit per org
        "max_summary_tokens": 10000,
        "priority": PlanPriority.HIGH.value,
    },
    # STORY-283 AC1: Map plan_ids found in production database
    "free": {
        "max_history_days": 7,
        "allow_excel": False,
        "allow_pipeline": False,
        "max_requests_per_month": 10,
        "max_requests_per_min": 2,
        "max_summary_tokens": 200,
        "priority": PlanPriority.LOW.value,
    },
    "master": {
        "max_history_days": 99999,
        "allow_excel": True,
        "allow_pipeline": True,
        "max_requests_per_month": 99999,
        "max_requests_per_min": 120,
        "max_summary_tokens": 10000,
        "priority": PlanPriority.HIGH.value,
    },
}

# Display names for UI
PLAN_NAMES: dict[str, str] = {
    "free_trial": "FREE Trial",
    "consultor_agil": "Consultor Ágil (legacy)",
    "maquina": "Máquina (legacy)",
    "sala_guerra": "Sala de Guerra (legacy)",
    "smartlic_pro": "SmartLic Pro",
    "founding_member": "SmartLic Founding Member",
    "consultoria": "SmartLic Consultoria",
    "free": "Free",
    "master": "Master",
}

# Pricing for error messages
PLAN_PRICES: dict[str, str] = {
    "consultor_agil": "R$ 297/mês",
    "maquina": "R$ 597/mês",
    "sala_guerra": "R$ 1.497/mês",
    "smartlic_pro": "R$ 397/mês",
    "founding_member": "R$ 197/mês",
    "consultoria": "R$ 997/mês",
}

# Upgrade path suggestions (for error messages)
UPGRADE_SUGGESTIONS: dict[str, dict[str, str]] = {
    "max_history_days": {
        "free_trial": "smartlic_pro",
        "consultor_agil": "smartlic_pro",
        "maquina": "smartlic_pro",
    },
    "allow_excel": {
        "free_trial": "smartlic_pro",
        "consultor_agil": "smartlic_pro",
    },
    "allow_pipeline": {
        "free_trial": "smartlic_pro",
        "consultor_agil": "smartlic_pro",
    },
    "max_requests_per_month": {
        "free_trial": "smartlic_pro",
        "consultor_agil": "smartlic_pro",
        "maquina": "smartlic_pro",
    },
}


# ============================================================================
# STORY-203 SYS-M04: Database-driven Plan Capabilities Loader
# ============================================================================

# Conservative defaults for unknown plans discovered at runtime
_UNKNOWN_PLAN_DEFAULTS = PlanCapabilities(
    max_history_days=30,
    allow_excel=False,
    allow_pipeline=False,  # STORY-250
    max_requests_per_month=10,
    max_requests_per_min=5,
    max_summary_tokens=200,
    priority=PlanPriority.NORMAL.value,
)


def _load_plan_capabilities_from_db() -> dict[str, PlanCapabilities]:
    """Load plan capabilities from database.

    STORY-203 SYS-M04: Loads plan definitions from `plans` table and converts
    to PlanCapabilities format. Falls back to hardcoded PLAN_CAPABILITIES on error.

    STORY-226 AC9: Uses data-driven lookup via PLAN_CAPABILITIES dict instead of
    if/elif chain. The DB's max_searches overrides max_requests_per_month when present.

    Returns:
        dict[str, PlanCapabilities]: Plan capabilities indexed by plan_id
    """
    try:
        from supabase_client import get_supabase
        sb = get_supabase()

        result = (
            sb.table("plans")
            .select("id, max_searches, price_brl, duration_days, description")
            .eq("is_active", True)
            .execute()
        )

        if not result.data:
            logger.warning("No plans found in database, using hardcoded fallback")
            return PLAN_CAPABILITIES

        db_capabilities: dict[str, PlanCapabilities] = {}

        for plan in result.data:
            plan_id = plan["id"]
            max_searches = plan.get("max_searches", 0)

            base_caps = PLAN_CAPABILITIES.get(plan_id)

            if base_caps is not None:
                caps = PlanCapabilities(
                    max_history_days=base_caps["max_history_days"],
                    allow_excel=base_caps["allow_excel"],
                    allow_pipeline=base_caps["allow_pipeline"],
                    max_requests_per_month=max_searches or base_caps["max_requests_per_month"],
                    max_requests_per_min=base_caps["max_requests_per_min"],
                    max_summary_tokens=base_caps["max_summary_tokens"],
                    priority=base_caps["priority"],
                )
            else:
                logger.warning(f"Unknown plan_id '{plan_id}' in database, using conservative defaults")
                caps = PlanCapabilities(
                    max_history_days=_UNKNOWN_PLAN_DEFAULTS["max_history_days"],
                    allow_excel=_UNKNOWN_PLAN_DEFAULTS["allow_excel"],
                    allow_pipeline=_UNKNOWN_PLAN_DEFAULTS["allow_pipeline"],
                    max_requests_per_month=max_searches or _UNKNOWN_PLAN_DEFAULTS["max_requests_per_month"],
                    max_requests_per_min=_UNKNOWN_PLAN_DEFAULTS["max_requests_per_min"],
                    max_summary_tokens=_UNKNOWN_PLAN_DEFAULTS["max_summary_tokens"],
                    priority=_UNKNOWN_PLAN_DEFAULTS["priority"],
                )

            db_capabilities[plan_id] = caps

        logger.info(
            f"Loaded {len(db_capabilities)} plan capabilities from database: "
            f"{list(db_capabilities.keys())}"
        )
        return db_capabilities

    except Exception as e:
        logger.error(f"Failed to load plan capabilities from database: {e}")
        logger.info("Falling back to hardcoded PLAN_CAPABILITIES")
        return PLAN_CAPABILITIES


def get_plan_capabilities() -> dict[str, PlanCapabilities]:
    """Get plan capabilities with caching.

    STORY-203 SYS-M04: Returns plan capabilities from in-memory cache (5min TTL)
    or loads from database. Falls back to hardcoded values on DB errors.

    Returns:
        dict[str, PlanCapabilities]: Plan capabilities indexed by plan_id
    """
    global _plan_capabilities_cache, _plan_capabilities_cache_time

    now = time.time()
    cache_age = now - _plan_capabilities_cache_time

    if _plan_capabilities_cache is not None and cache_age < PLAN_CAPABILITIES_CACHE_TTL:
        logger.debug(f"Plan capabilities cache HIT (age={cache_age:.1f}s)")
        return _plan_capabilities_cache

    logger.debug("Plan capabilities cache MISS - loading from database")
    _plan_capabilities_cache = _load_plan_capabilities_from_db()
    _plan_capabilities_cache_time = now

    return _plan_capabilities_cache


def clear_plan_capabilities_cache() -> None:
    """Clear plan capabilities cache (useful for testing or after plan updates).

    STORY-203 SYS-M04: Forces next get_plan_capabilities() call to reload from DB.
    """
    global _plan_capabilities_cache, _plan_capabilities_cache_time
    _plan_capabilities_cache = None
    _plan_capabilities_cache_time = 0
    logger.info("Plan capabilities cache cleared")


# ============================================================================
# Quota Info Models
# ============================================================================

class QuotaInfo(BaseModel):
    """Complete quota information for a user."""
    allowed: bool
    plan_id: str
    plan_name: str
    capabilities: dict
    quota_used: int
    quota_remaining: int
    quota_reset_date: datetime
    trial_expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    # STORY-309 AC5: Dunning degradation fields
    dunning_phase: str = "healthy"  # "healthy" | "active_retries" | "grace_period" | "blocked"
    days_since_failure: Optional[int] = None


class TrialPhaseInfo(TypedDict):
    phase: str  # "full_access" | "limited_access" | "not_trial"
    day: int
    days_remaining: int
