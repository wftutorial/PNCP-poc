# SAB-009: Dashboard — erro 500 em /api/organizations/me + badge "0%" sem contexto

**Origem:** UX Premium Audit P1-06
**Prioridade:** P1 — Alto
**Complexidade:** M (Medium)
**Sprint:** SAB-P1
**Owner:** @dev
**Screenshots:** `ux-audit/22-dashboard.png`, `ux-audit/23-dashboard-bottom.png`

---

## Problema

Três issues na página de Dashboard:

| Issue | Detalhe |
|-------|---------|
| **HTTP 500** | Console error: `GET /api/organizations/me` retorna 500 |
| **Badge "0%"** | Canto superior direito — sem tooltip ou explicação do que significa |
| **"64h economizadas"** | KPI "Horas Economizadas: 64h" — cálculo não explicado, parece arbitrário |

---

## Critérios de Aceite

### Erro 500

- [ ] **AC1:** Diagnosticar causa do `GET /api/organizations/me` 500 — rota existe? Table `organizations` existe no Supabase?
- [ ] **AC2:** Se a feature de organizations não está implementada: remover chamada do frontend (não chamar endpoint inexistente)
- [ ] **AC3:** Se está implementada mas com bug: corrigir o endpoint
- [ ] **AC4:** Zero erros de console (HTTP 4xx/5xx) na página `/dashboard` após fix

### Badge "0%"

- [ ] **AC5:** Identificar o que o badge "0%" representa (perfil completo? quota usada? algum score?)
- [ ] **AC6:** Se representa "Perfil de Licitante" completude: adicionar tooltip "Perfil de Licitante: 0% — Preencha para melhorar análises"
- [ ] **AC7:** Se não tem utilidade clara: remover o badge da interface

### KPI "Horas Economizadas"

- [ ] **AC8:** Documentar o cálculo de "Horas Economizadas" (como 64h é calculado?)
- [ ] **AC9:** Adicionar tooltip no KPI explicando a metodologia (ex: "Estimativa baseada em X buscas × Y minutos por busca manual")

---

## Arquivos Prováveis

- `frontend/app/dashboard/page.tsx` — página do dashboard
- `frontend/app/api/organizations/route.ts` — proxy (se existir)
- `backend/routes/` — endpoint organizations (se existir)

## Notas

- O erro 500 pode estar relacionado a STORY-331 (apply-organizations-migration). Verificar se a migration foi aplicada.
- Se `organizations` é uma feature futura não implementada, o frontend não deveria chamar o endpoint.
