# STORY-283: Phantom Sources & Stale Config Cleanup

**Priority:** P1
**Effort:** 0.5 day
**Squad:** @dev
**Fundamentacao:** Logs de producao 2026-02-26 (warnings constantes)

## Problemas Observados em Producao

### 1. Licitar Digital — Fonte Fantasma
```
WARNING: Licitar Digital enabled but LICITAR_API_KEY not set
Sources with pending credentials: ['Licitar']
```
- `source_config/sources.py`: config completo (URL, timeout, rate limit)
- `clients/licitar_client.py`: **arquivo vazio (0 bytes)**
- Nunca teve API key configurada
- **Status: JA CORRIGIDO** — default alterado para `enabled=False`

### 2. Unknown Plan IDs
```
Unknown plan_id 'free' in database, using conservative defaults
Unknown plan_id 'master' in database, using conservative defaults
Loaded 3 plan capabilities from database: ['free', 'master', 'smartlic_pro']
```
- `quota.py` so reconhece `smartlic_pro` e planos legacy (consultor_agil, maquina, sala_guerra)
- `free` e `master` existem na tabela `plan_capabilities` no Supabase
- Nao estao mapeados no `PLAN_CONFIGS` dict
- Warning polui logs a cada busca

### 3. Co-occurrence Triggers Orphans
```
Co-occurrence trigger 'padronizacao' in sector 'vestuario' does not match any keyword prefix — may never fire
Co-occurrence trigger 'rede' in sector 'informatica' does not match any keyword prefix — may never fire
```
- `sectors_data.yaml`: triggers definidos mas sem keyword correspondente
- Warning emitido no startup do worker (a cada restart)
- Funcional mas polui logs

## Acceptance Criteria

### AC1: Mapear plan_ids 'free' e 'master' no quota.py
- [ ] Adicionar `free` ao `PLAN_CONFIGS` com limites adequados:
  - `max_searches_per_month = 10` (ou o que o PO definir)
  - `max_history_days = 7`
  - `allow_excel = false`
  - `search_priority = "LOW"`
- [ ] Adicionar `master` com limites maximais:
  - `max_searches_per_month = unlimited`
  - `max_history_days = 99999`
  - `allow_excel = true`
  - `search_priority = "HIGH"`
- [ ] OU: remover da tabela `plan_capabilities` se nao sao mais usados
- [ ] **Decisao PO:** manter `free`/`master` ou substituir?

### AC2: Deletar arquivo vazio licitar_client.py
- [ ] `rm backend/clients/licitar_client.py`
- [ ] Verificar que nenhum import referencia o arquivo
- [ ] Manter config em sources.py (desabilitado) para futura integracao

### AC3: Corrigir co-occurrence triggers orphans
- [ ] `sectors_data.yaml` vestuario: verificar se "padronizacao" deve ter keyword correspondente
  - Se sim: adicionar "padronizacao" as keywords do setor
  - Se nao: remover o trigger ou corrigir para trigger que exista
- [ ] `sectors_data.yaml` informatica: verificar se "rede" deve ter keyword correspondente
  - "rede" e keyword valida para informatica (rede de computadores)
  - Provavelmente falta nas keywords — adicionar "rede" e "redes"
- [ ] Validar: zero warnings no startup apos fix

### AC4: Limpar logs de startup
- [ ] Apos fixes, Railway logs devem mostrar zero WARNINGs no startup
- [ ] Remover `Sources with pending credentials` do log quando lista vazia

## Files to Modify

| File | Change |
|------|--------|
| `backend/quota.py` | Map 'free' + 'master' plan_ids |
| `backend/clients/licitar_client.py` | **DELETE** |
| `backend/sectors_data.yaml` | Fix orphan co-occurrence triggers |
| `backend/source_config/sources.py` | ~~already fixed~~ |
