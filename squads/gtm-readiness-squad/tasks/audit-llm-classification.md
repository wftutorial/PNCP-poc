---
task: "Audit LLM Classification"
responsavel: "@pipeline-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/llm_arbiter.py
  - backend/llm.py
  - backend/relevance.py
  - backend/filter.py
Saida: |
  - LLM classification accuracy assessment
  - Feature flag validation
  - Fallback behavior check
Checklist:
  - "[ ] Keywords >5% density → keyword source"
  - "[ ] 2-5% density → llm_standard"
  - "[ ] 1-2% density → llm_conservative"
  - "[ ] 0% density → llm_zero_match"
  - "[ ] LLM failure → REJECT (zero noise)"
  - "[ ] LLM_ZERO_MATCH_ENABLED respected"
  - "[ ] ThreadPoolExecutor(10) for parallelism"
  - "[ ] ARQ jobs for summaries"
  - "[ ] Fallback summary works"
---

# *audit-llm

Validate LLM classification pipeline and fallback behavior.

## Steps

1. Read `backend/llm_arbiter.py` — check classification logic
2. Read `backend/filter.py` — check density thresholds
3. Verify feature flags: LLM_ZERO_MATCH_ENABLED, LLM_ARBITER_ENABLED
4. Check fallback behavior on LLM failure (must REJECT)
5. Verify ARQ background job for summaries

## Output

Score (0-10) + classification assessment + recommendations
