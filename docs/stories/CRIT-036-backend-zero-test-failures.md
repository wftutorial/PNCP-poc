# CRIT-036 — Backend: Zero Test Failures (25 → 0)

**Status:** Open
**Priority:** P0 — Blocker
**Severity:** Infraestrutura de qualidade
**Created:** 2026-02-23
**Blocks:** GTM launch (sem baseline limpo, regressões são invisíveis)

---

## Problema

25 testes backend falhando. Parecem "pre-existing" mas na verdade são **test rot** — código mudou, testes não acompanharam. Resultado: qualquer regressão real se esconde no ruído.

### Causa-Raiz por Grupo

| Grupo | Tests | Causa | Módulos |
|-------|-------|-------|---------|
| G1: Revalidation path | 10 | `get_source_config` movido para `source_config.sources`, mas testes patcheiam `search_cache` | test_background_revalidation (5), test_revalidation_quota_cache (4), test_cache_global_warmup (1) |
| G2: Consolidation path | 1 | `compute_search_hash` patched em `search_pipeline`, mas vive em `search_cache` | test_consolidation |
| G3: Profile context | 4 | Endpoint retorna 500 — mock incompleto (falta `.data` no retorno) | test_profile_context |
| G4: Strings i18n | 2 | Código traduzido para PT-BR, assertions ainda em inglês | test_search_state |
| G5: Quota tests | 4 | Quota assertions desatualizadas (limites mudaram de 50→3 buscas, strings PT-BR com encoding) | test_quota |
| G6: Individuais | 8 | Ver detalhes abaixo | 8 arquivos |

---

## Acceptance Criteria

### G1 — Revalidation Module Paths (10 tests)

- [ ] **AC1:** `test_background_revalidation.py` — Corrigir patches de `get_source_config` para `source_config.sources.get_source_config` onde necessário. Verificar se `_fetch_multi_source_for_revalidation` existe e onde é importado.
- [ ] **AC2:** `test_revalidation_quota_cache.py` — Mesmo fix (4 tests: T1 consolidation_service, T2 pcp_fallback, T2 all_fallbacks, T3 cache_hit_skips_quota)
- [ ] **AC3:** `test_cache_global_warmup.py::test_revalidation_falls_back_to_pncp_only` — Corrigir patch path

### G2 — Consolidation Hash Path (1 test)

- [ ] **AC4:** `test_consolidation.py::test_one_source_timeout_partial_results` — Patch `search_cache.compute_search_hash` em vez de `search_pipeline.compute_search_hash`

### G3 — Profile Context Endpoint (4 tests)

- [ ] **AC5:** `test_profile_context.py` — 4 tests (save_db_error, get_with_data, get_empty, get_null). Investigar se o endpoint em `routes/user.py` está falhando por mock incompleto (`.data` attribute) ou por exceção no try block. Corrigir mock OU endpoint.

### G4 — Strings PT-BR (2 tests)

- [ ] **AC6:** `test_search_state.py::test_old_searches_marked_timed_out` — Assertion espera `"Server restart"`, código gera `"O servidor reiniciou durante o processamento."`. Atualizar assertion.
- [ ] **AC7:** `test_search_state.py::test_recent_searches_marked_failed` — Assertion espera `"retry"`, código gera `"o servidor reiniciou. tente novamente."`. Atualizar assertion.

### G5 — Quota Tests (4 tests)

- [ ] **AC8a:** `test_quota.py:267,301,332` — 3 assertions `assert False is True`. Quota limits mudaram (provavelmente de 50 para valores GTM-002). Atualizar assertions para refletir limites atuais do plano `smartlic_pro`.
- [ ] **AC8b:** `test_quota.py:372` — Mensagem espera `"50 buscas mensais"` mas recebe `"Limite de 3 buscas mensais atingido..."` com encoding quebrado (mojibake: `Renova��o`). Corrigir: (1) atualizar expected string, (2) verificar encoding UTF-8 na geração da mensagem.

### G6 — Individuais (8 tests)

- [ ] **AC8:** `test_oauth_story224.py:408` — `decrypt_aes256(tampered)` não levanta Exception. Verificar se a lógica de tamper está criando dado realmente inválido, ou se `decrypt_aes256` silencia erros.
- [ ] **AC9:** `test_openapi_schema.py` — Schema drift. Regenerar snapshot: rodar teste com `--snapshot-update` ou copiar schema atual para `tests/snapshots/openapi_schema.json`.
- [ ] **AC10:** `test_sectors.py:129::test_excludes_nebulizacao` — Texto de nebulização costal com inseticida está matchando quando deveria ser excluído. Verificar se "nebulização" está nas exclusions do setor em `sectors_data.yaml`. Adicionar se não estiver.
- [ ] **AC11:** `test_job_queue.py` (2 tests: `test_parses_full_url`, `test_parses_minimal_url`) — Redis URL parsing. Verificar se `_get_redis_settings` está tratando URLs corretamente.
- [ ] **AC12:** `test_search_session_lifecycle.py:93` — `['RJ', 'SP'] != ['SP', 'RJ']`. Usar `sorted()` na assertion ou `set()` comparison, OU ordenar UFs antes de persistir.
- [ ] **AC13:** `test_api_buscar.py::test_no_quota_enforcement_when_disabled` — Feature flag patch não aplicado. Verificar se o patch path está correto para `ENABLE_NEW_PRICING`.
- [ ] **AC14:** `test_crit001_schema_alignment.py::test_mod_t03_expected_columns_returns_18` — Contagem de colunas mudou. Atualizar `expected_columns()` em models/cache.py OU atualizar o número esperado no teste.

### Gate Final

- [ ] **AC15:** `pytest` roda com **0 failures** (5106+ passed, 0 failed)
- [ ] **AC16:** Coverage ≥ 70% mantida
- [ ] **AC17:** Nenhum teste foi deletado — apenas corrigido

---

## Estimativa

**Esforço:** ~3-4 horas (maioria é atualização de patch paths e assertions)
**Risco:** Baixo — são fixes de testes, não de código de produção (exceto AC10 sectors exclusion)

## Files

- `backend/tests/test_background_revalidation.py`
- `backend/tests/test_revalidation_quota_cache.py`
- `backend/tests/test_cache_global_warmup.py`
- `backend/tests/test_consolidation.py`
- `backend/tests/test_profile_context.py`
- `backend/tests/test_search_state.py`
- `backend/tests/test_oauth_story224.py`
- `backend/tests/test_openapi_schema.py`
- `backend/tests/test_sectors.py`
- `backend/tests/test_job_queue.py`
- `backend/tests/test_search_session_lifecycle.py`
- `backend/tests/test_api_buscar.py`
- `backend/tests/test_crit001_schema_alignment.py`
- `backend/tests/snapshots/openapi_schema.json`
- `backend/sectors_data.yaml` (se AC10 necessitar)
