# Relatorio de Debito Tecnico — SmartLic

**Projeto:** SmartLic (smartlic.tech)
**Data:** 09/03/2026
**Versao:** 1.0
**Preparado por:** Equipe de Engenharia

---

## Resumo Executivo

### Situacao Atual

O SmartLic e uma plataforma SaaS B2G em estagio de POC avancado (v0.5), ja em producao com trials beta e pre-revenue. A plataforma agrega licitacoes de tres fontes governamentais (PNCP, PCP, ComprasGov), classifica oportunidades com inteligencia artificial e oferece um pipeline completo de gestao para empresas que participam de processos licitatorios. O produto atende a uma dor real de mercado e possui uma base tecnica robusta com mais de 5.100 testes automatizados no backend e 2.600 no frontend.

Uma auditoria tecnica abrangente, conduzida por quatro especialistas ao longo de 10 fases de analise, identificou **92 pontos de melhoria** na plataforma. Destes, **16 ja foram resolvidos** por trabalhos recentes de engenharia. Dos 80 debitos ativos restantes, **5 sao criticos** e requerem atencao imediata por envolverem riscos de seguranca (colisao de tokens de autenticacao), estabilidade do servidor (falhas silenciosas em producao) e qualidade dos resultados de IA (truncamento de respostas em 20-30% das chamadas ao modelo de linguagem).

A boa noticia: nenhum dos problemas identificados representa uma ameaca existencial ao produto. A maioria dos debitos criticos pode ser resolvida em 1-2 semanas com investimento moderado. O plano de resolucao esta estruturado em 4 fases progressivas, priorizando seguranca e estabilidade antes de otimizacoes e melhorias de longo prazo.

### Numeros Chave

| Metrica | Valor |
|---------|-------|
| Total de Debitos Identificados | 92 |
| Debitos Ativos | 80 |
| Debitos Criticos (P0) | 5 |
| Debitos de Alta Prioridade (P1) | 19 |
| Itens Ja Resolvidos | 16 |
| Esforco Total Estimado | ~340 horas |
| Custo Estimado (R$150/h) | R$ 51.000 |
| Prazo Total Estimado | 8-12 semanas |

### Recomendacao

Recomendamos aprovar a execucao imediata da **Fase 1 (Quick Wins)** e **Fase 2 (Fundacao)**, que juntas resolvem os 5 debitos criticos e os 7 de alta prioridade mais impactantes, com investimento de R$ 7.950 e prazo de 3-4 semanas. Este investimento inicial elimina 100% dos riscos de seguranca criticos, estabiliza a integracao com a API principal (PNCP) e melhora a taxa de sucesso da classificacao por IA de ~70% para >99%. As fases subsequentes devem ser aprovadas conforme os resultados das primeiras fases e a evolucao do negocio.

---

## Analise de Custos

### Custo de RESOLVER

| Categoria | Itens | Horas | Custo (R$150/h) |
|-----------|:---:|:---:|-----------------|
| Sistema/Backend | 37 | 168h | R$ 25.200 |
| Database | 21 | 29h | R$ 4.350 |
| Frontend/UX | 28 | 81h | R$ 12.150 |
| QA/Testes | 6 | 62h | R$ 9.300 |
| **TOTAL** | **92** | **~340h** | **R$ 51.000** |

*Nota: Alguns itens de frontend (cobertura de testes, sync de precos) sao esforcos continuos e nao foram contabilizados em horas fixas.*

### Custo de NAO RESOLVER (Risco Acumulado)

| Risco | Probabilidade | Impacto | Custo Potencial |
|-------|:---:|:---:|-----------------|
| **Brecha de seguranca** por colisao de tokens (SYS-004, CVSS 9.1) — acesso indevido a dados de usuarios | Alta | Critico | R$ 150.000 - R$ 500.000 (LGPD + reputacao + perda de clientes) |
| **Falha silenciosa na busca** — API PNCP rejeita requisicoes com >50 resultados/pagina sem erro claro (SYS-003) | Alta | Alto | R$ 30.000 - R$ 80.000 (usuarios nao encontram licitacoes, churn) |
| **Classificacao IA incorreta** — 20-30% das respostas truncadas geram classificacoes erradas (SYS-002) | Alta | Alto | R$ 20.000 - R$ 50.000 (perda de confianca, oportunidades perdidas) |
| **Instabilidade do servidor** — crashes por SIGSEGV em producao (SYS-001) | Media | Alto | R$ 15.000 - R$ 40.000 (downtime, SLA, reputacao) |
| **Crescimento descontrolado do banco** — sem limpeza automatica de dados expirados (DB-NEW-03) | Media | Medio | R$ 5.000 - R$ 15.000/ano (custos de storage Supabase) |
| **Perda de produtividade** — arquivos monoliticos (filter.py 177KB, buscar/page.tsx 983 linhas) dificultam manutencao | Alta | Medio | R$ 30.000 - R$ 60.000/ano (velocidade de desenvolvimento 30-40% menor) |
| **Vulnerabilidade CSP** — scripts inline sem nonce permitem potencial XSS (FE-010) | Baixa | Alto | R$ 50.000 - R$ 200.000 (se explorada: LGPD + dados) |

**Custo potencial de nao agir: R$ 300.000 - R$ 945.000** (acumulado em 12 meses, considerando probabilidades)

**Custo ponderado por probabilidade: ~R$ 180.000**

---

## Impacto no Negocio

### Performance

A plataforma atualmente opera com limitacoes que afetam diretamente a experiencia de busca. A integracao com a API PNCP (fonte primaria de dados) pode falhar silenciosamente quando o volume de resultados excede o novo limite imposto pelo governo (reduzido de 500 para 50 em fevereiro/2026). Isso significa que **usuarios podem estar perdendo licitacoes relevantes sem saber**. Alem disso, o modelo de IA tem um timeout de 15 segundos — 5 vezes acima do tempo medio de resposta — criando risco de travamento quando o servico da OpenAI fica lento. Resolver estes pontos garante que 100% das licitacoes disponiveis sejam capturadas e que o sistema responda de forma previsivel mesmo sob carga.

### Seguranca

Foram identificadas **2 vulnerabilidades criticas de seguranca**: um problema na geracao de tokens de autenticacao que pode permitir colisao entre sessoes de usuarios diferentes (classificacao CVSS 9.1 — severidade maxima), e a necessidade de modernizar o algoritmo de assinatura JWT de HS256 para ES256 (padrao atual da industria). Ambos os itens devem ser resolvidos antes de escalar a base de usuarios para proteger dados sensiveis de licitacoes e manter conformidade com a LGPD. A politica de seguranca de conteudo (CSP) do frontend tambem precisa de reforco para prevenir ataques de injecao de scripts.

### Experiencia do Usuario

A experiencia do usuario e funcional, mas tem pontos de fragilidade. **Quatro paginas principais** (dashboard, pipeline, historico, conta) nao possuem tratamento de erro — se qualquer componente falhar, a pagina inteira fica em branco sem mensagem explicativa. A acessibilidade (A11Y) esta parcialmente implementada: 15+ componentes ja possuem suporte a leitores de tela, mas ainda faltam anuncios de erro, indicadores de carregamento acessiveis e consistencia na navegacao por teclado. Melhorar estes pontos reduz abandono e amplia o publico potencial (incluindo compliance com normas de acessibilidade digital).

### Velocidade de Desenvolvimento

A base de codigo tem areas de alta complexidade que impactam a velocidade de entrega de novas funcionalidades. O arquivo principal de filtros (`filter.py`) tem 177KB e a pagina de busca (`buscar/page.tsx`) tem 983 linhas — ambos dificeis de modificar sem efeitos colaterais. A estrutura monolitica do backend (`main.py`) e a coexistencia de dois diretorios de componentes no frontend geram confusao e retrabalho. **Estimamos que resolver os debitos de arquitetura (Fases 3-4) aumentaria a velocidade de desenvolvimento em 25-35%**, permitindo entregar novas funcionalidades mais rapido e com menos bugs.

---

## Timeline Recomendado

### Fase 1: Quick Wins (1-2 semanas)

Resolucao de 12 itens de baixo esforco e alto impacto relativo. Inclui verificacoes de integridade no banco de dados, criacao de rotinas automaticas de limpeza de dados expirados, correcoes de acessibilidade pontuais e otimizacoes de dependencias.

| Item | Descricao em linguagem de negocio | Horas |
|------|-----------------------------------|:---:|
| Verificacao de integridade do banco (2 itens) | Confirmar que as relacoes entre tabelas estao validas em producao | 1h |
| Limpeza automatica de dados expirados | Prevenir crescimento desnecessario do banco (economia em storage) | 0.5h |
| Restricoes de dados em 3 tabelas | Garantir que dados invalidos nao entrem no sistema | 2h |
| Remocao de indice duplicado | Melhorar velocidade de escrita no banco | 0.5h |
| Correcoes de acessibilidade (2 itens) | Tornar mensagens de erro e carregamento visiveis para leitores de tela | 1h |
| Otimizacao de carregamento (1 componente) | Reduzir em 70KB o tamanho do dashboard (carrega mais rapido) | 0.5h |
| Rastreamento de alteracoes (2 tabelas) | Saber quando registros foram modificados pela ultima vez | 1h |

**Custo Fase 1: ~7h = R$ 1.050**
**ROI imediato:** Economia de storage, banco mais integro, paginas mais rapidas.

### Fase 2: Fundacao (3-4 semanas)

Resolucao dos 5 debitos criticos e 7 de alta prioridade. Foco em seguranca, estabilidade e confiabilidade do core do produto.

| Item | Descricao em linguagem de negocio | Horas |
|------|-----------------------------------|:---:|
| Correcao de seguranca em tokens (SYS-004) | Eliminar risco de um usuario acessar dados de outro | 4h |
| Estabilidade do servidor (SYS-001) | Eliminar crashes silenciosos em producao | 4h |
| Qualidade da IA (SYS-002) | Aumentar taxa de classificacao correta de ~70% para >99% | 4h |
| Modernizacao de autenticacao (SYS-005) | Adotar padrao ES256 (mais seguro, padrao da industria) | 8h |
| Correcao da integracao PNCP (SYS-003) | Garantir captura de 100% das licitacoes disponiveis | 8h |
| Resiliencia da IA (SYS-010 + SYS-012) | Prevenir travamentos quando servico de IA fica lento | 8h |
| Padronizacao do banco (DB-001) | Garantir integridade referencial em todas as tabelas | 6h |
| Tratamento de erros nas paginas (FE-NEW-02) | Usuarios verao mensagem util em vez de tela em branco | 4h |

**Custo Fase 2: ~46h = R$ 6.900**
**ROI imediato:** Zero vulnerabilidades criticas, busca confiavel, IA precisa.

### Fase 3: Otimizacao (5-8 semanas)

Melhorias de seguranca avancada, refatoracao de codigo para facilitar manutencao, implementacao de testes de acessibilidade automatizados e contratos de API.

| Tema | Descricao | Horas |
|------|-----------|:---:|
| Seguranca avancada (CSP) | Protecao contra injecao de scripts maliciosos | 14h |
| Refatoracao da busca | Simplificar codigo da pagina principal (facilita novas funcionalidades) | 18h |
| Organizacao de componentes | Estrutura clara para desenvolvimento frontend | 7h |
| Otimizacao de carregamento | Paginas carregam mais rapido (lazy loading de bibliotecas) | 11h |
| Testes de acessibilidade automatizados | Garantir conformidade A11Y em cada deploy | 8h |
| Contrato de API | Detectar automaticamente mudancas que quebram integracoes | 4h |
| Arquitetura backend | Separar modulos para facilitar manutencao | 16h |
| Migracao de bibliotecas | Modernizar dependencias (requests -> httpx) | 16h |
| Melhorias no pipeline de dados | Enriquecimento de resultados + observabilidade | 20h |
| Refatoracao frontend avancada | Resolver pendencias estruturais | 16h |
| Limpeza de testes | Confiabilidade do suite de testes de integracao | 4h |

**Custo Fase 3: ~134h = R$ 20.100**
**ROI:** Velocidade de desenvolvimento +25%, seguranca reforçada, manutencao facilitada.

### Fase 4: Excelencia (9-12 semanas)

Investimentos de longo prazo em qualidade, cobertura de testes, arquitetura sustentavel e features que preparam o produto para escala.

| Tema | Descricao | Horas |
|------|-----------|:---:|
| Simplificacao do streaming (SSE) | Reduzir complexidade do sistema de atualizacoes em tempo real | 22h |
| Decomposicao do filtro | Separar arquivo monolitico de 177KB em modulos gerenciaveis | 16h |
| Cobertura de testes frontend | Atingir meta de 60% de cobertura (atualmente ~50%) | 38h |
| Testes end-to-end | Cobrir fluxos criticos: pagamento, pipeline, mobile | 40h |
| Migracao de billing legado | Limpar codigo antigo de cobranca | 4h |
| Resiliencia de rede | Ajustar circuit breakers e tolerancia a falhas | 12h |
| Autenticacao multi-fator (MFA) | Seguranca adicional para contas de usuario | 16h |
| Itens diversos P3/P4 | Limpeza de codigo, convencoes, documentacao | 80h |

**Custo Fase 4: ~228h = R$ 34.200**
**ROI:** Produto sustentavel para escala, time de desenvolvimento produtivo, qualidade enterprise.

---

## ROI da Resolucao

| Investimento | Retorno Esperado |
|--------------|------------------|
| R$ 51.000 (resolucao completa) | R$ 180.000+ em riscos evitados (ponderado por probabilidade) |
| ~340 horas de engenharia | +25-35% de velocidade de desenvolvimento |
| 8-12 semanas | Produto sustentavel e seguro para escala |
| R$ 7.950 (Fases 1-2 apenas) | Eliminacao de 100% dos riscos criticos |

**ROI Estimado da resolucao completa: 3.5:1**

**ROI das Fases 1-2 (investimento minimo): 15:1** — com apenas R$ 7.950, eliminam-se os riscos mais graves que sozinhos poderiam custar R$ 120.000+.

### Comparativo Visual

```
Cenario A: Resolver tudo (R$ 51.000)
  → Riscos evitados: R$ 180.000+
  → Ganho de produtividade: R$ 30.000-60.000/ano
  → Economia de infraestrutura: R$ 5.000-15.000/ano
  → TOTAL RETORNO ANO 1: R$ 215.000+

Cenario B: Resolver apenas P0+P1 (R$ 7.950)
  → Riscos criticos evitados: R$ 120.000+
  → Debitos restantes acumulam juros tecnicos

Cenario C: Nao resolver (R$ 0 investimento)
  → Risco acumulado em 12 meses: R$ 180.000+
  → Velocidade de desenvolvimento: -30-40%
  → Possivel incidente de seguranca com impacto LGPD
```

---

## Proximos Passos

1. [ ] Aprovar orcamento de **R$ 7.950** para Fases 1-2 (minimo recomendado)
2. [ ] Aprovar orcamento total de **R$ 51.000** para resolucao completa (recomendado)
3. [ ] Executar diagnosticos SQL em producao (pre-requisito tecnico, 1h)
4. [ ] Estabelecer baselines de testes (pre-requisito tecnico, 2h)
5. [ ] Alocar time tecnico para Sprint de Seguranca (Fase 2, itens P0)
6. [ ] Iniciar Fase 1 — Quick Wins (7h de trabalho, impacto imediato)
7. [ ] Revisar progresso e aprovar Fases 3-4 apos conclusao das Fases 1-2

---

## Anexos

- [Assessment Tecnico Completo](../prd/technical-debt-assessment.md)
- [Revisao Database](../reviews/db-specialist-review.md)
- [Revisao UX](../reviews/ux-specialist-review.md)
- [Revisao QA](../reviews/qa-review.md)

---

*Documento preparado pela Equipe de Engenharia — SmartLic/CONFENGE*
*Baseado em auditoria tecnica de 10 fases com 4 especialistas, validada contra o codebase em producao.*
