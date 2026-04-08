"""Source result data structures and error types.

TD-008: Extracted from consolidation.py as part of DEBT-07 module split.
Contains SourceResult, ConsolidationResult, and AllSourcesFailedError.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SourceResult:
    """Result metrics from a single source fetch."""

    source_code: str
    record_count: int
    duration_ms: int
    error: Optional[str] = None
    status: str = "success"  # "success" | "error" | "timeout" | "skipped" | "disabled" | "degraded"
    # CRIT-053 AC3: Reason why source was skipped/degraded (e.g. "health_canary_timeout")
    skipped_reason: Optional[str] = None


@dataclass
class ConsolidationResult:
    """Result of consolidated multi-source fetch."""

    records: List[Dict[str, Any]]  # Legacy format (already converted)
    total_before_dedup: int
    total_after_dedup: int
    duplicates_removed: int
    source_results: List[SourceResult]
    elapsed_ms: int
    is_partial: bool = False
    degradation_reason: Optional[str] = None
    # GTM-STAB-003 AC3: UF tracking for early return
    ufs_completed: List[str] = field(default_factory=list)
    ufs_pending: List[str] = field(default_factory=list)


class AllSourcesFailedError(Exception):
    """Raised when all sources fail and fail_on_all_errors is True."""

    def __init__(self, source_errors: Dict[str, str]):
        self.source_errors = source_errors
        msg = "; ".join(f"{k}: {v}" for k, v in source_errors.items())
        super().__init__(f"All sources failed: {msg}")
