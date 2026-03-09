"""Pipeline stage tracing and validation utilities.

DEBT-015 SYS-002: Extracted from SearchPipeline class.
"""

import time


def validate_stage_outputs(stage_name: str, ctx) -> None:
    """CRIT-050 AC10-AC12: Validate outputs are correctly typed after each stage."""
    if stage_name == "pipeline.fetch":
        if ctx.data_sources is None:
            ctx.data_sources = []
        if not isinstance(ctx.licitacoes_raw, list):
            ctx.licitacoes_raw = []
    elif stage_name == "pipeline.filter":
        if ctx.filter_stats is None:
            ctx.filter_stats = {}
        if not isinstance(ctx.licitacoes_filtradas, list):
            ctx.licitacoes_filtradas = []


async def traced_stage(tracer, ctx, span_name: str, stage_fn):
    """AC11-AC12: Run a pipeline stage wrapped in a child span with timing and counts."""
    from telemetry import optional_span

    stage_start = time.time()
    items_in = len(ctx.licitacoes_raw) if hasattr(ctx, "licitacoes_raw") and ctx.licitacoes_raw else 0

    with optional_span(tracer, span_name) as span:
        try:
            result = await stage_fn(ctx)
            validate_stage_outputs(span_name, ctx)
            duration_ms = int((time.time() - stage_start) * 1000)
            span.set_attribute("duration_ms", duration_ms)
            span.set_attribute("status", "ok")
            if span_name == "pipeline.fetch":
                span.set_attribute("items_out", len(ctx.licitacoes_raw) if ctx.licitacoes_raw else 0)
            elif span_name == "pipeline.filter":
                span.set_attribute("items_in", items_in)
                span.set_attribute("items_out", len(ctx.licitacoes_filtradas) if ctx.licitacoes_filtradas else 0)
            return result
        except Exception as e:
            duration_ms = int((time.time() - stage_start) * 1000)
            span.set_attribute("duration_ms", duration_ms)
            span.set_attribute("status", "error")
            span.record_exception(e)
            try:
                from opentelemetry.trace import StatusCode
                span.set_status(StatusCode.ERROR, str(e))
            except ImportError:
                pass
            raise
