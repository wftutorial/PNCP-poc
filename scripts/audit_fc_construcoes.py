#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditor agent: adversarial audit of enriched JSON for FC CONSTRUCOES LTDA.
Reads, audits, writes back delivery_validation + coherence fixes.
"""
import json
import re
import os

INPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'docs', 'reports', 'data-33750637000154-2026-03-17.json')


def load_data():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def count_factual_assertions(text):
    """Count sentences with factual assertions (numbers, R$, distances, etc.)."""
    sentences = [s.strip() for s in text.replace('\n', '.').split('.') if s.strip()]
    count = 0
    for s in sentences:
        if re.search(
            r'(R\$|\d+[.,]\d+|\d+\s*(km|dia|%|contrato|meses|anos)|'
            r'capital social|acervo|distância|distancia|proximidade|prazo|'
            r'resultado potencial)',
            s, re.IGNORECASE
        ):
            count += 1
    return count


def check_english_terms(text):
    """Check for English/technical terms that shouldn't be in user-facing text."""
    english_words = [
        'risk', 'score', 'warning', 'check', 'benchmark', 'cluster',
        'pipeline', 'deadline', 'compliance', 'threshold', 'veto',
        'fallback', 'timeout', 'cache'
    ]
    return [w for w in english_words if w in text.lower()]


def get_edital_id(edital, idx):
    cnpj_orgao = edital.get('cnpj_orgao', '')
    ano = edital.get('ano_compra', '')
    seq = edital.get('sequencial_compra', '')
    if cnpj_orgao and ano and seq:
        return f"{cnpj_orgao}/{ano}/{seq}"
    return f"edital_idx_{idx}"


def audit_participar(edital, idx, empresa):
    """Full 11-check audit for PARTICIPAR editais."""
    checks = []
    justificativa = edital.get('justificativa', '') or ''
    analise_doc = edital.get('analise_documental')
    risk_score = edital.get('risk_score', {}) or {}
    hab = edital.get('habilitacao_checklist', {}) or {}
    distancia_km = edital.get('distancia_km')
    cnae_compat = edital.get('_cnae_compatible')
    simples_warning = hab.get('simples_revenue_warning', False)
    vetoed = risk_score.get('vetoed', False)
    fiscal_risk = risk_score.get('fiscal_risk', {}) or {}
    fiscal_nivel = fiscal_risk.get('nivel', '') if isinstance(fiscal_risk, dict) else ''
    link_valid = edital.get('link_valid')
    mei = empresa.get('mei', False)
    valor = edital.get('valor_estimado', 0) or 0

    # C1: >=2 factual assertions
    fc = count_factual_assertions(justificativa)
    if fc < 2:
        checks.append(('C1', 'FAIL', f'Justificativa com apenas {fc} asserção(ões) factual(is). Mínimo: 2.'))
    else:
        checks.append(('C1', 'PASS', ''))

    # C2: distancia_km mentioned
    if distancia_km is not None and distancia_km != '':
        if not any(w in justificativa.lower() for w in ['km', 'distância', 'distancia', 'proximidade', 'próximo', 'proximo']):
            checks.append(('C2', 'FAIL', f'distancia_km={distancia_km} preenchido mas justificativa não menciona distância.'))
        else:
            checks.append(('C2', 'PASS', ''))
    else:
        checks.append(('C2', 'PASS', ''))

    # C3: CAT required but not available
    if hab.get('cat_required') and not hab.get('cat_available'):
        checks.append(('C3', 'FAIL', 'cat_required=true mas cat_available=false.'))
    else:
        checks.append(('C3', 'PASS', ''))

    # C4: CNAE incompatible
    if cnae_compat is False:
        checks.append(('C4', 'FAIL', '_cnae_compatible=false mas recomendação é PARTICIPAR.'))
    else:
        checks.append(('C4', 'PASS', ''))

    # C5: Simples revenue warning
    if simples_warning:
        if not any(w in justificativa.lower() for w in ['simples', 'receita bruta', 'sublimite', 'faturamento', 'tributár', 'tributar']):
            checks.append(('C5', 'FAIL', 'simples_revenue_warning=true mas justificativa não menciona alerta tributário.'))
        else:
            checks.append(('C5', 'PASS', ''))
    else:
        checks.append(('C5', 'PASS', ''))

    # C6: MEI limit
    if mei and valor > 81000:
        checks.append(('C6', 'FAIL', f'MEI com valor R${valor:,.2f} acima do limite R$81.000.'))
    else:
        checks.append(('C6', 'PASS', ''))

    # C7: analise_documental filled
    if not analise_doc:
        checks.append(('C7', 'FAIL', 'analise_documental ausente.'))
    elif isinstance(analise_doc, dict) and not analise_doc.get('status'):
        checks.append(('C7', 'FAIL', 'analise_documental.status vazio.'))
    elif isinstance(analise_doc, str) and not analise_doc.strip():
        checks.append(('C7', 'FAIL', 'analise_documental string vazia.'))
    else:
        checks.append(('C7', 'PASS', ''))

    # C8: Link validity
    if link_valid is False:
        checks.append(('C8', 'FAIL', 'link_valid=false não sinalizado.'))
    else:
        checks.append(('C8', 'PASS', ''))

    # C9: Vetoed
    if vetoed:
        checks.append(('C9', 'FAIL', 'risk_score.vetoed=true mas recomendação é PARTICIPAR.'))
    else:
        checks.append(('C9', 'PASS', ''))

    # C10: High fiscal risk
    if fiscal_nivel and fiscal_nivel.upper() == 'ALTO':
        if not any(w in justificativa.lower() for w in ['fiscal', 'risco fiscal', 'regularidade', 'certidão', 'certidao', 'débito', 'debito']):
            checks.append(('C10', 'FAIL', 'fiscal_risk.nivel=ALTO sem menção na justificativa.'))
        else:
            checks.append(('C10', 'PASS', ''))
    else:
        checks.append(('C10', 'PASS', ''))

    # C11: English/technical terms
    found = check_english_terms(justificativa)
    if found:
        checks.append(('C11', 'FAIL', f'Termos em inglês na justificativa: {", ".join(found)}'))
    else:
        checks.append(('C11', 'PASS', ''))

    return checks


def audit_cautela(edital, idx, empresa):
    """C1, C7, C8, C11 only for AVALIAR COM CAUTELA."""
    checks = []
    justificativa = edital.get('justificativa', '') or ''
    analise_doc = edital.get('analise_documental')
    link_valid = edital.get('link_valid')

    # C1
    fc = count_factual_assertions(justificativa)
    if fc < 2:
        checks.append(('C1', 'FAIL', f'Justificativa com apenas {fc} asserção(ões) factual(is). Mínimo: 2.'))
    else:
        checks.append(('C1', 'PASS', ''))

    # C7
    if not analise_doc:
        checks.append(('C7', 'FAIL', 'analise_documental ausente.'))
    elif isinstance(analise_doc, dict) and not analise_doc.get('status'):
        checks.append(('C7', 'FAIL', 'analise_documental.status vazio.'))
    elif isinstance(analise_doc, str) and not analise_doc.strip():
        checks.append(('C7', 'FAIL', 'analise_documental string vazia.'))
    else:
        checks.append(('C7', 'PASS', ''))

    # C8
    if link_valid is False:
        checks.append(('C8', 'FAIL', 'link_valid=false não sinalizado.'))
    else:
        checks.append(('C8', 'PASS', ''))

    # C11
    found = check_english_terms(justificativa)
    if found:
        checks.append(('C11', 'FAIL', f'Termos em inglês: {", ".join(found)}'))
    else:
        checks.append(('C11', 'PASS', ''))

    return checks


def main():
    data = load_data()
    empresa = data.get('empresa', {})
    editais = data.get('editais', [])

    all_checks_detail = []
    rebaixamentos = []
    total_checks = 0
    total_fails = 0
    revisions = []

    # --- Phase 1: Audit PARTICIPAR editais ---
    for idx, e in enumerate(editais):
        if e.get('recomendacao') != 'PARTICIPAR':
            continue
        edital_id = get_edital_id(e, idx)
        checks = audit_participar(e, idx, empresa)
        for check_id, status, motivo in checks:
            total_checks += 1
            entry = {"edital_id": edital_id, "check": check_id, "status": status}
            if motivo:
                entry["motivo"] = motivo
            all_checks_detail.append(entry)
            if status == 'FAIL':
                total_fails += 1

        # Any fail -> downgrade
        fails = [(c, m) for c, s, m in checks if s == 'FAIL']
        if fails:
            motivo_rebaixamento = '; '.join([f"{c}: {m}" for c, m in fails])
            rebaixamentos.append({
                "edital_id": edital_id,
                "de": "PARTICIPAR",
                "para": "AVALIAR COM CAUTELA",
                "motivo": motivo_rebaixamento
            })
            e['justificativa_original'] = e.get('justificativa', '')
            e['motivo_rebaixamento'] = motivo_rebaixamento
            e['justificativa'] = f"Rebaixado de PARTICIPAR para AVALIAR COM CAUTELA. Motivos: {motivo_rebaixamento}"
            e['recomendacao'] = 'AVALIAR COM CAUTELA'
            revisions.append(f"Edital {edital_id}: rebaixado de PARTICIPAR para AVALIAR COM CAUTELA")

    # --- Phase 2: Audit AVALIAR COM CAUTELA (excluding downgraded) ---
    for idx, e in enumerate(editais):
        if e.get('recomendacao') != 'AVALIAR COM CAUTELA':
            continue
        if 'justificativa_original' in e:
            continue  # already audited as PARTICIPAR
        edital_id = get_edital_id(e, idx)
        checks = audit_cautela(e, idx, empresa)
        for check_id, status, motivo in checks:
            total_checks += 1
            entry = {"edital_id": edital_id, "check": check_id, "status": status}
            if motivo:
                entry["motivo"] = motivo
            all_checks_detail.append(entry)
            if status == 'FAIL':
                total_fails += 1

    # --- Phase 3: Coherence fixes ---

    # 3a: proximos_passos - remove entries pointing to non-PARTICIPAR editais
    proximos = data.get('proximos_passos', [])
    if isinstance(proximos, list):
        original_len = len(proximos)
        cleaned_proximos = []
        removed_proximos = []
        for p in proximos:
            eidx = p.get('edital_index')
            if eidx is not None and eidx < len(editais):
                actual_rec = editais[eidx].get('recomendacao', '')
                if actual_rec == 'PARTICIPAR':
                    cleaned_proximos.append(p)
                else:
                    removed_proximos.append(f"edital_index={eidx} (rec={actual_rec})")
            else:
                cleaned_proximos.append(p)  # keep if we can't verify
        if removed_proximos:
            data['proximos_passos'] = cleaned_proximos
            revisions.append(f"proximos_passos: removidos {len(removed_proximos)} itens referenciando editais não-PARTICIPAR: {', '.join(removed_proximos[:5])}")

    # 3b: resumo_executivo.recomendacoes - correct counts
    resumo = data.get('resumo_executivo', {})
    if resumo:
        current_counts = {}
        for e in editais:
            rec = e.get('recomendacao', '')
            current_counts[rec] = current_counts.get(rec, 0) + 1

        old_counts = resumo.get('recomendacoes', {})
        if old_counts != current_counts:
            resumo['recomendacoes'] = current_counts
            revisions.append(f"resumo_executivo.recomendacoes corrigido de {old_counts} para {current_counts}")

        # Update valor_total_participar
        valor_participar = sum(
            (e.get('valor_estimado', 0) or 0)
            for e in editais
            if e.get('recomendacao') == 'PARTICIPAR'
        )
        old_valor = resumo.get('valor_total_participar', 0)
        if abs(valor_participar - old_valor) > 1:
            resumo['valor_total_participar'] = round(valor_participar, 2)
            revisions.append(f"resumo_executivo.valor_total_participar corrigido de {old_valor} para {valor_participar:.2f}")

    # --- Phase 4: Format checks (spot check) ---
    # Check dates format in a few editais
    format_issues = []
    for idx, e in enumerate(editais[:10]):
        da = e.get('data_abertura', '')
        if da and not re.match(r'^\d{4}-\d{2}-\d{2}$', da):
            format_issues.append(f"edital {idx}: data_abertura '{da}' formato inesperado")

    # --- Phase 5: Determine gate ---
    if total_fails >= 3:
        gate = "BLOCKED"
        block_reasons = [f"{total_fails} checks falharam (limite: 3). Revisão necessária antes da entrega."]
    elif total_fails > 0:
        gate = "REVISED"
        block_reasons = []
    else:
        gate = "PASSED"
        block_reasons = []

    # Preserve existing gate_deterministic
    existing_validation = data.get('delivery_validation', {})
    gate_deterministic = existing_validation.get('gate_deterministic', 'N/A')

    # Final counts
    final_counts = {}
    for e in editais:
        rec = e.get('recomendacao', '')
        final_counts[rec] = final_counts.get(rec, 0) + 1

    failed_checks_detail = [c for c in all_checks_detail if c.get('status') == 'FAIL']

    validation = {
        "gate_deterministic": gate_deterministic,
        "gate_adversarial": gate,
        "checks_total": total_checks,
        "checks_failed": total_fails,
        "checks_detail": failed_checks_detail,
        "rebaixamentos": rebaixamentos,
        "block_reasons": block_reasons,
        "revisions_made": revisions,
        "reader_persona": "Dono de ME do setor Engenharia/Obras, 10min de atenção, busca ação concreta",
        "recommendation_counts_after_audit": final_counts,
        "coherence_fixes": {
            "proximos_passos_removed": len(removed_proximos) if 'removed_proximos' in dir() else 0,
            "resumo_counts_corrected": old_counts != current_counts if 'old_counts' in dir() else False
        }
    }

    data['delivery_validation'] = validation

    # Write back
    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Print summary
    print(f"=== AUDIT SUMMARY ===")
    print(f"Total editais: {len(editais)}")
    print(f"Checks executed: {total_checks}")
    print(f"Checks failed: {total_fails}")
    print(f"Gate adversarial: {gate}")
    print(f"Rebaixamentos: {len(rebaixamentos)}")
    print(f"Counts after audit: {final_counts}")
    print(f"Revisions made: {len(revisions)}")
    print()

    if rebaixamentos:
        print("=== REBAIXAMENTOS ===")
        for r in rebaixamentos:
            print(f"  {r['edital_id']}: {r['de']} -> {r['para']}")
            print(f"    Motivo: {r['motivo'][:200]}")
            print()

    if failed_checks_detail:
        print("=== FAILED CHECKS ===")
        for c in failed_checks_detail:
            print(f"  [{c['check']}] {c['edital_id']}: {c.get('motivo', '')[:150]}")
        print()

    if revisions:
        print("=== REVISIONS MADE ===")
        for r in revisions:
            print(f"  {r}")
        print()

    if format_issues:
        print("=== FORMAT ISSUES ===")
        for f in format_issues:
            print(f"  {f}")


if __name__ == '__main__':
    main()
