"""Enrich Construsol report JSON with document analysis."""
import json

INPUT = "docs/reports/data-39336452000184-2026-03-13.json"

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

# Remove edital UFC cantina - DESCARTADO (not engineering)
data["editais"] = [e for e in data["editais"] if "cantina" not in e["objeto"].lower()]

# Add metadata about discarded editais
data["_metadata"]["editais_descartados"] = [
    {
        "objeto": "Concessao de uso oneroso de espaco fisico para exploracao comercial de uma cantina (UFC)",
        "orgao": "UNIVERSIDADE FEDERAL DO CEARA",
        "valor": 580.25,
        "motivo": "Objeto incompativel com CNAEs da empresa - concessao comercial de cantina, nao servico de engenharia/obra",
    }
]

# Enrich Solonopole edital
edital = data["editais"][0]

edital["analise_documental"] = {
    "ficha_tecnica": {
        "numero": "Concorrencia no 2026.02.11.001",
        "processo": "00007.20260130/0001-00",
        "modalidade": "Concorrencia Eletronica",
        "criterio_julgamento": "Menor Preco por Lote",
        "modo_disputa": "Aberto e Fechado",
        "data_sessao": "2026-03-30 08:00",
        "plataforma": "compras.m2atecnologia.com.br",
        "prazo_vigencia": "12 meses, prorrogavel ate 10 anos",
        "prazo_execucao": "Continuo - 12 meses",
        "valor_estimado": "R$ 332.580,60",
        "dotacao_orcamentaria": [
            "Secretaria de Infraestrutura: R$ 114.787,08 (33903900)",
            "Secretaria de Educacao: R$ 108.896,76 (33903900)",
            "Secretaria de Saude: R$ 108.896,76 (33903900)",
        ],
        "garantia_proposta": "R$ 3.325,80 (1% do valor estimado)",
        "garantia_contratual": "Nao exigida",
        "local_execucao": "Obras publicas do Municipio de Solonopole/CE e dependencias da Secretaria de Infraestrutura",
    },
    "habilitacao_checklist": {
        "juridica": "Contrato social ou ato constitutivo registrado na Junta Comercial",
        "fiscal_federal": "Certidao conjunta RFB/PGFN (tributos + divida ativa + seguridade)",
        "fiscal_estadual": "CND Estadual (domicilio/sede)",
        "fiscal_municipal": "CND Municipal (domicilio/sede)",
        "fgts": "CRF - Certificado de Regularidade do FGTS",
        "trabalhista": "CNDT - Certidao Negativa de Debitos Trabalhistas",
        "falencia": "Certidao negativa de falencia (ate 60 dias antes da sessao)",
        "economico_financeira": "Balanco Patrimonial + DRE dos 2 ultimos exercicios. Indices minimos: LG >= 1,00, LC >= 1,00, SG >= 1,00",
        "qualificacao_tecnica": [
            "Registro/inscricao no CREA e/ou CAU",
            "2 profissionais: 1 engenheiro civil/arquiteto como RT coordenador + 1 engenheiro civil/arquiteto como apoio tecnico",
            "CAT(s) do RT comprovando fiscalizacao em: (a) Urbanizacao de vias, (b) Barragem de terra, (c) Pavimentacao asfaltica, (d) Construcao de estradas vicinais, (e) Pavimentacao em piso intertravado de concreto, (f) Edificacoes, (g) Sistemas de abastecimento de agua",
            "Experiencia com sistemas federais: SIMEC, SISMOB, SICONV, TRANSFEREGOV (CAT + declaracao do contratante)",
            "Comprovacao de vinculo dos profissionais (CTPS, contrato social ou contrato de prestacao de servicos)",
        ],
    },
    "condicoes_comerciais": {
        "subcontratacao": "NAO admitida",
        "consorcio": "NAO admitido",
        "me_epp": "Tratamento favorecido conforme LC 123/2006",
        "prazo_pagamento": "Conforme contrato (mensal)",
        "reajuste": "Conforme minuta do contrato",
    },
    "red_flags": [
        "Exigencia tecnica MUITO RESTRITIVA: CATs cobrindo 7 areas especificas (urbanizacao, barragem, pavimentacao asfaltica, estradas vicinais, piso intertravado, edificacoes, sistemas de abastecimento) - reduz significativamente o universo de concorrentes",
        "Exigencia de experiencia com 4 sistemas federais (SIMEC, SISMOB, SICONV, TRANSFEREGOV) e altamente especializada",
        "Garantia de proposta obrigatoria (R$ 3.325,80) como requisito de pre-habilitacao - desclassificacao automatica sem ela",
        "Empresa fundada em 2020 (5 anos) - verificar se possui os 2 exercicios contabeis exigidos para habilitacao economico-financeira",
    ],
    "resumo_executivo": (
        "Licitacao para contratacao de empresa especializada em assessoria e consultoria de engenharia "
        "para fiscalizacao de obras publicas do Municipio de Solonopole/CE. O contrato atende 3 secretarias "
        "(Infraestrutura, Educacao e Saude) com valor mensal entre R$ 9.074,73 e R$ 9.565,59 por secretaria, "
        "totalizando R$ 332.580,60 em 12 meses. A principal barreira de entrada sao os requisitos de "
        "qualificacao tecnica: exige-se RT com CATs em 7 areas distintas de engenharia e experiencia "
        "comprovada com sistemas federais de monitoramento. A empresa Construsol tem CNAE compativel "
        "(4120-4 - Construcao de edificios) e capital social amplamente suficiente (R$ 2,8M vs R$ 332,5K). "
        "Contudo, o objeto e de CONSULTORIA/FISCALIZACAO, nao de execucao de obras, o que representa "
        "um perfil diferente do core business da empresa."
    ),
    "_source": {
        "status": "ANALYSIS",
        "timestamp": "2026-03-14",
        "detail": "Analise documental do edital + termo de referencia via Claude (PDF PNCP)",
    },
}

edital["recomendacao"] = "AVALIAR COM CAUTELA"
edital["justificativa"] = (
    "A Construsol e uma construtora (CNAE 4120-4 - construcao de edificios), e este edital e de "
    "CONSULTORIA E FISCALIZACAO de obras, nao de execucao. Embora haja compatibilidade setorial "
    "(engenharia), o perfil operacional e diferente. Os requisitos de habilitacao tecnica sao muito "
    "exigentes: o RT precisa ter CATs em 7 areas especificas (urbanizacao, barragem, pavimentacao "
    "asfaltica, estradas vicinais, piso intertravado, edificacoes, abastecimento de agua) E experiencia "
    "com sistemas federais (SIMEC, SISMOB, SICONV, TRANSFEREGOV). Verificar se a empresa possui "
    "profissionais com esse acervo tecnico antes de investir na proposta. Se possuir os atestados, "
    "o capital social (R$ 2,8M) e a ausencia de sancoes sao pontos positivos. Valor mensal atrativo "
    "(~R$ 27.715/mes para 3 secretarias)."
)

edital["analise_detalhada"] = {
    "aderencia": {
        "nivel": "MEDIA",
        "texto": (
            "CNAE principal 4120-4 (Construcao de edificios) e do setor de engenharia, porem o objeto "
            "e de consultoria/fiscalizacao de obras, nao de execucao direta. CNAEs secundarios incluem "
            "4211101 (Construcao de rodovias e ferrovias), 4221901 (Construcao de barragens e represas) "
            "e 4221903 (Manutencao de redes de abastecimento de agua), que sao compativeis com as "
            "areas exigidas nos atestados."
        ),
    },
    "valor": {
        "texto": (
            "Valor total R$ 332.580,60 e baixo para o porte da empresa (capital social R$ 2,8M - "
            "proporcao 8,4x). Mensalidade de ~R$ 27.715 e receita recorrente e previsivel. "
            "Sem exigencia de garantia contratual, o que reduz o comprometimento financeiro."
        ),
    },
    "geografia": {
        "texto": (
            "Distancia de 359,4 km (6h12 de viagem) de Sobral a Solonopole. Fiscalizacao presencial "
            "exige visitas periodicas as obras, o que implica custos de deslocamento significativos. "
            "Considerar se o valor mensal cobre as despesas de transporte, hospedagem e diarias."
        ),
    },
    "prazo": {
        "texto": (
            "15 dias ate o encerramento (30/03/2026). Prazo apertado para preparar a garantia de "
            "proposta (R$ 3.325,80) e verificar se os profissionais possuem os atestados exigidos. "
            "Decisao go/no-go deve ser tomada ate 20/03/2026."
        ),
    },
    "modalidade": {
        "texto": (
            "Concorrencia Eletronica com criterio de Menor Preco. Modo de disputa aberto e fechado. "
            "Competicao baseada exclusivamente em preco, o que favorece empresas com estrutura enxuta "
            "e menores custos operacionais."
        ),
    },
    "habilitacao": {
        "texto": (
            "PONTO CRITICO. O edital exige qualificacao tecnica altamente especializada: "
            "(1) 2 engenheiros civis/arquitetos dedicados ao contrato, "
            "(2) RT com CATs em 7 areas de fiscalizacao (urbanizacao, barragem, pavimentacao asfaltica, "
            "estradas vicinais, piso intertravado, edificacoes, abastecimento de agua), "
            "(3) experiencia com 4 sistemas federais (SIMEC, SISMOB, SICONV, TRANSFEREGOV). "
            "A empresa precisa verificar IMEDIATAMENTE se seus profissionais possuem esse acervo tecnico."
        ),
    },
}

edital["inteligencia_mercado"] = {
    "panorama": (
        "O segmento de consultoria e fiscalizacao de obras publicas no Ceara apresenta demanda constante, "
        "dado o volume de obras municipais financiadas por convenios e transferencias federais. "
        "As exigencias de experiencia com sistemas como SIMEC e SISMOB indicam que o municipio possui "
        "obras com recursos federais."
    ),
    "competitividade": (
        "As exigencias tecnicas restritivas (7 areas + 4 sistemas federais) limitam significativamente "
        "o universo de concorrentes. Poucas empresas no interior do Ceara possuem profissionais com "
        "esse acervo tecnico abrangente, o que pode resultar em menor concorrencia."
    ),
    "oportunidade": (
        "Se a Construsol possui ou pode contratar profissionais com os atestados exigidos, este edital "
        "representa uma oportunidade de receita recorrente (contrato de 12 meses prorrogavel) com valor "
        "previsivel e sem exigencia de garantia contratual."
    ),
}

# Overall executive summary
data["resumo_executivo"] = {
    "total_editais_encontrados": 27,
    "editais_descartados_encerrados": 25,
    "editais_descartados_incompativeis": 1,
    "editais_analisados": 1,
    "valor_total_oportunidades": 332580.60,
    "recomendacoes": {
        "PARTICIPAR": 0,
        "AVALIAR COM CAUTELA": 1,
        "NAO RECOMENDADO": 0,
    },
    "destaque": (
        "De 1.853 editais PNCP nos ultimos 30 dias no CE, 27 passaram no filtro setorial (engenharia), "
        "25 estavam encerrados e 1 foi descartado por incompatibilidade (cantina UFC). Restou 1 "
        "oportunidade relevante: assessoria em fiscalizacao de obras em Solonopole (R$ 332,5K/12 meses). "
        "A recomendacao e AVALIAR COM CAUTELA, condicionada a verificacao de acervo tecnico dos "
        "profissionais da empresa."
    ),
}

data["proximos_passos"] = [
    {
        "acao": "Verificar acervo tecnico dos engenheiros da empresa",
        "prioridade": "URGENTE",
        "prazo": "2026-03-18",
        "detalhes": (
            "Consultar CREA/CAU para confirmar se o RT possui CATs em: urbanizacao de vias, "
            "barragem de terra, pavimentacao asfaltica, estradas vicinais, piso intertravado, "
            "edificacoes e abastecimento de agua. Tambem verificar experiencia com SIMEC, SISMOB, "
            "SICONV e TRANSFEREGOV."
        ),
    },
    {
        "acao": "Providenciar garantia de proposta",
        "prioridade": "ALTA",
        "prazo": "2026-03-25",
        "detalhes": (
            "R$ 3.325,80 em caucao, seguro-garantia, fianca bancaria ou titulo de capitalizacao. "
            "Conta para deposito: Banco do Brasil, Ag 1150-9, CC 6455-6."
        ),
    },
    {
        "acao": "Calcular custo operacional de fiscalizacao em Solonopole",
        "prioridade": "ALTA",
        "prazo": "2026-03-20",
        "detalhes": (
            "Estimar custos mensais de deslocamento (359 km), hospedagem, diarias e manutencao "
            "de 2 engenheiros. Verificar se a mensalidade (~R$ 27.715) cobre os custos com margem adequada."
        ),
    },
    {
        "acao": "Regularizar documentacao fiscal",
        "prioridade": "MEDIA",
        "prazo": "2026-03-25",
        "detalhes": (
            "Emitir/verificar: CND Federal/Previdenciaria, CND Estadual CE, CND Municipal Sobral, "
            "CRF (FGTS), CNDT (trabalhista), Certidao de falencia."
        ),
    },
    {
        "acao": "Preparar balanco patrimonial e demonstracoes contabeis",
        "prioridade": "MEDIA",
        "prazo": "2026-03-25",
        "detalhes": (
            "Garantir que o balanco dos 2 ultimos exercicios (2024 e 2025) esta disponivel e que "
            "os indices LG, LC e SG sao >= 1,00. Empresa fundada em 2020 - deve ter exercicios suficientes."
        ),
    },
]

with open(INPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"JSON enriched: {len(data['editais'])} editais, {len(data['_metadata']['editais_descartados'])} descartados")
