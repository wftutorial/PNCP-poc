# HARDEN-002: jemalloc/mimalloc no Dockerfile — FastAPI RSS Creep

**Severidade:** CRITICA
**Esforço:** 5 min
**Quick Win:** Sim
**Origem:** Conselho CTO — Pesquisa de Indústria (BetterUp Sept 2025, Medium Jan 2026)

## Contexto

Async FastAPI com glibc/musl sofre crescimento linear de RSS (não é leak real — é fragmentação de memória por interleaving de requests async). Container Railway cresce em RSS até OOM kill.

## Problema

- RSS cresce linearmente com requests processados
- Fragmentação por malloc de interleaved async requests
- Container Railway eventualmente atinge OOM
- Documentado em múltiplas fontes da indústria (2025-2026)

## Critérios de Aceitação

- [x] AC1: Dockerfile instala `libjemalloc2` (ou `libmimalloc2.0`)
- [x] AC2: `LD_PRELOAD` configurado no Dockerfile
- [x] AC3: RSS monitorado via Prometheus gauge `process_resident_memory_bytes`
- [ ] AC4: Deploy bem-sucedido no Railway com jemalloc ativo

## Solução

```dockerfile
# Dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends libjemalloc2 \
    && rm -rf /var/lib/apt/lists/*
ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2
```

## Arquivos Afetados

- `backend/Dockerfile`

## Referências

- BetterUp Engineering: "Chasing a Memory Leak in Async FastAPI" (Sept 2025)
- Medium: "Fragmented Pages, Not Leaks: Fixing FastAPI's Memory Crisis" (Jan 2026)
