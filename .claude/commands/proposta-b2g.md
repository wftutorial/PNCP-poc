# /proposta-b2g — Gerador de Proposta Comercial B2G

## Purpose

Gera um PDF de proposta comercial personalizada para um lead B2G de QUALQUER setor. A proposta apresenta o servico de consultoria em licitacoes — nao avalia editais nem faz analise de oportunidades (isso e trabalho do /intel-busca e /report-b2g).

**Output:** `docs/propostas/proposta-{CNPJ}-{slug}-{YYYY-MM-DD}.pdf` + `.md`

---

## REGRAS CRITICAS (ler antes de executar)

1. **NAO buscar editais individuais** — a proposta mostra volumes agregados do mercado, nunca lista editais
2. **NAO buscar historico de contratos** — suprimido da proposta
3. **NAO avaliar oportunidades** — a proposta VENDE o servico de monitoramento, nao FAZ o monitoramento
4. **NAO usar termos de construcao/engenharia** — comando e 100% setor-agnostico
5. **NAO referenciar cargo publico especifico** — autoridade e generica
6. **NAO incluir datas de editais, calendarios ou prazos de encerramento**
7. **Delegar coleta de dados ao script** — `python scripts/build-proposta-data.py {CNPJ}`
8. **Delegar geracao PDF ao script** — `python scripts/generate-proposta-pdf.py --input {json} --output {pdf}`

---

## Execucao (2 passos)

### Passo 1: Gerar JSON de dados

```bash
CNPJ_LIMPO=$(echo "{CNPJ}" | tr -d './-')
python scripts/build-proposta-data.py ${CNPJ_LIMPO} --pacote semanal
```

O script faz tudo automaticamente:
- Coleta perfil da empresa (OpenCNPJ ou BrasilAPI)
- Detecta setor via CNAE → `backend/sectors_data.yaml`
- Busca editais PNCP por UF/modalidade e agrega volumes
- Calcula UFs de abrangencia (vizinhas da sede)
- Gera campos setor-agnosticos (setor_intro, autoridade_exemplos, uf_abrangencia)
- Salva em `docs/propostas/data-{CNPJ}-{YYYY-MM-DD}.json`

Se o script falhar (ex: yaml nao encontrado), coletar APENAS:
- OpenCNPJ: `curl -s "https://api.opencnpj.org/${CNPJ_LIMPO}"`
- Montar JSON manualmente seguindo o schema abaixo

### Passo 2: Gerar PDF

```bash
python scripts/generate-proposta-pdf.py \
  --input docs/propostas/data-{CNPJ}-{YYYY-MM-DD}.json \
  --output docs/propostas/proposta-{CNPJ}-{slug}-{YYYY-MM-DD}.pdf \
  --pacote semanal
```

Pronto. Nao ha mais passos.

---

## Pacotes

| Pacote | Preco | Freq | UFs | Suporte |
|--------|-------|------|-----|---------|
| Mensal | R$997/mes | 1x/mes | UF sede | Comercial |
| **Semanal (Rec.)** | R$1.500/mes | 4x sem + 1x mes | sede + limitrofes | Estendido |
| Diario | R$2.997/mes | diario + sem + mes | sede + 4 UFs | Dedicado |

Desconto anual: pague 10, leve 12.

---

## Estrutura do PDF (11 secoes)

O script `generate-proposta-pdf.py` gera todas as secoes automaticamente a partir do JSON. Nao e necessario construir o PDF manualmente.

1. **Capa** — data, validade 15 dias, CNPJ, nome
2. **Carta ao Decisor** — usa `setor_intro` do JSON (generico por setor)
3. **Diagnostico da Empresa** — dados cadastrais, pontos fortes/atencao (sem historico de contratos)
4. **Panorama do Mercado** — volumes agregados por faixa de valor e modalidade (sem editais individuais)
5. **Dimensionamento da Oportunidade** — ROI, COM vs SEM monitoramento, projecao anual
6. **O Que Cada Relatorio Entrega** — alinhado com /intel-busca (top 20, 17 campos, analise documental)
7. **Pacotes de Monitoramento** — 3 tiers com UFs dinamicas do JSON
8. **Retorno do Investimento** — cenarios e analise de sensibilidade
9. **Quem Analisa Seus Editais** — autoridade generica via `autoridade_exemplos` do JSON
10. **Condicoes Comerciais** — preco, oferta limitada, forma de pagamento
11. **Proximos Passos** — CTA generico, plano de acao

---

## Suppressions (NUNCA incluir)

- Editais individuais com datas, objetos, orgaos ou links
- Historico de contratos ou faturamento governamental
- Calendario de editais em andamento
- "Mapa Competitivo", "Querido Diario", "Diarios Oficiais"
- Cargo publico especifico (ex: "engenheiro da SIE/SC")
- Experiencia setorial especifica (ex: "acompanhei obras", "execucoes de obras")
- Termos de construcao civil (ex: "pavimentacao", "infraestrutura", "obra") em textos genericos
- Qualquer hardcoding de UFs (ex: "SC+PR+RS")

---

## JSON Schema (referencia)

```json
{
  "empresa": { "razao_social": "...", "nome_fantasia": "...", "cnpj": "...", "cnae_principal": "...", "porte": "...", "capital_social": 0, "cidade_sede": "...", "uf_sede": "...", "qsa": [], "sancoes": {} },
  "setor": "Nome do Setor",
  "setor_intro": "Como consultor especializado em licitacoes publicas, acompanho o volume de contratacoes no setor de {setor}...",
  "uf_abrangencia": { "semanal": ["UF1", "UF2", "UF3"], "diario": ["UF1", "UF2", "UF3", "UF4", "UF5"] },
  "taxa_vitoria_setor": 0.20,
  "autoridade_exemplos": ["bullet 1", "bullet 2", "bullet 3", "bullet 4"],
  "editais": [],
  "resumo_executivo": { "texto": "...", "destaques": [] },
  "inteligencia_mercado": { "distribuicao_municipio": {}, "valor_total_mercado": 0, "modalidades": {} },
  "proximos_passos": []
}
```

---

## Params

$ARGUMENTS
