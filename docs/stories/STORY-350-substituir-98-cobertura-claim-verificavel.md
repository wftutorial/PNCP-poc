# STORY-350: Substituir "+98% cobertura" por claim verificável

**Prioridade:** P0
**Tipo:** fix (copy) + feature (métrica)
**Sprint:** Imediato
**Estimativa:** M
**Origem:** Conselho CTO Advisory Board — Auditoria de Promessas (2026-03-01)
**Dependências:** Nenhuma
**Bloqueado por:** —
**Bloqueia:** —
**Paralelo com:** STORY-352

---

## Contexto

A landing page exibe "+98% das oportunidades públicas do Brasil" em múltiplos locais. O SmartLic usa 3 fontes (PNCP, PCP v2, ComprasGov). Competidores como Effecti agregam 1.400+ portais. O claim é refutável e não tem infraestrutura de medição.

## Promessa Afetada

> "+98% das oportunidades públicas federais e estaduais"

## Causa Raiz

Claim quantificado sem fonte de dados. 3 fontes vs 1.400+ portais de competidores torna a promessa refutável por qualquer prospect que use Effecti.

## Critérios de Aceite

- [ ] AC1: Substituir "+98%" por "Fontes oficiais consolidadas" em `DataSourcesSection.tsx` (linhas 31, 57, 59, 73)
- [ ] AC2: Substituir "+98% cobertura" por "Cobertura nacional via fontes oficiais" em `valueProps.ts:172`
- [ ] AC3: Criar métrica `smartlic_sources_bids_fetched_total` (labels: source, uf) em `metrics.py` — permite calcular cobertura real no futuro
- [ ] AC4: Adicionar "+98%" ao array BANNED_PHRASES em `valueProps.ts`
- [ ] AC5: Atualizar testes e2e que verificam "+98%" (`landing-page.spec.ts`, `institutional-pages.spec.ts`)
- [ ] AC6: Criar card no `/admin` mostrando "Fontes ativas" com status real de cada fonte (UP/DOWN/DEGRADED)
- [ ] AC7: Documentar em `proofPoints` (comparisons.ts) a cobertura real: "3 fontes oficiais federais + portal de compras públicas"

## Arquivos Afetados

- `frontend/app/components/landing/DataSourcesSection.tsx`
- `frontend/lib/copy/valueProps.ts`
- `frontend/lib/copy/comparisons.ts`
- `backend/metrics.py`
- `frontend/e2e-tests/landing-page.spec.ts`
- `frontend/e2e-tests/institutional-pages.spec.ts`

## Validação

| Métrica | Threshold | Onde medir |
|---------|-----------|------------|
| `smartlic_sources_bids_fetched_total` | >0 para todas as 3 fontes em 24h | Prometheus |

## Notas

- Claim "+98%" não tem origem mensurável e pode ser 60% ou 95%.
- O repositionamento para "fontes oficiais consolidadas" é mais defensável e não perde poder comercial.
