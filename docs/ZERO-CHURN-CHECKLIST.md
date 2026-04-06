# ZERO-CHURN CHECKLIST — Eliminacao Total de Barreiras Trial-to-Paid

> **Missao:** Eliminar todo e qualquer motivo pelo qual um trial deixaria de converter em assinatura paga.
> **Contexto:** CAC zero via SEO organico (2K+ paginas). Cada trial que nao converte e receita jogada fora.
> **Data:** 2026-04-06 | **Baseline:** 40+ pontos de friccao identificados

---

## Como usar este checklist

- **P0 (BLOQUEANTE):** Impede conversao diretamente. Resolver antes de qualquer outra coisa.
- **P1 (CRITICO):** Reduz conversao significativamente. Resolver na primeira semana.
- **P2 (IMPORTANTE):** Friccao real mas contornavel. Resolver na segunda semana.
- **P3 (OTIMIZACAO):** Nice-to-have que melhora metricas. Resolver quando P0-P2 estiverem limpos.
- **Esforco:** S (< 2h), M (2-8h), L (8-24h), XL (24h+)

---

## 1. EMAILS & NURTURING

### 1.1 Sistema de emails quebrado (CRIT-044)

- [x] **P0 | S** — ~~Resolver conflito de dual-cron de trial emails~~ RESOLVIDO: `cron/__init__.py` agora importa `start_trial_sequence_task` de `jobs/cron/notifications.py` (canonical). Legacy `cron/notifications.py` stub deprecated.
  - Arquivo: `backend/cron/__init__.py`, `backend/cron/notifications.py`

- [x] **P0 | S** — ~~Corrigir timing do email Day 7~~ RESOLVIDO: Copy atualizado para "preview limitado a partir de HOJE" (email enviado Day 7, paywall ativa Day 7). Subject, body e preheader corrigidos em `trial_email_sequence.py` e `templates/emails/trial.py`.
  - Arquivo: `backend/services/trial_email_sequence.py`, `backend/templates/emails/trial.py`

- [x] **P0 | S** — ~~Cancelar emails de trial apos conversao~~ RESOLVIDO: `process_trial_emails()` ja verifica `plan_type != "free_trial"` (L264-268) em cada iteracao, e `checkout.py` webhook atualiza `plan_type` sincronamente (L100-103). Race condition eliminada pelo check inline. Emails futuros sao naturalmente skippados.
  - Arquivo: `backend/services/trial_email_sequence.py` L264-268, `backend/webhooks/handlers/checkout.py` L100-103

### 1.2 Sequencia de emails sem impacto

- [x] **P1 | M** — ~~Reordenar sequencia de emails~~ RESOLVIDO: Activation nudge movido para Day 1 (era Day 2). `_active_sequence()` agora retorna sorted por day. `DAY3_ACTIVATION_EMAIL_ENABLED` ativado por default.
  - Arquivo: `backend/services/trial_email_sequence.py` linhas 48-79

- [x] **P1 | M** — ~~Adicionar emails de feature discovery~~ RESOLVIDO: 3 novos templates (Day 2 Pipeline, Day 5 Excel, Day 8 IA) com feature flag `FEATURE_DISCOVERY_EMAILS_ENABLED`. Registrados na sequencia opcional.
  - Arquivo: `backend/templates/emails/trial.py`, `backend/services/trial_email_sequence.py`

- [x] **P1 | S** — ~~Segmentar emails por engagement~~ RESOLVIDO: Tier computation (high_value/active/dormant) em `_render_email()`. Subjects personalizados por tier para engagement e value emails.
  - Arquivo: `backend/services/trial_email_sequence.py`

- [ ] **P2 | S** — Diferenciar emails transacionais vs marketing no unsubscribe: usuario clica unsubscribe pensando ser "marketing" e perde TODOS os emails de conversao (Day 10 value, Day 13 last day, Day 16 comeback).
  - Arquivo: `backend/routes/trial_emails.py` linha 28
  - Acao: Separar `marketing_emails_enabled` de `trial_conversion_emails_enabled`

- [ ] **P2 | M** — Implementar timezone-aware email scheduling: emails podem chegar as 3am no fuso do usuario, sendo ignorados/deletados.
  - Arquivo: `backend/cron/notifications.py`
  - Acao: Armazenar timezone no profile, agendar envio no horario local

---

## 2. PAYWALL & LIMITES

### 2.1 Paywall com bypass

- [x] **P0 | S** — ~~Remover bypass do TrialPaywall~~ RESOLVIDO: Dismiss reduzido de 1h para 15min, limitado a 1x/dia via localStorage. Botao "Continuar com preview" oculto apos atingir limite diario.
  - Arquivo: `frontend/components/billing/TrialPaywall.tsx`

- [x] **P1 | S** — ~~Pipeline limit de 5 items muito restritivo~~ RESOLVIDO: Limite aumentado de 5 para 15 em `backend/config/features.py` e `frontend/app/pipeline/page.tsx`.
  - Arquivo: `backend/config/features.py`, `frontend/app/pipeline/page.tsx`

### 2.2 Sem grace period no trial

- [x] **P0 | M** — ~~Grace period 48h para trial~~ RESOLVIDO: `quota.py` agora concede 48h grace period com ate 3 buscas apos expiracao. Config via `TRIAL_GRACE_HOURS` e `TRIAL_GRACE_MAX_SEARCHES` env vars.
  - Arquivo: `backend/quota.py` L948-987

- [x] **P1 | M** — ~~Manter acesso read-only ao pipeline com CTA~~ RESOLVIDO: Banner melhorado com contagem de items, mensagem personalizada e botao "Assinar SmartLic Pro" direto.
  - Arquivo: `frontend/app/pipeline/page.tsx`

- [ ] **P2 | M** — Permitir download de dados exportados durante grace period: emails dizem "dados ficam salvos por 30 dias" mas sem enforcement ou UI para acessar.
  - Arquivo: `backend/quota.py`, `frontend/app/historico/`
  - Acao: Permitir GET em `/sessions` e download Excel de buscas anteriores por 30 dias

---

## 3. CHECKOUT & PRICING

### 3.1 Friccao no checkout

- [x] **P0 | M** — ~~Checkout direto no TrialConversionScreen~~ RESOLVIDO: CTA agora chama `POST /api/billing?endpoint=checkout` direto, redireciona para Stripe em 1 clique. Fallback gracioso para `/planos` se checkout falha.
  - Arquivo: `frontend/app/components/TrialConversionScreen.tsx`

- [x] **P0 | S** — ~~Precos dinamicos no TrialConversionScreen~~ RESOLVIDO: Usa `usePlans()` hook (SWR) para buscar precos do backend. Hardcoded mantido como fallback.
  - Arquivo: `frontend/app/components/TrialConversionScreen.tsx`

- [x] **P1 | S** — ~~Corrigir inconsistencia de pricing no banner~~ RESOLVIDO: Banner ja mostra "Planos a partir de R$ 297/mes" (COPY-369 aplicado). Verificado: nenhuma referencia a "R$ 9,90/dia" restante no codebase.
  - Arquivo: `frontend/app/components/TrialExpiringBanner.tsx`

### 3.2 Cupom e metodos de pagamento

- [x] **P1 | M** — ~~Auto-apply cupom na URL~~ RESOLVIDO: Frontend le `?coupon=` de searchParams e passa ao checkout. Backend resolve coupon via `stripe.PromotionCode.list()` e aplica em `discounts`.
  - Arquivo: `frontend/app/planos/page.tsx`, `backend/routes/billing.py`

- [ ] **P2 | S** — Exibir Boleto como opcao de pagamento na UI: backend ja configura `["card", "boleto"]` no Stripe session, mas frontend nao mostra Boleto como opcao visivel.
  - Arquivo: `frontend/app/planos/page.tsx`, `backend/routes/billing.py` linha 54
  - Acao: Adicionar badge "Aceitamos cartao e boleto" na pagina de planos

- [ ] **P2 | S** — Adicionar PIX como metodo de pagamento: PIX e o metodo mais usado no Brasil. Stripe suporta PIX desde 2023.
  - Arquivo: `backend/routes/billing.py`
  - Acao: Adicionar `"pix"` ao array de payment_method_types na session Stripe

---

## 4. VALOR PERCEBIDO DURANTE O TRIAL

### 4.1 Dashboard de valor inexistente durante trial

- [x] **P0 | L** — ~~Trial Value Dashboard~~ RESOLVIDO: Novo componente `TrialValueTracker.tsx` mostra "R$ X analisados | Y oportunidades | Z dias restantes" via SWR. Montado em buscar/page.tsx e dashboard/page.tsx.
  - Arquivo: `frontend/components/billing/TrialValueTracker.tsx` (NOVO), `frontend/app/buscar/page.tsx`, `frontend/app/dashboard/page.tsx`

- [x] **P1 | M** — ~~ROI em momentos de alto valor~~ RESOLVIDO: `TrialUpsellCTA variant="post-search"` ja implementado em SearchResults.tsx com trigger por contagem de resultados e valor.
  - Arquivo: `frontend/app/buscar/components/SearchResults.tsx`

- [x] **P1 | S** — ~~Incluir valor R$ nos emails~~ RESOLVIDO: Valor R$ incluido nos subjects de paywall_alert e last_day (alem de engagement e value que ja tinham). `_format_brl()` usado em todos.
  - Arquivo: `backend/services/trial_email_sequence.py`, `backend/templates/emails/trial.py`

### 4.2 Momentos de conversao desperdicados

- [x] **P1 | M** — ~~CTAs contextuais pos-acao~~ RESOLVIDO: `TrialUpsellCTA` ja implementado com 5 variantes (post-search, post-download, post-pipeline, dashboard, quota). Pipeline CTA trigger via `showPipelineCTA` state. Feature usage tracking adicionado.
  - Arquivo: `frontend/components/billing/TrialUpsellCTA.tsx`, `frontend/app/pipeline/page.tsx`

- [ ] **P2 | M** — Comparacao "trial vs paid" na tela de conversao: TrialConversionScreen mostra stats mas nao compara "o que voce tem hoje" vs "o que voce ganha pagando".
  - Arquivo: `frontend/app/components/TrialConversionScreen.tsx`
  - Acao: Tabela lado-a-lado: Trial (10 resultados, 5 pipeline) vs Pro (ilimitado, alertas, relatorios)

- [ ] **P2 | S** — "Uma unica licitacao ganha paga o sistema por um ano" — frase generica. Substituir por calculo personalizado baseado no valor que o usuario JA analisou.
  - Arquivo: `frontend/app/components/TrialConversionScreen.tsx`
  - Acao: "Voce analisou R$2.4M. Uma unica vitoria de 1% = R$24.000 — 5x o custo anual."

---

## 5. QUALIDADE DE BUSCA & RESULTADOS

### 5.1 Precisao e relevancia

- [x] **P0 | L** — ~~Falsos positivos setores genericos~~ RESOLVIDO: 14 novas exclusions + 2 co_occurrence_rules (software/sistema) + context_required tightened para "Software e Sistemas". Removido "gerenciamento" generico, adicionado "web/api/cloud/nuvem".
  - Arquivo: `backend/sectors_data.yaml`

- [x] **P0 | L** — ~~0 resultados em combos validas~~ RESOLVIDO: Adicionado Level-2 sector substring relaxation em `filter_stage.py`. Quando sector search retorna 0 mas raw>0, re-filtra com substring matching (mantendo exclusions). Tag `sector_substring_relaxation`.
  - Arquivo: `backend/pipeline/stages/filter_stage.py`

- [x] **P1 | M** — ~~Cross-sector collision~~ RESOLVIDO: Co-occurrence rules adicionadas em `sectors_data.yaml` para desambiguar "construcao + UBS/hospital" (saude vs engenharia).
  - Arquivo: `backend/sectors_data.yaml`

- [x] **P1 | M** — ~~Setores com recall baixo~~ RESOLVIDO: Keywords expandidas para materiais_eletricos (+10 termos) e engenharia_rodoviaria (+10 termos).
  - Arquivo: `backend/sectors_data.yaml`

### 5.2 Performance

- [x] **P0 | M** — ~~Timeouts de busca~~ RESOLVIDO: Adicionado TTL cache in-memory (1h, max 50 entries) para datalake queries em `datalake_query.py`. Queries repetidas servidas do cache, eliminando round-trip ao DB.
  - Arquivo: `backend/datalake_query.py`

- [ ] **P2 | M** — Mostrar resultados parciais antes do timeout completo: botao "Ver resultados parciais" aparece apos 45s, mas deveria aparecer apos 15s com contagem parcial.
  - Arquivo: `frontend/app/buscar/components/EnhancedLoadingProgress.tsx`
  - Acao: Reduzir threshold de "partial results" para 15s, mostrar contagem em tempo real

---

## 6. UX & ONBOARDING

### 6.1 Primeira experiencia

- [x] **P0 | M** — ~~Onboarding tour auto-trigger~~ RESOLVIDO: buscar e pipeline ja auto-triggeravam. Adicionado dashboard tour (3 steps: stats, chart, dimensions) com auto-trigger na primeira visita (800ms delay).
  - Arquivo: `frontend/app/dashboard/page.tsx`

- [x] **P1 | S** — ~~Onboarding pode ser skipado~~ RESOLVIDO: OnboardingEmptyState agora mostra banner "Configure seu perfil" com CTA "Configurar perfil → /onboarding" quando `smartlic-onboarding-completed` nao esta no localStorage.
  - Arquivo: `frontend/app/buscar/components/OnboardingEmptyState.tsx`

- [x] **P1 | M** — ~~Primeira analise falha silenciosa~~ RESOLVIDO: Timeout de 30s (AbortController), deteccao de 403 (trial expirado → CTA /planos), erro generico com botao "Ajustar filtros". OnboardingStep3 aceita props `error` e `onGoBack`.
  - Arquivo: `frontend/app/onboarding/page.tsx`, `frontend/app/onboarding/components/OnboardingStep3.tsx`

- [x] **P1 | S** — ~~Step 3 sem feedback de sucesso~~ RESOLVIDO: Tratado junto com "primeira analise falha silenciosa" — OnboardingStep3 agora mostra sugestoes (expandir UFs, ampliar valor) e botao "Ajustar filtros" quando zero resultados ou erro.
  - Arquivo: `frontend/app/onboarding/components/OnboardingStep3.tsx`

### 6.2 Tour e orientacao

- [ ] **P2 | M** — Tour so cobre 3 paginas (buscar, resultados, pipeline): faltam tours para dashboard, alertas, conta. Dashboard e a pagina mais importante para valor percebido.
  - Arquivo: `frontend/hooks/useShepherdTour.ts`
  - Acao: Adicionar tour para dashboard ("Aqui voce ve o valor acumulado") e alertas ("Configure alertas para nao perder oportunidades")

- [ ] **P2 | S** — Pipeline tour nao avisa sobre limite de 5 items: usuario atinge limite sem warning previo, frustrado.
  - Arquivo: `frontend/app/pipeline/page.tsx`
  - Acao: No tour step do pipeline, mencionar "Durante o trial, voce pode acompanhar ate 5 oportunidades"

- [ ] **P3 | S** — Falta help center linkado nos pontos de friccao: empty states, paywall, pipeline limit, erros nao linkam para `/ajuda`.
  - Arquivo: Multiplos componentes
  - Acao: Adicionar "Precisa de ajuda?" com link para FAQ relevante em cada ponto de friccao

---

## 7. ANALYTICS & TRACKING

### 7.1 Funnel de conversao inexistente

- [x] **P1 | L** — ~~Funnel tracking completo~~ RESOLVIDO: `track_funnel_event()` com cohort enrichment em `analytics_events.py`. Events: `onboarding_completed`, `subscription_activated`. Frontend: `feature_used` tracking em Excel download e pipeline add.
  - Arquivo: `backend/analytics_events.py`, `backend/webhooks/handlers/checkout.py`, `backend/routes/onboarding.py`

- [x] **P1 | M** — ~~Cohort analysis~~ RESOLVIDO: `track_funnel_event()` enriquece automaticamente com `searches_count`, `total_value`, `opportunities_found`, `pipeline_items`, `engagement_tier` via `trial_stats`.
  - Arquivo: `backend/analytics_events.py`

- [x] **P1 | M** — ~~Feature usage tracking~~ RESOLVIDO: `trackEvent("feature_used", { feature_name })` adicionado em Excel download (useSearchExport) e pipeline add (AddToPipelineButton).
  - Arquivo: `frontend/app/buscar/hooks/useSearchExport.ts`, `frontend/app/components/AddToPipelineButton.tsx`

### 7.2 Deteccao de risco

- [x] **P1 | L** — ~~At-risk trial detection cron~~ RESOLVIDO: `detect_at_risk_trials()` em `backend/jobs/cron/trial_risk_detection.py`. Categoriza trials em critical/at_risk/healthy. Registrado como cron job diario.
  - Arquivo: `backend/jobs/cron/trial_risk_detection.py`, `backend/cron_jobs.py`

- [ ] **P2 | M** — Dashboard admin de trial conversion: admin nao tem visibilidade sobre taxa de conversao, drop-off points, ou trials at-risk.
  - Arquivo: `frontend/app/admin/`, `backend/routes/admin.py`
  - Acao: Pagina admin com: trials ativos, conversion rate, at-risk list, engagement heatmap

- [ ] **P3 | M** — A/B testing capability: nao ha como testar variantes de messaging, pricing display, ou CTA copy. Sem variant parameter nos analytics events.
  - Arquivo: Frontend + backend analytics
  - Acao: Adicionar `variant` property em events de conversao, implementar feature flag por usuario

---

## 8. POS-CONVERSAO & RETENCAO

### 8.1 Experiencia pos-pagamento

- [x] **P1 | M** — ~~Tela de boas-vindas pos-conversao~~ RESOLVIDO: ObrigadoContent ja tinha polling, plan details e CTAs. Verificado e confirmado funcional.
  - Arquivo: `frontend/app/planos/obrigado/ObrigadoContent.tsx`

- [x] **P1 | S** — ~~Estado UI stale apos conversao~~ RESOLVIDO: `useUserProfile` agora escuta `storage` events. Quando ObrigadoContent atualiza o cache no localStorage, todas as tabs revalidam via `mutate()`.
  - Arquivo: `frontend/hooks/useUserProfile.ts`

- [x] **P1 | M** — ~~Email de boas-vindas pos-conversao~~ RESOLVIDO: `_send_welcome_email()` adicionada em `checkout.py`. Template em `welcome_subscriber.py` com 3 proximos passos. Chamada apos ativacao (card e Boleto/PIX).
  - Arquivo: `backend/webhooks/handlers/checkout.py`, `backend/templates/emails/welcome_subscriber.py`

### 8.2 Prevencao de churn precoce

- [x] **P1 | L** — ~~Health score do usuario~~ RESOLVIDO: At-risk detection cron categoriza users (critical/at_risk/healthy) baseado em searches, value, trial_day. Emite `trial_risk_assessed` analytics events.
  - Arquivo: `backend/jobs/cron/trial_risk_detection.py`

- [ ] **P2 | M** — Exit interview obrigatorio no cancelamento: Stripe permite cancel direto sem feedback. Nao sabemos POR QUE usuarios cancelam.
  - Arquivo: `frontend/app/conta/`, `backend/routes/billing.py`
  - Acao: Modal pre-cancelamento: "O que podemos melhorar?" com opcoes (preco, qualidade, nao uso, outro)

- [ ] **P2 | M** — Implementar trial extension como mecanismo de retencao: nenhuma logica para "Complete seu perfil por +3 dias" ou "Indique um amigo por +7 dias".
  - Arquivo: `backend/quota.py`, `backend/services/trial_email_sequence.py`
  - Acao: Endpoints para extensao de trial com condicoes (profile complete, referral, feedback)

---

## 9. TRUST & SOCIAL PROOF

- [x] **P1 | M** — ~~Social proof na UI do trial~~ RESOLVIDO: Badges de trust ("Dados oficiais PNCP", "Cancele quando quiser", "Sem fidelidade") adicionados em TrialConversionScreen.
  - Arquivo: `frontend/app/components/TrialConversionScreen.tsx`

- [ ] **P2 | S** — Exibir badges de seguranca e compliance: signup nao mostra LGPD compliance, SSL, ou politica de dados. Empresas B2G sao sensíveis a seguranca.
  - Arquivo: `frontend/app/signup/page.tsx`, `frontend/app/planos/page.tsx`
  - Acao: Badge "Dados criptografados" + "LGPD compliant" + "Fontes oficiais do governo"

- [ ] **P2 | M** — Adicionar garantia de satisfacao: nenhuma mensagem de "cancele quando quiser" ou "garantia de 30 dias" no checkout. Reduce risk perception.
  - Arquivo: `frontend/app/components/TrialConversionScreen.tsx`
  - Acao: Badge "Sem fidelidade. Cancele quando quiser." + "Garantia de satisfacao 30 dias"

---

## 10. BANNER & MESSAGING BUGS

- [x] **P0 | S** — ~~TrialExpiringBanner factual error~~ VERIFICADO: Codigo ja correto (COPY-369 aplicado): `===0` hoje, `===1` amanha, else N dias. Fix secundario: removido "R$ 9,90/dia" hardcoded, substituido por "Planos a partir de R$ 297/mes".
  - Arquivo: `frontend/app/components/TrialExpiringBanner.tsx`

- [x] **P1 | S** — ~~Quota progress visivel~~ RESOLVIDO: QuotaBadge agora mostra "X/1000 analises" (usado/total) em vez de apenas "X analises restantes". Tooltip com detalhes completos.
  - Arquivo: `frontend/app/components/QuotaBadge.tsx`

- [ ] **P2 | S** — TrialCountdown badge nao explica fases: mostra "5 dias restantes" mas nao diz que Day 8 traz restricoes. Usuario nao entende "5 dias = acesso limitado ja ativo".
  - Arquivo: `frontend/app/components/TrialCountdown.tsx`
  - Acao: Tooltip no hover: "Seu trial tem acesso completo ate Day 7. Apos, alguns recursos ficam limitados."

---

## RESUMO EXECUTIVO

### Distribuicao por severidade

| Severidade | Quantidade | Resolvidos | % do Total |
|------------|-----------|-----------|------------|
| P0 (Bloqueante) | 13 | **13 (100%)** | 27% |
| P1 (Critico) | 22 | **22 (100%)** | 46% |
| P2 (Importante) | 12 | 0 | 25% |
| P3 (Otimizacao) | 2 | 0 | 4% |
| **TOTAL** | **49** | **35** | **100%** |

### Top 10 acoes de maior impacto na conversao

| # | Acao | Categoria | Esforco | Impacto Estimado |
|---|------|-----------|---------|-----------------|
| 1 | Resolver sistema de emails quebrado (CRIT-044) | Emails | S | +15-20% conversao (usuarios voltam a receber nurturing) |
| 2 | Checkout direto no TrialConversionScreen | Checkout | M | +10-15% (remove 2 cliques de friccao) |
| 3 | Trial Value Dashboard durante trial | Valor | L | +10-15% (usuarios veem ROI em tempo real) |
| 4 | Grace period 48h no trial | Paywall | M | +5-10% (segunda chance para converter) |
| 5 | Corrigir banner factual error | Messaging | S | +5% (restaura confianca na messaging) |
| 6 | Resolver 0 resultados em setores validos | Busca | L | +10-15% (primeira impressao positiva) |
| 7 | Auto-trigger onboarding tour | UX | M | +5-10% (usuario descobre features) |
| 8 | CTAs contextuais pos-acao | Valor | M | +5-10% (converte no momento de pico de valor) |
| 9 | Cancelar emails trial apos conversao | Emails | S | +3-5% (elimina confusao pos-venda) |
| 10 | Cupom auto-apply na URL | Checkout | M | +5% (reativa trials expirados com desconto) |

### Sequencia recomendada de execucao

**Semana 1 (P0 — Desbloqueio):**
- CRIT-044: emails funcionando
- Banner factual fix
- Precos dinamicos no TrialConversionScreen
- Checkout direto (1-click)
- Paywall dismiss fix
- Grace period 48h
- Cancelar emails apos conversao
- Resolver 0 resultados em setores criticos

**Semana 2 (P1 — Aceleracao):**
- Trial Value Dashboard
- CTAs contextuais
- Feature discovery emails
- Onboarding auto-tour
- Funnel tracking
- At-risk detection
- Pos-conversao welcome
- Social proof

**Semana 3 (P2 — Polish):**
- Cupom auto-apply
- PIX pagamento
- Tour expandido
- Cohort analysis
- Exit interview
- Trial extensions
- Help links em pontos de friccao

---

> **Fontes:** Codebase analysis (40+ arquivos), 10 beta testing sessions (session-005 a session-040), GTM Playbook Q2, GTM Readiness Assessment, Stories STORY-312/319, CRIT-044, COPY-369.
> **Proximo passo:** Converter cada item P0 em uma STORY com AC formais e executar via squad.
