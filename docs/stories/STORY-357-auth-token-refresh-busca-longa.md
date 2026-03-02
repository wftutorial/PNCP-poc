# STORY-357: Auth token refresh durante busca longa

**Prioridade:** P1
**Tipo:** fix
**Sprint:** Sprint 2
**Estimativa:** M
**Origem:** Conselho CTO Advisory Board — Auditoria de Promessas (2026-03-01)
**Dependências:** Nenhuma
**Bloqueado por:** —
**Bloqueia:** —
**Paralelo com:** STORY-355, STORY-356

---

## Contexto

Buscas podem levar 60-110s. Se o token JWT do Supabase expira durante a busca (default 1h), o proxy usa o header com token expirado, backend rejeita 401, e o usuário vê "Autenticação necessária" sem possibilidade de retry automático. A sessão é perdida.

## Promessa Afetada

> "Produtivo desde a primeira sessão" (UX)
> "Alta disponibilidade" (confiança)

## Causa Raiz

Token refresh no proxy `/api/buscar/route.ts` usa `getRefreshedToken()` que pode falhar, caindo para header com token potencialmente expirado. Sem refresh-and-retry, sessões expiram silenciosamente durante buscas longas.

## Critérios de Aceite

- [x] AC1: No proxy `/api/buscar/route.ts`, implementar refresh-and-retry: se backend retorna 401, chamar `supabase.auth.refreshSession()` e reenviar request (max 1 retry)
- [x] AC2: Limite de 1 retry por request (evitar loop infinito)
- [x] AC3: Se refresh falhar, redirecionar para `/login` com query param `?returnTo=/buscar`
- [x] AC4: No `useSearch.ts`, detectar 401 e mostrar mensagem amigável: "Sua sessão expirou. Reconectando..." (em vez de erro genérico)
- [x] AC5: Implementar pre-emptive refresh: se token expira em < 5min, refreshar antes de iniciar busca
- [x] AC6: Testes: mock de token expirado durante busca → refresh automático bem-sucedido
- [x] AC7: Testes: mock de refresh falhando → redirect para /login com returnTo

## Arquivos Afetados

- `frontend/app/api/buscar/route.ts` — AC1/AC2/AC3: refresh-and-retry on 401, max 1 auth retry
- `frontend/app/buscar/hooks/useSearch.ts` — AC4: friendly session expired message, AC5: pre-emptive refresh
- `frontend/__tests__/api/buscar-auth-refresh.test.ts` — NEW: 4 proxy tests (AC6/AC7)
- `frontend/__tests__/hooks/useSearch-auth-refresh.test.ts` — NEW: 4 client tests (AC4/AC5/AC7)
- `frontend/__tests__/hooks/useSearch.test.ts` — Added supabase mock
- `frontend/__tests__/hooks/useSearch-failures.test.ts` — Added supabase mock
- `frontend/__tests__/hooks/useSearch-async.test.ts` — Added supabase mock
- `frontend/__tests__/hooks/useSearch-sab001.test.ts` — Added supabase mock
- `frontend/__tests__/hooks/useSearch-sab005.test.ts` — Added supabase mock
- `frontend/__tests__/hooks/useSearch-sse-fix.test.ts` — Already had supabase mock (no change)
- `frontend/__tests__/retry-unified.test.tsx` — Added supabase mock
- `frontend/__tests__/gtm-fix-033-sse-resilience.test.tsx` — Added supabase mock
- `frontend/__tests__/story-257b/ux-transparente.test.tsx` — Added supabase mock

## Validação

| Métrica | Threshold | Onde medir |
|---------|-----------|------------|
| Taxa de 401 não-recuperados | <0.1% das buscas | Sentry/logs |
