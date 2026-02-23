# CRIT-031 — Dashboard Skeleton Permanente + usePlan Retry Storm

**Severity:** P2 — Important
**Origin:** UX Production Audit 2026-02-23 (Observações de Infra)
**Parent:** CRIT-028, CRIT-018
**Status:** [x] Completed

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
- [x] **AC1**: Após 10s sem resposta do analytics, skeletons resolvem para empty state
- [x] **AC2**: Empty state exibe "Dados temporariamente indisponíveis. Tente novamente em alguns minutos."
- [x] **AC3**: Botão "Tentar novamente" no empty state
- [x] **AC4**: Se dados parciais disponíveis em cache, exibi-los com badge "Dados podem estar desatualizados"

### usePlan Backoff
- [x] **AC5**: `usePlan` usa `useFetchWithBackoff` (ou lógica equivalente de backoff exponencial)
- [x] **AC6**: Máximo 3 retries com backoff (2s → 4s → 8s), não 6 retries instantâneos
- [x] **AC7**: Console warnings limitados a max 3 (não 12)

### Testes
- [x] **AC8**: Teste: analytics API retorna 503 → após 10s, dashboard mostra empty state
- [x] **AC9**: Teste: usePlan com backend 503 → max 3 retries com delays crescentes
- [x] **AC10**: Zero regressão no baseline

## Arquivos Modificados

### Dashboard Skeletons
- `frontend/app/dashboard/page.tsx` — maxRetries 5→3, error state split (!data → empty state, data → stale banner), loading guard `!data`
- `frontend/__tests__/crit-031-dashboard-skeleton.test.tsx` — NEW: 13 tests (AC1-AC4)
- `frontend/__tests__/dashboard.test.tsx` — Updated for new copy/testids
- `frontend/__tests__/dashboard-retry.test.tsx` — Updated for maxRetries=3 and new copy/testids

### usePlan Backoff
- `frontend/hooks/usePlan.ts` — Full refactor: useFetchWithBackoff integration, stable deps, cache fallback via useMemo
- `frontend/__tests__/crit-031-usePlan-backoff.test.tsx` — NEW: 6 tests (AC5-AC7 + degradation)
- `frontend/__tests__/crit-028-dashboard-skeletons.test.tsx` — Updated for backoff timing

## Implementação

### Dashboard (AC1-AC4)
- `maxRetries: 5` → `maxRetries: 3` — resolves faster (~6s for fast 503, vs ~30s before)
- Error state split: `error && hasExhaustedRetries && !data` → empty state; `error && hasExhaustedRetries && data` → stale banner
- Empty state copy: "Dados temporariamente indisponíveis. Tente novamente em alguns minutos."
- Stale banner: yellow dot + "Dados podem estar desatualizados" + "Tentar novamente" button
- Loading guard: `loading && !data` prevents skeletons when previous data exists

### usePlan (AC5-AC7)
- Replaced manual fetch+setState with `useFetchWithBackoff` (maxRetries=3, 2s→4s→8s)
- Stable dependencies: `[session?.access_token, user?.id]` instead of `[session, user]`
- Cache fallback via `useMemo` (not in catch block) — fires once per error state change
- Console warnings: 1 per error (not 12) via `useEffect` on `[fetchError, data]`
- Degradation detection (CRIT-028) preserved inside fetchFn

### Test Results
- 19 new tests (13 dashboard + 6 usePlan), all pass
- 49 fail / 2443 pass — matches pre-existing baseline, zero regressions

## Referência

- Screenshots: `audit-02-dashboard.jpeg`, `audit-04-dashboard-15s.jpeg`
- Console logs: 12 usePlan warnings em /conta
- Audit doc: `docs/sessions/2026-02/2026-02-23-ux-production-audit.md`
