# Diagnostic Execution Workflow

## Metadata
- type: workflow
- mode: parallel_then_consolidate
- estimated_time: 2-4 hours
- squad: system-diagnostic-squad

## Execution Plan

```
Phase 1: Parallel Execution (~1.5-3h)
├── Track A: usuario-trial → jornada-trial-to-paid
├── Track B: usuario-pagante → jornada-busca-diaria
├── Track C: consultor-licitacao → jornada-consultor-volume
├── Track D: admin-operador → jornada-admin-oversight
└── Track E: auditor-tecnico → auditoria-falhas-silenciosas

Phase 2: Consolidation (~30min)
└── All agents → relatorio-diagnostico
```

## How to Execute

### Opcao 1: Sequencial (1 agente por vez)
Use quando estiver executando sozinho no Claude Code.

```
1. Ativar squad: /diagnostic
2. Executar cada task na ordem:
   a. jornada-trial-to-paid (requer browser — Playwright)
   b. jornada-busca-diaria (requer browser + API)
   c. jornada-consultor-volume (pode ser API-only)
   d. jornada-admin-oversight (CLI + dashboard checks)
   e. auditoria-falhas-silenciosas (code review + DB queries)
3. Compilar: relatorio-diagnostico
```

### Opcao 2: Parallel com Subagents
Use o Task tool para lançar agentes em paralelo:

```
- Task(agent=usuario-trial, task=jornada-trial-to-paid)
- Task(agent=usuario-pagante, task=jornada-busca-diaria)
- Task(agent=auditor-tecnico, task=auditoria-falhas-silenciosas)
-- wait --
- Compile relatorio-diagnostico from all outputs
```

**Nota:** Tracks A-C requerem acesso ao browser (Playwright MCP).
Track D requer acesso a dashboards externos (Sentry, Railway).
Track E pode rodar 100% via code review + CLI.

### Opcao 3: Hibrido (Recomendado)
1. **Primeiro:** Track E (auditor-tecnico) — nao precisa de browser, encontra riscos estruturais
2. **Depois:** Tracks A-C em paralelo via Playwright
3. **Por fim:** Track D (admin) + relatorio consolidado

## Dependency Map

```
jornada-trial-to-paid ──────┐
jornada-busca-diaria ───────┤
jornada-consultor-volume ───┼──→ relatorio-diagnostico
jornada-admin-oversight ────┤
auditoria-falhas-silenciosas┘
```

## Success Criteria
- Todas as 6 tasks executadas com output documentado
- Checklist diagnostic-checklist.md preenchida
- Relatorio final em docs/diagnostics/
- Veredicto GO/CONDITIONAL_GO/NO_GO fundamentado

## Abort Criteria
- BLOCKER encontrado em autenticacao (ninguem consegue logar)
- Producao instavel durante teste (erros cascata)
- Acesso insuficiente para executar tasks (sem Playwright, sem Supabase)
