# HARDEN-011: SSE Proxy Inactivity Timeout

**Severidade:** ALTA
**Esforço:** 20 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

Frontend SSE proxy em `app/api/buscar-progress/route.ts` usa `bodyTimeout: 0` (correto para SSE) mas não tem inactivity timeout no reader loop. Se backend para de enviar eventos e client desconecta, o reader.read() fica bloqueado até Railway matar (300s).

## Critérios de Aceitação

- [x] AC1: Inactivity timeout de 120s no reader loop (Promise.race) — configurable via `SSE_INACTIVITY_TIMEOUT_MS` env var
- [x] AC2: Timeout gera erro SSE `SSE_INACTIVITY_TIMEOUT` ao client com mensagem "Conexão inativa por tempo prolongado"
- [x] AC3: Cleanup de reader.cancel() no timeout + structured HARDEN-011 logging
- [x] AC4: 5 testes unitários validam timeout, error event, logging, normal flow, e default value
- [x] AC5: Zero regressions — 27/27 SSE proxy tests pass

## Solução

```typescript
const INACTIVITY_TIMEOUT_MS = 60_000;
while (true) {
  const { done, value } = await Promise.race([
    reader.read(),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('SSE_INACTIVITY_TIMEOUT')), INACTIVITY_TIMEOUT_MS)
    ),
  ]);
  if (done) break;
  // process...
}
```

## Arquivos Afetados

- `frontend/app/api/buscar-progress/route.ts`
- `frontend/__tests__/` — novo teste
