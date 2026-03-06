# /intel-b2g — Mapeamento Inteligente de Leads B2G

## Purpose

Varredura multi-fonte para mapear TODOS os players ativos de um setor em licitacoes publicas. Cruza PNCP contratos + OpenCNPJ + Portal da Transparencia para consolidar dados cadastrais, operacionais e de contato.

**Squad:** `squad-intel-b2g.yaml`
**Task:** `intel-b2g-leads.md`
**Output:** `docs/intel-b2g/leads-{setor}-{data}.md`

---

## Usage

```
/intel-b2g leads de {setor}
/intel-b2g leads de medicamentos
/intel-b2g leads de engenharia --meses 12 --ufs SP,RJ,MG
/intel-b2g leads de limpeza --min-contratos 3
```

## What It Does

1. **Coleta** — Busca contratos PNCP do setor (6-12 meses), extrai CNPJs vencedores
2. **Enriquecimento** — OpenCNPJ (cadastro, QSA, contato) + Portal Transparencia (sancoes, contratos federais)
3. **Decisor** — Identifica socio-administrador do QSA como ponto de contato
4. **Contato** — Valida telefones (flag WhatsApp), busca website e email
5. **Consolidacao** — Gera relatorio ordenado por faturamento gov mensal

## Output Schema (por lead)

| Campo | Fonte |
|-------|-------|
| Empresa + Nome Fantasia | OpenCNPJ |
| CNPJ | PNCP |
| Cidade Sede | OpenCNPJ |
| Setor (CNAE) | OpenCNPJ |
| UFs/Cidades de Atuacao | PNCP (agregado) |
| Faturamento Gov Mensal | PNCP + PT (calculado) |
| Capital Social + Porte | OpenCNPJ |
| Website | OpenCNPJ / Web Search |
| Telefone (WhatsApp flag) | OpenCNPJ |
| Email | OpenCNPJ |
| Decisor (Nome + Cargo) | OpenCNPJ QSA |
| Sancoes | Portal da Transparencia |

## Execution

When this command is invoked:

1. Load squad config from `.aios-core/development/agent-teams/squad-intel-b2g.yaml`
2. Load task workflow from `.aios-core/development/tasks/intel-b2g-leads.md`
3. Map user's sector name to `backend/sectors_data.yaml` keywords
4. Execute the 5-step pipeline (coleta → enriquecimento → decisor → contato → consolidacao)
5. Save output to `docs/intel-b2g/`

## Downstream

Leads gerados aqui alimentam o `/ataque-turbo` (squad de prospeccao ativa com cold outreach).

```
/intel-b2g leads de medicamentos    → mapeia 50-200 leads
/ataque-turbo medicamentos          → pega top 15 e gera cadencia de emails
```

## Params

$ARGUMENTS
