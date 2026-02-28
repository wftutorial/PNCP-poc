# STORY-328: Eliminar falsos positivos cross-setor — strip de contexto de órgão no objetoCompra

**Prioridade:** P0 (qualidade de resultados — o mais crítico para a proposta de valor do produto)
**Complexidade:** L (Large)
**Sprint:** CRIT-SEARCH

## Problema

A busca retorna resultados **bizarramente irrelevantes em TODOS os setores** porque o campo `objetoCompra` do PNCP inclui o nome do órgão comprador dentro da descrição do objeto. O setor Saúde é o caso mais gritante, mas o problema é **cross-setor**.

### Exemplos reais de produção (setor Saúde, 2026-02-28)

| Resultado exibido | Por que é irrelevante | Por que passou no filtro |
|---|---|---|
| Locação de veículos sedan e caminhonete | Transporte, não saúde | "Secretaria de Estado da **Saúde** - SESA" no objetoCompra |
| Gêneros alimentícios e materiais de limpeza | Alimentação/limpeza genérica | "Secretaria Municipal de **Saúde**" no objetoCompra |
| Equipamentos de informática | TI genérico | "Consórcio de **Saúde**" no objetoCompra |
| Material de escritório e papelaria | Suprimentos de escritório | "Secretaria Municipal de **Saúde**" no objetoCompra |
| Construção de muro de contenção | Construção civil | "Unidade de **Saúde**" no objetoCompra |
| Material odontológico para CEO | Borderline (odonto ≠ saúde geral) | keyword "saúde" no contexto do órgão |

Todos marcados como "Relevância média". Impacto direto na credibilidade e conversão trial→pago.

### Setores diretamente vulneráveis (keywords que são também nomes de órgão)

| Setor | Keyword vulnerável | Órgão típico que causa FP |
|---|---|---|
| **saude** | "saúde", "hospital", "clínica" | Secretaria de Saúde, Hospital Municipal, Clínica da Família |
| **informatica** | "tecnologia" | Secretaria de Tecnologia, Inst. de Tecnologia |
| **vigilancia** | "segurança" | Secretaria de Segurança Pública |

### Todos os 15 setores indiretamente vulneráveis

~30% dos `objetoCompra` no PNCP contêm cláusulas como:
- "para atender às necessidades da Secretaria de X"
- "em atendimento à demanda da Prefeitura Municipal de Y"
- "pertencentes à frota da Secretaria de Z"
- "de interesse do Instituto W"

Qualquer keyword de qualquer setor que apareça nessas cláusulas de órgão gera falso positivo.

## Causa Raiz

O `objetoCompra` do PNCP é um campo de texto livre que **mistura o que está sendo comprado com quem está comprando**. Exemplo real:

> "Contratação de empresa especializada na prestação de serviços de **locação de veículos** tipo sedan e caminhonete pick-up, sem motorista, para atendimento às necessidades da **Secretaria de Estado da Saúde** - SESA."

Cadeia de falha (aplicável a todos os setores):
1. `objetoCompra` contém nome do órgão (padrão PNCP)
2. Keyword do setor matcha no nome do órgão com **baixa densidade** (~1-3%)
3. Baixa densidade envia para LLM (`llm_conservative` ou `llm_zero_match`)
4. LLM prompt NÃO instrui ignorar nomes de órgãos
5. LLM retorna SIM → resultado irrelevante classificado como relevante
6. Exclusões por setor NÃO cobrem categorias genéricas cross-setor (veículos, papelaria, alimentação, informática, combustível)

## Critérios de Aceite

### Bloco 1: `_strip_org_context()` — função cross-setor em filter.py

- [ ] AC1: Criar função `_strip_org_context(texto: str) -> str` em `filter.py` que remove cláusulas de contexto de órgão do `objetoCompra` ANTES do keyword matching. Padrões regex a strip (clause-level, não word-level):
  ```
  - "para atend(er|imento) (a|à)s? (necessidades|demandas) (da|das|do|dos) ..." até fim
  - "de interesse (da|das|do|dos) ..." até fim
  - "em atendimento (a|à)s? (demandas?|necessidades?) (da|das|do|dos) ..." até fim
  - "visando atender ..." até fim
  - "pertencentes? (a|à|ao)s? ... (prefeitura|secretaria|município) ..." até fim
  - "a pedido (da|do) ..." até fim
  - "através (da|do) ..." até fim (quando seguido de nome de órgão)
  ```
- [ ] AC2: Strip também prefixos de fonte PCP: `[Portal de Compras Públicas] -` e variantes
- [ ] AC3: A função opera em texto normalizado (sem acentos) para capturar todas as variações
- [ ] AC4: O texto original é preservado para display — `_strip_org_context()` é usado APENAS para matching/density
- [ ] AC5: Aplicar `_strip_org_context()` na linha `filter.py:2459` ANTES de chamar `match_keywords()`:
  ```python
  objeto = lic.get("objetoCompra", "")
  objeto_for_matching = _strip_org_context(objeto)  # NEW
  match, matched_terms = match_keywords(objeto_for_matching, kw, exc, ...)
  ```
- [ ] AC6: Cross-validação com `nomeOrgao`: se uma keyword matchada aparece TAMBÉM no campo `nomeOrgao` da licitação E NÃO aparece no objeto stripped, descontar do density calculation

### Bloco 2: Exclusões genéricas cross-setor em sectors_data.yaml

- [ ] AC7: Criar seção `global_exclusions` no topo de `sectors_data.yaml` (ou em `filter.py` como constante) com categorias genéricas de compra que geram FP em QUALQUER setor:
  ```yaml
  global_exclusions:
    - "locação de veículo"    / "locação de veículos"    / sem acento
    - "material de escritório" / "material de papelaria"  / sem acento
    - "gêneros alimentícios"  / "gênero alimentício"      / sem acento
    - "equipamentos de informática" / "insumos de informática" / sem acento
    - "combustível" / "abastecimento de combustível" / sem acento
    - "serviço de limpeza" / "serviço de conservação"     / sem acento
    - "construção de muro" / "construção de cerca"        / sem acento
    - "material de copa e cozinha" / sem acento
    - "passagem aérea" / "passagens aéreas" / sem acento
    - "serviço de telefonia" / sem acento
  ```
- [ ] AC8: `global_exclusions` são aplicadas a TODOS os setores antes das exclusões específicas do setor
- [ ] AC9: Exclusões existentes por setor (ex: 72 do Saúde) permanecem intactas
- [ ] AC10: Cada setor pode ter um `global_exclusions_override` para excluir itens da lista global que SÃO relevantes para aquele setor (ex: setor `alimentos` pode override "gêneros alimentícios")

### Bloco 3: LLM prompt hardening (todos os setores)

- [ ] AC11: No `llm_arbiter.py:_build_zero_match_prompt()`, adicionar instrução: "ATENÇÃO: O campo 'Objeto' pode conter o nome do órgão comprador (ex: 'Secretaria de Saúde', 'Prefeitura Municipal'). IGNORE completamente nomes de órgãos/secretarias/hospitais/universidades. Foque EXCLUSIVAMENTE no que está sendo CONTRATADO ou ADQUIRIDO."
- [ ] AC12: No `llm_arbiter.py:_build_arbiter_prompt()` (density 1-5%), adicionar a mesma instrução
- [ ] AC13: Adicionar exemplos negativos dinâmicos ao prompt (baseados no setor): para cada setor, incluir 2-3 exemplos de "NÃO é {setor}" que usam o nome de órgão como armadilha
- [ ] AC14: O `objeto_truncated` passado ao LLM deve usar o texto JÁ STRIPPED (pós `_strip_org_context()`)

### Bloco 4: Auditoria dos 15 setores

- [ ] AC15: Auditar os 15 setores e documentar para cada um: (a) keywords vulneráveis a org name FP, (b) exclusões que faltam, (c) context_required_keywords adequados
- [ ] AC16: Para os 3 setores diretamente vulneráveis (saude, informatica, vigilancia), adicionar `context_required_keywords` para keywords genéricas:
  - `saude`: "saúde" requer contexto: "médico", "hospitalar", "medicamento", "paciente", "clínico", "ambulatorial", "SUS"
  - `informatica`: "tecnologia" requer contexto: "informação", "TI", "computador", "servidor", "rede", "sistema"
  - `vigilancia`: "segurança" requer contexto: "patrimonial", "vigilante", "monitoramento", "CFTV", "alarme"

### Bloco 5: Validação e testes

- [ ] AC17: Teste com os 7 exemplos reais de Saúde (produção 2026-02-28) — TODOS devem ser rejeitados
- [ ] AC18: Teste com exemplos sintéticos para CADA um dos 15 setores: "compra de X para Secretaria de {setor}" deve ser rejeitado quando X é genérico
- [ ] AC19: Teste que licitações legítimas continuam passando para cada setor:
  - Saúde: "aquisição de medicamentos para hospital municipal" → APROVADO
  - Informática: "servidores Dell PowerEdge para datacenter da Secretaria de Tecnologia" → APROVADO
  - Vigilância: "contratação de vigilância patrimonial armada" → APROVADO
- [ ] AC20: Teste de regressão: `pytest -k test_filter` com 0 falhas novas
- [ ] AC21: Teste de `_strip_org_context()` com 20+ variações de cláusulas de órgão
- [ ] AC22: Teste end-to-end: rodar pipeline completo com sample de 100 bids reais do PNCP, medir taxa de FP antes/depois, documentar redução

### Bloco 6: Métricas de qualidade

- [ ] AC23: Adicionar campo `org_context_stripped: bool` no result metadata quando `_strip_org_context()` alterou o texto — para análise posterior
- [ ] AC24: Log de nível DEBUG: "Stripped org context: '{removed_clause}' from bid {pncp_id}" para rastreabilidade
- [ ] AC25: Métrica Prometheus `smartlic_org_context_stripped_total` (counter, label: sector) para monitorar volume de strips

## Arquivos Afetados

- `backend/filter.py` (AC1-AC6: `_strip_org_context()`, integração antes de `match_keywords()`)
- `backend/sectors_data.yaml` (AC7-AC10: `global_exclusions`, AC16: `context_required_keywords`)
- `backend/llm_arbiter.py` (AC11-AC14: prompts hardened para todos os setores)
- `backend/sectors.py` (AC7-AC8: carregar `global_exclusions`)
- `backend/metrics.py` (AC25: nova métrica)
- `backend/tests/test_strip_org_context.py` (novo — AC17, AC21)
- `backend/tests/test_filter_cross_sector_fp.py` (novo — AC18-AC20)
- `backend/tests/test_llm_arbiter.py` (expandir — AC13)

## Impacto

Esta story é a **mais crítica** para a proposta de valor do SmartLic. Se o produto retorna "material de escritório" como oportunidade de Saúde, o usuário conclui que a IA não funciona e abandona durante o trial. O problema afeta TODOS os 15 setores — cada usuário de cada setor verá resultados irrelevantes.

Sem correção, a taxa de conversão trial→pago será efetivamente zero.

## Notas Técnicas

- O padrão PNCP inclui o comprador no `objetoCompra` — isso é comportamento da API, não bug nosso
- ~30% dos `objetoCompra` no PNCP contêm cláusulas de órgão (auditoria de 50 items reais)
- Strip deve ser clause-level (não word-level) para evitar remover palavras legítimas
- "serviços de secretaria" (secretariado) NÃO deve ser removido — por isso strip por cláusula, não por palavra
- Referência acadêmica: Zero-Shot Hierarchical Classification on CPV Taxonomy (Moiraghi et al., 2024) — preprocessar metadata separadamente do objeto
- A keyword "saúde" (e similares) deve ser MANTIDA — com o strip de contexto + context_required, ela matchará apenas quando "saúde" aparece no objeto real junto com termos médicos

## Ordem de implementação sugerida

1. `_strip_org_context()` + testes unitários (AC1-AC6, AC21)
2. `global_exclusions` + override (AC7-AC10)
3. LLM prompt hardening (AC11-AC14)
4. `context_required_keywords` para setores vulneráveis (AC16)
5. Testes cross-setor (AC17-AC22)
6. Métricas (AC23-AC25)
