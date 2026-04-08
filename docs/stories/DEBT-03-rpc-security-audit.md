# DEBT-03: RPC Security Audit (auth.uid)

**Epic:** EPIC-TD-2026
**Fase:** 1 (Quick Wins)
**Horas:** 4h
**Agente:** @architect + @qa
**Prioridade:** P1

## Debitos Cobertos

| TD | Item | Horas |
|----|------|-------|
| TD-059 | Auditar todas as RPCs Supabase para validacao auth.uid() | 4h |

## Acceptance Criteria

- [ ] AC1: Lista completa de RPCs user-scoped com status (protegida/exposta)
- [ ] AC2: Todas as RPCs sem auth.uid() corrigidas ou documentadas como intencionais
- [ ] AC3: Documento de findings salvo em `docs/reviews/rpc-audit-YYYY-MM-DD.md`
- [ ] AC4: Define escopo de TD-005 (per-user Supabase tokens)

## Contexto

Migration `20260404000000_security_hardening_rpc_rls.sql` ja corrigiu CRIT-SEC-001/002/004. Este audit cobre RPCs restantes.
