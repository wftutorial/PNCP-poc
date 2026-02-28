# CRIT-043: Reduzir Ruído de PNCP HTTP 400 na Página 5

**Epic:** Observability
**Sprint:** Sprint 4
**Priority:** P2 — MEDIUM
**Story Points:** 3 SP
**Estimate:** 1-2 horas
**Owner:** @dev

---

## Problem

O PNCP retorna HTTP 400 quando `pagina` ultrapassa o total de páginas disponíveis. Com `MAX_PAGES=5` e `tamanhoPagina=50`, UFs grandes (SP com 2160 items em modalidade 6) inevitavelmente atingem a página 5 e recebem 400. Isso gera:

1. **Sentry noise** — 2 issues PNCP 400 nas últimas 24h (SMARTLIC-BACKEND-1Y, SMARTLIC-BACKEND-1P)
2. **CB pollution** — `_circuit_breaker.record_failure()` é chamado para 400, que é um erro determinístico (não transiente)
3. **Log inconsistency** — path async loga WARNING, path sync loga ERROR para o mesmo cenário

**Contexto:** O truncamento por MAX_PAGES é intencional (STORY-282). O erro 400 na última página é um efeito colateral esperado e inofensivo.

---

## Solution

1. Distinguir "400 na última página (esperado)" de "400 na primeira página (erro real)"
2. Não registrar CB failure para 400 previsíveis
3. Unificar log level entre paths sync e async

---

## Acceptance Criteria

### Backend — PNCP Client

- [ ] **AC1:** Em `pncp_client.py:_fetch_single_modality()` (~line 1896): quando `PNCPAPIError` com status 400 ocorre em `pagina > 1`, logar como DEBUG (não WARNING) e NÃO chamar `_circuit_breaker.record_failure()`
- [ ] **AC2:** Em `pncp_client.py:_fetch_page_async()` (~line 1772): quando status 400 e `pagina > 1`, NÃO levantar `PNCPAPIError` — retornar resultado vazio (mesma semântica de "sem mais páginas")
- [ ] **AC3:** Em `pncp_client.py:_fetch_page()` (sync path, ~line 1027): alinhar log level — 400 em `pagina > 1` deve ser DEBUG (não ERROR)
- [ ] **AC4:** Manter log ERROR para 400 em `pagina == 1` (indica problema real com parâmetros)

### Sentry — Filtering

- [ ] **AC5:** No `before_send` do Sentry (main.py), dropar eventos que contenham "PNCP API error: status=400" E "pagina': 5" ou `pagina > 1` (são ruído esperado)

### Testes

- [ ] **AC6:** Teste: HTTP 400 na página 5 → sem `record_failure()` no CB, log DEBUG
- [ ] **AC7:** Teste: HTTP 400 na página 1 → `record_failure()` chamado, log ERROR
- [ ] **AC8:** Teste: HTTP 503 em qualquer página → `record_failure()` chamado (transiente)

---

## Impacto nos Warnings de MAX_PAGES

Os 30+ warnings de "MAX_PAGES (5) reached" são **informativos e corretos** — não devem ser alterados. Eles indicam que o truncamento funcionou como esperado. Apenas o ERROR/WARNING do HTTP 400 subsequente é ruído.

---

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `backend/pncp_client.py` | Log level 400 pagina>1: ERROR→DEBUG, sem CB failure |
| `backend/main.py` | `before_send` filter para PNCP 400 |
| `backend/tests/test_pncp_client.py` | Testes para 400 em diferentes páginas |
