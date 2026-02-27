# Diagnostic Checklist — SmartLic (50 usuarios pagantes)

## Criterio: Se QUALQUER item FAIL em "Critico", e BLOCKER.

---

## Critico (sem isso, perde usuario)

### Autenticacao
- [ ] Login email/senha funciona
- [ ] Sessao persiste apos refresh
- [ ] Logout limpa estado corretamente
- [ ] Token refresh funciona (sessao nao expira prematuramente)

### Busca (Core Value)
- [ ] Busca retorna resultados para setor valido
- [ ] SSE progress conecta e reporta progresso real
- [ ] Resultados sao relevantes (classificacao IA coerente)
- [ ] Dedup funciona (sem duplicatas visiveis)
- [ ] Busca completa em < 120s (caso tipico)

### Pagamento
- [ ] Stripe Checkout carrega com preco correto
- [ ] Webhook processa e `profiles.plan_type` atualiza
- [ ] Nenhum estado intermediario que confunda o usuario
- [ ] Grace period (3 dias) funciona

### Dados
- [ ] Pipeline items persistem apos refresh
- [ ] Export Excel contem todos os dados corretos
- [ ] Search sessions gravadas com user_id
- [ ] RLS impede acesso cross-usuario

---

## Importante (sem isso, usuario reclama)

### Experiencia
- [ ] Empty states tem orientacao (nao tela vazia)
- [ ] Loading states com feedback visual
- [ ] Erros mostram mensagem util (nao stack trace)
- [ ] Mobile responsivo (navegavel)

### Resiliencia
- [ ] Se PNCP cair, PCP compensa
- [ ] Se LLM falhar, classificacao defaults para REJECT
- [ ] Se ARQ job falhar, fallback summary aparece
- [ ] Circuit breaker tripa e recupera corretamente

### Operacional
- [ ] Health check endpoint funciona
- [ ] Sentry captura erros de producao
- [ ] Billing sync Stripe ↔ Supabase integro
- [ ] Quota enforcement funciona

---

## Desejavel (sem isso, operacao e fragil)

### Monitoramento
- [ ] SLO dashboard com dados atuais
- [ ] Email alerts configurados e disparando
- [ ] Prometheus/OTel metricas chegando
- [ ] Log sanitizer ativo (sem dados sensiveis nos logs)

### Volume
- [ ] 5 buscas sequenciais nao degradam
- [ ] Multi-UF (10+) completa sem timeout
- [ ] 3 exports sequenciais completam
- [ ] Rate limiting nao bloqueia uso legitimo

---

## Veredicto

| Categoria | Total | Pass | Fail | Skip |
|-----------|-------|------|------|------|
| Critico | 13 | | | |
| Importante | 11 | | | |
| Desejavel | 8 | | | |
| **Total** | **32** | | | |

**Resultado:** {GO | CONDITIONAL_GO | NO_GO}
- GO = Critico 100%, Importante >= 80%
- CONDITIONAL_GO = Critico 100%, Importante >= 60%
- NO_GO = Qualquer Critico FAIL
