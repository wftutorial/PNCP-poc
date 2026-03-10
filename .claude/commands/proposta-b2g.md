# /proposta-b2g — Gerador de Proposta Comercial B2G

## Purpose

Gera um PDF de proposta comercial personalizada e profissional para um lead especifico. Cruza perfil da empresa + oportunidades abertas + historico gov para construir uma proposta irrecusavel que mostra ao decisor exatamente quanto dinheiro ele esta deixando na mesa.

**Output primario:** `docs/propostas/proposta-{CNPJ}-{YYYY-MM-DD}.pdf`
**Output secundario:** `docs/propostas/proposta-{CNPJ}-{YYYY-MM-DD}.md` (markdown)
**Rodape:** "Tiago Sasaki - Consultor de Licitacoes (48)9 8834-4559"

---

## Usage

```
/proposta-b2g 12.345.678/0001-90
/proposta-b2g 12345678000190 --pacote premium
/proposta-b2g 12345678000190 --pacote basico --desconto 10
/proposta-b2g 12345678000190 --from-qualify docs/intel-b2g/qualified-medicamentos-2026-03-10.xlsx
```

## Pacotes Disponiveis

| Pacote | Preco | Entregaveis | ICP |
|--------|-------|-------------|-----|
| **Basico** | R$1.500/mes | Monitoramento + Alertas + 1 report/mes | PME com 1-5 contratos/ano |
| **Premium** | R$3.000/mes | Basico + Analise estrategica + Suporte a propostas + 4 reports/mes | Medio porte, 5-20 contratos/ano |
| **Enterprise** | R$5.000+/mes | Premium + Dedicado + Gestao completa do pipeline | Grande porte, 20+ contratos/ano |

Se `--pacote` nao for informado, o command seleciona automaticamente baseado no tier/score do `/qualify-b2g`.

## What It Does

### Phase 1: Coleta de Inteligencia (@data-engineer)

1. **Perfil da empresa** — OpenCNPJ (razao social, CNAE, porte, capital, cidade, QSA, decisor)
   ```bash
   CNPJ_LIMPO=$(echo "{CNPJ}" | tr -d './-')
   curl -s "https://api.opencnpj.org/${CNPJ_LIMPO}"
   ```

2. **Historico governamental** — PNCP contratos (ultimos 12 meses deste CNPJ)
   ```bash
   curl -s "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao\
     ?dataInicial={12_meses_atras_YYYYMMDD}\
     &dataFinal={hoje_YYYYMMDD}\
     &cnpj=${CNPJ_LIMPO}\
     &pagina=1&tamanhoPagina=50"
   ```
   - Contar contratos, somar valores, listar orgaos, mapear UFs
   - Calcular faturamento gov mensal medio
   - Identificar concentracao (% de receita do top orgao)

3. **Sancoes** — Portal da Transparencia (verificar impedimentos)
   ```bash
   PT_KEY=$(grep PORTAL_TRANSPARENCIA_API_KEY backend/.env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
   curl -s -H "chave-api-dados: ${PT_KEY}" \
     "https://api.portaldatransparencia.gov.br/api-de-dados/pessoa-juridica?cnpj=${CNPJ_LIMPO}"
   ```

4. **Oportunidades abertas** — Varredura PNCP + PCP dos editais ATUALMENTE abertos no setor
   - Usar keywords do setor mapeado via CNAE
   - Filtrar ultimos 30 dias
   - Contar: total de editais, valor total, por UF, por modalidade

5. **Cross-reference qualify** — Se `--from-qualify` fornecido, puxar score e tier do lead

### Phase 2: Calculo de ROI (@analyst)

O coracao da proposta. Demonstrar matematicamente o retorno do investimento.

**Metricas calculadas:**

1. **Oportunidades perdidas** — Editais abertos AGORA que o lead poderia participar mas provavelmente nao sabe
   ```
   Editais_setoriais_abertos - Editais_que_o_lead_participa = Oportunidades_perdidas
   ```

2. **Valor na mesa** — Soma dos valores estimados das oportunidades perdidas
   ```
   Valor_na_mesa = SUM(valor_estimado dos editais nao participados)
   ```

3. **Taxa de vitoria estimada** — Baseada no historico do lead
   ```
   Taxa_vitoria = Contratos_ganhos / Participacoes_estimadas
   Se sem historico suficiente, usar media setorial: 15-25%
   ```

4. **Receita incremental projetada** — O que o lead ganharia com a consultoria
   ```
   Receita_incremental = Valor_na_mesa × Taxa_vitoria × Fator_melhoria(1.3)
   ```

5. **ROI da consultoria**
   ```
   ROI = (Receita_incremental_anual - Custo_consultoria_anual) / Custo_consultoria_anual × 100
   ```

6. **Payback** — Em quantos meses o investimento se paga
   ```
   Payback_meses = Custo_consultoria_mensal / (Receita_incremental_mensal)
   ```

### Phase 3: Construcao da Proposta (@analyst + @dev)

**Estrutura do PDF (12 secoes):**

#### 1. Capa
- Titulo: "Proposta de Consultoria em Licitacoes Publicas"
- Subtitulo: "Preparada exclusivamente para {Nome_Fantasia}"
- CNPJ, Data, Consultor
- Visual limpo e profissional

#### 2. Carta ao Decisor
- Enderecada ao socio-administrador pelo nome (do QSA)
- Tom: consultivo, direto, sem floreios
- 3 paragrafos max:
  1. "Identifiquei que sua empresa {fato_especifico}..."
  2. "Existem {N} oportunidades abertas que voce pode estar perdendo..."
  3. "Esta proposta detalha como posso ajudar..."

#### 3. Diagnostico da Empresa
- Dados cadastrais (razao, fantasia, CNAE, porte, capital, cidade)
- Historico gov: {N} contratos em 12 meses, R${valor} faturamento gov
- UFs de atuacao
- Orgaos mais frequentes
- Analise de concentracao: "{X}% da receita gov vem de {orgao_top}" — risco ou oportunidade

#### 4. Radiografia do Mercado
- Total de editais abertos no setor: {N}
- Valor total em disputa: R${valor}
- Distribuicao por UF (tabela)
- Distribuicao por modalidade
- Tendencia: crescendo/estavel/caindo vs mesmo periodo ano anterior (se dados disponiveis)

#### 5. Oportunidades Identificadas (TOP 10)
- Tabela com os 10 melhores editais abertos para este CNPJ
- Colunas: Orgao | UF | Objeto (resumido) | Valor | Modalidade | Encerramento | Aderencia
- Ordenados por aderencia ao perfil × valor

#### 6. O que Voce Esta Perdendo (seção de dor)
- Numero de editais que passaram nos ultimos 6 meses sem participacao
- Valor acumulado desses editais
- "Empresas do seu porte no setor participam em media de {X} editais/mes. Voce participa de {Y}."
- Grafico simples: Potencial vs Realizado

#### 7. ROI da Consultoria
- Tabela clara:
  | Metrica | Valor |
  |---------|-------|
  | Investimento mensal | R${preco_pacote} |
  | Oportunidades mapeadas/mes | {N} |
  | Receita incremental projetada/mes | R${valor} |
  | ROI em 12 meses | {X}% |
  | Payback | {N} meses |
- Disclaimer: "Projecoes baseadas em dados publicos. Resultados dependem da execucao."

#### 8. Pacote Proposto
- Detalhamento do pacote selecionado
- Entregaveis com frequencia (semanal/mensal)
- O que esta INCLUIDO (lista clara)
- O que NAO esta incluido (evitar expectativas erradas)

#### 9. Metodologia de Trabalho
- Como funciona o monitoramento (fontes: PNCP, PCP, ComprasGov)
- Frequencia de reports
- Canal de comunicacao (WhatsApp + Email)
- Tempo de resposta para alertas de editais urgentes

#### 10. Sobre o Consultor
- Mini-bio profissional de Tiago Sasaki
- Experiencia em licitacoes
- Tecnologia proprietaria (SmartLic — sem detalhar demais)
- Diferenciais vs consultorias tradicionais

#### 11. Condicoes Comerciais
- Preco: R${valor}/mes
- Desconto (se `--desconto` informado): "Condicao especial: {X}% — valida ate {data+15dias}"
- Forma de pagamento: Boleto, PIX, Cartao
- Prazo de contrato: Minimo 3 meses
- Cancelamento: 30 dias de antecedencia
- Inicio: Imediato apos aceite

#### 12. Proximos Passos
- CTA claro: "Para iniciar, responda este WhatsApp ou ligue para (48)9 8834-4559"
- Timeline:
  1. Aceite da proposta → Dia 0
  2. Onboarding (perfil + preferencias) → Dia 1-2
  3. Primeiro report de oportunidades → Dia 3-5
  4. Monitoramento continuo → Dia 6+

**Rodape em todas as paginas:** "Tiago Sasaki - Consultor de Licitacoes (48)9 8834-4559"

### Phase 4: Geracao do PDF (@dev)

```bash
cd C:/Users/tiagosasaki/Desktop/PNCP-poc
python scripts/generate-proposta-b2g.py \
  --input docs/propostas/data-{CNPJ}-{data}.json \
  --output docs/propostas/proposta-{CNPJ}-{data}.pdf
```

Se o script nao existir, gerar o JSON de dados e criar o PDF via reportlab/weasyprint ou equivalente disponivel.

## APIs Reference

| API | Endpoint | Auth | Rate Limit |
|-----|----------|------|------------|
| OpenCNPJ | `api.opencnpj.org/{CNPJ}` | Nenhuma | 50 req/s |
| Portal Transparencia | `api.portaldatransparencia.gov.br/api-de-dados/` | `chave-api-dados` header | 90 req/min |
| PNCP | `pncp.gov.br/api/consulta/v1/contratacoes/publicacao` | Nenhuma | ~100 req/min |
| PCP v2 | `compras.api.portaldecompraspublicas.com.br/v2/licitacao/processos` | Nenhuma | ~60 req/min |

## Downstream

```
/intel-b2g leads de engenharia           → 150 leads brutos
/qualify-b2g engenharia                  → 35 Tier1
/proposta-b2g {CNPJ_tier1_top}          → PDF proposta personalizada
/cadencia-b2g engenharia --tier 1        → cadencia com proposta em anexo
```

## Params

$ARGUMENTS
