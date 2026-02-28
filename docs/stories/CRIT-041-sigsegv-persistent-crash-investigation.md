# CRIT-041: Investigar SIGSEGV Residual nos Workers

**Epic:** Production Stability
**Sprint:** Sprint 4
**Priority:** P2 — MEDIUM (preventivo)
**Story Points:** 5 SP
**Estimate:** 2-3 horas
**Owner:** @dev + @devops

---

## Problem

Após o fix CRIT-SIGSEGV (commit `b959cac`):
- Removido `uvicorn[standard]` → `uvicorn` (sem uvloop/httptools)
- Removido grpcio via `pip uninstall -y grpcio grpcio-status` no Dockerfile
- Habilitado `faulthandler.enable()` no topo de main.py
- Desabilitado `--preload` por padrão em start.sh

O Sentry registrou 55 eventos SIGSEGV (SMARTLIC-BACKEND-1N) nas últimas 48h, porém **todos ocorreram ANTES do deploy mais recente** (último SIGSEGV: ~19h atrás, deploy atual estável desde 14:22 UTC sem crashes). O fix parece ter funcionado, mas o issue Sentry permanece "Escalating" por conta do volume histórico.

**Status:** Monitoramento preventivo — confirmar que o fix é definitivo e resolver o issue no Sentry.

---

## Hipóteses de Investigação

### H1: Dockerfile cache bust desatualizado
O `LABEL build.timestamp="2026-02-20T12:00:00"` no Dockerfile pode não ter forçado rebuild. Railway pode estar usando imagem antiga (pré-fix) se o cache layer não foi invalidado.

**Ação:** Verificar se a imagem em produção realmente NÃO contém grpcio:
```bash
railway run pip list | grep -i grpc
railway run python -c "import uvloop; print('UVLOOP PRESENT')" 2>&1
```

### H2: cryptography C extension + --preload
start.sh documenta: "cryptography>=46.0.5 + --preload causes SIGSEGV". Embora `--preload` esteja desabilitado por padrão, verificar se `GUNICORN_PRELOAD=true` está setado em Railway.

### H3: Outro C extension fork-unsafe
Verificar todos os C extensions instalados no container:
```bash
railway run python -c "
import pkgutil, importlib
for m in pkgutil.iter_modules():
    try:
        mod = importlib.import_module(m.name)
        if hasattr(mod, '__file__') and mod.__file__ and ('.so' in mod.__file__ or '.pyd' in mod.__file__):
            print(f'{m.name}: {mod.__file__}')
    except: pass
"
```

### H4: Memory pressure (OOM → SIGSEGV)
Workers com `WEB_CONCURRENCY=2` em container com 8GB. Se um worker usa muita memória (large search results), o OOM killer pode enviar SIGSEGV ao invés do esperado SIGKILL.

---

## Acceptance Criteria

### Diagnóstico

- [ ] **AC1:** Executar `railway run pip list | grep -iE "grpc|uvloop|httptools"` e confirmar que NENHUM está presente
- [ ] **AC2:** Executar `railway run python -c "import faulthandler; print(faulthandler.is_enabled())"` e confirmar `True`
- [ ] **AC3:** Verificar `railway variables` para `GUNICORN_PRELOAD` — deve ser ausente ou `false`
- [ ] **AC4:** Verificar faulthandler output nos logs Railway — `Fatal Python error: Segmentation fault` deve mostrar o traceback completo
- [ ] **AC5:** Capturar output completo de um crash SIGSEGV do faulthandler (stack trace Python + C frame)

### Fix (baseado no diagnóstico)

- [ ] **AC6:** Se grpcio presente: atualizar Dockerfile `build.timestamp` para forçar rebuild + verificar que `pip uninstall` está executando
- [ ] **AC7:** Se faulthandler traceback aponta para C extension específico: remover e documentar
- [ ] **AC8:** Se OOM: considerar reduzir `WEB_CONCURRENCY=1` temporariamente ou aumentar memória do container
- [ ] **AC9:** Considerar migrar de Gunicorn (prefork) para Uvicorn standalone (`uvicorn main:app`) que NÃO faz fork — elimina toda a classe de problemas fork-unsafe

### Validação

- [ ] **AC10:** Após fix, monitorar Sentry por 24h — 0 eventos SIGSEGV
- [ ] **AC11:** Verificar que `smartlic_sse_connection_errors_total` não aumentou (sem regressão)

---

## Contexto Técnico

**Por que SIGSEGV em ASGI workers:**
- Gunicorn usa prefork model: processo pai faz fork() → processos filhos herdam memória
- C extensions (grpcio, uvloop, cryptography) usam thread-local state que é invalidado no fork
- Resultado: child process acessa memória corrompida → SIGSEGV

**Referências:**
- [gunicorn fork SIGSEGV issue #2761](https://github.com/benoitc/gunicorn/issues/2761)
- [grpc SIGSEGV issue #23796](https://github.com/grpc/grpc/issues/23796)
- [Python faulthandler docs](https://docs.python.org/3.12/library/faulthandler.html)
- [uvicorn deployment without gunicorn](https://www.uvicorn.org/deployment/)

---

## Arquivos Impactados

| Arquivo | Mudança Potencial |
|---------|-------------------|
| `backend/Dockerfile` | Atualizar build.timestamp, verificar uninstall |
| `backend/start.sh` | Possível migração para uvicorn standalone |
| `backend/requirements.txt` | Remover/pin C extensions problemáticos |
| Railway variables | `GUNICORN_PRELOAD`, `WEB_CONCURRENCY` |
