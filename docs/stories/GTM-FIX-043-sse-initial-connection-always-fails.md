# GTM-FIX-043 — SSE Initial Connection Falha Sempre (Reconnect Resolve)

**Status:** Done
**Priority:** P1 — High (toda busca gera erro + retry desnecessário, degrada experiência)
**Severity:** Frontend + Backend — timing de SSE connect vs search enqueue causa falha sistemática
**Created:** 2026-02-25
**Sprint:** GTM Stabilization
**Relates to:** GTM-STAB-006 (SSE proxy resilience), CRIT-012 (SSE heartbeat), GTM-STAB-009 (async search)
**Found:** Playwright E2E validation 2026-02-25

---

## Problema

Em **100% das buscas testadas** via Playwright (2026-02-25), o console mostra:

```
[WARNING] SSE initial connection failed
[INFO] SSE reconnecting in 3000ms (attempt 1/3)
```

Seguido de reconexão bem-sucedida. O fluxo funciona, mas com **3 segundos de atraso desnecessário** e um erro intermediário que:

1. Pode triggerar o error alert (GTM-FIX-040)
2. Incrementa métricas de erro no Sentry (`smartlic_sse_connection_errors_total`)
3. Adiciona 3s de latência percebida pelo usuário
4. Consome 1 dos 3 retries antes de começar a receber dados

### Causa raiz provável:

Com async search (STAB-009), o fluxo é:
1. Frontend faz `POST /buscar` → backend retorna 202 + `search_id`
2. Frontend abre SSE `GET /buscar-progress/{search_id}`
3. Backend registra tracker no ProgressTracker

**Race condition:** Se step 2 acontece antes de step 3 completar, o SSE endpoint não encontra o tracker → retorna erro → frontend retry → agora tracker existe → funciona.

No modelo sync antigo, o tracker era criado ANTES do SSE connect. No modelo async, o tracker é criado pelo worker job que pode levar alguns ms para iniciar.

### Impacto:

- 100% das buscas sofrem 3s de atraso desnecessário
- Métricas de SSE error são infladas (não representam erros reais)
- Error alert pode piscar brevemente antes dos resultados
- 1/3 dos retries consumido sem necessidade

---

## Acceptance Criteria

### AC1: Backend — wait-for-tracker no SSE endpoint
- [x] `routes/search.py` SSE endpoint: quando tracker não encontrado, aguardar até 5s com polling 200ms
- [x] Se tracker aparece durante o wait: iniciar stream normalmente
- [x] Se timeout (5s) sem tracker: retornar SSE error event (não HTTP error)
- [x] Nota: CRIT-012 já implementou wait-for-tracker com heartbeat — verificar se está funcionando no modo async

### AC2: Frontend — grace period antes de considerar SSE failure
- [x] `useSearchSSE.ts`: após POST 202, aguardar 2s antes de abrir SSE connection
- [x] OU: tratar primeiro SSE failure como "expected" e não incrementar retry counter
- [x] OU: implementar SSE connect com immediate retry (0ms delay) no primeiro failure

### AC3: Diagnóstico — confirmar causa raiz
- [x] Adicionar log no SSE endpoint: `search_id={id} tracker_found={bool} elapsed_ms={N}`
- [x] Verificar se o wait-for-tracker do CRIT-012 está ativo no modo async
- [x] Medir tempo entre POST 202 response e tracker registration no worker

### AC4: Eliminar SSE error noise
- [x] Se SSE connect falha por "tracker not found" e search é async: não logar como WARNING
- [x] Não incrementar `smartlic_sse_connection_errors_total` para expected race condition
- [x] Frontend: não mostrar error state para first SSE failure em async mode

### AC5: Testes
- [x] Backend: test SSE endpoint com tracker delay (simulate async worker startup)
- [x] Frontend: test async mode SSE connection → no error shown on first attempt
- [x] Integration: test POST 202 → SSE connect → verify no spurious errors

---

## Arquivos Envolvidos

| Arquivo | Ação |
|---------|------|
| `backend/routes/search.py` | AC1+AC3: SSE wait-for-tracker no async mode |
| `backend/progress.py` | AC1: verify tracker registration timing |
| `frontend/app/buscar/hooks/useSearchSSE.ts` | AC2+AC4: grace period ou smart retry |
| `frontend/app/buscar/hooks/useSearch.ts` | AC4: suppress error for async SSE race |
| `frontend/app/api/buscar-progress/[id]/route.ts` | AC3: structured logging |

---

## Decisões Técnicas

- **Wait-for-tracker é a fix correta** — O backend deve aguardar o tracker existir antes de tentar stream. 5s é mais que suficiente para o worker iniciar.
- **Grace period no frontend é paliativo** — Funciona, mas mascara o problema real (timing no backend).
- **CRIT-012 precedente** — Já implementou wait-for-tracker para o modo sync. Verificar se está ativo no async.

## Estimativa
- **Esforço:** 3-4h (diagnóstico + fix + testes)
- **Risco:** Médio (toca SSE lifecycle, async timing)
- **Squad:** @dev (backend + frontend) + @qa (testes)
