# Story DEBT-204: Backend Wave 2 + Banner System — pncp_client + cron/jobs + BannerStack

## Metadados
- **Epic:** EPIC-DEBT-V2
- **Sprint:** 5 (Semana 9-10)
- **Prioridade:** P1-P2
- **Esforco:** 30h
- **Agente:** @dev + @qa + @ux-design-expert
- **Status:** PLANNED

## Descricao

Como equipe de desenvolvimento, queremos decompor os 3 modulos backend monoliticos restantes (pncp_client, cron_jobs, job_queue) e consolidar o sistema de banners da tela de busca, para que falhas em um componente nao afetem outros (isolamento), testes sejam mais rapidos e focados, e a carga cognitiva do usuario na tela de busca seja reduzida.

## Debitos Incluidos

| ID | Debito | Horas | Responsavel |
|----|--------|-------|-------------|
| DEBT-SYS-004 | `pncp_client.py` sobrecarregado (2.559 LOC) — sync + async client, circuit breaker, retry | 10h | @dev |
| DEBT-SYS-005 | `cron_jobs.py` multiplas responsabilidades (2.251 LOC) | 8h | @dev + @qa |
| DEBT-SYS-006 | `job_queue.py` sobrecarregado (2.229 LOC) — config ARQ, pool Redis, jobs misturados | 6h | @dev + @qa |
| DEBT-FE-004 | 12 banners na busca — cognitive overload sem sistema de prioridade | 8h | @dev + @ux-design-expert |

**Nota:** DEBT-SYS-005 e DEBT-SYS-006 compartilham ARQ + Redis pool e devem ser decompostos juntos.

## Criterios de Aceite

### Decomposicao pncp_client.py (10h)
- [ ] `pncp_client.py` decomposto em:
  - `clients/pncp/async_client.py` — cliente async principal
  - `clients/pncp/sync_client.py` — fallback sincrono (wrapped em `asyncio.to_thread()`)
  - `clients/pncp/circuit_breaker.py` — logica de circuit breaker extraida
  - `clients/pncp/retry.py` — retry com exponential backoff
  - `clients/pncp/__init__.py` — re-exports facade
- [ ] `pncp_client.py` original mantem re-exports para backward-compat
- [ ] Circuit breaker extraido com canary test independente
- [ ] Nenhum submodulo excede 700 LOC

### Decomposicao cron_jobs.py + job_queue.py (14h)
- [ ] `cron_jobs.py` decomposto em:
  - `jobs/cron/cache_cleanup.py`
  - `jobs/cron/canary.py`
  - `jobs/cron/session_cleanup.py`
  - `jobs/cron/trial_emails.py`
  - `jobs/cron/scheduler.py` — registro centralizado de cron jobs
- [ ] `job_queue.py` decomposto em:
  - `jobs/queue/config.py` — configuracao ARQ
  - `jobs/queue/redis_pool.py` — pool Redis dedicado
  - `jobs/queue/definitions.py` — definicoes de jobs
  - `jobs/queue/worker.py` — WorkerSettings
- [ ] Arquivos originais mantem facade re-exports
- [ ] Worker lifecycle testado: startup → jobs → graceful shutdown

### BannerStack com Prioridade (8h)
- [ ] Componente `BannerStack` criado com sistema de prioridade
- [ ] Maximo 2 banners exibidos simultaneamente (priorizacao por severidade)
- [ ] Banners restantes acessiveis via "Ver mais alertas" expandivel
- [ ] Prioridade: error > warning > info > success
- [ ] 12 banners existentes migrados para usar BannerStack
- [ ] `aria-live` preservado nos banners visiveis
- [ ] Cognitive load score reduzido de 7/10 para <= 5/10

### Qualidade
- [ ] 33 testes diretos + 73 indiretos do pncp_client passam
- [ ] 36 testes cron_jobs passam
- [ ] 48 testes job_queue passam
- [ ] Suite completa: 5131+ backend + 2681+ frontend passam
- [ ] Zero jobs perdidos em teste de graceful shutdown

## Testes Requeridos

- [ ] `pytest -k "test_pncp_client" --timeout=30` — 33+ testes passam
- [ ] `pytest -k "test_cron" --timeout=30` — 36 testes passam
- [ ] `pytest -k "test_job_queue" --timeout=30` — 48 testes passam
- [ ] Worker lifecycle E2E: startup → enqueue job → execute → graceful shutdown
- [ ] Circuit breaker: teste de abertura apos 15 falhas + teste de cooldown (60s)
- [ ] Canary test PNCP real em horario de baixo trafego
- [ ] Frontend: BannerStack unit test — 3+ banners ativos → exibe top 2
- [ ] Frontend: BannerStack a11y — aria-live presente nos banners visiveis
- [ ] `npm test` — suite completa frontend

## Notas Tecnicas

- **DEBT-SYS-005 + SYS-006 juntos:** Compartilham ARQ + Redis pool. Decompor separadamente criaria dependencias circulares. Estrutura `jobs/` unificada resolve ambos.
- **ARQ mock:** Usar conftest `_isolate_arq_module` autouse fixture. NUNCA fazer `sys.modules["arq"] = MagicMock()` sem cleanup.
- **pncp_client sync fallback:** O `asyncio.to_thread()` wrapper DEVE ser preservado — nunca bloquear event loop do Gunicorn.
- **BannerStack:** Considerar contexto do usuario (plano, trial status) para priorizacao alem de severidade.

## Dependencias

- DEBT-201 (Sprint 2) e DEBT-203 (Sprint 4) devem estar completas para evitar conflitos em decomposicao
- DEBT-FE-004 (BannerStack) bloqueia DEBT-FE-003 (aria-live) que ja foi resolvido no Sprint 1 para os banners existentes — aqui e para os banners consolidados
