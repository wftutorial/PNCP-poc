# HARDEN-016: Health Check Split — Liveness vs Readiness

**Severidade:** ALTA
**Esforço:** 30 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Pesquisa de Industria (Google SRE Book)

## Contexto

SmartLic tem `/health` que retorna 200 sempre (process alive). Load balancer não sabe se Redis/Supabase estão down — continua roteando tráfego para instância com dependências mortas.

## Critérios de Aceitação

- [x] AC1: `GET /health/live` — retorna 200 se processo alive (sem dependency checks)
- [x] AC2: `GET /health/ready` — retorna 200 se Redis + Supabase OK, 503 se não
- [x] AC3: Readiness checks com timeout individual (Redis 2s, Supabase 3s)
- [x] AC4: Response body inclui detalhes de cada check
- [x] AC5: `/health` existente mantido para backward compatibility
- [x] AC6: Railway healthcheck configurado para `/health/ready`
- [x] AC7: Teste unitário para cenários de dependência down

## Arquivos Afetados

- `backend/main.py` — `/health/live` (new) + `/health/ready` (refactored)
- `backend/tests/test_health_ready.py` — 15 tests (3 live + 7 ready + 2 timeout + 2 body + 1 compat)
- `backend/railway.toml` — healthcheck already at `/health/ready` (unchanged)
