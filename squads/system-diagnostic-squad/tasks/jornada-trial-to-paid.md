# jornada-trial-to-paid

## Metadata
- agent: usuario-trial
- elicit: false
- priority: critical
- estimated_time: 30min
- tools: [Playwright MCP, Supabase CLI, Stripe CLI, Read, Grep, Bash]

## Objetivo
Simular a jornada completa de um novo usuario: do primeiro acesso ate se tornar pagante.
Cada passo deve ser executado e evidenciado. Se algo falhar, documentar com precisao.

## Pre-requisitos
- Acesso a https://smartlic.tech (producao)
- Credenciais de teste ou capacidade de criar conta nova
- Acesso Supabase para verificar estado do DB
- Acesso Stripe dashboard/CLI para verificar eventos

## Steps

### Step 1: Acesso Inicial
**Acao:** Navegar para https://smartlic.tech
**Verificar:**
- [ ] Pagina carrega em menos de 3s
- [ ] Nenhum erro no console do browser
- [ ] CTA de signup visivel e claro
- [ ] HTTPS ativo, sem mixed content
**Evidencia:** Screenshot + tempo de carga + console log

### Step 2: Signup
**Acao:** Criar conta com email/senha
**Verificar:**
- [ ] Formulario valida inputs (email invalido, senha fraca)
- [ ] Signup completa sem erro
- [ ] Email de confirmacao chega (se habilitado)
- [ ] Redirect pos-signup faz sentido (nao joga no vazio)
- [ ] `profiles` row criada no Supabase com `plan_type = 'free_trial'`
- [ ] `trial_ends_at` definido corretamente (data futura)
**Evidencia:** Screenshot formulario + Supabase query `select * from profiles where email = '...'`

### Step 3: Onboarding / Primeira Experiencia
**Acao:** Seguir o fluxo pos-login como usuario novo
**Verificar:**
- [ ] Guided tour (Shepherd.js) aparece se configurado
- [ ] Usuario entende o que fazer em menos de 30s
- [ ] Nenhum estado vazio confuso (empty states com orientacao)
- [ ] Setor default ou selecao de setor funciona
**Evidencia:** Screenshot de cada tela do onboarding

### Step 4: Primeira Busca
**Acao:** Executar uma busca real com setor e UFs
**Verificar:**
- [ ] Busca inicia sem erro
- [ ] SSE progress aparece e avanca (nao trava)
- [ ] Resultados aparecem em tempo razoavel (<60s para busca simples)
- [ ] Resultados sao relevantes para o setor escolhido
- [ ] Classificacao IA mostra scores coerentes
- [ ] Quota foi decrementada corretamente
- [ ] `search_sessions` row criada no Supabase
**Evidencia:** Response body + SSE events + Supabase search_sessions query

### Step 5: Checkout / Pagamento
**Acao:** Iniciar upgrade para plano pago
**Verificar:**
- [ ] Botao de upgrade acessivel e claro
- [ ] Redirect para Stripe Checkout funciona
- [ ] Stripe Checkout carrega com preco correto
- [ ] Pagamento teste completa (Stripe test mode se disponivel)
- [ ] Webhook processa: `profiles.plan_type` atualiza
- [ ] Usuario volta para o app em estado correto (plano ativo)
- [ ] Nenhum estado intermediario confuso durante o processo
**Evidencia:** Stripe event log + Supabase profiles query antes/depois

### Step 6: Pos-Pagamento
**Acao:** Usar o sistema como pagante
**Verificar:**
- [ ] Quota reflete o novo plano
- [ ] Features do plano pago estao acessiveis
- [ ] Nenhum artefato de trial restante visivel
**Evidencia:** Screenshot dashboard + quota check

## Output
Documento com:
- Status de cada step: PASS | FAIL | DEGRADED | SKIPPED
- Evidencia para cada step
- Tempo total da jornada
- Bloqueios encontrados (se houver)
- Recomendacoes (se FAIL ou DEGRADED)
