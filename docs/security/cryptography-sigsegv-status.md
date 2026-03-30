# Cryptography SIGSEGV — Status de Monitoramento

**Débito:** DEBT-SYS-002 (DEBT-206)
**Severidade:** Crítica — SIGSEGV intermitente com C extensions
**Status atual:** MONITORAMENTO ATIVO — pin <47.0 mantido
**Última revisão:** 2026-03-30
**Próxima revisão:** 2026-06-30 (Q3 2026)

---

## Problema

O SmartLic usa `cryptography` pinada em `<47.0` (`requirements.txt`) devido a SIGSEGV
intermitente ao carregar extensões C com uvloop. O SIGSEGV ocorre em alguns ambientes
durante inicialização do worker quando `cryptography >= 47.0` está instalada.

**Ticket de referência:** CRIT-SIGSEGV (interno)
**Upstream issue:** cryptography#<TBD> — aguardando fix em 47.x

---

## Versão Atual Pinada

```
cryptography>=41.0.3,<47.0   # ver requirements.txt
```

---

## Histórico de Testes

| Data | Versão Testada | Resultado | Testador | Notas |
|------|---------------|-----------|---------|-------|
| 2026-03-30 | 46.x (atual) | ✅ STABLE | @devops | Produção estável, sem crashes |
| 2026-03-30 | 47.x | ⚠️ NÃO TESTADO | — | Aguardando teste em staging |

---

## CVEs Ativos na Faixa 46.x

> Executar `pip-audit -r requirements.txt` ou `scripts/security/check_cryptography_cves.py`
> para relatório atualizado. Atualizar esta tabela após cada auditoria.

| CVE | Severidade | Versão afetada | Status |
|-----|-----------|----------------|--------|
| — | — | — | Auditoria pendente |

---

## Procedimento de Upgrade para 47.x

Quando `cryptography >= 47.0` estiver estável:

1. Criar branch `fix/cryptography-upgrade`
2. Atualizar `requirements.txt`: mudar `<47.0` para `>=47.0`
3. Deploy em staging (Railway preview)
4. Load test: 100 requests sem SIGSEGV
   ```bash
   python scripts/security/test_cryptography_load.py --requests 100
   ```
5. Monitorar logs por 24h: `railway logs --tail | grep -i "sigsegv\|segfault\|crash"`
6. Se stable: abrir PR, remover pin
7. Remover workarounds de uvloop em `backend/main.py` (se existirem)

---

## Impacto de NÃO Fazer Upgrade

- Exposição a CVEs não corrigidos em 46.x
- Impossibilidade de atualizar outras libs que dependem de cryptography >=47.0
- Acumulação de débito técnico de segurança

---

## Referências

- [cryptography changelog](https://cryptography.io/en/latest/changelog/)
- [pyup.io safety DB](https://pyup.io/safety/)
- `scripts/security/check_cryptography_cves.py` — auditoria automatizada
- `docs/security/quarterly-checklist.md` — procedimento de revisão trimestral
