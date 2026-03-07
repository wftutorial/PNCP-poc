# HARDEN-016: Health Check Split — Liveness vs Readiness

**Severidade:** ALTA
**Esforço:** 30 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Pesquisa de Industria (Google SRE Book)

## Contexto

SmartLic tem `/health` que retorna 200 sempre (process alive). Load balancer não sabe se Redis/Supabase estão down — continua roteando tráfego para instância com dependências mortas.

## Critérios de Aceitação

- [ ] AC1: `GET /health/live` — retorna 200 se processo alive (sem dependency checks)
- [ ] AC2: `GET /health/ready` — retorna 200 se Redis + Supabase OK, 503 se não
- [ ] AC3: Readiness checks com timeout individual (Redis 2s, Supabase 3s)
- [ ] AC4: Response body inclui detalhes de cada check
- [ ] AC5: `/health` existente mantido para backward compatibility
- [ ] AC6: Railway healthcheck configurado para `/health/ready`
- [ ] AC7: Teste unitário para cenários de dependência down

## Arquivos Afetados

- `backend/routes/health.py` — novos endpoints
- `backend/tests/test_health.py`
- Railway config (healthcheck path)
