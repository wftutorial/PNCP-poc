# HARDEN-011: SSE Proxy Inactivity Timeout

**Severidade:** ALTA
**Esforço:** 20 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

Frontend SSE proxy em `app/api/buscar-progress/route.ts` usa `bodyTimeout: 0` (correto para SSE) mas não tem inactivity timeout no reader loop. Se backend para de enviar eventos e client desconecta, o reader.read() fica bloqueado até Railway matar (300s).

## Critérios de Aceitação

- [ ] AC1: Inactivity timeout de 60s no reader loop (Promise.race)
- [ ] AC2: Timeout gera erro SSE `SSE_INACTIVITY_TIMEOUT` ao client
- [ ] AC3: Cleanup de AbortController no timeout
- [ ] AC4: Teste unitário valida timeout
- [ ] AC5: Zero regressions

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
