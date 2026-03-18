"""Base classes for collectors."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CollectorResult:
    """Standardized result from any collector.

    Attributes:
        data: The collected data (dict or list)
        source: Source tag dict {"status": "API"|"API_FAILED"|..., "timestamp": ..., "detail": ...}
        name: Collector name for logging
        duration_ms: Collection duration in milliseconds
        cached: Whether result came from cache
    """

    data: Any
    source: dict = field(default_factory=lambda: {"status": "UNAVAILABLE"})
    name: str = ""
    duration_ms: int = 0
    cached: bool = False

    @property
    def ok(self) -> bool:
        """True if data was collected successfully (API or CALCULATED)."""
        return self.source.get("status") in ("API", "CALCULATED", "API_PARTIAL")

    @property
    def failed(self) -> bool:
        """True if collection failed."""
        return self.source.get("status") in ("API_FAILED", "API_CORRUPT")


@dataclass
class PipelinePhase:
    """Represents a collection phase with dependencies.

    Used for DAG-based orchestration of parallel collection.

    Attributes:
        name: Phase name
        collectors: List of collector names in this phase
        depends_on: Phase names that must complete first
        parallel: Whether collectors in this phase can run in parallel
    """

    name: str
    collectors: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    parallel: bool = True


# Pipeline DAG definition
PIPELINE_PHASES = [
    PipelinePhase(
        name="profile",
        collectors=["opencnpj", "brasilapi"],
        depends_on=[],
        parallel=True,
    ),
    PipelinePhase(
        name="history",
        collectors=["transparencia"],
        depends_on=["profile"],
        parallel=False,
    ),
    PipelinePhase(
        name="enrichment",
        collectors=["ibge"],
        depends_on=["profile"],
        parallel=True,
    ),
    PipelinePhase(
        name="search",
        collectors=["pncp", "pcp", "querido_diario"],
        depends_on=["history"],  # needs keywords from contract history
        parallel=True,
    ),
    PipelinePhase(
        name="intel",
        collectors=["competitive", "documents", "distance"],
        depends_on=["search"],
        parallel=True,
    ),
    PipelinePhase(
        name="scoring",
        collectors=["deterministic"],
        depends_on=["intel"],
        parallel=False,
    ),
]
