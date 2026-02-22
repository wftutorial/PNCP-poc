# CRIT-FLT-001 — EPI Context Gate Excessivamente Restritiva (Falso Negativo)

**Prioridade:** P0 — Falso Negativo Confirmado
**Estimativa:** 2h
**Origem:** Auditoria de Pipeline 2026-02-22
**Track:** Backend

## Problema

A keyword "epi" no setor `vestuario` exige context_required com termos como:
```
["vestuario", "vestimenta", "uniforme", "fardamento", "roupa", "calca", "camisa", "bota", "botina"]
```

Porém, a formulação padrão em licitações públicas é:
> "EPI — Equipamento de Proteção Individual"

O termo "proteção" / "protecao" / "segurança" / "seguranca" **NÃO está na lista de contexto**. Resultado: licitações legítimas de EPIs de vestuário (calçados de segurança, luvas, etc.) são **rejeitadas silenciosamente**.

### Exemplo Real
```
Objeto: "Aquisição de EPI — equipamento de proteção individual para servidores"
Keyword match: "epi" ✓
Context found: NENHUM ✗
Decisão: REJECTED → FALSO NEGATIVO
```

## Acceptance Criteria

- [ ] **AC1:** Adicionar `"proteção"`, `"protecao"`, `"segurança"`, `"seguranca"`, `"proteção individual"`, `"protecao individual"`, `"segurança do trabalho"`, `"seguranca do trabalho"` ao context_required de "epi" e "epis" no `sectors_data.yaml` (setor vestuario)
- [ ] **AC2:** Verificar se outros setores têm keywords com context gates igualmente restritivos:
  - `informatica`: "servidor" (verificar se "virtual", "virtualização" estão no contexto)
  - `informatica`: "monitor" (verificar se "polegada" está no contexto)
  - `informatica`: "switch" (verificar se "porta", "gbps" estão no contexto)
- [ ] **AC3:** Adicionar testes unitários para cada context gate expandido
- [ ] **AC4:** Rodar `audit_all_sectors.py` antes e depois da mudança e comparar falsos negativos

## Impacto

- **Setor mais afetado:** vestuario (EPIs são ~15% do mercado de uniformes)
- **Risco de regressão:** BAIXO (apenas expande contextos, não remove)
- **Zero LLM cost:** Mudança é puramente determinística

## Arquivos

- `backend/sectors_data.yaml` (context_required para epi/epis)
- `backend/tests/test_filter.py` (novos testes de contexto)
