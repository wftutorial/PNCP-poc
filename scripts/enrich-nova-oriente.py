"""Enrich Nova Oriente report data with strategic analysis."""
import json

with open("docs/reports/data-05589462000100-2026-03-12.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Enrichment: Add strategic analysis per edital
analyses = {
    "MUNICIPIO DE VALENCA|49": {
        "recomendacao": "AVALIAR COM CAUTELA",
        "justificativa": "Edital fecha em 2 dias (16/03) - prazo insuficiente para preparacao. Objeto (servicos de engenharia e paisagismo) tem aderencia ao CNAE 4313400. Valor R$13.9M compativel com capital social R$22.5M. Concorrencia Presencial exige entrega fisica.",
        "aderencia": "Alta",
        "analise_detalhada": "SRP para servicos comuns de engenharia (paisagismo, jardinagem, recuperacao de passeios, manutencao urbana). Aderencia alta ao perfil. RISCO: prazo de apenas 2 dias."
    },
    "MUNICIPIO DE SAPUCAIA|1": {
        "recomendacao": "AVALIAR COM CAUTELA",
        "justificativa": "Prazo de 4 dias e muito curto. Objeto (construcao de portais) tem aderencia media. Valor R$764K acessivel. Distancia 164km (2.4h) viavel.",
        "aderencia": "Media",
        "analise_detalhada": "Construcao de 2 portais decorativos/turisticos em Sapucaia/RJ. Concorrencia Eletronica via Licitanet. CNAE 4120400 (edificacoes) como secundario aplicavel."
    },
    "MINISTERIO DA SAUDE|257": {
        "recomendacao": "NAO RECOMENDADO",
        "justificativa": "Objeto (locacao de equipamentos de PCR-RT para o INCA) e completamente incompativel com perfil de construcao civil. CNAE 4313400 nao tem qualquer relacao com equipamentos laboratoriais.",
        "aderencia": "Nenhuma",
        "analise_detalhada": "Equipamentos automatizados de extracao e amplificacao de acidos nucleicos (PCR-RT). Zero aderencia."
    },
    "MUNICIPIO DE RIO DE JANEIRO|205": {
        "recomendacao": "PARTICIPAR",
        "justificativa": "Obra de reconstrucao de quiosque na Ilha do Governador (RJ) - aderencia direta ao CNAE 4120400 (edificacoes). Valor R$212K acessivel. Localizacao na sede (0km). 10 dias de prazo. Boa oportunidade de entrada em contratos municipais do RJ.",
        "aderencia": "Alta",
        "analise_detalhada": "Reconstrucao do Quiosque 7 na Praia da Engenhoca, Ilha do Governador. Obra civil de pequeno porte. CNAE 4120400 presente como secundario. Capital social R$22.5M muito superior ao necessario. ROI Potencial: R$12.6K - R$23.5K."
    },
    "MINISTERIO DA SAUDE|258": {
        "recomendacao": "NAO RECOMENDADO",
        "justificativa": "Objeto (locacao de analisadores automatizados para analise de sedimento urinario) incompativel com perfil de construcao civil.",
        "aderencia": "Nenhuma",
        "analise_detalhada": "Locacao de analisadores automatizados para INCA. Equipamento medico-laboratorial. Zero aderencia."
    },
    "MUNICIPIO DE PORCIUNCULA|3": {
        "recomendacao": "AVALIAR COM CAUTELA",
        "justificativa": "Objeto (construcao de unidades habitacionais MCMV) tem aderencia alta. Valor R$9.26M compativel. RISCO PRINCIPAL: distancia de 366km (5.7h). Programa federal (Novo PAC) garante fonte de recurso.",
        "aderencia": "Alta",
        "analise_detalhada": "Construcao de unidades habitacionais MCMV - Novo PAC. CNAE 4120400 aplicavel. RISCOS: distancia 366km, margens apertadas do programa MCMV. ROI Potencial: R$459K - R$861K."
    },
    "ESTADO DO RIO DE JANEIRO|554": {
        "recomendacao": "PARTICIPAR",
        "justificativa": "Pavimentacao e drenagem em Campos dos Goytacazes - aderencia direta ao CNAE 4313400. Valor R$11.7M compativel. Criterio: maior desconto. 12 dias de prazo. ATENCAO: local real e Campos (~280km do RJ, nao 0km como calculado).",
        "aderencia": "Alta",
        "analise_detalhada": "Elaboracao de projeto executivo e execucao de obras de pavimentacao e drenagem em Tapera III, Campos dos Goytacazes. Concorrencia Eletronica via SIGA. Criterio: maior desconto linear. ROI Potencial: R$694K - R$1.3M."
    },
    "MUNICIPIO DE RIO DAS OSTRAS|9": {
        "recomendacao": "AVALIAR COM CAUTELA",
        "justificativa": "Fornecimento e instalacao de pisos elevados - nicho especializado. CNAE 4299599 cobre. Valor R$804K acessivel. Distancia 169km viavel. RISCO: exige especializacao em pisos elevados.",
        "aderencia": "Media",
        "analise_detalhada": "Pisos elevados com pedestais e longarinas. Nicho tecnico. Pregao Eletronico, menor preco. ROI Potencial: R$43.8K - R$82K."
    },
    "MUNICIPIO DE VALENCA|45": {
        "recomendacao": "PARTICIPAR",
        "justificativa": "SRP para servicos de engenharia (paisagismo, recuperacao de passeios). Aderencia alta. Valor sigiloso. 16 dias de prazo. Concorrencia Presencial.",
        "aderencia": "Alta",
        "analise_detalhada": "ARP para servicos de engenharia em Valenca/RJ. CNAE 4313400 e 4291000 cobrem o objeto. SRP permite entregas sob demanda."
    },
    "MUNICIPIO DE VALENCA|47": {
        "recomendacao": "PARTICIPAR",
        "justificativa": "Mesmo objeto do edital 45, com valor estimado R$13.9M. SRP para servicos de engenharia e urbanizacao. Aderencia alta. 16 dias de prazo. Concorrencia Presencial.",
        "aderencia": "Alta",
        "analise_detalhada": "ARP para servicos comuns de engenharia para Secretaria de Obras de Valenca/RJ. Inclui paisagismo, jardinagem, recuperacao de passeios, manutencao de mobiliario urbano. ROI Potencial: R$758K - R$1.4M."
    },
    "MUNICIPIO DE ANGRA DOS REIS|51": {
        "recomendacao": "PARTICIPAR",
        "justificativa": "Drenagem, esgoto e recapeamento asfaltico em Angra dos Reis - aderencia diretissima ao CNAE 4313400. Valor R$16.2M compativel. Concorrencia Presencial, menor preco global. 24 dias. Distancia 140km viavel. Atestados: Drenagem Pluvial + Pavimentacao CBUQ (50% parcelas). TOP PICK.",
        "aderencia": "Alta",
        "analise_detalhada": "Execucao de drenagem, rede de esgoto sanitario e recapeamento asfaltico em CBUQ no Conjunto Habitacional Morada do Bracui. Lei 14.133/2021. Empreitada por preco unitario. Atestados: Drenagem Pluvial + CBUQ (50%). Consorcio permitido. Vigencia 13 meses, execucao 10 meses. Garantia 60 meses. Orcamento: R$16.245.327,12. ROI Potencial: R$936K - R$1.75M."
    },
    "DNIT-DEPARTAMENTO NACIONAL DE INFRAEST DE TRANSPORTES|2": {
        "recomendacao": "NAO RECOMENDADO",
        "justificativa": "Engenharia consultiva (assessoramento, planejamento e gestao) - perfil de empresa de consultoria, nao de construtora. O CNAE 7112000 esta nos secundarios, mas core business e execucao de obras. Valor R$66.6M exigiria equipe de consultores seniores.",
        "aderencia": "Baixa",
        "analise_detalhada": "Servicos tecnicos de apoio e engenharia consultiva para o DNIT/RJ. Perfil incompativel - empresa e construtora, nao consultora."
    },
    "SOMAR|15": {
        "recomendacao": "AVALIAR COM CAUTELA",
        "justificativa": "Maior oportunidade (R$81.3M) - construcao de 8 porticos em Marica. Aderencia alta. POREM: (1) criterio Tecnica e Preco; (2) Semi-Integrada (projeto executivo + obra); (3) modo FECHADO; (4) valor pode exigir consorcio. Distancia 60km - excelente. 27 dias - viavel. Avaliar consorcio.",
        "aderencia": "Alta",
        "analise_detalhada": "Contratacao Semi-Integrada para 8 porticos em Marica. Concorrencia Eletronica 90005/2026, ComprasGov. T+P, Semi-Integrada, Fechado. Vigencia 24 meses, execucao 18 meses. R$81.282.880,49 (EMOP/SINAPI set/2025). Consorcio permitido. Marica tem recursos de royalties petroleo. ROI Potencial: R$4.68M - R$8.78M."
    },
    "COMANDO DA AERONAUTICA|3338": {
        "recomendacao": "AVALIAR COM CAUTELA",
        "justificativa": "Revitalizacao de paineis de media tensao na Casa de Forca do DTCEA-SC - engenharia eletrica especializada. CNAE 4313400 nao aderente. Local: Santa Catarina (nao RJ). Valor R$17.1M. RISCO: obra especializada em sistemas eletricos para instalacao militar.",
        "aderencia": "Baixa",
        "analise_detalhada": "Paineis de media tensao para instalacao militar (Forca Aerea). Engenharia eletrica industrial, nao construcao civil convencional. Local de execucao e SC, nao RJ."
    },
    "MUNICIPIO DE PETROPOLIS|34": {
        "recomendacao": "PARTICIPAR",
        "justificativa": "Drenagem e pavimentacao em Petropolis - aderencia diretissima ao CNAE 4313400. Valor R$778K acessivel. Distancia 87km (1.3h) viavel. 72 dias de prazo - muito confortavel. 9 documentos disponiveis (projeto, planilha, cronograma, matriz de risco). Excelente oportunidade.",
        "aderencia": "Alta",
        "analise_detalhada": "Sistema de drenagem e pavimentacao na Servidao Jose Ribeiro Guimaraes, Bingen, Petropolis/RJ. CNAE 4313400 diretamente aplicavel. 9 documentos no PNCP para orcamentacao. ROI Potencial: R$48K - R$90K."
    }
}

# Apply enrichments
for edital in data["editais"]:
    key = f"{edital['orgao']}|{edital['sequencial_compra']}"
    if key in analyses:
        a = analyses[key]
        edital["recomendacao"] = a["recomendacao"]
        edital["justificativa"] = a["justificativa"]
        edital["aderencia"] = a["aderencia"]
        edital["analise_detalhada"] = a["analise_detalhada"]
    else:
        if edital.get("dias_restantes", 0) < 0:
            edital["recomendacao"] = "NAO RECOMENDADO"
            edital["justificativa"] = f"Edital encerrado ha {abs(edital.get('dias_restantes', 0))} dias."
        else:
            edital["recomendacao"] = "NAO RECOMENDADO"
            edital["justificativa"] = "Dados insuficientes para analise."
        edital["aderencia"] = "N/A"
        edital["analise_detalhada"] = ""

# Add resumo executivo
abertos = [e for e in data["editais"] if e.get("dias_restantes", 0) > 0]
participar = [e for e in abertos if e.get("recomendacao") == "PARTICIPAR"]
avaliar = [e for e in abertos if e.get("recomendacao") == "AVALIAR COM CAUTELA"]
nao_rec = [e for e in abertos if "NAO" in e.get("recomendacao", "")]
valor_total = sum(e["valor_estimado"] for e in abertos if e["valor_estimado"] > 0)
valor_participar = sum(e["valor_estimado"] for e in participar if e["valor_estimado"] > 0)

data["resumo_executivo"] = {
    "total_editais": len(data["editais"]),
    "editais_abertos": len(abertos),
    "editais_encerrados": len(data["editais"]) - len(abertos),
    "participar": len(participar),
    "avaliar_cautela": len(avaliar),
    "nao_recomendado": len(nao_rec),
    "valor_total_abertos": valor_total,
    "valor_participar": valor_participar,
}

data["inteligencia_mercado"] = {
    "panorama": "O mercado de licitacoes de engenharia no Estado do Rio de Janeiro apresenta 15 oportunidades abertas, com valor total superior a R$235M. Predominam Concorrencias (Eletronicas e Presenciais), indicando obras de maior porte.",
    "tendencias": "Concentracao em obras de infraestrutura urbana (pavimentacao, drenagem, habitacao) impulsionada pelo Novo PAC.",
    "nichos": "Oportunidades em Valenca/RJ (3 editais do mesmo municipio) e obras de urbanizacao/paisagismo (SRP com demanda continua).",
    "vantagens_competitivas": "Nova Oriente tem sede no RJ (vantagem geografica), capital social robusto R$22.5M, CNAE diversificado (12 secundarios), 23 anos de mercado. ATENCAO: socio Oriente Construcao Civil LTDA esta em recuperacao judicial.",
    "ranking_prioridade": [
        "1. Angra dos Reis - Drenagem/Pavimentacao R$16.2M",
        "2. Estado RJ - Pavimentacao Campos R$11.7M",
        "3. Valenca - SRP Engenharia R$13.9M",
        "4. SOMAR Marica - Porticos R$81.3M",
        "5. Petropolis - Drenagem/Pavimentacao R$778K",
        "6. Rio de Janeiro - Quiosque R$212K"
    ]
}

data["proximos_passos"] = [
    {"prioridade": "URGENTE", "acao": "Decidir participacao nos editais de Valenca (16/03) e Sapucaia (18/03)", "prazo": "13-14/03/2026"},
    {"prioridade": "ALTA", "acao": "Preparar documentacao para Angra dos Reis (R$16.2M) - entrega presencial", "prazo": "04/04/2026"},
    {"prioridade": "ALTA", "acao": "Cadastrar no SIGA e preparar proposta para Estado RJ (R$11.7M)", "prazo": "24/03/2026"},
    {"prioridade": "MEDIA", "acao": "Avaliar consorcio para SOMAR Marica (R$81.3M) - criterio T+P", "prazo": "28/03/2026"},
    {"prioridade": "MEDIA", "acao": "Preparar proposta para Petropolis (R$778K) - prazo 72 dias", "prazo": "05/05/2026"},
    {"prioridade": "BAIXA", "acao": "Verificar situacao do socio em Recuperacao Judicial", "prazo": "20/03/2026"},
    {"prioridade": "BAIXA", "acao": "Regularizar SICAF (consulta falhou)", "prazo": "20/03/2026"}
]

with open("docs/reports/data-05589462000100-2026-03-12.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("JSON enriched successfully")
print(f"Abertos: {len(abertos)} | PARTICIPAR: {len(participar)} | AVALIAR: {len(avaliar)} | NAO REC: {len(nao_rec)}")
print(f"Valor total abertos: R${valor_total:,.2f}")
print(f"Valor PARTICIPAR: R${valor_participar:,.2f}")
