# Relatório de Débito Técnico — SmartLic

**Projeto:** SmartLic (smartlic.tech)
**Data:** 2026-03-21
**Versão:** 2.0
**Preparado por:** AIOS Technical Assessment Team
**Classificação:** Interno — Diretoria e Gestão de Produto

---

## Executive Summary

### Situação Atual

O SmartLic é a plataforma de inteligência em licitações públicas da CONFENGE, que automatiza a descoberta, análise e qualificação de oportunidades para empresas que vendem ao governo. O produto está em produção como POC avançado (v0.5), operando em fase beta com trials gratuitos de 14 dias e modelo de assinatura SmartLic Pro a partir de R$1.599/mês. A URL pública é smartlic.tech.

A plataforma já funciona — possui busca multi-fonte, classificação por inteligência artificial, pipeline de oportunidades e geração de relatórios. Porém, o ritmo acelerado de desenvolvimento para atingir o mercado primeiro resultou em acúmulo de débito técnico: arquivos monolíticos que dificultam manutenção, lacunas de acessibilidade que excluem usuários com deficiência, e pontos cegos de testes que elevam o risco de introduzir defeitos em cada nova funcionalidade.

Esta avaliação foi conduzida por quatro especialistas (arquitetura, banco de dados, experiência do usuário e qualidade) e identificou 76 itens de débito técnico. O objetivo é dar visibilidade ao custo de resolver versus o custo de não resolver, permitindo uma decisão informada sobre investimento.

### Números Chave

| Métrica | Valor |
|---------|-------|
| Total de Débitos Identificados | 76 |
| Débitos Acionáveis | 69 |
| Débitos Críticos (risco imediato) | 4 |
| Débitos de Alta Prioridade | 14 |
| Esforço Total Estimado | ~259 horas |
| Custo Estimado de Resolução | R$ 38.850 |
| Timeline Estimado | 13 semanas |
| Quick Wins Disponíveis (< 4h cada) | 22 itens, ~30h |

### Recomendação

Recomendamos a **Opção B (Resolução Parcial)** — investir R$ 12.863 em 5 semanas para resolver os 33 itens mais críticos (Waves 0, 1 e 2), mitigando aproximadamente 85% do risco acumulado com 33% do investimento total. A reestruturação profunda (Waves 3-4) pode ser intercalada com desenvolvimento de funcionalidades ao longo dos meses seguintes.

---

## Análise de Custos

### Custo de RESOLVER

| Wave | Descrição | Itens | Horas | Custo (R$150/h) | Timeline |
|------|-----------|-------|-------|-----------------|----------|
| Wave 0 | Rede de Segurança (testes) | 6 | 24h | R$ 3.600 | 1 semana |
| Wave 1 | Quick Wins + Correções Críticas | 15 | 26,25h | R$ 3.938 | 2 semanas |
| Wave 2 | Alta Prioridade | 12 | 35,5h | R$ 5.325 | 2 semanas |
| Wave 3 | Reestruturação de Código | 11 | 76h | R$ 11.400 | 4 semanas |
| Wave 4 | Polimento e Otimização | 25 | 97h | R$ 14.550 | 4 semanas |
| **TOTAL** | | **69** | **~259h** | **R$ 38.850** | **13 semanas** |

**Nota:** Wave 0 e Wave 1 podem rodar em paralelo (semanas 1-3). Wave 4 pode ser intercalada com desenvolvimento de novas funcionalidades.

### Custo de NÃO RESOLVER (Risco Acumulado em 12 Meses)

| Risco | Probabilidade | Impacto | Custo Potencial (12 meses) |
|-------|---------------|---------|---------------------------|
| **Exclusão de dados de conta incompleta** — deleção de conta sem transação pode deixar dados órfãos, gerando reclamações LGPD | 30% | R$ 50.000 | R$ 15.000 |
| **Inacessibilidade digital** — formulário principal sem ARIA, navegação por teclado quebrada. Risco de processos (LBI 13.146/2015) e perda de clientes B2G que exigem conformidade | 25% | R$ 80.000 | R$ 20.000 |
| **Drift de cobrança** — status de assinatura rastreado em dois lugares sem sincronização. Cliente pagante perde acesso ou inadimplente mantém acesso | 20% | R$ 30.000 | R$ 6.000 |
| **Perda de produtividade do time** — arquivos monolíticos (3.800+ linhas) causam conflitos, onboarding lento de novos devs, e tempo gasto navegando código | 90% | R$ 45.000 | R$ 40.500 |
| **Regressões em produção** — módulos críticos sem testes (cron jobs, circuit breaker, filtros) significam que mudanças podem quebrar funcionalidades silenciosamente | 40% | R$ 25.000 | R$ 10.000 |
| **Fonte de dados morta consumindo recursos** — ComprasGov v3 fora do ar desde março/2026 mas ainda ativa no pipeline, gerando timeouts desnecessários | 80% | R$ 5.000 | R$ 4.000 |

**Custo potencial de não agir em 12 meses: R$ 95.500**

Isto representa 2,5x o custo de resolução total (R$ 38.850). Mesmo considerando que nem todos os riscos se materializarão simultaneamente, a expectativa matemática de perdas supera significativamente o investimento de correção.

---

## Impacto no Negócio

### Segurança e Compliance

Foram identificados **4 itens críticos** que afetam diretamente a segurança e conformidade legal do produto:

- **Deleção de conta não é atômica** — Se o processo de exclusão de conta falhar no meio, dados parciais ficam no banco. Com a LGPD em vigor, qualquer reclamação de titular pode expor a empresa a sanções da ANPD.
- **Política de acesso ausente em tabela de emails** — A tabela `trial_email_log` tem controle de acesso habilitado mas sem regras definidas, o que pode permitir acesso indevido a dados de comunicação com usuários.
- **Dependência com padrão duplicado** — O cliente principal de dados (PNCP) usa simultaneamente duas bibliotecas de comunicação, uma síncrona e outra assíncrona, criando superfície de ataque desnecessária e comportamento imprevisível.

**Custo de correção: R$ 6.000 (Wave 1) | Risco se não corrigir: multas LGPD podem chegar a 2% do faturamento ou R$ 50M por infração**

### Experiência do Usuário

A auditoria de acessibilidade revelou que a **página principal do produto (busca) é invisível para tecnologias assistivas** — leitores de tela não conseguem identificar o formulário de busca. Adicionalmente:

- Navegação por teclado está quebrada em todas as páginas protegidas (dashboard, pipeline, histórico)
- Formulário de login não comunica erros de validação para leitores de tela
- Páginas de conversão (cadastro, onboarding, planos) não possuem recuperação de erro — um crash exibe tela branca

Para um produto B2G, acessibilidade não é diferencial — é requisito. Órgãos públicos estão cada vez mais exigindo conformidade com WCAG em suas licitações e ferramentas contratadas.

**Custo de correção: R$ 2.663 (itens de acessibilidade nas Waves 1-2) | Impacto: conversão + compliance**

### Velocidade de Desenvolvimento

O acúmulo de código monolítico reduz diretamente a velocidade de entrega de novas funcionalidades:

- **4 arquivos backend ultrapassam 2.000 linhas** — cada alteração exige navegar milhares de linhas, com alto risco de conflito quando dois desenvolvedores editam o mesmo arquivo
- **69 arquivos Python soltos na raiz** sem organização em pacotes — encontrar a função certa é como procurar agulha no palheiro
- **40+ feature flags** sem auditoria — flags permanentemente ligadas ou desligadas poluem o código com caminhos nunca executados

Estimamos que o time perde **~50 horas por mês** em produtividade por conta dessa dívida estrutural (navegação, conflitos, debugging em código entrelaçado). Após a reestruturação (Wave 3), essa perda cairia para ~10 horas/mês.

**Custo de correção: R$ 11.400 (Wave 3) | Economia anual: ~R$ 36.000 em produtividade recuperada**

### Confiabilidade do Produto

Módulos críticos do sistema operam sem rede de segurança:

- **Tarefas agendadas (cron jobs)** — 2.039 linhas de código executando diariamente sem nenhum teste automatizado. Se uma mudança quebrar o agendamento de emails de trial ou a limpeza de cache, ninguém saberá até um cliente reclamar.
- **Circuit breaker do banco de dados** — mecanismo que protege o sistema quando o banco está sobrecarregado, mas sem testes. Se falhar, todas as requisições podem ficar bloqueadas.
- **11 submódulos de filtros** — a lógica que decide quais licitações são relevantes para cada setor opera sem testes individuais.

**Custo de correção: R$ 3.600 (Wave 0) | Benefício: confiança para evoluir o produto sem medo de quebrar**

---

## Timeline Recomendado

### Wave 0: Rede de Segurança (Semana 1)

Antes de mexer em qualquer código existente, criamos testes automatizados para os módulos críticos que hoje operam sem cobertura. Isto é a fundação que permite todas as melhorias subsequentes sem risco de regressão.

- **Custo:** R$ 3.600
- **ROI:** Previne regressões durante toda a resolução. Estimativa de 20+ bugs evitados ao longo das Waves 1-3.

### Wave 1: Correções Críticas + Quick Wins (Semanas 2-3)

Resolve os 4 itens críticos (acessibilidade, segurança de dados, integridade de cobrança) e colhe 11 quick wins que melhoram imediatamente a experiência do produto. Organizado em 3 entregas temáticas para facilitar revisão e reversão se necessário.

- **Custo:** R$ 3.938
- **ROI:** Elimina riscos legais (LGPD, acessibilidade), corrige bugs visuais, desativa fonte de dados morta que causa lentidão.
- **Entregas visíveis:** formulário de busca acessível, navegação por teclado funcionando, ícone do dashboard corrigido, páginas "Em breve" com design adequado.

### Wave 2: Alta Prioridade (Semanas 4-5)

Resolve 12 itens de prioridade alta que afetam a qualidade do código e a experiência do usuário: migração de formulários para validação moderna, otimização de carregamento, e limpeza do pipeline de integração contínua.

- **Custo:** R$ 5.325
- **ROI:** Formulários de autenticação com experiência consistente, animações carregadas apenas onde necessário (economia de banda), banco de dados com migrações limpas e validadas.

### Wave 3: Reestruturação (Semanas 6-9)

Reorganiza a base de código: arquivos monolíticos são divididos em módulos focados, código é agrupado em pacotes por domínio (filtros, busca, cobrança, tarefas). Esta é a wave que mais impacta a velocidade de desenvolvimento futuro.

- **Custo:** R$ 11.400
- **ROI:** Nenhum arquivo acima de 1.000 linhas. Novos desenvolvedores produtivos em dias ao invés de semanas. Conflitos de merge reduzidos drasticamente. Estimativa de +40% na velocidade de entrega de funcionalidades.

### Wave 4: Polimento (Semanas 10-13)

Itens de menor prioridade tratados oportunisticamente, intercalados com desenvolvimento de funcionalidades normais. Inclui otimizações de banco que só fazem sentido com escala (10K+ usuários), testes de páginas secundárias, e limpeza cosmética.

- **Custo:** R$ 14.550
- **ROI:** Produto com acabamento profissional em todos os aspectos. Cobertura de testes acima dos gates de integração contínua (70% backend, 60% frontend). Zero itens críticos ou de alta prioridade pendentes.

---

## ROI da Resolução

| Investimento | Retorno Esperado |
|--------------|------------------|
| R$ 38.850 (resolução total, 259h) | R$ 95.500 em riscos evitados nos próximos 12 meses |
| R$ 12.863 (Waves 0-2 apenas, 86h) | R$ 81.500 em riscos evitados (85% do total) |
| 13 semanas de foco | Produto sustentável para escalar de beta para receita recorrente |
| Wave 3 (4 semanas) | +40% velocidade de entrega = ~R$ 36.000/ano em produtividade |

**ROI da resolução total: 2,5:1** (cada R$1 investido evita R$2,46 em riscos)

**ROI da resolução parcial (Opção B): 6,3:1** (melhor relação custo-benefício)

---

## Opções de Execução

### Opção A: Resolução Completa (13 semanas, R$ 38.850)

Resolve TODOS os 69 itens acionáveis. O produto fica com base limpa, testada e organizada para escalar. Nenhum item crítico ou de alta prioridade remanescente. Indicada se há recursos dedicados disponíveis e a prioridade é preparar o produto para escala agressiva.

| | |
|---|---|
| **Investimento** | R$ 38.850 (259h) |
| **Timeline** | 13 semanas |
| **Risco mitigado** | 100% dos itens identificados |
| **Trade-off** | 4 semanas de feature freeze (Wave 3) |

### Opção B: Resolução Parcial — Waves 0-2 (5 semanas, R$ 12.863)

Resolve todos os itens Críticos + Alta Prioridade + Quick Wins. Mitiga ~85% do risco com 33% do investimento. A reestruturação profunda (Wave 3) fica para quando houver janela de feature freeze. **Recomendada para o momento atual do produto.**

| | |
|---|---|
| **Investimento** | R$ 12.863 (85,75h) |
| **Timeline** | 5 semanas (3 efetivas, Waves 0+1 em paralelo) |
| **Risco mitigado** | ~85% (todos os Critical e High) |
| **Trade-off** | Arquivos monolíticos permanecem, impactando produtividade |

### Opção C: Mínimo Viável — Waves 0-1 (3 semanas, R$ 7.538)

Resolve apenas os 4 itens Críticos e os Quick Wins mais urgentes. Mitiga riscos imediatos de segurança e acessibilidade. Rede de segurança de testes incluída. Indicada se o orçamento é muito restrito.

| | |
|---|---|
| **Investimento** | R$ 7.538 (50,25h) |
| **Timeline** | 3 semanas (Wave 0 e 1 em paralelo) |
| **Risco mitigado** | ~60% (Critical + parte dos High) |
| **Trade-off** | Débitos de alta prioridade permanecem, reestruturação fica distante |

### Recomendação: Opção B

A Opção B oferece o melhor equilíbrio entre investimento e retorno. Com R$ 12.863 e 5 semanas de trabalho, eliminamos todos os riscos críticos e de alta prioridade, incluindo acessibilidade (requisito legal), integridade de dados (LGPD), e confiabilidade de cobrança (receita). O produto sai dessas 5 semanas significativamente mais robusto e em posição de converter trials em assinaturas com confiança.

A Wave 3 (reestruturação, R$ 11.400) pode ser planejada para um momento em que haja 4 semanas disponíveis sem pressão de lançamento — idealmente antes de escalar o time de desenvolvimento.

---

## Próximos Passos

1. [ ] Aprovar orçamento para Opção A, B ou C
2. [ ] Definir data de início da Wave 0 + Wave 1
3. [ ] Alocar desenvolvedor(es) — estimativa: 1 dev senior por 5 semanas (Opção B) ou 2 devs por 7 semanas (Opção A)
4. [ ] Iniciar Wave 0 (criação de testes para módulos críticos)
5. [ ] Review de progresso ao final de cada Wave
6. [ ] Decisão sobre Wave 3 ao concluir Wave 2

---

## Distribuição por Área

| Área | Itens | Horas | % do Esforço |
|------|-------|-------|--------------|
| Sistema / Arquitetura | 21 | ~91h | 35% |
| Banco de Dados | 22 | ~54h | 21% |
| Frontend / UX | 24 | ~68h | 26% |
| Qualidade / Testes | 9 | ~34h | 13% |
| CI/CD | 2 | ~5h | 2% |
| Design Choice (sem ação) | 3 | 0h | -- |

## Distribuição por Severidade

| Severidade | Itens | Horas | Custo |
|------------|-------|-------|-------|
| CRITICAL | 4 | 21h | R$ 3.150 |
| HIGH | 14 | 58h | R$ 8.700 |
| MEDIUM | 25 | 109h | R$ 16.350 |
| LOW | 27 | 71h | R$ 10.650 |
| INFO / N/A | 3 | 0h | R$ 0 |

---

## Anexos

- [Assessment Técnico Completo](../prd/technical-debt-assessment.md) — Inventário detalhado com 76 itens, dependências e critérios de sucesso
- [Arquitetura do Sistema](../architecture/system-architecture.md)
- [Auditoria de Banco de Dados](../../supabase/docs/DB-AUDIT.md)
- [Especificação Frontend](../frontend/frontend-spec.md)

---

*Relatório gerado em 2026-03-21 pela equipe AIOS Technical Assessment.*
*Baseado no Technical Debt Assessment v2.0 FINAL (76 itens, 5 waves, 13 semanas).*
*Custo hora base: R$150/h. Valores em reais brasileiros.*
