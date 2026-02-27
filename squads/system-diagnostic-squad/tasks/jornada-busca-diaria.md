# jornada-busca-diaria

## Metadata
- agent: usuario-pagante
- elicit: false
- priority: critical
- estimated_time: 30min
- tools: [Playwright MCP, Backend API, Supabase CLI, Read, Grep, Bash]

## Objetivo
Simular o uso diario de um usuario pagante: busca, classificacao, pipeline, export.
Este e o core loop do SmartLic — se isso nao funcionar, o produto nao tem valor.

## Pre-requisitos
- Conta pagante ativa em https://smartlic.tech
- Setor definido na conta
- Acesso ao backend para API calls diretas

## Steps

### Step 1: Login e Estado Inicial
**Acao:** Login com usuario pagante
**Verificar:**
- [ ] Login funciona sem erro
- [ ] Dashboard carrega com estado correto (plano, quota restante)
- [ ] Sessao persiste (refresh nao desloga)
- [ ] Historico de buscas anteriores visivel
**Evidencia:** Screenshot dashboard + session token validity

### Step 2: Busca Multi-Fonte
**Acao:** Executar busca com setor real + 3-5 UFs
**Verificar:**
- [ ] Busca inicia e SSE progress funciona
- [ ] Fontes ativas: PNCP (obrigatorio), PCP e ComprasGov (bonus)
- [ ] Resultados deduplicados corretamente (sem duplicatas visiveis)
- [ ] Contagem de resultados coerente com o que o SSE reportou
- [ ] Tempo total < 120s para busca tipica
- [ ] Se uma fonte falhar, as outras compensam (fallback cascade)
**Evidencia:** SSE event log completo + response body + timing

### Step 3: Classificacao IA
**Acao:** Analisar os resultados da busca
**Verificar:**
- [ ] Cada resultado tem score de relevancia
- [ ] Source da classificacao presente (keyword/llm_standard/llm_zero_match)
- [ ] Spot-check: pegar 5 resultados e validar se a classificacao faz sentido
  - 2 resultados com score alto → sao realmente relevantes?
  - 2 resultados com score baixo → sao realmente irrelevantes?
  - 1 resultado edge case → classificacao defensavel?
- [ ] Nenhum resultado com score = null ou undefined
**Evidencia:** 5 items com classificacao + justificativa manual

### Step 4: Pipeline Kanban
**Acao:** Mover 3+ resultados para o pipeline
**Verificar:**
- [ ] Drag-and-drop funciona entre colunas
- [ ] Item persiste apos refresh da pagina
- [ ] Dados do item no pipeline batem com a busca original
- [ ] Nao ha duplicatas no pipeline
- [ ] Status do item atualiza corretamente no DB
**Evidencia:** Screenshot pipeline + Supabase pipeline_items query

### Step 5: Export Excel
**Acao:** Exportar resultados para Excel
**Verificar:**
- [ ] Botao de export funciona
- [ ] Arquivo .xlsx baixa corretamente
- [ ] Abrir o arquivo: colunas presentes, dados completos
- [ ] Formatacao/estilizacao aplicada (headers, filtros)
- [ ] Numero de linhas no Excel == numero de resultados na busca
- [ ] Caracteres especiais (acentos) corretos
**Evidencia:** Arquivo Excel + contagem de linhas + spot-check de dados

### Step 6: Resumo IA
**Acao:** Verificar resumo executivo gerado pela IA
**Verificar:**
- [ ] Resumo aparece (ou fallback funcional se ARQ job pendente)
- [ ] Conteudo do resumo e coerente com os resultados
- [ ] Se SSE `llm_ready` event chega, resumo atualiza
- [ ] Nenhum placeholder ou erro visivel no resumo
**Evidencia:** Texto do resumo + SSE events

### Step 7: Consistencia entre Sessoes
**Acao:** Fazer segunda busca similar e comparar
**Verificar:**
- [ ] Resultados da segunda busca sao consistentes com a primeira
- [ ] Historico mostra ambas as sessoes
- [ ] Quota decrementou 2x (uma por busca)
- [ ] Cache nao causa resultados stale (se periodo diferente)
**Evidencia:** Comparacao de contagens + Supabase search_sessions

## Output
Documento com:
- Status de cada step: PASS | FAIL | DEGRADED
- Evidencia para cada step
- Core loop funcional? SIM | NAO | PARCIAL
- Issues encontrados com severidade
