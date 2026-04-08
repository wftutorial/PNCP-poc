# EPIC: Resolucao de Debitos Tecnicos — SmartLic

**Epic ID:** EPIC-TD-2026
**Owner:** @architect (Aria)
**Status:** Planning
**Created:** 2026-04-08
**Timeline:** 20 semanas (5 fases)
**Total:** 61 debitos, 9 stories, ~140h

## Stories (ordem de execucao)

| # | ID | Nome | Fase | Horas | Agente |
|---|-----|------|------|-------|--------|
| 1 | **DEBT-01** | DB Index + Retention Policies | 1 (Quick Wins) | 3.5h | @data-engineer |
| 2 | **DEBT-02** | Accessibility Quick Wins | 1 (Quick Wins) | 2h | @dev |
| 3 | **DEBT-03** | RPC Security Audit | 1 (Quick Wins) | 4h | @architect + @qa |
| 4 | **DEBT-04** | Backend Resilience | 2 (Foundation) | 7h | @dev + @devops |
| 5 | **DEBT-05** | DB Integrity (Backup + FK) | 2 (Foundation) | 7h | @data-engineer + @devops |
| 6 | **DEBT-06** | Search Hooks Refactor | 3 (Hardening) | 54h | @dev + @ux |
| 7 | **DEBT-07** | Backend Module Split | 3-4 (Hardening) | 28h | @dev |
| 8 | **DEBT-08** | CI Quality Gates | 4 (Polish) | 36h | @devops + @qa |
| 9 | **DEBT-09** | Long-term Backlog | 5 (Long-term) | ~90h | Varios |

## Paralelizacao

```
Semana 1-2:  DEBT-01 || DEBT-02 || DEBT-03
Semana 2-4:  DEBT-04 || DEBT-05
Semana 5-8:  DEBT-06 || DEBT-07
Semana 9-12: DEBT-07 (cont.) || DEBT-08
Semana 13+:  DEBT-09 (oportunistico)
```

## Documentos Relacionados

- [Assessment Final](../prd/technical-debt-assessment.md)
- [Relatorio Executivo](../reports/TECHNICAL-DEBT-REPORT.md)
- [DB Audit](../../supabase/docs/DB-AUDIT.md)
- [Frontend Spec](../frontend/frontend-spec.md)
- [System Architecture](../architecture/system-architecture.md)
