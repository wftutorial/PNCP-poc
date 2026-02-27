# STORY-304: Silent Failure Elimination

**Sprint:** CRITICAL — Semana 1 pos-recovery
**Size:** L (8-12h)
**Root Cause:** Diagnostic Report 2026-02-27 — BLOCKER B2/B3, HIGHs H1-H5
**Depends on:** STORY-303 (backend precisa estar de pe)
**Industry Standard:** [PEP 20 — Zen of Python](https://peps.python.org/pep-0020/): "Errors should never pass silently. Unless explicitly silenced."

## Contexto

A auditoria tecnica (Track E) encontrou **19 instancias** de excecoes silenciadas em caminhos criticos do backend. O padrao `except Exception: pass` e o anti-pattern mais perigoso em Python — erros acontecem e ninguem sabe. O sistema mente sobre sua propria saude.

**Impacto concreto:** Fontes de dados podem falhar, resultados podem ser incompletos, callbacks podem quebrar, e o operador NAO TEM COMO SABER. O usuario recebe dados parciais achando que sao completos.

**Evidencia da auditoria (19 findings):**

| Severidade | Qtd | Descricao |
|------------|-----|-----------|
| HIGH | 2 | Erros criticos logados como WARNING (search_pipeline.py:120, :307) |
| MEDIUM | 9 | `except Exception: pass` em fluxos que impactam dados/estado |
| LOW | 6 | `except Exception: pass` em cleanup/metrics (aceitavel com log) |
| INCOMPLETE | 2 | Logam WARNING mas sem Sentry capture (llm_arbiter.py:96, :116) |

**Fundamentacao tecnica:**
- [PEP 20 — Zen of Python](https://peps.python.org/pep-0020/): "Errors should never pass silently. Unless explicitly silenced."
- [Real Python — The Most Diabolical Python Antipattern](https://realpython.com/the-most-diabolical-python-antipattern/): "`except Exception: pass` is the most dangerous antipattern in Python"
- [Pybites — Avoiding Silent Failures](https://pybit.es/articles/python-errors-should-not-pass-silently/): "Debugging silent errors will be really difficult, since they won't show up in logs and exception reporting tools like Sentry"
- [DEV Community — Python Exceptions Anti-Pattern](https://dev.to/wemake-services/python-exceptions-considered-an-anti-pattern-17o9): "Don't catch any error — always specify which exceptions you are prepared to recover from"
- [Professional Programming — Error Handling Antipatterns](https://github.com/charlax/professional-programming/blob/master/antipatterns/error-handling-antipatterns.md): "Silencing an exception won't make the error go away: it's better for something to break hard, than for an error to be silenced"
- [Index.dev — How to Avoid Silent Failures](https://www.index.dev/blog/avoid-silent-failures-python): "Robust logging is the cornerstone of error detection"

## Acceptance Criteria

### Grupo 1: BLOCKERs — Exception silencing em dados de busca

- [ ] AC1: `consolidation.py:410` — `on_source_complete` callback: substituir `except Exception: pass` por `logger.warning(f"on_source_complete callback error for {code}: {e}")` + continuar
- [ ] AC2: `consolidation.py:431` — mesma correcao para path de erro
- [ ] AC3: `consolidation.py:475` — mesma correcao para fallback completion
- [ ] AC4: `search_pipeline.py:151` — link extraction: substituir `except Exception: pass` por `logger.debug(f"PNCP link extraction failed for {numeroControlePNCP}: {e}")` + fallback para URL vazia (ja funciona, so precisa logar)

### Grupo 2: HIGHs — Severidade errada (WARNING deveria ser ERROR)

- [ ] AC5: `search_pipeline.py:120` — email quota notification failure: mudar de `logger.warning` para `logger.error` + adicionar `sentry_sdk.capture_exception(e)`
- [ ] AC6: `search_pipeline.py:307` — bid conversion failure em response path: mudar de `logger.warning` para `logger.error` + adicionar `sentry_sdk.capture_exception(e)` + incrementar counter metrica `ITEMS_CONVERSION_ERRORS`

### Grupo 3: HIGHs — State machine transitions silenciadas

- [ ] AC7: `routes/search.py:957` — state machine completion: substituir `except Exception: pass` por `logger.warning(f"State machine complete() failed: {e}")`
- [ ] AC8: `routes/search.py:981` — state machine timeout: idem
- [ ] AC9: `routes/search.py:1005` — state machine failure: idem

### Grupo 4: MEDIUMs — Seguranca e observabilidade

- [ ] AC10: `routes/pipeline.py:47` — master access check: substituir `except Exception: pass` por `logger.warning(f"Master access check failed, falling through: {e}")`
- [ ] AC11: `routes/pipeline.py:86` — mesma correcao (segunda instancia)
- [ ] AC12: `routes/search.py:302` — SSE metrics: substituir `except Exception: pass` por `logger.debug(f"SSE metrics unavailable: {e}")`

### Grupo 5: INCOMPLETEs — Logging sem Sentry

- [ ] AC13: `llm_arbiter.py:96` — cache read failure: adicionar `sentry_sdk.capture_exception(e)` ao bloco existente (ja loga WARNING)
- [ ] AC14: `llm_arbiter.py:116` — cache write failure: idem

### Grupo 6: LOWs — Cleanup (aceitavel, mas deve logar)

- [ ] AC15: `consolidation.py:834` — adapter.close(): substituir `except Exception: pass` por `logger.debug(f"Adapter close error (non-critical): {e}")`
- [ ] AC16: `consolidation.py:840` — fallback_adapter.close(): idem
- [ ] AC17: `pncp_client.py:411,436,501` — Redis CB fallback: adicionar `logger.debug(f"Redis CB fallback: {e}")` (3 locais)

### Quality

- [ ] AC18: Zero instancias de `except Exception: pass` ou `except: pass` em arquivos criticos (consolidation.py, search_pipeline.py, routes/search.py, routes/pipeline.py)
- [ ] AC19: Grep automatizado: `grep -rn "except.*:.*pass" backend/ --include="*.py"` retorna APENAS instancias em testes ou locais explicitamente documentados
- [ ] AC20: Testes existentes passando (5131+ backend, 2681+ frontend)
- [ ] AC21: Sentry recebe eventos para erros que antes eram silenciosos (verificar no dashboard apos deploy)

## Technical Notes

### Principio: Cada except DEVE fazer pelo menos uma das 3 coisas

1. **Logar** o erro (severity apropriada: ERROR para impacto no usuario, WARNING para degradacao, DEBUG para cleanup)
2. **Reportar** ao Sentry (se impacta dados ou experiencia do usuario)
3. **Propagar** a excecao (se nao ha recovery possivel)

`pass` sozinho NAO e aceitavel. O unico caso aceitavel e `contextlib.suppress(SpecificException)` com comentario explicando POR QUE.

### Regra de severidade

| Impacto | Severidade | Sentry |
|---------|-----------|--------|
| Dado incorreto/incompleto pro usuario | ERROR | Sim |
| Degradacao de experiencia (lento, sem progresso) | WARNING | Sim |
| Metrica/log/cleanup falhando | DEBUG | Nao |

### NAO mudar a logica de controle de fluxo

Esta story NAO muda como o sistema se comporta — apenas torna os erros VISIVEIS. Todos os fallbacks continuam funcionando. A unica diferenca e que agora sabemos quando eles sao acionados.

## Files to Change

| File | Linhas | Tipo |
|------|--------|------|
| `backend/consolidation.py` | 410, 431, 475, 834, 840 | except pass → logger |
| `backend/search_pipeline.py` | 120, 151, 307 | WARNING → ERROR + Sentry |
| `backend/routes/search.py` | 302, 957, 981, 1005 | except pass → logger |
| `backend/routes/pipeline.py` | 47, 86 | except pass → logger.warning |
| `backend/llm_arbiter.py` | 96, 116 | Adicionar Sentry capture |
| `backend/pncp_client.py` | 411, 436, 501 | except pass → logger.debug |

## Definition of Done

- [ ] Zero `except Exception: pass` em caminhos criticos
- [ ] Sentry recebendo eventos de erros que antes eram invisiveis
- [ ] Log levels corretos (ERROR onde impacta usuario, WARNING onde degrada, DEBUG onde cleanup)
- [ ] Testes passando
- [ ] Grep clean: nenhum `except.*: pass` novo introduzido
