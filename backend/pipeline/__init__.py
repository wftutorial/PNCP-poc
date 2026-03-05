"""Pipeline package — extracted from search_pipeline.py (TD-008 AC20).

Re-exports all public symbols for backward compatibility:
  from search_pipeline import _build_pncp_link  # still works
  from pipeline.helpers import _build_pncp_link  # also works
"""

from pipeline.helpers import (
    _build_pncp_link,
    _calcular_urgencia,
    _calcular_dias_restantes,
    _map_confidence,
    _convert_to_licitacao_items,
    _build_coverage_metrics,
    _build_coverage_metadata,
    _maybe_send_quota_email,
)

from pipeline.cache_manager import (
    SEARCH_CACHE_TTL,
    _compute_cache_key,
    _read_cache,
    _write_cache,
    _build_cache_params,
    _maybe_trigger_revalidation,
    _build_degraded_detail,
    apply_stale_cache,
    set_empty_failure,
)

__all__ = [
    # helpers
    "_build_pncp_link",
    "_calcular_urgencia",
    "_calcular_dias_restantes",
    "_map_confidence",
    "_convert_to_licitacao_items",
    "_build_coverage_metrics",
    "_build_coverage_metadata",
    "_maybe_send_quota_email",
    # cache_manager
    "SEARCH_CACHE_TTL",
    "_compute_cache_key",
    "_read_cache",
    "_write_cache",
    "_build_cache_params",
    "_maybe_trigger_revalidation",
    "_build_degraded_detail",
    "apply_stale_cache",
    "set_empty_failure",
]
