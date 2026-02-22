# CRIT-FLT-010 — Red Flags Setoriais Expandidas (15 Setores)

**Prioridade:** P1 — Falso Positivo Prevention
**Estimativa:** 4h
**Origem:** Auditoria de Pipeline 2026-02-22
**Track:** Backend

## Problema

O sistema de red flags (STORY-181 AC6) tem apenas 3 conjuntos genéricos:
- `RED_FLAGS_MEDICAL` (12 termos)
- `RED_FLAGS_ADMINISTRATIVE` (12 termos)
- `RED_FLAGS_INFRASTRUCTURE` (8 termos)

Esses red flags genéricos detectam contextos médicos/admin/infra, mas **não cobrem contextos cross-setor específicos**. Cada setor tem seus próprios "impostores" — termos que parecem do setor mas na verdade pertencem a outro domínio.

### Exemplos de Lacunas

| Setor | Keyword Matchada | Red Flag Ausente | Resultado |
|-------|-----------------|-----------------|-----------|
| software | "sistema" | "sistema de registro de preços", "sistema de ar condicionado" | FP |
| vigilancia | "vigilância" | "vigilância sanitária", "vigilância epidemiológica" | FP |
| transporte | "transporte" | "transporte de dados", "transporte de resíduos" | FP |
| informatica | "equipamento" | "equipamento médico", "equipamento de proteção" | FP |
| mobiliario | "cadeira" | "cadeira de rodas", "cadeira odontológica" | FP |
| papelaria | "material" | "material cirúrgico", "material de construção" | FP |
| facilities | "manutenção" | "manutenção de veículos", "manutenção de software" | FP |
| alimentos | "alimentação" | "alimentação de dados", "alimentação ininterrupta (UPS)" | FP |
| materiais_eletricos | "cabo" | "cabo de rede (ethernet)", "cabo de aço (construção)" | FP |

## Acceptance Criteria

- [x] **AC1:** Criar `RED_FLAGS_PER_SECTOR` dict no `filter.py` com red flags específicas por setor
- [x] **AC2:** Red flags setoriais para cada um dos 15 setores:

### Red Flags por Setor

**vestuario:** (já coberto por exclusions, red flags genéricos OK)
- Manter exemptions: medical, infrastructure

**alimentos:**
- `["alimentação de dados", "alimentação ininterrupta", "fonte de alimentação", "alimentação elétrica", "alimentar processo", "alimentar sistema"]`

**informatica:**
- `["equipamento médico", "equipamento hospitalar", "equipamento odontológico", "equipamento laboratorial", "equipamento de proteção", "equipamento esportivo"]`

**software:**
- `["sistema de registro de preços", "sistema de ar condicionado", "sistema de combate a incêndio", "sistema de irrigação", "sistema viário", "sistema de drenagem", "sistema de esgoto"]`

**engenharia:**
- `["engenharia de software", "engenharia genética", "engenharia financeira", "engenharia reversa"]`

**facilities:**
- `["manutenção de veículos", "manutenção de software", "manutenção de equipamentos médicos", "manutenção rodoviária"]`

**saude:**
- Não precisa (setor específico por natureza)

**vigilancia:**
- `["vigilância sanitária", "vigilância epidemiológica", "vigilância ambiental", "vigilância em saúde"]`

**transporte:**
- `["transporte de dados", "transporte de resíduos", "transporte de materiais perigosos", "transporte de energia"]`

**mobiliario:**
- `["cadeira de rodas", "cadeira odontológica", "cadeira cirúrgica", "mesa cirúrgica", "mesa de bilhar"]`

**papelaria:**
- `["material cirúrgico", "material de construção", "material elétrico", "material hidráulico", "material hospitalar", "material bélico"]`

**manutencao_predial:**
- `["manutenção de software", "manutenção de veículos", "manutenção de equipamentos de TI"]`

**engenharia_rodoviaria:**
- (Keywords específicas o suficiente, red flags genéricos OK)

**materiais_eletricos:**
- `["cabo de rede ethernet", "cabo de aço", "material eletrônico", "equipamento eletrônico"]`

**materiais_hidraulicos:**
- `["hidratante", "hidromassagem", "hidroterapia"]`

- [x] **AC3:** Integrar `RED_FLAGS_PER_SECTOR` na Camada 2A (antes de enviar ao LLM):
  - Se keyword matched + sector-specific red flag matched → REJECT (sem LLM)
  - Threshold: 1 red flag setorial (mais específicos que genéricos, não precisa 2+)
- [x] **AC4:** Testes unitários para cada setor: 1 caso com red flag → REJECT, 1 caso sem → PASS
- [x] **AC5:** Adicionar stat `rejeitadas_red_flags_setorial` ao filter stats
- [x] **AC6:** Feature flag `SECTOR_RED_FLAGS_ENABLED` (default: true) para rollback

## Impacto

- **Cobertura:** 15 setores com red flags específicas
- **Precision gain:** ~5-10% melhoria em precision para setores com keywords genéricas
- **Custo LLM:** Economiza chamadas (rejeita antes de enviar ao LLM)
- **Risco de regressão:** MÉDIO (red flags setoriais podem ser agressivos demais → monitorar recall)

## Arquivos

- `backend/filter.py` (RED_FLAGS_PER_SECTOR + integração na Camada 2A)
- `backend/sectors_data.yaml` (alternativa: definir red flags no YAML por setor)
- `backend/tests/test_filter.py` (15 * 2 = 30 novos testes)
