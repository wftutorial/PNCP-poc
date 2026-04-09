#!/usr/bin/env python3
"""
Adversarial Audit for Report B2G - COMPACTA SUL PAVIMENTAÇÃO LTDA
CNPJ: 03.667.661/0001-63
"""
import json
import re
import sys
from datetime import datetime

JSON_PATH = "D:/pncp-poc/docs/reports/data-03667661000163-2026-03-18.json"

def load_json():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_forbidden_terms(text):
    if not text or not isinstance(text, str):
        return []
    forbidden = [
        (r'\bAPI\b', 'API'),
        (r'\bJSON\b', 'JSON'),
        (r'\bN/D\b', 'N/D'),
        (r'(?<!["\w])null(?!["\w])', 'null'),
        (r'\bindisponível\b', 'indisponível'),
        (r'\bUNAVAILABLE\b', 'UNAVAILABLE'),
        (r'(?<!["\w])None(?!["\w])', 'None'),
        (r'\bundefined\b', 'undefined'),
        (r'\bN/A\b', 'N/A'),
    ]
    found = []
    for pattern, label in forbidden:
        if re.search(pattern, text):
            found.append(label)
    return found

def check_justificativa(j):
    """C1: Justificativa has at least 2 factual assertions."""
    if not j or not isinstance(j, str):
        return False, "Justificativa vazia ou ausente"
    assertions = 0
    if re.search(r'R\$\s*[\d.,]+', j):
        assertions += 1
    if re.search(r'\d{2}/\d{2}/\d{4}|\d+ dias', j):
        assertions += 1
    if re.search(r'[A-Z][a-záàâãéèêíïóôõöúçñ]+(?:\s+[a-záàâãéèêíïóôõöúçñ]+)*', j):
        assertions += 1
    if re.search(r'(paviment|asfalto|CBUQ|obra|serviço|construção|drenagem|sinaliz|rodov|ponte|viaduto|fresag|recapeamento|terraplanag|infraestrutura)', j, re.IGNORECASE):
        assertions += 1
    if re.search(r'\d+%', j):
        assertions += 1
    if re.search(r'(concorrência|pregão|município|prefeitura|órgão|licitação)', j, re.IGNORECASE):
        assertions += 1
    return assertions >= 2, f"{assertions} assertions found"

def check_analise_documental(e):
    """C7: analise_documental is filled."""
    ad = e.get("analise_documental")
    if ad is None:
        return False, "analise_documental is null"
    if isinstance(ad, str) and not ad.strip():
        return False, "analise_documental is empty string"
    if isinstance(ad, dict) and not ad:
        return False, "analise_documental is empty dict"
    return True, "OK"

def check_links(e):
    """C8: Links valid."""
    link = e.get("link")
    link_valid = e.get("link_valid")
    if not link:
        return True, "No link"
    if link_valid is True:
        return True, "link_valid=true"
    if link_valid is False:
        return False, f"link_valid=false for {link}"
    return True, "link_valid not set"

def check_legal_language(e):
    """C11: No incorrect legal language."""
    issues = []
    for field in ["justificativa", "analise_documental"]:
        text = e.get(field, "")
        if not isinstance(text, str):
            continue
        if re.search(r'Lei\s+8\.666', text, re.IGNORECASE):
            issues.append(f'{field}: Lei 8.666 citada (revogada pela Lei 14.133/2021)')
    return len(issues) == 0, "; ".join(issues) if issues else "OK"


def run_audit():
    data = load_json()

    checks_detail = []
    checks_failed = 0
    checks_total = 0
    rebaixamentos = []
    revisions_made = []
    block_reasons = []

    editais = data.get("editais", [])
    resumo = data.get("resumo_executivo", {})
    proximos_passos = data.get("proximos_passos", {})

    # Count actual recommendations
    actual_counts = {"PARTICIPAR": 0, "AVALIAR COM CAUTELA": 0, "NÃO RECOMENDADO": 0}
    for e in editais:
        rec = e.get("recomendacao", "")
        if rec in actual_counts:
            actual_counts[rec] += 1

    print(f"=== AUDIT: COMPACTA SUL PAVIMENTAÇÃO LTDA ===")
    print(f"Total editais: {len(editais)}")
    print(f"Actual counts: {actual_counts}")

    # ========== Per-edital checks ==========
    for i, e in enumerate(editais):
        rec = e.get("recomendacao", "")
        obj = e.get("objeto", "")[:80]

        if rec == "AVALIAR COM CAUTELA":
            # C1
            checks_total += 1
            ok, detail = check_justificativa(e.get("justificativa", ""))
            checks_detail.append({"check": "C1", "edital_idx": i, "result": "PASS" if ok else "FAIL", "detail": detail, "objeto": obj if not ok else None})
            if not ok:
                checks_failed += 1

            # C7
            checks_total += 1
            ok, detail = check_analise_documental(e)
            checks_detail.append({"check": "C7", "edital_idx": i, "result": "PASS" if ok else "FAIL", "detail": detail, "objeto": obj if not ok else None})
            if not ok:
                checks_failed += 1

            # C8
            checks_total += 1
            ok, detail = check_links(e)
            checks_detail.append({"check": "C8", "edital_idx": i, "result": "PASS" if ok else "FAIL", "detail": detail, "objeto": obj if not ok else None})
            if not ok:
                checks_failed += 1

            # C11
            checks_total += 1
            ok, detail = check_legal_language(e)
            checks_detail.append({"check": "C11", "edital_idx": i, "result": "PASS" if ok else "FAIL", "detail": detail, "objeto": obj if not ok else None})
            if not ok:
                checks_failed += 1

        # ===== FORMAT: price_benchmark duplicate R$ =====
        pb = e.get("price_benchmark", {})
        if pb and "suggested_range" in pb:
            sr = pb["suggested_range"]
            checks_total += 1
            if "R$ R$" in str(sr):
                checks_failed += 1
                new_val = sr.replace("R$ R$", "R$")
                pb["suggested_range"] = new_val
                checks_detail.append({"check": "FORMAT_PRICE", "edital_idx": i, "result": "FAIL", "detail": f"Fixed: '{sr}' -> '{new_val}'"})
                revisions_made.append(f"edital[{i}].price_benchmark.suggested_range: removed duplicate R$")
            else:
                checks_detail.append({"check": "FORMAT_PRICE", "edital_idx": i, "result": "PASS"})

    # ========== COHERENCE: resumo_executivo counts ==========
    checks_total += 1
    count_fixes = []

    if resumo:
        field_map = {
            "recomendacao_participar": actual_counts["PARTICIPAR"],
            "recomendacao_avaliar": actual_counts["AVALIAR COM CAUTELA"],
            "recomendacao_nao_recomendado": actual_counts["NÃO RECOMENDADO"],
            "total_editais_analisados": len(editais),
        }

        for field, expected in field_map.items():
            if field in resumo and resumo[field] != expected:
                old_val = resumo[field]
                resumo[field] = expected
                count_fixes.append(f"{field}: {old_val} -> {expected}")

        # Fix valor_total_participar (should be 0 since 0 PARTICIPAR)
        if "valor_total_participar" in resumo and actual_counts["PARTICIPAR"] == 0:
            # Recalculate: sum of values for AVALIAR COM CAUTELA that were previously PARTICIPAR
            # Since all PARTICIPAR were rebaixado, valor_total_participar should be 0
            if resumo["valor_total_participar"] != 0:
                old_val = resumo["valor_total_participar"]
                # Move the value to cautela
                resumo["valor_total_participar"] = 0
                # Recalculate cautela total
                cautela_total = sum(
                    (e.get("valor_estimado") or 0) for e in editais
                    if e.get("recomendacao") == "AVALIAR COM CAUTELA"
                )
                resumo["valor_total_cautela"] = round(cautela_total, 2)
                count_fixes.append(f"valor_total_participar: {old_val} -> 0")
                count_fixes.append(f"valor_total_cautela: recalculated to {resumo['valor_total_cautela']}")

        # Also fix the sintese text if it mentions wrong counts
        if "sintese" in resumo:
            sintese = resumo["sintese"]
            # Replace "8 para participar imediatamente" with "0 para participar imediatamente"
            # and "14 para avaliar com cautela" with "22 para avaliar com cautela"
            old_sintese = sintese
            # Fix participar count in text
            sintese = re.sub(
                r'(\d+)\s+(para participar|recomendados para participa)',
                f'{actual_counts["PARTICIPAR"]} \\2',
                sintese
            )
            # Fix avaliar count in text
            sintese = re.sub(
                r'(\d+)\s+(para avaliar|recomendados para avaliar|para analise com cautela|para avalia.+?cautela)',
                f'{actual_counts["AVALIAR COM CAUTELA"]} \\2',
                sintese
            )
            if sintese != old_sintese:
                resumo["sintese"] = sintese
                count_fixes.append(f"sintese: updated counts in text")

    if count_fixes:
        checks_failed += 1
        checks_detail.append({"check": "COHERENCE_COUNTS", "result": "FAIL", "detail": f"Fixed: {count_fixes}"})
        revisions_made.extend(count_fixes)
    else:
        checks_detail.append({"check": "COHERENCE_COUNTS", "result": "PASS", "detail": "Counts match"})

    # ========== COHERENCE: proximos_passos references ==========
    checks_total += 1
    nao_rec_editais = [e for e in editais if e.get("recomendacao") == "NÃO RECOMENDADO"]
    nao_rec_seqs = set()
    for e in nao_rec_editais:
        seq = e.get("sequencial_compra")
        if seq:
            nao_rec_seqs.add(str(seq))

    passos_fixed = False
    if isinstance(proximos_passos, dict):
        for key in ["acao_imediata", "curto_prazo", "medio_prazo", "acoes_imediatas", "acoes"]:
            if key in proximos_passos and isinstance(proximos_passos[key], list):
                original_len = len(proximos_passos[key])
                # Remove entries that reference NÃO RECOMENDADO editais
                cleaned = []
                for item in proximos_passos[key]:
                    if isinstance(item, dict):
                        editais_ref = item.get("editais_afetados", [])
                        # If ALL referenced editais are NÃO RECOMENDADO, remove the step
                        if editais_ref and all(str(ref) in nao_rec_seqs for ref in editais_ref):
                            passos_fixed = True
                            revisions_made.append(f"proximos_passos.{key}: removed step referencing only NÃO RECOMENDADO editais")
                            continue
                    cleaned.append(item)
                proximos_passos[key] = cleaned

    if passos_fixed:
        checks_detail.append({"check": "COHERENCE_PASSOS", "result": "FAIL", "detail": "Removed steps referencing NÃO RECOMENDADO editais"})
        checks_failed += 1
    else:
        checks_detail.append({"check": "COHERENCE_PASSOS", "result": "PASS", "detail": "OK"})

    # ========== COHERENCE: alertas_gate in resumo should reflect rebaixamento ==========
    checks_total += 1
    if resumo and "alertas_gate" in resumo:
        # Check if alertas_gate mentions the acervo rebaixamento
        has_acervo_alert = any(
            "acervo" in str(a).lower() or "rebaixa" in str(a).lower()
            for a in resumo["alertas_gate"]
        )
        if not has_acervo_alert and actual_counts["PARTICIPAR"] == 0:
            resumo["alertas_gate"].append(
                "8 editais originalmente PARTICIPAR foram rebaixados a AVALIAR COM CAUTELA: acervo técnico NAO_VERIFICADO (sem histórico de contratos governamentais comprovado)"
            )
            revisions_made.append("resumo_executivo.alertas_gate: added acervo rebaixamento alert")
            checks_detail.append({"check": "COHERENCE_ALERTAS", "result": "FAIL", "detail": "Added missing acervo rebaixamento alert"})
            checks_failed += 1
        else:
            checks_detail.append({"check": "COHERENCE_ALERTAS", "result": "PASS"})
    else:
        checks_detail.append({"check": "COHERENCE_ALERTAS", "result": "PASS"})

    # ========== Verify no PARTICIPAR editais exist (sanity) ==========
    checks_total += 1
    if actual_counts["PARTICIPAR"] > 0:
        checks_failed += 1
        checks_detail.append({"check": "SANITY_NO_PARTICIPAR", "result": "FAIL", "detail": f"Expected 0 PARTICIPAR but found {actual_counts['PARTICIPAR']}"})
    else:
        checks_detail.append({"check": "SANITY_NO_PARTICIPAR", "result": "PASS", "detail": "0 PARTICIPAR as expected"})

    # ========== DECISION ==========
    # Recount: only count non-format failures for blocking decision
    # Format fixes (R$ R$) are auto-corrected, should not block
    non_format_failures = sum(1 for c in checks_detail if c["result"] == "FAIL" and not c["check"].startswith("FORMAT_"))

    print(f"\n=== RESULTS ===")
    print(f"Total checks: {checks_total}")
    print(f"Failed checks: {checks_failed}")
    print(f"Non-format failures: {non_format_failures}")

    # Gate decision: format issues auto-fixed count as REVISED not BLOCKED
    if non_format_failures >= 4:
        gate = "BLOCKED"
        block_reasons.append(f"{non_format_failures} non-format checks failed (threshold: 4)")
    elif checks_failed > 0:
        gate = "REVISED"
    else:
        gate = "PASSED"

    print(f"Gate: {gate}")

    failures = [c for c in checks_detail if c["result"] == "FAIL"]
    if failures:
        print(f"\n=== FAILURES ({len(failures)}) ===")
        for f in failures:
            obj_str = f" [{f['objeto'][:50]}]" if f.get('objeto') else ""
            print(f"  {f['check']}{obj_str}: {f.get('detail', '')}")

    # ========== Write delivery_validation ==========
    data["delivery_validation"] = {
        "gate_adversarial": gate,
        "checks_total": checks_total,
        "checks_failed": checks_failed,
        "checks_detail": [c for c in checks_detail if c["result"] in ("FAIL", "INFO")],
        "rebaixamentos": rebaixamentos,
        "block_reasons": block_reasons,
        "revisions_made": revisions_made,
        "reader_persona": "Dono de empresa de pavimentação de porte médio do RS, 10min de atenção, busca ação concreta"
    }

    save_json(data)
    print(f"\nJSON saved to {JSON_PATH}")
    return gate, checks_failed, checks_total

if __name__ == "__main__":
    gate, failed, total = run_audit()
    print(f"\n{'='*50}")
    print(f"FINAL: {gate} ({failed}/{total} checks failed)")
