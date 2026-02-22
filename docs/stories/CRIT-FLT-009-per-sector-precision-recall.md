# CRIT-FLT-009 — Precision/Recall Benchmark por Setor (15/15)

**Prioridade:** P0 — Validação End-to-End
**Estimativa:** 10h (inclui execução manual + LLM calls)
**Origem:** Auditoria de Pipeline 2026-02-22 + Pedido de Cobertura 15 Setores
**Track:** Backend + QA
**Depende de:** CRIT-FLT-005 (script de auditoria), CRIT-FLT-007 (cobertura setorial)

## Objetivo

Executar a busca REAL para cada um dos 15 setores, classificar manualmente uma amostra, e produzir métricas quantitativas de precision e recall. O objetivo é provar ou refutar a promessa de "0 falsos positivos e 0 falsos negativos".

## Metodologia

Para cada setor:
1. Buscar 200+ itens brutos do PNCP (SP, MG, RJ, BA, PR — 10 dias)
2. Aplicar pipeline completo (keywords → exclusions → context → co-occurrence → proximity → density → LLM arbiter → zero-match)
3. Amostra de 30 itens (15 aprovados + 15 rejeitados) para classificação manual
4. Classificação manual: CORRETO ou INCORRETO com justificativa
5. Calcular: Precision = TP/(TP+FP), Recall = TP/(TP+FN)

## Acceptance Criteria por Setor

### Métricas Target

| Métrica | Target Mínimo | Ideal |
|---------|--------------|-------|
| Precision | >= 85% | >= 95% |
| Recall | >= 70% | >= 85% |
| Cross-sector FP rate | < 10% | < 5% |
| LLM calls per search | < 30 | < 15 |

### 1. Vestuário e Uniformes (`vestuario`)
- [ ] **AC-VES-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-VES-2:** "confecção de placa/grade/prótese" → REJEITADO (exclusion)
- [ ] **AC-VES-3:** "EPI de proteção individual" → APROVADO (após CRIT-FLT-001)
- [ ] **AC-VES-4:** "uniformização de procedimentos" → REJEITADO (exclusion)
- [ ] **AC-VES-5:** Documentar top 3 FPs e top 3 FNs reais

### 2. Alimentos e Merenda (`alimentos`)
- [ ] **AC-ALI-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-ALI-2:** "merenda escolar" → APROVADO
- [ ] **AC-ALI-3:** "alimentação de dados" → REJEITADO (exclusion necessária?)
- [ ] **AC-ALI-4:** "gêneros alimentícios" → APROVADO
- [ ] **AC-ALI-5:** Validar que "alimentos para animais" / "ração" tem exclusion

### 3. Hardware e Equipamentos de TI (`informatica`)
- [ ] **AC-INF-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-INF-2:** "servidor público" (pessoa) → REJEITADO (context gate)
- [ ] **AC-INF-3:** "monitor de vídeo" → APROVADO
- [ ] **AC-INF-4:** "switch de rede" → APROVADO (context gate)
- [ ] **AC-INF-5:** "servidor para data center" → APROVADO (context gate)

### 4. Mobiliário (`mobiliario`)
- [ ] **AC-MOB-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-MOB-2:** "cadeira de rodas" → REJEITADO (exclusion: contexto médico)
- [ ] **AC-MOB-3:** "mesa cirúrgica" → REJEITADO (exclusion: contexto médico)
- [ ] **AC-MOB-4:** "armário de escritório" → APROVADO
- [ ] **AC-MOB-5:** Validar exclusions para mobiliário hospitalar/médico

### 5. Papelaria e Material de Escritório (`papelaria`)
- [ ] **AC-PAP-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-PAP-2:** "material de escritório" → APROVADO
- [ ] **AC-PAP-3:** "material de construção" → REJEITADO (context gate ou exclusion)
- [ ] **AC-PAP-4:** "material hospitalar" → REJEITADO (red flag)
- [ ] **AC-PAP-5:** "toner e cartucho" → APROVADO

### 6. Engenharia, Projetos e Obras (`engenharia`)
- [ ] **AC-ENG-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-ENG-2:** "obra de engenharia" → APROVADO
- [ ] **AC-ENG-3:** "engenharia de software" → REJEITADO (exclusion: não é obra)
- [ ] **AC-ENG-4:** "projeto executivo de edificação" → APROVADO
- [ ] **AC-ENG-5:** Validar que não colide com engenharia_rodoviaria

### 7. Software e Sistemas (`software`)
- [ ] **AC-SOF-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-SOF-2:** "sistema de registro de preços" → REJEITADO (após CRIT-FLT-004)
- [ ] **AC-SOF-3:** "software de gestão" → APROVADO
- [ ] **AC-SOF-4:** "licença de software" → APROVADO
- [ ] **AC-SOF-5:** "sistema de ar condicionado" → REJEITADO

### 8. Facilities e Manutenção (`facilities`)
- [ ] **AC-FAC-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-FAC-2:** "serviço de limpeza" → APROVADO
- [ ] **AC-FAC-3:** "manutenção de veículos" → REJEITADO (é transporte)
- [ ] **AC-FAC-4:** "conservação predial" → APROVADO ou vai para manutencao_predial?
- [ ] **AC-FAC-5:** Documentar colisão facilities vs manutencao_predial

### 9. Saúde (`saude`)
- [ ] **AC-SAU-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-SAU-2:** "medicamento" → APROVADO
- [ ] **AC-SAU-3:** "equipamento médico" → APROVADO
- [ ] **AC-SAU-4:** "material de limpeza hospitalar" → REJEITADO (é facilities)
- [ ] **AC-SAU-5:** Validar que não colide com vestuario (uniformes hospitalares)

### 10. Vigilância e Segurança Patrimonial (`vigilancia`)
- [ ] **AC-VIG-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-VIG-2:** "vigilância armada" → APROVADO
- [ ] **AC-VIG-3:** "vigilância sanitária" → REJEITADO (exclusion necessária!)
- [ ] **AC-VIG-4:** "CFTV e monitoramento" → APROVADO
- [ ] **AC-VIG-5:** "segurança da informação" → REJEITADO (é software/informatica)

### 11. Transporte e Veículos (`transporte`)
- [ ] **AC-TRA-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-TRA-2:** "locação de veículos" → APROVADO
- [ ] **AC-TRA-3:** "transporte de dados" → REJEITADO (exclusion necessária?)
- [ ] **AC-TRA-4:** "combustível" → APROVADO
- [ ] **AC-TRA-5:** "ambulância" → ambíguo (transporte OU saude?)

### 12. Manutenção e Conservação Predial (`manutencao_predial`)
- [ ] **AC-MAN-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-MAN-2:** "pintura de fachada" → APROVADO
- [ ] **AC-MAN-3:** "manutenção de software" → REJEITADO (é software)
- [ ] **AC-MAN-4:** "reparos hidráulicos prediais" → APROVADO
- [ ] **AC-MAN-5:** Documentar colisão com facilities e materiais_hidraulicos

### 13. Engenharia Rodoviária e Infraestrutura Viária (`engenharia_rodoviaria`)
- [ ] **AC-ROD-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-ROD-2:** "recapeamento asfáltico" → APROVADO
- [ ] **AC-ROD-3:** "sinalização viária" → APROVADO
- [ ] **AC-ROD-4:** "construção de ponte" → APROVADO ou vai para engenharia?
- [ ] **AC-ROD-5:** Documentar colisão com engenharia geral

### 14. Materiais Elétricos e Instalações (`materiais_eletricos`)
- [ ] **AC-ELE-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-ELE-2:** "cabo de rede" → ambíguo (materiais_eletricos ou informatica?)
- [ ] **AC-ELE-3:** "quadro de distribuição" → APROVADO
- [ ] **AC-ELE-4:** "luminária LED" → APROVADO
- [ ] **AC-ELE-5:** "equipamento eletrônico" → REJEITADO (é informatica)

### 15. Materiais Hidráulicos e Saneamento (`materiais_hidraulicos`)
- [ ] **AC-HID-1:** Precision >= 85%, Recall >= 70%
- [ ] **AC-HID-2:** "tubo PVC" → APROVADO
- [ ] **AC-HID-3:** "bomba hidráulica" → APROVADO
- [ ] **AC-HID-4:** "hidratante" → REJEITADO (é saude/cosmético)
- [ ] **AC-HID-5:** Documentar colisão com manutencao_predial (reparos hidráulicos)

## Output Final

- [ ] **AC-FINAL-1:** Tabela consolidada 15 setores x [Precision, Recall, FP count, FN count, LLM calls]
- [ ] **AC-FINAL-2:** Lista de colisões cross-setor (pares que compartilham >5% dos itens)
- [ ] **AC-FINAL-3:** Relatório `docs/audit/precision-recall-benchmark-YYYY-MM-DD.md`
- [ ] **AC-FINAL-4:** Se qualquer setor tem Precision < 85% ou Recall < 70%, criar sub-story específica

## Impacto

- **Prova de qualidade:** Primeira vez que temos precision/recall medidos para todos os 15 setores
- **Sustenta a promessa comercial:** "0 falsos positivos" → Precision 95%+
- **Identifica setores fracos:** Prioriza investimento em keywords/exclusions

## Arquivos

- `backend/scripts/audit_pipeline_complete.py` (execução)
- `docs/audit/precision-recall-benchmark-YYYY-MM-DD.md` (resultado)
- `backend/sectors_data.yaml` (correções emergenciais se precision < 85%)
