# STORY-359: Transparência de degradação SSE para o usuário

**Prioridade:** P2
**Tipo:** fix (UX)
**Sprint:** Sprint 3
**Estimativa:** S
**Origem:** Conselho CTO Advisory Board — Auditoria de Promessas (2026-03-01)
**Dependências:** Nenhuma
**Bloqueado por:** —
**Bloqueia:** —
**Paralelo com:** STORY-353, STORY-358, STORY-360

---

## Contexto

Quando SSE falha, o frontend cai silenciosamente para progresso simulado baseado em tempo. O usuário vê barra de progresso avançando mas não sabe que é simulação. Se a busca falhar, a barra "mentiu". Transparência > perfeição.

## Promessa Afetada

> Confiança geral do usuário no sistema

## Causa Raiz

SSE fallback simulado é silencioso. `EnhancedLoadingProgress.tsx` usa time-based progress quando real SSE events não chegam. Sem indicação visual de que progresso é estimado.

## Critérios de Aceite

- [ ] AC1: Quando SSE cai para fallback simulado, exibir indicador discreto: ícone de info + tooltip "Progresso estimado (conexão em tempo real indisponível)"
- [ ] AC2: Se SSE reconectar com sucesso, remover indicador e mostrar progresso real
- [ ] AC3: Não bloquear UX — indicador é informativo, não alarme (cor cinza/azul, não vermelho)
- [ ] AC4: Prometheus counter `smartlic_sse_fallback_simulated_total` no frontend (via telemetry endpoint)
- [ ] AC5: Testes: SSE fail → indicador aparece → SSE reconnect → indicador some

## Arquivos Afetados

- `frontend/components/EnhancedLoadingProgress.tsx`
- `frontend/hooks/useSearchSSE.ts` (ou equivalente)
- `frontend/hooks/useSearchProgress.ts` (ou equivalente)

## Validação

| Métrica | Threshold | Onde medir |
|---------|-----------|------------|
| `smartlic_sse_fallback_simulated_total` | Trending down | Prometheus |
