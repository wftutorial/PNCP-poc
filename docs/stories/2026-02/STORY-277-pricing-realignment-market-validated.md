# STORY-277: Repricing Fundamentado — R$1.999 → Faixa de Mercado

**Priority:** P0 BLOCKER
**Effort:** 1 day (decisao) + 1 day (implementacao)
**Squad:** @po + @pm + @dev
**Replaces:** STORY-269 (pricing strategy) — agora com dados reais de mercado

## Fundamentacao (Precos Reais dos Concorrentes — Fev 2026)

### Mapeamento Competitivo Validado

| Plataforma | Menor Plano | Plano Premium | AI? | Fonte |
|------------|------------|--------------|-----|-------|
| Alerta Licitacao | R$31/mes (anual) | R$45/mes | Nao | [alertalicitacao.com.br](https://alertalicitacao.com.br/) |
| LicitaIA | R$67/mes | R$247/mes (ilimitado) | Sim (core) | [licitaia.app](https://www.licitaia.app/) |
| Licitei | R$0 (free) | R$393/mes (Premium) | Sim | [licitei.com.br/planos](https://www.licitei.com.br/planos) |
| Portal Compras | R$96-149/mes | R$149/mes | Nao | [conlicitacao.com.br](https://conlicitacao.com.br/) |
| Licita Ja | R$160/mes (3 anos) | R$235/mes | Limitado | [licitaja.com.br](https://www.licitaja.com.br/subscription.php) |
| Siga Pregao | R$208/mes (anual) | R$397/mes | Sim (12-200/dia) | [sigapregao.com.br/p/precos](https://www.sigapregao.com.br/p/precos/) |
| ConLicitacao | Oculto (sales-led) | Oculto | Sim | [conlicitacao.com.br/planos](https://conlicitacao.com.br/planos/) |
| Effecti | Oculto (sales-led) | Oculto | Sim | [effecti.com.br/planos](https://effecti.com.br/planos/) |
| **SmartLic** | — | **R$1.999/mes** | Sim (core) | — |

### Analise de Posicionamento

- **Faixa de mercado para AI + busca:** R$100-400/mes
- **SmartLic a R$1.999 e 5-13x acima do mercado**
- **Maior preco publico do mercado:** Licitei Multiempresas R$1.179/mes (para 3 CNPJs)
- Concorrentes na faixa R$300-400 incluem: robo de lance, automacao de proposta, monitoramento de chat — funcionalidades que SmartLic NAO tem ainda

### O que SmartLic tem de unico
- Classificacao IA por setor (GPT-4.1-nano) — nenhum concorrente faz
- Viability assessment 4 fatores — unico
- Multi-fonte consolidada (PNCP + PCP + ComprasGov) com dedup

### O que SmartLic NAO tem (vs concorrentes a R$300-400)
- Robo de lance automatico
- Automacao de proposta
- Monitoramento de chat/pregoeiro
- Email alerts/digest (STORY-278)
- Multi-CNPJ

## Opcoes de Pricing (Decisao PO — Timebox 24h)

### Opcao 1: Beta Gratuito (RECOMENDADO para GTM)
- **R$0 por 30 dias** (beta aberto, sem cartao)
- Apos beta: SmartLic Pro R$297/mes (anual) / R$397/mes (mensal)
- **Racional:** Posiciona no topo do mercado visivel (par com Siga Pregao/Licitei Premium) mas justificado pela IA unica. Beta gratuito elimina barreira de entrada.
- **Benchmark:** Licitei oferece plano FREE. LicitaIA tem garantia 7 dias.

### Opcao 2: Entry Tier + Premium
- **SmartLic Busca:** R$97/mes (busca + filtro, sem IA, sem pipeline)
- **SmartLic Pro:** R$297/mes (tudo incluso)
- **Racional:** Entrada competitiva com LicitaIA (R$67-117), upsell para Pro
- **Risco:** Dois planos = complexidade de billing/onboarding

### Opcao 3: Credit-Based (modelo LicitaIA)
- **R$67/mes** (30 buscas com IA)
- **R$117/mes** (60 buscas)
- **R$197/mes** (ilimitado)
- **Racional:** Alinha com modelo de mercado emergente
- **Risco:** Requer refactor significativo do quota system

## Acceptance Criteria

### AC1: Decisao de Pricing (Dia 1 — Timebox 24h)
- [ ] PO escolhe opcao (1, 2, ou 3) com justificativa
- [ ] Se nenhuma decisao em 24h: **default = Opcao 1** (beta gratuito + R$297-397)

### AC2: Implementar Pricing Escolhido (Dia 2)
- [ ] Atualizar `billing.py`: novo(s) price_id(s) no Stripe
- [ ] Atualizar `frontend/app/planos/page.tsx`: novos precos e copy
- [ ] Atualizar `frontend/app/termos/page.tsx` secao 3.2: remover phantom plans (E-HIGH-001)
- [ ] Atualizar quota.py: limites do novo plano

### AC3: Remover Phantom Plans do ToS
- [ ] Secao 3.2 de `/termos` referencia planos que NAO EXISTEM:
  - "Free: 5 buscas/mes" (nao existe)
  - "Professional: buscas ilimitadas" (nao existe)
  - "Enterprise: API access, white-label, SLA 24/7" (nao existe)
- [ ] Reescrever para refletir planos reais

### AC4: Landing Page Pricing Section
- [ ] Atualizar comparativo de precos se visivel na landing
- [ ] Adicionar badge "Beta" se Opcao 1

## Fontes dos Dados
- Licitei: https://www.licitei.com.br/planos
- Siga Pregao: https://www.sigapregao.com.br/p/precos/
- LicitaIA: https://www.licitaia.app/
- Licita Ja: https://www.licitaja.com.br/subscription.php
- Alerta Licitacao: https://alertalicitacao.com.br/
