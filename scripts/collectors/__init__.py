"""
Collector modules for B2G Report data pipeline.

This package provides a modular interface to the data collection
functions in collect-report-data.py. Each collector follows the
Collector protocol:

    result = collector.collect(api, cnpj, **kwargs) -> dict

Currently wraps existing monolith functions. Future decomposition
will extract each collector into its own file.

Modules:
    opencnpj    -- Company profile from OpenCNPJ API
    transparencia -- Sanctions + contract history from Portal da Transparencia
    brasilapi   -- Simples Nacional + MEI from BrasilAPI
    ibge        -- Population + GDP from IBGE SIDRA
    pncp        -- Procurement search from PNCP
    pcp         -- Municipal procurement from PCP v2
    querido_diario -- Gazette mentions from Querido Diario
    competitive -- Historical contracts for competitive intelligence
    distance    -- OSRM distance calculations
    sicaf       -- SICAF cadastral verification
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Collector(Protocol):
    """Protocol for all data collectors."""

    name: str

    def collect(self, api: Any, cnpj: str, **kwargs: Any) -> dict:
        """Collect data from source. Returns dict with _source field."""
        ...


# Lazy imports -- only load when accessed to avoid circular imports
_REGISTRY: dict[str, type] = {}


def get_collector(name: str) -> type:
    """Get collector class by name."""
    if name not in _REGISTRY:
        raise KeyError(f"Unknown collector: {name}. Available: {list(_REGISTRY.keys())}")
    return _REGISTRY[name]


def list_collectors() -> list[str]:
    """List all registered collector names."""
    return list(_REGISTRY.keys())
