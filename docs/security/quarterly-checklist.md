# Checklist de Segurança Trimestral — cryptography/SIGSEGV

**Frequência:** Trimestral (Q1/Q2/Q3/Q4)
**Responsável:** @devops
**Tempo estimado:** 2h por revisão

---

## Checklist

### 1. Auditoria de CVEs (30min)

```bash
cd backend
source venv/bin/activate  # ou venv\Scripts\activate no Windows
python ../scripts/security/check_cryptography_cves.py
```

- [x] Zero CVEs críticos (CVSS >= 9.0) na faixa 46.x? — SIM (auditoria 2026-03-30: 0 CVEs em cryptography 46.0.6)
- [x] Zero CVEs altos (CVSS >= 7.0) sem mitigação conhecida? — SIM (PyJWT CVE-2026-32597 MEDIUM corrigido via upgrade para 2.12.0)
- [x] Atualizar tabela CVEs em `docs/security/cryptography-sigsegv-status.md` — CONCLUIDO 2026-03-30

### 2. Teste de Upgrade em Staging (60min)

```bash
# 1. Instalar versão candidata em ambiente isolado
pip install "cryptography>=47.0" --upgrade

# 2. Verificar imports básicos
python -c "from cryptography.fernet import Fernet; print('OK')"
python -c "import uvicorn; print('OK')"

# 3. Load test (100 requests)
python scripts/security/test_cryptography_load.py --requests 100

# 4. Verificar logs — zero SIGSEGV
grep -i "sigsegv\|segfault\|signal 11" /tmp/test_output.log
```

- [ ] Versão 47.x testada sem SIGSEGV? — BLOQUEADO: 47.x ainda nao publicado (verificado 2026-03-30)
- [x] 100 requests completados sem crash? — PASS: 46.0.6 = 100/100 OK, 0 erros (2026-03-30)
- [ ] Worker startup/shutdown limpo? — pendente para quando 47.x for publicado

### 3. Decisão e Documentação (30min)

- [x] Atualizar `docs/security/cryptography-sigsegv-status.md` com resultado — CONCLUIDO 2026-03-30
- [ ] Se 47.x estável: abrir issue para upgrade com resultados do teste — aguardando 47.x ser publicado
- [ ] Se 47.x instável: documentar versão testada + resultado + próxima data — N/A por enquanto
- [x] Commit com mensagem: `docs(security): quarterly cryptography audit YYYY-QN` — pendente neste PR

---

## Critério para Upgrade

**Upgrade AUTORIZADO quando:**
- 100 requests em staging sem SIGSEGV
- Zero CVEs críticos em 46.x pendentes (ou CVE critico em 46.x com fix em 47.x)
- upstream cryptography issue resolvido

**Manter pin quando:**
- SIGSEGV reproduzido em staging com 47.x
- Nenhuma CVE urgente em 46.x

---

*Última revisão: 2026-03-30. Próxima: 2026-06-30*
