# STORY-352: Substituir "24/7" por promessa realista de disponibilidade

**Prioridade:** P0
**Tipo:** fix (copy)
**Sprint:** Imediato
**Estimativa:** S
**Origem:** Conselho CTO Advisory Board — Auditoria de Promessas (2026-03-01)
**Dependências:** Nenhuma
**Bloqueado por:** —
**Bloqueia:** —
**Paralelo com:** STORY-350

---

## Contexto

A comparison table e TrustSignals prometem "Disponível 24/7" e "Suporte prioritário 24/7". O sistema teve CRIT-SIGSEGV (crash loop), CRIT-046 (connection pool exhaustion), CRIT-012 (SSE heartbeat gap). Não existe suporte humano 24h para equipe pré-revenue.

## Promessas Afetadas

> "Disponível 24/7"
> "Suporte prioritário 24/7"

## Causa Raiz

Promessa de 100% uptime e suporte humano 24h é inverificável e falsa para startup pré-revenue. Uptime realista para early-stage SaaS: 99-99.5%.

## Critérios de Aceite

- [ ] AC1: Substituir "Disponível 24/7" por "Alta disponibilidade com monitoramento contínuo" em `comparisons.ts:104`
- [ ] AC2: Substituir "Suporte prioritário 24/7" por "Suporte dedicado para assinantes" em `TrustSignals.tsx:139`
- [ ] AC3: Adicionar "24/7" ao BANNED_PHRASES em `valueProps.ts`
- [ ] AC4: Criar Prometheus gauge `smartlic_uptime_pct_30d` calculado a partir dos health checks existentes
- [ ] AC5: Na página `/admin`, exibir uptime real dos últimos 30 dias
- [ ] AC6: Atualizar testes e2e que verificam texto "24/7" se existirem
- [ ] AC7: Revisar `ajuda/page.tsx` para remover "24 horas" se presente

## Arquivos Afetados

- `frontend/lib/copy/comparisons.ts`
- `frontend/components/subscriptions/TrustSignals.tsx`
- `frontend/lib/copy/valueProps.ts`
- `frontend/app/ajuda/page.tsx`

## Validação

| Métrica | Threshold | Onde medir |
|---------|-----------|------------|
| `smartlic_uptime_pct_30d` | >99% para claim "alta disponibilidade" | /admin page |

## Notas

- "Alta disponibilidade" é defensável e comercialmente forte sem ser quantitativamente refutável.
- Quando atingir 99.9% consistente por 3 meses, pode publicar SLO formal.
