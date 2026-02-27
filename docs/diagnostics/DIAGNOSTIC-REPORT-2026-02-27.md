# SmartLic Diagnostic Report
**Data:** 2026-02-27
**Versao:** v0.5
**Target:** 50 usuarios pagantes
**Executado por:** system-diagnostic-squad

## Veredicto Geral: NO_GO

### Criterios de Decisao
- **GO:** Zero BLOCKERs, zero HIGHs nao mitigados
- **CONDITIONAL_GO:** Zero BLOCKERs, HIGHs com mitigation plan e deadline
- **NO_GO:** Qualquer BLOCKER presente

**Razao principal:** Backend em crash loop (SIGSEGV) — nenhuma funcionalidade core acessivel.

---

## 1. Jornada Trial -> Pagante
**Agent:** usuario-trial
**Status:** FAIL (BLOCKED by SIGSEGV)

| Step | Status | Evidencia | Notas |
|------|--------|-----------|-------|
| Acesso Inicial | PASS | Screenshot `track-a-step1-landing.png` | HTTPS OK, CTA visivel, sem erros JS |
| Signup | PASS | Screenshot `track-a-step2-signup.png` | Validacao email/senha funciona, bloqueio disposable emails OK |
| Onboarding | NAO VALIDADO | - | Login com conta existente, tour nao disparou |
| Primeira Busca | FAIL | Screenshot `track-a-step4-search-FAILED.png` | POST /api/buscar retorna 502, SSE falhou 3x, polling 404 |
| Checkout/Pagamento | NAO VALIDADO | - | Backend down impede teste |
| Pos-Pagamento | NAO VALIDADO | - | Backend down impede teste |

**Bloqueios:** SIGSEGV crash loop no backend impede qualquer funcionalidade apos login.

---

## 2. Jornada Busca Diaria (Core Loop)
**Agent:** usuario-pagante
**Status:** FAIL (NOT EXECUTED — backend down)

| Step | Status | Evidencia | Notas |
|------|--------|-----------|-------|
| Login/Estado | NAO VALIDADO | - | Backend unreachable |
| Busca Multi-Fonte | NAO VALIDADO | - | 502 em todas tentativas |
| Classificacao IA | NAO VALIDADO | - | Depende de busca funcional |
| Pipeline Kanban | NAO VALIDADO | - | Depende de dados de busca |
| Export Excel | NAO VALIDADO | - | Depende de sessao de busca |
| Resumo IA | NAO VALIDADO | - | Depende de sessao de busca |
| Consistencia | NAO VALIDADO | - | Sem dados para validar |

**Core loop funcional:** NAO

---

## 3. Jornada Consultor (Volume)
**Agent:** consultor-licitacao
**Status:** FAIL (NOT EXECUTED — backend down)

| Step | Status | Evidencia | Notas |
|------|--------|-----------|-------|
| Buscas Sequenciais | NAO VALIDADO | - | Backend unreachable |
| Multi-Setor | NAO VALIDADO | - | Backend unreachable |
| Multi-UF Nacional | NAO VALIDADO | - | Backend unreachable |
| Quota/Limites | NAO VALIDADO | - | Backend unreachable |
| Exports Volume | NAO VALIDADO | - | Backend unreachable |

**Aguenta 50 users nesse padrao:** INDETERMINADO (impossivel avaliar com backend down)

---

## 4. Visibilidade Operacional
**Agent:** admin-operador
**Status:** FAIL (PARTIAL — backend down)

| Step | Status | Evidencia | Notas |
|------|--------|-----------|-------|
| Health Check | FAIL | `{"backend":"unreachable","latency_ms":5001}` | Frontend relata backend unreachable |
| Billing Sync | NAO VALIDADO | - | Backend down |
| Sentry/Errors | PARTIAL | Railway logs mostram SIGSEGV crash loop | Sentry pode estar recebendo crashes |
| SLO Dashboard | NAO VALIDADO | - | Backend down |
| Email Alerts | NAO VALIDADO | - | Backend down |
| Deteccao Problemas | FAIL | - | SIGSEGV nao esta gerando alerta automatico |

**Saberia antes do cliente:** NAO — crash loop nao gera alerta proativo.

---

## 5. Auditoria Tecnica (Falhas Silenciosas)
**Agent:** auditor-tecnico
**Status:** DEGRADED
**Risk Score:** 7/10

| Area | Status | Findings | Severidade |
|------|--------|----------|------------|
| Exception Handling | FAIL | 28 findings: 12x `except Exception: pass` em fluxos criticos | 2 BLOCKER, 10 HIGH |
| Circuit Breakers | WARN | Dual CB com thresholds conflitantes (5 vs 15), ComprasGov sem CB | 2 MEDIUM |
| Cache Integrity | WARN | Cache key exclui datas (pode servir dados de range errado) | 2 MEDIUM |
| Data Integrity | NAO VALIDADO | Requer queries no Supabase (nao executadas) | - |
| Webhook Reliability | OK | Stripe signature OK, handlers corretos, TOCTOU minor | 1 MEDIUM |
| Race Conditions | WARN | Pipeline drag-drop last-write-wins, quota fallback race | 2 MEDIUM |
| Fallback Paths | WARN | Fallbacks declarados mas nao testados em producao | MEDIUM |

**Top 3 Riscos:**
1. **SIGSEGV crash loop** — `cryptography>=46.0.5` + Gunicorn `--preload` causa fork-unsafe OpenSSL state. Workers completam startup e crasham no primeiro request.
2. **Exception silencing** — 12 ocorrencias de `except Exception: pass` em fluxos criticos (search_pipeline.py:149, consolidation.py:278, pncp_client.py:411/436/501). Erros sao engolidos silenciosamente, impedindo diagnostico.
3. **Circuit breaker inconsistency** — Dois sistemas CB com thresholds diferentes (5 vs 15). ComprasGov nao tem CB. Se uma fonte travar, nao ha protecao.

---

## Findings Consolidados

### BLOCKERs (devem ser resolvidos antes de 50 users)

| # | Finding | Agent | Impacto | Acao |
|---|---------|-------|---------|------|
| B1 | **SIGSEGV crash loop**: `cryptography>=46.0.5` + `--preload` causa segfault em workers Gunicorn | auditor-tecnico | 100% downtime — NENHUMA funcionalidade acessivel | Set `GUNICORN_PRELOAD=false` OU pin `cryptography==43.0.3` |
| B2 | **`except Exception: pass` em consolidation.py:278**: Task results descartados silenciosamente — fontes inteiras podem falhar sem ninguem saber | auditor-tecnico | Resultados de busca incompletos sem alerta | Substituir por `logger.error()` + Sentry capture |
| B3 | **`except Exception: pass` em search_pipeline.py:149**: Link builder falha silenciosa — licitacoes podem perder URLs | auditor-tecnico | Links quebrados em resultados | Substituir por `logger.warning()` + fallback URL |

### HIGHs (devem ser resolvidos em 2 semanas)

| # | Finding | Agent | Impacto | Acao |
|---|---------|-------|---------|------|
| H1 | Erros criticos logados como WARNING em 6 locais (deviam ser ERROR) | auditor-tecnico | Monitoramento nao dispara alertas | Reclassificar para logger.error() |
| H2 | Circuit breaker Redis fallback `except Exception: pass` (pncp_client.py:411/436/501) | auditor-tecnico | CB state perdido silenciosamente, pode nao tripar quando deveria | Log error + continue |
| H3 | SSE metrics exception swallowed (routes/search.py:302) | auditor-tecnico | Sem visibility de falhas SSE | Log + Sentry capture |
| H4 | State machine transitions swallowed (routes/search.py:957/1004) | auditor-tecnico | Search pode ficar em estado inconsistente | Log transitions |
| H5 | Callback handlers swallowed (consolidation.py:358/409/431/475) | auditor-tecnico | Callbacks de progresso falham sem alerta | Log warning |
| H6 | Dual CB systems com thresholds conflitantes (5 vs 15) | auditor-tecnico | Comportamento imprevisivel sob falha | Unificar thresholds |
| H7 | ComprasGov sem circuit breaker | auditor-tecnico | Se ComprasGov travar, sem protecao | Adicionar CB |
| H8 | Cache key exclui datas — pode servir resultados de periodo errado | auditor-tecnico | Usuario recebe dados stale sem saber | Incluir date_from/date_to no cache key |
| H9 | Sem alerta proativo para crash loops | admin-operador | Downtime descoberto por usuarios, nao por operadores | Implementar healthcheck externo (UptimeRobot/Betterstack) |
| H10 | Busca nao e resiliente a falha total de backend | usuario-trial | Core value proposition quebra completamente | Arquitetura precisa de graceful degradation |

### MEDIUMs (backlog priorizado)

| # | Finding | Agent | Impacto | Acao |
|---|---------|-------|---------|------|
| M1 | TOCTOU race no Stripe webhook idempotency (webhooks/stripe.py:109-146) | auditor-tecnico | Webhook duplicado pode processar 2x (raro) | Use INSERT ON CONFLICT |
| M2 | Pipeline drag-drop last-write-wins (routes/pipeline.py:208-261) | auditor-tecnico | Moves rapidos perdem dados | Optimistic locking (version column) |
| M3 | Quota fallback read-modify-write race (quota.py:456-477) | auditor-tecnico | Fallback path pode over-count | Use transaction |
| M4 | Dual L2 cache paths com TTLs diferentes | auditor-tecnico | Inconsistencia entre cache layers | Unificar TTLs |
| M5 | SWR background revalidation sem limit de concorrencia efetivo | auditor-tecnico | Thundering herd possivel | Limit concurrent revalidations |

### Items NAO VALIDADOS (sem evidencia)

| # | Item | Motivo | Risco |
|---|------|--------|-------|
| NV1 | Login email/senha funciona | Backend down | CRITICO — nao se sabe se auth funciona |
| NV2 | Sessao persiste apos refresh | Backend down | CRITICO |
| NV3 | Token refresh funciona | Backend down | CRITICO |
| NV4 | Busca retorna resultados para setor valido | Backend down | CRITICO — core value |
| NV5 | SSE progress conecta e reporta progresso real | Backend down | CRITICO |
| NV6 | Classificacao IA coerente | Backend down | CRITICO |
| NV7 | Dedup funciona | Backend down | IMPORTANTE |
| NV8 | Busca completa em < 120s | Backend down | IMPORTANTE |
| NV9 | Stripe Checkout carrega com preco correto | Backend down | CRITICO |
| NV10 | Webhook processa e plan_type atualiza | Backend down | CRITICO |
| NV11 | Pipeline items persistem apos refresh | Backend down | CRITICO |
| NV12 | Export Excel contem dados corretos | Backend down | IMPORTANTE |
| NV13 | RLS impede acesso cross-usuario | Requer queries Supabase | CRITICO |
| NV14 | Data integrity (search_sessions sem user_id, etc) | Requer queries Supabase | MEDIO |
| NV15 | Empty states tem orientacao | Backend down | IMPORTANTE |
| NV16 | Se PNCP cair, PCP compensa | Backend down | IMPORTANTE |
| NV17 | Se LLM falhar, classificacao defaults para REJECT | Backend down | IMPORTANTE |
| NV18 | Billing sync Stripe <-> Supabase integro | Backend down | CRITICO |
| NV19 | Quota enforcement funciona | Backend down | IMPORTANTE |
| NV20 | SLO dashboard com dados atuais | Backend down | DESEJAVEL |
| NV21 | Email alerts configurados e disparando | Backend down | DESEJAVEL |

---

## Checklist Summary

| Categoria | Total | Pass | Fail | Skip/NV |
|-----------|-------|------|------|---------|
| Critico | 13 | 1 | 1 | 11 |
| Importante | 11 | 0 | 2 | 9 |
| Desejavel | 8 | 0 | 0 | 8 |
| **Total** | **32** | **1** | **3** | **28** |

**Resultado:** **NO_GO**
- Criticos com FAIL (busca 502, health check unreachable)
- 28 de 32 items nao puderam ser validados
- BLOCKER primario: SIGSEGV crash loop impede TODA funcionalidade

---

## Analise Estrutural: Por que a busca nao deveria derrubar tudo

O usuario acertou em cheio: "fontes instaveis nao sao desculpas...busca e async cazzo".

**Problema fundamental:** O backend SmartLic e um monolito onde QUALQUER falha no startup (neste caso, cryptography/OpenSSL fork-safety) derruba TODAS as funcionalidades — login, billing, pipeline, exports, TUDO. A busca deveria ser o componente mais resiliente, nao o mais fragil.

**O que deveria acontecer com fontes instaveis:**
1. PNCP down -> retorna PCP + ComprasGov (ja implementado no codigo, mas morto com o SIGSEGV)
2. Todas as fontes down -> retorna cache stale com aviso "dados de Xh atras"
3. Backend lento -> SSE mantem usuario informado do progresso real
4. Backend crash -> health checks externos detectam e alertam ANTES do usuario descobrir

**O que acontece hoje:** Worker SIGSEGV -> 502 -> usuario ve "servico indisponivel" -> sem alerta -> sem recuperacao automatica.

---

## Proximos Passos (prioridade de execucao)

### Imediato (hoje)
1. **FIX SIGSEGV:** Set `GUNICORN_PRELOAD=false` em Railway env vars (fix imediato, zero downtime)
2. **Alternativa:** Pin `cryptography==43.0.3` se preload for necessario para performance
3. **Verificar:** Apos fix, confirmar que workers sobrevivem e health check retorna OK

### Urgente (proximos 3 dias)
4. **Exception cleanup:** Substituir os 12x `except Exception: pass` por logging adequado
5. **External monitoring:** Configurar UptimeRobot/Betterstack para health check com alerta SMS/email
6. **CB unification:** Unificar thresholds dos circuit breakers + adicionar CB para ComprasGov

### Importante (proxima semana)
7. **Cache key fix:** Incluir date_from/date_to no cache key
8. **Log severity:** Reclassificar 6 WARNING criticos para ERROR
9. **Re-executar diagnostico completo** apos SIGSEGV fix para validar os 28 items NAO VALIDADOS

### Desejavel (2 semanas)
10. **Race conditions:** TOCTOU no webhook, pipeline optimistic locking
11. **Graceful degradation:** Se backend crashar, frontend mostra ultimo dado cached

---

*Gerado por system-diagnostic-squad em 2026-02-27*
*Auditor: auditor-tecnico (code review completo)*
*Tracks A-D: parcialmente executados (SIGSEGV impediu validacao funcional)*
*Track E: executado integralmente via code review*
