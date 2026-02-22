# GTM-COPY-008: Limpeza de Marca & Consistência SmartLic

**Épico:** GTM-COPY — Reposicionamento Estratégico de Comunicação
**Prioridade:** P1
**Tipo:** Cleanup
**Estimativa:** S (5-6 ACs)

## Objetivo

Garantir que **todo o frontend** seja 100% SmartLic — sem referências a BidIQ, sem viés setorial (vestuário/uniformes), e com branding consistente em todos os pontos de contato.

## Contexto

### Problemas Identificados

1. **localStorage key `bidiq-theme`** em `layout.tsx` (linha 131) — exposto ao usuário via DevTools
2. **Potenciais referências internas** a BidIQ em código (variáveis, comentários, console.logs)
3. **Risco de viés setorial** — garantir que nenhuma copy, exemplo, ou placeholder remeta a setor específico
4. **Inconsistência de branding** — verificar se "SmartLic" é usado consistentemente (não "Smartlic", "SMARTLIC", "Smart Lic")

## Acceptance Criteria

### AC1 — Remover Referências BidIQ (Frontend)
- [ ] Buscar e eliminar TODAS as ocorrências de "BidIQ", "bidiq", "bid-iq", "Bid IQ" no código frontend
- [ ] `bidiq-theme` → `smartlic-theme` em `layout.tsx`
- [ ] Verificar: localStorage keys, console.logs, comentários, data-attributes, CSS classes
- [ ] Migração transparente: se usuário já tem `bidiq-theme` no localStorage, migrar para `smartlic-theme`

### AC2 — Remover Referências BidIQ (Backend)
- [ ] Buscar ocorrências de "BidIQ", "bidiq" no backend que possam vazar para o frontend
- [ ] Redis keys que começam com `bidiq:` — avaliar se precisam migrar
- [ ] Nota: Redis keys internas (`bidiq:job_result:*`) são aceitáveis se nunca expostas ao user
- [ ] Endpoints que retornam "BidIQ" em response bodies — verificar e corrigir se necessário

### AC3 — Eliminar Viés Setorial no Frontend
- [ ] Buscar referências a "vestuário", "uniformes", "vestuario", "fardamento" em todo o frontend
- [ ] Nenhum setor específico deve aparecer em:
  - Exemplos na landing page
  - Placeholders de inputs
  - Textos de ajuda/tooltips
  - Marketing copy
- [ ] Exemplos devem ser **multi-setoriais** ou genéricos

### AC4 — Consistência de Branding
- [ ] Verificar todas as ocorrências do nome da marca:
  - Correto: "SmartLic" (capital S, capital L)
  - Incorreto: "Smartlic", "SMARTLIC", "Smart Lic", "smartlic" (em texto visível)
  - Exceção: `smartlic` minúsculo em URLs, variáveis, CSS classes é aceitável
- [ ] Verificar: títulos de página, headings, alt text, meta tags, CTAs, emails
- [ ] Arquivo principal: `layout.tsx`, todos os `page.tsx`

### AC5 — Email Templates
- [ ] Verificar templates de email em `backend/templates/emails/`:
  - Branding consistente (SmartLic, não BidIQ)
  - Sem referências setoriais
  - Logo e footer corretos
- [ ] Se houver templates com "BidIQ", atualizar

### AC6 — Zero Regressions
- [ ] localStorage migration (bidiq-theme → smartlic-theme) é transparente
- [ ] TypeScript compila
- [ ] Testes: zero novas falhas (frontend e backend)
- [ ] Funcionalidade de theme switching preservada

## Arquivos Impactados

| Arquivo | Mudança |
|---------|---------|
| `frontend/app/layout.tsx` | AC1 — bidiq-theme → smartlic-theme |
| Todos os `*.tsx`, `*.ts` do frontend | AC1, AC3, AC4 — busca e substituição |
| `backend/templates/emails/` | AC5 |
| Potencialmente `backend/job_queue.py` | AC2 — Redis keys (avaliar) |

## Notas de Implementação

- localStorage migration: no `layout.tsx`, ao carregar, verificar se `bidiq-theme` existe → copiar valor para `smartlic-theme` → deletar `bidiq-theme`
- A migração de localStorage é one-time e pode ser removida em release futura
- Backend Redis keys (`bidiq:*`) são internas e não afetam o usuário — documentar decisão de manter ou migrar
- Usar `git grep -i "bidiq"` para busca exaustiva

## Definition of Done

- [ ] ACs 1-6 verificados
- [ ] Zero ocorrências de "BidIQ" em texto visível ao usuário no frontend
- [ ] Zero viés setorial em copy/exemplos
- [ ] Commit: `fix(frontend): GTM-COPY-008 — limpeza de marca SmartLic`
