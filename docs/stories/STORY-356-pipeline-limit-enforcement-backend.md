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

- [ ] AC1: Adicionar validação em `POST /pipeline` que verifica contagem atual de items do usuário vs limite do plano
- [ ] AC2: Trial: max 5 items (usar `TRIAL_PAYWALL_MAX_PIPELINE` de config.py — já existe)
- [ ] AC3: Retornar HTTP 403 com body `{"error_code": "PIPELINE_LIMIT_EXCEEDED", "limit": N, "current": M}`
- [ ] AC4: Frontend exibe modal de upgrade ao receber 403 com error_code `PIPELINE_LIMIT_EXCEEDED`
- [ ] AC5: Paid users: sem limite (ou limite alto configurável via `PLAN_CAPABILITIES`)
- [ ] AC6: Testes: trial user tenta adicionar item #6, recebe 403
- [ ] AC7: Testes: paid user adiciona item sem limite

## Arquivos Afetados

- `backend/routes/pipeline.py`
- `backend/config.py`
- `frontend/app/pipeline/page.tsx`

## Validação

| Métrica | Threshold | Onde medir |
|---------|-----------|------------|
| 403 em POST /pipeline para trial excedido | 100% enforcement | Integration tests |
