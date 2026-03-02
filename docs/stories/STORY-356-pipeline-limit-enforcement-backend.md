# STORY-356: Pipeline limit enforcement no backend

**Prioridade:** P1
**Tipo:** fix (segurança)
**Sprint:** Sprint 2
**Estimativa:** S
**Origem:** Conselho CTO Advisory Board — Auditoria de Promessas (2026-03-01)
**Dependências:** Nenhuma
**Bloqueado por:** —
**Bloqueia:** —
**Paralelo com:** STORY-355, STORY-357

---

## Contexto

O limite de itens no pipeline é aplicado apenas no frontend (`PIPELINE_LIMIT` em `pipeline/page.tsx`). Qualquer chamada direta à API (cURL, Postman, automação) bypassará o limite. Isso compromete a integridade da restrição trial e do modelo de billing.

## Promessa Afetada

> Integridade da restrição trial (afeta confiança no modelo freemium)

## Causa Raiz

Frontend-only enforcement. Backend `POST /pipeline` não verifica contagem atual vs limite do plano.

## Critérios de Aceite

- [x] AC1: Adicionar validação em `POST /pipeline` que verifica contagem atual de items do usuário vs limite do plano
- [x] AC2: Trial: max 5 items (usar `TRIAL_PAYWALL_MAX_PIPELINE` de config.py — já existe)
- [x] AC3: Retornar HTTP 403 com body `{"error_code": "PIPELINE_LIMIT_EXCEEDED", "limit": N, "current": M}`
- [x] AC4: Frontend exibe modal de upgrade ao receber 403 com error_code `PIPELINE_LIMIT_EXCEEDED`
- [x] AC5: Paid users: sem limite (ou limite alto configurável via `PLAN_CAPABILITIES`)
- [x] AC6: Testes: trial user tenta adicionar item #6, recebe 403
- [x] AC7: Testes: paid user adiciona item sem limite

## Arquivos Afetados

- `backend/routes/pipeline.py` — `_check_pipeline_limit()` + call in `create_pipeline_item()`
- `backend/tests/test_pipeline.py` — added `_noop_check_pipeline_limit` mock to POST tests
- `backend/tests/test_pipeline_limit.py` — 9 new tests (AC6/AC7)
- `frontend/hooks/usePipeline.ts` — detect `PIPELINE_LIMIT_EXCEEDED` in `addItem()`
- `frontend/app/components/AddToPipelineButton.tsx` — "limit" status state
- `frontend/__tests__/pipeline/pipeline-limit.test.tsx` — 5 new tests (AC4)

## Validação

| Métrica | Threshold | Onde medir |
|---------|-----------|------------|
| 403 em POST /pipeline para trial excedido | 100% enforcement | Integration tests |
