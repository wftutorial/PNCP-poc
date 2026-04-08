# EPIC: Resolucao de Debitos Tecnicos — SmartLic

**Epic ID:** EPIC-TD-2026
**Owner:** @architect (Aria)
**Status:** Planning
**Created:** 2026-04-08
**Timeline:** 20 semanas (5 fases)
**Budget:** R$ 18.000 (Fases 1-4) + R$ 30.000 (Fase 5, sob demanda)
**Supersedes:** Previous epic EPIC-DEBT-2026 (54 items / 6 batches / ~196h) -- assessment v2.0 re-validated by 4 specialists, corrected to 61 items across 5 phases.

## Objetivo

Resolver 61 debitos tecnicos identificados no Brownfield Discovery (Assessment v2.0, validado por @architect, @data-engineer, @ux-design-expert, @qa), priorizando itens P0 (critical path ~9h) e P1 (foundation ~65h), garantindo estabilidade operacional e preparando a plataforma para escala. O custo de nao agir e estimado em R$ 161.800 - R$ 229.800/ano em riscos acumulados.

**Justificativa de negocio:**
- **Operacional:** Supabase FREE tier (500MB) vs datalake ~3GB — risco de parada total do sistema de busca
- **Performance:** Indice composto ausente causa 2-3x mais latencia em toda busca ao datalake
- **Seguranca:** service_role usado para operacoes de usuario + RPCs sem auditoria de auth.uid()
- **Manutenibilidade:** 3.775 LOC em hooks de busca + 3 arquivos backend >1.300 LOC cada
- **Mobile UX:** Touch targets 28px (minimo 44px), scroll jank no SSE, conteudo cortado por BottomNav

## Escopo

### Incluido
- Todos os 61 debitos catalogados no Assessment Final v2.0
- 5 fases de resolucao, ordenadas por risco e ROI
- 4 itens P0 (Criticos — Semanas 1-2): Storage, indice, bloat, retencao
- 12 itens P1 (Altos — Semanas 2-6): Backup, alertas, hooks, seguranca, touch targets
- 15 itens P2 (Medios — Semanas 5-8): Timeouts, backend refactoring, a11y, visual regression
- 12 itens P3 (Baixos — Semanas 9-12): Migration squash, cache, error boundaries
- 14 itens P4 (Backlog — Semanas 13-20): i18n, offline, Storybook (sob demanda)
- 4 itens Resolved (monitoramento apenas)

### Excluido
- Rewrite completo de arquitetura (apenas decomposicao incremental)
- Mudancas de stack (permanece FastAPI + Next.js)
- Novas features (exceto TD-037 saved filter presets, que e user-facing value direto)
- TD-048 i18n (100h, Brasil-only) e TD-049 offline (50h, sem demanda) — Fase 5 sob demanda

## Criterios de Sucesso

### Performance
| Metrica | Atual | Meta | Medicao |
|---------|-------|------|---------|
| `search_datalake` RPC latencia (p50) | Sem baseline | 50-70% reducao apos TD-019 | `EXPLAIN ANALYZE` antes/depois |
| PNCP API disponibilidade | 94% | >= 95% | Prometheus `smartlic_pncp_health_*` |
| Cache hit rate | 65-75% | >= 75% sustentado | Prometheus `smartlic_cache_hit_rate` |
| DB size | ~500MB (estimado) | Monitorado, < 80% do limite do tier | `pg_database_size()` semanal |
| Search page hooks total lines | 3.775 | < 2.500 apos refatoracao | `wc -l frontend/app/buscar/hooks/*.ts` |

### Cobertura
| Area | Atual | Meta | Gate |
|------|-------|------|------|
| Backend test coverage | >= 70% (CI gate) | Manter >= 70% | `pytest --cov` |
| Frontend test coverage | >= 60% (CI gate) | Manter >= 60% | `npm run test:coverage` |
| a11y automated coverage | 0% | >= 80% dos top 10 componentes | jest-axe apos TD-056 |
| Visual regression | 0% | 10 telas criticas | Chromatic apos TD-036 |
| Dependency vulnerability scan | Nao em CI | 0 high/critical findings | pip-audit + npm audit apos TD-058 |

### Seguranca
| Check | Atual | Meta |
|-------|-------|------|
| RPCs com auth.uid() validado | Desconhecido | 100% das user-scoped RPCs (apos TD-059) |
| Dependencies com CVEs conhecidas | Desconhecido | 0 high/critical (apos TD-058) |
| Secrets no git history | Desconhecido | 0 (apos TD-060) |

## Stories

### Fase 1: Quick Wins (Semanas 1-2) — ~10h, R$ 1.500
- **STORY-TD-001:** [Quick Wins P0 — Eliminar riscos de parada operacional](story-TD-001-quick-wins-p0.md)
  - TD-033: Supabase Pro upgrade (0.5h)
  - TD-019: Indice composto pncp_raw_bids (1h)
  - TD-020: Soft-delete bloat cleanup (3h)
  - TD-025/026/027/NEW-001: 4 retention policies (2h)
  - TD-022: content_hash COMMENT fix (0.5h)
  - TD-052: FeedbackButtons touch target (1.5h)
  - TD-053: CompatibilityBadge font size (0.5h)
  - TD-059: RPC auth.uid() audit (4h)

### Fase 2: Foundation (Semanas 3-6) — ~16h, R$ 2.400
- **STORY-TD-002:** [DB Foundation — Backup, integridade e cleanup](story-TD-002-db-foundation.md)
  - TD-034: Weekly pg_dump + PITR (2h)
  - TD-020/NEW-002: Soft-delete investigation + cleanup cron (3h)
  - TD-021: plan_type CHECK -> FK migration (4h)
  - TD-NEW-002: purge_old_bids() fix (1h)
- **STORY-TD-003:** [Backend Foundation — Alertas, timeouts e async](story-TD-003-backend-foundation.md)
  - TD-061: Ingestion failure alerting (3h)
  - TD-015: Railway/Gunicorn timeout alignment (2h)
  - TD-029: Alert cron asyncio.gather (2h)

### Fase 3: Hardening (Semanas 5-8) — ~54h, R$ 8.100
- **STORY-TD-004:** [Frontend Hardening — Hooks decomposition e filtros salvos](story-TD-004-frontend-hardening.md)
  - TD-050: useSearchExecution 852 LOC -> 3 hooks (18h)
  - TD-035: useSearchFilters 607 LOC -> 5 hooks (14h)
  - TD-037: Saved filter presets feature (22h)
- **STORY-TD-005:** [Security & Backend Hardening — Scanning e refactoring](story-TD-005-security-qa.md)
  - TD-058: pip-audit + npm audit in CI (4h)
  - TD-007: quota.py split (12h)
  - TD-008: consolidation.py split (8h)

### Fase 4: Polish (Semanas 9-12) — ~44h, R$ 6.600
- **STORY-TD-006:** Quality Automation — Visual regression, a11y, LLM modularizacao
  - TD-036: Chromatic visual regression (18h)
  - TD-056: jest-axe a11y testing (14h)
  - TD-009: llm_arbiter.py split (8h)
  - TD-058: Dependency scanning CI integration (4h)

### Fase 5: Long-term (Semanas 13-20) — ~200h, sob demanda
- **STORY-TD-007:** Long-term Backlog
  - TD-016: Migration squash 121 -> ~10 (24h) — APOS todas migracoes Fases 1-4
  - TD-005: Per-user Supabase tokens (16h) — apos TD-059
  - TD-051: Search hooks architecture docs + XState (16h)
  - TD-011: Railway auto-scaling (4h)
  - TD-046: useDeferredValue SSE scroll (10h)
  - TD-043: Storybook (28h) — se equipe FE >= 3
  - TD-048/049: i18n + offline (150h) — adiado indefinidamente
  - Demais P3/P4: ~30h oportunisticos

## Riscos

| Risco | Severidade | Mitigacao |
|-------|------------|-----------|
| DB storage exhaustion cascade (TD-033 + TD-020 + TD-025/026/027) | CRITICAL | Fase 1 executar esta semana — upgrade + retencao |
| Hook decomposition quebra testes existentes | HIGH | Facade pattern preserva imports. Full test suite apos cada move. |
| Migration squash (TD-016) invalida checkpoints de dev | HIGH | MUST ser LAST apos todas migracoes Fases 1-4 |
| Silent request death sem Sentry trace (TD-015 + TD-011) | HIGH | Fase 2: alinhar timeouts + middleware deteccao |
| Backend decomposition quebra imports de teste | MEDIUM | 1 arquivo por vez, full test suite, `__init__.py` facade |
| Perda de dados sem backup independente (TD-034 + TD-033) | HIGH | Fase 1 (Pro) + Fase 2 (pg_dump + PITR) |

## Dependencias

### Resolution Order (DAG)

```
FASE 1 (Semanas 1-2, parallel tracks):
  TD-033 Supabase Pro ────────> desbloqueia TD-034 (PITR + backup)
  TD-019 indice composto ────> sem dependencias, ship imediatamente
  TD-025/026/027 + NEW-001 ──> retencao, bundle 1 migracao
  TD-022 COMMENT fix ────────> ship com migracao de retencao
  TD-052 FeedbackButtons ───> ship independentemente (1.5h)
  TD-059 RPC audit ─────────> informa escopo TD-005

FASE 2 (Semanas 3-6):
  TD-034 pg_dump to S3 ─────> requer TD-033
  TD-020 + NEW-002 ─────────> deve preceder TD-016 (squash)
  TD-021 plan_type FK ──────> deve preceder TD-016 (squash)
  TD-029 alert cron async ──> independente
  TD-061 ingestion alerting > independente
  TD-015 timeout alignment ─> independente

FASE 3 (Semanas 7-12):
  TD-050 useSearchExecution ──> antes de TD-035
  TD-035 useSearchFilters ───> apos TD-050, antes de TD-037
  TD-037 saved filter presets > apos TD-035
  TD-007/008 backend splits ─> independente, paralelo com FE

FASE 4 (Semanas 9-12):
  TD-036 visual regression ──> paralelo com Fase 3
  TD-056 jest-axe ───────────> independente
  TD-058 dep scanning ──────> independente
  TD-009 llm_arbiter split ─> independente

FASE 5 (Semanas 13-20+):
  TD-016 migration squash ──> APOS todas migracoes Fases 1-4
  TD-005 per-user tokens ───> apos TD-059 definir escopo
  Demais P3/P4 ─────────────> oportunisticos
```

### Parallelization Tracks

| Track A (DB/Infra) | Track B (Frontend) | Track C (Security/CI) |
|--------------------|--------------------|-----------------------|
| TD-033 Pro upgrade | TD-052 touch targets | TD-059 RPC audit |
| TD-019 composite index | TD-050 hook split | TD-058 dep scanning |
| TD-025/026/027 retention | TD-035 hook split | TD-061 alerting |
| TD-034 pg_dump backup | TD-037 saved presets | TD-060 secret scanning |
| TD-020 bloat cleanup | TD-036 visual regression | |
| TD-021 FK migration | TD-056 jest-axe | |

Tres tracks paralelos podem executar simultaneamente se staffed.

## Documentos Relacionados

- [Assessment Tecnico Final v2.0](../prd/technical-debt-assessment.md) — 61 debitos detalhados, grafo de dependencias, matriz de priorizacao, criterios de sucesso
- [Relatorio Executivo v2.0](../reports/TECHNICAL-DEBT-REPORT.md) — Analise de custos, ROI 9:1, recomendacoes
- [Review Database](../reviews/db-specialist-review.md) — Validacao @data-engineer (Fase 5)
- [Review Frontend/UX](../reviews/ux-specialist-review.md) — Validacao @ux-design-expert (Fase 6)
- [QA Review](../reviews/qa-review.md) — Aprovacao final @qa (Fase 7)

---

*Epic v2.0 criado em 2026-04-08 por @pm (Morgan) durante Brownfield Discovery Phase 10 — Planning.*
*Baseado no Technical Debt Assessment Final v2.0 (61 items, 5 phases, ~320h total).*
*Supersedes previous epic (54 items / 6 batches / ~196h) based on specialist-reviewed assessment v2.0.*
