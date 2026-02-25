# GTM-FIX-041 — Resumo IA Mostra Nome do Setor em Busca por Termos

**Status:** Open
**Priority:** P2 — Medium (informação incorreta no resumo, não bloqueia uso)
**Severity:** Backend + Frontend — LLM summary e fallback usam setor_id quando busca é por termos
**Created:** 2026-02-25
**Sprint:** GTM Stabilization
**Relates to:** GTM-RESILIENCE-F01 (ARQ job queue), STORY-267 (term search parity)
**Found:** Playwright E2E validation 2026-02-25

---

## Problema

Quando o usuário faz uma busca por **termos específicos** (ex: "calibração de equipamentos metrológicos"), o resumo IA e o fallback summary exibem o nome do **setor** em vez dos termos:

### O que aparece:

```
"Encontradas 10 licitações de Vestuário e Uniformes totalizando R$ 0.00."
"Setor de Vestuário e Uniformes: 10 oportunidades distribuídas em 2 estado(s)"
```

### O que deveria aparecer:

```
"Encontradas 10 licitações para 'calibração de equipamentos metrológicos' totalizando R$ 0.00."
"Busca por termos: 10 oportunidades distribuídas em 2 estado(s)"
```

### Causa raiz:

`gerar_resumo_fallback()` em `search_pipeline.py` usa `setor_nome` incondicionalmente. Quando a busca é por termos, o `setor_id` default ("vestuario") é usado no fallback, mesmo não sendo relevante.

O prompt do LLM summary (`llm.py`) provavelmente também recebe o setor_nome em vez dos termos de busca.

---

## Acceptance Criteria

### AC1: Fallback summary usa termos quando search mode = terms
- [ ] `gerar_resumo_fallback()` — detectar se `termos_busca` está preenchido
- [ ] Se termos: usar `"para '{termos}'"` em vez de `"de {setor_nome}"`
- [ ] Se setor: manter behavior atual
- [ ] Contexto do setor: substituir por "Busca por termos: ..." quando aplicável

### AC2: LLM prompt inclui termos de busca
- [ ] `llm.py` — quando `termos_busca` presente, incluir no system prompt
- [ ] O resumo gerado por IA deve referenciar os termos, não o setor
- [ ] Se ambos presentes (termos + setor), priorizar termos no resumo

### AC3: Frontend exibe corretamente
- [ ] Verificar que o componente de resumo renderiza o texto do backend sem alterar
- [ ] Se `search_mode == "terms"`, header do resumo deve usar os termos

### AC4: Testes
- [ ] Backend: test fallback summary com termos_busca → output não menciona setor
- [ ] Backend: test fallback summary com setor → output menciona setor (regressão)

---

## Arquivos Envolvidos

| Arquivo | Ação |
|---------|------|
| `backend/search_pipeline.py` | AC1: gerar_resumo_fallback() condicional |
| `backend/llm.py` | AC2: prompt com termos_busca |
| `backend/schemas.py` | Verificar se search_mode está disponível no contexto |

---

## Estimativa
- **Esforço:** 1-2h
- **Risco:** Baixo (string formatting, não altera pipeline)
- **Squad:** @dev (backend) + @qa (testes)
