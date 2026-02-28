# SAB-010: Conta — polish do perfil de licitante e acentos

**Origem:** UX Premium Audit P2-01, P2-02, P3-04
**Prioridade:** P2 — Médio
**Complexidade:** M (Medium)
**Sprint:** SAB-P2
**Owner:** @dev
**Screenshot:** `ux-audit/27-conta-full.png`

---

## Problema

Três issues na página `/conta`:

### P2-01: Perfil de Licitante 0% sem guidance
"Perfil de Licitante" mostra "0/7 campos preenchidos — 0% completo" com 7 campos "Não informado". Sem explicação de benefício nem wizard guiado.

### P2-02: Acentos faltando em labels
Vários labels sem acentos:
- "Estados de atuacao" → "Estados de atuação"
- "Experiencia" → "Experiência"
- "Funcionarios" → "Funcionários"
- "licitacao" → "licitação" (seção Alertas)
- "Frequencia" → "Frequência"

### P3-04: Seções sem separação visual
7 seções empilhadas em scroll vertical longo sem tabs ou navegação interna.

---

## Critérios de Aceite

### Perfil de Licitante — Guidance (P2-01)

- [ ] **AC1:** Adicionar banner motivacional no topo da seção: "Perfil completo melhora a precisão da análise de viabilidade em até 40%"
- [ ] **AC2:** Botão "Preencher agora" que foca no primeiro campo vazio
- [ ] **AC3:** Progress bar visual colorida (vermelho 0-33%, amarelo 34-66%, verde 67-100%)

### Acentos (P2-02)

- [ ] **AC4:** Corrigir "Estados de atuacao" → "Estados de atuação"
- [ ] **AC5:** Corrigir "Experiencia" → "Experiência"
- [ ] **AC6:** Corrigir "Funcionarios" → "Funcionários"
- [ ] **AC7:** Corrigir "licitacao" → "licitação"
- [ ] **AC8:** Corrigir "Frequencia" → "Frequência"
- [ ] **AC9:** Grep por palavras sem acento em toda a página `/conta` para encontrar outros

### Navegação Interna (P3-04)

- [ ] **AC10:** Adicionar navegação por âncoras no topo da página (sticky): Perfil | Segurança | Senha | Acesso | Licitante | Alertas | LGPD
- [ ] **AC11:** Scroll suave ao clicar em cada âncora

---

## Arquivos Prováveis

- `frontend/app/conta/page.tsx` — página de conta
- `frontend/components/` — componentes de perfil/conta

## Notas

- Os acentos faltando podem ser do mesmo root cause que SAB-002 (Unicode escapes). Verificar se são `\u00` escapes ou realmente falta de acentos no source.
