---
task: "Audit LLM Throughput"
responsavel: "@performance-auditor"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - backend/llm_arbiter.py
  - backend/llm.py
  - backend/job_queue.py
Saida: |
  - LLM throughput measurements
  - Cost per search validation
  - Background job reliability
Checklist:
  - "[ ] GPT-4.1-nano < 5s per batch"
  - "[ ] ThreadPoolExecutor(10) utilized"
  - "[ ] Cost ~ R$0.005/search verified"
  - "[ ] LLM timeout doesn't block response"
  - "[ ] Fallback summary works"
  - "[ ] ARQ processes background jobs"
---

# *audit-llm-throughput

Measure LLM classification throughput and cost.

## Steps

1. Read llm_arbiter.py — check ThreadPoolExecutor config
2. Read job_queue.py — check ARQ job processing
3. Check LLM model and pricing (GPT-4.1-nano)
4. Verify fallback summary generation
5. Calculate cost per search from token usage

## Output

Score (0-10) + throughput metrics + cost analysis
