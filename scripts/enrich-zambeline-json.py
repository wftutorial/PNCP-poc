#!/usr/bin/env python3
"""Enrich Zambeline JSON with analysis fields for PDF generation."""

import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

INPUT = "docs/reports/data-09352456000195-2026-03-12.json"

data = json.load(open(INPUT, encoding="utf-8"))
editais = data["editais"]

# ============================================================
# Edital 0: Vila Pavao - Creche FNDE Tipo 1
# ============================================================
editais[0]["recomendacao"] = "AVALIAR COM CAUTELA"
editais[0]["justificativa"] = (
    "Valor compatível com porte da empresa e requisitos financeiros atendidos "
    "(PL mínimo R$ 585k < capital R$ 1,4M). Porém, prazo de apenas 4 dias torna "
    "participação extremamente difícil. Recomendado apenas se empresa já possui "
    "proposta FNDE Tipo 1 pré-elaborada e atestados de cobertura metálica."
)
editais[0]["analise"] = {
    "aderencia": "Alta — objeto 100% compatível com CNAEs 4120-4/00 (Construção de edifícios) e 7112-0/00 (Serviços de engenharia)",
    "valor": "Compatível — R$ 5,9M dentro da faixa operacional (capital R$ 1,4M, PL mínimo exigido R$ 585k)",
    "geografica": "Distante — 255,8 km / 4,1 horas de Vitória. Custos logísticos significativos.",
    "prazo": "CRÍTICO — Apenas 4 dias restantes. Insuficiente para preparação completa.",
    "modalidade": "Concorrência Eletrônica — Menor Preço Global. Empreitada por Preço Unitário.",
    "habilitacao": "Atestados específicos: telha termoisolante (1.441kg) e estrutura treliçada (16.957kg). Equipe tripla (Civil + Segurança + Elétrica). PL >= R$ 585k atendido.",
    "riscos": "Prazo extremamente apertado (4 dias). Atestados específicos de cobertura metálica FNDE podem não estar disponíveis.",
}
editais[0]["perguntas_decisor"] = {
    "Vale a pena participar?": "Somente se já possui proposta FNDE Tipo 1 pré-elaborada e atestados de cobertura metálica termoisolante. Com 4 dias, não há tempo para preparar do zero.",
    "Quanto eu deveria ofertar?": "Valor estimado R$ 5.847.166,85 (SINAPI Jan/2025). Proposta < 75% (R$ 4,4M) é presuntivamente inexequível. Proposta < 85% (R$ 5,0M) exige garantia adicional.",
    "Quais documentos preciso preparar?": "CNDs (federal, estadual, municipal, FGTS, CNDT), certidão de falência, balanço patrimonial, atestados técnicos (cobertura metálica), CAT, CREA/CAU, equipe técnica tripla.",
    "Qual o risco de não conseguir executar?": "Médio — obra padronizada (FNDE Tipo 1) mas distante (256 km). Logística e supervisão demandam estrutura.",
    "Existe restrição que me impeça?": "Possível — verificar se possui atestados de telha termoisolante PIR e estrutura treliçada. Sem estes, está inabilitado.",
}

# ============================================================
# Edital 1: Colatina - Infraestrutura ES-080
# ============================================================
editais[1]["recomendacao"] = "AVALIAR COM CAUTELA"
editais[1]["justificativa"] = (
    "Oportunidade de alto valor (R$ 19,8M) com prazo adequado (33 dias) e consórcio "
    "permitido. Porém, PL mínimo de R$ 1,99M possivelmente excede capacidade individual "
    "(capital R$ 1,4M). Semi-integrada + Técnica e Preço (60/40) exigem forte proposta "
    "técnica. Recomendação: formar consórcio."
)
editais[1]["analise"] = {
    "aderencia": "Alta — infraestrutura urbana (drenagem, pavimentação, calçadas, obras de arte) compatível com CNAEs 4211-1/01, 4221-9/01, 4212-0/00",
    "valor": "Acima da capacidade individual — R$ 19,8M, PL mínimo R$ 1,99M > capital R$ 1,4M. Viável via consórcio.",
    "geografica": "140,7 km / 2,3 horas de Vitória. Distância gerenciável.",
    "prazo": "Adequado — 33 dias restantes. Tempo para preparar proposta técnica e formar consórcio.",
    "modalidade": "Concorrência Eletrônica — Técnica e Preço (60/40). Semi-Integrada (projeto executivo + execução). Modo Fechado.",
    "habilitacao": "5 CATs exigidos (drenagem, via especial, calçada, CBUQ, armação CA-50). Quantitativos expressivos: 60.000m² via, 2.246t CBUQ. Garantia de proposta R$ 199k.",
    "riscos": "PL insuficiente isoladamente. Quantitativos de atestados elevados. Semi-integrada requer capacidade de projeto executivo. Garantia de proposta de R$ 199k.",
}
editais[1]["perguntas_decisor"] = {
    "Vale a pena participar?": "Sim, via consórcio. Valor expressivo (R$ 19,8M) com critério técnica e preço que favorece qualidade sobre preço.",
    "Quanto eu deveria ofertar?": "Valor estimado R$ 19.867.468,52. Critério técnica (60%) + preço (40%). Foco na proposta técnica — nota mínima 50 pontos.",
    "Quem são os concorrentes prováveis?": "Construtoras de médio/grande porte do ES com experiência em infraestrutura urbana e obras de arte. Semi-integrada reduz campo.",
    "Quais documentos preciso preparar?": "Proposta técnica detalhada, 5 CATs, balanço PL >= R$ 1,99M (ou consórcio), garantia R$ 199k, 10+ declarações (anexos).",
    "Qual o risco de não conseguir executar?": "Alto se isolado — obra complexa semi-integrada. Baixo se em consórcio com empresa complementar.",
    "Existe restrição que me impeça?": "PL mínimo R$ 1,99M — se balanço < R$ 1,99M E índices < 1,0, inabilitado isoladamente. Consórcio resolve.",
}

# ============================================================
# Editais 2-9: Dispensas (abertas mas já contratadas ou fora do escopo)
# ============================================================
dispensa_labels = {
    2: ("NÃO RECOMENDADO", "Dispensa já contratada — Plena Engenharia LTDA (23.472.560/0001-44) por R$ 84.241,49."),
    3: ("NÃO RECOMENDADO", "Fora do escopo — telefonia móvel corporativa. Não compatível com CNAEs de engenharia."),
    4: ("NÃO RECOMENDADO", "Dispensa já contratada — Construtora Luarte LTDA (08.827.579/0001-72) por R$ 85.800,00."),
    5: ("NÃO RECOMENDADO", "Fora do escopo — certificados digitais. Não compatível com CNAEs de engenharia."),
    6: ("NÃO RECOMENDADO", "Dispensa já contratada — Construtora Padrão LTDA (16.456.069/0001-64) por R$ 44.968,82."),
    7: ("NÃO RECOMENDADO", "Fora do escopo — sacos de lixo plástico. Não compatível com CNAEs de engenharia."),
    8: ("NÃO RECOMENDADO", "Dispensa já contratada — Construtora Padrão LTDA (16.456.069/0001-64) por R$ 22.347,09."),
    9: ("NÃO RECOMENDADO", "Fora do escopo — link de internet. Não compatível com CNAEs de engenharia."),
}
for idx, (rec, just) in dispensa_labels.items():
    editais[idx]["recomendacao"] = rec
    editais[idx]["justificativa"] = just

# ============================================================
# Editais 10-21: Encerrados (referência de mercado)
# ============================================================
for idx in range(10, 22):
    editais[idx]["recomendacao"] = "ENCERRADO"
    editais[idx]["justificativa"] = "Edital encerrado — incluído como referência de mercado."

# ============================================================
# Top-level: resumo_executivo
# ============================================================
data["resumo_executivo"] = {
    "texto": (
        "Foram identificadas 22 oportunidades no Espírito Santo nos últimos 30 dias, "
        "das quais 2 estão abertas e são relevantes para o perfil de engenharia da "
        "Zambeline, totalizando R$ 25,8 milhões. A oportunidade principal é Colatina "
        "(R$ 19,8M, infraestrutura urbana, 33 dias), que aceita consórcio — importante "
        "dado que o patrimônio líquido exigido pode superar a capacidade individual. "
        "Vila Pavão (R$ 5,9M, creche FNDE) tem prazo crítico de 4 dias. Das 20 demais, "
        "4 são dispensas já contratadas, 4 são de outros setores, e 12 estão encerradas "
        "mas indicam demanda consistente no mercado capixaba."
    ),
    "destaques": [
        "Colatina — R$ 19,8M em infraestrutura urbana ES-080 (Técnica e Preço, consórcio permitido, 33 dias)",
        "Vila Pavão — R$ 5,9M em creche FNDE Tipo 1 (menor preço, 4 dias restantes — prazo crítico)",
        "12 editais de engenharia encerrados nos últimos 30 dias indicam mercado ES aquecido",
        "Zambeline sem sanções — apta a licitar em qualquer modalidade",
        "Capital social R$ 1,4M permite disputar até ~R$ 14M isoladamente (PL 10%)",
    ],
}

# ============================================================
# Top-level: inteligencia_mercado
# ============================================================
data["inteligencia_mercado"] = {
    "panorama": (
        "O setor de engenharia no Espírito Santo apresenta demanda ativa com 22 editais "
        "identificados nos últimos 30 dias. Destaque para habitação popular (4 editais, "
        "R$ 14,8M em Águia Branca e Gov. Lindenberg), infraestrutura urbana (Colatina "
        "R$ 19,8M, Pedro Canário R$ 5,4M) e equipamentos públicos (creche, escola, CRAS, "
        "hospital)."
    ),
    "tendencias": (
        "• Habitação popular em alta — Programa habitacional ativo no norte do ES\n"
        "• Infraestrutura viária recorrente — pavimentação, drenagem e ligação rodoviária\n"
        "• Dispensas frequentes — Baixo Guandu publicou 4 dispensas simultâneas (R$ 237k total)\n"
        "• Valores concentrados — 2 editais representam 86% do valor total aberto\n"
        "• Concorrência eletrônica predomina sobre presencial"
    ),
    "vantagens": (
        "• Vitória é central no ES — acesso a todo o estado em até 4-5 horas\n"
        "• 18 anos de atividade (desde 2008) — credibilidade e histórico\n"
        "• Sem sanções em nenhum cadastro federal\n"
        "• 13 CNAEs secundários cobrem construção, infraestrutura, instalações\n"
        "• Capital de R$ 1,4M permite disputar editais de até ~R$ 14M (PL 10%)"
    ),
    "nichos": (
        "• Habitação popular no norte do ES — pouco competido por grandes construtoras de Vitória\n"
        "• Reformas e ampliações institucionais (R$ 200k-4,5M) — porte ideal para a empresa\n"
        "• Consórcio para obras grandes — acesso a infraestrutura viária e habitação em escala"
    ),
    "recomendacao_geral": (
        "Priorizar Colatina (R$ 19,8M) via consórcio com empresa de obras de arte especiais. "
        "Monitorar resultado de Vila Pavão — se deserto/fracassado, novo prazo. "
        "Cadastrar alertas PNCP para engenharia no ES. Prospectar dispensas em municípios do "
        "noroeste (Águia Branca, Gov. Lindenberg) para obras habitacionais futuras."
    ),
}

# ============================================================
# Top-level: proximos_passos
# ============================================================
data["proximos_passos"] = [
    {
        "acao": "Avaliar atestados de cobertura metálica termoisolante para creche FNDE. Se disponíveis, preparar proposta emergencial Vila Pavão.",
        "prazo": "Hoje (12/03)",
        "prioridade": "URGENTE",
    },
    {
        "acao": "Verificar balanço patrimonial atual — se PL < R$ 1,99M, iniciar busca de parceiro para consórcio (Colatina).",
        "prazo": "Até 20/03",
        "prioridade": "ALTA",
    },
    {
        "acao": "Agendar visita técnica em Colatina (tel: (27) 3177-7080, prazo até 08/04).",
        "prazo": "Até 25/03",
        "prioridade": "ALTA",
    },
    {
        "acao": "Obter garantia de proposta 1% (R$ 199k) — caução, seguro-garantia ou fiança bancária.",
        "prazo": "Até 05/04",
        "prioridade": "ALTA",
    },
    {
        "acao": "Levantar atestados técnicos: drenagem, CBUQ, armação CA-50, calçada concreto, via especial.",
        "prazo": "Até 25/03",
        "prioridade": "MÉDIA",
    },
    {
        "acao": "Preparar proposta técnica Colatina (peso 60%) — metodologia, cronograma, equipe, soluções.",
        "prazo": "Até 10/04",
        "prioridade": "MÉDIA",
    },
    {
        "acao": "Consultar SICAF — verificar status cadastral e habilitações vigentes.",
        "prazo": "Até 20/03",
        "prioridade": "MÉDIA",
    },
    {
        "acao": "Monitorar resultado Vila Pavão — se deserto/fracassado, preparar para reabertura.",
        "prazo": "Após 17/03",
        "prioridade": "BAIXA",
    },
    {
        "acao": "Cadastrar alertas PNCP para Engenharia no ES — monitoramento contínuo.",
        "prazo": "Contínuo",
        "prioridade": "BAIXA",
    },
]

# ============================================================
# Top-level: mapa_competitivo
# ============================================================
data["mapa_competitivo"] = {
    "concorrentes_identificados": [
        {
            "empresa": "PLENA ENGENHARIA LTDA",
            "cnpj": "23.472.560/0001-44",
            "contratos": 1,
            "valor_total": 84241.49,
            "orgao": "Baixo Guandu",
        },
        {
            "empresa": "CONSTRUTORA LUARTE LTDA",
            "cnpj": "08.827.579/0001-72",
            "contratos": 1,
            "valor_total": 85800.00,
            "orgao": "Baixo Guandu",
        },
        {
            "empresa": "CONSTRUTORA PADRÃO LTDA",
            "cnpj": "16.456.069/0001-64",
            "contratos": 2,
            "valor_total": 67315.91,
            "orgao": "Baixo Guandu",
        },
    ],
    "analise_colatina": (
        "Competição Média a Alta — valor expressivo (R$ 19,8M) atrai construtoras de médio/grande "
        "porte do ES. Critério técnica e preço reduz competição por preço puro. Semi-integrada "
        "filtra participantes menores. Consórcio amplia campo."
    ),
    "analise_vila_pavao": (
        "Competição Média — creches FNDE são licitadas frequentemente. Menor preço favorece "
        "custo competitivo. Requisito de cobertura metálica pode filtrar participantes."
    ),
    "fonte": "Dispensas contratadas em Baixo Guandu (PNCP) + análise de mercado",
}

# ============================================================
# Save
# ============================================================
with open(INPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("JSON enriched successfully!")
print(f"  - {len(editais)} editais with recomendacao")
print(f"  - resumo_executivo added")
print(f"  - inteligencia_mercado added")
print(f"  - proximos_passos added ({len(data['proximos_passos'])} items)")
print(f"  - mapa_competitivo added")
