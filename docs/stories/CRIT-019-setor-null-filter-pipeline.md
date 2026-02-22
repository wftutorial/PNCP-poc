# CRIT-019 — setor=None Desabilita 6 Caminhos de Classificacao no Pipeline de Filtros

**Tipo:** Bug Critico / Recall Killer
**Prioridade:** P0 (Afeta TODOS os 15 setores em producao)
**Criada:** 2026-02-22
**Status:** Pendente
**Origem:** Investigacao P0 — busca de engenharia retornando 0 resultados
**Dependencias:** Nenhuma
**Estimativa:** XS (2 linhas de codigo + testes)

---

## Problema

`search_pipeline.py` chama `aplicar_todos_filtros()` em duas ocasioes (L1530 e L1562) sem passar o parametro `setor`. O parametro tem default `None`, o que desabilita **6 features criticas** que dependem de `if setor:` guards em `filter.py`.

O `setor_id` esta disponivel e correto em `ctx.request.setor_id` (setado na stage 2, L730). Simplesmente nao e passado.

### Impacto

Todas as features abaixo estao **desabilitadas em producao para todos os 15 setores**:

| Feature | Guard em `filter.py` | Consequencia |
|---|---|---|
| LLM Zero-Match (Camada 3B) | `if LLM_ZERO_MATCH_ENABLED and setor:` (L2493) | Bids com 0% keyword match silenciosamente descartadas — sem segunda chance via LLM |
| FLUXO 2 Recovery | `if setor and not _skip_fluxo_2:` (L3072) | Sem synonym matching, sem LLM fallback, sem relaxacao zero-results |
| Item Inspection (Camada 1C) | `if setor and get_feature_flag(...)` (L2609) | Sem analise de sub-itens |
| Proximity Context (Camada 1B.3) | `if get_feature_flag(...) and setor:` (L2372) | Sem matching por proximidade contextual |
| Co-occurrence Rules (Camada 1B.5) | `if setor and get_feature_flag(...)` (L2431) | Sem correlacao multi-termo |
| Value Threshold (Camada 1A) | `if setor:` (L2259) | Sem filtro max_contract_value por setor |

### Efeito Colateral Adicional

- `filter_stats.record_rejection(sector=None)` em TODAS as rejeicoes — metricas por setor sao inuteis
- Impossivel saber qual setor sofre mais com `keyword_miss` vs `exclusion_hit` vs `density_low`

---

## Solucao

### Abordagem: Passar `setor=ctx.request.setor_id` nas 2 chamadas

### Criterios de Aceitacao

- [ ] **AC1:** `search_pipeline.py:1530` passa `setor=ctx.request.setor_id` para `aplicar_todos_filtros()`
- [ ] **AC2:** `search_pipeline.py:1562` (retry relaxado) passa `setor=ctx.request.setor_id` para `aplicar_todos_filtros()`
- [ ] **AC3:** Teste unitario confirma que `aplicar_todos_filtros` recebe `setor` != None quando `request.setor_id` existe
- [ ] **AC4:** Teste de integracao confirma que LLM Zero-Match (Camada 3B) e ativado quando `setor` e passado
- [ ] **AC5:** Teste confirma que `filter_stats.record_rejection()` recebe `sector` != None
- [ ] **AC6:** Teste de regressao — busca por setor que ja funcionava continua retornando resultados

### Verificacao Pos-Deploy

- [ ] Logs em producao mostram `sector=engenharia` (nao `null`) nas rejeicoes
- [ ] Metricas de `filter_rejection` mostram distribuicao por setor
- [ ] Zero-match LLM calls aparecem nos logs (indicando que o caminho esta ativo)

---

## Arquivos Envolvidos

| Arquivo | Mudanca |
|---|---|
| `backend/search_pipeline.py` | L1530, L1562 — adicionar `setor=ctx.request.setor_id` |
| `backend/tests/` | Novo teste ou extensao de existente |

---

## Notas de Implementacao

- `ctx.request.setor_id` e setado em stage 2 (PrepareSearch, L730) a partir do request body
- O parametro `setor` em `aplicar_todos_filtros()` e `Optional[str]` com default `None` (L1916)
- Nao alterar a assinatura da funcao — apenas adicionar o kwarg na chamada
- Risco de regressao: BAIXO — ativa caminhos que ja existem mas nunca rodaram em producao
- **ATENCAO:** Ao ativar LLM Zero-Match, pode haver aumento de custo OpenAI. Monitorar.
