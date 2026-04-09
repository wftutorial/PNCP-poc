# INBOUND-V2.md — Estratégia de Relatórios B2G a R$97 via Aquisição Multicanal

**Data:** 11 de março de 2026
**Status:** Em validação
**Autor:** Tiago Sasaki (CONFENGE Avaliações e Inteligência Artificial LTDA)
**Produto:** SmartLic Report — Relatório Executivo de Oportunidades B2G (avulso)
**Supersede:** INBOUND.md (V1, 11/03/2026) — corrige premissas de conversão, adiciona LGPD, retenção, canal de parceria, e limites operacionais

---

## 1. Resumo Executivo

Vender relatórios individuais de inteligência B2G a R$97/unidade, gerados pelo `/report-b2g`, usando dois canais de aquisição complementares: **parcerias com consultorias de licitação** (CAC zero) e **Google Ads Search** (CAC controlado).

**Metas realistas (founder solo com emprego CLT):**

| Horizonte | Meta | Receita mensal |
|-----------|------|----------------|
| Mês 1-2 | 3-5 relatórios/semana | R$1.300-2.100 |
| Mês 3-4 | 8-12 relatórios/semana | R$3.400-5.100 |
| Mês 6+ | 15-20 relatórios/semana | R$6.400-8.500 |

**Por que funciona:**
- Nenhum concorrente vende relatórios avulsos — todos operam modelo SaaS mensal (seção 4.2)
- Canal de parceria (consultorias + escolas de licitação) tem CAC zero e leads pré-qualificados
- Google Ads captura demanda existente — empresas já buscam "licitações [setor] [estado]"
- Margem bruta de ~69% incluindo tempo do founder (seção 7.1)
- Relatório avulso é porta de entrada para upsell definido (seção 11)

**O que mudou da V1:**
- Conversão landing page corrigida de 25% para **2,5%** (benchmark real Brasil — Leadster 2025)
- CAC recalculado: R$160-400 via ads (não R$53)
- Canal de parceria adicionado como canal primário (CAC zero)
- LGPD: seção completa de compliance (Art. 7, 8, 9, 10, 41)
- Limites de capacidade do founder: 12-20 relatórios/mês sustentável
- Estratégia de retenção e recompra detalhada
- Produto de upsell definido (consultoria mensal)
- Riscos de qualidade do PDF e relatório "ruim" endereçados
- Plano B/C/D para canais de aquisição
- "Conselho de CMOs" removido — autor é o founder com pesquisa de mercado verificável

---

## 2. Contexto e Problema

### Situação Atual
- Founder solo com emprego CLT, 10-15h/semana disponíveis para o projeto
- Cold outreach para consultoria R$1.500/mês tem conversão muito baixa (alto ticket + zero confiança)
- Ferramentas como `/report-b2g` geram relatórios de alta qualidade, mas a venda é manual
- Parceria com Descomplicita (escola de licitações) está aquecida mas não capitalizada

### Diagnóstico
O cold outreach fracassou **por design, não por execução**. Vender R$1.500/mês via mensagem fria para PMEs B2G exige confiança que não existe no primeiro contato. O relatório a R$97 inverte a dinâmica: cliente paga pouco, recebe muito valor, e pede mais. Mas a estratégia de aquisição precisa priorizar canais de baixo CAC (parcerias) antes de investir em ads.

### Restrição Crítica: Tempo do Founder

| Bloco de tempo | Capacidade realista | Fonte |
|----------------|--------------------|----|
| Noite útil (2h) | 1 revisão de relatório OU 1 batch de follow-up | [Self Financial — Side Hustle Statistics](https://www.self.inc/info/side-hustle-statistics/) |
| Fim de semana (4-5h) | 1-2 relatórios completos | [Memtime — Knowledge Worker Productivity](https://www.memtime.com/blog/knowledge-worker-productivity-stats-improvements) |
| Total semanal (10-15h) | 3-5 relatórios (a 2-3h cada) | Estimativa baseada em dados acima |
| Total mensal (sustentável) | **12-20 relatórios** | Acima de 25/mês entra em zona de burnout |
| Zona de burnout | >20h/semana ou >25 relatórios/mês | [Beta Boom — 72% of Founders Burn Out](https://betaboom.com/why-72-of-founders-burnout-how-to-beat-the-odds/) |

**Implicação:** A meta de "10 relatórios/dia" da V1 é fisicamente impossível para um founder solo com CLT. A meta real é 3-5/semana, escalando para 15-20/semana com automação parcial e VA.

---

## 3. O Produto: SmartLic Report

### O que é
Relatório executivo PDF personalizado por CNPJ que inclui:

| Seção | Conteúdo | Diferencial |
|-------|----------|-------------|
| Perfil da Empresa | OpenCNPJ + check de sanções (CEIS/CNEP/CEPIM/CEAF) + histórico de contratos federais | Dados cruzados de 3 fontes públicas |
| Varredura de Editais | Scan multi-fonte: PNCP + PCP v2 (últimos 30 dias) | Nenhum concorrente faz varredura multi-fonte avulsa |
| Análise Documental | Download e leitura dos PDFs reais dos editais — requisitos de habilitação, prazos, red flags | Único no mercado — concorrentes mostram metadados, não o documento |
| Inteligência Competitiva | Mapeamento de incumbentes, histórico de preços, nível de competição | Dados de PNCP histórico cruzados com OpenCNPJ |
| Recomendação Estratégica | PARTICIPAR / AVALIAR / NÃO RECOMENDADO — com motivo factual por edital | Baseado em cruzamento perfil × edital × documento |
| Próximos Passos | Lista exata de documentos a preparar, extraída do edital real | Acionável, não genérico |

### Limitações Conhecidas do Produto (Seção Nova)

| Limitação | Impacto | Mitigação |
|-----------|---------|-----------|
| **PDFs escaneados (image-only)** | Editais de municípios pequenos são frequentemente escaneados, impossibilitando extração de texto. TCU Acórdão 934/2021 reconhece o problema como sistêmico. | OCR via Azure (96% accuracy em português impresso). Para PDFs ilegíveis, relatório marca como "edital não processável — análise manual recomendada" com link direto. |
| **PDFs com senha/corrompidos** | Alguns editais têm proteção de senha ou estão corrompidos | Log de erro + inclusão no relatório como "documento protegido — contatar órgão licitante" |
| **Baixo volume de editais** | Setores de nicho ou UFs com pouca publicação podem ter <3 editais relevantes em 30 dias | Política de qualidade mínima (seção 3.1) |
| **CNPJ sem dados úteis** | MEIs novos, empresas sem histórico B2G, CNPJs com dados incompletos no OpenCNPJ | Preview gratuito revela se há dados suficientes ANTES da compra. Formato do `capital_social` é string com vírgula ("1232000,00"). |
| **PNCP API instável** | `tamanhoPagina` max = 50 (fev/2026), `codigoModalidadeContratacao` agora obrigatório, timeouts frequentes | Circuit breaker com fallback para cache SWR. Disclaimer no relatório se dados parciais. |
| **Dados com 86,4% de inconsistência** | TCU auditoria (2024) encontrou taxa crescente de inconsistências em registros PNCP | Cross-referência multi-fonte (PNCP + PCP v2) para validação |

**Fontes:**
- [TCU — Acórdão 934/2021 Plenário (PDFs escaneados)](https://licitacoesecontratos.tcu.gov.br/wp-content/uploads/sites/11/2024/09/Licitacoes-e-Contratos-Orientacoes-e-Jurisprudencia-do-TCU-5a-Edicao-29-08-2024.pdf)
- [Transparência Brasil — Qualidade de Dados PNCP (dez/2024)](https://www.transparencia.org.br/downloads/publicacoes/qualidade_dados_portal_nacional_de_contratacoes_publicas.pdf)
- [TCU — Implementação do PNCP Apresenta Falhas](https://portal.tcu.gov.br/imprensa/noticias/implementacao-do-portal-nacional-de-contratacoes-publicas-apresenta-falhas-no-cumprimento-da-nova-lei-de-licitacoes)

### 3.1 Política de Qualidade Mínima

**Definição de relatório "ruim":** Relatório com <3 editais relevantes E <2 insights acionáveis.

| Cenário | Ação |
|---------|------|
| 0 editais relevantes encontrados | Não gerar relatório. Devolver pagamento integral. Email explicativo: "Seu setor/UF não tem editais publicados nos últimos 30 dias." |
| 1-2 editais encontrados | Gerar com disclaimer: "Volume abaixo da média para seu setor. Considere expandir UFs ou período." Oferecer crédito de 50% para próximo relatório. |
| 3+ editais encontrados | Relatório padrão completo |
| Editais encontrados mas PDFs não processáveis (>50%) | Gerar com metadados + links. Disclaimer: "X de Y editais possuem documentos não processáveis automaticamente." |

### Custo de produção

| Componente | Custo por relatório | Fonte |
|------------|-------------------|-------|
| OpenAI GPT-4.1-nano (~5 chamadas) | R$0,50 | [OpenAI Pricing (mar/2026)](https://openai.com/pricing) |
| APIs PNCP + PCP v2 | R$0,00 | APIs públicas gratuitas |
| Infraestrutura Railway (compute) | R$0,20 | Estimativa pro-rata do plano atual |
| Stripe (3,99% + R$0,39) | R$4,26 | [Stripe Brasil Pricing](https://stripe.com/br/pricing) |
| **Tempo do founder (20-30 min)** | **R$33-50** | Valoração a R$100/h |
| **COGS total** | **~R$38-55** | |
| **Margem bruta** | **R$42-59 (43-61%)** | Incluindo tempo do founder |
| **Margem bruta (sem tempo)** | **R$92,04 (94,9%)** | Custo variável puro |

**Nota:** O tempo real por relatório é 20-30 minutos (não 15 como estimado na V1). Inclui: geração via `/report-b2g` (5-15 min) + revisão de qualidade (5-10 min) + envio e contextualização (5 min).

---

## 4. Análise de Mercado

### 4.1 Tamanho do Mercado (TAM)

| Métrica | Valor | Fonte |
|---------|-------|-------|
| Volume anual de compras públicas no Brasil | R$1,52 trilhão (~12% do PIB) | [Otmow — Compras Públicas Brasil (set/2025)](https://otmow.com/2025/09/05/o-mercado-de-compras-publicas-no-brasil-numeros-setores-e-oportunidades/) |
| Fornecedores registrados no SICAF (federal) | 452.500 | [e-Licitagov — Guia SICAF 2026](https://e-licitagov.com.br/informativos/o-que-e-sicaf-guia-definitivo-2026) |
| % micro e pequenas empresas (MPEs) | 67,7% (297.200 empresas) | [Agência Sebrae — Participação MPEs](https://agenciasebrae.com.br/economia-e-politica/participacao-das-mpe-nas-compras-publicas-cresceu-93-nos-ultimos-tres-anos/) |
| Crescimento MPEs em compras públicas (2018-2021) | +93% (R$21,3B → R$41B) | Agência Sebrae (ibid.) |
| Participação MPEs em processos homologados (2025) | 82%+ | [Effecti — Panorama Licitações 2026](https://effecti.com.br/panorama-das-licitacoes-e-tendencias-para-2026/) |
| Municípios no Brasil | 5.570 | IBGE |
| Municípios com estratégia digital | ~20% | [ME/CAF — Maturidade Digital dos Municípios (2022)](https://www.gov.br/economia/pt-br/assuntos/noticias/2022/agosto/estudo-apresenta-grau-de-maturidade-digital-dos-municipios-brasileiros) |

**TAM para relatórios avulsos (cenário conservador):**
- 1% de 452.500 fornecedores federais × 1 relatório/ano × R$97 = **R$4,4M/ano**
- SAM realista (primeiro ano): 200-500 relatórios = **R$19K-48K**

### 4.2 Cenário Competitivo

| Plataforma | Modelo | Relatório avulso? | Preço | Fonte |
|------------|--------|-------------------|-------|-------|
| Effecti | SaaS mensal | Não | Planos tiered | [effecti.com.br/plataforma](https://effecti.com.br/plataforma/) |
| ConLicitação | SaaS mensal | Não | Assinatura | [conlicitacao.com.br](https://conlicitacao.com.br/) |
| LicitaIA | SaaS + créditos | Não (créditos mensais) | Basic/PRO | [licitaia.app](https://www.licitaia.app/) |
| Wavecode | SaaS mensal | Não | Planos custom | [wavecode.com.br](https://www.wavecode.com.br/planos/) |
| **SmartLic Report** | **Avulso** | **SIM — R$97** | **R$97/unidade** | **Categoria nova** |

**Nota sobre o Effecti:** Possui [programa de parcerias aberto](https://www.effecti.com.br/parcerias/) com infra de revenda — benchmark para nosso programa.

### 4.3 Referências de Preço

| Produto | Preço | Tipo | Fonte |
|---------|-------|------|-------|
| Consultor de licitações (CLT) | ~R$3.000/mês + encargos | Profissional interno | [Triunfo Legis](https://www.triunfolegis.com.br/consultoria-licitacoes-preco) |
| Consultoria de licitações (PJ) | R$1.500-5.000/mês ou % do contrato | Serviço externo | [Effecti — Como Cobrar](https://effecti.com.br/como-cobrar-comissionamento-na-consultoria-de-licitacoes/) |
| **SmartLic Report** | **R$97** | **Inteligência personalizada** | **Proposta** |

O posicionamento a R$97 substitui 4-8h de trabalho de consultor. Preço psicológico padrão low-ticket brasileiro ([Estúdio Site](https://www.estudiosite.com.br/site/ead/low-ticket-infoproduto-27-a-97-em-alto-volume)).

---

## 5. Estratégia de Aquisição: Dois Canais

### DIFERENÇA CRÍTICA DA V1: Canal de parceria é o canal PRIMÁRIO, não um afterthought.

| Canal | Prioridade | CAC | Timeline |
|-------|-----------|-----|----------|
| **Parcerias (consultorias + escolas)** | P0 — começar imediatamente | R$0-29 (comissão) | Semana 1+ |
| **Google Ads Search** | P1 — após validar produto com parcerias | R$160-400 (estimativa) | Mês 2+ |
| **SEO + Conteúdo** | P2 — longo prazo | R$0 (tempo) | Mês 4+ |
| **Meta Ads Retargeting** | P3 — somente com base de visitantes | R$80-150 | Mês 3+ |

### 5.1 Canal Primário: Parcerias

**Por que parceria primeiro (não ads):**
- CAC zero ou comissão fixa (R$29 por venda = 30% de R$97)
- Leads pré-qualificados (alunos e clientes de consultorias JÁ querem licitar)
- Valida o produto com clientes reais antes de gastar com ads
- Partner-originated leads convertem 2x mais que cold leads e têm ciclo 46% mais curto ([WinningSales — Arquitetura de Receita B2B](https://winningsales.com.br/blog/arquitetura-de-receita/))

**Parceiros-alvo prioritários:**

| Parceiro | Perfil | Potencial | Abordagem |
|----------|--------|-----------|-----------|
| **Descomplicita** | Escola de licitações, cursos Lei 14.133 | Alto — alunos são ICP exato | Oferecer relatório como "ferramenta prática" pós-curso. Comissão 30%. |
| **Effecti** | Plataforma SaaS + programa de parcerias aberto | Médio — concorrente adjacente | Posicionar como complemento (eles monitoram, nós analisamos). Explorar programa existente. |
| **Consultorias regionais** (Eagle, Licijur, Route) | Consultorias PJ de licitações | Médio — clientes pagantes existentes | LinkedIn outreach. Comissão 30% ou desconto para clientes deles. |
| **LicitaBR** | Plataforma + consultoria | Médio | Co-marketing: "Relatório SmartLic para novos licitantes" |

**Programa de afiliados MVP (custo zero):**

```
Estrutura: "Parceiros SmartLic"
Comissão: 30% (R$29,10 por relatório vendido)
Tracking: Códigos de cupom únicos por parceiro no Stripe
Payout: Mensal via Pix (mínimo R$100)
Gestão: Planilha Google (até 20 parceiros)
Upgrade: Rewardful ($49/mo) quando >20 parceiros
```

**Fontes:**
- [Effecti — Programa de Parcerias](https://www.effecti.com.br/parcerias/)
- [Base Viral — CAC no Marketing de Indicação](https://baseviral.com.br/custo-de-aquisicao-de-clientes/)
- [SaaStisfeito — Ecossistema de Parcerias SaaS B2B](https://saastisfeito.com.br/ecossistema-de-parcerias/)
- [Rewardful — SaaS Affiliate Commission Benchmarks](https://www.rewardful.com/articles/saas-affiliate-program-benchmarks)

### 5.2 Canal Secundário: Google Ads Search

**Premissa corrigida:** Usar benchmarks reais do Brasil (Leadster Panorama 2025), não benchmarks americanos.

| Métrica | V1 (errado) | V2 (corrigido) | Fonte real |
|---------|-------------|-----------------|------------|
| Conversão landing → lead | 25% | **2,5%** (mediana B2B Brasil) | [Leadster Panorama 2025](https://leadster.com.br/blog/panorama-geracao-de-leads-2025/) |
| CPC B2B Brasil | R$4 | **R$3-8** (range real) | [Wayno — Quanto Custa Google Ads](https://blog.wayno.in/quanto-custa-google-ads-por-mes-tabela-completa/), [Statista](https://www.statista.com/statistics/1115426/brazil-search-advertising-cpc/) |
| CTR B2B | 3,5% | **Sem dado Brasil** (proxy US: ~4%) | Nenhuma fonte brasileira verificável |
| Conversão preview → compra | 30% | **10-15%** (estimativa conservadora) | Sem benchmark verificável — número de validação |
| CAC resultante | R$53 | **R$160-400** | Cálculo abaixo |

**Cálculo CAC honesto (cenário base):**

```
CPC médio: R$5,00 (keywords "licitações [setor] [UF]")
Conversão landing → lead: 2,5% (Leadster 2025 — mediana B2B Brasil)
Conversão lead → preview enviado: 90% (automático, 10% bounce de email)
Conversão preview → compra: 12% (estimativa — NÚMERO DE VALIDAÇÃO)

Cliques para 1 lead: 40 (1/0.025)
Leads para 1 venda: 9,3 (1/(0.90 × 0.12))
Cliques para 1 venda: 370
CAC: R$1.851 ← INVIÁVEL com ads diretos

---

COM LANDING PAGE OTIMIZADA (meta 5% conversão — top quartile Leadster):
Cliques para 1 lead: 20
Leads para 1 venda: 9,3
Cliques para 1 venda: 186
CAC: R$930 ← AINDA INVIÁVEL

---

COM PREVIEW CONVERTENDO 25% (meta otimista):
Cliques para 1 lead: 20 (5% landing)
Leads para 1 venda: 4,4 (1/(0.90 × 0.25))
Cliques para 1 venda: 89
CAC: R$445 ← PREJUÍZO em ads, mas positivo com LTV

---

COM LANDING DE ALTA CONVERSÃO (8%) + PREVIEW 25%:
Cliques para 1 lead: 12,5
Leads para 1 venda: 4,4
Cliques para 1 venda: 55
CAC: R$277 ← BREAKEVEN considerando LTV
```

**Conclusão brutal:** Google Ads como canal isolado provavelmente tem CAC > R$97 no mês 1. Funciona APENAS se:
1. A landing page converte >5% (top quartile Brasil)
2. O preview converte >20% (validação necessária)
3. O LTV compensa o CAC via recompra e upsell

**Por isso parcerias são P0 e ads são P1.** Validar o funil (preview → compra) com leads de parceria antes de investir em ads.

### 5.3 Estrutura de Campanhas Google Ads (quando ativar)

**Orçamento inicial:** R$30/dia (R$660/mês) — NÃO R$50/dia como V1.

**Campanha 1 — Long-tail setorial (70% do budget)**
- Keywords: "licitações construção civil SC", "editais obras públicas MG"
- Match type: Exact e Phrase
- Negativar: "concurso", "emprego", "estágio", "resultado", "como fazer", "grátis"
- CPC esperado: R$2-5 (baixa competição em long-tail)

**Campanha 2 — Educacional (30% do budget)**
- Keywords: "como participar de licitação", "documentos para licitação"
- Objetivo: Gerar leads para preview (topo de funil)
- CPC esperado: R$1,50-3

**Stop-loss rígido:** Se após 200 cliques (R$600-1.000) e 0 vendas, pausar e diagnosticar. Não "otimizar" — o funil está quebrado.

### 5.4 Plano B/C/D (se Google Ads não performar)

| Cenário | Sinal | Ação |
|---------|-------|------|
| **CAC > R$200 após 30 dias** | Ads queimando dinheiro | Pausar ads. Dobrar em parcerias. Testar LinkedIn orgânico. |
| **CAC R$100-200** | Marginal | Otimizar landing page (A/B test). Melhorar preview. Adicionar retargeting Meta. |
| **CAC < R$100** | Funcionando | Escalar budget gradualmente (R$50 → R$75/dia). |
| **Google Ads desaprovado** | Policy violation | Migrar para LinkedIn Ads (CPC mais alto mas sem restrições de "oportunidades"). Foco em conteúdo orgânico. |
| **Nenhum canal pago funciona** | Todos inviáveis | Pivotar para 100% parceria + conteúdo. Relatório vira ferramenta de demonstração para vender consultoria. |

**Canais alternativos em ordem de prioridade:**

1. **LinkedIn orgânico** — Posts sobre licitações, artigos educativos, comentários em grupos. R$0. Lento mas cumulativo.
2. **Meta Ads retargeting** — Somente para quem já visitou o site ou recebeu preview. CPC menor para audiência quente.
3. **SEO/Blog** — Artigos sobre "como participar de licitação em [setor]". Resultado em 3-6 meses. Investimento de tempo.
4. **Programa de indicação** — Cliente que comprou indica empresa do mesmo setor. Relatório grátis por indicação que compra.
5. **WhatsApp broadcast** — Para base de leads existente (Zambeline, Gamarra, GJS, Líder Obras). Custo zero.

---

## 6. Funil de Conversão (Revisado)

### 6.1 Funil via Parceria (Canal Primário)

```
Parceiro indica lead (WhatsApp/email)
    ↓
Lead preenche formulário simplificado (CNPJ + email + WhatsApp)
    ↓ 100% → Preview automático enviado via Resend (seção 6.3)
Preview gratuito (1 página)
    ↓ Meta: 20-30% convertem para compra
Stripe Payment Link R$97
    ↓ Webhook → confirmação automática + notificação ao founder
Geração do relatório (manual, 20-30 min)
    ↓ Entrega via email + WhatsApp
Follow-up (dia 2, 7, 14, 25) → recompra ou upsell
```

### 6.2 Funil via Ads (Canal Secundário)

```
Google Ads (R$30/dia)
    ↓ CPC R$3-5 = 6-10 cliques/dia
Landing page /relatorio
    ↓ Meta: 5%+ preenchem formulário
    = 0,3-0,5 leads/dia (6-10/mês)
Preview gratuito por email (automático)
    ↓ Meta: 20% convertem
    = 1-2 vendas/mês via ads no mês 1
Stripe Checkout R$97
    ↓
Entrega manual (20-30 min)
    ↓
Follow-up de recompra + upsell
```

### 6.3 O Preview Automático — Escopo Real de Implementação

**A V1 estimou "1-2h" para o preview. Estimativa real: 2-3 dias de desenvolvimento.**

O preview é um mini-produto que requer:

| Componente | Descrição | Tempo estimado | Status |
|------------|-----------|----------------|--------|
| Formulário web (`/relatorio`) | CNPJ + email + WhatsApp + setor + UFs | 4-6h | A construir |
| Integração OpenCNPJ | Busca dados da empresa (razão social, CNAE, porte) | 2-3h | Já existe no backend |
| Scan PNCP automatizado | Busca editais relevantes (últimos 30 dias) | 2-3h | Já existe (`/report-b2g`) |
| Template HTML de preview | 1 página: perfil + 3 editais + CTA | 3-4h | A construir |
| Envio via Resend | Automático, triggered por form submission | 1-2h | Infra já existe |
| Rate limiting + anti-abuse | Evitar uso do preview como ferramenta gratuita ilimitada | 2-3h | A construir |
| **Total** | | **~16-24h (2-3 dias)** | |

**Conteúdo do preview (1 página):**
- Nome da empresa + CNPJ + setor identificado
- "Encontramos X editais abertos relevantes para seu perfil"
- Tabela com 3 editais: objeto (resumido), órgão, valor, data abertura
- SEM análise documental, SEM recomendação, SEM inteligência competitiva
- CTA: "Relatório completo com análise de cada edital → R$97"

**Limitação de preview:** Máximo 2 previews por CNPJ/email a cada 30 dias. Evita que lead use preview como serviço gratuito.

### 6.4 Fluxo Pós-Pagamento (Detalhado)

**A V1 não especificava o que acontece após o pagamento. Aqui está o fluxo completo:**

```
Cliente paga R$97 via Stripe Payment Link
    |
    ├─ Stripe envia email de confirmação automático (nativo)
    ├─ Stripe push notification no app mobile do founder
    |
    ├─ Webhook checkout.session.completed ──→ backend
    │   ├─ Grava pedido em Supabase (report_orders)
    │   ├─ Envia email ao CLIENTE via Resend:
    │   │   "Obrigado! Seu relatório será entregue em até 24h."
    │   └─ Envia email ao FOUNDER via Resend:
    │       "NOVO PEDIDO R$97 - {nome} - {CNPJ}"
    |
    ├─ FOUNDER (manual):
    │   ├─ Gera relatório via /report-b2g (~15 min)
    │   ├─ Revisa qualidade (~5-10 min)
    │   ├─ Envia relatório via email + WhatsApp
    │   └─ Marca pedido como "fulfilled" em Supabase
    |
    └─ Automação pós-entrega (email sequence):
        ├─ Dia 2: WhatsApp "Viu as oportunidades?"
        ├─ Dia 7: Email com case de uso
        ├─ Dia 14: "Novas licitações desde seu relatório"
        └─ Dia 25: "Seu próximo relatório está disponível"
```

**Infra existente no codebase:**
- `backend/webhooks/stripe.py` — handler de webhooks com idempotência e verificação de assinatura
- `backend/email_service.py` — Resend com retry (3 tentativas, backoff exponencial)
- `backend/services/billing.py` — lógica de billing

**Novo a construir:**
- Tabela `report_orders` em Supabase (4-6h)
- Branch no webhook handler para produto "relatório avulso" (2-4h)
- Template de email de confirmação (1-2h)
- **Total: ~1-2 dias de desenvolvimento**

**Fontes:**
- [Stripe — Fulfill Orders After Checkout](https://docs.stripe.com/checkout/fulfillment)
- [Stripe — Payment Links Post-Payment](https://docs.stripe.com/payment-links/post-payment)

### 6.5 Handling Off-Hours (Leads Fora do Horário Comercial)

| Evento | Horário comercial (8h-18h) | Fora do horário |
|--------|---------------------------|-----------------|
| Form preenchido | Preview enviado em <5 min (automático) | Preview enviado em <5 min (automático) — **sem diferença** |
| Pagamento R$97 | Relatório entregue em 4-12h | Relatório entregue na manhã seguinte (até 24h). Email de confirmação automático garante expectativa. |
| Dúvida via WhatsApp | Resposta em <2h | Auto-reply WhatsApp Business: "Recebemos sua mensagem! Responderemos em até 12h." Resposta na manhã seguinte. |

**SLA de entrega:**
- Preview: <5 min (automático, 24/7)
- Relatório: até 24h úteis após pagamento
- Suporte WhatsApp: até 12h em horário comercial

---

## 7. Projeções Financeiras (Revisadas)

### 7.1 Unit Economics por Relatório

```
RECEITA
  Preço de venda:                     R$ 97,00

CUSTOS VARIÁVEIS
  Stripe (3,99% + R$0,39):           -R$ 4,26
  OpenAI GPT-4.1-nano (~5 calls):    -R$ 0,50
  PNCP/PCP APIs:                     -R$ 0,00
  Railway compute (pro-rata):        -R$ 0,20
  Total custos variáveis:            -R$ 4,96

MARGEM DE CONTRIBUIÇÃO:               R$ 92,04 (94,9%)

CUSTO DE AQUISIÇÃO (por canal)
  Parceria (comissão 30%):             R$ 29    → Margem R$63 (65%)
  Google Ads (cenário otimista):       R$ 277   → PREJUÍZO unitário
  Google Ads (cenário realista):       R$ 445   → PREJUÍZO unitário
  Orgânico (indicação/SEO):            R$ 0     → Margem R$92 (95%)

CUSTO DO TEMPO DO FOUNDER
  25 min/relatório × R$100/h:         R$ 41,67
  Margem líquida (via parceria):      R$ 21,37/relatório
  Margem líquida (via orgânico):      R$ 50,37/relatório
```

**Implicação:** Google Ads isoladamente é deficitário para este produto. O canal de parceria e indicação é o que viabiliza a unidade econômica. Ads podem funcionar como acelerador se o LTV (recompra + upsell) compensar o CAC alto.

### 7.2 Projeção de Receita Mensal (Revisada — Founder Solo com CLT)

| Métrica | Mês 1-2 | Mês 3-4 | Mês 6 | Mês 12 |
|---------|---------|---------|-------|--------|
| **Canal parceria** | | | | |
| Parceiros ativos | 2-3 | 5-8 | 10-15 | 20+ |
| Vendas via parceria/mês | 3-5 | 8-12 | 15-25 | 30-50 |
| Receita parceria (líq. de comissão) | R$200-340 | R$540-810 | R$1.000-1.700 | R$2.000-3.400 |
| **Canal ads** (se ativado mês 2+) | | | | |
| Gasto ads/mês | R$0 | R$660 | R$1.100 | R$1.500 |
| Vendas via ads/mês | 0 | 1-3 | 3-6 | 5-10 |
| Receita ads (líq. de CAC) | R$0 | R$97-291 | R$291-582 | R$485-970 |
| **Canal orgânico** | | | | |
| Vendas orgânicas/mês | 0-1 | 1-2 | 3-5 | 8-15 |
| Receita orgânica | R$0-97 | R$97-194 | R$291-485 | R$776-1.455 |
| **Totais** | | | | |
| **Relatórios/mês** | **3-6** | **10-17** | **21-36** | **43-75** |
| **Receita bruta/mês** | **R$291-582** | **R$970-1.650** | **R$2.037-3.492** | **R$4.171-7.275** |
| **Lucro operacional** | -R$100 a R$200 | R$200-800 | R$500-1.500 | R$1.500-4.000 |

**Premissas:**
- Founder produz max 5 relatórios/semana nos meses 1-4
- A partir do mês 5, contrata VA part-time (R$800-1.200/mês) para relatórios simples
- CAC via ads decresce com otimização (learning period Google: 2-4 semanas)
- Recompra de 10-15% dos compradores no mês seguinte
- Upsell não incluído (seção 11 separada)
- 22 dias úteis/mês

### 7.3 Cenário de Break-Even

| Item | Custo mensal fixo |
|------|-------------------|
| Railway (backend + frontend) | R$100 |
| Supabase (free tier) | R$0 |
| Stripe (apenas variável) | — |
| Google Ads (se ativo) | R$660 |
| Rewardful (se >20 parceiros) | R$250 |
| **Total fixo (sem ads)** | **~R$100** |
| **Total fixo (com ads)** | **~R$960** |

**Break-even sem ads:** 2 relatórios/mês (R$194 receita bruta)
**Break-even com ads:** ~15 relatórios/mês (R$1.455 receita bruta)

### 7.4 Lifetime Value (LTV) — Revisado

| Componente | Conversão | Receita | LTV Ponderado |
|------------|-----------|---------|---------------|
| Relatório inicial | 100% | R$97 | R$97,00 |
| Segundo relatório (60 dias) | 10-15% | R$97 | R$9,70-14,55 |
| Terceiro relatório (90 dias) | 5-8% | R$97 | R$4,85-7,76 |
| Upgrade consultoria mensal (seção 11) | 3-5% | R$4.800 (R$800/mês × 6 meses) | R$144-240 |

| Cenário | LTV Total | CAC (parceria) | LTV:CAC |
|---------|-----------|----------------|---------|
| Conservador | R$156 | R$29 | **5,4x** |
| Base | R$256 | R$29 | **8,8x** |
| Otimista | R$359 | R$29 | **12,4x** |

**Referência:** LTV:CAC saudável >3x ([For Entrepreneurs — SaaS Metrics 2.0](https://www.forentrepreneurs.com/saas-metrics-2/)).

**NOTA IMPORTANTE:** Estes números de recompra e upsell são ESTIMATIVAS a serem validadas. Não existe benchmark verificável para recompra de relatórios B2G avulsos no Brasil. Tratar como hipóteses, não fatos.

---

## 8. Playbook de Execução (Revisado)

### Fase 0 — LGPD e Compliance (Dias 0-3) — **BLOQUEANTE**

| Ação | Tempo | Status |
|------|-------|--------|
| Revisar e atualizar `/privacidade` com requisitos LGPD (seção 12) | 3-4h | Página existe, conteúdo a revisar |
| Revisar `/termos` com cláusulas de tratamento de dados | 2-3h | Página existe, conteúdo a revisar |
| Designar DPO/Encarregado e publicar contato no site (Art. 41) | 1h | **FALTANDO** |
| Implementar checkbox de consentimento nos formulários (Art. 8) | 1-2h | A verificar |
| **Total** | **~8-10h** | |

### Fase 1 — Setup de Produto (Dias 3-10)

| Ação | Tempo | Prioridade |
|------|-------|-----------|
| Stripe Payment Link (produto "Relatório Executivo B2G" R$97) | 30 min | P0 |
| Webhook handler para `checkout.session.completed` + notificação | 4-6h | P0 |
| Tabela `report_orders` em Supabase | 2-3h | P0 |
| Template de preview (1 página) no Resend | 3-4h | P0 |
| Formulário em `/relatorio` (CNPJ + email + WhatsApp + setor + UFs) | 4-6h | P0 |
| Integração formulário → OpenCNPJ → PNCP scan → preview | 4-6h | P0 |
| Relatório exemplo anonimizado para landing page | 1h | P0 |
| Auto-reply WhatsApp Business (horário e fora do horário) | 30 min | P1 |
| **Total** | **~20-28h (3-4 dias de trabalho)** | |

### Fase 2 — Ativação de Parcerias (Dias 10-30)

| Ação | Tempo |
|------|-------|
| Contatar Descomplicita — propor parceria com comissão 30% | 1h |
| Criar 3 relatórios gratuitos para beta testers — coletar depoimentos | 6-9h |
| Montar página `/parceiros` (simples, com link de cadastro) | 2-3h |
| Contatar 10 consultorias de licitações via LinkedIn | 2-3h |
| Configurar códigos de cupom Stripe por parceiro | 1h |
| Gerar e entregar primeiros relatórios pagos | Ongoing |
| Coletar NPS e feedback por WhatsApp após cada entrega | 5 min/entrega |

**Stop-loss parcerias:** Se após 30 dias e 5+ parceiros ativos, 0 vendas, investigar: o preview não converte? O parceiro não divulga? O produto não tem fit?

### Fase 3 — Ativação de Ads (Dias 30-60)

- Ligar Google Ads com R$30/dia (somente se Fase 2 validou preview → compra >15%)
- Campanha long-tail setorial (70%) + educacional (30%)
- Monitorar diariamente: CPC, CTR, leads, conversão preview → compra
- **Stop-loss ads:** Se CAC > R$200 após 200 cliques, pausar e revisar landing/preview

### Fase 4 — Escala e Delegação (Dias 60-120)

- Se >15 relatórios/mês: contratar VA part-time (R$800-1.200/mês) via Workana/99Freelas
- VA treina em: revisão de relatório, envio via email, follow-up templates WhatsApp
- Founder foca em: geração do relatório, decisões estratégicas, parcerias
- Testar pacote "3 relatórios por R$249" (R$83/un)
- Adicionar Meta retargeting para leads que receberam preview mas não compraram

**Custo VA part-time (10h/semana):**
| Task | Horas/semana | Custo/mês |
|------|-------------|-----------|
| Revisão de relatórios simples | 4h | R$320-480 |
| Envio + follow-up WhatsApp | 3h | R$240-360 |
| Admin (planilha, organização) | 3h | R$240-360 |
| **Total** | **10h** | **R$800-1.200** |

**Fontes VA:**
- [SalaryExpert — VA Salary Brazil 2025](https://www.salaryexpert.com/salary/job/virtual-assistant/brazil)
- [Workana — Virtual Assistants Brazil](https://www.workana.com/en/freelancers/brazil/virtual-assistant)
- [MeuTudo — Quanto Ganha Freelancer 2026](https://meutudo.com.br/blog/quanto-ganha-um-freelancer-por-dia-e-hora/)

---

## 9. Estratégia de Retenção e Recompra (Seção Nova)

### 9.1 Email Sequence Pós-Compra

| Dia | Canal | Conteúdo | Objetivo |
|-----|-------|----------|----------|
| 0 | Email | Entrega do relatório + "Como usar em 5 minutos" | Ativação |
| 2 | WhatsApp | "Viu as oportunidades do relatório? Alguma dúvida?" | Engajamento |
| 7 | Email | Mini case: "Empresa do setor X usou para..." | Social proof |
| 14 | Email | "X novas licitações desde seu relatório" (teaser) | Urgência |
| 21 | WhatsApp | Áudio curto: "Vi licitação em [UF] que pode te interessar" | Personalização |
| 25 | Email | "Seu próximo relatório está disponível" + link Stripe | Recompra |
| 30 | Email | "Última chance: oportunidades fecham esta semana" | FOMO |

**80% das vendas B2B acontecem após o 5º contato.** A maioria dos vendedores desiste após 2. ([Ploomes — Prospecção Multicanal](https://blog.ploomes.com/prospeccao-multicanal/))

### 9.2 Triggers de Recompra

| Trigger | Ação |
|---------|------|
| Lead não abriu email de entrega em 48h | WhatsApp: "Seu relatório está esperando por você" |
| 30 dias desde último relatório | Email automático: "Novas oportunidades no seu setor" |
| Lead respondeu positivamente ao preview mas não comprou | WhatsApp pessoal (founder) |
| Cliente comprou 2+ relatórios | Oferecer pacote trimestral com desconto |

### 9.3 Expansão de Valor por Relatório

Cada relatório subsequente deve referenciar o anterior: "Comparado ao seu relatório de fevereiro, surgiram 8 novos editais no seu setor." Isso cria uma série temporal que torna cada relatório mais valioso.

---

## 10. Prova Social (Seção Nova)

### 10.1 Estratégia para Produto com Zero Reviews

**Semana 1-2 (credibilidade técnica):**
- "Analisa dados de 1.400+ portais de compras públicas"
- "3 fontes oficiais integradas: PNCP, PCP, ComprasGov"
- "Dados oficiais do Portal Nacional de Contratações Públicas"
- Mostrar relatório exemplo anonimizado na landing page

**Mês 1 (beta testers):**
- Oferecer 5-10 relatórios gratuitos para empresas do setor 1 (Engenharia) em troca de depoimento de 2 frases + permissão de uso do nome da empresa
- Framework: "A empresa X do setor Y descobriu Z oportunidades que não sabia existir"

**Mês 2+ (proof progressivo):**
- Agregar dados: "Nossos relatórios já identificaram R$X milhões em oportunidades"
- Video depoimentos (1 relatório grátis em troca de vídeo de 60s)
- Seção "Usado por empresas de [setor]" com logos reais

**Regra:** Nunca fabricar depoimentos. Um depoimento real e imperfeito vale mais que dez polidos e falsos.

---

## 11. Produto de Upsell: Consultoria Mensal (Seção Nova — Definição Clara)

### O que é

| Aspecto | Relatório Avulso (R$97) | Consultoria Mensal (R$800/mês) |
|---------|------------------------|-------------------------------|
| **Frequência** | Sob demanda | 1 relatório/mês + monitoramento contínuo |
| **Varredura** | Últimos 30 dias, 1x | Contínua, alertas em tempo real |
| **Análise documental** | Editais encontrados no momento | Novos editais analisados conforme publicação |
| **Suporte** | Email de entrega + 1 follow-up | WhatsApp dedicado + call mensal de 30 min |
| **Estratégia** | Recomendação por edital | Planejamento trimestral de participação |
| **Inteligência competitiva** | Snapshot do momento | Tracking contínuo de concorrentes |
| **SLA** | Até 24h | Até 4h para alertas críticos |

### Pricing

- R$800/mês (mensal) — reduzido de R$1.500 da V1 para aumentar conversão
- R$680/mês (semestral, 15% off)
- R$560/mês (anual, 30% off)

### Quando oferecer

- Follow-up dia 7 após entrega do relatório
- Após 2ª compra de relatório pelo mesmo CNPJ
- Quando cliente pergunta "vocês fazem isso todo mês?"

### Meta de conversão

- 3-5% dos compradores de relatório avulso → consultoria mensal
- Objetivo: 2-5 clientes de consultoria no primeiro semestre
- Receita recorrente mensal: R$1.600-4.000 (MRR)

---

## 12. Compliance LGPD (Seção Nova — Obrigatória)

### 12.1 Dados Coletados e Base Legal

| Dado | Classificação LGPD | Base legal | Artigo |
|------|--------------------|-----------|----|
| CNPJ (PJ normal) | Não é dado pessoal | N/A | — |
| CNPJ (MEI/EI) | **Dado pessoal** (identifica pessoa natural) | Legítimo interesse | Art. 7 IX, Art. 10 |
| Email | Dado pessoal | Consentimento explícito | Art. 7 I, Art. 8 |
| WhatsApp (telefone) | Dado pessoal | Consentimento explícito | Art. 7 I, Art. 8 |
| Dados PNCP/PCP (editais) | Dados públicos governamentais | Art. 7 §3 (dados de acesso público) | Art. 7 §3 |
| Dados OpenCNPJ (razão social, CNAE) | Dados públicos | Art. 7 §3 | Art. 7 §3 |
| QSA/sócios (nomes, CPFs) | **Dado pessoal** | Legítimo interesse + LIA | Art. 7 IX, Art. 10 |
| CEIS/CNEP/CEPIM (sanções) | Dados públicos | Art. 7 §3 (finalidade pública) | Art. 7 §3 |

### 12.2 Requisitos Imediatos (Bloqueantes para Lançamento)

| Requisito | Artigo LGPD | Ação |
|-----------|-------------|------|
| **Política de Privacidade** atualizada | Art. 9, Art. 6 VI | Revisar `/privacidade` com: tipos de dados, finalidades, base legal, compartilhamento (OpenAI US, Stripe US, Supabase US), DPO |
| **DPO/Encarregado** designado e publicado | Art. 41 | Founder como DPO + email `dpo@confenge.com.br` no rodapé do site |
| **Consentimento explícito** no formulário | Art. 8 | Checkbox NÃO pré-marcado: "Aceito receber comunicações sobre oportunidades de licitação e novidades do SmartLic" |
| **Opt-in separado** para WhatsApp | Art. 8 §4 | Checkbox dedicado: "Aceito receber mensagens via WhatsApp" |
| **Unsubscribe** em todos os emails marketing | Art. 8 §5 | Link de descadastro no rodapé (Resend suporta nativamente) |
| **Log de consentimento** | Art. 8 §2 | Gravar: timestamp, IP, texto consentido, checkbox marcado |

### 12.3 Requisitos de 30 Dias

| Requisito | Artigo |
|-----------|--------|
| ROPA (Registro de Operações de Tratamento) | Art. 37 |
| LIA (Legitimate Interest Assessment) para uso de dados PNCP/OpenCNPJ | Art. 10 |
| Documentação de transferência internacional (Supabase US, OpenAI US, Stripe US) | Art. 33-36 |
| Política de retenção de dados (por quanto tempo guardamos cada tipo) | Art. 16 |
| Cookie consent banner (se usar analytics) | Art. 7 I |

### 12.4 Riscos Regulatórios

**ANPD (Autoridade Nacional de Proteção de Dados):**
- Primeira multa aplicada em 2023: R$14.400 para empresa que usou listas de WhatsApp sem base legal ([ANPD — Primeira Multa](https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-aplica-a-primeira-multa-por-descumprimento-a-lgpd))
- Em 2025, ANPD virou autarquia independente com poderes ampliados e 200 novos servidores
- Em 2026, fase de "fiscalização ativa" — não mais orientativa ([TI Inside — Nova Fase Cibersegurança 2026](https://tiinside.com.br/02/03/2026/a-nova-fase-da-ciberseguranca-em-2026-da-orientacao-a-fiscalizacao-ativa/))
- Sanções vão além de multa: bloqueio de dados, suspensão de tratamento, publicização da infração ([Art. 52 LGPD](https://lgpd-brasil.info/capitulo_08/artigo_52))

**Google Ads:**
- SmartLic Report **não se enquadra como serviço financeiro** — é ferramenta de inteligência empresarial
- Verificação financeira (obrigatória desde ago/2022 no Brasil) **não se aplica** ([Google — Financial Services Verification Brazil](https://support.google.com/adspolicy/answer/15332527))
- **Risco real:** claims como "encontre contratos de milhões" ou "ganhe licitações" podem ser enquadrados como "misrepresentation" ([Google — Misrepresentation Policy](https://support.google.com/adspolicy/answer/6020955))
- **Copy seguro:** "descubra editais", "monitore licitações", "análise de oportunidades" — factual, sem promessa de resultado

**Fontes adicionais:**
- [Sebrae — LGPD Coleta Segura](https://sebrae.com.br/sites/PortalSebrae/artigos/lgpd-aprenda-a-realizar-a-coleta-de-dados-de-forma-segura-e-legal)
- [LGPD para SaaS — Iugu](https://www.iugu.com/blog/lgpd-para-saas)
- [Art. 7 LGPD — Hipóteses de Tratamento](https://lgpd-brasil.info/capitulo_02/artigo_07)
- [ANPD — Guia Orientativo Legítimo Interesse](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia_orientativo_hipoteses_legais_tratamento_de_dados_pessoais_legitimo_interesse)

---

## 13. Setores Prioritários

Começar com setores onde o report-b2g gera mais valor (editais complexos, PDFs densos, valores altos):

| Prioridade | Setor | Qualidade do relatório | Justificativa |
|-----------|-------|----------------------|---------------|
| 1 | Engenharia, Projetos e Obras | Excelente (PDFs longos, requisitos técnicos) | ~35% do mercado B2G, editais complexos = alto valor percebido |
| 2 | Tecnologia e Sistemas | Muito boa (empresas digitais convertem melhor online) | ~15% do mercado, público receptivo a compra online |

**Recomendação:** Começar APENAS com setores 1-2 nas primeiras 8 semanas. Expandir conforme valida conversão.

---

## 14. Métricas de Acompanhamento

| Métrica | Meta Mês 1 | Meta Mês 3 | Meta Mês 6 | Frequência |
|---------|-----------|-----------|-----------|-----------|
| Relatórios vendidos/semana | 1-2 | 3-5 | 8-12 | Semanal |
| Conversão preview → compra | > 15% | > 20% | > 25% | Semanal |
| CAC médio (blended) | < R$50 | < R$40 | < R$30 | Mensal |
| Tempo form → entrega preview | < 5 min | < 5 min | < 5 min | Automático |
| Tempo pagamento → entrega relatório | < 24h | < 12h | < 6h | Por venda |
| NPS do relatório | > 7 | > 8 | > 9 | Por venda (48h) |
| Taxa de recompra (60 dias) | > 5% | > 10% | > 15% | Mensal |
| Parceiros ativos | 3+ | 8+ | 15+ | Mensal |
| Upsell para consultoria mensal | 0 | 1-2 | 3-5 | Mensal |
| ROAS (canal ads, se ativo) | > 0,5x | > 1,5x | > 3x | Semanal |

---

## 15. Riscos e Mitigações (Atualizado)

| Risco | Prob. | Impacto | Mitigação |
|-------|-------|---------|-----------|
| **CAC via ads > ticket (R$97)** | **Alta** | Alto | Canal de parceria como P0. Ads somente após validar funil. Stop-loss R$200 CAC. |
| **Gargalo de capacidade founder** | Alta (mês 3+) | Alto | VA part-time (R$800-1.200/mês) a partir de 15 relatórios/mês. |
| **PDFs não processáveis** | Média-Alta | Médio | OCR fallback + disclaimer honesto no relatório + política de reembolso (seção 3.1) |
| **Relatório "ruim" (poucos editais)** | Média | Alto | Política de qualidade mínima. Preview gratuito filtra leads de setores com baixo volume. |
| **PNCP/PCP instável** | Média | Médio | Cache SWR + multi-fonte. Disclaimer + atualização gratuita quando normalizar. |
| **LGPD non-compliance** | Média | **Crítico** | Fase 0 bloqueante. DPO designado. Consentimento explícito. Log de tratamento. |
| **Concorrente copia modelo avulso** | Baixa (3-6m) | Médio | First-mover + qualidade documental + rede de parcerias. |
| **Google Ads desaprovação** | Baixa | Alto | Copy factual. Backup: LinkedIn Ads, conteúdo orgânico. |
| **CNPJ sem dados no OpenCNPJ** | Média | Baixo | Preview revela ausência de dados ANTES do pagamento. |
| **Burnout do founder** | Média (mês 4+) | **Crítico** | Limite rígido de 20 relatórios/mês. Contratar VA antes de atingir limite. Não aceitar mais pedidos do que pode entregar. |

---

## 16. Anti-Patterns — O que NÃO fazer

1. **NÃO investir em Google Ads antes de validar funil via parcerias** — CAC provavelmente inviável sem otimização
2. **NÃO prometer "10 relatórios/dia"** — Capacidade real de founder solo com CLT: 3-5/semana
3. **NÃO automatizar entrega antes de 30 vendas** — Cada relatório manual é iteração de produto + conversa com cliente
4. **NÃO lançar sem compliance LGPD** — ANPD está em fase de fiscalização ativa desde 2025
5. **NÃO usar benchmarks americanos para CAC** — Brasil B2B converte 2,5% (não 25%)
6. **NÃO ignorar o canal Descomplicita** — Parceria aquecida com CAC zero é mais valiosa que qualquer ad
7. **NÃO construir checkout integrado no SmartLic agora** — Stripe Payment Link resolve em 30 min
8. **NÃO aceitar mais pedidos do que pode entregar** — SLA de 24h é compromisso. Acima da capacidade, adicionar VA ou pausar aquisição.
9. **NÃO enviar emails marketing sem consentimento explícito** — ANPD multou empresa por WhatsApp sem base legal
10. **NÃO tratar "Conselho de CMOs" ou output de IA como fonte de autoridade** — Toda projeção deve citar fonte verificável ou ser marcada como "hipótese a validar"

---

## 17. Fontes Consolidadas

### Mercado e TAM
- [Otmow — O Mercado de Compras Públicas no Brasil (set/2025)](https://otmow.com/2025/09/05/o-mercado-de-compras-publicas-no-brasil-numeros-setores-e-oportunidades/)
- [Effecti — Panorama das Licitações 2026](https://effecti.com.br/panorama-das-licitacoes-e-tendencias-para-2026/)
- [Agência Sebrae — Participação MPEs nas Compras Públicas](https://agenciasebrae.com.br/economia-e-politica/participacao-das-mpe-nas-compras-publicas-cresceu-93-nos-ultimos-tres-anos/)
- [e-Licitagov — Guia SICAF 2026](https://e-licitagov.com.br/informativos/o-que-e-sicaf-guia-definitivo-2026)

### Conversão (Benchmarks Brasil)
- [Leadster — Panorama Geração de Leads 2025](https://leadster.com.br/blog/panorama-geracao-de-leads-2025/) — **Fonte primária: 2.861 sites, 167M acessos, 3.7M leads**
- [Leadster — Taxa de Conversão por Segmento 2025](https://leadster.com.br/blog/taxa-de-conversao-por-segmento/)
- [SEOLab — Taxa de Conversão no Brasil 2025](https://seolab.com.br/taxa-de-conversao-no-brasil-em-2025-o-que-esta-acontecendo-com-os-leads/)

### Google Ads
- [Wayno — Quanto Custa Google Ads por Mês (tabela completa)](https://blog.wayno.in/quanto-custa-google-ads-por-mes-tabela-completa/)
- [Statista — Brazil Google Ads CPC by Industry 2023](https://www.statista.com/statistics/1115426/brazil-search-advertising-cpc/)
- [WordStream — Average CPC by Country](https://www.wordstream.com/blog/average-cost-per-click)
- Google Keyword Planner (dados requerem conta ativa)

### LGPD
- [Lei 13.709/2018 (LGPD) — Texto Oficial](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/L13709compilado.htm)
- [ANPD — Guia Orientativo Legítimo Interesse (nov/2024)](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia_orientativo_hipoteses_legais_tratamento_de_dados_pessoais_legitimo_interesse)
- [ANPD — Primeira Multa (2023)](https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-aplica-a-primeira-multa-por-descumprimento-a-lgpd)
- [TI Inside — Nova Fase Cibersegurança 2026](https://tiinside.com.br/02/03/2026/a-nova-fase-da-ciberseguranca-em-2026-da-orientacao-a-fiscalizacao-ativa/)
- [Sebrae — LGPD Coleta Segura](https://sebrae.com.br/sites/PortalSebrae/artigos/lgpd-aprenda-a-realizar-a-coleta-de-dados-de-forma-segura-e-legal)
- [Iugu — LGPD para SaaS](https://www.iugu.com/blog/lgpd-para-saas)

### PNCP e Qualidade de Dados
- [Transparência Brasil — API & Acesso aos Dados PNCP (jun/2024)](https://www.transparencia.org.br/downloads/publicacoes/portalnacionaldecontratacoespublicas_recomendacoesedesafiostecnicos.pdf)
- [Transparência Brasil — Qualidade de Dados PNCP (dez/2024)](https://www.transparencia.org.br/downloads/publicacoes/qualidade_dados_portal_nacional_de_contratacoes_publicas.pdf)
- [TCU — Implementação do PNCP Apresenta Falhas](https://portal.tcu.gov.br/imprensa/noticias/implementacao-do-portal-nacional-de-contratacoes-publicas-apresenta-falhas-no-cumprimento-da-nova-lei-de-licitacoes)
- [TCU — Acórdão 934/2021 (PDFs escaneados)](https://licitacoesecontratos.tcu.gov.br/)
- [ME/CAF — Maturidade Digital dos Municípios (2022)](https://www.gov.br/economia/pt-br/assuntos/noticias/2022/agosto/estudo-apresenta-grau-de-maturidade-digital-dos-municipios-brasileiros)

### Stripe e Pagamento
- [Stripe Brasil — Pricing](https://stripe.com/br/pricing)
- [Stripe — Fulfill Orders After Checkout](https://docs.stripe.com/checkout/fulfillment)
- [Stripe — Payment Links Post-Payment](https://docs.stripe.com/payment-links/post-payment)
- [Stripe — Webhook Documentation](https://docs.stripe.com/webhooks)

### Parcerias e Canais
- [Effecti — Programa de Parcerias](https://www.effecti.com.br/parcerias/)
- [Base Viral — CAC no Marketing de Indicação](https://baseviral.com.br/custo-de-aquisicao-de-clientes/)
- [SaaStisfeito — Ecossistema de Parcerias SaaS B2B](https://saastisfeito.com.br/ecossistema-de-parcerias/)
- [WinningSales — Arquitetura de Receita B2B 2026](https://winningsales.com.br/blog/arquitetura-de-receita/)
- [Rewardful — SaaS Affiliate Commission Benchmarks](https://www.rewardful.com/articles/saas-affiliate-program-benchmarks)

### Retenção e Follow-up
- [Ploomes — Prospecção Multicanal B2B](https://blog.ploomes.com/prospeccao-multicanal/)
- [RevenueHero — B2B Lead Response Times](https://www.revenuehero.io/blog/b2b-lead-response-times)
- [PipeRun — Retenção de Clientes B2B](https://crmpiperun.com.br/blog/retencao-de-clientes-b2b/)

### Capacidade do Founder
- [Self Financial — Side Hustle Statistics](https://www.self.inc/info/side-hustle-statistics/)
- [Memtime — Knowledge Worker Productivity](https://www.memtime.com/blog/knowledge-worker-productivity-stats-improvements)
- [Beta Boom — 72% of Founders Burn Out](https://betaboom.com/why-72-of-founders-burnout-how-to-beat-the-odds/)
- [SalaryExpert — VA Salary Brazil 2025](https://www.salaryexpert.com/salary/job/virtual-assistant/brazil)
- [Workana — VAs Brazil](https://www.workana.com/en/freelancers/brazil/virtual-assistant)

### Low-Ticket e Unit Economics
- [Estúdio Site — Low Ticket R$27-R$97](https://www.estudiosite.com.br/site/ead/low-ticket-infoproduto-27-a-97-em-alto-volume)
- [For Entrepreneurs — SaaS Metrics 2.0](https://www.forentrepreneurs.com/saas-metrics-2/)
- [CloudZero — SaaS Unit Economics](https://www.cloudzero.com/blog/saas-unit-economics/)

### Concorrentes
- [Effecti](https://effecti.com.br/plataforma/) | [ConLicitação](https://conlicitacao.com.br/) | [LicitaIA](https://www.licitaia.app/) | [Wavecode](https://www.wavecode.com.br/planos/)

---

## Apêndice A: Checklist de Lacunas Endereçadas (vs. Crítica da V1)

| Lacuna Identificada | Seção que Endereça | Status |
|----------------------|-------------------|--------|
| Benchmarks americanos aplicados ao Brasil | 5.2, 7.1, 7.2 | Corrigido — Leadster 2025 como fonte primária |
| CAC de R$53 com falsa precisão | 5.2, 7.1 | Corrigido — CAC real R$160-400 via ads |
| "Conselho de CMOs" como autor fictício | Cabeçalho | Removido — autor é o founder |
| Quem constrói a landing page e em quanto tempo | 8 (Fase 1) | Detalhado — 20-28h de desenvolvimento |
| Fluxo pós-pagamento não definido | 6.4 | Completo — webhook + email + notificação |
| Preview subestimado como "1-2h" | 6.3 | Corrigido — 16-24h (2-3 dias) |
| Leads fora do horário comercial | 6.5 | Endereçado — auto-reply + SLA definido |
| Qualidade dos PDFs de editais | 3 (Limitações) | Novo — TCU Acórdão 934/2021, OCR fallback |
| Relatório "ruim" sem definição | 3.1 | Novo — política de qualidade mínima |
| CNPJ sem dados no OpenCNPJ | 3 (Limitações) | Endereçado — preview filtra antes da compra |
| Retenção ignorada (100% aquisição) | 9 | Novo — email sequence + triggers de recompra |
| Upsell sem produto definido | 11 | Novo — consultoria mensal R$800/mês detalhada |
| Zero estratégia de prova social | 10 | Novo — roadmap de 3 fases |
| LGPD não mencionada | 12 | Novo — seção completa com artigos específicos |
| Google Ads policies não detalhadas | 12.4 | Endereçado — não é serviço financeiro, copy seguro |
| Founder como recurso infinito | 2, 8, 15 | Corrigido — 12-20 relatórios/mês, VA no mês 5 |
| Canal Descomplicita ignorado | 5.1 | Novo — parceria como canal primário |
| Sem plano B para ads | 5.4 | Novo — 5 canais alternativos priorizados |

---

*Documento elaborado em 11/03/2026 por Tiago Sasaki (CONFENGE LTDA) com pesquisa de mercado baseada em fontes verificáveis. Projeções financeiras marcadas como hipóteses onde não há benchmark verificável — resultados reais dependem de execução e validação empírica.*
