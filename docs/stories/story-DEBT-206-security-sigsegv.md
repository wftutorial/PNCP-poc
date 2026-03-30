# Story DEBT-206: Seguranca — Monitoramento cryptography/SIGSEGV

## Metadados
- **Epic:** EPIC-DEBT-V2
- **Sprint:** 6 (Semana 11-12) + Recorrente
- **Prioridade:** P0 (Critico — monitoramento periodico)
- **Esforco:** 4h (inicial) + 4h (backlog, quando 47.x estavel)
- **Agente:** @devops
- **Status:** PLANNED

## Descricao

Como equipe de seguranca, queremos monitorar periodicamente vulnerabilidades na dependencia `cryptography` pinada em <47.0 e testar compatibilidade com versoes mais recentes, para que a plataforma nao fique exposta a CVEs conhecidos sem patch disponivel e possamos fazer upgrade assim que possivel.

## Debitos Incluidos

| ID | Debito | Horas | Responsavel |
|----|--------|-------|-------------|
| DEBT-SYS-002 | SIGSEGV intermitente com C extensions (CRIT-SIGSEGV) — cryptography >= 47.0 pinada | 4h inicial + 4h futuro | @devops |

## Criterios de Aceite

### Investigacao Inicial (4h)
- [ ] cryptography 47.x instalado em environment de staging isolado
- [ ] Teste de carga: 100 requests sem SIGSEGV
- [ ] CVEs na faixa cryptography 46.x verificados via `pip-audit` e NVD
- [ ] Resultado documentado em `docs/security/cryptography-sigsegv-status.md`:
  - Versao testada
  - Resultado: SIGSEGV reproduzido? Sim/Nao
  - CVEs ativos na faixa 46.x
  - Recomendacao: upgrade / manter pin / aguardar upstream fix
- [ ] Se CVE critico encontrado: issue de seguranca criada imediatamente

### Monitoramento Recorrente
- [ ] Checklist trimestral definido:
  1. Verificar novos CVEs para cryptography 46.x
  2. Testar cryptography latest em staging
  3. Atualizar documento de status
- [ ] Reminder criado para proxima verificacao (Q3 2026)

### Backlog Futuro (4h — quando 47.x estavel)
- [ ] Upgrade de cryptography para >=47.0
- [ ] Remocao do pin de versao em `requirements.txt`
- [ ] Remocao das restricoes de uvloop relacionadas ao SIGSEGV
- [ ] Suite completa de testes em producao pos-upgrade

## Testes Requeridos

- [ ] Teste de carga em staging com cryptography 47.x (100 requests, zero crashes)
- [ ] `pip-audit` em `requirements.txt` — zero CVEs criticos
- [ ] `pytest --timeout=30 -q` — suite completa em environment com cryptography testado

## Notas Tecnicas

- **Contexto CRIT-SIGSEGV:** Bug intermitente de segfault com C extensions (uvloop + cryptography >= 47.0). Pin atual em <47.0 e workaround, nao solucao.
- **Risco:** Se CVE critico for descoberto na faixa 46.x, o workaround se torna vulnerabilidade. Monitoramento e essencial.
- **Nao bloqueia outras stories:** Esta e uma atividade de monitoramento, nao de desenvolvimento.
- **uvloop:** Restricoes de uvloop tambem relacionadas — verificar se versao mais recente resolve.

## Dependencias

- Nenhuma — independente de todas as outras stories
- Executavel a qualquer momento
