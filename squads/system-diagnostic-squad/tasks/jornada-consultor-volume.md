# jornada-consultor-volume

## Metadata
- agent: consultor-licitacao
- elicit: false
- priority: high
- estimated_time: 25min
- tools: [Backend API, Supabase CLI, Playwright MCP, Bash]

## Objetivo
Simular uso de volume alto — multiplos setores, multiplas UFs, muitas buscas sequenciais.
Validar que o sistema aguenta o padrao de uso de um power user sem degradar.

## Pre-requisitos
- Conta pagante com plano que permita volume (pro ou enterprise)
- Lista de 3+ setores diferentes para testar
- Acesso ao backend API

## Steps

### Step 1: Buscas Sequenciais Rapidas
**Acao:** Executar 5 buscas em sequencia rapida (intervalo < 30s entre cada)
**Verificar:**
- [ ] Todas as 5 buscas completam sem erro
- [ ] Nenhuma busca bloqueada por rate limiting indevido
- [ ] Tempos de resposta nao degradam significativamente (busca 5 nao e 3x mais lenta que busca 1)
- [ ] Cada busca gera sua propria sessao no DB
- [ ] Quota decrementada corretamente (5 unidades)
**Evidencia:** Tabela com [busca#, setor, UFs, tempo_resposta, resultados, status]

### Step 2: Multi-Setor
**Acao:** Buscar em 3 setores diferentes
**Verificar:**
- [ ] Resultados de cada setor sao distintos (nao ha contaminacao cross-setor)
- [ ] Classificacao IA adapta keywords por setor
- [ ] Nenhum resultado de "Tecnologia" aparece na busca de "Saude"
**Evidencia:** Comparacao de resultados por setor (top 3 items cada)

### Step 3: Multi-UF (Abrangencia Nacional)
**Acao:** Buscar com 10+ UFs simultaneamente
**Verificar:**
- [ ] Busca completa sem timeout (< 180s)
- [ ] Resultados vem de multiplas UFs (nao so 1-2)
- [ ] UF batching funciona (PNCP_BATCH_SIZE=5)
- [ ] Se alguma UF falhar, as outras retornam normalmente
**Evidencia:** Distribuicao de resultados por UF

### Step 4: Quota e Limites
**Acao:** Verificar comportamento proximo ao limite de quota
**Verificar:**
- [ ] Quota restante visivel para o usuario
- [ ] Aviso aparece quando quota esta baixa
- [ ] Quando quota esgota: mensagem clara (nao erro generico)
- [ ] Quota reseta corretamente no periodo (mensal)
- [ ] `check_and_increment_quota_atomic` funciona sem race condition
**Evidencia:** Supabase profiles query mostrando quota + comportamento UI

### Step 5: Exports em Volume
**Acao:** Gerar 3 exports Excel de buscas diferentes
**Verificar:**
- [ ] Todos os 3 exports completam
- [ ] Arquivos nao estao corrompidos
- [ ] ARQ jobs processam sem fila excessiva
- [ ] Nenhum export trava ou fica pendente indefinidamente
**Evidencia:** 3 arquivos Excel + status dos ARQ jobs

## Output
Documento com:
- Status de cada step: PASS | FAIL | DEGRADED
- Tabela de performance (tempos por busca)
- Limites encontrados (quota, rate limit, timeout)
- O sistema aguenta 50 usuarios nesse padrao? SIM | NAO | COM RESSALVAS
