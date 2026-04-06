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

- [ ] **P1 | M** — Reordenar sequencia de emails: activation nudge (Day 2) chega DEPOIS do email de engagement (Day 3). Se usuario nao buscou nada, email Day 3 mostra "0 oportunidades analisadas".
  - Arquivo: `backend/services/trial_email_sequence.py` linhas 48-79
  - Acao: Day 1: activation nudge (se 0 buscas) → Day 3: engagement (se buscas > 0) → condicional

- [ ] **P1 | M** — Adicionar emails de feature discovery: emails atuais focam em VALOR (R$) mas nunca explicam features (pipeline, Excel export, resumo IA, alertas). Usuario nao sabe o que tem disponivel.
  - Arquivo: `backend/templates/emails/trial.py`
  - Acao: Day 2: "Conheca o Pipeline" | Day 5: "Exporte para Excel" | Day 8: "IA classifica para voce"

- [ ] **P1 | S** — Segmentar emails por engagement: high-value trials (R$10M+ analisados) recebem mesma mensagem que low-value. Sem personalizacao por setor, regiao, ou perfil de empresa.
  - Arquivo: `backend/services/trial_email_sequence.py`
  - Acao: Consultar `trial_stats` antes de enviar, branch por tier (high/medium/low)

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

- [ ] **P1 | S** — Pipeline limit de 5 items e muito restritivo: funnel B2B tipico precisa de 10-20 oportunidades. Usuarios atingem o limite antes de avaliar o pipeline como ferramenta.
  - Arquivo: `backend/config/features.py` linhas 66-70, `frontend/app/pipeline/page.tsx`
  - Acao: Aumentar para 15 items, ou remover limite e manter paywall so em Excel/IA

### 2.2 Sem grace period no trial

- [x] **P0 | M** — ~~Grace period 48h para trial~~ RESOLVIDO: `quota.py` agora concede 48h grace period com ate 3 buscas apos expiracao. Config via `TRIAL_GRACE_HOURS` e `TRIAL_GRACE_MAX_SEARCHES` env vars.
  - Arquivo: `backend/quota.py` L948-987

- [ ] **P1 | M** — Manter acesso read-only ao pipeline apos trial expirar: usuario pode VER pipeline (GET funciona) mas nao tem CTA de conversao na pagina. Oportunidade desperdicada.
  - Arquivo: `frontend/app/pipeline/page.tsx`
  - Acao: Adicionar banner "Seu trial expirou. Assine para continuar gerenciando oportunidades." com CTA

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

- [ ] **P1 | S** — Corrigir inconsistencia de pricing no banner: TrialExpiringBanner diz "a partir de R$ 9,90/dia" (= R$297/mes anual) mas CTA principal diz "R$ 397/mes" (mensal). Usuario nao sabe o preco real.
  - Arquivo: `frontend/app/components/TrialExpiringBanner.tsx` linha 60
  - Acao: Unificar messaging — mostrar preco mensal com "(ou R$9,90/dia no plano anual)"

### 3.2 Cupom e metodos de pagamento

- [ ] **P1 | M** — Implementar auto-apply de cupom na URL: email Day 16 envia link com `?coupon=TRIAL_COMEBACK_20` mas `/planos` nao le o parametro. Usuario precisa digitar codigo manualmente.
  - Arquivo: `frontend/app/planos/page.tsx`, `backend/routes/billing.py`
  - Evidencia: `backend/services/trial_email_sequence.py` linha 83 — define `TRIAL_COMEBACK_COUPON`
  - Acao: Ler `searchParams.coupon`, passar para `POST /v1/checkout` como `promotion_code`

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

- [ ] **P1 | M** — Mostrar ROI estimado em momentos de alto valor: quando usuario encontra 10+ resultados relevantes, nenhum CTA contextual aparece.
  - Arquivo: `frontend/app/buscar/components/SearchResults.tsx`
  - Evidencia: `docs/stories/STORY-312-trial-upsell-ctas-contextuais.md` — "faltam CTAs contextuais"
  - Acao: Apos busca com >5 resultados, mostrar "Voce encontrou R$X em oportunidades. Com SmartLic Pro, monitore automaticamente."

- [ ] **P1 | S** — Incluir valor acumulado nos emails de trial: emails Day 3 e Day 10 mostram contagem de buscas mas nao o VALOR em R$ que o usuario ja descobriu.
  - Arquivo: `backend/templates/emails/trial.py`, `backend/services/trial_stats.py`
  - Acao: Consultar trial_stats e incluir "Voce ja descobriu R$X.XXX.XXX em oportunidades"

### 4.2 Momentos de conversao desperdicados

- [ ] **P1 | M** — CTAs contextuais pos-acao: nenhum upsell aparece quando usuario exporta Excel, adiciona ao pipeline, ou gera resumo IA. Esses sao os momentos de MAIOR perceived value.
  - Arquivo: `frontend/components/billing/TrialUpsellCTA.tsx` (existe mas limitado)
  - Evidencia: STORY-312 — "CTAs de conversao sao genericos e aparecem apenas quando trial expira"
  - Acao: Trigger upsell CTA apos: download Excel, add pipeline (5o item), gerar resumo IA

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

- [ ] **P1 | M** — Cross-sector collision rate 22.7%: descricoes de licitacoes naturalmente matcheiam multiplos setores. "construcao de UBS" aparece em engenharia E saude.
  - Arquivo: `backend/filter.py`, benchmark em `backend/docs/audit/precision-recall-benchmark-2026-02-22.md`
  - Acao: Implementar sector affinity scoring — priorizar setor primario, mostrar secundario como tag

- [ ] **P1 | M** — Setores com recall baixo: materiais_eletricos 73.3%, engenharia_rodoviaria 86.7%. Trial users nesses setores perdem oportunidades reais.
  - Arquivo: `backend/sectors_data.yaml`
  - Acao: Expandir keyword lists para setores com recall < 85%

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

- [ ] **P1 | S** — Onboarding pode ser skipado: usuario vai direto para `/buscar` e ve empty state sem orientacao. Nenhum redirect para onboarding.
  - Arquivo: `frontend/app/buscar/components/OnboardingEmptyState.tsx`
  - Acao: Se `profile_context` vazio, redirecionar para `/onboarding` com banner "Configure seu perfil para melhores resultados"

- [ ] **P1 | M** — Primeira analise pode falhar silenciosamente: se `require_active_plan(user)` falha (edge case), usuario ve spinner infinito sem mensagem de erro.
  - Arquivo: `backend/routes/onboarding.py` linha 56, `frontend/app/onboarding/components/OnboardingStep3.tsx`
  - Acao: Adicionar timeout de 30s + erro amigavel + retry button

- [ ] **P1 | S** — Onboarding Step 3 sem feedback de sucesso: diz "Isso leva ~15 segundos" mas se retorna 0 resultados, nao ha orientacao sobre o que fazer.
  - Arquivo: `frontend/app/onboarding/components/OnboardingStep3.tsx` linhas 61-69
  - Acao: Se 0 resultados, sugerir: expandir UFs, mudar faixa de valor, tentar outro setor

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

- [ ] **P1 | L** — Implementar tracking de funnel completo: signup → first login → onboarding complete → first search → value generated → paywall hit → checkout initiated → payment completed. Nao existe hoje.
  - Arquivo: `backend/analytics_events.py` (Mixpanel), frontend tracking
  - Acao: Adicionar events Mixpanel em cada stage, criar funnel report

- [ ] **P1 | M** — Implementar cohort analysis: nao ha como medir conversion rate por dia, setor, valor gerado, ou engagement level. Impossivel otimizar o que nao se mede.
  - Arquivo: `backend/analytics_events.py`
  - Acao: Adicionar properties `trial_day`, `total_value`, `searches_count`, `engagement_tier` em cada event

- [ ] **P1 | M** — Tracking de feature usage: nao sabemos se usuarios usam pipeline, Excel, IA summary, alertas. Sem isso, nao sabemos quais features drive conversion.
  - Arquivo: Frontend analytics calls
  - Acao: Track `feature_used` event com `feature_name` property (pipeline, excel, ai_summary, alerts)

### 7.2 Deteccao de risco

- [ ] **P1 | L** — Cron de deteccao de at-risk trials: nenhum job identifica trials que nao buscaram ate Day 2, nao geraram >R$100k ate Day 10, ou usaram <10% da quota ate Day 7.
  - Arquivo: NOVO `backend/cron/trial_risk_detection.py`
  - Acao: Job diario que categoriza trials em healthy/at-risk/critical, trigger email ou acao especifica

- [ ] **P2 | M** — Dashboard admin de trial conversion: admin nao tem visibilidade sobre taxa de conversao, drop-off points, ou trials at-risk.
  - Arquivo: `frontend/app/admin/`, `backend/routes/admin.py`
  - Acao: Pagina admin com: trials ativos, conversion rate, at-risk list, engagement heatmap

- [ ] **P3 | M** — A/B testing capability: nao ha como testar variantes de messaging, pricing display, ou CTA copy. Sem variant parameter nos analytics events.
  - Arquivo: Frontend + backend analytics
  - Acao: Adicionar `variant` property em events de conversao, implementar feature flag por usuario

---

## 8. POS-CONVERSAO & RETENCAO

### 8.1 Experiencia pos-pagamento

- [ ] **P1 | M** — Criar tela de boas-vindas pos-conversao: usuario paga no Stripe e volta para `/planos/obrigado` generico. Nenhuma confirmacao de "agora voce tem acesso completo" com lista de features desbloqueadas.
  - Arquivo: `frontend/app/planos/obrigado/page.tsx`
  - Acao: Tela "Bem-vindo ao SmartLic Pro!" com: features desbloqueadas, proximos passos, "Configure alertas para nao perder oportunidades"

- [ ] **P1 | S** — Estado UI stale apos conversao: paywall nao desaparece ate reload. Usuario paga e ainda ve resultados blur.
  - Arquivo: `frontend/components/billing/TrialPaywall.tsx`
  - Acao: Polling de subscription status apos redirect do Stripe, ou invalidar cache de plano no callback

- [ ] **P1 | M** — Email de boas-vindas pos-conversao: nenhum email confirma assinatura com next steps. Usuario fica sem orientacao apos pagar.
  - Arquivo: `backend/webhooks/handlers/checkout.py`
  - Acao: No webhook `checkout.session.completed`, enviar email "Sua assinatura esta ativa" com: link para alertas, link para pipeline, dica de busca avancada

### 8.2 Prevencao de churn precoce

- [ ] **P1 | L** — Implementar health score do usuario: sem metrica de engagement pos-conversao. Cancellamentos precoces sao silenciosos.
  - Arquivo: NOVO `backend/services/user_health_score.py`
  - Evidencia: GTM Playbook — "Churn precoce = HIGH impact risk, so ligacao pessoal como mitigacao"
  - Acao: Score baseado em: buscas/semana, pipeline items, exports, logins. Alert admin quando score cai.

- [ ] **P2 | M** — Exit interview obrigatorio no cancelamento: Stripe permite cancel direto sem feedback. Nao sabemos POR QUE usuarios cancelam.
  - Arquivo: `frontend/app/conta/`, `backend/routes/billing.py`
  - Acao: Modal pre-cancelamento: "O que podemos melhorar?" com opcoes (preco, qualidade, nao uso, outro)

- [ ] **P2 | M** — Implementar trial extension como mecanismo de retencao: nenhuma logica para "Complete seu perfil por +3 dias" ou "Indique um amigo por +7 dias".
  - Arquivo: `backend/quota.py`, `backend/services/trial_email_sequence.py`
  - Acao: Endpoints para extensao de trial com condicoes (profile complete, referral, feedback)

---

## 9. TRUST & SOCIAL PROOF

- [ ] **P1 | M** — Adicionar social proof na UI do trial: nenhum "X empresas usam SmartLic", nenhum testimonial, nenhum rating. Landing page tem "Proof of Value" mas app nao.
  - Arquivo: `frontend/app/components/TrialConversionScreen.tsx`, `frontend/app/planos/page.tsx`
  - Acao: Adicionar 2-3 testimonials reais, numero de empresas, selo "Dados oficiais PNCP"

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

- [ ] **P1 | S** — Quota progress nao visivel durante trial: usuario nao ve "247 / 1000 buscas usadas este mes". Surpreendido quando bloqueado.
  - Arquivo: `frontend/app/buscar/page.tsx`
  - Backend: `backend/quota.py` `get_monthly_quota_used()` — endpoint existe
  - Acao: Adicionar badge discreto no header ou sidebar: "847/1000 buscas restantes"

- [ ] **P2 | S** — TrialCountdown badge nao explica fases: mostra "5 dias restantes" mas nao diz que Day 8 traz restricoes. Usuario nao entende "5 dias = acesso limitado ja ativo".
  - Arquivo: `frontend/app/components/TrialCountdown.tsx`
  - Acao: Tooltip no hover: "Seu trial tem acesso completo ate Day 7. Apos, alguns recursos ficam limitados."

---

## RESUMO EXECUTIVO

### Distribuicao por severidade

| Severidade | Quantidade | Resolvidos | % do Total |
|------------|-----------|-----------|------------|
| P0 (Bloqueante) | 13 | **13 (100%)** | 27% |
| P1 (Critico) | 22 | 0 | 46% |
| P2 (Importante) | 12 | 0 | 25% |
| P3 (Otimizacao) | 2 | 0 | 4% |
| **TOTAL** | **49** | **13** | **100%** |

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
