---
task: "Audit OpenTelemetry Tracing"
responsavel: "@observability-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/telemetry.py
  - OTEL configuration
Saida: |
  - Tracing coverage assessment
  - Export endpoint validation
  - Sampling configuration check
Checklist:
  - "[ ] 7 pipeline spans instrumented"
  - "[ ] 10% sampling rate"
  - "[ ] OTEL_EXPORTER_OTLP_ENDPOINT set"
  - "[ ] Traces exportable"
  - "[ ] Correlation IDs propagated"
---

# *audit-otel

Validate OpenTelemetry tracing configuration.

## Steps

1. Read backend/telemetry.py — check span instrumentation
2. Verify OTEL_EXPORTER_OTLP_ENDPOINT is configured (not empty)
3. Check sampling rate (10%)
4. Verify correlation ID propagation
5. Check if traces reach a backend (Jaeger/Tempo)

## Known Issue

OTEL_EXPORTER_OTLP_ENDPOINT may be empty — tracing collected but not exported.

## Output

Score (0-10) + tracing assessment + recommendations
