# CRIT-017 — "Application not found" Raw Error Leaks to Users

**Tipo:** Bug / UX Critico
**Prioridade:** P0 (Blocker — afeta ALL pages quando backend offline)
**Criada:** 2026-02-22
**Status:** Concluida
**Origem:** Teste de primeiro uso real em producao (UX Expert audit)

---

## Problema

Quando o backend Railway esta offline, reiniciando, ou sem instancias ativas, o texto raw **"Application not found"** aparece diretamente na UI para o usuario. Esse texto e a resposta padrao do Railway quando nenhum container esta rodando — NAO e uma mensagem do SmartLic.

### Evidencias (2026-02-22, ~12:14 UTC)

**Paginas afetadas:**
- `/buscar` — "Application not found" em banner vermelho-claro, com botao "Tentar novamente (0:24)"
- `/pipeline` — "Application not found" em banner vermelho-claro, ACIMA do empty state educativo
- `/dashboard` — skeletons eternos sem nenhuma mensagem (ver UX-338)

**Console:**
- 502 em `/api/health`
- 502 em `/api/buscar`
- 404 em `/api/buscar` (apos retry)
- 502 em `/api/analytics?endpoint=summary|searches-over-time|top-dimensions`
- 404 em `/api/pipeline?limit=200`

**Railway logs mostram:** Backend estava UP e respondendo 200 em `/health` e `/v1/me`. O problema foi que o **frontend Next.js container reiniciou** (2 deployments simultaneous: `e8d2571b` stopping + `653c4e86` starting), causando ~60s de downtime no proxy.

### Root Cause

O proxy Next.js (`app/api/*/route.ts`) faz fetch para `BACKEND_URL/...` e, quando recebe erro, retorna o response body RAW como `{ error: responseBody }`. Quando o upstream retorna HTML ou texto plain do Railway/infra, esse texto vaza para o frontend.

### Impacto

- **Primeiro uso destruido:** Novo usuario ve "Application not found" e pensa que o produto nao existe/esta quebrado
- **Perda de confianca:** Texto tecnico em ingles para publico BR nao-tecnico
- **Multi-pagina:** Afeta buscar, pipeline, dashboard, historico — qualquer pagina com API call

---

## Solucao

### Abordagem: Interceptar erros nao-JSON no proxy e transformar em mensagens amigaveis

**Principio:** O usuario NUNCA deve ver texto que nao foi escrito pelo SmartLic.

### Criterios de Aceitacao

#### Proxy Layer (Frontend API Routes)

- [x] **AC1:** Proxy detecta respostas nao-JSON (Content-Type != application/json) e retorna erro estruturado:
  ```json
  {
    "error": "Nossos servidores estao sendo atualizados. Tente novamente em alguns instantes.",
    "error_code": "BACKEND_UNAVAILABLE",
    "retry_after_seconds": 30
  }
  ```
- [x] **AC2:** Proxy detecta status 502/503/504 e retorna mensagem amigavel mesmo que body seja JSON
- [x] **AC3:** Proxy detecta body contendo "Application not found" (Railway) e mapeia para `BACKEND_UNAVAILABLE`
- [x] **AC4:** Proxy detecta body contendo "Bad Gateway" (nginx) e mapeia para `BACKEND_UNAVAILABLE`
- [x] **AC5:** Header `X-Error-Source: proxy` adicionado quando erro e sintetico (nao veio do backend)

#### Frontend Components

- [x] **AC6:** `/buscar` — mensagem de erro mostra texto em PT-BR, nunca texto raw do proxy
- [x] **AC7:** `/pipeline` — erro de fetch mostra banner azul "Estamos atualizando..." (nao vermelho com texto em ingles)
- [x] **AC8:** `/dashboard` — (delegado para UX-338) mas deve usar mesma infraestrutura de erro
- [x] **AC9:** Texto "Application not found" NUNCA aparece em nenhuma tela, em nenhum cenario

#### Fallback UX

- [x] **AC10:** Quando backend indisponivel, cada pagina mostra estado graceful:
  - Buscar: "Servidores em atualizacao. Sua busca sera executada assim que voltarmos." + timer retry
  - Pipeline: Empty state normal (sem banner de erro)
  - Dashboard: "Painel temporariamente indisponivel" + ultimo dado cacheado se houver
  - Historico: Dados do Supabase (nao depende do backend)

#### Testes

- [x] **AC11:** Teste unitario: proxy retorna erro estruturado quando backend retorna HTML
- [x] **AC12:** Teste unitario: proxy retorna erro estruturado quando backend retorna 502
- [x] **AC13:** Teste unitario: proxy retorna erro estruturado quando fetch throws (network error)
- [x] **AC14:** Teste frontend: componente de busca renderiza mensagem PT-BR para erro BACKEND_UNAVAILABLE
- [x] **AC15:** Nenhum teste existente quebra

---

## Arquivos Envolvidos

### Criar/Modificar
- `frontend/lib/proxy-error-handler.ts` — **NOVO**: funcao centralizada para sanitizar erros de proxy
- `frontend/app/api/buscar/route.ts` — usar proxy-error-handler
- `frontend/app/api/analytics/route.ts` — usar proxy-error-handler
- `frontend/app/api/pipeline/route.ts` — usar proxy-error-handler
- `frontend/app/api/admin/[...path]/route.ts` — usar proxy-error-handler
- `frontend/app/api/feedback/route.ts` — usar proxy-error-handler
- `frontend/app/api/me/route.ts` — usar proxy-error-handler (story listed as user/route.ts)
- `frontend/app/api/trial-status/route.ts` — usar proxy-error-handler (bonus: same bug as analytics)
- `frontend/lib/error-messages.ts` — adicionar mensagens para BACKEND_UNAVAILABLE + defense-in-depth

### Testes
- `frontend/__tests__/proxy-error-handler.test.ts` — **NOVO** (31 tests)
- `frontend/__tests__/buscar-proxy-errors.test.ts` — **NOVO** (11 tests)

---

## Estimativa

- **Complexidade:** Media (pattern unico replicado em ~8 proxies)
- **Risco:** Baixo (proxy layer isolada, nao toca em componentes de UI)
- **Dependencias:** Nenhuma. Pode ser implementada independentemente.
- **Prioridade de execucao:** ANTES de qualquer feature nova — este e o bug mais visivel em producao.

---

## Notas

- O erro "Application not found" tambem pode ocorrer quando Railway faz cold start do backend (primeiros ~5s)
- O CRIT-008 ja implementou auto-retry e BackendStatusIndicator, mas nao sanitiza o texto do erro
- O CRIT-009 implementou SearchErrorCode mas o proxy so extrai metadata de respostas JSON
- Esta story complementa CRIT-008/009 fechando a lacuna: **erros nao-JSON do upstream**
