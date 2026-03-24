# /proposta-b2g — Gerador de Proposta Comercial B2G

## Purpose

Gera um PDF de proposta comercial personalizada e profissional para um lead especifico de QUALQUER setor. Cruza perfil da empresa + panorama de mercado + historico gov para construir uma proposta irrecusavel que mostra ao decisor exatamente quanto dinheiro ele esta deixando na mesa.

**Output primario:** \x60docs/propostas/proposta-{CNPJ}-{YYYY-MM-DD}.pdf\x60
**Output secundario:** \x60docs/propostas/proposta-{CNPJ}-{YYYY-MM-DD}.md\x60 (markdown)
**Rodape:** "Tiago Sasaki - Consultor de Licitacoes (48)9 8834-4559"

---

## Usage

\x60\x60\x60
/proposta-b2g 12.345.678/0001-90
/proposta-b2g 12345678000190 --pacote premium
/proposta-b2g 12345678000190 --pacote basico --desconto 10
/proposta-b2g 12345678000190 --from-qualify docs/intel-b2g/qualified-medicamentos-2026-03-10.xlsx
\x60\x60\x60

## Pacotes Disponiveis

| Pacote | Preco | Report freq | PDF analysis | UFs | Suporte |
|--------|-------|-------------|-------------|-----|---------|
| **Mensal** | R\x24997/mes | 1x/mes | Ate 3 editais | UF sede | Comercial |
| **Semanal (Rec.)** | R\x241.500/mes | 4x semanal + 1x mensal | Ate 8 editais | UF sede + limitrofes (de \x60uf_abrangencia.semanal\x60) | Estendido |
| **Diario** | R\x242.997/mes | Diario + semanal + mensal | Ilimitada | Cobertura ampla (de \x60uf_abrangencia.diario\x60) | Dedicado |

Todos os pacotes tem desconto anual: pague 10, leve 12.

Se \x60--pacote\x60 nao for informado, o command seleciona automaticamente baseado no tier/score do \x60/qualify-b2g\x60.

**Cobertura de UFs e dinamica:** O campo \x60uf_abrangencia\x60 no JSON de dados define quais UFs cada pacote cobre, calculado a partir da UF-sede da empresa. Nunca hardcodar UFs na proposta.

## Principios de Conversao

- **Autoridade**: Tiago Sasaki e consultor especializado em licitacoes publicas com experiencia comprovada. Analisa editais profissionalmente, identificando armadilhas que eliminam licitantes desavisados.
- **Escassez temporal**: Novos editais sao publicados toda semana. Cada semana sem monitoramento = oportunidades perdidas. O CTA usa urgencia generica, nunca datas de editais especificos.
- **Prova de valor**: A proposta em si E o produto. Mostra exatamente o que o relatorio /intel-busca entrega.
- **Reciprocidade**: Primeiro mes de cortesia para contratacoes na vigencia da proposta.
- **Contraste**: Tabela "COM vs SEM monitoramento" e "Consultoria Tradicional vs Esta Consultoria".
- **Dados reais, nao promessas**: Todo numero vem de fonte publica verificavel (PNCP, PCP v2, Portal da Transparencia, OpenCNPJ, IBGE).
