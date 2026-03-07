# HARDEN-025: EmptyResults Component com Sugestões

**Severidade:** BAIXA
**Esforço:** 20 min
**Quick Win:** Nao
**Origem:** Conselho CTO — Auditoria de Fragilidades (2026-03-06)

## Contexto

Quando search retorna 0 resultados, não há orientação ao usuário. Filter summary mostra "0 relevantes de N analisadas" sem sugestões de como melhorar a busca.

## Critérios de Aceitação

- [ ] AC1: Componente `EmptyResults` com ícone e mensagem amigável
- [ ] AC2: Sugestões contextuais: "ampliar período", "remover filtros de UF", "usar termos genéricos"
- [ ] AC3: Exibido quando `total_filtrado === 0`
- [ ] AC4: Teste de renderização

## Arquivos Afetados

- `frontend/app/buscar/components/EmptyResults.tsx` — novo componente
- `frontend/app/buscar/page.tsx` — integração
