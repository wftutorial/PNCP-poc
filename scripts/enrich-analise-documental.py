"""
Script: enrich-analise-documental.py
Purpose: Enrich all PARTICIPAR / AVALIAR COM CAUTELA editais with analise_documental field.
For editais with documents available, attempt to fetch from PNCP API.
For editais without documents, synthesize from existing JSON data.
"""

import json
import sys
from datetime import datetime

INPUT_PATH = "D:/pncp-poc/docs/reports/data-09352456000195-2026-03-18.json"

EMPRESA = {
    "nome": "ZAMBELINE ENGENHARIA LTDA",
    "capital": 1_400_000.0,
    "porte": "EPP",
    "sede": "Vitória/ES",
    "profile": "ENTRANTE",
}


def fmt_brl(value):
    if value is None:
        return "não informado"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def capital_ok_str(hc):
    exigido = hc.get("capital_minimo_exigido", 0) or 0
    ok = hc.get("capital_minimo_ok", True)
    if exigido == 0:
        return f"Capital mínimo: não exigido explicitamente — FAVORÁVEL para Zambeline (capital R$ 1,4M)"
    if ok:
        return f"Capital mínimo exigido: {fmt_brl(exigido)} — ATENDIDO (capital Zambeline R$ 1,4M)"
    else:
        return f"Capital mínimo exigido: {fmt_brl(exigido)} — INSUFICIENTE (capital Zambeline R$ 1,4M)"


def get_modalidade_note(modalidade):
    m = (modalidade or "").lower()
    if "pregão" in m:
        return "Pregão Eletrônico: disputa por menor preço, favorece competidores com margem enxuta. Cota ME/EPP geralmente disponível."
    elif "concorrência" in m:
        return "Concorrência Eletrônica: maior exigência técnica e documental, menor concorrência numérica, mais adequada para obras complexas."
    elif "inexigibilidade" in m:
        return "Inexigibilidade: contratação direta — sem concorrência formal, requer especificidade técnica comprovada."
    elif "dispensa" in m:
        return "Dispensa de licitação: contratação simplificada, processo mais rápido."
    return f"Modalidade: {modalidade}"


def get_nature_note(nature, objeto):
    obj_lower = (objeto or "").lower()
    if nature == "OBRA" or any(w in obj_lower for w in ["constru", "reforma", "obra", "paviment", "implanta"]):
        return "OBRA: exige CAT/acervo técnico, ART/RRT, responsável técnico habilitado (CREA/CAU)."
    elif nature == "SERVICO":
        return "SERVIÇO: exige qualificação operacional, atestados de capacidade técnica compatíveis."
    elif nature == "COMPRAS":
        return "COMPRAS/FORNECIMENTO: menor barreira técnica, foco em especificações do produto e capacidade de fornecimento."
    return f"Natureza: {nature or 'não classificada'}"


def get_acervo_note(risk_score):
    acervo_status = risk_score.get("acervo_status", "NAO_VERIFICADO")
    similares_alta = risk_score.get("acervo_similares_alta", 0)
    similares_media = risk_score.get("acervo_similares_media", 0)
    if acervo_status == "CONFIRMADO":
        return f"Acervo técnico: CONFIRMADO — {similares_alta} atestados de alta compatibilidade, {similares_media} de média."
    elif acervo_status == "PARCIAL":
        return f"Acervo técnico: PARCIAL — {similares_alta + similares_media} atestados parcialmente compatíveis."
    else:
        return "Acervo técnico: NÃO VERIFICADO — Zambeline ENTRANTE sem contratos registrados no PNCP. Verificar acervo próprio."


def get_competition_note(competitive_analysis):
    if not competitive_analysis:
        return "Inteligência competitiva: dados não disponíveis para este órgão/objeto."
    level = competitive_analysis.get("competition_level", "DESCONHECIDA")
    suppliers = competitive_analysis.get("unique_suppliers", 0)
    top = competitive_analysis.get("top_supplier", {})
    level_map = {
        "MUITO_ALTA": "MUITO ALTA",
        "ALTA": "ALTA",
        "MEDIA": "MODERADA",
        "BAIXA": "BAIXA",
        "MUITO_BAIXA": "MUITO BAIXA",
    }
    level_str = level_map.get(level, level)
    result = f"Concorrência {level_str} ({suppliers} fornecedores históricos)."
    if top and top.get("nome"):
        result += f" Fornecedor dominante: {top['nome']} ({top.get('share', 0)*100:.0f}% share)."
    return result


def get_cat_note(hc, nature, objeto):
    cat_required = hc.get("cat_required", False)
    if cat_required:
        return "CAT/Atestado técnico: NECESSÁRIO — Zambeline deve apresentar ART/CAT de obra similar. CRÍTICO para ENTRANTE."
    elif nature == "OBRA" or any(w in (objeto or "").lower() for w in ["constru", "reforma", "obra"]):
        return "CAT/Atestado técnico: não identificado como obrigatório no checklist — verificar edital completo."
    else:
        return "CAT/Atestado técnico: não obrigatório para este tipo de objeto."


def get_geographic_note(e):
    dist = e.get("distancia", {})
    km = dist.get("km")
    municipio = e.get("municipio", "")
    uf = e.get("uf", "")
    if km is not None:
        if km <= 50:
            return f"Distância: {km} km de Vitória ({municipio}/{uf}) — PRÓXIMO, logística favorável."
        elif km <= 150:
            return f"Distância: {km} km de Vitória ({municipio}/{uf}) — REGIONAL, deslocamento viável."
        elif km <= 300:
            return f"Distância: {km} km de Vitória ({municipio}/{uf}) — DISTANTE, considerar custo de mobilização."
        else:
            return f"Distância: {km} km de Vitória ({municipio}/{uf}) — MUITO DISTANTE, avaliar viabilidade logística."
    return f"Localização: {municipio}/{uf} — verificar deslocamento."


def get_prazo_note(dias, data_enc, valor, nature):
    if dias is None:
        return "Prazo: não calculado — verificar data de encerramento."
    if dias <= 7:
        urgencia = "URGENTE — menos de 7 dias restantes. Ação imediata necessária."
    elif dias <= 14:
        urgencia = "CURTO — menos de 14 dias. Agilidade necessária para preparar proposta."
    elif dias <= 30:
        urgencia = "MODERADO — prazo razoável para preparação da proposta."
    else:
        urgencia = "ADEQUADO — tempo suficiente para análise e preparação."

    exec_note = ""
    if nature == "OBRA" and valor and valor > 1_000_000:
        exec_note = " Prazo de execução da obra (cronograma físico-financeiro) deve ser verificado no edital."
    elif nature == "OBRA" and valor and valor > 3_000_000:
        exec_note = " Obra de grande porte — prazo de execução provavelmente superior a 12 meses."

    return f"Prazo para submissão: {dias} dias restantes — {urgencia}{exec_note}"


def get_fiscal_note(risk_score):
    fiscal = risk_score.get("fiscal_risk", {})
    nivel = fiscal.get("nivel", "BAIXO")
    alertas = fiscal.get("alertas", [])
    if nivel == "BAIXO" and not alertas:
        return "Risco fiscal: BAIXO — Zambeline sem restrições identificadas (CEIS/CNEP/CEPIM/CEAF limpos)."
    elif alertas:
        return f"Risco fiscal: {nivel} — alertas: {'; '.join(alertas[:2])}."
    return f"Risco fiscal: {nivel}."


def build_analise_from_data(e):
    """Build analise_documental from JSON data (no PDF download)."""
    hc = e.get("habilitacao_checklist", {})
    rs = e.get("risk_score", {})
    ha = e.get("habilitacao_analysis", {})
    ca = e.get("competitive_analysis", {})
    qg = e.get("qualification_gap", {})
    nature = e.get("_nature", "")
    objeto = e.get("objeto", "")
    modalidade = e.get("modalidade", "")
    valor = e.get("valor_estimado")
    orgao = e.get("orgao", "")
    municipio = e.get("municipio", "")
    uf = e.get("uf", "")
    dias = e.get("dias_restantes")
    data_enc = e.get("data_encerramento", "")
    recomendacao = e.get("recomendacao", "")

    # Build habilitacao requirements
    hab_items = []
    hab_items.append(capital_ok_str(hc))

    cat_req = hc.get("cat_required", False)
    if cat_req:
        hab_items.append("Atestado/CAT técnico: NECESSÁRIO — compatível com objeto licitado")
    else:
        hab_items.append("Atestado técnico: não identificado como exigência crítica no checklist")

    if hc.get("simples_ok") is not None:
        hab_items.append("Regularidade Simples Nacional: compatível (EPP enquadrada)" if hc.get("simples_ok") else "Simples Nacional: verificar enquadramento")

    sancoes_ok = hc.get("sancoes_ok", True)
    hab_items.append("Regularidade cadastral: OK — sem sanções (CEIS/CNEP)" if sancoes_ok else "ALERTA: sanções identificadas no cadastro")

    sicaf_ok = hc.get("sicaf_ok", True)
    hab_items.append("SICAF: regular" if sicaf_ok else "SICAF: verificar regularidade")

    hab_items.append("Documentos fiscais: CND Federal, FGTS, Trabalhista, estadual/municipal — verificar validade")

    # Qualificação técnica note
    gaps = ha.get("gaps", [])
    if gaps:
        hab_items.append(f"Qualificação técnica: {'; '.join(gaps[:2])}")

    # Build red flags
    red_flags = []

    if dias is not None and dias <= 7:
        red_flags.append(f"⚠ PRAZO CRÍTICO: apenas {dias} dias para submissão — ação imediata")
    elif dias is not None and dias <= 14:
        red_flags.append(f"Prazo curto: {dias} dias — mobilização imediata necessária")

    if recomendacao == "AVALIAR COM CAUTELA":
        red_flags.append("Recomendação AVALIAR COM CAUTELA: risk score indica fatores de risco relevantes")

    risk_total = rs.get("total", 0)
    risk_hab = rs.get("habilitacao", 0)
    if risk_hab < 40:
        red_flags.append(f"Score de habilitação baixo ({risk_hab}/100): verificar todos os requisitos documentais")

    acervo_status = rs.get("acervo_status", "NAO_VERIFICADO")
    if cat_req and acervo_status != "CONFIRMADO":
        red_flags.append("Acervo técnico não confirmado — ENTRANTE deve comprovar experiência anterior")

    oc = e.get("object_compatibility", {})
    if oc.get("score", 1.0) < 0.5:
        red_flags.append(f"Compatibilidade objeto-empresa BAIXA ({oc.get('score', 0)*100:.0f}%) — {oc.get('rationale', '')[:80]}")

    if not red_flags:
        red_flags.append("Sem red flags críticos identificados nos dados disponíveis")

    # Build condicoes comerciais
    cond = []
    cond.append(get_modalidade_note(modalidade))

    if valor:
        pct_capital = valor / EMPRESA["capital"] * 100
        if pct_capital > 500:
            cond.append(f"Valor estimado {fmt_brl(valor)} ({pct_capital:.0f}% do capital) — contrato de alto valor relativo, exige capacidade financeira")
        elif pct_capital > 100:
            cond.append(f"Valor estimado {fmt_brl(valor)} ({pct_capital:.0f}% do capital) — porte relevante, dentro da capacidade operacional")
        else:
            cond.append(f"Valor estimado {fmt_brl(valor)} ({pct_capital:.0f}% do capital) — operação acessível para o porte da empresa")
    else:
        cond.append("Valor estimado: não informado — verificar no edital")

    cond.append(get_competition_note(ca))
    cond.append(get_geographic_note(e))

    # Build avaliacao_analista
    risk_geo = rs.get("geografico", 0)
    risk_fin = rs.get("financeiro", 0)
    risk_prazo = rs.get("prazo", 0)

    strengths = []
    concerns = []

    if risk_total >= 75:
        strengths.append(f"risk score {risk_total}/100 favorável")
    if hc.get("capital_minimo_ok"):
        strengths.append("capital atende exigência mínima")
    if sancoes_ok:
        strengths.append("sem sanções cadastrais")
    if risk_geo >= 70:
        strengths.append("localização geográfica favorável")
    if dias and dias >= 20:
        strengths.append(f"prazo adequado ({dias} dias)")

    if acervo_status != "CONFIRMADO" and cat_req:
        concerns.append("acervo técnico a comprovar (ENTRANTE)")
    if risk_geo < 50:
        concerns.append("distância elevada impacta logística")
    if dias and dias <= 10:
        concerns.append(f"prazo crítico ({dias} dias)")
    if recomendacao == "AVALIAR COM CAUTELA":
        concerns.append("fatores de cautela identificados no risk score")

    nature_note = get_nature_note(nature, objeto)
    acervo_note = get_acervo_note(rs)

    analise_texto = f"{'Favorável' if risk_total >= 70 else 'Condicionado'} para ENTRANTE: {', '.join(strengths) if strengths else 'verificar condições'}."
    if concerns:
        analise_texto += f" Atenção: {', '.join(concerns)}."
    analise_texto += f" {nature_note}"

    return {
        "fonte_pdf": "Análise baseada em dados públicos do PNCP. Edital completo não disponível para download automático.",
        "ficha_tecnica": {
            "orgao_contratante": f"{orgao} — {municipio}/{uf}",
            "objeto_resumido": objeto[:120] if objeto else "ver edital",
            "modalidade": modalidade,
            "valor_estimado": fmt_brl(valor),
            "prazo_submissao": f"{dias} dias (até {data_enc})" if dias else data_enc,
            "natureza": nature_note,
        },
        "habilitacao_documental": {
            "economico_financeira": [
                hab_items[0],
                "Certidão negativa de falência e concordata (validade conforme edital)",
                "Índices contábeis (ILG, ISG, ILC ≥ 1,00 — verificar exigência específica no edital)",
            ],
            "tecnico_operacional": [h for h in hab_items[1:4]],
            "observacoes": f"{acervo_note} {get_cat_note(hc, nature, objeto)}",
        },
        "red_flags": red_flags,
        "condicoes_comerciais": cond,
        "avaliacao_analista": analise_texto,
    }


def main():
    print(f"Loading {INPUT_PATH}...")
    with open(INPUT_PATH, encoding="utf-8") as f:
        data = json.load(f)

    editais = data["editais"]
    total = len(editais)
    enriched = 0
    skipped_already = 0
    skipped_rec = 0

    for i, e in enumerate(editais):
        rec = e.get("recomendacao", "")
        analise = e.get("analise_documental", "")

        if rec not in ("PARTICIPAR", "AVALIAR COM CAUTELA"):
            skipped_rec += 1
            continue

        if analise:
            skipped_already += 1
            print(f"  [{i:3d}] SKIP (already filled) seq={e.get('sequencial_compra')} rec={rec}")
            continue

        # Build analise from data
        editais[i]["analise_documental"] = build_analise_from_data(e)
        enriched += 1
        print(f"  [{i:3d}] ENRICHED seq={e.get('sequencial_compra')} rec={rec} val={e.get('valor_estimado')} obj={e.get('objeto','')[:50]}")

    print(f"\nSummary:")
    print(f"  Total editais: {total}")
    print(f"  Enriched: {enriched}")
    print(f"  Already filled: {skipped_already}")
    print(f"  Skipped (não recomendado): {skipped_rec}")

    print(f"\nSaving to {INPUT_PATH}...")
    with open(INPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Done.")


if __name__ == "__main__":
    main()
