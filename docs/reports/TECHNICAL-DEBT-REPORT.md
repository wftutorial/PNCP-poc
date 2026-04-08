# Relatorio de Debito Tecnico — SmartLic

**Projeto:** SmartLic — Inteligencia em Licitacoes
**Empresa:** CONFENGE Avaliacoes e Inteligencia Artificial LTDA
**Data:** 2026-04-08
**Versao:** 2.0
**Elaborado por:** @analyst (Alex) — Fase 9, Brownfield Discovery
**Base:** Assessment Tecnico Final v2.0 (61 debitos, 5 fases, revisado por 4 especialistas)

---

## Executive Summary

### Situacao Atual

O SmartLic esta em producao com usuarios reais, mais de 5.100 testes automatizados no backend e 2.600 no frontend, resiliencia multi-camada (circuit breakers, cache SWR, degradacao graciosa) e observabilidade completa (Prometheus + Sentry + OpenTelemetry). Quatro debitos criticos ja foram resolvidos durante a propria avaliacao (worker health, async search, fork-safety, single-worker), demonstrando capacidade de execucao. A base tecnica e funcional e o produto entrega valor diariamente.

Entretanto, a transicao acelerada de POC para producao acumulou 57 debitos tecnicos ativos em quatro areas: sistema/backend, banco de dados, interface/UX e qualidade/seguranca. Os riscos mais urgentes sao operacionais: o **Supabase esta no tier gratuito com limite de 500MB contra um datalake que cresce para ~3GB**, indices criticos estao ausentes (impactando performance de busca em ate 70%), e quatro tabelas crescem sem limite por falta de politicas de retencao. Essas tres questoes, se nao tratadas nas proximas semanas, podem causar **parada total do sistema de busca**.

A boa noticia: o caminho critico (P0) exige apenas **~9 horas de trabalho**. Com um investimento de R$ 1.350, os quatro riscos de parada operacional sao eliminados. O plano completo de cinco fases distribui o esforco ao longo de 20 semanas, com retorno incremental a cada fase.

### Numeros Chave

| Metrica | Valor |
|---------|-------|
| Total de Debitos Identificados | 61 |
| Debitos Ativos | 57 |
| Debitos Resolvidos (monitoramento) | 4 |
| Debitos Criticos (P0) | 4 |
| Debitos de Alta Prioridade (P1) | 12 |
| Esforco Total (Fases 1-4) | 100-130 horas |
| Esforco Backlog (Fase 5) | 150-250 horas |
| Custo Estimado (Fases 1-4) | R$ 15.000 - R$ 19.500 |
| Custo do Critical Path (P0) | R$ 1.350 (~9h) |
| Especialistas na Avaliacao | 4 (arquiteto, DBA, UX, QA) |

### Recomendacao

Aprovar imediatamente a execucao da **Fase 1 — Quick Wins (R$ 1.500, ~10 horas, 1 semana)** para eliminar o risco de esgotamento de armazenamento do banco de dados (que pode derrubar toda a plataforma), criar o indice que acelera buscas em 50-70%, estabelecer politicas de limpeza automatica nas 4 tabelas que crescem sem controle, e corrigir alvos de toque em componentes usados em todos os cartoes de resultado. Esses itens tem retorno operacional imediato e previnem a **cascata de falhas mais provavel**: banco cheio -> ingesta falha -> busca retorna resultados vazios -> usuarios abandonam.

---

## Analise de Custos

### Custo de RESOLVER

| Categoria | Debitos Ativos | Horas (Fases 1-4) | Custo (R$150/h) |
|-----------|---------------|-------------------|-----------------|
| Sistema/Backend | 14 | ~40h | R$ 6.000 |
| Banco de Dados | 18 | ~22h | R$ 3.300 |
| Frontend/UX | 21 | ~48h | R$ 7.200 |
| Cross-Cutting/QA | 6 | ~25h | R$ 3.750 |
| **TOTAL (Fases 1-4)** | **57** | **~120h** | **R$ 18.000** |
| Backlog (Fase 5) | incl. acima | ~200h | R$ 30.000 |
| **TOTAL GERAL** | **57** | **~320h** | **R$ 48.000** |

*Nota: A Fase 5 inclui itens de longo prazo como internacionalizacao (100h), suporte offline (50h) e Storybook (28h), que so fazem sentido se houver demanda ou crescimento da equipe. O investimento obrigatorio real e o das Fases 1-4.*

### Custo de NAO RESOLVER (Risco Acumulado)

| Risco | Probabilidade | Impacto | Custo Potencial |
|-------|---------------|---------|-----------------|
| **Esgotamento de armazenamento Supabase FREE (500MB)** — ingesta para, busca retorna vazio, usuarios abandonam | Muito Alta (semanas) | Critico | R$ 30.000 - R$ 50.000 (perda de todos os trials ativos + reputacao) |
| **Perda de dados sem backup independente** — se Supabase tiver incidente, nao ha recuperacao | Media | Critico | R$ 50.000+ (reconstrucao completa + perda de dados de clientes) |
| **Busca lenta por falta de indice** — cada busca consome 2-3x mais recursos que o necessario | Certa | Alto | R$ 5.000/ano (custo computacional extra + degradacao de experiencia) |
| **Tabelas sem limpeza atingem limites** — stripe_webhook_events, alert_sent, health_checks crescem indefinidamente | Alta (6 meses) | Medio | R$ 3.000 - R$ 8.000 (degradacao de performance, downtime para remediar) |
| **Falha de ingesta silenciosa** — crawler diario falha sem alerta, dados ficam defasados sem que ninguem saiba | Media | Alto | R$ 10.000 - R$ 20.000/ano (oportunidades de licitacao perdidas pelos clientes) |
| **Vulnerabilidade de seguranca (service_role tokens)** — uso de token administrativo para operacoes de usuario | Baixa | Alto | R$ 20.000 - R$ 50.000 (multa LGPD + remediacao de emergencia) |
| **Hooks de busca com 3.775 linhas** — qualquer mudanca na pagina de busca exige entender codigo altamente acoplado | Certa | Medio | +40% tempo de desenvolvimento = ~R$ 3.600/feature x 8 features/ano = R$ 28.800/ano |
| **Experiencia mobile degradada** — scroll travado no SSE, alvos de toque pequenos, conteudo cortado pelo menu | Alta | Medio | R$ 15.000/ano (churn de usuarios mobile, ~30% do trafego) |

**Custo potencial acumulado de nao agir: R$ 161.800 - R$ 229.800/ano**

---

## Impacto no Negocio

### Performance

**Estado atual:** O indice mais importante do banco de dados (busca por UF + modalidade + data de publicacao) nao existe. Cada consulta ao datalake faz uma varredura completa, consumindo 2-3x mais tempo e recursos. Alem disso, linhas marcadas como inativas (`is_active=false`) nunca sao removidas, causando inchacho progressivo.

**Apos resolucao (Fase 1):** Reducao de 50-70% na latencia da busca principal. Tabelas mantidas automaticamente com politicas de retencao. Monitoramento de tamanho do banco ativo.

**Impacto no negocio:** Buscas mais rapidas significam usuarios mais satisfeitos e maior conversao de trials para pagantes. A busca e o coracao do produto — cada milissegundo conta.

### Seguranca

**Estado atual:** O backend usa `service_role` (token administrativo com acesso total) para operacoes que deveriam usar tokens por usuario. As politicas de seguranca por linha (RLS) mitigam o risco, mas a arquitetura nao atenderia uma auditoria formal. Adicionalmente, nao ha auditoria das funcoes RPC quanto a validacao de `auth.uid()`, e nao existe varredura de vulnerabilidades em dependencias no CI.

**Apos resolucao (Fases 1-2):** Auditoria completa de RPCs (TD-059 na Fase 1), migracao para tokens por usuario (TD-005 na Fase 5, escopo definido pela auditoria), varredura automatica de dependencias em cada pull request (TD-058 na Fase 4).

**Impacto no negocio:** Requisito para apresentar o produto a grandes empresas e orgaos publicos. Pre-condicao para certificacoes de seguranca. Protecao contra multas LGPD.

### Experiencia do Usuario

**Estado atual:** No mobile, o scroll trava durante atualizacoes em tempo real da busca (SSE). Os botoes de feedback sao menores (28x28px) que o minimo recomendado (44x44px), dificultando o toque. O menu inferior cobre conteudo em varias paginas. Cinco implementacoes diferentes de tratamento de erro geram inconsistencia visual.

**Apos resolucao (Fases 1-3):** Touch targets em conformidade com WCAG AA em todos os componentes de resultado. Scroll suave durante SSE via `useDeferredValue`. Experiencia mobile equivalente a desktop. Padroes de erro unificados.

**Impacto no negocio:** ~30% do trafego e mobile. Cada problema de UX e um potencial trial perdido. Conformidade com acessibilidade e obrigacao legal (Lei 13.146/2015).

### Manutenibilidade

**Estado atual:** O backend tem 3 arquivos com mais de 1.300 linhas cada (`quota.py` com 1.660, `consolidation.py` com 1.394, `llm_arbiter.py` com 1.362). No frontend, os hooks da pagina de busca somam 3.775 linhas em 13 arquivos interconectados. Isso significa que qualquer mudanca na busca — a funcionalidade central do produto — exige entender milhares de linhas de codigo acoplado.

**Apos resolucao (Fases 2-3):** Nenhum modulo acima de 500 linhas. Hooks de busca abaixo de 2.500 linhas totais. Novos desenvolvedores produtivos em dias, nao semanas.

**Impacto no negocio:** Reducao de ~30% no tempo de implementacao de novas funcionalidades. Menor risco de bugs em producao. Capacidade de escalar a equipe sem gargalos de onboarding.

---

## Timeline Recomendado

### Fase 1: Quick Wins (Semana 1-2) — ~10h, R$ 1.500

**Objetivo:** Eliminar riscos de parada operacional e corrigir problemas de alto impacto com baixo esforco.

| Item | O que resolve | Horas | Impacto |
|------|---------------|-------|---------|
| **Upgrade Supabase para Pro** (TD-033) | Banco no tier gratuito (500MB) vs datalake de ~3GB — risco de parada total | 0.5h | Elimina risco #1 de queda do sistema |
| **Indice composto de busca** (TD-019) | Busca no datalake sem indice otimizado | 1h | 50-70% de reducao na latencia de busca |
| **Limpeza de dados inativos** (TD-020) | Linhas soft-deleted nunca removidas, inchacho crescente | 3h | Banco mais enxuto, queries mais rapidas |
| **4 politicas de retencao** (TD-025/026/027/NEW-001) | Webhooks Stripe, alertas, emails de trial e health_checks crescem sem limite | 2h | Previne saturacao do banco em 6 meses |
| **Touch targets nos botoes de feedback** (TD-052) | Alvos de toque de 28px (minimo: 44px) em cada cartao de resultado | 1.5h | Melhoria imediata de usabilidade mobile |
| **Tamanho minimo de texto** (TD-053) | Texto de 10px abaixo do minimo legivel em mobile | 0.5h | Legibilidade em dispositivos pequenos |
| **Auditoria de seguranca RPC** (TD-059) | Funcoes de banco sem validacao de usuario verificada | 4h | Define escopo real das correcoes de seguranca |

**Resultado:** Risco de parada eliminado. Busca 50-70% mais rapida. Banco com crescimento controlado. Conformidade basica de acessibilidade mobile. Escopo de seguranca definido.

### Fase 2: Fundacao (Semanas 3-6) — ~16h, R$ 2.400

**Objetivo:** Estabelecer fundacao operacional robusta — backup, alertas e correcoes estruturais.

| Item | O que resolve | Horas | Impacto |
|------|---------------|-------|---------|
| **Backup semanal + PITR** (TD-034) | Sem backup independente — risco de perda total | 2h | Recuperacao garantida em caso de desastre |
| **Limpeza de soft-deletes + investigacao** (TD-020/NEW-002) | Funcao de purge ignora linhas inativas | 3h | Banco limpo e funcao corrigida |
| **Integridade plan_type** (TD-021) | Tipo de plano sem chave estrangeira — risco de dados orfaos | 4h | Integridade referencial garantida |
| **Alertas de falha de ingesta** (TD-061) | Crawler diario pode falhar silenciosamente — dados ficam defasados | 3h | Equipe notificada imediatamente sobre falhas |
| **Alert cron assincrono** (TD-029) | Envio sequencial de 1000 alertas leva 60-100s | 2h | Alertas enviados em ~10s |
| **Alinhamento de timeouts** (TD-015) | Railway mata requests em 120s mas Gunicorn espera 180s — morte silenciosa | 2h | Erros rastreados no Sentry em vez de desaparecer |

**Resultado:** Backup operacional. Alertas de falha de ingesta. Timeouts alinhados. Integridade de dados.

### Fase 3: Hardening (Semanas 5-8) — ~54h, R$ 8.100

**Objetivo:** Refatorar codigo complexo que impede velocidade de desenvolvimento.

| Trilha | O que resolve | Horas | Impacto |
|--------|---------------|-------|---------|
| **Frontend: Decomposicao de hooks de busca** (TD-050 + TD-035) | 2 hooks com 1.459 linhas combinadas -> modulos menores | 32h | Mudancas na busca 40% mais rapidas |
| **Frontend: Filtros salvos** (TD-037) | Usuarios avancados reconfiguram filtros a cada sessao | 22h | Feature solicitada por consultorias — valor direto |
| **Backend: Decomposicao de modulos** (TD-007 + TD-008) | quota.py (1.660 LOC) + consolidation.py (1.394 LOC) | 20h | Manutencao 30% mais rapida |

**Resultado:** Nenhum hook acima de 400 linhas. Nenhum modulo backend acima de 600 linhas. Feature de filtros salvos para power users.

### Fase 4: Polish (Semanas 9-12) — ~44h, R$ 6.600

**Objetivo:** Qualidade automatizada e protecao contra regressoes.

| Item | O que resolve | Horas | Impacto |
|------|---------------|-------|---------|
| **Testes de regressao visual** (TD-036) | Sem protecao visual — mudancas de CSS podem quebrar layout | 18h | 10 telas criticas protegidas |
| **Testes de acessibilidade automatizados** (TD-056) | 0% de cobertura automatizada de acessibilidade | 14h | 80%+ dos top 10 componentes verificados |
| **Varredura de vulnerabilidades** (TD-058) | Dependencias nao auditadas contra CVEs conhecidas | 4h | 0 vulnerabilidades criticas em CI |
| **Decomposicao llm_arbiter.py** (TD-009) | 1.362 linhas de classificacao IA em arquivo unico | 8h | Pipeline de IA modular e testavel |

**Resultado:** Regressoes visuais detectadas automaticamente. Acessibilidade verificada em CI. Dependencias auditadas. Pipeline de IA modular.

### Fase 5: Long-term (Semanas 13-20) — ~200h, R$ 30.000

**Objetivo:** Itens de backlog executados conforme demanda e crescimento.

| Item | O que resolve | Horas | Gatilho |
|------|---------------|-------|---------|
| **Squash de 121 migracoes** (TD-016) | Ambientes novos levam 2-3 min para setup | 24h | Apos TODAS as migracoes das Fases 1-4 |
| **Tokens por usuario** (TD-005) | Substituir service_role por tokens individuais | 16h | Apos auditoria TD-059 definir escopo |
| **Documentacao de hooks** (TD-051) | 3.775 linhas sem documentacao de arquitetura | 16h | Quando novo dev FE entrar |
| **Auto-scaling** (TD-011) | Scaling manual no Railway | 4h | Quando trafego exceder 200 buscas/dia |
| **Scroll mobile** (TD-046) | SSE causa jank no scroll | 10h | Quando trafego mobile crescer |
| **Storybook** (TD-043) | 65+ componentes sem catalogo visual | 28h | Quando equipe FE crescer para 3+ devs |
| **i18n + offline** (TD-048/049) | Internacionalizacao e suporte offline | 150h | Sem demanda atual — adiado indefinidamente |

**Resultado:** Itens executados sob demanda, sem custo desnecessario.

---

## ROI da Resolucao

### Investimento vs Retorno

| Investimento | Retorno Esperado |
|-------------|-----------------|
| R$ 18.000 (resolucao Fases 1-4) | R$ 161.800 - R$ 229.800 em riscos evitados (ano 1) |
| 120 horas de trabalho tecnico | +30% velocidade de desenvolvimento permanente |
| 12 semanas de execucao | Produto sustentavel e escalavel |

### Retorno por Fase

| Fase | Investimento | Retorno Direto |
|------|-------------|----------------|
| Fase 1 (Quick Wins) | R$ 1.500 | Previne parada total do sistema (valor: R$ 30.000-50.000) |
| Fase 2 (Fundacao) | R$ 2.400 | Backup + alertas (valor: R$ 50.000+ em desastre evitado) |
| Fase 3 (Hardening) | R$ 8.100 | -30% tempo de dev + feature de filtros salvos |
| Fase 4 (Polish) | R$ 6.600 | Protecao automatizada contra regressoes |

### Analise de Payback

| Metrica | Valor |
|---------|-------|
| Investimento Fases 1-4 | R$ 18.000 |
| Riscos evitados (conservador, ano 1) | R$ 161.800 |
| Economia de velocidade de dev (ano 1) | R$ 28.800 |
| **Payback** | **< 2 meses** |
| **ROI Fases 1-4 (conservador)** | **9:1** |

A Fase 1 sozinha (R$ 1.500) previne riscos de R$ 30.000-50.000. O ROI isolado da Fase 1 e de **20:1 a 33:1**.

---

## Riscos Cruzados (Cascatas)

Os debitos nao sao independentes. Seis cenarios de cascata foram identificados onde debitos em areas diferentes se amplificam mutuamente:

| # | Cenario de Cascata | Debitos Envolvidos | Severidade | Mitigacao |
|---|--------------------|--------------------|------------|-----------|
| 1 | **Banco cheio -> ingesta falha -> busca vazia -> usuarios abandonam** | TD-033 + TD-020 + TD-025/026/027 | Critico | Fase 1: upgrade + retencao. **Executar esta semana.** |
| 2 | **Request morre silenciosamente** — Railway mata em 120s, Gunicorn espera 180s, Sentry nao captura | TD-015 + TD-011 | Alto | Fase 2: alinhar timeouts + middleware de deteccao |
| 3 | **Perda de dados sem recuperacao** — sem PITR, sem backup independente, tier gratuito | TD-034 + TD-033 | Alto | Fase 1 (Pro) + Fase 2 (pg_dump + PITR) |
| 4 | **Cliff de manutenibilidade na busca** — 3.775 linhas de hooks acoplados | TD-035 + TD-050 + TD-051 | Medio | Fase 3: refatoracao ordenada |
| 5 | **Nao passa auditoria de seguranca** — service_role + RLS sem documentacao + RPCs sem verificacao | TD-005 + TD-030 + TD-059 | Medio | Fase 1 (auditoria) -> Fase 5 (migracao) |
| 6 | **UX mobile degradada** — scroll travado + toque dificil + conteudo cortado | TD-046 + TD-052 + TD-047/055 | Medio | Fase 1 (touch) + Fase 5 (scroll) |

---

## Proximos Passos

1. [ ] **Aprovar Fase 1** (R$ 1.500, ~10h) — inicio imediato
2. [ ] **Upgrade Supabase para tier pago** (URGENTE — P0, TD-033) — executar esta semana
3. [ ] **Alocar desenvolvedor** para execucao da Fase 1 (1 semana)
4. [ ] **Executar Fase 1** — indice, retencao, touch targets, auditoria RPC
5. [ ] **Validar resultados** — latencia de busca (EXPLAIN ANALYZE), tamanho do banco (pg_database_size), politicas de retencao ativas
6. [ ] **Aprovar Fase 2** (R$ 2.400, ~16h) — backup e fundacao operacional
7. [ ] **Aprovar Fase 3** (R$ 8.100, ~54h) — refatoracao de codigo + filtros salvos
8. [ ] **Aprovar Fase 4** (R$ 6.600, ~44h) — qualidade automatizada
9. [ ] **Revisar backlog** (Fase 5) trimestralmente — executar sob demanda

---

## Anexos

- [Assessment Tecnico Completo](../prd/technical-debt-assessment.md) — 61 debitos detalhados, grafo de dependencias, matriz de priorizacao, criterios de sucesso
- [Review Database](../reviews/db-specialist-review.md) — validacao especialista de debitos de banco por @data-engineer
- [Review Frontend/UX](../reviews/ux-specialist-review.md) — validacao especialista de debitos de interface por @ux-design-expert
- [QA Review](../reviews/qa-review.md) — aprovacao final com condicoes bloqueantes atendidas

---

*Documento gerado como parte do processo de Brownfield Discovery (10 fases). Este relatorio representa a Fase 9 — sintese executiva para tomada de decisao. Versao 2.0 incorpora o Assessment Final v2.0 revisado por 4 especialistas em 2026-04-08.*
