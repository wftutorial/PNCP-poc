#!/usr/bin/env python3
"""
Analyst enrichment script for FC CONSTRUCOES LTDA (33.750.637/0001-54)
Report date: 2026-03-17

Addresses WARNINGS:
1. HABILITACAO_UNIVERSAL_PARCIAL: 436/465 editais (94%) PARCIALMENTE_APTA
2. SICAF_MISSING: Dados SICAF indisponíveis
"""

import json
import os
from datetime import datetime

DATA_PATH = "D:/pncp-poc/docs/reports/data-33750637000154-2026-03-17.json"

with open(DATA_PATH, encoding="utf-8") as f:
    data = json.load(f)

editais = data["editais"]
empresa = data["empresa"]

# ── Company profile summary ──
CAPITAL = empresa["capital_social"]  # 550,000
SEDE = f"{empresa['cidade_sede']}/{empresa['uf_sede']}"  # FLORIANOPOLIS/SC
PORTE = empresa["porte"]  # MICRO EMPRESA
SIMPLES = empresa["simples_nacional"]  # True
HISTORICO_COUNT = len(empresa.get("historico_contratos", []))  # 6
SANCIONADA = empresa["sancoes"]["sancionada"]  # False

# Simples Nacional annual revenue cap
SIMPLES_TETO = 4_800_000

# ── Edital-level analysis ──
# Track recommendation counts for cross-referencing
rec_counts = {"PARTICIPAR": 0, "AVALIAR COM CAUTELA": 0, "NÃO RECOMENDADO": 0}
participar_list = []
avaliar_list = []

# Documental analysis results from PDF reading (Phase 2)
# Only 6 AVALIAR editais had downloadable documents
documental_analysis = {
    427: {
        "status": "ANALISADO",
        "orgao": "Prefeitura Municipal de Balneário Arroio do Silva",
        "objeto_detalhado": "Pavimentação asfáltica da Avenida Santa Catarina em dois trechos (Caçamba-Arpoador e divisa Balneário Gaivota-Lagoinha)",
        "regime": "Empreitada global (material e mão de obra)",
        "julgamento": "Menor preço por lote",
        "patrimonio_liquido": "10% do valor estimado (R$ 530.959)",
        "atestado_tecnico": "CAT com execução de obra similar, mínimo 50% dos quantitativos. Exige pavimentação asfáltica comprovada.",
        "participacao": "NÃO exclusiva ME/EPP (art. 10 Decreto 8.538/2015, art. 49 LC 123/2006 — justificativa no edital)",
        "garantia": "5 anos de garantia da execução da obra",
        "red_flags": [
            "Valor total R$ 5.3M pode ultrapassar teto do Simples Nacional (R$ 4.8M/ano)",
            "Concorrência presencial exige deslocamento até Balneário Arroio do Silva",
            "Atestado de 50% dos quantitativos pode ser difícil para micro empresa"
        ],
        "capital_ok": False,  # 550k < 530k -> OK technically, but tight
        "observacao": "Patrimônio líquido de 10% exige R$ 530.959 — capital social de R$ 550.000 atende marginalmente. Necessário confirmar balanço patrimonial atualizado."
    },
    392: {
        "status": "ANALISADO",
        "orgao": "Município de Chapecó",
        "objeto_detalhado": "Execução de pavimentação asfáltica de trechos das Rua Paulo Everaldo Flores e EMC 020",
        "regime": "Menor preço global",
        "julgamento": "Concorrência Eletrônica via Portal de Compras Públicas",
        "patrimonio_liquido": "Não especificado explicitamente no edital (padrão Lei 14.133: 10%)",
        "atestado_tecnico": "Exige documentação de habilitação padrão — certidões e atestados de capacidade técnica",
        "participacao": "Ampla concorrência",
        "garantia": "Garantia contratual de execução (art. 96, § 1° Lei 14.133/2021)",
        "red_flags": [
            "Valor R$ 5.09M ultrapassa teto do Simples Nacional",
            "Chapecó está a ~550km de Florianópolis — custo logístico elevado",
            "Ampla concorrência — concorrentes de maior porte participarão"
        ],
        "capital_ok": False,  # 10% of 5.09M = 509k, capital 550k marginal
        "observacao": "Patrimônio líquido exigido ~R$ 509.003 (10% padrão). Capital de R$ 550.000 atende marginalmente. Distância geográfica é fator limitante."
    },
    404: {
        "status": "ANALISADO",
        "orgao": "Município de Içara",
        "objeto_detalhado": "Construção de 43 unidades habitacionais (Programa Casa Catarina) em 4 lotes distribuídos por bairros de Içara/SC",
        "regime": "Menor preço por lote",
        "julgamento": "Concorrência Eletrônica via BNC",
        "patrimonio_liquido": "10% do valor estimado da contratação (R$ 498.558 por lote total)",
        "atestado_tecnico": "Atestado(s) ou certidão(ões) de obras similares certificados pelo CREA/CAU. Exige CAT de cercamento de campo de futebol (requisito incomum). Declaração de conhecimento do local.",
        "participacao": "Ampla concorrência",
        "garantia": "Garantia de proposta conforme art. 96 Lei 14.133",
        "red_flags": [
            "Valor total R$ 4.98M ultrapassa teto do Simples Nacional",
            "Obra dividida em 4 lotes — possível participar em lotes individuais (R$ 1.05M-1.5M por lote)",
            "Exigência de CAT específica de cercamento pode não estar no acervo da empresa"
        ],
        "capital_ok": True,  # If bidding per lot, capital is sufficient
        "observacao": "OPORTUNIDADE: Licitação por lotes permite participação parcial. Lotes individuais entre R$ 1.05M e R$ 1.5M cabem no perfil financeiro. Içara fica a ~190km de Florianópolis."
    },
    218: {
        "status": "ANALISADO",
        "orgao": "Município de Ibirama",
        "objeto_detalhado": "Fornecimento de material e mão de obra para pavimentação asfáltica da Estrada Geral Rafael (~3.350m), convênio com MAPA",
        "regime": "Empreitada por preço global",
        "julgamento": "Menor preço por item, Concorrência Eletrônica via Portal de Compras Públicas",
        "patrimonio_liquido": "10% do valor estimado (R$ 489.959)",
        "atestado_tecnico": "Registro no CREA/CAU. Atestado de vistoria técnica (opcional mas recomendada). Qualificação técnica com comprovação de serviços similares.",
        "participacao": "Ampla concorrência com tratamento favorecido para ME/EPP (LC 123/2006)",
        "garantia": "Garantia de proposta conforme art. 96 Lei 14.133",
        "red_flags": [
            "Valor R$ 4.9M ultrapassa teto do Simples Nacional",
            "Ibirama está a ~200km de Florianópolis",
            "Recurso vinculado a convênio federal (MAPA) — pode ter exigências adicionais de prestação de contas"
        ],
        "capital_ok": True,  # 550k > 489k
        "observacao": "Capital de R$ 550.000 atende o mínimo de 10% (R$ 489.959). Tratamento favorecido para ME/EPP é vantagem. Convênio federal pode exigir documentação adicional."
    },
    459: {
        "status": "ANALISADO",
        "orgao": "Município de Taió",
        "objeto_detalhado": "Construção de ponte em concreto armado sobre o Rio Itajaí do Oeste, entre comunidades do Ribeirão Pinheiro e Ribeirão do Salto",
        "regime": "Empreitada por preço global",
        "julgamento": "Menor preço global, Concorrência Eletrônica via licitar.digital",
        "patrimonio_liquido": "Não especificado (padrão 10% = R$ 439.706)",
        "atestado_tecnico": "Atestado de capacidade técnica com CAT registrada no CREA, mínimo 40% do objeto. Exige experiência em estruturas de concreto armado em obras de infraestrutura viária, incluindo pontes.",
        "participacao": "Ampla concorrência",
        "garantia": "5% do valor do contrato como garantia de execução",
        "red_flags": [
            "CRÍTICO: Exige CAT em pontes de concreto armado — muito específico",
            "Valor R$ 4.4M pode impactar teto do Simples",
            "Obra de ponte é alta complexidade técnica para micro empresa",
            "Taió está a ~260km de Florianópolis"
        ],
        "capital_ok": True,  # 550k > 439k
        "observacao": "ALERTA: Exigência de CAT em pontes é muito específica. Empresa tem histórico em reformas e construções, mas NÃO em pontes. Risco alto de inabilitação técnica."
    },
}

# Process each edital
for idx, edital in enumerate(editais):
    rec = edital.get("recomendacao", "")
    valor = edital.get("valor_estimado", 0) or 0
    dias = edital.get("dias_restantes")
    risk_total = edital.get("risk_score", {}).get("total", 0)
    hab_analysis = edital.get("habilitacao_analysis", {})
    hab_status = hab_analysis.get("status", "DESCONHECIDO")
    distancia = edital.get("distancia", {})
    dist_km = distancia.get("km") if isinstance(distancia, dict) else None
    roi = edital.get("roi_potential", {})
    cronograma = edital.get("cronograma", [])
    competitivo = edital.get("competitive_intel", {})
    objeto = edital.get("objeto", "")
    municipio = edital.get("municipio", "")
    modalidade = edital.get("modalidade", "")

    # ── Skip expired/encerrado editais ──
    if dias is not None and dias <= 0:
        # Keep NÃO RECOMENDADO for expired
        if rec != "NÃO RECOMENDADO":
            edital["recomendacao"] = "NÃO RECOMENDADO"
            edital["justificativa"] = f"Edital encerrado ({dias} dia(s) restante(s)). Prazo insuficiente para participação."
        rec_counts["NÃO RECOMENDADO"] = rec_counts.get("NÃO RECOMENDADO", 0) + 1
        edital["analise_resumo"] = "Edital fora do prazo — sem possibilidade de participação."
        continue

    # ── Build justificativa enrichment ──
    # Address HABILITACAO_UNIVERSAL_PARCIAL warning
    hab_dims = hab_analysis.get("dimensions", [])
    hab_issues = [d for d in hab_dims if d.get("status") not in ("OK",)]
    capital_ok = any(d.get("dimension") == "Capital Mínimo" and d.get("status") == "OK" for d in hab_dims)

    # Check SIMPLES impact
    simples_warning = ""
    if SIMPLES and valor > SIMPLES_TETO:
        simples_warning = f"ALERTA TRIBUTÁRIO: contrato de R$ {valor:,.0f} pode ultrapassar teto do Simples Nacional (R$ 4,8M/ano). "

    # Distance factor
    dist_text = ""
    if dist_km is not None:
        if dist_km <= 50:
            dist_text = f"Proximidade favorável ({dist_km:.0f}km de {municipio or 'sede'}). "
        elif dist_km <= 150:
            dist_text = f"Distância moderada ({dist_km:.0f}km). "
        elif dist_km <= 300:
            dist_text = f"Distância significativa ({dist_km:.0f}km) — considerar custos logísticos. "
        else:
            dist_text = f"Distância elevada ({dist_km:.0f}km) — custo logístico impacta viabilidade. "

    # ROI text
    roi_text = ""
    if roi:
        roi_min = roi.get("roi_if_win_min", roi.get("roi_min", 0))
        roi_max = roi.get("roi_if_win_max", roi.get("roi_max", 0))
        if roi_min and roi_max:
            roi_text = f"Resultado Potencial: R$ {roi_min:,.0f} — R$ {roi_max:,.0f}. "

    # ── Determine recommendation adjustments ──
    # For PARTICIPAR: validate and potentially downgrade
    if rec == "PARTICIPAR":
        downgrade_reasons = []

        # Check SIMPLES teto
        if SIMPLES and valor > SIMPLES_TETO:
            downgrade_reasons.append("Valor ultrapassa teto do Simples Nacional")

        # Check habilitacao PARCIALMENTE_APTA
        if hab_status == "PARCIALMENTE_APTA":
            # For PARTICIPAR with moderate values, keep if capital OK and risk >= 60
            if not capital_ok and valor > CAPITAL * 10:
                downgrade_reasons.append("Capital social insuficiente para o valor do edital")
            # If many hab issues, downgrade
            critical_issues = [d for d in hab_issues if d.get("status") in ("ALERTA", "NAO_ATENDE")]
            if len(critical_issues) >= 2:
                downgrade_reasons.append(f"{len(critical_issues)} requisitos de habilitação não atendidos")

        if downgrade_reasons and risk_total < 65:
            edital["recomendacao"] = "AVALIAR COM CAUTELA"
            rec = "AVALIAR COM CAUTELA"

        # Build enriched justificativa
        justificativa_parts = []
        if capital_ok:
            cap_min = valor * 0.1
            justificativa_parts.append(f"Capital social R$ {CAPITAL:,.0f} atende mínimo de R$ {cap_min:,.0f}")
        justificativa_parts.append(dist_text.strip())
        if dias and dias > 0:
            justificativa_parts.append(f"Prazo adequado: {dias} dia(s) para preparação")
        if HISTORICO_COUNT > 0:
            justificativa_parts.append(f"Acervo técnico inferido: {HISTORICO_COUNT} contratos similares no histórico")
        if simples_warning:
            justificativa_parts.append(simples_warning.strip())
        justificativa_parts.append(roi_text.strip())

        edital["justificativa"] = ". ".join(p for p in justificativa_parts if p) + "."

    elif rec == "AVALIAR COM CAUTELA":
        # Build enriched justificativa for AVALIAR
        justificativa_parts = []

        if risk_total >= 50:
            justificativa_parts.append(f"Pontuação de risco moderada ({risk_total}/100)")
        else:
            justificativa_parts.append(f"Pontuação de risco baixa ({risk_total}/100) — requer atenção redobrada")

        if capital_ok:
            justificativa_parts.append(f"Capital social R$ {CAPITAL:,.0f} atende requisito financeiro")
        elif valor > CAPITAL * 10:
            justificativa_parts.append(f"ALERTA: Capital social R$ {CAPITAL:,.0f} pode ser insuficiente para edital de R$ {valor:,.0f}")

        if hab_status == "PARCIALMENTE_APTA":
            issue_list = [d.get("dimension", "?") for d in hab_issues[:3]]
            justificativa_parts.append(f"Habilitação parcial — verificar: {', '.join(issue_list)}")

        justificativa_parts.append(dist_text.strip())

        if simples_warning:
            justificativa_parts.append(simples_warning.strip())

        justificativa_parts.append(roi_text.strip())

        if dias and dias <= 10:
            justificativa_parts.append(f"Prazo curto: apenas {dias} dia(s) restante(s)")

        edital["justificativa"] = ". ".join(p for p in justificativa_parts if p) + "."

    elif "NÃO RECOMENDADO" in rec:
        # Ensure NÃO RECOMENDADO has factual justificativa
        justificativa_parts = []

        veto_reasons = edital.get("risk_score", {}).get("veto_reasons", [])
        threshold = edital.get("risk_score", {}).get("threshold_applied", "")

        if veto_reasons:
            justificativa_parts.append(f"Veto: {', '.join(veto_reasons)}")
        elif risk_total < 30:
            justificativa_parts.append(f"Pontuação de risco insuficiente ({risk_total}/100)")

        if threshold:
            threshold_labels = {
                "prazo_critico": "Prazo crítico para preparação",
                "capital_insuficiente": "Capital social insuficiente",
                "distancia_excessiva": "Distância excessiva da sede",
                "hab_inapta": "Habilitação técnica insuficiente",
            }
            justificativa_parts.append(threshold_labels.get(threshold, f"Limite aplicado: {threshold}"))

        if valor > CAPITAL * 15:
            justificativa_parts.append(f"Valor R$ {valor:,.0f} muito acima da capacidade financeira (capital R$ {CAPITAL:,.0f})")

        if dist_km and dist_km > 400:
            justificativa_parts.append(f"Distância elevada ({dist_km:.0f}km)")

        if dias is not None and dias <= 3:
            justificativa_parts.append(f"Prazo insuficiente ({dias} dia(s))")

        if simples_warning:
            justificativa_parts.append(simples_warning.strip())

        edital["justificativa"] = ". ".join(p for p in justificativa_parts if p) + "." if justificativa_parts else edital.get("justificativa", "Dados insuficientes para análise detalhada.")

    # ── Documental analysis (Phase 2) ──
    if idx in documental_analysis:
        da = documental_analysis[idx]
        edital["analise_documental"] = {
            "status": da["status"],
            "orgao": da["orgao"],
            "objeto_detalhado": da["objeto_detalhado"],
            "regime_execucao": da["regime"],
            "criterio_julgamento": da["julgamento"],
            "patrimonio_liquido_exigido": da["patrimonio_liquido"],
            "atestado_tecnico_exigido": da["atestado_tecnico"],
            "tipo_participacao": da["participacao"],
            "garantia": da["garantia"],
            "red_flags": da["red_flags"],
            "observacao_analista": da["observacao"]
        }
        edital["red_flags_documentais"] = da["red_flags"]

        # Downgrade recommendation if documental analysis reveals issues
        if not da["capital_ok"] and rec == "AVALIAR COM CAUTELA" and valor > SIMPLES_TETO:
            # Keep AVALIAR but add stronger warning
            edital["condicionantes"] = [
                "Verificar balanço patrimonial atualizado para atender patrimônio líquido mínimo",
                f"Avaliar impacto tributário: contrato de R$ {valor:,.0f} vs teto Simples Nacional R$ 4,8M",
                "Confirmar acervo técnico (CAT) compatível com exigências do edital"
            ]
        elif idx == 459 and rec == "AVALIAR COM CAUTELA":
            # Ponte edital — very specific CAT requirement
            edital["recomendacao"] = "NÃO RECOMENDADO"
            edital["justificativa"] = f"Exigência de CAT em pontes de concreto armado não corresponde ao acervo técnico da empresa (histórico em reformas e construções civis). Risco alto de inabilitação técnica. {dist_text}"
            rec = "NÃO RECOMENDADO"
            edital["condicionantes"] = []
    else:
        # No document available
        if edital.get("documentos") and len(edital.get("documentos", [])) > 0:
            edital["analise_documental"] = {
                "status": "NÃO ANALISADO",
                "motivo": "Análise documental priorizada para editais de maior valor com recomendação PARTICIPAR ou AVALIAR COM CAUTELA"
            }
        else:
            edital["analise_documental"] = {
                "status": "INDISPONÍVEL",
                "motivo": "Documentos do edital não disponíveis para download no Portal Nacional de Contratações Públicas"
            }

    # ── Análise detalhada ──
    analise_parts = []

    # Object compatibility
    obj_compat = edital.get("object_compatibility", {})
    if obj_compat:
        compat_level = obj_compat.get("compatibility", "DESCONHECIDA")
        analise_parts.append(f"Compatibilidade com perfil da empresa: {compat_level}")

    # Habilitacao
    if hab_status == "PARCIALMENTE_APTA":
        issues_text = ", ".join(d.get("dimension", "?") + " (" + d.get("status", "?") + ")" for d in hab_issues[:4])
        analise_parts.append(f"Habilitação parcial — itens pendentes: {issues_text}")
        analise_parts.append("SICAF não consultado — regularidade fiscal deve ser verificada diretamente")

    # Risk breakdown
    rs = edital.get("risk_score", {})
    if rs:
        analise_parts.append(
            f"Composição do risco: Habilitação {rs.get('habilitacao', 0)}/100, "
            f"Financeiro {rs.get('financeiro', 0)}/100, "
            f"Geográfico {rs.get('geografico', 0)}/100, "
            f"Prazo {rs.get('prazo', 0)}/100, "
            f"Competitivo {rs.get('competitivo', 0)}/100"
        )

    # Competitive context
    comp = edital.get("competitive_analysis", {})
    if comp and comp.get("competition_level"):
        analise_parts.append(f"Nível de concorrência: {comp['competition_level']}")

    edital["analise_detalhada"] = ". ".join(analise_parts) + "." if analise_parts else "Dados insuficientes para análise detalhada."

    # ── Condicionantes (if not already set) ──
    if "condicionantes" not in edital:
        conds = []
        if hab_status == "PARCIALMENTE_APTA" and rec in ("PARTICIPAR", "AVALIAR COM CAUTELA"):
            conds.append("Verificar regularidade fiscal (SICAF indisponível)")
            if any(d.get("dimension") == "Regularidade Fiscal" for d in hab_issues):
                conds.append("Obter certidões negativas: FGTS, INSS, tributos federais/estaduais/municipais")
        if SIMPLES and valor > SIMPLES_TETO and rec in ("PARTICIPAR", "AVALIAR COM CAUTELA"):
            conds.append(f"Avaliar impacto tributário: contrato R$ {valor:,.0f} vs teto Simples Nacional")
        if rec == "PARTICIPAR" and dias and dias <= 10:
            conds.append(f"Prazo curto ({dias} dias) — iniciar preparação imediatamente")
        edital["condicionantes"] = conds

    # ── Análise resumo ──
    if rec == "PARTICIPAR":
        edital["analise_resumo"] = (
            f"Edital recomendado para participação. {objeto[:100]}. "
            f"Valor estimado R$ {valor:,.0f}. {dist_text}"
            f"{roi_text}"
            f"Prazo: {dias} dia(s) restante(s)."
        )
    elif rec == "AVALIAR COM CAUTELA":
        edital["analise_resumo"] = (
            f"Edital requer avaliação cautelosa. {objeto[:100]}. "
            f"Valor estimado R$ {valor:,.0f}. Risco: {risk_total}/100. "
            f"{dist_text}"
            f"{'Habilitação parcial — verificar requisitos. ' if hab_status == 'PARCIALMENTE_APTA' else ''}"
        )
    else:
        edital["analise_resumo"] = (
            f"Edital não recomendado. "
            f"{'Prazo expirado. ' if dias is not None and dias <= 0 else ''}"
            f"Risco: {risk_total}/100. "
            f"Valor R$ {valor:,.0f}."
        )

    # Count final recommendations
    final_rec = edital["recomendacao"]
    if "NÃO RECOMENDADO" in final_rec:
        rec_counts["NÃO RECOMENDADO"] = rec_counts.get("NÃO RECOMENDADO", 0) + 1
    elif final_rec in rec_counts:
        rec_counts[final_rec] = rec_counts.get(final_rec, 0) + 1

    if final_rec == "PARTICIPAR":
        participar_list.append({
            "index": idx,
            "objeto": objeto[:120],
            "valor": valor,
            "municipio": municipio,
            "dias_restantes": dias,
            "risk_total": risk_total
        })
    elif final_rec == "AVALIAR COM CAUTELA":
        avaliar_list.append({
            "index": idx,
            "objeto": objeto[:120],
            "valor": valor,
            "municipio": municipio,
            "dias_restantes": dias,
            "risk_total": risk_total
        })

# ── Resumo Executivo ──
total_valor_participar = sum(e.get("valor_estimado", 0) or 0 for e in editais if e.get("recomendacao") == "PARTICIPAR")
total_valor_avaliar = sum(e.get("valor_estimado", 0) or 0 for e in editais if e.get("recomendacao") == "AVALIAR COM CAUTELA")
total_valor_nr = sum(e.get("valor_estimado", 0) or 0 for e in editais if "NÃO RECOMENDADO" in (e.get("recomendacao") or ""))

# Recount after adjustments
final_participar = sum(1 for e in editais if e.get("recomendacao") == "PARTICIPAR")
final_avaliar = sum(1 for e in editais if e.get("recomendacao") == "AVALIAR COM CAUTELA")
final_nr = sum(1 for e in editais if "NÃO RECOMENDADO" in (e.get("recomendacao") or ""))

# Average distance for PARTICIPAR
part_dists = []
for e in editais:
    if e.get("recomendacao") == "PARTICIPAR":
        d = e.get("distancia", {})
        if isinstance(d, dict) and d.get("km") is not None:
            part_dists.append(d["km"])
avg_dist_participar = sum(part_dists) / len(part_dists) if part_dists else None

data["resumo_executivo"] = {
    "data_analise": "2026-03-18",
    "empresa": empresa["razao_social"],
    "cnpj": empresa["cnpj"],
    "setor_analisado": data.get("setor", "Engenharia e Construção Civil"),
    "uf_analisada": "SC",
    "total_editais_analisados": len(editais),
    "recomendacoes": {
        "PARTICIPAR": final_participar,
        "AVALIAR COM CAUTELA": final_avaliar,
        "NÃO RECOMENDADO": final_nr
    },
    "valor_total_participar": total_valor_participar,
    "valor_total_avaliar": total_valor_avaliar,
    "valor_total_nao_recomendado": total_valor_nr,
    "perfil_empresa": {
        "porte": PORTE,
        "capital_social": CAPITAL,
        "simples_nacional": SIMPLES,
        "sede": SEDE,
        "historico_contratos": HISTORICO_COUNT,
        "sancionada": SANCIONADA,
        "maturidade": data.get("maturity_profile", {}).get("profile", "REGIONAL")
    },
    "alertas_gerais": [
        f"HABILITAÇÃO PARCIAL: {sum(1 for e in editais if e.get('habilitacao_analysis',{}).get('status') == 'PARCIALMENTE_APTA')}/{len(editais)} editais com habilitação PARCIALMENTE APTA — empresa pode não ter acervo técnico completo. Regularidade fiscal (SICAF) não verificada.",
        f"SIMPLES NACIONAL: Empresa optante pelo Simples Nacional com teto de R$ 4,8M/ano. Contratos acima desse valor exigem planejamento tributário.",
        "SICAF INDISPONÍVEL: Dados do SICAF não foram consultados. A regularidade fiscal deve ser verificada diretamente junto aos órgãos competentes antes de cada participação.",
        f"MICRO EMPRESA: Porte limita participação em editais de alto valor (acima de R$ {CAPITAL * 10:,.0f}). Priorizar editais compatíveis com capacidade financeira."
    ],
    "tese_estrategica": data.get("strategic_thesis", {}).get("thesis", "EXPANDIR"),
    "confianca_tese": data.get("strategic_thesis", {}).get("confidence", "alta"),
    "racional_tese": data.get("strategic_thesis", {}).get("rationale", ""),
    "distancia_media_participar_km": round(avg_dist_participar, 1) if avg_dist_participar is not None else None,
    "documentos_analisados": len(documental_analysis),
    "fontes_dados": [
        "Receita Federal (dados cadastrais e CNAE)",
        "Portal da Transparência (sanções e contratos federais)",
        "Portal Nacional de Contratações Públicas (editais e documentos)",
        "Portal de Compras Públicas (editais eletrônicos)",
        "Querido Diário (menções em diários oficiais)",
        "Instituto Brasileiro de Geografia e Estatística (dados municipais)"
    ]
}

# ── Inteligência de Mercado ──

# Modalidade distribution
from collections import Counter
modal_part = Counter(e.get("modalidade") for e in editais if e.get("recomendacao") == "PARTICIPAR")
modal_aval = Counter(e.get("modalidade") for e in editais if e.get("recomendacao") == "AVALIAR COM CAUTELA")
modal_all = Counter(e.get("modalidade") for e in editais)

# Value ranges
valores_part = [e.get("valor_estimado", 0) or 0 for e in editais if e.get("recomendacao") == "PARTICIPAR"]
valores_aval = [e.get("valor_estimado", 0) or 0 for e in editais if e.get("recomendacao") == "AVALIAR COM CAUTELA"]

# Municipality concentration
muni_part = Counter(e.get("municipio", "?") for e in editais if e.get("recomendacao") == "PARTICIPAR")
muni_aval = Counter(e.get("municipio", "?") for e in editais if e.get("recomendacao") == "AVALIAR COM CAUTELA")

# Price benchmarks
price_bench = data.get("_metadata", {}).get("sources", {}).get("price_benchmarks", {})
market_hhi_src = data.get("_metadata", {}).get("sources", {}).get("market_hhi", {})

data["inteligencia_mercado"] = {
    "panorama_setorial": {
        "editais_abertos": len([e for e in editais if (e.get("dias_restantes") or 0) > 0]),
        "valor_total_mercado": sum(e.get("valor_estimado", 0) or 0 for e in editais),
        "valor_medio_edital": sum(e.get("valor_estimado", 0) or 0 for e in editais) / len(editais) if editais else 0,
        "concentracao_uf": "SC (100% — busca restrita ao estado sede)",
        "municipios_com_oportunidades": len(set(e.get("municipio") for e in editais if e.get("municipio"))),
        "natureza_predominante": "OBRA (100%)",
        "fonte_recursos": "Majoritariamente recursos próprios municipais, com parcela de convênios federais e estaduais (Programa Casa Catarina, MAPA)"
    },
    "tendencias": {
        "modalidades_comuns": {k: v for k, v in modal_all.most_common(5)},
        "valor_medio_participar": sum(valores_part) / len(valores_part) if valores_part else 0,
        "valor_medio_avaliar": sum(valores_aval) / len(valores_aval) if valores_aval else 0,
        "faixa_ideal_empresa": "R$ 100.000 a R$ 1.500.000 (compatível com capital social e porte)",
        "tendencia_mercado": data.get("strategic_thesis", {}).get("signals", {}).get("trend", "EXPANSAO"),
        "crescimento_anualizado": f"{data.get('strategic_thesis', {}).get('signals', {}).get('growth_rate_pct', 0):.0f}%",
        "desconto_medio_mercado": f"{data.get('strategic_thesis', {}).get('signals', {}).get('avg_discount_pct', 0):.1f}%",
        "indice_concentracao_hhi": data.get("strategic_thesis", {}).get("signals", {}).get("hhi_value", 0),
        "interpretacao_hhi": "Mercado altamente competitivo (HHI < 0,15) — muitos fornecedores, sem dominância"
    },
    "vantagens_competitivas": [
        "Sede em Florianópolis — posição central no litoral catarinense com acesso rápido a vários municípios",
        "Empresa ativa desde 2019 com 6 contratos federais no histórico — experiência comprovada",
        "Micro empresa optante pelo Simples Nacional — tratamento favorecido na LC 123/2006",
        "Sem sanções em nenhum cadastro (CEIS, CNEP, CEPIM, CEAF) — idoneidade comprovada",
        "CNAE principal 4120-4/00 (Construção de edifícios) + 20 CNAEs secundários — ampla cobertura de atividades",
        "Acervo técnico em reformas, construções e obras de engenharia em instituições federais (UFSC, IFSC)"
    ],
    "oportunidades_nicho": [
        {
            "nicho": "Unidades habitacionais (Programa Casa Catarina)",
            "descricao": "Vários editais de construção de unidades habitacionais (30-43 unidades) com lotes entre R$ 1M-1.5M — compatíveis com porte",
            "editais_relevantes": sum(1 for e in editais if "habitacion" in (e.get("objeto", "").lower()) and e.get("recomendacao") in ("PARTICIPAR", "AVALIAR COM CAUTELA")),
            "acao": "Focar em lotes individuais para manter valor dentro da capacidade"
        },
        {
            "nicho": "Pavimentação asfáltica",
            "descricao": "Alta demanda por pavimentação em municípios catarinenses, valores variados",
            "editais_relevantes": sum(1 for e in editais if "paviment" in (e.get("objeto", "").lower()) and e.get("recomendacao") in ("PARTICIPAR", "AVALIAR COM CAUTELA")),
            "acao": "Priorizar editais até R$ 1.5M com tratamento ME/EPP"
        },
        {
            "nicho": "Materiais de construção (Pregão)",
            "descricao": "Pregões eletrônicos para fornecimento de materiais — menor complexidade de habilitação",
            "editais_relevantes": sum(1 for e in editais if "material" in (e.get("objeto", "").lower()) and "Pregão" in (e.get("modalidade", "")) and e.get("recomendacao") in ("PARTICIPAR", "AVALIAR COM CAUTELA")),
            "acao": "Participar em pregões de materiais como entrada em novos municípios"
        },
        {
            "nicho": "Reformas e manutenção",
            "descricao": "Editais de menor valor (R$ 100k-500k) para reformas e manutenções — perfil forte no histórico da empresa",
            "editais_relevantes": sum(1 for e in editais if ("reforma" in (e.get("objeto", "").lower()) or "manuten" in (e.get("objeto", "").lower())) and e.get("recomendacao") in ("PARTICIPAR", "AVALIAR COM CAUTELA")),
            "acao": "Focar em contratos de reforma — acervo técnico mais forte nesta área"
        }
    ],
    "tese_estrategica": {
        "posicionamento": "EXPANDIR",
        "racional": (
            "Mercado catarinense em expansão (crescimento de 100% anualizado) com baixa concentração de fornecedores (HHI 0,0074). "
            "Empresa tem posição geográfica favorável e acervo técnico em reformas e construções. "
            "Estratégia recomendada: expandir participação em editais de até R$ 1,5M compatíveis com o porte, "
            "priorizando lotes individuais em licitações de maior valor e aproveitando tratamento favorecido da LC 123/2006."
        ),
        "restricoes": [
            "Teto do Simples Nacional (R$ 4,8M/ano) limita contratos de grande valor",
            "Capital social de R$ 550.000 restringe participação em editais acima de R$ 5,5M",
            "Acervo técnico concentrado em reformas — expandir para pavimentação e habitação",
            "SICAF não verificado — regularizar cadastro para agilizar habilitações"
        ]
    },
    "orgaos_mais_ativos": dict(Counter(
        e.get("orgao", e.get("cnpj_orgao", "?"))
        for e in editais
        if e.get("recomendacao") in ("PARTICIPAR", "AVALIAR COM CAUTELA")
    ).most_common(10))
}

# ── Próximos Passos ──
# Only include PARTICIPAR and conditioned AVALIAR editais
proximos = []

# Sort PARTICIPAR by urgency (days remaining)
participar_editais = [(i, e) for i, e in enumerate(editais) if e.get("recomendacao") == "PARTICIPAR"]
participar_editais.sort(key=lambda x: x[1].get("dias_restantes", 999))

for idx, e in participar_editais[:15]:
    dias = e.get("dias_restantes", 0)
    valor = e.get("valor_estimado", 0) or 0
    municipio = e.get("municipio", "?")
    objeto_short = e.get("objeto", "")[:100]
    cron = e.get("cronograma", [])

    passo = {
        "prioridade": "ALTA" if dias <= 10 else "MEDIA",
        "acao": f"Preparar documentação para: {objeto_short}",
        "edital_index": idx,
        "municipio": municipio,
        "valor": valor,
        "dias_restantes": dias,
        "recomendacao": "PARTICIPAR"
    }

    # Add cronograma milestones
    if cron:
        marcos = []
        for c in cron[:3]:
            marcos.append(f"{c.get('marco', '?')}: {c.get('data', '?')} ({c.get('dias_ate_marco', '?')} dias)")
        passo["cronograma"] = marcos

    # Add condicionantes
    conds = e.get("condicionantes", [])
    if conds:
        passo["condicionantes"] = conds

    proximos.append(passo)

# Add top AVALIAR COM CAUTELA with high values and reasonable risk
top_avaliar = [(i, e) for i, e in enumerate(editais)
               if e.get("recomendacao") == "AVALIAR COM CAUTELA" and (e.get("risk_score", {}).get("total", 0)) >= 50]
top_avaliar.sort(key=lambda x: x[1].get("valor_estimado", 0) or 0, reverse=True)

for idx, e in top_avaliar[:10]:
    dias = e.get("dias_restantes", 0)
    valor = e.get("valor_estimado", 0) or 0
    municipio = e.get("municipio", "?")
    objeto_short = e.get("objeto", "")[:100]

    passo = {
        "prioridade": "MEDIA",
        "acao": f"Avaliar viabilidade: {objeto_short}",
        "edital_index": idx,
        "municipio": municipio,
        "valor": valor,
        "dias_restantes": dias,
        "recomendacao": "AVALIAR COM CAUTELA",
        "condicionantes": e.get("condicionantes", ["Verificar requisitos de habilitação no edital completo"])
    }
    proximos.append(passo)

# Add general strategic actions
proximos.append({
    "prioridade": "ALTA",
    "acao": "Regularizar cadastro SICAF — fundamental para agilizar habilitações em todas as licitações",
    "tipo": "ADMINISTRATIVO"
})
proximos.append({
    "prioridade": "ALTA",
    "acao": "Obter certidões negativas atualizadas: CND federal, estadual, municipal, FGTS, INSS",
    "tipo": "ADMINISTRATIVO"
})
proximos.append({
    "prioridade": "MEDIA",
    "acao": "Consultar contador sobre impacto tributário: planejamento para contratos que somem acima de R$ 4,8M/ano (teto Simples Nacional)",
    "tipo": "TRIBUTARIO"
})
proximos.append({
    "prioridade": "MEDIA",
    "acao": "Atualizar acervo técnico no CREA — registrar CATs dos 6 contratos federais realizados para fortalecer habilitação técnica",
    "tipo": "TECNICO"
})

data["proximos_passos"] = proximos

# ── Cross-reference validation ──
# 1. No DESCARTADO/NÃO RECOMENDADO in proximos_passos
nr_indices = {i for i, e in enumerate(editais) if "NÃO RECOMENDADO" in (e.get("recomendacao") or "")}
data["proximos_passos"] = [p for p in data["proximos_passos"] if p.get("edital_index") not in nr_indices or "edital_index" not in p]

# 2. Verify counts match
actual_participar = sum(1 for e in editais if e.get("recomendacao") == "PARTICIPAR")
actual_avaliar = sum(1 for e in editais if e.get("recomendacao") == "AVALIAR COM CAUTELA")
actual_nr = sum(1 for e in editais if "NÃO RECOMENDADO" in (e.get("recomendacao") or ""))

data["resumo_executivo"]["recomendacoes"]["PARTICIPAR"] = actual_participar
data["resumo_executivo"]["recomendacoes"]["AVALIAR COM CAUTELA"] = actual_avaliar
data["resumo_executivo"]["recomendacoes"]["NÃO RECOMENDADO"] = actual_nr
data["resumo_executivo"]["valor_total_participar"] = sum(e.get("valor_estimado", 0) or 0 for e in editais if e.get("recomendacao") == "PARTICIPAR")
data["resumo_executivo"]["valor_total_avaliar"] = sum(e.get("valor_estimado", 0) or 0 for e in editais if e.get("recomendacao") == "AVALIAR COM CAUTELA")
data["resumo_executivo"]["valor_total_nao_recomendado"] = sum(e.get("valor_estimado", 0) or 0 for e in editais if "NÃO RECOMENDADO" in (e.get("recomendacao") or ""))

# 3. Verify PARTICIPAR conditioned editais have conditions in proximos_passos
for p in data["proximos_passos"]:
    eidx = p.get("edital_index")
    if eidx is not None and eidx < len(editais):
        e = editais[eidx]
        if e.get("condicionantes") and p.get("recomendacao") == "PARTICIPAR":
            if "condicionantes" not in p:
                p["condicionantes"] = e["condicionantes"]

# ── Save ──
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"JSON atualizado com sucesso: {DATA_PATH}")
print(f"  PARTICIPAR: {actual_participar} (R$ {data['resumo_executivo']['valor_total_participar']:,.0f})")
print(f"  AVALIAR COM CAUTELA: {actual_avaliar} (R$ {data['resumo_executivo']['valor_total_avaliar']:,.0f})")
print(f"  NÃO RECOMENDADO: {actual_nr} (R$ {data['resumo_executivo']['valor_total_nao_recomendado']:,.0f})")
print(f"  Documentos analisados: {len(documental_analysis)}")
print(f"  Próximos passos: {len(data['proximos_passos'])}")
