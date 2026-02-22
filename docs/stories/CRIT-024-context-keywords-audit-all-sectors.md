# CRIT-024 — Auditoria Sistemica de context_required_keywords e Red Flags em Todos os 15 Setores

**Tipo:** Auditoria / Recall Sistemico
**Prioridade:** P1 (Prevencao — mesmo problema de engenharia pode afetar outros setores)
**Criada:** 2026-02-22
**Status:** Pendente
**Origem:** Investigacao P0 — problema de engenharia revelou padroes sistemicos
**Dependencias:** CRIT-019, CRIT-020, CRIT-021 (corrigir primeiro os bugs conhecidos)
**Estimativa:** M (analise + ajustes em 15 setores)

---

## Problema

A investigacao do setor engenharia revelou 3 padroes problematicos que podem afetar QUALQUER dos 15 setores:

1. **RED_FLAGS aplicados globalmente** — cada set de red flags (MEDICAL, ADMINISTRATIVE, INFRASTRUCTURE) e aplicado a todos os setores sem discriminacao
2. **context_required_keywords restritivos** — termos genericos com listas de contexto incompletas
3. **Sector-specific tuning ausente** — thresholds de densidade, red flags, e recovery paths sao one-size-fits-all

### Impacto Estimado por Setor

| Setor | Red Flags | Context Gates | Risco |
|---|---|---|---|
| engenharia | INFRA mata bids | "engenharia" restritivo | CRITICO — corrigido em CRIT-020/021 |
| engenharia_rodoviaria | INFRA mata bids | Similar a engenharia | CRITICO |
| manutencao_predial | INFRA parcialmente | "reforma" restritivo | ALTO |
| materiais_hidraulicos | INFRA parcialmente | "saneamento" | ALTO |
| saude | MEDICAL pode afetar? | Verificar | MEDIO |
| informatica | ADMIN pode afetar? | "sistema" restritivo? | MEDIO |
| software | ADMIN pode afetar? | "software" contexto? | MEDIO |
| facilities | INFRA/ADMIN overlap | "manutencao" | MEDIO |
| vestuario | Design original | Verificar recall | BAIXO |
| Demais 6 setores | Verificar | Verificar | DESCONHECIDO |

---

## Solucao

### Abordagem: Auditoria setor-por-setor com teste de recall

### Criterios de Aceitacao

#### Fase 1: Mapeamento

- [ ] **AC1:** Para cada um dos 15 setores, documentar:
  - Quantos keywords tem context_required
  - Quais context words estao definidos
  - Quais RED_FLAGS sets afetam o setor
  - Se ha overlap entre keywords do setor e red flags

- [ ] **AC2:** Criar matriz de risco (setor x red_flag_set) mostrando colisoes

#### Fase 2: Correcoes

- [ ] **AC3:** Para cada setor com RED_FLAGS collision, adicionar exemption (similar a CRIT-020)
- [ ] **AC4:** Para cada setor com context_required restritivo, expandir lista de contexto
- [ ] **AC5:** Documentar razao de cada context_required como comentario no YAML

#### Fase 3: Validacao

- [ ] **AC6:** Script de teste que roda busca simulada para cada setor e verifica recall > 0
- [ ] **AC7:** Comparar total_raw vs total_filtrado antes e depois das correcoes
- [ ] **AC8:** Metricas de `rejeitadas_red_flags` por setor mostram distribuicao saudavel

---

## Arquivos Envolvidos

| Arquivo | Mudanca |
|---|---|
| `backend/sectors_data.yaml` | Expansao de context_required para multiplos setores |
| `backend/filter.py` | Exemptions de red flags por setor (se nao coberto por CRIT-020) |
| `backend/tests/` | Testes de recall por setor |

---

## Notas de Implementacao

- Esta story e de ANALISE + CORRECAO. Fase 1 (mapeamento) deve ser feita primeiro.
- Usar dados reais do PNCP (ultimos 10 dias) como corpus de teste
- Focar primeiro nos setores de risco CRITICO e ALTO
- Considerar ferramenta/script de "filter dry-run" que mostra rejeicoes sem aplicar
- Pospor setores de risco BAIXO/DESCONHECIDO para sprint seguinte se necessario
