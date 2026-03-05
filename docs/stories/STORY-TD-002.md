# STORY-TD-002: RLS + Trigger Cleanup + Accessibility + Branding

**Epic:** Resolucao de Debito Tecnico
**Tier:** 0
**Area:** Database / Frontend / Backend
**Estimativa:** 7.5h (5.5h codigo + 2h testes)
**Prioridade:** P0
**Debt IDs:** C-02, H-01, FE-12, FE-13, FE-07, FE-24, TD-P03, TD-P04

## Objetivo

Story combinada de quick wins que nao requerem refatoracao profunda. Resolve: (1) tabelas sem RLS policies explicitas, (2) trigger functions duplicadas, (3) acessibilidade critica no sidebar, (4) branding residual "BidIQ", e (5) consolidacao de constantes.

## Acceptance Criteria

### Database: RLS Policies (C-02) — 1h
- [x] AC1: Adicionar RLS policies explicitas para `health_checks` (SELECT/INSERT/UPDATE/DELETE para service_role) → `20260304120000_rls_policies_trigger_consolidation.sql`
- [x] AC2: Adicionar RLS policies explicitas para `incidents` (SELECT/INSERT/UPDATE/DELETE para service_role)
- [ ] AC3: Verificar que nenhuma tabela no schema public tem RLS habilitado sem policies — pendente: requer `supabase db push`

### Database: Trigger Consolidation (H-01) — 2h
- [x] AC4: Identificar as 3 trigger functions `updated_at` duplicadas: `update_pipeline_updated_at()`, `update_alert_preferences_updated_at()`, `update_alerts_updated_at()`
- [x] AC5: Consolidar em uma unica function `set_updated_at()` reutilizada por todos os triggers
- [x] AC6: Migration DROP das functions duplicadas + CREATE OR REPLACE da consolidada
- [ ] AC7: Verificar que todos triggers `updated_at` funcionam apos consolidacao — pendente: requer `supabase db push`

### Frontend: Accessibility (FE-12 + FE-13) — 2h
- [x] AC8: Adicionar `aria-label` em todos os botoes icon-only do Sidebar (Sign Out + collapse toggle + collapsed nav items)
- [x] AC9: Adicionar `aria-hidden="true"` em todos SVGs decorativos do Sidebar (via lucide-react prop + span wrappers)
- [ ] AC10: Axe DevTools audit do Sidebar retorna zero violations de acessibilidade — pendente: requer browser audit
- [x] AC11: Testes unitarios verificam presenca de aria-labels nos botoes icon-only (6 new tests)

### Frontend: SVG Cleanup (FE-07) — 1.5h
- [x] AC12: Substituir SVGs inline no Sidebar (~75 linhas → 9 lucide-react imports) por icones do `lucide-react`
- [x] AC13: Manter visual identico (tamanho w-5 h-5, cor via currentColor, posicionamento)
- [x] AC14: Verificar que `lucide-react` ja esta no `package.json` — confirmado v0.563.0

### Frontend: APP_NAME Consolidation (FE-24) — 0.5h
- [x] AC15: Criar constante `APP_NAME` em `lib/config.ts` (arquivo existente com branding config)
- [x] AC16: Substituir todas 7 redeclaracoes de APP_NAME nos arquivos por import da constante
- [x] AC17: Grep confirma zero declaracoes locais de `APP_NAME` fora de `lib/config.ts`

### Backend: Branding Cleanup (TD-P03 + TD-P04) — 0.5h
- [x] AC18: User-Agent headers ja usam "SmartLic" em todos HTTP clients (pre-existing)
- [x] AC19: `pyproject.toml` ja usa `name = "smartlic-backend"` (pre-existing)
- [x] AC20: Grep confirma zero ocorrencias de "BidIQ" em arquivos Python do backend

## Technical Notes

**RLS policy pattern para service_role-only tables:**
```sql
ALTER TABLE health_checks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all" ON health_checks
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
```

**Trigger consolidation pattern:**
```sql
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Then for each table:
DROP TRIGGER IF EXISTS set_updated_at ON table_name;
CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON table_name
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
```

**lucide-react icons:** Verificar mapeamento 1:1 com SVGs atuais. Icones comuns: `Menu`, `X`, `ChevronLeft`, `ChevronRight`, `Home`, `Search`, `Settings`, `User`, `BarChart3`, `Kanban`, `History`, `MessageSquare`, `HelpCircle`.

## Dependencies

- Nenhuma — independente de TD-001
- Pode ser executada em paralelo com TD-001

## Definition of Done
- [x] Migration(s) criada(s) em `supabase/migrations/`
- [ ] Migration(s) aplicada(s) no Supabase Cloud — pendente: requer `supabase db push`
- [ ] Zero tabelas com RLS habilitado sem policies — pendente: requer Cloud verify
- [x] Uma unica function `set_updated_at()` no schema (migration created)
- [ ] Axe audit do Sidebar passa sem violations — pendente: requer browser audit
- [x] Zero "BidIQ" em User-Agent strings
- [x] All backend tests passing (pre-existing 1 fail unrelated)
- [x] All frontend tests passing (pre-existing 23 fails unrelated — HistoricoUX354/357)
- [x] No regressions (zero new failures introduced)
- [ ] Reviewed by @data-engineer (DB parts) and @ux-design-expert (FE parts)
