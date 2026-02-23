# CRIT-031 — Dashboard Skeleton Permanente + usePlan Retry Storm

**Severity:** P2 — Important
**Origin:** UX Production Audit 2026-02-23 (Observações de Infra)
**Parent:** CRIT-028, CRIT-018
**Status:** [ ] Pending

---

## Problema

Dois gaps nas correções de CRIT-028 e CRIT-018:

### Gap 1: Dashboard Skeletons Eternos (CRIT-028 incompleto)
Quando o backend retorna 503 persistente, o dashboard exibe skeleton loaders indefinidamente (15s+ observado, nunca resolvem). O CRIT-028 corrigiu o retry storm e adicionou fallback no `usePlan`, mas o dashboard page inteiro fica em skeleton porque o endpoint `/api/analytics?endpoint=summary` falha.

**Esperado:** Após N segundos ou N retries, skeletons resolvem para:
- Empty state com mensagem "Dados temporariamente indisponíveis"
- Ou dados parciais do cache

### Gap 2: usePlan Retry Storm (CRIT-018 incompleto)
A página `/conta` gera 12 console warnings (`[usePlan] Backend error — using cached plan`) em rápida sucessão — 6 fetch attempts. O hook `useFetchWithBackoff` de CRIT-018 não foi aplicado ao `usePlan`.

**Console observado em /conta:**
```
[usePlan] Backend error — using cached plan (x6)
[usePlan] Failed to fetch plan info: Failed... (x6)
```

## Acceptance Criteria

### Dashboard Skeletons
- [ ] **AC1**: Após 10s sem resposta do analytics, skeletons resolvem para empty state
- [ ] **AC2**: Empty state exibe "Dados temporariamente indisponíveis. Tente novamente em alguns minutos."
- [ ] **AC3**: Botão "Tentar novamente" no empty state
- [ ] **AC4**: Se dados parciais disponíveis em cache, exibi-los com badge "Dados podem estar desatualizados"

### usePlan Backoff
- [ ] **AC5**: `usePlan` usa `useFetchWithBackoff` (ou lógica equivalente de backoff exponencial)
- [ ] **AC6**: Máximo 3 retries com backoff (2s → 4s → 8s), não 6 retries instantâneos
- [ ] **AC7**: Console warnings limitados a max 3 (não 12)

### Testes
- [ ] **AC8**: Teste: analytics API retorna 503 → após 10s, dashboard mostra empty state
- [ ] **AC9**: Teste: usePlan com backend 503 → max 3 retries com delays crescentes
- [ ] **AC10**: Zero regressão no baseline

## Arquivos Prováveis

### Dashboard Skeletons
- `frontend/app/dashboard/page.tsx` — skeleton rendering, timeout logic
- `frontend/hooks/useFetchWithBackoff.ts` — reuse for dashboard fetches

### usePlan Backoff
- `frontend/hooks/usePlan.ts` — plan fetch logic
- `frontend/hooks/useFetchWithBackoff.ts` — backoff hook to integrate

## Referência

- Screenshots: `audit-02-dashboard.jpeg`, `audit-04-dashboard-15s.jpeg`
- Console logs: 12 usePlan warnings em /conta
- Audit doc: `docs/sessions/2026-02/2026-02-23-ux-production-audit.md`
