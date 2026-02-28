# SAB-002: Unicode escape sequences renderizadas como texto literal

**Origem:** UX Premium Audit P0-02
**Prioridade:** P0 — BLOQUEADOR
**Complexidade:** M (Medium)
**Sprint:** SAB-P0 (imediato)
**Owner:** @dev
**Screenshots:** `ux-audit/24-historico.png`, `ux-audit/25-pipeline.png`, `ux-audit/26-alertas.png`

---

## Problema

Textos em 3 páginas principais exibem Unicode escapes como texto literal em vez de caracteres acentuados:

| Página | Texto renderizado | Esperado |
|--------|------------------|----------|
| Histórico (header) | `Hist\u00f3rico` | Histórico |
| Pipeline (empty state) | `licita\u00e7\u00f5es`, `est\u00e1gios`, `c\u00e1`, `in\u00edcio` | licitações, estágios, cá, início |
| Alertas (subtítulo) | `notificacoes automaticas sobre novas licitacoes` | notificações automáticas sobre novas licitações |

**Causa provável:** Strings JSON com Unicode escapes (`\u00e7`) sendo renderizadas sem `JSON.parse()`, ou double-encoding (JSON.stringify de strings que já são UTF-8).

**REGRESSÃO:** Este bug foi identificado no audit de 2026-02-23 (BUG P2 item UX-353) e **não foi corrigido**. Agora aparece em mais páginas.

---

## Critérios de Aceite

### Diagnóstico

- [ ] **AC1:** Mapear TODAS as páginas que exibem texto com Unicode escapes (Histórico, Pipeline, Alertas + qualquer outra)
- [ ] **AC2:** Identificar a origem do texto: é hardcoded no frontend, vem do backend via API, ou vem do banco (Supabase)?
- [ ] **AC3:** Determinar se é double-encoding (JSON.stringify de string já escaped) ou falta de decoding (string JSON crua)

### Fix Global

- [ ] **AC4:** Corrigir na FONTE (não em cada componente). Se é backend: garantir que JSON responses usam UTF-8 puro. Se é frontend: garantir decode correto onde os textos são definidos.
- [ ] **AC5:** Histórico — header exibe "Histórico" com acento correto
- [ ] **AC6:** Pipeline empty state — todos os textos com acentos corretos: "licitações", "estágios", "início"
- [ ] **AC7:** Alertas subtítulo — "notificações automáticas sobre novas licitações"
- [ ] **AC8:** Buscar e corrigir qualquer OUTRO texto com padrão `\uXXXX` em todo o frontend (`grep -r '\\u00' frontend/`)

### Prevenção

- [ ] **AC9:** Adicionar lint rule ou test que detecta `\u00` em strings hardcoded do frontend (prevenção de regressão)

---

## Arquivos Prováveis

- `frontend/app/historico/page.tsx` — header "Histórico"
- `frontend/app/pipeline/page.tsx` — empty state texts
- `frontend/app/alertas/page.tsx` — subtítulo
- Qualquer arquivo com strings contendo `\u00`

## Notas

- Este é um bug de REGRESSÃO que persiste há 5+ dias. Prioridade máxima na correção.
- O fix deve ser global (na fonte), não patch por página.
