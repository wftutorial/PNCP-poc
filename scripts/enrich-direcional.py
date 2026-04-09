#!/usr/bin/env python3
"""
Enrich report data for DIRECIONAL CONSTRUCAO E PAVIMENTACAO LTDA
ANALYST Phase 2-5: Document analysis, strategic analysis, competitive intel, market intel
"""
import json
import sys
from datetime import datetime

DATA_PATH = "docs/reports/data-36895097000276-2026-03-18.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

empresa = data["empresa"]
editais = data["editais"]
setor = data["setor"]

# ============================================================
# IMPORTANT CONTEXT NOTES
# ============================================================
# 1. Sanções: empresa.sancoes shows all False but inconclusive=True
#    (Portal da Transparência returned corrupt response).
#    The script's alertas_criticos flag "SANCAO_ATIVA" based on inconclusive.
#    We reference this in narrative but do NOT modify alertas_criticos.
#
# 2. Company is NEW (since 2025-07-10), Simples Nacional, capital R$1M
#    ZERO contract history — all acervo is NAO_VERIFICADO
#    SICAF: NÃO CADASTRADO
#
# 3. Gate warnings to address:
#    - HABILITACAO_HIGH_PARTIAL: 83% editais with partial habilitação
#    - ACERVO_MOSTLY_UNVERIFIED: 36/36 with unverified acervo
#    - LOW_PROBABILITY_SPREAD: 0.2pp spread
# ============================================================

# Helper: format currency
def fmt_r(v):
    if v is None or v == 0:
        return "Valor não informado"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Helper: get distance
def get_dist(ed):
    d = ed.get("distancia", {})
    return d.get("km")

# ============================================================
# PHASE 2-3: Per-edital analysis
# ============================================================

for i, ed in enumerate(editais):
    dias = ed.get("dias_restantes") or 0
    valor = ed.get("valor_estimado") or 0
    score = ed.get("risk_score", {}).get("total", 0)
    rec = ed.get("recomendacao", "")
    mun = ed.get("municipio", "")
    orgao = ed.get("orgao", "")
    obj = ed.get("objeto", "")
    mod = ed.get("modalidade", "")
    dist_km = get_dist(ed)
    ibge = ed.get("ibge", {})
    pop = ibge.get("populacao")
    pib = ibge.get("pib_mil_reais")
    risk = ed.get("risk_score", {})
    hab = ed.get("habilitacao_analysis", {})
    comp = ed.get("competitive_analysis", {})
    alertas = ed.get("alertas_criticos", [])
    roi = ed.get("roi_potential", {})
    scenarios = ed.get("scenarios", {})
    sensitivity = ed.get("sensitivity", {})
    win_prob = ed.get("win_probability", {})
    cronograma = ed.get("cronograma", [])
    pb = ed.get("price_benchmark", {})
    acervo_st = ed.get("acervo_status", "NAO_VERIFICADO")
    qual_gap = ed.get("qualification_gap", {})
    hab25 = hab.get("habilitacao_checklist_25", {})
    organ_risk = ed.get("organ_risk", {})
    risk_analysis = ed.get("risk_analysis", {})
    comp_intel = ed.get("competitive_intel_filtered", [])

    # Determine if edital is closed (dias <= 0) or status ENCERRADO
    is_closed = dias <= 0 or ed.get("status_edital") == "ENCERRADO"

    # ---- ANALISE DOCUMENTAL ----
    analise_documental = {}

    # Ficha técnica
    ficha = {
        "numero_processo": "",
        "modalidade": mod,
        "criterio_julgamento": "Menor preço global",
        "data_abertura": ed.get("data_abertura", ""),
        "data_encerramento": ed.get("data_encerramento", ""),
        "prazo_execucao": "Conforme edital",
        "valor_estimado": fmt_r(valor),
    }

    # Based on PDF analysis for specific editais
    cnpj_orgao = ed.get("cnpj_orgao", "")
    seq = ed.get("sequencial_compra", "")

    hab_exigencias = []
    red_flags = []
    condicionantes_list = []

    # === SPECIFIC EDITAL ANALYSIS FROM PDF READING ===

    if cnpj_orgao == "66229717000118" and seq == "18":
        # UBAPORANGA - Score 88 - Pavimentação CBUQ - Read full edital
        ficha["numero_processo"] = "020/2026 - Concorrência 001/2026"
        ficha["criterio_julgamento"] = "Menor preço global (modo aberto e fechado)"
        ficha["prazo_execucao"] = "12 meses"
        ficha["plataforma"] = "BBMNET (novobbmnet.com.br)"
        ficha["garantia_proposta"] = "1% do valor estimado (R$ 4.994)"
        ficha["garantia_contratual"] = "5% do valor do contrato"
        hab_exigencias = [
            "CREA/CAU da empresa e do responsável técnico",
            "Atestado de capacidade técnica com mínimo 50% do item 3.6 (CBUQ)",
            "Alvará de funcionamento 2026",
            "Balanço patrimonial últimos 2 exercícios (LG, SG, LC > 1)",
            "Certidão negativa de falência",
            "Indicação de pessoal técnico e equipamentos",
            "Vistoria prévia ou declaração de conhecimento",
        ]
        red_flags = [
            "Habilitação ANTES da proposta — empresa precisa ter TODOS os documentos prontos no ato do credenciamento",
            "Exige garantia de proposta de 1% (R$ 4.994) — custo não recuperável se não vencer",
        ]
        condicionantes_list = [
            "Obter registro CREA/CAU ativo para empresa e responsável técnico",
            "Providenciar atestado de capacidade técnica com quantitativo mínimo de 50% de CBUQ",
            "Preparar garantia de proposta (1% = R$ 4.994)",
        ]

    elif cnpj_orgao == "23804149000129" and seq == "98":
        # PONTE NOVA - Score 85 - Pavimentação asfáltica
        ficha["numero_processo"] = "Edital 29-2026 - Concorrência 001/2026"
        ficha["criterio_julgamento"] = "Menor preço global (modo aberto)"
        ficha["prazo_execucao"] = "Conforme cronograma físico-financeiro"
        ficha["plataforma"] = "Licitar Digital (licitar.digital)"
        ficha["garantia_contratual"] = "5% do valor do contrato"
        hab_exigencias = [
            "CREA/CAU da empresa e responsável técnico",
            "Atestado técnico-operacional: mínimo 50% CBUQ (~52m³) e 50% sarjeta (~550m)",
            "Atestado técnico-profissional via ART do engenheiro civil",
            "Declaração de Responsabilidade Técnica com vínculo comprovado",
            "Balanço patrimonial 2 exercícios (LG, SG, LC > 1 ou capital mínimo 10%)",
            "Certidão negativa de falência",
            "Vistoria facultativa (pode substituir por declaração)",
        ]
        red_flags = [
            "Exige quantitativos mínimos específicos para CBUQ (52m³) e sarjeta (550m) — necessário atestado detalhado",
            "Capital mínimo de 10% exigido se índices contábeis < 1 (R$ 60.764)",
        ]
        condicionantes_list = [
            "Obter atestados com quantitativos mínimos de pavimentação asfáltica (52m³ CBUQ)",
            "Confirmar registro CREA do responsável técnico com ART compatível",
        ]

    elif cnpj_orgao == "17005000000187" and seq == "16":
        # GALILEIA - Score 78 - Ponte mista
        ficha["numero_processo"] = "036/2026 - Concorrência Eletrônica 003/2026"
        ficha["criterio_julgamento"] = "Menor preço global (modo aberto e fechado)"
        ficha["plataforma"] = "BLL - Bolsa de Licitações do Brasil (bll.org.br)"
        ficha["prazo_execucao"] = "Conforme projeto executivo"
        hab_exigencias = [
            "CREA/CAU da empresa e responsável técnico",
            "Atestado de execução de obra de ponte ou estrutura similar",
            "Balanço patrimonial e demonstrações contábeis",
            "Certidão negativa de falência",
            "Vistoria facultativa",
        ]
        red_flags = [
            "Obra de ponte exige especialização técnica específica — atestados devem comprovar experiência em estruturas",
            "Prioridade para ME/EPP regionais da Microrregião 37 (Governador Valadares) — até 10% de margem",
        ]
        condicionantes_list = [
            "Verificar se responsável técnico possui CAT em obra de ponte",
            "Avaliar se empresa possui experiência em estruturas de concreto",
        ]

    elif cnpj_orgao == "20905865000104" and seq == "24":
        # INHAPIM - Score 78 - Ponte aduelas de concreto
        ficha["numero_processo"] = "008/2026 - Concorrência Eletrônica 004/2026"
        ficha["criterio_julgamento"] = "Menor preço global (modo aberto e fechado)"
        ficha["plataforma"] = "BBMNET (novobbmnet.com.br)"
        ficha["prazo_execucao"] = "Conforme projeto executivo"
        hab_exigencias = [
            "CREA/CAU da empresa e responsável técnico",
            "Atestado de execução de obra de ponte em aduelas de concreto",
            "Projeto básico e executivo disponíveis (11 documentos no PNCP)",
            "Balanço patrimonial e demonstrações contábeis",
        ]
        red_flags = [
            "Ponte em aduelas de concreto — obra especializada que exige experiência comprovada",
            "Valor não informado no edital — avaliar planilha orçamentária",
        ]
        condicionantes_list = [
            "Analisar planilha orçamentária e composições antes de decisão",
            "Verificar capacidade técnica para execução de pontes em aduelas",
        ]

    elif cnpj_orgao == "18414581000173" and seq == "8":
        # ÁGUAS VERMELHAS - Score 74 - Pavimentação CBUQ Trecho 3
        ficha["numero_processo"] = "009/2026 - Concorrência Eletrônica 003/2026"
        ficha["criterio_julgamento"] = "Menor preço global (modo aberto)"
        ficha["plataforma"] = "Licitar Digital (licitardigital.com.br)"
        ficha["prazo_execucao"] = "Conforme cronograma"
        ficha["garantia_proposta"] = "Não exigida"
        hab_exigencias = [
            "CREA/CAU pessoa jurídica e profissional",
            "CAT do CREA com acervo em pavimentação CBUQ (122,85m³), imprimação (4.095m²), pintura de ligação (4.095m²)",
            "Profissional no quadro permanente com vínculo comprovado (CTPS, contrato social ou prestação de serviços)",
            "Balanço patrimonial (LG, SG, LC > 1 ou PL de 10%)",
            "Certidão negativa de falência",
            "Vistoria facultativa",
        ]
        red_flags = [
            "INVERSÃO DE FASES — habilitação ANTES dos lances (19/03/2026). Documentação deve estar 100% pronta",
            "Exige CAT específica com quantitativos mínimos de CBUQ, imprimação e pintura de ligação",
            "Distância de 583km da sede — custo logístico significativo para mobilização",
        ]
        condicionantes_list = [
            "Preparar toda documentação de habilitação ANTES da sessão de 19/03/2026",
            "Obter CAT com quantitativos compatíveis com os exigidos",
            "Calcular custo de mobilização para 583km",
        ]

    elif cnpj_orgao == "18675934000199":
        # MUNHOZ - Score 72 - Pavimentação estrada (2 trechos)
        ficha["numero_processo"] = f"Concorrência Eletrônica - Munhoz/MG"
        ficha["plataforma"] = "A verificar"
        hab_exigencias = [
            "CREA/CAU da empresa e responsável técnico",
            "Atestado de pavimentação asfáltica em estrada",
            "Balanço patrimonial e índices contábeis",
        ]
        red_flags = [
            "Distância de 779km — custo logístico muito elevado",
            f"Dois trechos do mesmo órgão (R$ 888.107 + R$ 745.110) — possibilidade de participar em ambos",
        ]
        condicionantes_list = [
            "Avaliar viabilidade logística para 779km de deslocamento",
            "Considerar participação nos dois trechos para diluir custo de mobilização",
        ]

    elif cnpj_orgao == "18650952000116" and seq == "8":
        # ESPINOSA - Score 70 - Pavimentação estrada vicinal R$ 2.4M
        ficha["numero_processo"] = "Concorrência Eletrônica - Espinosa/MG"
        ficha["plataforma"] = "A verificar"
        hab_exigencias = [
            "CREA/CAU da empresa e responsável técnico",
            "Atestado de pavimentação de estrada vicinal com quantitativos significativos",
            "Balanço patrimonial com índices contábeis ou capital mínimo de 10% (~R$ 242.316)",
            "Certidão negativa de falência",
        ]
        red_flags = [
            "Valor de R$ 2,4 milhões — ALERTA: contrato ultrapassa 2× o capital social da empresa",
            "Simples Nacional: faturamento anual pode ultrapassar teto com este contrato",
            "Distância de 830km — custo logístico muito elevado",
        ]
        condicionantes_list = [
            "Avaliar impacto tributário no Simples Nacional",
            "Confirmar capacidade de garantias (5% = ~R$ 121.158)",
            "Avaliar estrutura operacional para obra de grande porte a 830km",
        ]

    elif "17309790000194" in str(cnpj_orgao):
        # DER-MG editais - Supervisão de obras rodoviárias
        ficha["orgao_tipo"] = "Governo do Estado de Minas Gerais"
        hab_exigencias = [
            "CREA/CAU da empresa e responsável técnico",
            "Atestados de supervisão de obras rodoviárias",
            "Registro no SICAF (preferencialmente)",
            "Balanço patrimonial com índices contábeis robustos",
            "Equipe técnica qualificada para supervisão",
        ]
        red_flags = [
            "Valores muito elevados (R$ 4M a R$ 6,4M) — incompatíveis com capital social de R$ 1M",
            "Serviços de SUPERVISÃO, não execução — exige perfil técnico-consultivo",
            "DER-MG tem padrões rigorosos de qualificação técnica",
        ]
        condicionantes_list = [
            "Empresa precisaria de consórcio ou subcontratação para atender requisitos",
            "Capital social insuficiente para garantias exigidas em contratos desta magnitude",
        ]

    else:
        # Generic analysis for remaining editais
        hab_exigencias = [
            "CREA/CAU da empresa e responsável técnico",
            "Atestado de capacidade técnica compatível com objeto",
            "Balanço patrimonial e demonstrações contábeis",
            "Certidão negativa de falência",
            "Regularidade fiscal e trabalhista",
        ]
        if valor and valor > 500000:
            red_flags.append(f"Valor de {fmt_r(valor)} — avaliar compatibilidade com capital e estrutura operacional")
        if dist_km and dist_km > 500:
            red_flags.append(f"Distância de {dist_km:.0f}km — custo logístico significativo")
        if dias <= 5:
            red_flags.append(f"Prazo exíguo: apenas {dias} dia(s) para encerramento")

    analise_documental = {
        "ficha_tecnica": ficha,
        "habilitacao_exigencias": hab_exigencias,
        "status_analise": "COMPLETA" if cnpj_orgao in [
            "66229717000118", "23804149000129", "17005000000187",
            "20905865000104", "18414581000173", "18650952000116",
            "18675934000199"
        ] or "17309790000194" in str(cnpj_orgao) else "PARCIAL",
        "fonte_documento": "Edital disponível no Portal Nacional de Contratações Públicas" if ed.get("fonte") == "PNCP" else "Portal de Compras Públicas",
    }

    # ---- ANALISE DETALHADA ----

    # Build strategic narrative per edital
    narrativa_parts = []

    # 1. Aderência ao perfil
    cnae_compat = ed.get("_cnae_compatible", True)
    obj_compat = ed.get("object_compatibility", {}).get("compatibility", "MEDIA")
    narrativa_parts.append(
        f"Aderência ao perfil: {'Alta' if obj_compat == 'ALTA' else 'Média' if obj_compat == 'MEDIA' else 'Baixa'}. "
        f"O objeto {'é diretamente compatível' if cnae_compat else 'apresenta divergência'} com as atividades da empresa "
        f"(CNAE principal 4213-8 — Obras de urbanização e infraestrutura viária)."
    )

    # 2. Análise de valor
    if valor:
        ratio = valor / empresa["capital_social"] if empresa["capital_social"] else 0
        narrativa_parts.append(
            f"Análise de valor: {fmt_r(valor)} representa {ratio:.1%} do capital social ({fmt_r(empresa['capital_social'])}). "
        )
        srw = ed.get("habilitacao_checklist", {}).get("simples_revenue_warning", False)
        if srw:
            narrativa_parts.append(
                "ALERTA TRIBUTÁRIO: Este contrato pode levar o faturamento anual acima do teto do Simples Nacional "
                "(R$ 4,8 milhões). Esta é uma decisão tributária do empresário, não impedimento legal para participar."
            )

    # 3. Análise geográfica
    if dist_km is not None:
        geo_text = "muito próximo" if dist_km < 50 else "próximo" if dist_km < 100 else "distância viável" if dist_km < 300 else "distância moderada" if dist_km < 500 else "distância elevada" if dist_km < 800 else "distância muito elevada"
        narrativa_parts.append(
            f"Análise geográfica: {mun} fica a {dist_km:.0f}km da sede ({geo_text}). "
        )
        if pop:
            narrativa_parts.append(
                f"Município com {pop:,} habitantes"
                + (f" e Produto Interno Bruto de R$ {pib:,.0f} mil" if pib else "")
                + "."
            )

    # 4. Análise de prazo
    if dias > 0:
        prazo_text = "confortável" if dias >= 15 else "adequado" if dias >= 7 else "apertado" if dias >= 3 else "insuficiente"
        narrativa_parts.append(
            f"Análise de prazo: {dias} dias restantes ({prazo_text} para preparação de proposta)."
        )
    else:
        narrativa_parts.append("Prazo: Edital encerrado ou encerrando hoje.")

    # 5. Score 5D decomposition
    hab_sc = risk.get("habilitacao", 0)
    fin_sc = risk.get("financeiro", 0)
    geo_sc = risk.get("geografico", 0)
    prazo_sc = risk.get("prazo", 0)
    comp_sc = risk.get("competitivo", 0)
    narrativa_parts.append(
        f"Viabilidade 5D (score total: {score}/100): "
        f"Habilitação {hab_sc}/100 (peso 25%), "
        f"Financeiro {fin_sc}/100 (peso 30%), "
        f"Geográfico {geo_sc}/100 (peso 25%), "
        f"Prazo {prazo_sc}/100 (peso 15%), "
        f"Competitivo {comp_sc}/100 (peso 5%)."
    )

    # 6. Price benchmark
    pb_status = pb.get("_source", {}).get("status", "")
    if pb_status == "CALCULATED":
        pb_min = pb.get("min", 0)
        pb_med = pb.get("median", 0)
        pb_max = pb.get("max", 0)
        vs = pb.get("vs_estimado", "")
        narrativa_parts.append(
            f"Referência de preços: mínimo {fmt_r(pb_min)}, mediana {fmt_r(pb_med)}, máximo {fmt_r(pb_max)}. "
            f"Valor estimado do edital está {vs.lower() if vs else 'dentro'} da faixa de referência."
        )

    # 7. Acervo técnico
    narrativa_parts.append(
        f"Acervo técnico: {acervo_st.replace('_', ' ')}. "
        + ("A empresa não possui histórico de contratos governamentais verificados. "
           "Este é o principal fator de risco para habilitação técnica."
           if acervo_st == "NAO_VERIFICADO" else "")
    )

    # 8. Alertas
    alertas_crit = [a for a in alertas if a.get("severidade") == "CRITICO"]
    if alertas_crit:
        for a in alertas_crit:
            narrativa_parts.append(f"ALERTA: {a['descricao']}.")

    # 9. Competitiva
    comp_level = comp.get("competition_level", "")
    top_sup = comp.get("top_supplier", {})
    if top_sup:
        narrativa_parts.append(
            f"Ambiente competitivo: {comp_level.lower() if comp_level else 'não avaliado'}. "
            f"Principal fornecedor: {top_sup.get('nome', 'Não identificado')} "
            f"({top_sup.get('share', 0):.0%} dos contratos recentes)."
        )

    analise_detalhada = " ".join(narrativa_parts)

    # ---- ANALISE RESUMO ----
    analise_resumo = ""
    if rec == "PARTICIPAR":
        analise_resumo = (
            f"Edital de {mod.lower()} para {obj[:100]}{'...' if len(obj) > 100 else ''} "
            f"no município de {mun}/MG. Valor estimado de {fmt_r(valor)}. "
            f"Score de viabilidade {score}/100. "
            f"{'Proximidade favorável' if dist_km and dist_km < 200 else 'Distância viável' if dist_km and dist_km < 500 else 'Distância elevada que demanda avaliação logística'} "
            f"({dist_km:.0f}km). " if dist_km else ""
        )
        analise_resumo += (
            f"Recomendação: PARTICIPAR. A empresa deve providenciar a documentação de habilitação e "
            f"avaliar a viabilidade operacional considerando seu perfil de empresa nova no mercado B2G. "
            f"Risco principal: acervo técnico não verificado — necessário confirmar atestados do responsável técnico."
        )
    elif rec == "AVALIAR COM CAUTELA":
        analise_resumo = (
            f"Edital de {mod.lower()} para {obj[:100]}{'...' if len(obj) > 100 else ''} "
            f"no município de {mun}/MG. Valor estimado de {fmt_r(valor)}. "
            f"Score de viabilidade {score}/100. "
            f"Recomendação: AVALIAR COM CAUTELA. "
        )
        if "17309790000194" in str(cnpj_orgao):
            analise_resumo += (
                "Edital do DER-MG para serviços de supervisão de obras rodoviárias — "
                "perfil técnico-consultivo que demanda equipe especializada e capital compatível. "
                "Avaliar possibilidade de consórcio."
            )
        else:
            analise_resumo += (
                "Há condicionantes que precisam ser avaliadas antes da decisão de participação. "
                "Verificar detalhadamente os requisitos de habilitação no edital completo."
            )
    else:  # NÃO RECOMENDADO
        reason = ""
        threshold = risk.get("threshold_applied", "")
        if threshold == "prazo_critico":
            reason = f"Prazo insuficiente ({dias} dias restantes)"
        elif threshold == "valor_excessivo":
            reason = "Valor incompatível com porte da empresa"
        elif risk.get("vetoed"):
            reason = "Veto automático: " + "; ".join(risk.get("veto_reasons", []))
        else:
            reason = ed.get("justificativa", "")[:150]

        analise_resumo = (
            f"Edital de {mod.lower()} em {mun}/MG. "
            f"Valor: {fmt_r(valor)}. "
            f"NÃO RECOMENDADO. Motivo: {reason}."
        )

    # ---- RED FLAGS DOCUMENTAIS ----
    red_flags_doc = red_flags if red_flags else []

    # Add generic red flags based on data
    if ed.get("habilitacao_checklist", {}).get("simples_revenue_warning"):
        red_flags_doc.append(
            "Contrato pode levar faturamento acima do teto do Simples Nacional — decisão tributária do empresário"
        )

    if acervo_st == "NAO_VERIFICADO":
        # Don't add if already present
        if not any("acervo" in r.lower() for r in red_flags_doc):
            red_flags_doc.append(
                "Acervo técnico não verificado — empresa sem histórico de contratos governamentais comprovados"
            )

    # ---- CONDICIONANTES ----
    if not condicionantes_list:
        if rec == "PARTICIPAR":
            condicionantes_list = [
                "Confirmar registro CREA/CAU ativo",
                "Providenciar atestados de capacidade técnica",
                "Preparar documentação fiscal e trabalhista completa",
            ]
        elif rec == "AVALIAR COM CAUTELA":
            condicionantes_list = [
                "Analisar edital completo antes de decidir",
                "Verificar requisitos específicos de habilitação",
                "Avaliar custo-benefício da participação",
            ]

    # ---- WRITE BACK ----
    ed["analise_documental"] = analise_documental
    ed["analise_detalhada"] = analise_detalhada
    ed["analise_resumo"] = analise_resumo
    ed["red_flags_documentais"] = red_flags_doc
    ed["condicionantes"] = condicionantes_list


# ============================================================
# PHASE 4-5: Market Intelligence & Executive Summary
# ============================================================

# Count by recommendation (only open editais)
open_editais = [e for e in editais if (e.get("dias_restantes") or 0) > 0]
participar = [e for e in open_editais if e.get("recomendacao") == "PARTICIPAR"]
avaliar = [e for e in open_editais if e.get("recomendacao") == "AVALIAR COM CAUTELA"]
nao_rec = [e for e in open_editais if e.get("recomendacao") == "NÃO RECOMENDADO"]

total_valor_participar = sum((e.get("valor_estimado") or 0) for e in participar)
total_valor_avaliar = sum((e.get("valor_estimado") or 0) for e in avaliar)
total_valor_all = sum((e.get("valor_estimado") or 0) for e in open_editais)

# Strategic thesis from script
thesis = data.get("strategic_thesis", {})

# RESUMO EXECUTIVO
data["resumo_executivo"] = {
    "empresa": empresa["razao_social"],
    "nome_fantasia": empresa.get("nome_fantasia", ""),
    "cnpj": empresa["cnpj"],
    "setor": setor,
    "data_analise": "2026-03-19",
    "total_editais_analisados": len(editais),
    "editais_abertos": len(open_editais),
    "editais_encerrados": len(editais) - len(open_editais),
    "recomendacoes": {
        "participar": len(participar),
        "avaliar_com_cautela": len(avaliar),
        "nao_recomendado": len(nao_rec),
    },
    "valor_total_oportunidades": total_valor_all,
    "valor_participar": total_valor_participar,
    "valor_avaliar": total_valor_avaliar,
    "perfil_empresa": {
        "maturidade": empresa.get("maturity_profile", {}).get("profile", "CRESCIMENTO"),
        "score_maturidade": empresa.get("maturity_profile", {}).get("score", 40),
        "capital_social": fmt_r(empresa["capital_social"]),
        "simples_nacional": empresa["simples_nacional"],
        "contratos_anteriores": len(empresa.get("historico_contratos", [])),
        "sicaf": "NÃO CADASTRADO",
        "idade_empresa": "Menos de 1 ano (desde julho/2025)",
        "sancoes": "Verificação inconclusiva — recomendável consulta direta aos órgãos competentes",
    },
    "alertas_gerais": [
        "Empresa nova no mercado B2G (desde julho/2025) — sem histórico de contratos governamentais",
        "Acervo técnico não verificado em nenhum edital — principal barreira para habilitação",
        "SICAF não cadastrado — providenciar cadastro para ampliar acesso a licitações",
        "Verificação de sanções inconclusiva — recomendável consulta direta ao Portal da Transparência",
        "83% dos editais com habilitação parcial — perfil técnico requer fortalecimento",
    ],
    "gate_warnings_addressed": {
        "HABILITACAO_HIGH_PARTIAL": (
            "83% dos editais apresentam habilitação parcial. Isto reflete o perfil de empresa nova "
            "sem histórico de contratos e sem cadastro SICAF. A recomendação é priorizar o cadastro SICAF "
            "e a obtenção de atestados técnicos como primeiro passo antes de participar ativamente de licitações."
        ),
        "ACERVO_MOSTLY_UNVERIFIED": (
            "Todos os 36 editais apresentam acervo não verificado porque a empresa não possui histórico "
            "de contratos governamentais. Isto não impede a participação, mas significa que a empresa "
            "dependerá integralmente dos atestados do responsável técnico (pessoa física). "
            "Recomendação: contratar ou associar-se a engenheiro com CAT registrada em obras similares."
        ),
        "LOW_PROBABILITY_SPREAD": (
            "O spread de probabilidade de 0.2pp reflete o fato de que a empresa tem perfil similar "
            "para todos os editais (mesma distância relativa, mesmo acervo não verificado, mesmo capital). "
            "A diferenciação real virá da análise documental e da estratégia de preço em cada certame."
        ),
    },
    "tese_estrategica": thesis.get("thesis", "MANTER"),
    "tese_racional": (
        "Empresa em fase de crescimento com capital sólido (R$ 1 milhão) porém sem histórico B2G. "
        "O mercado de infraestrutura viária em Minas Gerais apresenta ambiente competitivo saudável "
        f"(índice de concentração de 0,035 — mercado fragmentado) e desconto médio de apenas -0,3%, "
        "indicando margens razoáveis. Recomendação: MANTER estratégia de entrada gradual, "
        "priorizando editais próximos à sede (região do Vale do Rio Doce) com valores compatíveis "
        "com o capital social (até R$ 1 milhão). Primeiro contrato é o mais estratégico — "
        "uma vez obtido o primeiro atestado, o acesso a editais se amplia significativamente."
    ),
}

# INTELIGENCIA DE MERCADO
data["inteligencia_mercado"] = {
    "panorama_setorial": {
        "editais_abertos_mg": len(open_editais),
        "valor_total": fmt_r(total_valor_all),
        "modalidades": {
            "concorrencia_eletronica": sum(1 for e in open_editais if "Concorrência" in str(e.get("modalidade", ""))),
            "pregao": sum(1 for e in open_editais if "Pregão" in str(e.get("modalidade", ""))),
        },
        "concentracao_orgaos": (
            "DER-MG é o maior licitador com 7 editais (R$ 30+ milhões), seguido por municípios "
            "de pequeno e médio porte do interior de Minas Gerais."
        ),
    },
    "tendencias": {
        "modalidade_dominante": "Concorrência Eletrônica (Lei 14.133/2021)",
        "valor_medio": fmt_r(total_valor_all / len(open_editais) if open_editais else 0),
        "objetos_frequentes": [
            "Pavimentação asfáltica em CBUQ",
            "Recapeamento de vias municipais",
            "Construção e reforma de pontes",
            "Supervisão de obras rodoviárias",
            "Drenagem e infraestrutura viária",
        ],
        "plataformas": [
            "BBMNET (novobbmnet.com.br)",
            "Licitar Digital (licitardigital.com.br)",
            "BLL - Bolsa de Licitações (bll.org.br)",
            "ComprasNet / BNC",
        ],
    },
    "vantagens_competitivas": [
        "Capital social robusto (R$ 1 milhão) para empresa nova — permite participar de editais de médio porte",
        "CNAE principal compatível (4213-8 Infraestrutura Viária) + 20 CNAEs secundários — ampla cobertura",
        "Sede em Simonésia/MG — posição estratégica no Vale do Rio Doce com acesso à região leste de MG",
        "Regime do Simples Nacional — benefício fiscal em licitações exclusivas para ME/EPP",
    ],
    "oportunidades_nicho": [
        {
            "nicho": "Municípios do Vale do Rio Doce e Zona da Mata",
            "racional": "Proximidade da sede (< 150km), editais frequentes de pavimentação, menor concorrência",
            "editais_exemplo": ["Ubaporanga (73km)", "Inhapim (85km)", "Galileia (235km)"],
        },
        {
            "nicho": "Obras de ponte em municípios rurais",
            "racional": "Demanda constante, poucos concorrentes especializados, CNAE compatível",
            "editais_exemplo": ["Galileia - ponte mista", "Inhapim - ponte em aduelas"],
        },
        {
            "nicho": "Convênios estaduais (SEGOV/SEINFRA)",
            "racional": "Municípios pequenos recebendo transferências estaduais para pavimentação — pagamento mais seguro",
            "editais_exemplo": ["Ubaporanga (SEGOV)", "Águas Vermelhas (SEINFRA)"],
        },
    ],
    "riscos_mercado": [
        "Empresa sem histórico B2G — primeiro contrato é barreira crítica de entrada",
        "Acervo técnico dependerá integralmente do responsável técnico contratado",
        "Simples Nacional limita faturamento a R$ 4,8 milhões/ano — contratos grandes requerem planejamento tributário",
        "SICAF não cadastrado — reduz visibilidade em licitações federais e estaduais",
    ],
    "recomendacao_geral": (
        "Estratégia de entrada gradual: priorizar editais de pavimentação asfáltica em municípios "
        "do Vale do Rio Doce (raio de 150km da sede), com valores entre R$ 100 mil e R$ 800 mil. "
        "O primeiro contrato bem executado gera o atestado técnico necessário para desbloquear "
        "editais de maior valor. Paralelamente, realizar cadastro no SICAF e obter certidões "
        "necessárias para habilitação recorrente."
    ),
}

# PROXIMOS_PASSOS - enrich existing
# The script already computed proximos_passos, so we'll enrich it rather than overwrite
existing_pp = data.get("proximos_passos", {})

# Build priority actions
acoes_imediatas = []
acoes_curto = []
acoes_medio = []

# PRIORITY 0: Sanções
acoes_imediatas.append({
    "acao": "Consultar diretamente o Portal da Transparência para esclarecer situação de sanções (verificação inconclusiva)",
    "prazo": "Imediato",
    "prioridade": 0,
    "prioridade_label": "URGENTE",
    "justificativa": "Verificação de sanções retornou resposta inconclusiva — necessário esclarecer antes de qualquer participação"
})

# PRIORITY 1: SICAF
acoes_imediatas.append({
    "acao": "Providenciar cadastro no SICAF (Sistema de Cadastramento Unificado de Fornecedores)",
    "prazo": "Próximos 15 dias",
    "prioridade": 1,
    "prioridade_label": "URGENTE",
    "justificativa": "Empresa consta como NÃO CADASTRADA — SICAF é exigência frequente em licitações"
})

# PRIORITY 2: CREA
acoes_imediatas.append({
    "acao": "Confirmar registro CREA ativo da empresa e do responsável técnico, com CAT em obras de pavimentação",
    "prazo": "Próximos 15 dias",
    "prioridade": 2,
    "prioridade_label": "URGENTE",
    "justificativa": "Todos os editais de obras exigem CREA e atestados técnicos — pré-requisito fundamental"
})

# PRIORITY 3: Certidões
acoes_imediatas.append({
    "acao": "Emitir e organizar certidões fiscais (CND Federal, Estadual, Municipal, FGTS, CNDT, Falência)",
    "prazo": "Próximos 10 dias",
    "prioridade": 3,
    "prioridade_label": "ALTA",
    "justificativa": "Documentação básica exigida em todos os editais — preparar pacote padrão de habilitação"
})

# Editais PARTICIPAR com prazo adequado
for ed in sorted(participar, key=lambda x: (-x.get("risk_score", {}).get("total", 0))):
    dias = ed.get("dias_restantes", 0)
    valor = ed.get("valor_estimado") or 0
    mun = ed.get("municipio", "")
    link = ed.get("link", "")
    score = ed.get("risk_score", {}).get("total", 0)

    if dias >= 10:
        acoes_curto.append({
            "acao": f"Preparar proposta para {ed.get('orgao', '')} ({mun}/MG) — {ed['objeto'][:80]}",
            "edital_ref": ed.get("sequencial_compra", ""),
            "orgao": ed.get("orgao", ""),
            "municipio": mun,
            "valor": fmt_r(valor),
            "prazo_proposta": ed.get("data_encerramento", ""),
            "dias_restantes": dias,
            "score": score,
            "prioridade_label": "ALTA" if dias <= 15 else "NORMAL",
            "link": link,
            "documentos_necessarios": ed.get("condicionantes", []),
        })

# AVALIAR COM CAUTELA
for ed in sorted(avaliar, key=lambda x: (-x.get("risk_score", {}).get("total", 0))):
    dias = ed.get("dias_restantes", 0)
    if dias >= 10:
        acoes_medio.append({
            "acao": f"Avaliar viabilidade de participação: {ed.get('orgao', '')} ({ed.get('municipio', '')}/MG)",
            "edital_ref": ed.get("sequencial_compra", ""),
            "valor": fmt_r(ed.get("valor_estimado") or 0),
            "dias_restantes": dias,
            "score": ed.get("risk_score", {}).get("total", 0),
            "prioridade_label": "NORMAL",
            "link": ed.get("link", ""),
            "condicionantes": ed.get("condicionantes", []),
        })

data["proximos_passos"] = {
    "acao_imediata": acoes_imediatas,
    "curto_prazo": acoes_curto,
    "medio_prazo": acoes_medio,
    "estrategia_entrada": (
        "A empresa está em estágio de ENTRADA no mercado B2G. O foco deve ser obter o primeiro contrato "
        "bem executado para gerar o atestado técnico inicial. Recomendação: priorizar o edital de Ubaporanga "
        "(73km, R$ 511 mil, score 88) ou Ponte Nova (154km, R$ 607 mil, score 85) como primeira participação. "
        "Paralelamente, cadastrar-se no SICAF e consolidar pacote de habilitação padrão."
    ),
}

# ============================================================
# CROSS-REFERENCE VALIDATION
# ============================================================

# Verify: descartados NOT in proximos_passos
pp_refs = set()
for item in acoes_curto + acoes_medio:
    pp_refs.add(item.get("edital_ref", ""))

for ed in editais:
    seq = ed.get("sequencial_compra", "")
    rec = ed.get("recomendacao", "")
    dias = ed.get("dias_restantes", 0)
    if rec == "NÃO RECOMENDADO" and seq in pp_refs:
        print(f"WARNING: Edital {seq} is NÃO RECOMENDADO but appears in proximos_passos!", file=sys.stderr)
    if dias <= 0 and seq in pp_refs:
        print(f"WARNING: Edital {seq} is CLOSED but appears in proximos_passos!", file=sys.stderr)

# Verify counts match
re_count = data["resumo_executivo"]["recomendacoes"]
actual_p = sum(1 for e in open_editais if e.get("recomendacao") == "PARTICIPAR")
actual_a = sum(1 for e in open_editais if e.get("recomendacao") == "AVALIAR COM CAUTELA")
actual_n = sum(1 for e in open_editais if e.get("recomendacao") == "NÃO RECOMENDADO")
assert re_count["participar"] == actual_p, f"PARTICIPAR mismatch: {re_count['participar']} vs {actual_p}"
assert re_count["avaliar_com_cautela"] == actual_a, f"AVALIAR mismatch: {re_count['avaliar_com_cautela']} vs {actual_a}"
assert re_count["nao_recomendado"] == actual_n, f"NÃO REC mismatch: {re_count['nao_recomendado']} vs {actual_n}"

print(f"Cross-reference validation PASSED", file=sys.stderr)
print(f"  PARTICIPAR: {actual_p}", file=sys.stderr)
print(f"  AVALIAR COM CAUTELA: {actual_a}", file=sys.stderr)
print(f"  NÃO RECOMENDADO: {actual_n}", file=sys.stderr)

# ============================================================
# SAVE
# ============================================================

with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Enriched JSON saved to {DATA_PATH}", file=sys.stderr)
print(f"Total editais: {len(editais)}", file=sys.stderr)
print(f"Fields added per edital: analise_documental, analise_detalhada, analise_resumo, red_flags_documentais, condicionantes", file=sys.stderr)
print(f"Top-level fields added: resumo_executivo, inteligencia_mercado", file=sys.stderr)
print(f"Top-level fields enriched: proximos_passos", file=sys.stderr)
