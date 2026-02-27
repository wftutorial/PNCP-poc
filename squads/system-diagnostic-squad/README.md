# system-diagnostic-squad

Squad de diagnostico sem complacencia para o SmartLic.

## Filosofia
Cada agente simula um stakeholder real. Se a jornada dele quebrar, voce perde dinheiro.
Pareto: minimo trabalho, maximo resultado para garantir zero dor de cabeca ate 50 usuarios pagantes.

## Agentes (Stakeholders)

| Agent | Simula | Pergunta-chave |
|-------|--------|----------------|
| usuario-trial | Novo usuario cetico | "Isso funciona? Vale meu dinheiro?" |
| usuario-pagante | Empresa B2G pagante | "Minha busca diaria funciona sem falha?" |
| consultor-licitacao | Assessor power user | "Consigo escalar meu trabalho aqui?" |
| admin-operador | Operador do sistema | "Vou saber antes do cliente reclamar?" |
| auditor-tecnico | Auditor invisivel | "O que esta quebrando sem ninguem saber?" |

## Tasks

| Task | Agent | Foco |
|------|-------|------|
| jornada-trial-to-paid | usuario-trial | Signup → busca → pagamento |
| jornada-busca-diaria | usuario-pagante | Core loop completo |
| jornada-consultor-volume | consultor-licitacao | Volume e limites |
| jornada-admin-oversight | admin-operador | Monitoramento e billing |
| auditoria-falhas-silenciosas | auditor-tecnico | Erros inviseis e resiliencia |
| relatorio-diagnostico | todos | GO/NO-GO consolidado |

## Como Executar

```bash
# Recomendado: hibrido
# 1. Auditor tecnico primeiro (code review, sem browser)
# 2. Jornadas de usuario em paralelo (Playwright)
# 3. Admin + relatorio final
```

## Output
`docs/diagnostics/DIAGNOSTIC-REPORT-{date}.md`
