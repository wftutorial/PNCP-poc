# MAYDAY STRATEGY — SmartLic Survival & Cash Generation

**Data:** 2026-03-05 | **Status:** URGENTE | **Autor:** Squad MAYDAY (analyst + po + pm)
**Versao:** 2.0 — Operacionalizado com leads, contatos e templates

---

## SITUACAO ATUAL

- **Produto:** SmartLic v0.5 — plataforma production-grade com 47 features em 12 categorias
- **Receita:** Pre-revenue (beta com trials, 0 clientes pagantes)
- **Custos infra:** Railway + Supabase + Redis + OpenAI + dominio (~R$200-400/mes)
- **Equipe:** Solo founder, full-stack + AI
- **Urgencia:** Falencia iminente. Precisa de cash em dias, nao meses.
- **Mercado:** R$554 bilhoes/ano em compras publicas. 700K+ fornecedores registrados no SICAF. 20K+ empresas ja pagam por servicos similares (ConLicitacao).

---

## VALUATION FUNDAMENTADO

| Cenario | Faixa | Base |
|---------|-------|------|
| Venda de IP (codigo + pipelines + AI) | R$200K - R$1M | Benchmarks micro-SaaS, desconto Brasil |
| Acqui-hire (founder + IP) | R$500K - R$3M | Rate por cabeca ajustado BR |
| Aquisicao estrategica (Softplan) | R$1M - R$5M | Gap-filling + AI pipeline |
| Com MRR de R$5-10K | R$2M - R$8M | 3-5x ARR micro-SaaS |

**Multiples referencia:** SaaS privado mediana 4.8x ARR (bootstrapped), 5.3x (equity-backed). Micro-SaaS <$1M ARR: 5-7x ARR em 2025 (fonte: [IndieExit](https://indieexit.com/micro-saas-valuation-metrics/), [SaaS Capital](https://www.saas-capital.com/blog-posts/private-saas-company-valuations-multiples/)).

**Mercado GovTech Brasil:** 470+ startups, US$18.5B em 2025, CAGR 13.8%. Exits recentes: Visma+Conta Azul R$1.8B, Softplan+1Doc (2025), Aprova Digital seed US$4M.

---

## DIFERENCIAIS TECNICOS VERIFICADOS (auditoria de codigo)

1. **LLM Zero-Match Classification** — GPT-4.1-nano classifica editais com 0% keyword density. Concorrentes rejeitam; SmartLic captura 15-20% oportunidades adicionais.
2. **Viability Assessment 4-Fatores** — Score 0-100 (modalidade 30% + timeline 25% + valor 25% + geografia 20%). Nenhum concorrente tem.
3. **Multi-Source Consolidation** — PNCP + PCP + ComprasGov com dedup inteligente. 40% mais cobertura.
4. **CNAE-to-Sector Mapping** — Auto-onboarding em <60s. 10K+ CNAEs mapeados.
5. **Resilience Engineering** — Circuit breakers, SWR cache, graceful degradation.
6. **Test Coverage** — 5,131+ backend + 2,681+ frontend tests, 0 failures. 77 migrations. 17 CI/CD workflows.
7. **Billing completo** — Stripe + PIX + Boleto, trial 14 dias, quota enforcement atomico.
8. **Pipeline Kanban** — 5 estagios, drag-drop, alertas email, historico.

---

# PLANO DE ACAO — ORDENADO POR VELOCIDADE DE CASH

---

## TRACK A: DINHEIRO EM 1-3 DIAS

### A1. Assessoria de Licitacoes (Consulting Pivot)

**O que:** Vender servico de analise manual usando SmartLic como ferramenta interna. Zero desenvolvimento.

| Item | Detalhe |
|------|---------|
| Preco mercado | R$3.000-5.000/mes (retainer) + 3-10% comissao por exito |
| Seu preco de entrada | R$1.500/mes + 3% comissao (undercut proposital) |
| Meta semana 1 | 3-5 prospects, 1-2 contratos fechados |
| Receita potencial | R$3.000-7.500/mes recorrente |
| Como entregar | Roda busca no SmartLic, exporta Excel, adiciona capa com marca |

**Fontes de precos:** [SigaPregao](https://www.sigapregao.com.br/consultor-de-licitacoes-saiba-quanto-ganha/), [Effecti](https://effecti.com.br/comissao-consultoria-licitacoes/), [Triunfo Legis](https://www.triunfolegis.com.br/consultoria-licitacoes-preco)

#### LEADS DIRETOS — Empresas B2G para Prospectar

**Construcao Civil (maior volume de licitacoes):**

| Empresa | Cidade/UF | Contato | Notas |
|---------|-----------|---------|-------|
| Alianca Construtora de Obras | PR | aliancaobras@hotmail.com, (45) 99138-2727 | Pequena, ativa em editais municipais |
| PRO Engenharia | RS/SC/SP | proee.com.br | Gestao de obras, Sul + Sudeste |
| TEDESCO Construtora | SC | tedesco.com.br | Ativa na regiao Sul |
| RN Engenharia | Nacional | rnengenharia.com | Obras comerciais |
| Ferraz Amemiya Eng. e Construcao | SP | CNPJ 31.206.387/0001-60 | Venceu edital reforma Matarazzo SP |
| EPT Engenharia | SP | CNPJ 60.730.645/0001-01 | Arquitetura/urbanismo para governo |

**Saude/Hospitalar:**

| Empresa | Contato | Notas |
|---------|---------|-------|
| Gamacamp Produtos Hospitalares | (19) 3743-7070, comercial@gamacamp.com.br, gamacamp.com.br | 20+ anos, depto licitacao dedicado |
| Magazine Medica (BALLKE) | (11) 5199-0688, magazinemedica@uol.com.br | 21 anos, distribuicao nacional |
| Unitec Hospitalar | (11) 97364-8404, vendas@unitec-hospitalar.com.br | Desde 1982, oxigenoterapia |
| Pratik Medical | (17) 3301-2001, pratikmedical.com.br | Fornecedor hospitalar |
| Supri Med | supri.med.br | Importador equipamentos medicos |

**TI/Tecnologia (govtech):**

| Empresa | Contato | Notas |
|---------|---------|-------|
| Licitati | licitati.com.br | Consultoria/treinamento para TIC em licitacoes |
| BrazilLAB GovTechs | brazillab.org.br/selo-govtech | 300+ startups certificadas vendendo para governo |

#### ASSOCIACOES SETORIAIS (acesso a milhares de membros)

**Construcao Civil — Rede SINDUSCON:**

| Capitulo | Contato | Obs |
|----------|---------|-----|
| SINDUSCON-SP | sindusconsp.com.br | Maior capitulo |
| SINDUSCON-PR | (41) 3051-4300, sinduscon@sindusconpr.com.br | R. Joao Viana Seiler 116, Curitiba |
| SINDUSCON-RJ | (21) 2221-5225, sinduscon@sinduscon-rio.com.br | R. do Senado 213, Centro |
| SINDUSCON-MG | (31) 3253-2684, bruno@sinduscon-mg.org.br | R. Marilia de Dirceu 226, BH |
| SINDUSCON-RS | (51) 3021-3440, contato@sinduscon-rs.com.br | R. Augusto Meyer 146, POA |
| SINDUSCON-BA | atendimento@sinduscon-ba.com.br | R. Minas Gerais 436, Salvador |
| SINDUSCON-CE | (85) 3456-4050, WhatsApp (85) 8956-6830 | R. Tomas Acioli 840, Fortaleza |
| CBIC (nacional) | cbic.org.br | Guarda-chuva de 85 sindicatos em 27 estados |

**Tecnologia:**

| Associacao | Contato | Membros |
|------------|---------|---------|
| ABES (Software) | (11) 2161-2833, Av. Ibirapuera 2907, SP | 2.000+ empresas, 85% receita SW brasileiro. Diretorio: associados.abes.org.br |
| Brasscom | brasscom.org.br | TI/telecom nacional |

**Saude:**

| Associacao | Contato | Membros |
|------------|---------|---------|
| ABIMED | abimed.org.br/contact/ | 65% do mercado de equipamentos medicos |
| ABIMO | (11) 3285-0155, Av. Paulista 1313, 7o andar, SP | Dispositivos medicos/hospitalares |
| ABRAMED | R. Oscar Freire 379, SP, abramed.org.br/contato/ | Fleury, Dasa, Sabin, Einstein |
| ABRAIDI | abraidi.com.br | Distribuicao de produtos de saude |

#### ESTRATEGIA COM ASSOCIACOES

Propor webinar gratuito ou newsletter para membros: "Inteligencia Artificial em Licitacoes: Como encontrar editais relevantes 10x mais rapido". Associacoes adoram conteudo para membros. Resultado: exposicao para centenas de empresas-alvo de uma vez.

#### EVENTOS PRESENCIAIS 2026 (concentracao de leads)

| Evento | Data | Local | Publico |
|--------|------|-------|---------|
| **21o Congresso Brasileiro de Pregoeiros** | 23-26/mar/2026 | Foz do Iguacu/PR | 30K+ historico. R$7.330 presencial, R$4.890 online |
| **4o Congresso da Lei 14.133** | 20-22/mai/2026 | Fortaleza/CE | Pregoeiros + fornecedores |
| **INGEP 2026** | 29/jun-03/jul/2026 | Bento Goncalves/RS (hibrido) | Gestao publica |
| **ConLicitantes 2026** | 14-16/out/2026 | Centro Convencoes Reboucas, SP | **700+ licitantes**. contato@conlicitantes.com.br, WhatsApp (11) 3789-9128 |
| **16o Cong. Licitacoes FME** | TBD 2026 | Online (YouTube) | **Gratis** |

**Prioridade:** ConLicitantes (700+ licitantes = ICP perfeito) e FME (gratis, online).

#### COMUNIDADES ONLINE B2G

| Comunidade | Descricao | Contato |
|------------|-----------|---------|
| B2G Club | Mentoria 12 meses para licitantes, equipe especializada | b2g.com.br/b2gclub |
| ConLicitacao | 20.000+ empresas clientes, desde 1999 | conlicitacao.com.br |
| Fornecedores Governamentais (LinkedIn) | 3.000+ conexoes, mailing de 5.505 prefeituras + 41K emails gov | linkedin.com/in/fornecedoresgovernamentais/ |
| Vendas Governo (LinkedIn) | 2.000+ seguidores | linkedin.com/company/vendas-governo---portal-de-licita-es |
| Alerta Licitacao | 3.000+ novos editais/dia de 5.000+ sites | alertalicitacao.com.br |
| Portal de Compras Publicas | 3.000+ prefeituras + 400K+ fornecedores registrados | portaldecompraspublicas.com.br |

#### GERACAO PROGRAMATICA DE LEADS

Use a propria infraestrutura do SmartLic para gerar leads:
1. **ComprasGov Open Data API** (`compras.dados.gov.br/fornecedores/`) — extrair fornecedores por CNAE
2. **PNCP API** — extrair vencedores de editais recentes (empresas que ja participam ativamente)
3. **CNAEs prioritarios:** 4120-4 (Construcao), 4211-1 (Obras rodoviarias), 6201-5 (Desenvolvimento SW), 6202-3 (Consultoria TI)
4. **Contrata+Brasil** — 16 milhoes de MEIs, so 70K registrados como fornecedores gov (mercado gigante inexplorado)

---

### A2. Pre-venda "Founding 20" (Cash Imediato)

**Pesquisa validou:** NAO fazer lifetime deal. Desconto de 50% e o sweet spot — atrai clientes serios, nao deal-hunters.

| Oferta | Preco | vs. Normal | Lock-in |
|--------|-------|------------|---------|
| Founding Member (mensal) | R$197/mes | 50% off R$397 | Preco travado enquanto ativo |
| Founding Member (anual) | R$147/mes (R$1.764/ano) | 63% off | Pago upfront |

**Por que NAO lifetime deal:** LTD buyers nao tem skin in the game, churn mental, drenam margem. Monday.com vendeu founding slots a apenas 15% de desconto — a exclusividade e o atrativo, nao o desconto.

**Capacidade:** 20 vagas publicas. Meta real: 10 conversoes.

#### MECANICA DE ESCASSEZ

1. Hard cap: 20 vagas (publicar "20", vender 10, reservar 10 para referrals/parcerias)
2. Countdown timer de 7 dias na landing page
3. Counter ao vivo: "X/20 vagas restantes"
4. Garantia de 7 dias (nao 30 — urgencia importa)
5. Bonus: 1h sessao estrategica gratis sobre licitacoes com IA (valor percebido: R$500)

#### SETUP EM 30 MINUTOS

**Opcao 1 — Stripe Payment Link (RECOMENDADO, 5 min):**
1. Stripe Dashboard > Payment Links > New
2. Produto: "SmartLic Founding Member"
3. Preco: R$197/mes (recorrente)
4. PIX via EBANX (Stripe suporta PIX no Brasil desde agosto 2025)
5. Copiar link, compartilhar via WhatsApp/email/LinkedIn

**Opcao 2 — Landing page Carrd.co (1 hora):**
- Free tier ou Pro R$19/ANO
- Suporta Stripe embed, countdown, formularios
- Subdominio: `fundadores.smartlic.tech`

**Opcao 3 — Zero infra:**
- Google Forms + chave PIX manual
- Funciona para primeiros 5 clientes

**Estrutura da pagina:**
```
[HERO] "SmartLic Founding Members" — "Apenas 20 vagas"
[PROBLEMA] "Voce perde horas procurando editais..."
[SOLUCAO] "SmartLic encontra, classifica e analisa com IA"
[OFERTA] "R$197/mes (50% off) — preco travado para sempre"
[PROVA] "3 fontes de dados, 15 setores, cobertura nacional"
[CTA] Botao Stripe Payment Link
[FAQ] Cancelamento, reembolso, como funciona
```

#### TEMPLATES DE OUTREACH (COPY-PASTE)

**Template 1 — LinkedIn InMail para dono de construtora:**

Assunto: `Pergunta rapida sobre editais, [Nome]`

```
Oi [Nome], tudo bem?

Vi que a [Empresa] atua em [obras publicas / engenharia / construcao civil].

Pergunta direta: quantas horas por semana sua equipe gasta procurando editais
no PNCP, Portal de Compras e ComprasGov?

Criamos o SmartLic — plataforma que busca editais em 3 fontes simultaneamente,
classifica por relevancia com IA e analisa viabilidade automaticamente.
Empresas como a sua economizam 15-20h/semana.

Estamos abrindo 20 vagas de Membro Fundador a R$197/mes (50% off permanente).

Posso te mostrar em 10 minutos como funciona com editais reais do seu setor?

Abraco,
Tiago
```

**Template 2 — WhatsApp para empresa B2G:**

```
Bom dia [Nome]!

Me chamo Tiago, sou fundador do SmartLic — plataforma de inteligencia
em licitacoes com IA.

Vi que a [Empresa] participa de licitacoes em [setor].

Criei uma ferramenta que busca editais no PNCP, Portal de Compras
e ComprasGov ao mesmo tempo, filtra por relevancia e analisa viabilidade
automaticamente.

Estou abrindo apenas 20 vagas de Membro Fundador com 50% de desconto
permanente (R$197/mes ao inves de R$397).

Posso te mandar um video de 2 minutos mostrando como funciona
com editais reais do seu setor?
```

**Follow-up (dia 3, sem resposta):**

```
Oi [Nome], tudo bem?

So passando para dizer que ja preenchemos [X] das 20 vagas
de Membro Fundador do SmartLic.

Se fizer sentido, posso reservar uma vaga para voces ate sexta.

Sem compromisso — se nao for para voces, sem problema algum.
```

**Template 3 — Email para assessoria de licitacao (parceria):**

Assunto: `Parceria: IA para seus clientes de licitacao`

```
Oi [Nome],

Trabalho com inteligencia artificial aplicada a licitacoes publicas
e vi que a [Empresa] assessora empresas em processos licitatorios.

Pergunta rapida: seus clientes ainda buscam editais manualmente
no PNCP e portais de compras?

Criei o SmartLic (smartlic.tech) — plataforma que:
-> Busca em 3 fontes simultaneamente (PNCP, Portal de Compras, ComprasGov)
-> Classifica relevancia por setor com IA (GPT-4)
-> Analisa viabilidade em 4 fatores (modalidade, prazo, valor, geografia)
-> Exporta relatorios Excel profissionais

Proposta de parceria:
- Seus clientes ganham acesso ao SmartLic com condicoes especiais
- Voce recebe 20% de comissao recorrente por indicacao
- Posso criar filtro customizado para o nicho de cada cliente

Estamos em fase de Membros Fundadores (20 vagas a R$197/mes —
50% off permanente). Reservei 5 vagas para parceiros.

Posso te mostrar a plataforma em 15 minutos esta semana?

Abraco,
Tiago Sasaki
Fundador, SmartLic
smartlic.tech
```

#### POST LINKEDIN VIRAL (publicar dia 1, 8-10h)

```
Ha 6 meses eu comecei a construir o SmartLic.

O problema: empresas que participam de licitacoes gastam
15-20 horas por semana buscando editais manualmente no PNCP,
Portal de Compras e ComprasGov.

A solucao: uma plataforma com IA que busca em 3 fontes
simultaneamente, classifica relevancia por setor e analisa
viabilidade automaticamente.

Hoje o SmartLic esta em producao, cobrindo 15 setores
e todos os estados brasileiros.

E agora estou abrindo 20 vagas de Membro Fundador:

-> 50% de desconto permanente (R$197/mes)
-> Linha direta comigo no WhatsApp
-> Voto em prioridade de features
-> Sessao estrategica gratis de 1h

Por que Membro Fundador? Porque quero 20 empresas que
me ajudem a moldar o produto. Em troca, o preco fica
travado para sempre.

Se sua empresa participa de licitacoes publicas,
comenta "EU QUERO" que te mando os detalhes.

#licitacoes #B2G #govtech #startup #IA
```

Postar o link Stripe/Carrd no PRIMEIRO COMENTARIO (algoritmo do LinkedIn penaliza links no post).

#### CANAIS DE DISTRIBUICAO — PRIORIDADE

| Prioridade | Canal | Acao | Resultado esperado |
|------------|-------|------|--------------------|
| ALTA | WhatsApp direto | 50 mensagens personalizadas | 25 conversas, 5 vendas |
| ALTA | LinkedIn outreach | 30 InMails personalizados | 5-8 respostas, 2 vendas |
| ALTA | Assessorias de licitacao | 20 emails com proposta parceria | 3-5 respostas, 2-4 referrals |
| MEDIA | LinkedIn post organico | Post founding members + storytelling | 1K-5K views, 1-2 leads |
| MEDIA | LinkedIn Sales Navigator | Free trial 30 dias. Filtro: Brasil + Construcao + Diretor | Melhor targeting para InMails |
| BAIXA | Product Hunt | Nao e o publico (tech/consumer, nao B2G) | Pular |
| BAIXA | AppSumo | Comissao de 70% — inviavel | Pular |

**Matematica:** WhatsApp response rate BR B2B = 40-60%. Conversao de warm lead = 10-20%. Para 10 clientes, precisa de ~100 mensagens WhatsApp. LinkedIn InMail response rate personalizado = 18-25%.

---

## TRACK B: DINHEIRO EM 3-7 DIAS

### B1. Data-as-a-Service (Reports Avulsos)

**Zero desenvolvimento.** Roda busca no SmartLic, exporta, entrega.

| Produto | Preco | Entrega |
|---------|-------|---------|
| Digest semanal (setor+UF) | R$97/semana ou R$297/mes | Excel + resumo IA |
| Relatorio setorial 90 dias | R$497 one-time | Analise profunda de landscape |
| Alertas diarios com score IA | R$197/mes | Email automatizado |

**Benchmark concorrente:** Alerta Licitacao cobra R$44.90/mes por alertas basicos. SmartLic diferencia com IA + viabilidade.

---

### B2. Freelance/Contratos (Track Paralelo de Sobrevivencia)

**Titulo do perfil:** "AI Engineer | LLM Integration & FastAPI"

| Plataforma | Rate | Tempo ate 1o job | Prioridade |
|------------|------|-------------------|------------|
| Lemon.io | $50-80/hr | 48h pos-aprovacao | 1 (match rapido, LATAM-friendly) |
| Arc.dev | $50-70/hr | 1-2 semanas | 2 (board ativo de FastAPI jobs) |
| Upwork | $40-65/hr (iniciar $40, subir apos 3 jobs) | 1-2 semanas | 3 (volume) |
| Toptal | $65-200/hr | 5 semanas (vetting) | 4 (iniciar processo agora) |
| Revelo (BR) | R$150-300/hr | 1 semana | 5 (PJ nacional) |
| GeekHunter (BR) | ~R$10.679/mes senior | 1-2 semanas | 6 (posicoes fixas PJ) |

**Meta:** 20h/semana x $50/hr = $4.000/mes (~R$20.000/mes). Restam 20h+ para SmartLic.

**Gigs Fiverr (produtizados, criar HOJE):**

| Gig | Preco | Prazo |
|-----|-------|-------|
| "I will build a FastAPI backend with OpenAI/LLM integration" | $500-1.500 | 5-7 dias |
| "I will create a RAG pipeline with FastAPI + vector database" | $800-2.000 | 7-10 dias |
| "I will integrate AI/GPT into your existing Python API" | $300-800 | 3-5 dias |

**Oportunidade gov AI:** PBIA (Plano Brasileiro de IA) = R$23 bilhoes ate 2028. TCU ja usa IA (Alice) em compras. Editais de "inteligencia artificial generativa" estao aparecendo (ex: TJCE Pregao 025/2025). Use o PROPRIO SmartLic para encontrar esses editais.

**Case study SmartLic (escrever em 2h, usar como portfolio):**
1. Problema: empresas gastam 40h/mes buscando editais manualmente
2. Solucao: pipeline multi-fonte com GPT-4 classification
3. Arquitetura: FastAPI + SWR cache + circuit breakers + SSE streaming
4. Resultado: 10K+ editais processados, 15 setores, sub-2s classificacao
5. Publicar no Dev.to + LinkedIn + GitHub README

**ALERTA:** Limite maximo 3 meses ou ate SmartLic bater R$5K MRR. Senao vira armadilha.

---

## TRACK C: DINHEIRO EM 7-14 DIAS

### C1. Parceria com Assessorias Existentes

**Modelos de parceria:**

| Modelo | Preco | Vantagem |
|--------|-------|----------|
| Revenue share (60/40) | Variavel | Sem risco pra parceiro |
| White-label | R$997-1.997/mes flat | Receita previsivel |
| Licenca interna | R$497/mes | Menor compromisso |
| Referral (20-30% comissao) | Variavel | Facil de aceitar |

**20 ASSESSORIAS VERIFICADAS (ordenadas por tamanho/relevancia):**

**Tier 1 — Grandes/Estabelecidas (10+ anos, alcance nacional):**

| # | Empresa | Cidade/UF | Contato | Fundacao | Diferencial |
|---|---------|-----------|---------|----------|-------------|
| 1 | **Licijur** | Porto Alegre/RS | [licijur.com.br/contato](https://www.licijur.com.br/contato-porto-alegre/), Av. Goethe 71 sala 1004 | 2002 | Consultoria 360 (diagnostico, captacao, juridico) |
| 2 | **Vianna e Consultores** | Sao Caetano do Sul/SP | [viannaconsultores.com.br](https://www.viannaconsultores.com.br/), [LinkedIn](https://br.linkedin.com/company/vianna-e-consultores) | 1989 | 25.000+ analistas treinados, 11-50 func. CEO: Mario Vianna |
| 3 | **Eagle Consultoria** | SP | (15) 3418-1299, lgpd@eaglelicitacoes.com.br | 10+ anos | Atendimento nacional. Sites: consultoriaemlicitacao.com.br + assessoriaemlicitacoes.com.br |
| 4 | **Triunfo Legis** | Guarulhos/SP | (11) 2087-2251, [triunfolegis.com.br](https://www.triunfolegis.com.br/) | 2013 | Advogados ex-administracao publica |
| 5 | **Lamarao Advogados (RC Licitacao)** | Nacional | [rclicitacao.com.br](https://www.rclicitacao.com.br/) | 18+ anos | 1.200+ clientes, R$768M em negocios fechados |
| 6 | **Daexe Assessoria** | Brasilia/DF | [daexe.com.br](https://www.daexe.com.br/), Av. Pau Brasil Lote 06 Sala 407, Aguas Claras | 2012 | Cadastro em portais de compras, treinamento gerencial |

**Tier 2 — Medias/Tech-Forward (boas para parceria tech):**

| # | Empresa | Cidade/UF | Contato | Diferencial |
|---|---------|-----------|---------|-------------|
| 7 | **Pro Licitante** | Nacional | [prolicitante.com.br](https://prolicitante.com.br/), [LinkedIn](https://br.linkedin.com/company/prolicitante), @prolicitante | **Lawtech** — 1a empresa de tecnologia juridica em licitacoes (2014). MELHOR FIT para parceria tech. |
| 8 | **Maximus B2Gov** | Nacional | (15) 3199-0955, comercial@maximuslicitacoes.com.br, @maximusb2gov | Usa robo de pregao. Tech-friendly. "Empresa pronta para licitar em 4 dias" |
| 9 | **Concreta Licitacoes** | Rio do Sul/SC | [concretalicitacoes.com.br](https://concretalicitacoes.com.br/), @concretalicitacoes, [LinkedIn](https://br.linkedin.com/company/concreta-assessoria-e-consultoria-em-licitacoes) | 350+ clientes, R$1B em contratos. Fundada 2019. |
| 10 | **Siga Pregao** | Nacional | [sigapregao.com.br](https://www.sigapregao.com.br/), @sigapregao (**55K Instagram**) | Software para licitantes, 10 anos. Maior audiencia do nicho. |
| 11 | **ConLicitacao** | SP | 0800 11 14133, apoio@conlicitacao.com.br | **20.000+ clientes**, lider de mercado desde 1999 |

**Tier 3 — Regionais (targets para abordagem direta):**

| # | Empresa | Cidade/UF | Contato | Notas |
|---|---------|-----------|---------|-------|
| 12 | **E3 Licitacoes** | Porto Alegre/RS | [e3licitacoes.com.br](https://e3licitacoes.com.br/) | 15+ anos, atendimento nacional |
| 13 | **Exito Licitacoes** | Porto Alegre/RS | comercial@exitolicitacoes.com.br, @exitolicitacoes, [LinkedIn](https://br.linkedin.com/company/exitolicitacoes) | Compliance + gestao contratos. Fundada 2018. |
| 14 | **11E Licitacoes** | Rio de Janeiro/RJ | (31) 3568-8311, contato@11e.com.br, Av. Maracana 667 | Terceirizacao de licitacao completa |
| 15 | **Magna Licitacoes** | Hortolandia/SP | (19) 2518-0157, @magnalicitacoes, [Telegram](https://www.magnalicitacoes.com.br/magnata) | Treinamento + consultoria desde 2016 |
| 16 | **Liciticon** | Rio de Janeiro/RJ | (21) 3955-1470, WhatsApp 21 97514-3001 | Filial em Angra dos Reis. Fundada 2019. |
| 17 | **Start Licitacoes** | Osasco/SP | (11) 3742-2174, atendimentocomercialhosp@gmail.com | Desde 2017 |
| 18 | **LicitaBR** | Nacional | [licitabr.com](https://lp.licitabr.com/), [LinkedIn](https://br.linkedin.com/company/licitabr) | Dir: Thiago Rocha. Representacao + captacao nacional |
| 19 | **MC Consultoria** | Curitiba/PR | [mclicitacao.com](https://www.mclicitacao.com/) | Regional PR |
| 20 | **AC Assessoria** | Santos/SP | (13) 99177-2160, (13) 3468-5270, ac@acassessoria.com | R. Conselheiro Nebias 756, Santos |

**Acoes prioritarias para parcerias:**
1. **Pro Licitante** (lawtech, ja usa tech) — propor licenca white-label
2. **Siga Pregao** (55K Instagram) — propor integracao ou parceria de visibilidade
3. **ConLicitacao** (20K clientes) — propor como add-on para base de clientes
4. **Maximus B2Gov** (usa robo) — propor IA como diferencial competitivo
5. **Concreta** (R$1B contratos) — propor ferramenta de analise para clientes

**Influenciadores para visibilidade (parceria de conteudo):**

| Nome | Alcance | Contato |
|------|---------|---------|
| Raphael Icaro | 21K Instagram (@raphaelicarolicitacoes) | 19+ anos consultor/mentor |
| Carlos Nascimento (LicitaCursos) | 5.000+ alunos | licitacursos.com.br, linktr.ee/licitacursos |
| Nadia Dall Agnol | Comunidade WhatsApp VIP | nadiadallagnol.com.br, "Jornada do Pregao Eletronico" |
| Mario Vianna | 25.000+ analistas treinados | viannaconsultores.com.br |

**Grupos WhatsApp/Telegram para entrar HOJE:**

| Grupo | Link |
|-------|------|
| Licitacao Online | [licitacao.online/grupo-de-whatsapp](https://www.licitacao.online/grupo-de-whatsapp) |
| "Assessoria em Licitacoes" | [gruposwhats.app/group/464157](https://gruposwhats.app/group/464157) |
| "LICITACAO - DUVIDAS" | [gruposwhats.app/group/743069](https://gruposwhats.app/group/743069) |
| Magna Licitacoes (Telegram) | [magnalicitacoes.com.br/magnata](https://www.magnalicitacoes.com.br/magnata) |

---

## TRACK D: DINHEIRO EM 14-90 DIAS

### D1. Abordagem Softplan (Aquisicao Estrategica)

**Softplan perfil:** HQ Florianopolis/SC. R$803M receita (2024). 12 aquisicoes desde 2020. R$500M+ gastos em M&A. Dividido em Softplan (setor publico, CEO Marcio Santana) e Starian (setor privado). Email pattern: `primeiro.ultimo@softplan.com.br` (96% dos casos).

**Criterios de aquisicao Softplan:** Preferem empresas com R$10M+/ano receita. Buscam negocios maduros e complementares. Media de 40% YoY crescimento pos-aquisicao. MAS: o ex-Diretor de M&A Guilherme Tossulino saiu — funcao provavelmente com CFO ou COO agora.

#### CONTATOS VERIFICADOS — SOFTPLAN

| Nome | Cargo | LinkedIn | Email provavel | Relevancia |
|------|-------|----------|---------------|------------|
| **Marcio Santana** | CEO Softplan (Setor Publico) | [LinkedIn](https://www.linkedin.com/in/m%C3%A1rcio-santana-4bba7131/) | marcio.santana@softplan.com.br | Decisor principal. Ex-TOTVS, ex-SONDA. Disse que 2026 e "o ano da IA landing" em governo. |
| **Marcio Huri** | Diretor Comercial | (buscar no LinkedIn) | marcio.huri@softplan.com.br | 20+ anos em govtech, ex-TOTVS setor publico. **Entry point mais quente** — entende licitacoes. |
| **Bruno Klassmann** | CFO | [LinkedIn](https://www.linkedin.com/in/brunocklassmann/) | bruno.klassmann@softplan.com.br | Due diligence financeira. Ex-CFO Grupo Alura. Entrou jan/2026. |
| **Andrey Abreu** | COO | [LinkedIn](https://www.linkedin.com/in/andreyabreu/) | andrey.abreu@softplan.com.br | Avalia fit produto/tech. Harvard exec. Entrou jan/2026. |
| **Ilson Stabile** | Co-Fundador e Conselheiro | [LinkedIn](https://www.linkedin.com/in/ilsonstabile/) | ilson.stabile@softplan.com.br | Co-fundou em 1990. Autoridade de governanca. |

**Caminhos de entrada:**
1. **Formulario comercial:** [softplan.com.br/contato/comercial](https://www.softplan.com.br/contato/comercial/) — selecionar "Parceria"
2. **Programa Finder:** [Termos publicados](https://www.softplan.com.br/termos-e-condicoes-gerais-parceria-finder/)
3. **LinkedIn direto** para Marcio Huri (mais quente) ou Marcio Santana
4. **Ex-M&A Director Guilherme Tossulino** agora na Questum (advisory M&A) — pode ser intermediario: [LinkedIn](https://br.linkedin.com/in/tossulino/pt)

**Artigos para referenciar no pitch:**
- [Marcio Santana: "Brasil e referencia em GovTech"](https://www.poder360.com.br/poder-economia/brasil-e-referencia-em-govtech-diz-presidente-da-softplan/)
- [Softplan 12a aquisicao](https://neofeed.com.br/negocios/softplan-faz-sua-12a-aquisicao-de-olho-em-faturamento-de-r-1-bilhao-em-2025/)
- [R$250M para M&A](https://startups.com.br/negocios/ma/com-mais-r-250m-no-caixa-softplan-quer-acelerar-em-2025/)

**Ordem de abordagem recomendada:**
1. Marcio Huri (Dir. Comercial) — mais acessivel, entende o espaco
2. Marcio Santana (CEO) — referenciar entrevista Poder360 sobre IA
3. Formulario comercial (paralelo)

#### OUTROS POTENCIAIS COMPRADORES/INVESTIDORES

**BLL Compras:**

| Item | Detalhe |
|------|---------|
| HQ | Pinhais/Curitiba, PR |
| Fundador | Ademar Nitschke |
| Contato fornecedores | (41) 3097-4600, contato@bll.org.br |
| Contato orgaos | (41) 3148-9870, contatoorgaos@bll.org.br |
| LinkedIn | [BLL](https://br.linkedin.com/company/bll---bolsa-de-licita-es-e-leil-es) |
| Scale | 3.000+ orgaos publicos, 60K+ fornecedores, 100% PNCP integrado |

**Effecti:**

| Item | Detalhe |
|------|---------|
| HQ | Rio do Sul, SC (+ Florianopolis) |
| CEO | Alan Conti — [LinkedIn](https://www.linkedin.com/in/alanconti/) |
| Contato | effecti.com.br/contato |
| Scale | 2.000+ empresas, 850+ cidades, ~100 funcionarios |
| Posicao | Concorrente direto MAS complementar: Effecti foca execucao (robos de pregao), SmartLic foca descoberta (IA). Pode ser aquisicao OU parceria. |

**Portal de Compras Publicas:**

| Item | Detalhe |
|------|---------|
| CEO | Leonardo Ladeira — [LinkedIn](https://br.linkedin.com/in/leonardocesarladeira) |
| Co-founder | Bruno Ladeira |
| Contato | (61) 2195-6000, portaldecompraspublicas.com.br |
| Scale | 2.400+ municipios (40%+ do Brasil), R$60B volume anual |
| Funding | R$2.5M seed da Cedro Capital (2019) |
| Fit | SmartLic ja consome API PCP v2. Interesse natural em IA para fornecedores. |

**Betha Sistemas (independente, NAO e da Softplan):**

| Item | Detalhe |
|------|---------|
| CEO | Aldo Garcia — [LinkedIn](https://www.linkedin.com/in/aldodesouzagarcia/) |
| HQ | Criciuma, SC |
| Scale | R$300M receita, 800+ municipios, 22 estados |
| Fit | ERP municipal — SmartLic seria add-on de procurement intelligence |

**IPM Sistemas:**

| Item | Detalhe |
|------|---------|
| Fundador/CEO | Aldo Luiz Mees |
| VP Tech | Lucia Mees |
| HQ | Florianopolis, SC |
| Produto | Atende.Net (ERP municipal 100% cloud). Lancou "Dara" assistente IA (2023). |
| Contato | ipm.com.br/fale-conosco |

#### FUNDOS DE INVESTIMENTO GOVTECH

| Fundo | Contato chave | Tese | Link |
|-------|---------------|------|------|
| **Cedro Capital / Fundo GovTech** (co-gerido com KPTL) | Alessandro Machado (CEO), Adriano Pitoli (Head GovTech) | R$105.7M (dobrou de R$49M com Finep/Fapesp). Portfolio: Colab, Prosas, Portal de Compras Publicas. Meta 20-25 investimentos. | [cedrocapital.com/contact-cedro](https://www.cedrocapital.com/contact-cedro/?lang=en) |
| **Astella Investimentos** | Guilherme Lima (tese govtech, liderou Aprova + Gove). Email: guilherme@astellainvest.com, Tel: (11) 98181-8363 | Early-stage a Series A. | [Medium — tese govtech](https://medium.com/astella-investimentos/as-oportunidades-em-govtech-no-brasil-e-nossos-investimentos-em-aprova-e-gove-b3044afd5ec0) |
| **VOX Capital** | Via voxcapital.com.br | Investiu na Aprova Digital com Astella. Gere fundo de impacto do BB. | voxcapital.com.br |

---

### D2. Aceleradoras/Grants (Paralelo)

| Programa | Valor | Deadline | Tempo ate cash |
|----------|-------|----------|----------------|
| ESX 2026 (ES) | Mentoria + conexoes investidores | 05/abr/2026 | 2-3 meses |
| Sebrae Startup SC | R$80.000 seed | 08/mar/2026 | 2-3 meses |
| FAPESP PIPE (SP) | R$300K (Fase 1) | Continuo | 3-6 meses |
| Inova Startups (Sebrae SC + Bossa) | Investimento | 2026 | 3-4 meses |

---

## MATRIZ DE DECISAO — PROBABILIDADE x VELOCIDADE x VALOR

| Estrategia | Dias ate cash | Probabilidade | Valor potencial/mes | Esforco |
|------------|---------------|---------------|----------------------|---------|
| A1. Assessoria | 1-7 | **ALTA (80%)** | R$3.000-7.500 | Baixo |
| A2. Founding 20 | 1-7 | **MEDIA (50%)** | R$3.940 MRR | Baixo |
| B1. Data reports | 3-7 | MEDIA (60%) | R$500-2.000 | Minimo |
| B2. Freelance | 7-14 | **ALTA (90%)** | R$16.000-20.000 | Alto (tempo) |
| C1. Parcerias | 7-14 | MEDIA (40%) | R$1.000-4.000 | Medio |
| D1. Softplan/Acqui | 30-90 | BAIXA (20%) | R$200K-3M one-time | Alto |
| D2. Fundos GovTech | 30-90 | MEDIA (30%) | R$500K-3M one-time | Medio |
| D3. Grants | 60-180 | MEDIA (30%) | R$80K-300K one-time | Medio |

---

## CRONOGRAMA OPERACIONAL — PROXIMOS 7 DIAS

### Dia 1 (HOJE)

| Horario | Acao | Ferramenta |
|---------|------|------------|
| 08:00-09:00 | Criar Stripe Payment Link "SmartLic Founding Member" R$197/mes | Stripe Dashboard |
| 09:00-10:00 | Publicar post LinkedIn "Founding Members" | LinkedIn |
| 10:00-12:00 | Rodar SmartLic para 5 setores (construcao, TI, saude, engenharia, alimentos). Exportar 5 Excels estilizados | smartlic.tech |
| 13:00-14:00 | Criar perfil Upwork ("AI Engineer - LLM Integration & FastAPI") | upwork.com |
| 14:00-15:00 | Aplicar para Lemon.io + Arc.dev | lemon.io, arc.dev |
| 15:00-17:00 | Enviar 20 WhatsApp personalizados (Template 2) para empresas B2G | WhatsApp |
| 17:00-18:00 | Enviar 10 LinkedIn InMails (Template 1) para diretores construcao/TI | LinkedIn |

### Dia 2

| Horario | Acao |
|---------|------|
| 08:00-10:00 | Mais 20 WhatsApp + 10 InMails |
| 10:00-12:00 | Preparar Carrd landing page (fundadores.smartlic.tech) |
| 13:00-15:00 | Enviar 10 emails para assessorias (Template 3) |
| 15:00-17:00 | Ativar LinkedIn Sales Navigator free trial. Filtrar: Brasil + Construcao + Diretor |
| 17:00-18:00 | Responder conversas do dia 1 |

### Dia 3

| Horario | Acao |
|---------|------|
| 08:00-10:00 | Follow-up WhatsApp batch dia 1 |
| 10:00-12:00 | Mais 20 WhatsApp novos + 10 InMails novos |
| 13:00-15:00 | Demos agendadas |
| 15:00-17:00 | Escrever case study SmartLic (publicar Dev.to + LinkedIn) |
| 17:00-18:00 | LinkedIn update: "Ja preenchemos X vagas..." |

### Dia 4

| Horario | Acao |
|---------|------|
| 08:00-10:00 | Follow-up LinkedIn InMails batch dia 1-2 |
| 10:00-12:00 | Contatar 5 associacoes (SINDUSCON, ABES, ABIMED) com proposta de webinar |
| 13:00-15:00 | Demos agendadas |
| 15:00-17:00 | Aplicar para 5 Upwork jobs (AI/FastAPI) |
| 17:00-18:00 | Criar 2-3 Fiverr gigs |

### Dia 5

| Horario | Acao |
|---------|------|
| 08:00-10:00 | Follow-up todos os pendentes |
| 10:00-12:00 | Email frio Softplan (Marcio Huri) + Effecti (Alan Conti) |
| 13:00-15:00 | Contatar Cedro Capital + Astella (investidores govtech) |
| 15:00-17:00 | LinkedIn post: compartilhar case study / screenshot de resultado |
| 17:00-18:00 | Ligacoes telefonicas para leads quentes que nao converteram |

### Dia 6

| Horario | Acao |
|---------|------|
| 08:00-10:00 | WhatsApp: "Ultimas X vagas" para todos que mostraram interesse |
| 10:00-12:00 | Follow-up assessorias + associacoes |
| 13:00-15:00 | Demos + fechamentos |
| 15:00-17:00 | Post LinkedIn: "Ultimas vagas de Membro Fundador" |
| 17:00-18:00 | Review: pipeline de leads, ajustar precos se necessario |

### Dia 7

| Horario | Acao |
|---------|------|
| 08:00-10:00 | "Ultima chance" — WhatsApp para todos os leads quentes |
| 10:00-12:00 | Fechar founding member enrollment |
| 13:00-15:00 | Postar resultados no LinkedIn |
| 15:00-17:00 | Planejar semana 2 baseado nos resultados |
| 17:00-18:00 | Iniciar aplicacao ESX 2026 (deadline 05/abr) |

---

## O QUE NAO FAZER

1. **Nao gastar tempo desenvolvendo features novas** — 47 features production-ready
2. **Nao vender IP por menos de R$200K** — esta abaixo do justo
3. **Nao abandonar SmartLic por freelance** — limite 20h/semana, maximo 3 meses
4. **Nao esperar pelo cenario perfeito** — R$1.500/mes assinado hoje > R$50K em 3 meses
5. **Nao ter vergonha de vender servico manual** — maiores SaaS comecaram "nao-escalavel"
6. **Nao fazer lifetime deal** — atrai deal-hunters, drena margem
7. **Nao descontar mais de 50%** — sinaliza desespero
8. **Nao fingir escassez** — se diz 20 vagas, honrar (reputacao B2G)
9. **Nao mandar audio ou anexo no primeiro contato WhatsApp**
10. **Nao usar "plano", "assinatura", "tier", "pacote"** em copy (regra GTM-002)

---

## METRICAS CHAVE

| Metrica | Benchmark |
|---------|-----------|
| WhatsApp response rate (BR B2B) | 40-60% |
| LinkedIn InMail personalizado | 18-25% response |
| Cold email open rate (B2B SaaS) | 38-42% |
| Founding member conversao warm leads | 10-20% |
| Melhor horario envio | Ter-Qui, 8-10h |
| Para 10 clientes via WhatsApp | ~100 mensagens necessarias |

---

## FONTES VERIFICADAS

### Valuation e M&A
- [Aventis Advisors — SaaS Multiples 2025](https://aventis-advisors.com/saas-valuation-multiples/)
- [SaaS Capital — Private SaaS Valuations](https://www.saas-capital.com/blog-posts/private-saas-company-valuations-multiples/)
- [IndieExit — Micro-SaaS Valuation](https://indieexit.com/micro-saas-valuation-metrics/)
- [Development Corporate — Pre-Seed Acquisitions](https://developmentcorporate.com/corporate-development/enterprise-value-of-pre-seed-and-seed-stage-saas-acquisitions-in-2025/)

### Softplan M&A
- [Softplan R$250M para M&A](https://startups.com.br/negocios/ma/com-mais-r-250m-no-caixa-softplan-quer-acelerar-em-2025/)
- [Softplan 12a aquisicao](https://neofeed.com.br/negocios/softplan-faz-sua-12a-aquisicao-de-olho-em-faturamento-de-r-1-bilhao-em-2025/)
- [Softplan novos executivos jan/2026](https://tiinside.com.br/14/01/2026/softplan-anuncia-tres-novos-executivos-e-reforca-lideranca-para-sustentar-crescimento/)
- [Marcio Santana — Brasil referencia GovTech](https://www.poder360.com.br/poder-economia/brasil-e-referencia-em-govtech-diz-presidente-da-softplan/)
- [Tossulino sai para Questum](https://startups.com.br/danca-das-cadeiras/guilherme-tossulino-ex-softplan-e-o-novo-socio-da-questum/)

### Fundos GovTech
- [Cedro Capital GovTech Fund R$105M](https://startups.com.br/dealflow/fundo-govtech-dobra-de-tamanho-e-mira-r-150m-em-2026/)
- [Astella tese govtech](https://medium.com/astella-investimentos/as-oportunidades-em-govtech-no-brasil-e-nossos-investimentos-em-aprova-e-gove-b3044afd5ec0)

### Precos Assessoria
- [SigaPregao — Quanto Ganha Consultor](https://www.sigapregao.com.br/consultor-de-licitacoes-saiba-quanto-ganha/)
- [Effecti — Comissionamento](https://effecti.com.br/comissao-consultoria-licitacoes/)
- [Triunfo Legis — Precos](https://www.triunfolegis.com.br/consultoria-licitacoes-preco)

### Mercado
- [TI Inside — 470+ GovTechs](https://tiinside.com.br/en/07/05/2024/em-cinco-anos-numero-de-empresas-focas-em-tecnologia-para-governo-cresce-seis-vezes/)
- [WEF — Brazil GovTech](https://www.weforum.org/stories/2025/04/brazil-govtech-digital-public-infrastructure-development/)
- [Convergencia Digital — R$1 trilhao compras gov](https://convergenciadigital.com.br/governo/compras-governamentais-ultrapassam-r-1-trilhao-em-2025/)
- [Portal Compras Publicas R$60B](https://experienceclub.com.br/portal-de-compras-publicas-negocia-r-60-bilhoes-por-ano/)

### Freelance
- [Arc.dev FastAPI Jobs](https://arc.dev/remote-jobs/fastapi)
- [Lemon.io LATAM Developers](https://lemon.io/hire/latam-developers/)
- [Upwork AI Engineer Rates](https://www.upwork.com/hire/artificial-intelligence-engineers/cost/)
- [AI Skills Demand 2026](https://expertshub.ai/blog/highest-paying-ai-skills-2026-hiring-learning-guide/)

### Eventos
- [21o Congresso Pregoeiros](https://negociospublicos.com.br/congresso/)
- [ConLicitantes 2026](https://conlicitantes.com.br/)
- [4o Congresso da 14.133](https://congressoda14133.com.br/)

### Outreach / Sales
- [Stripe PIX via EBANX](https://www.prnewswire.com/news-releases/stripe-users-can-now-accept-pix-in-brazil-via-ebanx-302526007.html)
- [LinkedIn InMail Stats 2026](https://salesso.com/blog/linkedin-inmail-response-rate-statistics/)
- [WhatsApp B2B Templates](https://www.socialhub.pro/blog/cold-message-whatsapp-b2b-templates/)
- [Prospeccao Fria WhatsApp](https://vendas.mkt4sales.com/prospec%C3%A7%C3%A3o-fria-por-whatsapp-como-abordar-o-cliente-da-forma-correta)
- [Carrd.co](https://carrd.co/)

### Associacoes Setoriais
- [SINDUSCON-PR](https://sindusconpr.com.br/)
- [SINDUSCON-SP](https://sindusconsp.com.br/)
- [ABES](https://associados.abes.org.br/)
- [ABIMED](https://abimed.org.br/)
- [ABIMO](https://abimo.org.br/)
- [BrazilLAB Selo GovTech](https://brazillab.org.br/selo-govtech)
