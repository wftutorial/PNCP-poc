# DEBT-117: Page Smoke Tests + LGPD Cascade Test

**Prioridade:** GTM-RISK (30 dias)
**Estimativa:** 16-20h
**Fonte:** Brownfield Discovery — @ux (FE-011), @qa (QA-NEW-01)
**Score Impact:** Integrity 7→8

## Contexto
Nenhuma das 5 principais páginas autenticadas (dashboard, pipeline, historico, onboarding, conta) tem teste de rendering. Ademais, não existe teste de integração que valide a chain de FK cascade para user deletion (LGPD compliance).

## Acceptance Criteria

### Page Smoke Tests (12-16h)
- [ ] AC1: Test render /dashboard — monta sem crash, mostra loading state
- [ ] AC2: Test render /pipeline — monta sem crash, mostra loading state
- [ ] AC3: Test render /historico — monta sem crash, mostra loading state
- [ ] AC4: Test render /onboarding — monta sem crash, mostra step 1
- [ ] AC5: Test render /conta — monta sem crash, mostra sidebar
- [ ] AC6: Test error state em cada página (mock API failure → mostra ErrorBoundary/error.tsx)
- [ ] AC7: Test loading state em cada página
- [ ] AC8: Todos os testes passam com mocks de auth/user context

### LGPD User Deletion Cascade (4h)
- [ ] AC9: Integration test backend: cria user, popula search_sessions, pipeline_items, search_results_cache, classification_feedback, user_oauth_tokens, google_sheets_exports
- [ ] AC10: Deleta user via Supabase Admin API (auth.users delete)
- [ ] AC11: Verifica que TODAS as rows dependentes foram deletadas (cascade chain)
- [ ] AC12: Test documenta quais tabelas têm CASCADE e quais não (para referência futura)

## File List
- [ ] `frontend/__tests__/pages/dashboard.test.tsx` (NEW)
- [ ] `frontend/__tests__/pages/pipeline.test.tsx` (NEW)
- [ ] `frontend/__tests__/pages/historico.test.tsx` (NEW)
- [ ] `frontend/__tests__/pages/onboarding.test.tsx` (NEW)
- [ ] `frontend/__tests__/pages/conta.test.tsx` (NEW)
- [ ] `backend/tests/integration/test_user_deletion_cascade.py` (NEW)
