# UX Production Audit — Sprint 1-3 Validation

**Data:** 2026-02-23 02:05–02:20 UTC
**Auditor:** @ux-design-expert (Uma)
**Ambiente:** Produção (smartlic.tech), logado como tiago.sasaki@gmail.com (admin)
**Backend status:** DEGRADADO — 503/524 durante toda a sessão

---

## Contexto

Validação em produção do trabalho de 3 sprints recentes:

| Sprint | Stories | Tipo |
|--------|---------|------|
| Sprint 1 (BLOCKER) | CRIT-027, CRIT-028, UX-353 | Fixes + Polish |
| Sprint 2 (CRITICAL) | UX-348, UX-349, UX-350 | Features |
| Sprint 3 (POLISH) | UX-351, UX-352 | Polish |

---

## Resumo Executivo

| Categoria | Resultado |
|-----------|-----------|
| Stories validáveis | 5 de 8 (backend down impediu 3) |
| Bugs novos encontrados | **7** (2 P1, 4 P2, 1 P3) |
| Funcionalidades confirmadas OK | **14** |
| Bloqueado por infra | UX-348 badges, UX-349 Excel, UX-350 AI summary |

---

## Validação por Story

### UX-353 — Acentuação e Consistência Textual

| Item | Esperado | Encontrado | Veredicto |
|------|----------|------------|-----------|
| Sidebar "Histórico" | Com acento | "Histórico" ✅ | **PASS** |
| Sidebar "Mensagens" → "Suporte" | Suporte | Sidebar: "Suporte" ✅ | **PASS** |
| Page header "Mensagens" | "Suporte" | Ainda "Mensagens" | **BUG P3** — inconsistência sidebar vs header |
| Header bar Histórico | "Histórico" | `Hist\u00f3rico` (raw unicode) | **BUG P2** — encoding não resolvido |
| Error message buscar | "licitações" | "licitacoes" (sem acento) | **BUG P2** — accent missing |
| Pipeline empty state | Acentos corretos | Todos corretos ✅ | **PASS** |
| Conta page labels | PT-BR | Todos corretos ✅ | **PASS** |
| Footer logged-in area | CONFENGE | "CONFENGE Avaliações e Inteligência Artificial LTDA" ✅ | **PASS** |
| Landing page footer | Sem "servidores públicos" | Removido ✅ | **PASS** |

**Veredicto: 6/9 PASS — 3 bugs residuais**

### CRIT-027 — Search State Machine Correctness

| Item | Esperado | Encontrado | Veredicto |
|------|----------|------------|-----------|
| State reset on new search | result=null, rawCount=0 | Resultados antigos limpam ao trocar setor ✅ | **PASS** |
| No premature empty state | Empty só quando !loading | Empty state apareceu durante nova busca (Engenharia sobre Vestuário) | **BUG P1** |
| UF progress grid | Mostra progresso real | Grid aparece e atualiza corretamente ✅ | **PASS** |
| SSE connection | Conecta e atualiza | Funciona quando backend saudável, ERR_QUIC_PROTOCOL_ERROR quando degradado | **PASS** (infra) |
| Loading indicator cleanup | Remove quando completo | "Atualizando dados em tempo real..." persistiu por 30s+ após busca Vestuário | **BUG P2** |

**Veredicto: 3/5 PASS — 1 P1 (state bleed), 1 P2 (loading stuck)**

### CRIT-028 — Dashboard Without Eternal Skeletons

| Item | Esperado | Encontrado | Veredicto |
|------|----------|------------|-----------|
| Dashboard loads data | Data ou empty state | Skeleton loaders eternos (15s+) | **BUG P1** |
| usePlan fallback | localStorage cache | Console: "using cached plan" ✅ (warnings) | **PASS** (degraded) |
| No error storm | Max 5 retries | 12 warnings usePlan em /conta (6 attempts) | **BUG P2** |
| Console errors | Downgraded to warn | Warnings (não errors) ✅ | **PASS** |

**Veredicto: 2/4 PASS — 1 P1 (skeletons), 1 P2 (retry count)**

### UX-348 — Viability Badges + Positive Header + Edital Links

**BLOQUEADO POR INFRA** — Backend retornou 0 resultados para todos setores (503/524). Não foi possível validar viability badges, header positivo, ou links de edital com resultados reais.

**Landing page validation:** O card de exemplo na landing mostra "RECOMENDADA" + "92% compatível" + viability badges corretamente ✅

### UX-349 — Excel Button Visible + Google Sheets

**BLOQUEADO POR INFRA** — Sem resultados, botão Excel não aparece. Proxy Google Sheets criado (code review confirmou).

### UX-350 — AI Summary Timeout + Strategic Recommendations

**BLOQUEADO POR INFRA** — Sem resultados, summary section não renderiza. 30s timeout + fallback confirmados em code review.

### UX-351 — Histórico Funcional

| Item | Esperado | Encontrado | Veredicto |
|------|----------|------------|-----------|
| Dedup | Sem duplicatas | Engenharia 20:40 aparece 2x (183.7s vs 0.5s), Vestuário 20:37 aparece 2x | **BUG P1** |
| UF formatting | "Todo o Brasil" para 27 UFs | "Todo o Brasil" ✅ | **PASS** |
| Status labels PT | "Concluída", "Em andamento", "Falhou" | Todos em PT-BR ✅ | **PASS** |
| Portuguese errors | "O servidor reiniciou..." | "Server restart — retry recommended" (inglês!) | **BUG P2** |
| Sector names | Nome completo | Slugs: "vestuario", "engenharia" | **BUG P2** |
| Button labels | PT-BR | "Repetir busca", "Tentar novamente" ✅ | **PASS** |
| Polling auto-refresh | Status atualiza | Não pôde validar (buscas falharam) | **N/A** |
| Result with data | Mostra contagem e valor | 153 resultados, R$ 1.585.028.056,56 ✅ | **PASS** |

**Veredicto: 4/7 PASS — 1 P1 (dedup), 2 P2 (english error, slugs)**

### UX-352 — Badge Cleanup, Visual Hierarchy, No Jargon

| Item | Esperado | Encontrado | Veredicto |
|------|----------|------------|-----------|
| "Oportunidades recentes" | Substituiu "Últimos 10 dias" | "Oportunidades recentes" ✅ | **PASS** |
| "Volte amanhã" | Mensagem de encorajamento | "Volte amanhã para novas oportunidades." ✅ | **PASS** |
| Sem "Fonte Oficial" badge | Removido | N/A (sem resultados para verificar) | **BLOQUEADO** |
| Sem "Palavra-chave" badge | Removido | N/A (sem resultados) | **BLOQUEADO** |
| "Alta relevância" | Substituiu "Alta confiança" | N/A (sem resultados) | **BLOQUEADO** |
| Suggestions box | Sugestões úteis no empty state | 3 sugestões claras em PT-BR ✅ | **PASS** |

**Veredicto: 3/3 validáveis PASS — 3 bloqueados por infra**

---

## Funcionalidades Confirmadas OK

1. Sidebar labels corretos ("Histórico", "Suporte", "Pipeline") ✅
2. Landing page copy consistente com área logada ✅
3. UF Progress Grid atualiza em tempo real via SSE ✅
4. 5-stage progress pipeline visual (Consultando → Buscando → Filtrando → Avaliando → Excel) ✅
5. BackendStatusIndicator red/green dot funcional (CRIT-008) ✅
6. Auto-retry countdown com timer circular (CRIT-008) ✅
7. Error detail expandível "Detalhes técnicos" (CRIT-009) ✅
8. CRIT-018 retry storm prevention — apenas 1 error em console para analytics ✅
9. Pipeline empty state em PT-BR com instruções claras ✅
10. Conta page com seções corretas (perfil, senha, LGPD) ✅
11. Search form "Buscar por: Setor / Termos Específicos" ✅
12. Sector dropdown com 15 setores + descrições ✅
13. Footer com CNPJ CONFENGE correto ✅
14. Theme toggle (Light/Dark) presente em todas páginas ✅

---

## Bugs Encontrados

### P1 — Críticos (2)

| # | Onde | Bug | Story |
|---|------|-----|-------|
| 1 | /historico | **Dedup falha**: Entradas duplicadas (mesmo setor + timestamp, duração diferente: 183s vs 0.5s). Cache hit cria segunda entrada. | UX-351 |
| 2 | /buscar | **State bleed**: Empty state da busca anterior ("302 editais") permanece visível quando nova busca inicia para setor diferente | CRIT-027 |

### P2 — Importantes (4)

| # | Onde | Bug | Story |
|---|------|-----|-------|
| 3 | /historico header bar | **Unicode escape**: "Hist\u00f3rico" renderiza como texto raw em vez de "Histórico" | UX-353 |
| 4 | /historico entries | **English error msg**: "Server restart — retry recommended" em vez de "O servidor reiniciou. Tente novamente." | UX-351 |
| 5 | /historico entries | **Sector slugs**: "vestuario", "engenharia" em vez de "Vestuário e Uniformes", "Engenharia, Projetos e Obras" | UX-351 |
| 6 | /buscar error | **Missing accent**: "Erro ao buscar licitacoes" — falta acento em "licitações" | UX-353 |

### P3 — Cosméticos (1)

| # | Onde | Bug | Story |
|---|------|-----|-------|
| 7 | /mensagens | **Label inconsistência**: Sidebar diz "Suporte", page header diz "Mensagens" | UX-353 |

### Observação Adicional (Infra, não UX)

- **usePlan retry storm**: `/conta` gera 12 console warnings (6 fetch attempts). O hook `useFetchWithBackoff` de CRIT-018 não cobre o `usePlan` hook.
- **Dashboard skeletons eternos**: Quando analytics API retorna 503, skeletons nunca resolvem para empty state. O CRIT-028 previne retry storm mas não resolve o visual.

---

## Items Bloqueados (Requerem Backend Saudável)

| Story | O que falta validar |
|-------|---------------------|
| UX-348 | Viability badges em resultados reais, header "X oportunidades selecionadas de Y analisadas", links "Ver edital completo" |
| UX-349 | Botão Excel visível, 3 estados (gerando/pronto/retry), Google Sheets |
| UX-350 | "Recomendações Estratégicas" title, 30s timeout, AI transparency label, profile incomplete banner |
| UX-352 | Remoção de "Fonte Oficial" badge, remoção de "Palavra-chave" badge, "Alta relevância" label |

---

## Screenshots Capturados

| # | Arquivo | Descrição |
|---|---------|-----------|
| 1 | audit-01-landing-hero.jpeg | Landing page hero section |
| 2 | audit-02-dashboard.jpeg | Dashboard skeletons (initial) |
| 3 | audit-03-dashboard-after-wait.jpeg | Dashboard skeletons (15s) |
| 4 | audit-04-dashboard-15s.jpeg | Dashboard skeletons (persistent) |
| 5 | audit-05-buscar-form.jpeg | Search form clean state |
| 6 | audit-06-search-result.jpeg | Vestuário empty state |
| 7 | audit-07-engenharia-30s.jpeg | Engenharia search (state bleed) |
| 8 | audit-08-historico.jpeg | Histórico page (viewport) |
| 9 | audit-09-historico-full.jpeg | Histórico page (full — dedup visible) |
| 10 | audit-10-pipeline.jpeg | Pipeline empty state |
| 11 | audit-11-saude-progress.jpeg | Saúde search UF progress grid |
| 12 | audit-12-saude-processing.jpeg | Saúde 27/27 UFs + red dot |
| 13 | audit-13-saude-error.jpeg | Search error with retry countdown |
| 14 | audit-14-conta.jpeg | Account page |

---

## Recomendações

### Imediato (antes do próximo deploy)
1. Fix dedup no histórico (P1) — session dedup check não está filtrando cache hits
2. Fix state bleed CRIT-027 (P1) — adicionar `!loading` guard ao rendering block do empty state anterior
3. Fix unicode escape "Hist\u00f3rico" (P2) — provavelmente `JSON.stringify` ou encoding issue no header

### Próximo Sprint
4. Traduzir error messages restantes para PT-BR (P2)
5. Mapear sector slugs para nomes completos no histórico (P2)
6. Fix accent em "licitacoes" na mensagem de erro (P2)
7. Alinhar label /mensagens header com sidebar "Suporte" (P3)
8. Aplicar `useFetchWithBackoff` ao hook `usePlan` (CRIT-018 gap)
9. Dashboard: resolver skeletons para empty state quando API retorna 503 persistente

### Quando Backend Estável
10. Re-executar auditoria para UX-348, UX-349, UX-350, UX-352 com resultados reais
