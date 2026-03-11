# INBOUND.md — Estratégia de Relatórios B2G a R$97 via Google Ads

**Data:** Março 2026
**Status:** Em estudo
**Autor:** Conselho Consultivo de CMOs (53 CMOs, 8 clusters) + Market Research
**Produto:** SmartLic Report — Relatório Executivo de Oportunidades B2G (avulso)

---

## 1. Resumo Executivo

Substituir o cold outreach manual (consultoria R$1.500/mês, baixa conversão) por um funil inbound via Google Ads vendendo relatórios individuais gerados pelo `/report-b2g` a **R$97/unidade**.

**Meta:** 10 relatórios/dia (R$970/dia = ~R$21.340/mês em 22 dias úteis).
**Prazo para atingir meta:** 60-90 dias.
**Investimento inicial em ads:** R$1.500/mês (R$50/dia).

**Por que funciona:**
- Nenhum concorrente vende relatórios avulsos — todos são SaaS mensais
- O report-b2g leva ~15 min para gerar e tem valor percebido de R$500+ (4-8h de trabalho de consultor)
- Google Search captura demanda existente (empresas já buscam "licitações [setor] [estado]")
- Margem bruta de ~94% por relatório (custo variável < R$6)
- O relatório avulso é cavalo de tróia para upsell (assinatura R$397/mês ou consultoria R$1.500/mês)

---

## 2. Contexto e Problema

### Situação Atual
- Founder solo, sem aptidão comercial, fazendo "trabalho de formiguinha" abordando leads individualmente
- Cold outreach para consultoria R$1.500/mês tem conversão muito baixa (alto ticket + zero confiança pré-estabelecida)
- Ferramentas como `/report-b2g` geram material impactante, mas negociação e tracking recaem sobre disponibilidade limitada do founder
- A assimetria desejada (pouco esforço → alto retorno) não se materializa no modelo atual

### Diagnóstico
O cold outreach fracassou **por design, não por execução**. Vender R$1.500/mês via mensagem fria para PMEs B2G exige confiança pré-estabelecida que não existe no primeiro contato. O relatório a R$97 inverte a dinâmica: cliente paga pouco, recebe muito valor, e pede mais. O upsell para assinatura acontece organicamente.

---

## 3. O Produto: SmartLic Report

### O que é
Relatório executivo PDF personalizado por CNPJ que inclui:

| Seção | Conteúdo | Diferencial |
|-------|----------|-------------|
| Perfil da Empresa | OpenCNPJ + check de sanções (CEIS/CNEP/CEPIM/CEAF) + histórico de contratos federais | Dados cruzados de 3 fontes públicas |
| Varredura de Editais | Scan multi-fonte: PNCP + PCP v2 + Querido Diário (últimos 30 dias) | Nenhum concorrente faz varredura multi-fonte avulsa |
| **Análise Documental** | **Download e leitura dos PDFs reais dos editais** — requisitos de habilitação, prazos, red flags | **Único no mercado** — concorrentes mostram metadados, não o documento |
| Inteligência Competitiva | Mapeamento de incumbentes, histórico de preços, nível de competição | Dados de PNCP histórico cruzados com OpenCNPJ |
| Recomendação Estratégica | PARTICIPAR / AVALIAR / NÃO RECOMENDADO — com motivo factual por edital | Baseado em cruzamento perfil x edital x documento |
| Próximos Passos | Lista exata de documentos a preparar, extraída do edital real | Acionável, não genérico |

### Custo de produção

| Componente | Custo por relatório | Fonte |
|------------|-------------------|-------|
| OpenAI GPT-4.1-nano (~5 chamadas) | R$0,50 | Pricing OpenAI março/2026 |
| APIs PNCP + PCP v2 + Querido Diário | R$0,00 | APIs públicas gratuitas |
| Infraestrutura Railway (compute) | R$0,20 | Estimativa pro-rata do plano atual |
| Stripe (3,99% + R$0,39) | R$4,26 | [Stripe Brasil pricing](https://stripe.com/br/pricing) |
| **Tempo do founder (15 min)** | **R$25,00** | Valoração a R$100/h |
| **COGS total** | **~R$30,00** | |
| **Margem bruta** | **R$67,00 (69%)** | Incluindo tempo do founder |
| **Margem bruta (sem tempo)** | **R$92,04 (94,9%)** | Custo variável puro |

### Tempo de produção
- Geração via `/report-b2g`: 5-15 minutos (dependendo do número de editais e PDFs)
- Revisão + envio: 5 minutos
- **Total por relatório: ~15-20 minutos**
- **Capacidade diária: 10 relatórios = 2,5-3,5h de trabalho**

---

## 4. Análise de Mercado

### 4.1 Tamanho do Mercado (TAM)

| Métrica | Valor | Fonte |
|---------|-------|-------|
| Volume anual de compras públicas no Brasil | R$1,52 trilhão (~12% do PIB) | [Otmow — Compras Públicas Brasil (set/2025)](https://otmow.com/2025/09/05/o-mercado-de-compras-publicas-no-brasil-numeros-setores-e-oportunidades/), [IBGE PIB 2025](https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/45968-pib-cresce-2-3-em-2025-e-fecha-o-ano-em-r-12-7-trilhoes) |
| Fornecedores registrados no Compras.gov.br (federal) | 452.500 | [e-Licitagov — Guia SICAF 2026](https://e-licitagov.com.br/informativos/o-que-e-sicaf-guia-definitivo-2026) |
| % que são micro e pequenas empresas (MPEs) | 67,7% (297.200 empresas) | [Agência Sebrae — Participação MPEs](https://agenciasebrae.com.br/economia-e-politica/participacao-das-mpe-nas-compras-publicas-cresceu-93-nos-ultimos-tres-anos/) |
| Crescimento MPEs em compras públicas (2018-2021) | +93% (R$21,3B → R$41B) | Agência Sebrae (ibid.) |
| Fornecedores estimados (todos os níveis gov) | 1-2 milhões | Extrapolação federal → estadual/municipal |
| Participação MPEs em processos homologados (2025) | 82%+ | [Effecti — Panorama Licitações 2026](https://effecti.com.br/panorama-das-licitacoes-e-tendencias-para-2026/) |

**TAM para relatórios avulsos:**
- Conservador: 1% de 452.500 fornecedores federais × 1 relatório/ano × R$97 = **R$4,4M/ano**
- Moderado: 2% de 1M fornecedores × 1,5 relatórios/ano × R$97 = **R$2,9M/ano**
- Agressivo: 5% de 1M × 2 relatórios/ano × R$97 = **R$9,7M/ano**

### 4.2 Cenário Competitivo

| Plataforma | Modelo | Vende relatório avulso? | Preço | Fonte |
|------------|--------|------------------------|-------|-------|
| Effecti | SaaS mensal | Não | Planos tiered (calculadora custom) | [effecti.com.br/plataforma](https://effecti.com.br/plataforma/) |
| ConLicitação | SaaS mensal | Não | Assinatura (pricing fechado) | [conlicitacao.com.br/planos](https://conlicitacao.com.br/planos/) |
| Licitagov | SaaS mensal | Não | Assinatura | [licitagov.org](https://licitagov.org/) |
| LicitaIA | SaaS + créditos | Não (créditos mensais) | Basic 30 créditos / PRO 60 créditos | [licitaia.app](https://www.licitaia.app/) |
| Wavecode | SaaS mensal | Não | Planos custom | [wavecode.com.br/planos](https://www.wavecode.com.br/planos/) |
| Alerta Licitação | SaaS mensal | Não | Assinatura | [alertalicitacao.com.br](https://alertalicitacao.com.br/) |
| Lictus | SaaS mensal | Não (relatórios inclusos) | Assinatura | [lictus.com.br](https://lictus.com.br/) |
| **SmartLic Report** | **Avulso** | **SIM — R$97** | **R$97/unidade** | **Categoria nova** |

**Conclusão:** Nenhum concorrente identificado vende relatórios de inteligência avulsos por CNPJ. Todos operam exclusivamente com modelo de assinatura mensal/anual. O SmartLic Report cria uma **categoria nova**: "consultoria on-demand de licitações".

### 4.3 Referências de Preço (Mercado de Relatórios B2B)

| Produto | Preço | Tipo | Fonte |
|---------|-------|------|-------|
| Crunchbase Company Report | US$99-199 | Perfil empresarial | crunchbase.com |
| Dun & Bradstreet Credit Report | US$150-300 | Crédito empresarial | dnb.com |
| IBISWorld Industry Report | US$1.195 | Análise setorial | ibisworld.com |
| Consultor de licitações (CLT) | ~R$3.000/mês + encargos | Profissional interno | [Triunfo Legis](https://www.triunfolegis.com.br/consultoria-licitacoes-preco) |
| Consultoria de licitações (PJ) | R$1.500-5.000/mês ou % do contrato | Serviço externo | [Effecti — Como Cobrar](https://effecti.com.br/como-cobrar-comissionamento-na-consultoria-de-licitacoes/) |
| **SmartLic Report** | **R$97 (~US$18)** | **Inteligência personalizada** | **Proposta** |

O posicionamento a R$97 é extremamente competitivo: ~US$18 por um relatório hiper-personalizado que substitui 4-8h de trabalho de consultor.

---

## 5. Estratégia de Aquisição: Google Ads Search

### 5.1 Por que Google Ads (e não Meta)

| Critério | Google Ads Search | Meta/Instagram |
|----------|------------------|----------------|
| Intenção do usuário | **Alta** — busca ativa por "licitações" | Baixa — scrollando feed |
| CPC B2B Brasil | R$1-5 (keywords nicho) | R$5,40 média B2B |
| Conversão direta | 2-5% landing page | 0,5-1% cold |
| Bot traffic Brasil | Baixo | 20-30% maior que Tier 1 |
| Melhor para | Aquisição direta | Retargeting (fase 3+) |
| Custo de criativo | Zero (só texto) | Alto (vídeo/imagem) |

**Fontes:**
- CPC Google Ads Brasil: [MetricNexus — Benchmarks 2026](https://metricnexus.ai/blog/google-ads-benchmarks-2026), [WordStream — Average CPC](https://www.wordstream.com/blog/average-cost-per-click)
- CPC Meta Brasil: [AdAmigo — CPM/CPC Benchmarks 2026](https://www.adamigo.ai/blog/meta-ads-cpm-cpc-benchmarks-by-country-2026)
- Bot traffic: [SQ Magazine — Social Media Advertising Statistics 2026](https://sqmagazine.co.uk/social-media-advertising-statistics/)

### 5.2 Keywords e Volume Estimado

| Cluster de Keywords | Vol. Mensal Estimado (Brasil) | Competição | CPC Estimado |
|--------------------|------------------------------|------------|-------------|
| "licitações abertas" | 10K-50K | Média-Alta | R$2-5 |
| "licitações [setor]" (ex: "licitações construção civil") | 1K-10K cada | **Baixa** | R$1-3 |
| "editais [cidade/estado]" (ex: "editais São Paulo") | 1K-5K cada | **Baixa** | R$0,80-2 |
| "como participar de licitação" | 5K-20K | Baixa-Média | R$1,50-3 |
| "oportunidades licitação [segmento]" | 1K-5K | **Baixa** | R$1-2,50 |
| "plataforma licitações" | 1K-5K | Alta | R$5-10 |

**Fontes:** Triangulação de [uPrOAS — Google Ads Benchmarks 2026](https://www.uproas.io/blog/google-ads-benchmarks), [WebFX — PPC Benchmarks 2026](https://www.webfx.com/blog/marketing/ppc-benchmarks-to-know/), [Google Keyword Planner](https://ads.google.com/intl/pt-BR_br/home/tools/keyword-planner/).

**Nota:** Volumes exatos requerem acesso ao Google Keyword Planner com conta ativa. Estimativas baseadas em dados de mercado e atividade de concorrentes.

**Estratégia recomendada:**
1. Começar com keywords long-tail setoriais: "licitações construção civil SC", "editais obras públicas MG"
2. Evitar keywords broad ("licitações", "editais") — cliques irrelevantes de servidores e estudantes
3. 3 campanhas iniciais: intenção direta, educacional, descoberta por localidade
4. Negativar: "concurso", "emprego", "estágio", "resultado", "como fazer"

### 5.3 Estrutura de Campanhas

**Campanha 1 — Intenção Direta (60% do budget)**
- Keywords: "licitações [setor] [estado]", "editais abertos [setor]"
- Anúncio: "Relatório de Licitações do seu Setor — R$97 | Editais analisados com IA"
- Landing: `/relatorio`

**Campanha 2 — Educacional (25% do budget)**
- Keywords: "como participar de licitação", "documentos para licitação"
- Anúncio: "Saiba Quais Licitações Valem a Pena | Análise por IA em 24h"
- Landing: `/relatorio` (com conteúdo educacional acima do formulário)

**Campanha 3 — Descoberta Local (15% do budget)**
- Keywords: "editais [cidade]", "licitações [município] 2026"
- Anúncio: "Licitações Abertas em [Cidade] — Relatório Personalizado R$97"
- Landing: `/relatorio` (com UF pré-selecionada via UTM)

---

## 6. Funil de Conversão

```
Google Ads (R$50/dia)
    ↓ CPC R$3-5 = 10-17 cliques/dia
Landing Page /relatorio
    ↓ 20-25% preenchem formulário (CNPJ + setor + UF + email + WhatsApp)
    = 2-4 leads/dia
Preview Gratuito por Email (automático via Resend)
    ↓ 1 página: 3 editais relevantes + resumo do perfil (sem análise documental)
    ↓ 25-33% convertem para compra
Stripe Checkout R$97
    ↓ = 1-2 vendas/dia (mês 1)
Entrega do Relatório Completo (manual, 15 min)
    ↓ Via email + WhatsApp
Follow-up de Upsell (7 dias depois)
    ↓ "Quer receber isso todo mês? R$397/mês"
    ↓ 5% convertem para assinatura
```

### O Preview Gratuito — Mecanismo Crítico

O preview de 1 página é o **make-or-break** do funil. Sem ele, o lead não tem como avaliar a qualidade antes de pagar R$97, e o CAC estoura. Com ele, demonstra-se valor concreto (editais reais do setor do lead) e a conversão para compra sobe de ~10% para 25-33%.

**Conteúdo do preview (1 página, automático):**
- Nome da empresa + CNPJ + setor identificado
- "Encontramos X editais abertos relevantes para seu perfil"
- Tabela com 3 editais: objeto (resumido), órgão, valor, data abertura
- SEM análise documental, SEM recomendação, SEM competitiva
- CTA: "Relatório completo com análise de cada edital → R$97"

---

## 7. Projeções Financeiras

### 7.1 Unit Economics por Relatório

```
RECEITA
  Preço de venda:                     R$ 97,00

CUSTOS VARIÁVEIS
  Stripe (3,99% + R$0,39):           -R$ 4,26
  OpenAI GPT-4.1-nano (~5 calls):    -R$ 0,50
  PNCP/PCP/QD APIs:                  -R$ 0,00
  Railway compute (pro-rata):        -R$ 0,20
  Total custos variáveis:            -R$ 4,96

MARGEM DE CONTRIBUIÇÃO:               R$ 92,04 (94,9%)

CUSTO DE AQUISIÇÃO (cenários)
  Conservador (sem preview):          R$ 125   → PREJUÍZO
  Com preview (base):                 R$ 48    → Margem R$44 (45%)
  Otimista (preview + retargeting):   R$ 30    → Margem R$62 (64%)
  Orgânico (indicação/SEO):           R$ 0     → Margem R$92 (95%)

CUSTO DO TEMPO DO FOUNDER
  15 min/relatório × R$100/h:        R$ 25,00
  Margem líquida (com preview):      R$ 19,04/relatório
```

### 7.2 Modelagem CAC Detalhada

**Cenário Base (com preview gratuito):**

| Etapa | Métrica | Fonte |
|-------|---------|-------|
| CPC médio | R$4,00 | [MetricNexus 2026](https://metricnexus.ai/blog/google-ads-benchmarks-2026) — B2B Brasil |
| CTR (Click-Through Rate) | 3,5% | [uPrOAS 2026](https://www.uproas.io/blog/google-ads-benchmarks) — B2B services |
| Conversão landing → lead | 25% | [Unbounce 2025 Benchmarks](https://unbounce.com/conversion-benchmark-report/) — B2B SaaS |
| Conversão lead → preview enviado | 100% | Automático via Resend |
| Conversão preview → compra | 30% | Estimativa baseada em [First Page Sage Funnel Benchmarks 2026](https://firstpagesage.com/seo-blog/sales-funnel-conversion-rate-benchmarks-2025-report/) — adjusted for low-ticket |
| **Cliques para 1 venda** | 13,3 | 1 / (0.25 × 0.30) |
| **CAC** | **R$53,33** | 13,3 × R$4,00 |
| **Margem após CAC** | **R$38,71 (39,9%)** | R$92,04 - R$53,33 |

**Cenário Conservador (sem preview, venda direta):**

| Etapa | Métrica | Referência |
|-------|---------|------------|
| CPC médio | R$5,00 | Keywords mais competitivas |
| Conversão landing → compra direta | 2% | [VWO Funnel Conversion Rates 2026](https://vwo.com/blog/what-is-a-good-funnel-conversion-rate/) |
| Cliques para 1 venda | 50 | 1 / 0.02 |
| **CAC** | **R$250** | 50 × R$5,00 |
| **Resultado** | **-R$158 PREJUÍZO** | Modelo inviável sem preview |

**Cenário Otimista (preview + remarketing Meta mês 3+):**

| Etapa | Métrica | Referência |
|-------|---------|------------|
| CPC médio blended (Google 70% + Meta retargeting 30%) | R$3,50 | Split recomendado |
| Conversão com retargeting | 35% preview → compra | Retargeting aumenta conversão em 30-50% ([SaaSRise Case Study](https://www.saasrise.com/blog/case-study-how-a-b2b-saas-firm-scaled-new-customer-acquisition-353-from-ads)) |
| **CAC** | **R$40** | |
| **Margem após CAC** | **R$52,04 (53,6%)** | |

### 7.3 Projeção de Receita Mensal

| Métrica | Mês 1 | Mês 2 | Mês 3 (meta) | Mês 6 | Mês 12 |
|---------|-------|-------|--------------|-------|--------|
| Gasto ads/dia | R$30 | R$50 | R$50 | R$75 | R$100 |
| Gasto ads/mês | R$660 | R$1.100 | R$1.100 | R$1.650 | R$2.200 |
| Cliques/dia | 8 | 13 | 13 | 19 | 25 |
| Leads/dia | 2 | 3 | 3 | 5 | 6 |
| Vendas/dia (relatórios) | 0,5 | 1,5 | 3-5 | 5-8 | 8-10 |
| **Receita relatórios/mês** | **R$1.067** | **R$3.201** | **R$6.500-10.700** | **R$10.700-17.100** | **R$17.100-21.340** |
| CAC médio | R$80 | R$55 | R$45 | R$35 | R$30 |
| Upsells assinatura R$397 | 0 | 1 | 2-3 | 3-5 | 5-8 |
| **Receita upsell/mês** | R$0 | R$397 | R$794-1.191 | R$1.191-1.985 | R$1.985-3.176 |
| **Receita total/mês** | **R$1.067** | **R$3.598** | **R$7.294-11.891** | **R$11.891-19.085** | **R$19.085-24.516** |
| Lucro operacional/mês | -R$100 | R$1.500 | R$4.500-8.500 | R$8.500-15.000 | R$15.000-20.000 |

**Premissas:**
- 22 dias úteis/mês
- CAC decresce com otimização de campanhas e acúmulo de dados (Google Ads learning period: 2-4 semanas)
- Upsell rate de 5% dos compradores de relatório (conservador — [HelloFunnels low-ticket upsell benchmark](https://hellofunnels.co/208-how-to-upsell-your-low-ticket-offer-in-2024/): 15-25% para first upsell)
- Churn de assinatura: 10%/mês (padrão SaaS B2B Brasil)
- Sem considerar recompra de relatórios (upside adicional)

### 7.4 Lifetime Value (LTV) por Comprador de Relatório

| Componente | Conversão | Receita | LTV Ponderado |
|------------|-----------|---------|---------------|
| Relatório inicial | 100% | R$97 | R$97,00 |
| Segundo relatório (30 dias) | 15-20% | R$97 | R$14,55-19,40 |
| Terceiro relatório (60 dias) | 8-10% | R$97 | R$7,76-9,70 |
| Upgrade assinatura SmartLic Pro (R$397/mês × 6 meses médios) | 5% | R$2.382 | R$119,10 |
| Upgrade consultoria (R$1.500/mês × 4 meses médios) | 1-2% | R$6.000 | R$60-120 |

| Cenário | LTV Total | CAC (preview) | LTV:CAC |
|---------|-----------|---------------|---------|
| Conservador | R$238 | R$53 | **4,5x** |
| Base | R$298 | R$48 | **6,2x** |
| Otimista | R$365 | R$40 | **9,1x** |

**Referência:** LTV:CAC saudável para SaaS B2B: >3x ([SaaS Metrics 2.0 — For Entrepreneurs](https://www.forentrepreneurs.com/saas-metrics-2/), [CloudZero — SaaS Unit Economics](https://www.cloudzero.com/blog/saas-unit-economics/)).

### 7.5 Break-Even

| Cenário | CAC | Margem/relatório | Relatórios para cobrir ads (R$1.100/mês) | Dias úteis |
|---------|-----|------------------|------------------------------------------|-----------|
| Base (com preview) | R$53 | R$38,71 | 29 relatórios/mês | ~1,3/dia |
| Otimista | R$40 | R$52,04 | 22 relatórios/mês | 1/dia |
| Incluindo tempo founder | R$53 | R$13,71 | 81 relatórios/mês | 3,7/dia |

**Break-even de ads puro:** ~1,3 relatórios/dia (atingível no mês 1).
**Break-even incluindo custo de oportunidade do tempo:** ~3,7 relatórios/dia (atingível no mês 2).

---

## 8. Playbook de Execução

### Fase 1 — Setup (Dias 0-7)

| Ação | Tempo | Prioridade |
|------|-------|-----------|
| Landing page `/relatorio` no Next.js | 2-4h | P0 |
| Stripe Checkout link (produto "Relatório Executivo B2G" R$97) | 30 min | P0 |
| Template de preview (1 página) no Resend | 1-2h | P0 |
| Conta Google Ads + configuração de campanhas | 2-3h | P0 |
| Relatório exemplo anonimizado para landing page | 1h | P0 |
| WhatsApp Business configurado | 30 min | P1 |
| **Total:** | **~8-12h** | |

### Fase 2 — Validação (Dias 7-30)

- Ligar campanhas com R$30/dia
- Monitorar diariamente: CPC, CTR, leads, conversão preview→compra
- Gerar relatórios manualmente, coletar feedback por WhatsApp
- **Stop-loss:** Se CAC > R$80 após 30 leads, pausar e revisar landing/preview
- **Go-signal:** Se CAC < R$60 e NPS > 8, aumentar budget para R$50/dia

### Fase 3 — Escala (Dias 30-90)

- Aumentar budget para R$50-75/dia
- Introduzir pacote "3 relatórios por R$249" (R$83/un)
- Adicionar email nurture sequence (7 dias) para upsell assinatura
- Adicionar Meta retargeting (20% do budget) para leads que não compraram
- Semi-automatizar coleta de dados (formulário → OpenCNPJ + PNCP scan automático)
- Meta: 5-10 relatórios/dia

### Fase 4 — Otimização (Dias 90+)

- SEO complementar (blog sobre licitações por setor)
- Programa de indicação (relatório grátis por indicação que compra)
- Avaliar automação completa (self-service no SmartLic)
- Escalar para setores além de Engenharia/Construção

---

## 9. Setores Prioritários

Começar com setores onde o report-b2g gera mais valor (editais complexos, PDFs densos, valores altos):

| Prioridade | Setor | % do mercado B2G | Ticket médio editais | Qualidade do relatório |
|-----------|-------|-----------------|---------------------|----------------------|
| 1 | Engenharia, Projetos e Obras | ~35% | R$500K-50M | Excelente (PDFs longos, requisitos técnicos) |
| 2 | Tecnologia e Sistemas | ~15% | R$100K-5M | Muito boa (empresas digitais convertem melhor online) |
| 3 | Equipamentos e Insumos Hospitalares | ~12% | R$200K-20M | Boa (alto volume, alta recorrência) |
| 4 | Serviços de Engenharia e Manutenção | ~10% | R$100K-10M | Boa |
| 5 | Alimentação e Nutrição | ~8% | R$50K-5M | Média (pregões menores, menos análise documental) |

**Recomendação:** Começar APENAS com setores 1-2 nas primeiras 4 semanas. Expandir conforme valida conversão.

---

## 10. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|-------------|---------|-----------|
| CAC estoura ticket nos primeiros 30 dias | Média | Alto | Preview gratuito obrigatório; stop-loss R$80 CAC após 30 leads |
| Gargalo de capacidade (>10/dia) | Baixa (mês 1-3) | Médio | Problema excelente — semi-automatizar ou contratar freelancer |
| PNCP/PCP instável no dia da geração | Média | Médio | Disclaimer honesto + atualização gratuita quando normalizar |
| Concorrente copia modelo avulso | Baixa (3-6m) | Médio | Defesa: qualidade documental, velocidade, relação WhatsApp |
| Google Ads desaprovação | Baixa | Alto | Compliance total, sem promessas de resultado financeiro |
| Baixa qualidade percebida em setores simples | Média | Médio | Restringir a setores 1-3 inicialmente |
| Canibalização da assinatura | Baixa | Baixo | Públicos diferentes: avulso = experimentação, assinatura = monitoramento contínuo |

---

## 11. Anti-Patterns — O que NÃO fazer

1. **NÃO usar Meta/Instagram Ads no mês 1** — CPM alto, intenção baixa, criativo caro
2. **NÃO automatizar entrega antes de 50 vendas** — Cada relatório manual é iteração de produto + conversa com cliente
3. **NÃO oferecer grátis** — O preview de 1 página É a amostra. Relatório completo é pago. Ponto.
4. **NÃO atacar 15 setores simultaneamente** — Engenharia + Tecnologia primeiro
5. **NÃO construir checkout integrado no SmartLic agora** — Stripe Checkout link resolve em 30 min
6. **NÃO investir em SEO/blog no mês 1** — SEO leva 3-6 meses. Ads geram leads no dia 1.
7. **NÃO abandonar leads qualificados existentes** — Zambeline, Gamarra, GJS, Líder Obras são candidatos a assinatura. 1 WhatsApp semanal basta.
8. **NÃO usar R$99** — Usar **R$97** (preço psicológico padrão low-ticket brasileiro, fonte: [Estúdio Site — Low Ticket](https://www.estudiosite.com.br/site/ead/low-ticket-infoproduto-27-a-97-em-alto-volume))

---

## 12. Métricas de Acompanhamento (Dashboard Diário)

| Métrica | Meta Mês 1 | Meta Mês 3 | Frequência |
|---------|-----------|-----------|-----------|
| CAC (gasto total / vendas) | < R$80 | < R$50 | Diária |
| Conversão preview → compra | > 20% | > 30% | Diária |
| Tempo formulário → entrega | < 24h | < 12h | Por venda |
| NPS do relatório | > 8 | > 9 | Por venda (48h depois) |
| Taxa de recompra (30 dias) | > 10% | > 20% | Semanal |
| Upsell para assinatura | > 3% | > 5% | Mensal |
| ROAS (Revenue / Ad Spend) | > 1,5x | > 5x | Semanal |

---

## 13. Fontes Consolidadas

### Mercado e TAM
- [Otmow — O Mercado de Compras Públicas no Brasil (set/2025)](https://otmow.com/2025/09/05/o-mercado-de-compras-publicas-no-brasil-numeros-setores-e-oportunidades/)
- [Effecti — Panorama das Licitações 2026](https://effecti.com.br/panorama-das-licitacoes-e-tendencias-para-2026/)
- [Agência Sebrae — Participação das MPEs nas Compras Públicas](https://agenciasebrae.com.br/economia-e-politica/participacao-das-mpe-nas-compras-publicas-cresceu-93-nos-ultimos-tres-anos/)
- [IBGE — PIB 2025](https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/45968-pib-cresce-2-3-em-2025-e-fecha-o-ano-em-r-12-7-trilhoes)
- [e-Licitagov — Guia SICAF 2026](https://e-licitagov.com.br/informativos/o-que-e-sicaf-guia-definitivo-2026)

### Google Ads e CPC
- [MetricNexus — Google Ads Benchmarks 2026](https://metricnexus.ai/blog/google-ads-benchmarks-2026)
- [uPrOAS — 2026 Google Ads Benchmarks](https://www.uproas.io/blog/google-ads-benchmarks)
- [WebFX — 2026 PPC Benchmarks](https://www.webfx.com/blog/marketing/ppc-benchmarks-to-know/)
- [WordStream — Average CPC by Country](https://www.wordstream.com/blog/average-cost-per-click)
- [Google Keyword Planner](https://ads.google.com/intl/pt-BR_br/home/tools/keyword-planner/)

### Meta Ads
- [AdAmigo — Meta Ads CPM/CPC Benchmarks by Country 2026](https://www.adamigo.ai/blog/meta-ads-cpm-cpc-benchmarks-by-country-2026)
- [SQ Magazine — Social Media Advertising Statistics 2026](https://sqmagazine.co.uk/social-media-advertising-statistics/)

### Conversão e Funnels
- [First Page Sage — Sales Funnel Conversion Rate Benchmarks 2026](https://firstpagesage.com/seo-blog/sales-funnel-conversion-rate-benchmarks-2025-report/)
- [First Page Sage — B2B Conversion Rates by Industry 2026](https://firstpagesage.com/reports/b2b-conversion-rates-by-industry-fc/)
- [VWO — What Is a Good Funnel Conversion Rate (2026)](https://vwo.com/blog/what-is-a-good-funnel-conversion-rate/)
- [HelloFunnels — How to Upsell Low-Ticket Offers](https://hellofunnels.co/208-how-to-upsell-your-low-ticket-offer-in-2024/)

### Low-Ticket Funnels (Brasil)
- [Estúdio Site — Low Ticket: Infoproduto de R$27 a R$97](https://www.estudiosite.com.br/site/ead/low-ticket-infoproduto-27-a-97-em-alto-volume)
- [Entrega Digital — Low Ticket Strategy](https://www.entregadigital.app.br/artigos/low-ticket-como-usar-essa-estrategia-para-vender-mais/)
- [Casuo Ishimine — Low Ticket para Tráfego Pago](https://casuoishimine.com.br/estrategia-low-ticket-trafego-pago/)

### Unit Economics SaaS
- [CloudZero — SaaS Unit Economics](https://www.cloudzero.com/blog/saas-unit-economics/)
- [For Entrepreneurs — SaaS Metrics 2.0](https://www.forentrepreneurs.com/saas-metrics-2/)
- [Paddle — Unit Economics](https://www.paddle.com/resources/unit-economics)

### Concorrentes
- [Effecti](https://effecti.com.br/plataforma/) | [ConLicitação](https://conlicitacao.com.br/planos/) | [Licitagov](https://licitagov.org/) | [LicitaIA](https://www.licitaia.app/) | [Wavecode](https://www.wavecode.com.br/planos/) | [Alerta Licitação](https://alertalicitacao.com.br/) | [Lictus](https://lictus.com.br/)

### Case Studies
- [Via Agência Digital — Matrix Go ROI +101%](https://www.viaagenciadigital.com.br/blog/trafego-pago-case-matrix-go/)
- [SaaSRise — B2B SaaS +353% Customer Acquisition](https://www.saasrise.com/blog/case-study-how-a-b2b-saas-firm-scaled-new-customer-acquisition-353-from-ads)

### Consultoria de Licitações (Pricing)
- [Triunfo Legis — Consultoria Licitações Preço](https://www.triunfolegis.com.br/consultoria-licitacoes-preco)
- [Effecti — Como Cobrar Consultoria](https://effecti.com.br/como-cobrar-comissionamento-na-consultoria-de-licitacoes/)

### Stripe
- [Stripe Brasil — Pricing](https://stripe.com/br/pricing)

---

*Documento gerado em 11/03/2026 pelo Conselho Consultivo de CMOs (53 CMOs, 8 clusters) com dados de mercado validados por web research. Projeções financeiras baseadas em benchmarks públicos — resultados reais variam conforme execução.*
