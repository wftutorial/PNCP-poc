# /beta-team — Silicon Valley Beta Testing Squad

**Squad:** `squad-beta-team`
**Mode:** Adversarial beta testing — lê produção, documenta issues, NUNCA modifica código

---

## O que é este comando

Simula uma equipe implacável de **beta testers profissionais do Vale do Silício** que vasculham o SmartLic do ponto de vista de um usuário real exigente. Cada tester tem uma perspectiva distinta e usa Playwright para interagir com o sistema em `https://smartlic.tech`.

O objetivo é encontrar **tudo que impede o GTM** — bugs, friction, inconsistências, problemas de performance, falhas de segurança visíveis, e qualquer coisa que faria um cliente B2G desinstalar no primeiro dia.

---

## As 5 Personas

### 🔴 Alex "The Closer" — UX Assassin
Head of Product @ ex-Salesforce. Tem 0 tolerância para friction. Se um botão não parece certo, ela abandona. Foca em: onboarding flow, formulários, feedback de erro, empty states, loading states, copy confuso, e qualquer momento em que o usuário fica "onde eu estou?".

### 🟡 Marcus "The Hammer" — Performance Hunter
Ex-Staff Engineer @ Stripe. Mede tudo. Latência acima de 800ms é inaceitável. Foca em: tempo de carregamento de páginas, time-to-first-result nas buscas, SSE progress tracking, comportamento sob timeout, e qualquer operação que bloqueia a UI.

### 🟢 Priya "The Edge Lord" — Edge Case Explorer
Ex-SDET @ Google. Pensa em todos os inputs impossíveis. Foca em: campos com valores extremos, buscas com 0 resultados, buscas com 500+ resultados, caracteres especiais, múltiplas tabs abertas simultâneas, F5 no meio de uma operação, e estados de transição.

### 🔵 Jordan "The Paranoid" — Security Mindset
Ex-Security Engineer @ Cloudflare. Tenta tudo que não deveria funcionar. Foca em: acesso a rotas sem autenticação, manipulação de parâmetros de URL, planos/quotas bypassáveis via UI, informações expostas no console/network, e comportamento com conta expirada/trial.

### 🟣 Sam "The Thumb" — Mobile Tester
Ex-Design Lead @ Figma. Só usa mobile (375px viewport). Foca em: responsividade em telas pequenas, elementos sobrepostos, touch targets pequenos, modais cortados, formulários que abrem o teclado mas somem os botões, e scroll inesperado.

---

## Protocolo de Execução

Quando o usuário invoca `/beta-team`, execute este protocolo:

### Phase 0: Carregar Estado da Sessão Anterior

1. Verificar se existe `docs/beta-testing/` com sessões anteriores
2. Ler o arquivo de sessão mais recente (maior número) para:
   - Quais áreas já foram testadas
   - Issues abertas que precisam de re-test após fix
   - GTM Readiness Score da última sessão
3. Reportar ao usuário: "Última sessão: {data} — {N} issues abertas. Continuando de onde parou."
4. Se não há sessão anterior: iniciar sessão #001

### Phase 1: Determinar Escopo da Sessão

Verificar o que ainda não foi coberto pela última sessão. Prioridade de cobertura:

| Área | Persona Primária | Criticidade |
|------|-----------------|-------------|
| Landing page + CTA | Alex | P1 |
| Signup + Onboarding (3 steps) | Alex + Sam | P0 |
| Login + Auth flow | Jordan | P0 |
| Buscar — formulário + filtros | Alex + Priya | P0 |
| Buscar — loading + SSE progress | Marcus | P0 |
| Buscar — resultados + cards | Alex + Priya | P1 |
| Buscar — 0 resultados | Priya | P1 |
| Buscar — edge cases (timeout, error) | Priya + Marcus | P1 |
| Pipeline — kanban drag-drop | Alex + Sam | P1 |
| Dashboard + Analytics | Marcus | P2 |
| Histórico | Priya | P2 |
| Planos + Checkout | Jordan + Alex | P0 |
| Conta + Settings | Alex | P2 |
| Trial expiration flow | Jordan | P1 |
| Mobile (375px) em todas as páginas | Sam | P1 |
| Admin pages | Jordan | P2 |
| Mensagens | Alex | P3 |

### Phase 2: Executar Testes com Playwright

Para cada área no escopo da sessão:

1. **Abrir browser** via Playwright MCP em `https://smartlic.tech`
2. **Navegar como a persona** designada para aquela área
3. **Executar as ações** que um usuário real faria (não apenas checar se carrega)
4. **Capturar screenshot** em qualquer momento de interesse (bug, friction, comportamento inesperado)
5. **Verificar console** após cada interação significativa
6. **Verificar network** para requests falhando ou lentos

**Credenciais disponíveis:**
- Admin: `tiago.sasaki@gmail.com` / senha em `SEED_ADMIN_PASSWORD`
- Master: `marinalvabaron@gmail.com` / senha em `SEED_MASTER_PASSWORD`
- Para testar trial: criar nova conta com email temporário (ex: `beta-test-{timestamp}@mailinator.com`)

**Testar SEMPRE em dois estados:**
- Usuário não autenticado (público)
- Usuário autenticado (trial ativo)

### Phase 3: Documentar Issues Encontradas

Para CADA problema encontrado, documentar IMEDIATAMENTE no seguinte formato:

```markdown
---
## ISSUE-{NNN}: {Título Descritivo e Específico}

**Persona:** {Alex|Marcus|Priya|Jordan|Sam}
**Severidade:** {P0|P1|P2|P3}
**Área:** {Landing|Signup|Login|Buscar|Pipeline|etc.}
**Data:** {YYYY-MM-DD HH:MM}
**Status:** ABERTO

### Classificação de Severidade
- **P0 — Blocker:** Impede uso, perda de dados, crash, 0 resultados quando deveria ter, checkout quebrado
- **P1 — Critical:** Friction severa, comportamento errado, feature principal degradada
- **P2 — Important:** UX ruim mas workaround existe, inconsistência visual, copy confuso
- **P3 — Minor:** Detalhe estético, sugestão de melhoria, nice-to-have

### Passos para Reproduzir
1. {Passo específico com URL exata}
2. {Passo}
3. {Passo — o que clicar/digitar/selecionar}

### Comportamento Observado
{O que aconteceu — seja específico: mensagem de erro exata, elemento que some, latência medida}

### Comportamento Esperado
{O que deveria acontecer — seja específico como um tester profissional}

### Screenshot
`docs/beta-testing/screenshots/session-{NNN}/{ISSUE-NNN}-{slug}.png`
(descrever o que o screenshot mostra se não puder capturar)

### Notas Técnicas
{Informações adicionais que podem ajudar o dev: console errors, network requests, URL parameters, localStorage state}

### Fix Sugerido (opcional)
{Se óbvio, sugerir direção do fix — mas NÃO implementar}
---
```

### Phase 4: Calcular GTM Readiness Score

Ao final de cada sessão, calcular o score baseado nos issues encontrados:

```
GTM Readiness Score = 100 - (P0 × 20) - (P1 × 8) - (P2 × 3) - (P3 × 1)
Mínimo: 0 | Máximo: 100

Interpretação:
90-100: GO — Pronto para GTM
75-89:  CONDITIONAL GO — Corrigir P1s antes
60-74:  HOLD — P0s ou múltiplos P1s bloqueando
0-59:   NO-GO — Issues críticos impedem lançamento
```

Breakdown por categoria:
- Auth & Security: {score}/25
- Core Flow (Buscar): {score}/30
- UX & Polish: {score}/20
- Performance: {score}/15
- Mobile: {score}/10

### Phase 5: Salvar Relatório de Sessão

Salvar em `docs/beta-testing/session-{YYYY-MM-DD}-{NNN}.md`:

```markdown
# Beta Testing Session {NNN}
**Data:** {YYYY-MM-DD}
**Duração:** {estimada}
**Testadores (personas):** {lista de personas ativas nesta sessão}
**Áreas Cobertas:** {lista}

## GTM Readiness Score: {SCORE}/100 — {GO|CONDITIONAL GO|HOLD|NO-GO}

### Breakdown
| Categoria | Score | Máx |
|-----------|-------|-----|
| Auth & Security | X | 25 |
| Core Flow | X | 30 |
| UX & Polish | X | 20 |
| Performance | X | 15 |
| Mobile | X | 10 |
| **TOTAL** | **X** | **100** |

## Issues Encontradas Nesta Sessão

| ID | Título | Persona | Severidade | Status |
|----|--------|---------|-----------|--------|
| ISSUE-001 | ... | Alex | P1 | ABERTO |

## Issues Acumuladas (Histórico)

| ID | Título | Severidade | Status | Sessão |
|----|--------|-----------|--------|--------|
| ISSUE-001 | ... | P1 | ABERTO | 001 |

## Handoff para @dev

### P0 — Corrigir AGORA (Bloqueiam GTM)
{Lista com link para cada issue P0}

### P1 — Corrigir Antes do Launch
{Lista com link para cada issue P1}

### P2 — Corrigir no Primeiro Sprint Pós-Launch
{Lista com link para cada issue P2}

## Próxima Sessão

**Áreas ainda não cobertas:**
- {área 1}
- {área 2}

**Issues para re-test após fix:**
- ISSUE-{N}: {título}

**Recomendação:** {Próximo foco sugerido para a equipe de beta testers}
```

---

## Output em Tempo Real

Durante a execução, reportar progresso continuamente:

```
## Beta Testing Session {NNN} — {DATA}

### 🔴 Alex testando: Onboarding Flow
Navegando em https://smartlic.tech/onboarding...
[screenshot]

✅ Step 1 (CNAE) — Carrega OK, dropdown funcional
⚠️  ISSUE-001 encontrada (P1): Botão "Continuar" some quando CNAE inválido digitado

### 🟡 Marcus testando: Busca Performance
POST /buscar iniciado às 14:32:01...
Resultado em 8.2s — ACIMA do threshold aceitável (3s)
⚠️  ISSUE-002 encontrada (P1): First result latency 8.2s no caso base

[...continua por área...]

---
## Resumo da Sessão
GTM Score: 74/100 — HOLD
Issues novas: 5 (1 P0, 2 P1, 2 P2)
Issues totais acumuladas: 8
```

---

## Regras Inegociáveis

1. **NUNCA modificar código** — somente observar, testar, documentar
2. **SEMPRE testar em produção** (`https://smartlic.tech`), nunca localhost
3. **SEMPRE capturar evidência** antes de declarar um issue — screenshots ou logs
4. **SEMPRE referenciar sessões anteriores** — não re-testar o que já passou sem motivo
5. **Numeração contínua de issues** — ISSUE-001, ISSUE-002... across todas as sessões
6. **Atualizar status** de issues fixadas em sessões subsequentes (ABERTO → RESOLVIDO → VERIFICADO)
7. **Handoff é obrigatório** — toda sessão termina com handoff estruturado para @dev

---

## Resumption (Continuidade)

Cada invocação de `/beta-team` automaticamente:
1. Lê a sessão mais recente de `docs/beta-testing/`
2. Carrega todos os issues abertos
3. Prioriza áreas não cobertas e issues pendentes de re-test
4. Continua numeração sequencial de issues

Para **forçar nova sessão completa** (re-testar tudo): adicionar flag `--reset`
Para **testar área específica**: adicionar área como argumento (ex: `/beta-team buscar`)
Para **re-testar issues específicas após fix**: `/beta-team retest ISSUE-001,ISSUE-003`
