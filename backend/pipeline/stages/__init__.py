"""Pipeline stage functions — extracted from SearchPipeline methods (DEBT-015 SYS-002).

Each stage is an async function taking (pipeline, ctx) where:
  - pipeline: SearchPipeline instance (provides self.deps)
  - ctx: SearchContext (mutable state passed between stages)
"""

from pipeline.stages.validate import stage_validate
from pipeline.stages.prepare import stage_prepare
from pipeline.stages.execute import stage_execute
from pipeline.stages.filter_stage import stage_filter
from pipeline.stages.enrich import stage_enrich
from pipeline.stages.generate import stage_generate
from pipeline.stages.persist import stage_persist

__all__ = [
    "stage_validate",
    "stage_prepare",
    "stage_execute",
    "stage_filter",
    "stage_enrich",
    "stage_generate",
    "stage_persist",
]
