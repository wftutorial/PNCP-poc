# HARDEN-026: localStorage Quota Check com Fallback

**Severidade:** BAIXA
**Esforço:** 10 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

Se usuário acumula 50+ searches (cada 100KB JSON), localStorage (5-10MB) pode exceder quota. Writes falham silenciosamente e searches salvas desaparecem ao recarregar.

## Critérios de Aceitação

- [ ] AC1: Wrapper `safeSetItem()` com try/catch no setItem
- [ ] AC2: Em caso de QuotaExceededError, evict items mais antigos
- [ ] AC3: Usado em todos os localStorage writes do app
- [ ] AC4: Teste unitário

## Arquivos Afetados

- `frontend/lib/storage.ts` ou utils — novo helper
- `frontend/` — substituir localStorage.setItem direto
