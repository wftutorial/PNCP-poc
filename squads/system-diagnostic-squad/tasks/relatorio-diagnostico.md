# relatorio-diagnostico

## Metadata
- agent: all (evidence-compiler role)
- elicit: false
- priority: critical
- estimated_time: 20min
- tools: [Read, Write, Grep]
- depends_on: [jornada-trial-to-paid, jornada-busca-diaria, jornada-consultor-volume, jornada-admin-oversight, auditoria-falhas-silenciosas]

## Objetivo
Consolidar todas as evidencias dos 5 agentes em um unico relatorio GO/NO-GO.
Nenhum item pode ser marcado PASS sem evidencia. Sem evidencia = NAO VALIDADO.

## Template do Relatorio

```markdown
# SmartLic Diagnostic Report
**Data:** {date}
**Versao:** v0.5
**Target:** 50 usuarios pagantes
**Executado por:** system-diagnostic-squad

## Veredicto Geral: {GO | CONDITIONAL_GO | NO_GO}

### Criterios de Decisao
- **GO:** Zero BLOCKERs, zero HIGHs nao mitigados
- **CONDITIONAL_GO:** Zero BLOCKERs, HIGHs com mitigation plan e deadline
- **NO_GO:** Qualquer BLOCKER presente

---

## 1. Jornada Trial → Pagante
**Agent:** usuario-trial
**Status:** {PASS | FAIL | DEGRADED}

| Step | Status | Evidencia | Notas |
|------|--------|-----------|-------|
| Acesso Inicial | | | |
| Signup | | | |
| Onboarding | | | |
| Primeira Busca | | | |
| Checkout/Pagamento | | | |
| Pos-Pagamento | | | |

**Bloqueios:** {lista ou "nenhum"}

---

## 2. Jornada Busca Diaria (Core Loop)
**Agent:** usuario-pagante
**Status:** {PASS | FAIL | DEGRADED}

| Step | Status | Evidencia | Notas |
|------|--------|-----------|-------|
| Login/Estado | | | |
| Busca Multi-Fonte | | | |
| Classificacao IA | | | |
| Pipeline Kanban | | | |
| Export Excel | | | |
| Resumo IA | | | |
| Consistencia | | | |

**Core loop funcional:** {SIM | NAO | PARCIAL}

---

## 3. Jornada Consultor (Volume)
**Agent:** consultor-licitacao
**Status:** {PASS | FAIL | DEGRADED}

| Step | Status | Evidencia | Notas |
|------|--------|-----------|-------|
| Buscas Sequenciais | | | |
| Multi-Setor | | | |
| Multi-UF Nacional | | | |
| Quota/Limites | | | |
| Exports Volume | | | |

**Aguenta 50 users nesse padrao:** {SIM | NAO | COM RESSALVAS}

---

## 4. Visibilidade Operacional
**Agent:** admin-operador
**Status:** {PASS | FAIL | DEGRADED}

| Step | Status | Evidencia | Notas |
|------|--------|-----------|-------|
| Health Check | | | |
| Billing Sync | | | |
| Sentry/Errors | | | |
| SLO Dashboard | | | |
| Email Alerts | | | |
| Deteccao Problemas | | | |

**Saberia antes do cliente:** {SIM | NAO | DEPENDE}

---

## 5. Auditoria Tecnica (Falhas Silenciosas)
**Agent:** auditor-tecnico
**Status:** {PASS | FAIL | DEGRADED}
**Risk Score:** {1-10}

| Area | Status | Findings | Severidade |
|------|--------|----------|------------|
| Exception Handling | | | |
| Circuit Breakers | | | |
| Cache Integrity | | | |
| Data Integrity | | | |
| Webhook Reliability | | | |
| Race Conditions | | | |
| Fallback Paths | | | |

**Top 3 Riscos:**
1. {risco}
2. {risco}
3. {risco}

---

## Findings Consolidados

### BLOCKERs (devem ser resolvidos antes de 50 users)
| # | Finding | Agent | Impacto | Acao |
|---|---------|-------|---------|------|

### HIGHs (devem ser resolvidos em 2 semanas)
| # | Finding | Agent | Impacto | Acao |
|---|---------|-------|---------|------|

### MEDIUMs (backlog priorizado)
| # | Finding | Agent | Impacto | Acao |
|---|---------|-------|---------|------|

### Items NAO VALIDADOS (sem evidencia)
| # | Item | Motivo | Risco |
|---|------|--------|-------|

---

## Proximos Passos
1. {acao 1}
2. {acao 2}
3. {acao 3}

---
*Gerado por system-diagnostic-squad em {date}*
```

## Instrucoes de Preenchimento

1. **Coletar outputs** de cada task executada pelos 5 agentes
2. **Para cada step:** copiar status e evidencia do output do agente
3. **Classificar findings:**
   - BLOCKER = usuario pagante PERDE dinheiro ou dados
   - HIGH = experiencia degradada, risco de churn
   - MEDIUM = inconveniencia, nao critico
   - LOW = polish, nice-to-have
4. **NAO VALIDADO** = nao teve tempo/acesso para testar — listar explicitamente
5. **Veredicto geral** baseado SOMENTE em evidencias, nao em suposicoes

## Output
Arquivo: `docs/diagnostics/DIAGNOSTIC-REPORT-{date}.md`
