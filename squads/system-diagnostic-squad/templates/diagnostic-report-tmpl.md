# SmartLic Diagnostic Report

**Data:** {date}
**Versao:** v0.5
**Target:** 50 usuarios pagantes
**Squad:** system-diagnostic-squad
**Duracao:** {duration}

---

## Veredicto Geral: {GO | CONDITIONAL_GO | NO_GO}

| Categoria | Total | Pass | Fail | N/A |
|-----------|-------|------|------|-----|
| Critico | 13 | | | |
| Importante | 11 | | | |
| Desejavel | 8 | | | |

---

## Jornadas Executadas

### 1. Trial → Pagante (usuario-trial)
**Status:** {status}
{output da task}

### 2. Busca Diaria — Core Loop (usuario-pagante)
**Status:** {status}
{output da task}

### 3. Volume — Consultor (consultor-licitacao)
**Status:** {status}
{output da task}

### 4. Visibilidade Operacional (admin-operador)
**Status:** {status}
{output da task}

### 5. Falhas Silenciosas (auditor-tecnico)
**Status:** {status}
**Risk Score:** {1-10}
{output da task}

---

## Findings

### BLOCKERs
{lista ou "Nenhum encontrado"}

### HIGHs
{lista}

### NAO VALIDADOS
{lista com motivo}

---

## Plano de Acao
| # | Acao | Prioridade | Responsavel | Deadline |
|---|------|-----------|-------------|----------|

---

*Gerado por system-diagnostic-squad*
