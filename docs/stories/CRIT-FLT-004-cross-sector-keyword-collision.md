# CRIT-FLT-004 — Cross-Sector Keyword Collisions (Falso Positivo)

**Prioridade:** P1 — Falso Positivo Sistemático
**Estimativa:** 4h
**Origem:** Auditoria de Pipeline 2026-02-22
**Track:** Backend

## Problema

Palavras-chave genéricas matcham em múltiplos setores sem contexto suficiente, causando **falsos positivos cross-setor**. O proximity context filter (Camada 1B.3) e co-occurrence rules (Camada 1B.5) mitigam parcialmente, mas existem lacunas:

### Colisões Identificadas

| Keyword | Setor Correto | Falso Positivo Em | Exemplo |
|---------|--------------|-------------------|---------|
| "sistema" | software | Qualquer setor que mencione "sistema de registro de preços" | 10 de 200 itens PNCP (5%) |
| "manutenção" | facilities, manutencao_predial | engenharia (manutenção de obras) | Frequente |
| "material" | papelaria, materiais_eletricos, materiais_hidraulicos | Qualquer licitação de "material" genérico | Altíssimo |
| "serviço" | facilities, software | Praticamente qualquer licitação | 56 de 200 itens (28%) |
| "instalação" | materiais_eletricos, materiais_hidraulicos | engenharia, software | Frequente |
| "equipamento" | informatica, saude | Qualquer setor com equipamentos | Frequente |
| "rede" | informatica | saude ("rede de saúde"), facilities ("rede de proteção") | Médio |
| "confecção" | vestuario | papelaria ("confecção de material gráfico") | Coberto por exclusão |

### "sistema de registro de preços" — Caso Especial
- 5% dos itens PNCP contêm essa frase no objetoCompra
- Se o setor "software" tem keyword "sistema", essas licitações matcham falsamente
- Nenhuma exclusão atual bloqueia "sistema de registro de preços" para o setor software
- O proximity filter não pega porque "sistema" e "registro de preços" são do mesmo domínio semântico

## Acceptance Criteria

- [ ] **AC1:** Adicionar exclusão "sistema de registro de preços" / "sistema de registro de precos" / "srp" ao setor `software` em `sectors_data.yaml`
- [ ] **AC2:** Adicionar exclusão "sistema de registro" ao setor `software`
- [ ] **AC3:** Auditar os 15 setores para keywords com alta ambiguidade cross-setor. Output: tabela de colisões potenciais
- [ ] **AC4:** Para keywords genéricas ("material", "serviço", "equipamento"), verificar se `context_required` existe e é suficiente
- [ ] **AC5:** Adicionar context_required para "sistema" no setor software: requer ["informação", "informacao", "software", "digital", "computador", "tecnologia", "ti", "automação", "automacao"]
- [ ] **AC6:** Rodar `audit_all_sectors.py` (cross-sector conflict analysis) e documentar resultado
- [ ] **AC7:** Testes unitários para cada nova exclusão e context gate

## Dados de Suporte

Auditoria PNCP 2026-02-22 (200 itens, SP/MG/RJ, 5 dias):
- "sistema de registro de precos": 10 itens (5%)
- "servico": 56 itens (28%)
- Descrições curtas (<50 chars): 19 itens (9.5%) — difícil classificar

## Impacto

- **Setor mais afetado:** software (keyword "sistema" é extremamente genérica)
- **Risco de regressão:** MÉDIO (adicionar exclusões pode criar falsos negativos se demasiado amplas)
- **Abordagem:** Exclusões específicas (frases exatas) + context gates (termos confirmatórios)

## Arquivos

- `backend/sectors_data.yaml` (exclusões e context_required para 15 setores)
- `backend/scripts/audit_all_sectors.py` (execução de validação)
- `backend/tests/test_filter.py`
