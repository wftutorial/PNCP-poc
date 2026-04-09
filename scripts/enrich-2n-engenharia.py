#!/usr/bin/env python3
"""Enrich JSON report data for 2N ENGENHARIA LTDA."""
import json

INPUT = "docs/reports/data-00346953000106-2026-03-15.json"

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

editais = data["editais"]

# Enrichment data per edital index
enrichments = {
    0: {
        "recomendacao": "DESCARTADO",
        "justificativa": "Prazo encerrado (0 dias restantes). Edital expirado.",
        "analise_detalhada": "O edital de Cacador/SC para coleta de residuos esta expirado com 0 dias restantes. Nao ha como preparar proposta para processo ja encerrado.",
        "analise_documental": None,
    },
    1: {
        "recomendacao": "NAO RECOMENDADO",
        "justificativa": "Prazo insuficiente (2 dias) para preparacao de proposta em concorrencia presencial. Distancia elevada de Sao Paulo (1.400+ km). Apesar de ser obra de construcao compativel com CNAE, prazo inviavel.",
        "analise_detalhada": "Obra de implantacao de UBS em Santa Ines/BA e tecnicamente compativel com o CNAE 4120400 da empresa. Porem, com apenas 2 dias de prazo e distancia de mais de 1.400 km da sede em Sao Paulo, a viabilidade logistica e operacional e extremamente baixa. A preparacao adequada de proposta para concorrencia presencial requer visita tecnica ao local, elaboracao de planilha orcamentaria detalhada e mobilizacao de equipe — impossivel em 48 horas.",
        "analise_documental": None,
    },
    2: {
        "recomendacao": "NAO RECOMENDADO",
        "justificativa": "Prazo insuficiente (2 dias). Servico de limpeza/conservacao, nao construcao civil. Empresa nao tem historico expressivo em servicos de limpeza de grande porte para justificar participacao neste valor.",
        "analise_detalhada": "O edital do CEAGESP/SP para servicos de limpeza e higienizacao tem valor expressivo (R$13,4M) e localizacao favoravel (Sao Paulo), mas apresenta dois problemas criticos: (1) prazo de apenas 2 dias impossibilita preparo adequado de proposta; (2) o objeto e servico de limpeza/asseio, que embora apareca nos clusters de atividade historica da empresa, nao corresponde ao core business de engenharia civil. A competicao neste segmento e acirrada com empresas especializadas.",
        "analise_documental": None,
    },
    3: {
        "recomendacao": "AVALIAR COM CAUTELA",
        "justificativa": "Obra de reforma de UBS compativel com CNAE 4120. Valor baixo (R$156K) vs capital da empresa (R$20M) — baixa expressividade financeira. Concorrencia presencial exige deslocamento. Municipio pequeno (6.090 hab, PIB R$211M). Oportunidade tecnica mas margem apertada.",
        "analise_detalhada": "A reforma da Unidade Basica de Saude de Campina do Monte Alegre/SP e tecnicamente compativel com o CNAE principal 4120400. O prazo de 8 dias e apertado mas manejavel para empresa experiente. A principal questao e a proporcionalidade: com capital social de R$20M e historico de 1002 contratos, uma obra de R$156K representa apenas 0,78% do capital — margem de lucro absoluta baixa para o esforco envolvido. Concorrencia Presencial exige deslocamento ate Campina do Monte Alegre (interior de SP). Recomenda-se avaliar capacidade operacional disponivel na regiao e custo de deslocamento antes de decidir.",
        "analise_documental": "Concorrencia Presencial 02/2026. Criterio: Menor preco. Protocolacao ate 24/03/2026 as 10h. Inclui projeto tecnico, memorial descritivo, cronograma e planilha orcamentaria. Lei 14.133/2021.",
    },
    4: {
        "recomendacao": "PARTICIPAR",
        "justificativa": "Construcao de 40 unidades habitacionais FNHIS — plenamente compativel com CNAE 4120 (construcao de edificios). Valor expressivo (R$5,4M) adequado ao porte da empresa. Financiamento federal (FNHIS/Caixa) garante pagamento. Permite consorcio. Prazo de 10 dias e viavel para empresa experiente. Empreitada global com menor preco.",
        "analise_detalhada": "Este e o edital de maior destaque do conjunto analisado. A construcao de 40 unidades habitacionais em Guararapes/SP via financiamento FNHIS (Fundo Nacional de Habitacao de Interesse Social) e perfeitamente alinhada ao CNAE 4120400 (Construcao de edificios). Valor de R$5,4M e proporcional ao porte da empresa (27% do capital social). O financiamento via Caixa Federal elimina risco de inadimplencia pelo orgao publico. A modalidade eletronica facilita participacao sem necessidade de deslocamento imediato. Cada unidade tem area de 53,87m2, e o prazo de execucao de 360 dias e adequado para empreitada de 40 casas. Permite formacao de consorcio caso seja necessario compartilhar riscos ou capacidade tecnica.",
        "analise_documental": "Concorrencia Eletronica 001/2026, Processo 010/2026. Criterio: Menor preco global, empreitada global. Abertura 26/03/2026 as 08:31, inicio da disputa as 09:00. Prazo de execucao: 360 dias. Vigencia do contrato: 730 dias. Area por unidade: 53,87m2. Plataforma: BLL (bolsa-licitacoes.com.br). Permite consorcio. Financiamento: FNHIS via Caixa Federal, Termo de Compromisso 041147/2025.",
    },
    5: {
        "recomendacao": "NAO RECOMENDADO",
        "justificativa": "Objeto e desenvolvimento de software ERP, completamente fora do escopo de engenharia civil. A empresa nao tem qualificacao tecnica em TI/software. Criterio tecnica+preco exige demonstracao de capacidade tecnica em sistemas. Apesar do alto valor, e incompativel com o perfil da empresa.",
        "analise_detalhada": "O edital do CISMETRO Holambra para contratacao de ERP (Enterprise Resource Planning) tem valor expressivo de R$25,2M quinquenal, mas o objeto e desenvolvimento e manutencao de sistema de software de gestao — radicalmente incompativel com o CNAE de construcao de edificios. A avaliacao por tecnica e preco exige comprovacao de experiencia e capacidade tecnica em TI que a 2N Engenharia nao possui. Participar seria temerario e resultaria em inabilitacao na fase de habilitacao tecnica.",
        "analise_documental": "Concorrencia Eletronica 01/2026. Objeto: contratacao de pessoa juridica para implantacao e manutencao de ERP do CISMETRO Holambra. Criterio: Tecnica e preco. Valor total estimado: R$25,2M (quinquenal). Sessao publica: 12/05/2026. Videoconferencia: Google Meet.",
    },
    6: {
        "recomendacao": "NAO RECOMENDADO",
        "justificativa": "Contratacao de organizacao social sem fins lucrativos para gestao de saude. 2N Engenharia e empresa de engenharia com fins lucrativos, nao atende ao requisito de ser organizacao social qualificada. Inexigibilidade por natureza singular.",
        "analise_detalhada": "A inexigibilidade de Paraibuna/SP busca contratar organizacao social sem fins lucrativos qualificada para gestao de unidades de saude. Alem da incompatibilidade de objeto com engenharia civil, ha uma barreira juridica intransponivel: a 2N Engenharia e uma Sociedade Empresaria Limitada com fins lucrativos, enquanto o edital exige especificamente entidade sem fins lucrativos com qualificacao como organizacao social na area da saude.",
        "analise_documental": None,
    },
    7: {
        "recomendacao": "NAO RECOMENDADO",
        "justificativa": "Credenciamento para prestacao de servicos especializados de saude. Exige qualificacao em area da saude que a empresa nao possui. Incompativel com CNAE de engenharia.",
        "analise_detalhada": "O credenciamento de Dona Emma/SC para servicos especializados de saude exige registro nos conselhos de classe da area da saude (CRM, COREN, CRF etc.) e comprovacao de capacidade tecnica em procedimentos medicos/hospitalares. A 2N Engenharia nao possui essas qualificacoes e nao pode se credenciar para este tipo de servico.",
        "analise_documental": None,
    },
    8: {
        "recomendacao": "NAO RECOMENDADO",
        "justificativa": "Locacao de imovel por inexigibilidade. Objeto incompativel — empresa de engenharia nao e locadora de imoveis. Valor irrisorio (R$14.400).",
        "analise_detalhada": "A inexigibilidade de Lindoia do Sul/SC para locacao de imovel tem dupla incompatibilidade: o objeto (locacao de imovel) nao tem relacao com engenharia civil ou distribuicao, e o valor anual de R$14.400 e irrisorio para empresa de grande porte. Inexigibilidades de locacao tipicamente exigem que o fornecedor seja o proprietario ou titular de direito real sobre o imovel especifico.",
        "analise_documental": None,
    },
    9: {
        "recomendacao": "NAO RECOMENDADO",
        "justificativa": "Aquisicao de generos alimenticios hortifrutigranjeiros via chamada publica (PPAIS). Exige produtor rural ou cooperativa. Incompativel com perfil de empresa de engenharia. Valor baixo (R$14K).",
        "analise_detalhada": "A Chamada Publica 003/2025-PPAIS de Riolandia/SP para aquisicao de hortifrutigranjeiros e uma modalidade especifica da Lei 11.947/2009 (PNAE/PAA) que reserva participacao a agricultores familiares, empreendedores familiares rurais e suas organizacoes/cooperativas. A 2N Engenharia nao se enquadra nesses requisitos legais.",
        "analise_documental": None,
    },
    10: {
        "recomendacao": "NAO RECOMENDADO",
        "justificativa": "Mesmo tipo que edital 9 — chamada publica PPAIS para hortifrutigranjeiros. Incompativel e valor irrisorio.",
        "analise_detalhada": "Identico ao Edital 9 — outra chamada publica PPAIS de Riolandia/SP para generos alimenticios hortifrutigranjeiros. Mesma incompatibilidade legal e de objeto. Valor de R$9.300 e ainda mais irrisorio.",
        "analise_documental": None,
    },
    11: {
        "recomendacao": "AVALIAR COM CAUTELA",
        "justificativa": "Servico de divisorias e reformas internas no Paco Municipal. Compativel com construcao civil mas valor muito baixo (R$20K) para empresa de grande porte. Margem minima. Dispensa de licitacao simplifica processo.",
        "analise_detalhada": "O servico de divisorias e reformas internas no Paco Municipal de Presidente Epitacio/SP e tecnicamente compativel com a atuacao de empresa de construcao civil. A dispensa de licitacao torna o processo agil e menos burocratico. No entanto, o valor de R$20.000 representa apenas 0,1% do capital social da empresa — o esforco administrativo pode nao compensar a margem de lucro obtida. Recomenda-se avaliar se ha capacidade instalada proxima ao municipio que torne o deslocamento economicamente viavel.",
        "analise_documental": None,
    },
    12: {
        "recomendacao": "DESCARTADO",
        "justificativa": "Valor irrisorio (R$113,20). Aquisicao de equipamento de salvamento, completamente fora do escopo da empresa.",
        "analise_detalhada": "Dispensa de licitacao para aquisicao de cordeletes de salvamento em altura em Jabora/SC. O valor de R$113,20 e absolutamente irrisorio e o objeto (equipamento de seguranca/salvamento) e completamente incompativel com engenharia civil ou distribuicao.",
        "analise_documental": None,
    },
    13: {
        "recomendacao": "DESCARTADO",
        "justificativa": "Valor irrisorio (R$1.800). Equipamento de salvamento, fora do escopo.",
        "analise_detalhada": "Dispensa de licitacao para aquisicao de mochila organizadora de equipamento de salvamento em Jabora/SC. O valor de R$1.800 e o objeto (equipamento de seguranca) sao incompativeis com o perfil da empresa.",
        "analise_documental": None,
    },
}

# Apply enrichments to each edital
for idx, enrichment in enrichments.items():
    edital = editais[idx]
    edital["recomendacao"] = enrichment["recomendacao"]
    edital["justificativa"] = enrichment["justificativa"]
    edital["analise_detalhada"] = enrichment["analise_detalhada"]
    if enrichment.get("analise_documental"):
        edital["analise_documental"] = enrichment["analise_documental"]

# Separate descartados from main list
descartados = [e for e in editais if e.get("recomendacao") == "DESCARTADO"]
editais_ativos = [e for e in editais if e.get("recomendacao") != "DESCARTADO"]

data["editais"] = editais_ativos
data["editais_descartados"] = descartados

# Add market intelligence
data["inteligencia_mercado"] = {
    "panorama": "Mercado B2G diversificado com predominancia de editais de saude e materiais hospitalares nas UFs de atuacao (SC, BA, SP). Para o segmento especifico de construcao civil (CNAE da empresa), o volume e menor mas os valores unitarios sao significativamente maiores.",
    "tendencias": "Crescimento de licitacoes de construcao habitacional via FNHIS. Concorrencias eletronicas tornando-se padrao sob Lei 14.133/2021. Pregoes presenciais em declinio.",
    "vantagens_competitivas": "Capital social elevado (R$20M) permite participar de licitacoes de grande porte. Historico extenso (1002 contratos) demonstra maturidade. Atuacao em 15 UFs oferece flexibilidade geografica.",
    "oportunidades_nicho": "Construcao habitacional de interesse social (FNHIS/PAC). Reformas de unidades de saude (UBS). Obras publicas municipais de medio porte (R$100K-R$10M).",
    "recomendacao_geral": "Focar busca em editais de construcao civil, reformas e obras publicas — os segmentos que correspondem ao CNAE e onde a empresa tem maior vantagem competitiva. A diversificacao em materiais hospitalares e saneantes pode ser explorada em separado mas requer estrategia especifica."
}

# Add proximos passos
data["proximos_passos"] = [
    {
        "prioridade": 1,
        "acao": "Preparar proposta para Concorrencia Eletronica 001/2026 de Guararapes (construcao 40 casas FNHIS). Prazo: ate 26/03/2026. Cadastrar na plataforma BLL.",
        "prazo": "26/03/2026",
        "edital_idx": 4,
    },
    {
        "prioridade": 2,
        "acao": "Avaliar viabilidade de participacao na Concorrencia Presencial 02/2026 de Campina do Monte Alegre (reforma UBS R$156K). Prazo: ate 24/03/2026.",
        "prazo": "24/03/2026",
        "edital_idx": 3,
    },
    {
        "prioridade": 3,
        "acao": "Recalibrar busca de oportunidades focando em editais de construcao civil, reformas e obras publicas (modalidades Concorrencia e Pregao). A busca atual trouxe muitos editais de saude/TI/alimentos por causa dos clusters de atividade historica.",
        "prazo": "Continuo",
        "edital_idx": None,
    },
    {
        "prioridade": 4,
        "acao": "Regularizar cadastro SICAF (consulta nao realizada por indisponibilidade tecnica). Verificar se todos os documentos estao atualizados.",
        "prazo": "31/03/2026",
        "edital_idx": None,
    },
    {
        "prioridade": 5,
        "acao": "Avaliar estrategia de participacao em consorcio para obras de grande porte (>R$10M) que exijam qualificacao tecnica alem da capacidade individual.",
        "prazo": "Continuo",
        "edital_idx": None,
    },
]

# Add resumo executivo
data["resumo_executivo"] = {
    "total_editais": 14,
    "editais_participar": 1,
    "editais_avaliar": 2,
    "editais_nao_recomendado": 8,
    "editais_descartados": 3,
    "valor_total_participar": 5388199.94,
    "valor_total_avaliar": 176530.43,
    "roi_agregado": "Resultado potencial estimado de R$161.646 a R$538.820 no cenario base (margem 3-10% sobre R$5,4M da obra de Guararapes)",
    "destaques": [
        "Melhor oportunidade: Construcao de 40 casas populares em Guararapes/SP (R$5,4M, FNHIS) — plenamente compativel com CNAE 4120",
        "ALERTA: Divergencia setorial identificada — CNAE e Engenharia mas 70% dos contratos historicos sao em materiais hospitalares, saneantes e alimentacao",
        "Apenas 1 edital de construcao civil encontrado entre 14 — busca futura deve focar em modalidades Concorrencia e Pregao para obras/engenharia",
    ],
}

# Save enriched JSON
with open(INPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Done! Summary:")
print(f"  editais (active): {len(data['editais'])}")
print(f"  editais_descartados: {len(data['editais_descartados'])}")
print("  inteligencia_mercado: added")
print(f"  proximos_passos: {len(data['proximos_passos'])} items")
print("  resumo_executivo: added")
print()
print("Active editais recommendations:")
for i, e in enumerate(data["editais"]):
    print(f"  [{i}] {e.get('municipio')}/{e.get('uf')} — {e.get('recomendacao')}")
print()
print("Descartados:")
for e in data["editais_descartados"]:
    jus = e.get("justificativa", "")[:60]
    print(f"  {e.get('municipio')}/{e.get('uf')} — {jus}")
