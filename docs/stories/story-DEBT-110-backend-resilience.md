# Story DEBT-110: Backend Resilience & Observability — Circuit Breakers, Caching & Monitoring

## Metadata
- **Story ID:** DEBT-110
- **Epic:** EPIC-DEBT
- **Batch:** D (Long-term)
- **Sprint:** 7+ (Semanas 11-12+)
- **Estimativa:** 80h
- **Prioridade:** P3
- **Agent:** @dev + @architect

## Descricao

Como engenheiro de plataforma, quero ajustar circuit breakers, implementar Redis L2 cache para LLM, decompor o filter.py monolitico, completar MFA, resolver dependencias de seguranca, e melhorar observabilidade, para que o backend seja resiliente, observavel, e maintainable a longo prazo.

## Debt Items Cobertos

| ID | Debito | Severidade | Horas |
|----|--------|:---:|:---:|
| SYS-018 | Circuit breaker pattern tuning (15 failures -> 60s cooldown) | MEDIUM | 8h |
| SYS-019 | CB integration — quando Supabase CB open, skip retries | MEDIUM | 4h |
| SYS-021 | Redis L2 cache para cross-worker LLM sharing | MEDIUM | 4h |
| SYS-030 | filter.py 177KB monolithic file decomposition | MEDIUM | 16h |
| SYS-031 | N+1 patterns em analytics queries | MEDIUM | 8h |
| SYS-024 | MFA (aal2) requirement + TOTP + recovery codes | MEDIUM | 16h |
| SYS-022 | cryptography pin >=46.0.5,<47.0.0 fork-safe with Gunicorn | MEDIUM | 4h |
| SYS-027 | chardet<6 pin removal (needs SYS-008 httpx migration) | MEDIUM | 2h |
| SYS-028 | pytest timeout_method="thread" Windows compat | MEDIUM | 2h |
| SYS-016 | Feature flag caching with lazy import — circular dependency prevention | MEDIUM | 4h |
| SYS-017 | Lazy-load filter stats tracker to prevent circular imports | MEDIUM | 2h |
| SYS-023 | Health canary every 5 min for source health tracking | MEDIUM | 4h |
| SYS-025 | Legacy route tracking — non-/v1/ deprecated endpoints | MEDIUM | 2h |
| SYS-032 | LLM cost optimization — cheaper models for low-stakes | MEDIUM | 4h |

## Acceptance Criteria

- [ ] AC1: Circuit breaker thresholds configuraveis via env vars
- [ ] AC2: Supabase CB open -> skip retries automaticamente
- [ ] AC3: Redis L2 cache para LLM results — cross-worker sharing funciona
- [ ] AC4: filter.py decomposto em modulos: `filter_keywords.py`, `filter_density.py`, `filter_status.py`, `filter_value.py`, `filter_uf.py`
- [ ] AC5: Todos os 170+ filter tests passam apos decomposicao
- [ ] AC6: N+1 queries em analytics eliminados (verificado via EXPLAIN ANALYZE)
- [ ] AC7: MFA TOTP implementado com recovery codes
- [ ] AC8: cryptography pin atualizado para fork-safe version
- [ ] AC9: chardet removido do requirements (post httpx migration)
- [ ] AC10: pytest timeout_method="thread" em pyproject.toml
- [ ] AC11: Feature flags com lazy import (sem circular deps)
- [ ] AC12: Health canary rodando a cada 5 min
- [ ] AC13: Legacy routes com deprecation counter metric
- [ ] AC14: LLM cost analysis documentado; cheaper model para low-stakes se viavel

## Testes Requeridos

- Circuit breaker: integration test com failure injection
- Redis L2: mock Redis, test cache hit/miss/eviction
- filter.py: todos os 170+ tests existentes passam sem modificacao
- MFA: TOTP enrollment + verification + recovery code flow
- Health canary: test que canary reports source status corretamente
- Legacy routes: deprecation metric incrementa em hit
- Full suite: `python scripts/run_tests_safe.py` — 0 failures

## Notas Tecnicas

- **SYS-030 (filter.py):** 177KB e o maior file do projeto. Decompor por responsabilidade (UF, value, keyword, density, status, date). Manter `filter.py` como facade que importa submodulos.
- **SYS-024 (MFA):** Supabase Auth suporta TOTP nativamente. Verificar `supabase.auth.mfa.enroll()`.
- **SYS-027:** So pode ser feito APOS SYS-008 (httpx migration) em DEBT-107.
- **SYS-028:** Ja documentado em CLAUDE.md e pyproject.toml — verificar se esta aplicado.

## Dependencias

- **Depende de:** DEBT-107 (SYS-008 httpx migration enables SYS-027 chardet removal)
- **Bloqueia:** Nenhuma

## Definition of Done

- [ ] Todos os 14 items implementados
- [ ] filter.py decomposto (<50KB por modulo)
- [ ] MFA TOTP funcional
- [ ] Testes passando
- [ ] Metricas expostas (CB, cache, canary, legacy routes)
- [ ] Code review aprovado
- [ ] Documentacao atualizada
