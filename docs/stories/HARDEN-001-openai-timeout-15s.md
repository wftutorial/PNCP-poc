# HARDEN-001: OpenAI Client Timeout 600s → 15s

**Severidade:** CRITICA
**Esforço:** 5 min
**Quick Win:** Sim
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

O `OpenAI()` client em `llm_arbiter.py:40` é inicializado sem parâmetro `timeout`. O default do SDK é 600s (10 min). Se 10 workers do ThreadPoolExecutor bloqueiam simultaneamente em chamadas OpenAI, o pipeline inteiro trava por até 10 minutos enquanto o pipeline timeout é 110s.

## Problema

- GPT-4.1-nano p99 latency ≈ 3s
- Timeout default do SDK = 600s (100× o p99)
- Threads bloqueadas continuam consumindo recursos mesmo após pipeline timeout
- max_retries default = 2, causando até 3 tentativas × 600s = 1800s de bloqueio

## Critérios de Aceitação

- [x] AC1: `OpenAI()` inicializado com `timeout=15` (5× p99)
- [x] AC2: `max_retries=1` (reduzir de 2 para 1)
- [x] AC3: Timeout configurável via env var `LLM_TIMEOUT_S`
- [x] AC4: Teste unitário valida que client usa timeout correto
- [x] AC5: Zero regressions nos testes existentes

## Solução

```python
# llm_arbiter.py:40
_LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT_S", "15"))

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=_LLM_TIMEOUT,
            max_retries=1,
        )
    return _client
```

## Arquivos Afetados

- `backend/llm_arbiter.py` — _get_client()
- `backend/tests/test_llm_arbiter.py` — novo teste

## Referência

Stripe usa 10-15s timeout para LLM calls. Netflix recomenda timeout = 2× p99.
