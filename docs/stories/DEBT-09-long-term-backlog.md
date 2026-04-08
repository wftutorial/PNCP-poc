# DEBT-09: Long-term Backlog

**Epic:** EPIC-TD-2026
**Fase:** 5 (Semanas 13-20+)
**Horas:** ~90h+
**Agente:** Varios
**Prioridade:** P3-P4

## Debitos Cobertos

| TD | Item | Horas | Trigger |
|----|------|-------|---------|
| TD-016 | Migration squash (121 -> ~10) | 24h | APOS todas as migrations de Fases 1-4 |
| TD-005 | Per-user Supabase tokens (SYS-023) | 16h | APOS DEBT-03 (RPC audit) |
| TD-051 | Search hooks docs + state machine (XState) | 16h | APOS DEBT-06 (refactor) |
| TD-033 | Supabase Pro upgrade | 0.5h | Quando DB > 350MB (hoje: 146MB) |
| TD-011 | Railway auto-scaling | 4h | Quando throughput exceder single-worker |
| TD-046 | SSE scroll jank mobile (useDeferredValue) | 10h | Quando mobile > 30% do trafego |
| TD-043 | Storybook | 28h | Quando time FE > 3 devs |

## Notas

Itens P3/P4 restantes (~20 items, ~80h) sao resolvidos oportunisticamente quando se trabalha em areas adjacentes. Nao requerem stories dedicadas.
