# Auditoria UX Premium — SmartLic Production

**Data:** 2026-02-28 19:30–20:15 UTC
**Auditor:** @ux-design-expert (Uma)
**Ambiente:** Produção (smartlic.tech), logado como tiago.sasaki@gmail.com (admin, SmartLic Pro)
**Dispositivos:** Desktop 1280x720 + Mobile 375x812
**Tema testado:** Light + Dark
**Screenshots:** `ux-audit/` (31 capturas, 01–31)
**Audit anterior:** `2026-02-23-ux-production-audit.md` (7 bugs identificados, vários persistem)

---

## Resumo Executivo

| Severidade | Qtd | Status |
|------------|-----|--------|
| P0 — Bloqueador | 3 | Impedem uso real do produto |
| P1 — Alto | 6 | Degradam percepção premium |
| P2 — Médio | 8 | Polimento abaixo do padrão |
| P3 — Baixo | 5 | Nice-to-have para premium |
| **Total** | **22** | |

**Veredito geral:** O SmartLic **não está em padrão premium**. Existem 3 bloqueadores que impedem o uso básico do produto, bugs de encoding que persistem há 5+ dias desde o último audit, e o dark mode está ilegível em múltiplas páginas. Um usuário pagando R$397/mês abandonaria na primeira sessão.

---

## P0 — BLOQUEADORES (3)

### P0-01: Busca trava em 70% — resultados nunca aparecem
- **Página:** `/buscar`
- **Screenshots:** `17-busca-loading.png` → `20-busca-stuck-130s.png` → `21-busca-stuck-backend-done.png`
- **Reprodução:** Buscar "Vestuário e Uniformes" em SP, últimos 10 dias
- **Comportamento:** Backend completa em ~14s (confirmado nos logs: `llm_summary_job`, `excel_generation_job`, `bid_analysis_job` todos concluídos). Frontend fica preso em "Filtrando resultados" 70% com skeletons de loading por 145+ segundos. Resultados **nunca** renderizam.
- **Barra inferior:** Mostra "8 relevantes de 594 analisadas — Filtragem concluída" mas os cards de resultado não aparecem
- **Causa provável:** Desconexão SSE ou race condition entre a resposta principal do POST `/buscar` e os eventos SSE de background jobs (`llm_ready`, `excel_ready`)
- **Impacto:** Funcionalidade CORE do produto está quebrada. Usuário não consegue ver resultados.
- **Evidência dos logs:**
  ```
  search_id=0b3a3f0e... completed
  llm_summary_job completed
  excel_generation_job completed
  bid_analysis_job completed
  SWR revalidation completed in 61943ms
  ```

### P0-02: Unicode escape sequences como texto literal
- **Páginas afetadas:** Histórico, Pipeline, Alertas
- **Screenshots:** `24-historico.png`, `25-pipeline.png`, `26-alertas.png`
- **Exemplos visíveis:**
  - Header Histórico: `Hist\u00f3rico` (deveria ser "Histórico")
  - Pipeline empty state: `licita\u00e7\u00f5es`, `est\u00e1gios`, `c\u00e1`, `in\u00edcio`
  - Alertas subtítulo: `notificacoes automaticas sobre novas licitacoes` (sem acentos)
- **Causa provável:** JSON strings com Unicode escapes não são decodificadas na renderização Next.js (possivelmente `JSON.parse` missing ou template literals com dados crus do backend)
- **Impacto:** Textos ilegíveis em 3 das 7 páginas principais. Transmite amadorismo.
- **REGRESSÃO:** Este bug foi identificado no audit de 2026-02-23 (BUG P2 no item UX-353) e **não foi corrigido**.

### P0-03: Dark mode ilegível
- **Páginas afetadas:** Área logada inteira (confirmado pelo usuário: "smartlic ilegível no dark")
- **Screenshots:** `30-dark-mode.png`, `31-mobile-busca.png` (mobile dark)
- **Problemas específicos:**
  - Sidebar: texto legível mas sem separação visual suficiente entre itens
  - Logo "SmartLic.tech" cortada/parcialmente visível no canto superior esquerdo
  - Footer no dark mode: links e texto com contraste insuficiente
  - Página de busca: relativamente OK, mas campos de formulário e dropdown têm bordas quase invisíveis
  - Pipeline/Histórico/Alertas: texto com Unicode + dark mode = completamente ilegível
- **Impacto:** Usuários que preferem dark mode (40-60% em SaaS B2B) não conseguem usar o produto.

---

## P1 — ALTO IMPACTO (6)

### P1-01: Alertas sem sidebar de navegação
- **Página:** `/alertas` (via menu lateral)
- **Screenshot:** `26-alertas.png`
- **Problema:** A página de Alertas renderiza em layout full-width SEM a sidebar padrão. Todas as outras páginas (Buscar, Dashboard, Pipeline, Histórico, Conta) têm sidebar consistente.
- **Impacto:** Quebra de consistência de navegação. Usuário "perde" o menu e precisa usar o browser back.

### P1-02: Busca — skeleton loading permanente
- **Página:** `/buscar` (após busca)
- **Screenshots:** `18-busca-results-loading.png` → `21-busca-stuck-backend-done.png`
- **Problema:** Skeleton cards de resultado aparecem durante o loading mas nunca são substituídos por resultados reais (vinculado ao P0-01). Não há timeout/fallback — fica em skeleton infinitamente.
- **Esperado:** Após 30s sem dados, mostrar mensagem "Resultados demorando mais que o esperado" com botão de retry.

### P1-03: Landing page excessivamente longa e repetitiva
- **Página:** `/` (homepage)
- **Screenshots:** `01-landing-hero.png` → `09-landing-footer.png` (9 screenshots para cobrir)
- **Problemas:**
  - Seção "Como Funciona" aparece **duas vezes** (`03-landing-como-funciona.png` e `08-landing-como-funciona2.png`)
  - Múltiplas menções a "87% filtrados" e "27 UFs" espalhadas em seções diferentes
  - Seção de dor ("Sua empresa perde R$..") muito longa com whitespace excessivo
  - Stats counter ("0%" visível antes de animar — flash of uninitialized content)
  - Scroll total ~8x viewport height — acima do benchmark premium (3-5x max)
- **Impacto:** Taxa de bounce alta. Usuário não encontra o CTA de signup sem scroll excessivo.

### P1-04: Signup — botão "Criar conta" sem feedback de validação
- **Página:** `/signup`
- **Screenshot:** `11-signup-page.png`
- **Problema:** Botão "Criar conta" aparece visualmente como desabilitado/greyed out sem nenhuma indicação do que falta preencher. Campos de validação não mostram erros inline.
- **Esperado:** Validação inline em cada campo (email format, senha força, nome required) com mensagens claras. Botão deve mostrar "Preencha todos os campos" como tooltip no hover quando disabled.

### P1-05: Inconsistência do período de trial
- **Página:** `/signup`
- **Screenshot:** `11-signup-page.png`
- **Problema:** Tela de signup diz "14 dias do produto completo" mas a configuração do sistema (CLAUDE.md, STORY-264/277) define trial como **30 dias**.
- **Impacto:** Se o trial é 30 dias, o marketing está sub-vendendo. Se é 14, a documentação está errada.

### P1-06: Dashboard — erro 500 e badge "0%" sem contexto
- **Página:** `/dashboard`
- **Screenshots:** `22-dashboard.png`, `23-dashboard-bottom.png`
- **Problemas:**
  - Console error: `GET /api/organizations/me` retorna HTTP 500
  - Badge "0%" no canto superior direito sem tooltip ou explicação do que significa
  - KPI "Horas Economizadas: 64h" — cálculo não explicado, parece arbitrário
- **Impacto:** Erros de console degradam confiança. Badge confuso poluí a interface.

---

## P2 — MÉDIO (8)

### P2-01: Conta — "Perfil de Licitante" 0% sem guidance
- **Página:** `/conta`
- **Screenshot:** `27-conta-full.png`
- **Problema:** Seção "Perfil de Licitante" mostra "0/7 campos preenchidos — Seu perfil está 0% completo" com 7 campos "Não informado". Não há tooltip explicando por que preencher (benefício), nem um wizard guiado.
- **Esperado:** Tooltip ou banner explicando "Perfil completo melhora a precisão da análise de viabilidade em até 40%" + botão "Preencher agora" que abre wizard step-by-step.

### P2-02: Conta — acentos faltando em labels
- **Página:** `/conta`
- **Screenshot:** `27-conta-full.png`
- **Problema:** Vários labels sem acentos:
  - "Estados de atuacao" → "Estados de atuação"
  - "Experiencia" → "Experiência"
  - "Funcionarios" → "Funcionários"
  - "licitacao" → "licitação" (seção Alertas)
  - "Frequencia" → "Frequência"
- **Impacto:** Inconsistência textual percebida como descuido.

### P2-03: Planos — badge "BETA" no produto pago
- **Página:** `/planos`
- **Screenshot:** `28-planos.png`
- **Problema:** Card de pricing mostra "SmartLic Pro **BETA**" com badge azul. Cobrar R$397/mês por um produto em "BETA" gera desconfiança.
- **Esperado:** Remover badge BETA ou reposicionar como "Early Adopter" com benefício (preço lock-in, features priority).

### P2-04: Planos — heading questionável
- **Página:** `/planos`
- **Screenshot:** `28-planos.png`
- **Problema:** Título "Escolha Seu Nível de Compromisso" é estranho para pricing. "Compromisso" tem conotação negativa em português ("obrigação").
- **Sugestão:** "Escolha o melhor para sua empresa" ou "Invista na inteligência competitiva"

### P2-05: Histórico — tempo de busca exposto demais
- **Página:** `/historico`
- **Screenshot:** `24-historico.png`
- **Problema:** Cada card mostra o tempo da busca (39.8s, 93.8s, 26.6s, 31.7s). Tempos de 90+ segundos transmitem lentidão.
- **Sugestão:** Esconder tempo ou mostrar apenas quando < 30s. Substituir por "Análise profunda" quando > 60s.

### P2-06: Valores monetários — formatação inconsistente
- **Páginas:** Histórico, Dashboard
- **Screenshots:** `24-historico.png`, `22-dashboard.png`
- **Problema:** Valores como "R$ 3.850.119,79" e "R$ 130.720.257,99" usam formatação correta, mas "R$ 3495.1M" no Dashboard usa formato abreviado americano (ponto para milhares, M para milhão).
- **Esperado:** Formato PT-BR consistente: "R$ 3,5 bi" ou "R$ 3.495,1 mi"

### P2-07: Mobile — bottom nav com labels truncados
- **Página:** Mobile 375px (todas as páginas)
- **Screenshot:** `31-mobile-busca.png`
- **Problema:** Bottom navigation bar mostra "Buscar | Pipeline | Histórico | Msg | Mais" — "Histórico" fica apertado, "Msg" é abreviação não óbvia.
- **Sugestão:** Usar apenas ícones sem labels no mobile (com tooltips no long-press), ou abreviar consistentemente: "Busca | Pipeline | Hist. | Msgs | Mais"

### P2-08: Login — 3 métodos sem hierarquia visual
- **Página:** `/login`
- **Screenshot:** `10-login-page.png`
- **Problema:** Login oferece Google OAuth + Email/Senha + Magic Link no mesmo nível visual. Padrão premium: destaque no método preferido (Google) e secundarize os demais.
- **Sugestão:** Google OAuth como botão primary (full-width, acima), depois divider "ou", depois email/senha compacto.

---

## P3 — BAIXO / NICE-TO-HAVE (5)

### P3-01: Landing — stats counter flash "0%"
- **Página:** `/` (hero section)
- **Screenshot:** `01-landing-hero.png`
- **Problema:** Contadores de stats ("87% filtrados", "27 UFs", etc.) mostram "0%" brevemente antes da animação de contagem iniciar. Flash of uninitialized content (FOUC).
- **Fix:** Iniciar contadores com `opacity: 0` e fazer fade-in junto com a animação de contagem.

### P3-02: Sidebar — sem indicador de hover/active states claros
- **Página:** Todas as páginas logadas
- **Problema:** Items da sidebar têm highlight no item ativo (azul) mas o hover state é sutil demais. Sem transição suave.
- **Sugestão:** Adicionar `transition: background-color 150ms` + hover state mais visível (bg-gray-100).

### P3-03: Busca — "Personalizar busca" collapsed por default
- **Página:** `/buscar`
- **Screenshot:** `15-busca-clean.png`
- **Problema:** Filtros avançados ("Personalizar busca") estão escondidos em accordion. Usuários recorrentes precisam expandir toda vez.
- **Sugestão:** Salvar estado do accordion no localStorage. Se já expandiu antes, manter aberto.

### P3-04: Conta — seções sem separação visual forte
- **Página:** `/conta`
- **Screenshot:** `27-conta-full.png`
- **Problema:** 7 seções (Perfil, Segurança, Senha, Acesso, Perfil Licitante, Alertas, LGPD) empilhadas em scroll vertical longo. Sem tabs ou navegação interna.
- **Sugestão:** Tab navigation horizontal no topo ou sticky sidebar com links âncora para cada seção.

### P3-05: Footer logado — redundante com sidebar
- **Página:** Todas as páginas logadas
- **Screenshot:** `30-dark-mode.png` (footer visível na busca)
- **Problema:** Footer com links "Sobre", "Planos", "Central de Ajuda", etc. é redundante com a sidebar de navegação na área logada.
- **Sugestão:** Footer simplificado na área logada (apenas copyright + links legais).

---

## Comparação com Audit Anterior (2026-02-23)

| Bug | Status 02/23 | Status 02/28 | Evolução |
|-----|-------------|-------------|----------|
| Unicode `Hist\u00f3rico` header | P2 identificado | P0-02 persistente | **PIOROU** (agora em mais páginas) |
| Sidebar "Mensagens" → "Suporte" | Corrigido | OK | Mantido |
| Pipeline empty state acentos | PASS em 02/23 | P0-02 FAIL agora | **REGREDIU** |
| Alertas sem sidebar | Não testado | P1-01 novo | Novo achado |
| Busca travando | Não testado (503) | P0-01 novo | Backend estava down antes |
| Dark mode | Não testado | P0-03 novo | Novo achado |

---

## Benchmark Premium — Gaps Principais

| Critério Premium | SmartLic Atual | Gap |
|-----------------|----------------|-----|
| **Zero-error experience** | 3 bloqueadores, textos ilegíveis | Crítico |
| **Sub-3s perceived performance** | 14s-94s buscas + loading infinito | Crítico |
| **Consistent visual language** | Dark mode quebrado, layout Alertas diferente | Alto |
| **Microcopy profissional** | Unicode escapes, acentos faltando | Alto |
| **Progressive disclosure** | Filtros escondidos, 0% perfil sem guidance | Médio |
| **Responsive excellence** | Mobile funcional mas não polido | Médio |
| **Delightful animations** | Stats FOUC, sem hover transitions | Baixo |
| **Trust signals** | Badge "BETA" no produto pago | Médio |

---

## Recomendação de Priorização

### Sprint Imediato (P0 — esta semana)
1. **P0-01:** Diagnosticar SSE disconnect na busca. Verificar se `useSearch` consome o evento final corretamente.
2. **P0-02:** Fix global de Unicode encoding — provavelmente `JSON.parse()` em strings já decodificadas ou vice-versa.
3. **P0-03:** Audit completo de dark mode — mapear todas as variáveis CSS, testar contraste WCAG AA (4.5:1 para texto, 3:1 para UI).

### Sprint Seguinte (P1 — próxima semana)
4. **P1-01:** Adicionar sidebar na página Alertas (copiar layout das outras páginas)
5. **P1-02:** Timeout + retry na busca (30s sem dados → mensagem + botão)
6. **P1-03:** Condensar landing page (remover seção duplicada, reduzir para 4x viewport max)
7. **P1-04:** Validação inline no signup
8. **P1-05:** Corrigir período trial (14 → 30 dias ou vice-versa)
9. **P1-06:** Investigar `/api/organizations/me` 500, remover badge "0%" ou dar contexto

### Backlog (P2+P3 — quando possível)
- P2-01 a P2-08: Polimento geral
- P3-01 a P3-05: Detalhes premium

---

## Screenshots Reference

| # | Arquivo | Página | Achados |
|---|---------|--------|---------|
| 01-09 | `01-landing-hero.png` → `09-landing-footer.png` | Landing | P1-03, P3-01 |
| 10 | `10-login-page.png` | Login | P2-08 |
| 11 | `11-signup-page.png` | Signup | P1-04, P1-05 |
| 14-16 | `14-busca-onboarding.png` → `16-busca-filtros.png` | Busca (clean) | P3-03 |
| 17-21 | `17-busca-loading.png` → `21-busca-stuck-backend-done.png` | Busca (loading) | **P0-01**, P1-02 |
| 22-23 | `22-dashboard.png`, `23-dashboard-bottom.png` | Dashboard | P1-06, P2-06 |
| 24 | `24-historico.png` | Histórico | **P0-02**, P2-05 |
| 25 | `25-pipeline.png` | Pipeline | **P0-02** |
| 26 | `26-alertas.png` | Alertas | **P0-02**, P1-01 |
| 27 | `27-conta-full.png` | Conta | P2-01, P2-02, P3-04 |
| 28-29 | `28-planos.png`, `29-planos-bottom.png` | Planos | P2-03, P2-04 |
| 30 | `30-dark-mode.png` | Dark mode | **P0-03** |
| 31 | `31-mobile-busca.png` | Mobile | P2-07, **P0-03** |
