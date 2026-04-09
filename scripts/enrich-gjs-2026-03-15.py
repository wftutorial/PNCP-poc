#!/usr/bin/env python3
"""
Enrich GJS Construções report data with recommendations and justifications.
CNPJ: 09.225.035/0001-01 | Date: 2026-03-15
"""
import json
from pathlib import Path

INPUT = Path("D:/pncp-poc/docs/reports/data-09225035000101-2026-03-15.json")

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

editais = data["editais"]

# ── Top 10 manual overrides (from Phase 2 analysis) ──────────────────────

MANUAL = {
    # PARTICIPAR (3)
    81: {
        "recomendacao": "PARTICIPAR",
        "justificativa": (
            "Obra simples de bloquetamento em Fama/MG (701km), valor R$127K compatível com capital. "
            "Probabilidade 16,4% — maior entre os editais analisados. "
            "Verificar exigência de visita técnica (prazo entre 09 e 27/03). "
            "Concorrência baixa esperada para obra de pequeno porte em município pequeno."
        ),
    },
    121: {
        "recomendacao": "PARTICIPAR",
        "justificativa": (
            "Habitação popular em Natércia/MG (728km) com recurso CAIXA, R$3,9M. "
            "Score 83, probabilidade 9,1%. Prazo de execução longo (11 meses) permite planejamento. "
            "Empresa tem CNAE compatível e experiência em construção. "
            "Critério menor preço favorece competitividade."
        ),
    },
    93: {
        "recomendacao": "PARTICIPAR",
        "justificativa": (
            "Habitação em Floreal/SP (R$1,6M) com critério Técnica+Preço, que valoriza "
            "histórico e qualificação técnica — vantagem para empresa estabelecida com 1000 contratos. "
            "Probabilidade 3,6% reflete competição, mas critério qualitativo compensa."
        ),
    },
    # AVALIAR COM CAUTELA (3)
    116: {
        "recomendacao": "AVALIAR COM CAUTELA",
        "justificativa": (
            "Construção de 25 casas FNHIS em Guaimbé/SP (R$3,4M), score 84 — maior score entre candidatos. "
            "Contratação integrada exige projeto + execução, o que aumenta complexidade e risco. "
            "Avaliar capacidade de elaboração de projetos ou subcontratar projetista. "
            "Prazo 53 dias para submissão permite preparação adequada."
        ),
    },
    80: {
        "recomendacao": "AVALIAR COM CAUTELA",
        "justificativa": (
            "Habitação Programa Casa Catarina em Joaçaba/SC (R$3,4M), score 82. "
            "Perfil da licitação atende requisitos técnicos, porém distância até SC "
            "exige avaliação de custos logísticos e mobilização de equipe. "
            "Programa estadual pode ter exigências específicas de cadastro em SC."
        ),
    },
    76: {
        "recomendacao": "AVALIAR COM CAUTELA",
        "justificativa": (
            "Ampliação PSF em Porto Murtinho/MS (R$563K), score 78, probabilidade 11,1%. "
            "Tecnicamente compatível — obra de saúde pública de menor porte. "
            "Porém, localização extremamente remota (fronteira com Paraguai) eleva custos "
            "de mobilização e logística de materiais. Avaliar viabilidade econômica."
        ),
    },
    # NÃO RECOMENDADO (4)
    83: {
        "recomendacao": "NÃO RECOMENDADO",
        "justificativa": (
            "Irani/SC — Usina de asfalto a frio. Edital exige fornecedor dentro de raio de 50km "
            "do município, o que elimina empresa sediada em MG. "
            "Critério geográfico restritivo é inabilitante."
        ),
    },
    # Pinhalzinho has two entries: 104 (vetoed, pista) and 123/124 (centro poliesportivo)
    123: {
        "recomendacao": "NÃO RECOMENDADO",
        "justificativa": (
            "Pinhalzinho/SC (R$5,3M) — Construção de centro poliesportivo. "
            "Edital exige acervo técnico em pré-fabricado e cobertura metálica, "
            "especialidades não comprovadas no histórico da empresa. "
            "Risco de inabilitação por falta de atestados técnicos específicos."
        ),
    },
    124: {
        "recomendacao": "NÃO RECOMENDADO",
        "justificativa": (
            "Duplicata do edital Pinhalzinho/SC (centro poliesportivo) em outra fonte. "
            "Mesmas restrições: exige acervo em pré-fabricado e cobertura metálica."
        ),
    },
    78: {
        "recomendacao": "NÃO RECOMENDADO",
        "justificativa": (
            "Piratini/RS (R$155K) — Serviço de elaboração de projetos de engenharia, não obra. "
            "Empresa focada em execução de obras, não em serviços técnicos de projeto. "
            "Distância de 2.350km torna inviável para valor baixo."
        ),
    },
    107: {
        "recomendacao": "NÃO RECOMENDADO",
        "justificativa": (
            "Iguatama/MG — Concessão de saneamento (água e esgoto) por 35 anos. "
            "Modelo de negócio completamente diferente de construção civil. "
            "Exige capacidade operacional contínua, capital massivo e expertise em gestão "
            "de serviços públicos. Incompatível com perfil da empresa."
        ),
    },
}

# Also mark Pinhalzinho vetoed one
MANUAL[104] = {
    "recomendacao": "NÃO RECOMENDADO",
    "justificativa": (
        "Pinhalzinho/SC (R$17,9M) — Pista de atletismo. "
        "Vetado pelo sistema: valor excede capacidade financeira. "
        "Exige acervo em pista de atletismo e infraestrutura esportiva especializada."
    ),
}

# ── Automated rules for remaining 167 editais ────────────────────────────

def classify_edital(idx: int, ed: dict) -> tuple[str, str]:
    """Return (recomendacao, justificativa) based on calculated fields."""

    rs = ed.get("risk_score", {})
    if not isinstance(rs, dict):
        return "NÃO RECOMENDADO", "Dados de risco insuficientes para análise."

    score = rs.get("total", 0)
    vetoed = rs.get("vetoed", False)
    veto_reasons = rs.get("veto_reasons", [])

    hab = ed.get("habilitacao_analysis", {})
    hab_status = hab.get("status", "") if isinstance(hab, dict) else ""
    hab_gaps = hab.get("gaps", []) if isinstance(hab, dict) else []

    dias = ed.get("dias_restantes")

    dist = ed.get("distancia", {})
    km = dist.get("km", 0) if isinstance(dist, dict) else 0

    valor = ed.get("valor_estimado", 0) or 0

    obj_compat = ed.get("object_compatibility", {})
    compat = obj_compat.get("compatibility", "") if isinstance(obj_compat, dict) else ""
    compat_score = obj_compat.get("score", 0) if isinstance(obj_compat, dict) else 0

    municipio = ed.get("municipio", "")
    uf = ed.get("uf", "")
    modalidade = ed.get("modalidade", "")
    objeto = ed.get("objeto", "")[:120]

    win_prob = ed.get("win_probability", {})
    prob = win_prob.get("probability", 0) if isinstance(win_prob, dict) else 0

    strategic = ed.get("strategic_category", "")

    reasons = []

    # ── VETO checks (NÃO RECOMENDADO) ──
    if vetoed:
        vr = "; ".join(veto_reasons) if veto_reasons else "Critério eliminatório identificado"
        return "NÃO RECOMENDADO", f"Vetado: {vr}."

    if hab_status == "INAPTA":
        gap_text = "; ".join(hab_gaps[:2]) if hab_gaps else "Requisitos de habilitação não atendidos"
        return "NÃO RECOMENDADO", f"Empresa inapta para este edital: {gap_text}."

    if dias is not None and dias <= 0:
        return "NÃO RECOMENDADO", f"Prazo encerrado (encerramento já ocorreu). Não é possível participar."

    # Logistics rule: distant + low value
    if km > 1500 and 0 < valor < 500000:
        return (
            "NÃO RECOMENDADO",
            f"Distância de {km:.0f}km com valor de apenas R${valor:,.0f} — "
            f"custo logístico de mobilização supera margem esperada."
            .replace(",", "X").replace(".", ",").replace("X", ".")
        )

    # Very low score
    if score < 30:
        reasons_low = []
        if km > 1000:
            reasons_low.append(f"distância elevada ({km:.0f}km)")
        if dias is not None and dias < 5:
            reasons_low.append(f"prazo crítico ({dias} dias)")
        if compat == "BAIXA":
            reasons_low.append("baixa compatibilidade com objeto")
        detail = "; ".join(reasons_low) if reasons_low else "Score geral muito baixo indica múltiplos fatores de risco"
        return "NÃO RECOMENDADO", f"Score {score}/100 — {detail}."

    # ── PARTICIPAR checks (score >= 70, good conditions) ──
    if score >= 70 and hab_status != "INAPTA" and (dias is None or dias > 5):
        # But check for cautionary factors
        caution_factors = []

        if km > 1200:
            caution_factors.append(f"distância significativa ({km:.0f}km)")
        if compat == "BAIXA" or compat_score < 0.3:
            caution_factors.append("compatibilidade baixa com objeto")
        if dias is not None and dias < 10:
            caution_factors.append(f"prazo curto ({dias} dias restantes)")

        if len(caution_factors) >= 2:
            detail = "; ".join(caution_factors)
            return (
                "AVALIAR COM CAUTELA",
                f"Score favorável ({score}/100) porém com ressalvas: {detail}. "
                f"Avaliar custo-benefício antes de investir na proposta."
            )

        # Strong PARTICIPAR
        positives = []
        if compat in ("ALTA", "MEDIA") or compat_score >= 0.5:
            positives.append("objeto compatível com perfil da empresa")
        if km < 800:
            positives.append(f"localização acessível ({km:.0f}km)")
        elif km < 1200:
            positives.append(f"distância gerenciável ({km:.0f}km)")
        if valor > 100000:
            val_fmt = f"R${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            positives.append(f"valor expressivo ({val_fmt})")
        if prob > 0.05:
            positives.append(f"probabilidade estimada de {prob*100:.1f}%".replace(".", ","))
        if dias is not None and dias > 30:
            positives.append(f"prazo confortável ({dias} dias)")

        # Check if it's a "PARTICIPAR with caveats"
        if hab_status == "PARCIALMENTE_APTA" and hab_gaps:
            gap_short = hab_gaps[0][:80] if hab_gaps else ""
            detail = "; ".join(positives[:3]) if positives else f"Score {score}/100"
            return (
                "PARTICIPAR",
                f"{detail}. "
                f"Atenção: verificar pendência de habilitação ({gap_short})."
            )

        detail = "; ".join(positives[:3]) if positives else f"Score {score}/100 indica boa aderência"
        return "PARTICIPAR", f"{detail}."

    # ── AVALIAR COM CAUTELA (middle ground) ──
    if score >= 50 or hab_status == "PARCIALMENTE_APTA":
        factors = []
        if score >= 50:
            factors.append(f"score moderado ({score}/100)")
        if hab_status == "PARCIALMENTE_APTA":
            factors.append("habilitação parcial — verificar pendências")
        if km > 1000:
            factors.append(f"distância de {km:.0f}km requer planejamento logístico")
        if dias is not None and dias < 15:
            factors.append(f"prazo limitado ({dias} dias)")
        if compat in ("MEDIA",) or (0.3 <= compat_score < 0.7):
            factors.append("compatibilidade moderada com objeto")

        detail = "; ".join(factors[:3]) if factors else "Análise aprofundada necessária"
        return "AVALIAR COM CAUTELA", f"{detail}."

    # ── Fallback: NÃO RECOMENDADO ──
    return (
        "NÃO RECOMENDADO",
        f"Score {score}/100 insuficiente. Múltiplos fatores de risco identificados."
    )


# ── Apply recommendations ─────────────────────────────────────────────────

stats = {"PARTICIPAR": 0, "AVALIAR COM CAUTELA": 0, "NÃO RECOMENDADO": 0}

for i, ed in enumerate(editais):
    if i in MANUAL:
        ed["recomendacao"] = MANUAL[i]["recomendacao"]
        ed["justificativa"] = MANUAL[i]["justificativa"]
    else:
        rec, justif = classify_edital(i, ed)
        ed["recomendacao"] = rec
        ed["justificativa"] = justif

    # Normalize recommendation key for stats
    rec_upper = ed["recomendacao"].upper()
    if "PARTICIPAR" in rec_upper:
        stats["PARTICIPAR"] += 1
    elif "AVALIAR" in rec_upper or "CAUTELA" in rec_upper:
        stats["AVALIAR COM CAUTELA"] += 1
    else:
        stats["NÃO RECOMENDADO"] += 1


# ── Add recomendacao_geral (executive summary) ────────────────────────────

data["recomendacao_geral"] = (
    f"De 177 editais analisados, {stats['PARTICIPAR']} apresentam condições favoráveis para participação imediata, "
    f"{stats['AVALIAR COM CAUTELA']} merecem avaliação aprofundada e {stats['NÃO RECOMENDADO']} não são recomendados. "
    "ALERTA ESTRATÉGICO: Apesar do CNAE principal ser Construção Civil (4120-4/00), "
    "o histórico de 1000 contratos revela atuação dominante em Saúde/Hospitalar (30,4%), "
    "Limpeza (14,5%) e Alimentação (13,9%). Esta divergência setorial deve ser considerada "
    "na seleção de editais — priorizar obras de menor complexidade técnica onde a experiência "
    "diversificada da empresa pode ser vantajosa. "
    "ALERTA HABILITAÇÃO: 93% dos editais classificados como 'Parcialmente Apta' — "
    "a empresa deve providenciar registro SICAF (nível I não cadastrado) e confirmar "
    "acervo técnico junto ao CREA antes de qualquer submissão."
)

# ── Save enriched JSON ────────────────────────────────────────────────────

with open(INPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"OK - Enriched {len(editais)} editais")
print(f"  PARTICIPAR: {stats['PARTICIPAR']}")
print(f"  AVALIAR COM CAUTELA: {stats['AVALIAR COM CAUTELA']}")
print(f"  NÃO RECOMENDADO: {stats['NÃO RECOMENDADO']}")
print(f"  Saved to {INPUT}")
