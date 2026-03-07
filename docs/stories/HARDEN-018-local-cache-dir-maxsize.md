# HARDEN-018: Local Cache Dir Max Size (200MB)

**Severidade:** MEDIA
**Esforço:** 15 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

`LOCAL_CACHE_DIR` em `search_cache.py:51-56` cresce com cada cached search. Cleanup a cada 6h (cron), mas em picos pode acumular 500MB. Railway tem /tmp limitado.

## Critérios de Aceitação

- [x] AC1: `_check_cache_dir_size()` helper que verifica tamanho total do diretório
- [x] AC2: Se > 200MB, deleta arquivos mais antigos até < 100MB
- [x] AC3: Chamado antes de cada write + no cleanup periódico
- [x] AC4: Teste unitário

## Arquivos Afetados

- `backend/search_cache.py`
