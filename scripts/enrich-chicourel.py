"""Enrich Chicourel Arquitetura report data with Phases 2-5 analysis."""
import json

d = json.load(open("docs/reports/data-14495815000101-2026-03-17.json", encoding="utf-8"))

# === Phase 2: Documental analysis ===

# Edital 1 - Piratini (PARTICIPAR)
ed1 = d["editais"][0]
ed1["analise_documental"] = {
    "ficha_tecnica": {
        "numero": "Concorrência nº 07/2026",
        "modalidade": "Concorrência Eletrônica",
        "criterio_julgamento": "Menor Preço por Lote",
        "modo_disputa": "Aberto",
        "regime_execucao": "Empreitada por Preço Global por Lote",
        "data_abertura_propostas": "01/04/2026 às 11:00",
        "prazo_impugnacao": "até 27/03/2026",
        "prazo_esclarecimentos": "até 27/03/2026",
        "prazo_execucao": "60 dias corridos por lote",
        "local_execucao": "Piratini/RS",
        "valor_estimado": "R$ 155.480,01",
        "lotes": [
            "Lote 1 - EMEF Vera Maria de Azevedo Moreira",
            "Lote 2 - EMEI Recanto Infantil",
            "Lote 3 - EMEI Gente Miúda",
        ],
    },
    "habilitacao_checklist": {
        "juridica": "Registro no CREA e/ou CAU em situação regular",
        "fiscal": "CND Federal, Estadual, Municipal, FGTS, CNDT",
        "tecnica": [
            "Registro da empresa no CREA e/ou CAU",
            "Registro profissional do(s) RT(s) no CREA e/ou CAU",
            "Comprovação de vínculo do RT com a empresa",
            "Atestado(s) de capacidade técnica em projetos compatíveis",
            "CAT emitida pelo CREA/CAU",
            "Declaração de equipe multidisciplinar (arquitetura, estrutura, elétrica, hidrossanitário, PPCI, acessibilidade)",
        ],
        "economico_financeira": [
            "Balanço Patrimonial do último exercício",
            "Certidão negativa de falência (60 dias)",
            "Índices: LG >= 1,0, LC >= 1,0, SG >= 1,0",
            "Patrimônio Líquido mínimo 10% do valor se índices insuficientes (R$ 15.548)",
        ],
    },
    "condicoes_comerciais": {
        "subcontratacao": "Vedada",
        "consorcio": "Não mencionado",
        "me_epp": "Tratamento diferenciado conforme LC 123/2006",
        "pagamento": "Integral por lote após entrega e aprovação",
    },
    "red_flags": [
        "Prazo curto: 14 dias até encerramento das propostas",
        "Distância 313 km de Lajeado - levantamentos in loco obrigatórios",
    ],
    "resumo_executivo": (
        "Contratação de empresa para elaborar projetos técnicos completos "
        "(arquitetônico + complementares + orçamento SINAPI) para reforma e "
        "ampliação de 3 escolas municipais em Piratini/RS. Valor total "
        "R$ 155.480 em 3 lotes independentes. Critério menor preço por lote. "
        "Prazo 60 dias por lote. Exige equipe multidisciplinar com CREA/CAU "
        "e atestados de projetos similares. Principal risco: prazo de 14 dias "
        "para preparar proposta + levantamento in loco a 313 km."
    ),
}
ed1["recomendacao"] = "PARTICIPAR"
ed1["justificativa"] = (
    "Edital alinhado ao perfil da empresa (elaboração de projetos arquitetônicos "
    "e complementares para escolas). Capital social R$ 80.000 atende ao mínimo de "
    "10% do valor (R$ 15.548). Concorrência por menor preço - não exige portfólio "
    "extenso. Empresa tem experiência com IFSC e IFFAR (projetos executivos). "
    "Risco principal: prazo de 14 dias para preparar proposta e necessidade de "
    "levantamento in loco a 313 km de Lajeado. Recomenda-se priorizar 1 ou 2 "
    "lotes se recursos limitados."
)
ed1["alternativa_participacao"] = "INDIVIDUAL"

# Edital 3 - Bento Gonçalves — RECLASSIFICAR
ed3 = d["editais"][2]
ed3["valor_estimado"] = 2275050.0
ed3["analise_documental"] = {
    "ficha_tecnica": {
        "numero": "Concorrência Eletrônica nº 002/2026",
        "modalidade": "Concorrência Eletrônica",
        "criterio_julgamento": "Técnica e Preço (70% técnica / 30% preço)",
        "modo_disputa": "Fechado",
        "prazo_execucao": "24 meses",
        "valor_estimado": "R$ 2.275.050,00",
        "recurso": "Federal - TC nº 968376/2024/MCIDADES/CAIXA",
    },
    "habilitacao_checklist": {
        "tecnica_especializada": [
            "Coordenador Técnico com experiência em PDDU para município >100k hab",
            "Modelagem hidrológica e hidráulica com simulação de cenários",
            "Experiência em planos integrados de infraestrutura urbana",
            "Experiência em Soluções Baseadas na Natureza (SBN)",
        ],
    },
    "red_flags": [
        "Valor R$ 2.275.050 - capital social R$ 80k = 3,5% (mínimo usual 10%)",
        "Técnica e Preço 70/30 - exige portfólio robusto em PDDU",
        "Experiência exigida em municípios >100k habitantes",
        "Prazo 24 meses - comprometimento de longo prazo",
        "Subcontratação não permitida",
    ],
}
ed3["recomendacao"] = "NÃO RECOMENDADO"
ed3["justificativa"] = (
    "Capital social insuficiente: R$ 80.000 = 3,5% do valor R$ 2.275.050 "
    "(mínimo usual: 10%). Critério Técnica e Preço 70/30 exige portfólio "
    "especializado em Planos Diretores de Drenagem Urbana para municípios com "
    "mais de 100 mil habitantes, modelagem hidrológica avançada e Soluções "
    "Baseadas na Natureza (SBN). Valor descoberto na análise documental "
    "(PNCP não informou)."
)
ed3["risk_score"]["vetoed"] = True
ed3["risk_score"]["veto_reasons"] = [
    "Capital social insuficiente: R$ 80.000 = 3,5% do valor R$ 2.275.050",
    "Requisitos técnicos altamente especializados (PDDU, modelagem hidrológica, SBN)",
]

# Phase 5 — Market intelligence
d["inteligencia_mercado"] = {
    "panorama": (
        "Mercado de projetos técnicos no RS apresenta volume estável nos últimos "
        "12 meses (variação 0%). Concentração baixa (HHI 0,0025) indica ambiente "
        "competitivo saudável. A maioria dos editais encontrados são de grande porte "
        "(acima de R$ 2M), fora do alcance da empresa."
    ),
    "tendencias": (
        "Concorrências eletrônicas predominam no segmento de projetos técnicos. "
        "Critério Técnica e Preço cada vez mais comum para PDDU e planos diretores. "
        "Forte demanda por PPCI e acessibilidade em reformas escolares."
    ),
    "vantagens_competitivas": (
        "Empresa de pequeno porte com experiência em projetos para instituições "
        "federais de ensino (IFSC, IFFAR). Perfil ideal para editais de R$ 50k-200k "
        "voltados a projetos de escolas, postos de saúde e edificações públicas."
    ),
    "oportunidades_nicho": (
        "Municípios pequenos do interior do RS que precisam de projetos técnicos "
        "para reformas e ampliações com recursos do FNDE/FUNDEB."
    ),
    "tese_estrategica": (
        "MANTER exposição B2G com foco em editais de menor porte (até R$ 300k) "
        "para projetos de escolas e edificações públicas."
    ),
}

# Next steps
d["proximos_passos"] = [
    {
        "prioridade": 1,
        "acao": "Preparar proposta para Concorrência 07/2026 de Piratini",
        "prazo": "27/03/2026 (prazo de esclarecimentos)",
        "detalhes": (
            "Verificar viabilidade de levantamento in loco (313 km). "
            "Considerar focar em 1-2 lotes se recursos limitados. "
            "Reunir atestados de projetos similares e CATs."
        ),
    },
    {
        "prioridade": 2,
        "acao": "Registrar CATs dos projetos realizados para IFSC e IFFAR",
        "prazo": "Imediato",
        "detalhes": "CATs são exigidas em praticamente todos os editais de projetos técnicos.",
    },
    {
        "prioridade": 3,
        "acao": "Cadastrar-se no Portal de Compras Públicas e SICAF",
        "prazo": "30 dias",
        "detalhes": "Editais de Piratini e Bento Gonçalves usam portais diferentes.",
    },
    {
        "prioridade": 4,
        "acao": "Monitorar editais de projetos técnicos no RS (até R$ 300k)",
        "prazo": "Contínuo (semanal)",
        "detalhes": (
            "Focar em concorrências e pregões para serviços de engenharia e "
            "arquitetura no Vale do Taquari, Serra Gaúcha e Campanha."
        ),
    },
]

# Delivery validation
d["delivery_validation"] = {
    "gate_deterministic": "WARNINGS",
    "gate_adversarial": "REVISED",
    "revisions_made": [
        (
            "Reclassificado Edital 3 (Bento Gonçalves PDDU) de PARTICIPAR para "
            "NÃO RECOMENDADO - valor R$ 2.275.050 descoberto na análise documental "
            "(PNCP não informou) + requisitos técnicos especializados"
        ),
        (
            "Alerta de amostra pequena (4 contratos): cluster Manutenção Predial "
            "sub-representado nos editais - validador emitiu WARNING (não BLOCK)"
        ),
    ],
    "reader_persona": (
        "Dona de escritório de arquitetura EPP (capital R$ 80k), "
        "sede em Lajeado/RS, busca ações concretas para participar "
        "de licitações de projetos técnicos"
    ),
}

with open("docs/reports/data-14495815000101-2026-03-17.json", "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print("JSON enriquecido salvo com sucesso")
for i, ed in enumerate(d["editais"]):
    v = ed.get("valor_estimado")
    vstr = f"R$ {v:,.2f}" if v else "Sigiloso"
    print(f"  {i+1}. [{ed['recomendacao']}] {ed.get('orgao','?')} - {ed.get('municipio')}/{ed.get('uf')} - {vstr}")
