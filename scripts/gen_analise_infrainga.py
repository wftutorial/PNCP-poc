#!/usr/bin/env python3
"""
Generate analise for each of the 20 editais in the top20 array of
intel-27735305000106-2026-03-21.json (INFRAINGA ENGENHARIA LTDA).

Reads structured extraction + texto_documentos + _analysis_context.
Writes back to the same JSON file.
"""

import json
import re
import sys
from pathlib import Path

FILE = Path("D:/pncp-poc/docs/intel/intel-27735305000106-2026-03-21.json")

# Empresa profile
EMPRESA = "INFRAINGA ENGENHARIA LTDA"
CAPITAL = 2_000_000.0
SEDE = "Fênix/PR"
CNAE_PRINCIPAL = "4222701"  # construção de redes de água/esgoto
IS_ME_EPP = False  # Capital R$ 2M suggests medium company, NOT ME/EPP


def fmt_valor(v):
    if v is None or v == 0:
        return "Não informado"
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"R$ {v/1_000:.0f} mil"
    return f"R$ {v:.2f}"


def parse_date(dt_str):
    """Parse ISO date/datetime into DD/MM/YYYY [às HH:MM]"""
    if not dt_str:
        return None
    dt_str = dt_str.strip()
    # Try datetime first
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})", dt_str)
    if m:
        return f"{m.group(3)}/{m.group(2)}/{m.group(1)} às {m.group(4)}:{m.group(5)}"
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", dt_str)
    if m:
        return f"{m.group(3)}/{m.group(2)}/{m.group(1)}"
    return dt_str


def extract_from_text(text, pattern, default="Não consta no edital disponível"):
    """Search text for regex pattern, return first group or default."""
    if not text:
        return default
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        return m.group(1).strip() if m.lastindex else m.group(0).strip()
    return default


def get_field(ext, field_name, default="Não identificado no edital"):
    """Get a field from _structured_extraction.fields."""
    if not ext:
        return None
    fields = ext.get("fields", {})
    f = fields.get(field_name, {})
    if f.get("found"):
        return f.get("value", default)
    return None


def classify_logistics(dist_km, modalidade):
    """Assess logistics cost impact."""
    if dist_km is None:
        return "Distância não calculada"
    if dist_km <= 50:
        return f"Impacto logístico BAIXO — {dist_km:.0f} km da sede, deslocamento rápido"
    elif dist_km <= 150:
        return f"Impacto logístico BAIXO — {dist_km:.0f} km da sede, viável para ida e volta no dia"
    elif dist_km <= 300:
        return f"Impacto logístico MODERADO — {dist_km:.0f} km da sede, pode requerer pernoite para visitas e mobilização"
    elif dist_km <= 500:
        is_eletronica = "eletrôn" in (modalidade or "").lower() or "eletrôn" in (modalidade or "").lower()
        sessao_note = "sessão eletrônica dispensa deslocamento" if is_eletronica else "sessão presencial exige deslocamento"
        return f"Impacto logístico ALTO — {dist_km:.0f} km da sede, {sessao_note}. Mobilização de equipe onerosa"
    else:
        return f"Impacto logístico MUITO ALTO — {dist_km:.0f} km da sede, custos significativos de mobilização e hospedagem"


def is_me_epp_exclusive(edital):
    """Check if edital is exclusive for ME/EPP."""
    ext = edital.get("_structured_extraction", {})
    me_field = get_field(ext, "exclusividade_me_epp")
    if me_field:
        val = me_field.lower()
        if "exclusiv" in val:
            return True
    return False


def extract_prazo_from_text(text, objeto):
    """Try to extract prazo de execução from text or objeto."""
    if not text and not objeto:
        return "Não consta no edital disponível"

    combined = (objeto or "") + " " + (text or "")[:5000]

    patterns = [
        r"prazo\s+(?:de\s+)?execu[çc][ãa]o[:\s]+(?:de\s+)?(\d+)\s*\(?\w*\)?\s*(dias|meses|mês)",
        r"prazo\s+(?:de\s+)?(\d+)\s*\(?\w*\)?\s*(dias|meses|mês)\s+(?:para\s+)?execu",
        r"(\d+)\s*\(?\w+\)?\s*(dias|meses|mês)\s+(?:de\s+)?(?:prazo|execu[çc][ãa]o)",
        r"prazo\s+(?:de\s+)?vigência[:\s]+(?:de\s+)?(\d+)\s*\(?\w*\)?\s*(dias|meses|mês)",
        r"Prazo de execu[çc][ãa]o:\s*(\d+)\s*\(?\w*\)?\s*(dias|meses|mês)",
    ]
    for p in patterns:
        m = re.search(p, combined, re.IGNORECASE)
        if m:
            num = m.group(1)
            unit = m.group(2).lower()
            if "dia" in unit:
                return f"{num} dias a partir da Ordem de Serviço"
            else:
                return f"{num} meses a partir da Ordem de Serviço"

    # Check structured extraction
    return None


def extract_visita_from_text(text):
    """Extract visita técnica info."""
    if not text:
        return None
    text_lower = text[:10000].lower()
    if "visita técnica" in text_lower or "visita tecnica" in text_lower:
        if "obrigatória" in text_lower or "obrigatoria" in text_lower:
            if "não é obrigatória" in text_lower or "nao e obrigatoria" in text_lower or "não será obrigatória" in text_lower or "facultativa" in text_lower:
                return "Facultativa"
            return "Obrigatória"
        if "facultativa" in text_lower:
            return "Facultativa"
        if "dispensada" in text_lower or "não será exigida" in text_lower:
            return "Dispensada"
        return "Mencionada no edital — verificar obrigatoriedade"
    return "Não consta no edital disponível"


def generate_analise(edital):
    """Generate the analise object for one edital."""

    _id = edital["_id"]
    objeto = edital.get("objeto", "")
    valor = edital.get("valor_estimado")
    modalidade = edital.get("modalidade_nome", "")
    municipio = edital.get("municipio", "")
    uf = edital.get("uf", "")
    data_abertura = edital.get("data_abertura_proposta", "")
    data_encerramento = edital.get("data_encerramento_proposta", "")
    status_temporal = edital.get("status_temporal", "")
    dias_restantes = edital.get("dias_restantes")
    dist = edital.get("distancia", {})
    dist_km = dist.get("km")
    texto = edital.get("texto_documentos", "")
    ext = edital.get("_structured_extraction", {})
    extraction_quality = edital.get("extraction_quality", "")
    analysis_limited = edital.get("_analysis_limited", False)
    extraction_sections = edital.get("extraction_sections", {})
    ibge = edital.get("ibge", {})
    competitive = edital.get("competitive_intel", {})
    roi = edital.get("roi_proposta", {})
    custo_proposta = edital.get("custo_proposta", {})
    bid_sim = edital.get("_bid_simulation", {})
    victory_fit = edital.get("_victory_fit", 0)

    is_limited = analysis_limited or not texto
    source = "claude_limited" if is_limited else "claude_inline"

    # --- RESUMO OBJETO ---
    resumo = objeto[:300]
    # Make it a proper summary
    if len(objeto) > 100:
        # Use the objeto itself as summary since it's already descriptive
        resumo = objeto.split(",")[0] if "," in objeto else objeto[:200]
        if municipio:
            if municipio.lower() not in resumo.lower():
                resumo += f", no município de {municipio}/{uf}"
        if valor and valor > 0:
            resumo += f". Valor estimado: {fmt_valor(valor)}."
        else:
            resumo += "."

    # --- REQUISITOS TÉCNICOS ---
    req_tec = []
    acervo = get_field(ext, "acervo_tecnico")
    if acervo:
        req_tec.append(f"Acervo técnico (CAT) registrado no CREA/CAU: {acervo[:150]}")

    # Extract from text
    if texto:
        if re.search(r"responsável técnico|responsavel tecnico|RT", texto[:10000], re.IGNORECASE):
            req_tec.append("Responsável técnico habilitado (engenheiro civil ou similar)")
        if re.search(r"registro no CREA|registro.*CAU", texto[:10000], re.IGNORECASE):
            if not any("CREA" in r for r in req_tec):
                req_tec.append("Registro no CREA/CAU do responsável técnico")
        if re.search(r"ART|anotação de responsabilidade", texto[:10000], re.IGNORECASE):
            req_tec.append("ART/RRT de execução")
        if re.search(r"ISO|certificação|certificacao", texto[:10000], re.IGNORECASE):
            req_tec.append("Certificações específicas conforme edital")

    if not req_tec:
        if is_limited:
            req_tec = ["Edital não disponível para extração — verificar requisitos no portal"]
        else:
            req_tec = ["Verificar requisitos técnicos detalhados no edital completo"]

    # --- REQUISITOS HABILITAÇÃO ---
    req_hab = []
    if texto:
        hab_patterns = {
            "Certidão Negativa de Débitos Trabalhistas (CNDT)": r"CNDT|certidão.*trabalhist|certidao.*trabalhist",
            "Certidão Negativa de Falência e Concordata": r"certidão.*falência|certidao.*falencia",
            "Certidão de Regularidade do FGTS (CRF)": r"CRF|regularidade.*FGTS|FGTS",
            "Certidão Negativa de Débitos Federais (CND)": r"CND|débitos federais|debitos federais|Receita Federal",
            "Prova de regularidade fiscal municipal e estadual": r"regularidade.*fiscal.*municipal|regularidade.*estadual",
            "Inscrição no CNPJ": r"CNPJ",
            "Registro no CREA/CAU da empresa": r"registro.*CREA|registro.*CAU|inscrição.*CREA",
            "Balanço patrimonial do último exercício social": r"balanço patrimonial|balanco patrimonial",
        }
        for desc, pat in hab_patterns.items():
            if re.search(pat, texto[:15000], re.IGNORECASE):
                req_hab.append(desc)

    if not req_hab:
        if is_limited:
            req_hab = ["Edital não disponível — verificar habilitação jurídica, fiscal, trabalhista e técnica no portal"]
        else:
            req_hab = ["Habilitação jurídica, regularidade fiscal e trabalhista conforme Lei 14.133/2021"]

    # --- QUALIFICAÇÃO ECONÔMICA ---
    pl = get_field(ext, "patrimonio_liquido")
    if pl:
        if "%" in str(pl) or pl.isdigit():
            pct = re.search(r"(\d+)", str(pl))
            if pct and valor:
                pct_val = int(pct.group(1))
                pl_min = valor * pct_val / 100
                qual_eco = f"Patrimônio líquido mínimo de {pct_val}% do valor estimado (R$ {pl_min:,.2f})"
            else:
                qual_eco = f"Patrimônio líquido mínimo de {pl} do valor estimado"
        else:
            qual_eco = f"Patrimônio líquido mínimo: {pl}"
    elif texto and re.search(r"patrimônio líquido|patrimonio liquido", texto[:15000], re.IGNORECASE):
        m = re.search(r"patrimônio líquido.*?(\d+)%", texto[:15000], re.IGNORECASE)
        if m and valor:
            pct = int(m.group(1))
            pl_min = valor * pct / 100
            qual_eco = f"Patrimônio líquido mínimo de {pct}% do valor estimado (R$ {pl_min:,.2f})"
        else:
            qual_eco = "Patrimônio líquido mínimo exigido — verificar percentual no edital"
    else:
        qual_eco = "Não identificado no edital disponível" if is_limited else "Verificar exigência de patrimônio líquido no edital"

    # --- PRAZO EXECUÇÃO ---
    prazo_ext = get_field(ext, "prazo_execucao")
    if prazo_ext:
        try:
            num = int(re.search(r"\d+", str(prazo_ext)).group(0))
            if num > 365:
                prazo = f"{num} dias ({num//30} meses aprox.) a partir da Ordem de Serviço"
            elif num > 30:
                prazo = f"{num} dias a partir da Ordem de Serviço"
            else:
                prazo = f"{num} dias a partir da Ordem de Serviço"
        except:
            prazo = f"{prazo_ext} a partir da Ordem de Serviço"
    else:
        prazo = extract_prazo_from_text(texto, objeto)
        if prazo is None:
            # Check objeto for "Prazo de execução: X dias"
            m = re.search(r"[Pp]razo.*?execu[çc][ãa]o.*?(\d+).*?(dias|meses)", objeto)
            if m:
                prazo = f"{m.group(1)} {m.group(2)} a partir da Ordem de Serviço"
            else:
                prazo = "Não consta no edital disponível" if is_limited else "Verificar prazo no edital completo"

    # --- GARANTIAS ---
    garantia_field = get_field(ext, "garantia_proposta")
    if garantia_field:
        m = re.search(r"(\d+)%|(\d+)\s*por\s*cento", garantia_field)
        if m:
            pct = m.group(1) or m.group(2)
            garantias = f"{pct}% do valor do contrato"
        else:
            garantias = garantia_field[:200]
    elif texto and re.search(r"garantia", texto[:15000], re.IGNORECASE):
        m = re.search(r"garantia.*?(\d+)%", texto[:15000], re.IGNORECASE)
        if m:
            garantias = f"{m.group(1)}% do valor do contrato"
        else:
            garantias = "Exigida — verificar percentual no edital"
    else:
        garantias = "Não consta no edital disponível" if is_limited else "Verificar exigência no edital"

    # --- CRITÉRIO JULGAMENTO ---
    criterio = get_field(ext, "criterio_julgamento")
    if criterio:
        criterio_upper = criterio.upper()
        if "MAIOR DESCONTO" in criterio_upper:
            criterio_julg = "Maior Desconto"
        elif "MENOR PREÇO POR ITEM" in criterio_upper:
            criterio_julg = "Menor Preço por Item"
        elif "MENOR PREÇO" in criterio_upper or "MENOR PRECO" in criterio_upper:
            criterio_julg = "Menor Preço Global"
        elif "TÉCNICA E PREÇO" in criterio_upper or "TECNICA E PRECO" in criterio_upper:
            criterio_julg = "Técnica e Preço"
        else:
            criterio_julg = criterio.strip()
    else:
        criterio_julg = "Não identificado — verificar no edital"

    # --- DATA SESSÃO ---
    data_sessao_field = get_field(ext, "data_sessao")
    plataforma = get_field(ext, "plataforma") or ""

    if data_sessao_field:
        data_sessao = data_sessao_field
        if plataforma:
            data_sessao += f" (plataforma: {plataforma})"
    elif data_encerramento:
        data_sessao = parse_date(data_encerramento)
        if plataforma:
            data_sessao += f" (plataforma: {plataforma})"
    else:
        data_sessao = "Data não informada no PNCP"

    # --- PRAZO PROPOSTA ---
    if data_encerramento:
        prazo_proposta = parse_date(data_encerramento)
    elif data_abertura:
        prazo_proposta = parse_date(data_abertura)
    else:
        prazo_proposta = "Data não informada"

    # --- VISITA TÉCNICA ---
    visita = extract_visita_from_text(texto)
    if visita is None:
        visita = "Não consta no edital disponível"

    # --- EXCLUSIVIDADE ME/EPP ---
    me_epp_exclusive = is_me_epp_exclusive(edital)
    me_field = get_field(ext, "exclusividade_me_epp")
    if me_field:
        val_lower = me_field.lower()
        if "exclusiv" in val_lower and ("microempresa" in val_lower or "me" in val_lower.split()):
            exclusividade = f"Sim — {me_field}"
        elif "exclusiv" in val_lower:
            exclusividade = f"Sim — {me_field}"
        elif "cota" in val_lower:
            exclusividade = f"Cota reservada — {me_field}"
        else:
            exclusividade = me_field
    else:
        if texto:
            txt_lower = texto[:10000].lower()
            # Must find explicit ME/EPP exclusivity pattern, not just word co-occurrence
            me_epp_patterns = [
                r"exclusiv\w+\s+(?:para\s+)?(?:participação\s+de\s+)?microempresa",
                r"exclusiv\w+\s+(?:para\s+)?me/?epp",
                r"licitação\s+exclusiva\s+(?:para\s+)?me",
                r"participação\s+exclusiva\s+de\s+microempresa",
                r"reservad[oa]\s+(?:para\s+)?(?:a\s+)?(?:participação\s+de\s+)?microempresa",
            ]
            found_me = False
            for pat in me_epp_patterns:
                if re.search(pat, txt_lower):
                    exclusividade = "Sim — exclusivo para ME/EPP"
                    me_epp_exclusive = True
                    found_me = True
                    break
            if not found_me:
                if re.search(r"cota\s+reservada", txt_lower):
                    exclusividade = "Cota reservada para ME/EPP"
                else:
                    exclusividade = "Não identificada restrição de porte"
        else:
            exclusividade = "Não consta no edital disponível"

    # --- REGIME EXECUÇÃO ---
    regime = get_field(ext, "regime_execucao")
    if regime:
        regime_exec = regime.strip()
        if regime_exec.lower() == "global":
            regime_exec = "Empreitada por preço global"
        elif regime_exec.lower() == "integrada":
            regime_exec = "Contratação integrada"
    elif texto:
        txt_lower = texto[:5000].lower()
        if "preço global" in txt_lower or "preco global" in txt_lower:
            regime_exec = "Empreitada por preço global"
        elif "preço unitário" in txt_lower or "preco unitario" in txt_lower:
            regime_exec = "Empreitada por preço unitário"
        elif "integrada" in txt_lower:
            regime_exec = "Contratação integrada"
        else:
            regime_exec = "Verificar no edital"
    else:
        regime_exec = "Não consta no edital disponível"

    # --- CONSÓRCIO ---
    consorcio_field = get_field(ext, "consorcio")
    if consorcio_field:
        val_lower = consorcio_field.lower()
        if "não" in val_lower or "vedado" in val_lower or "nao" in val_lower:
            consorcio = "Vedado"
        elif "permitid" in val_lower or "sim" in val_lower:
            consorcio = "Permitido"
        else:
            consorcio = consorcio_field
    elif texto and extraction_sections.get("consorcio"):
        txt_lower = texto[:15000].lower()
        if "vedada a participação" in txt_lower and "consórcio" in txt_lower:
            consorcio = "Vedado"
        elif "não será permitid" in txt_lower and "consórcio" in txt_lower:
            consorcio = "Vedado"
        elif "participação de consórcio" in txt_lower:
            consorcio = "Verificar condições no edital"
        else:
            consorcio = "Não mencionado no edital"
    else:
        consorcio = "Não mencionado no edital" if not is_limited else "Não consta no edital disponível"

    # --- OBSERVAÇÕES CRÍTICAS ---
    obs = []

    if is_limited:
        obs.append("Análise limitada — edital principal não disponível para download no PNCP")

    if me_epp_exclusive and not IS_ME_EPP:
        obs.append("ATENÇÃO: Licitação exclusiva para ME/EPP — empresa com capital social de R$ 2M pode não se enquadrar como ME/EPP. Verificar faturamento bruto anual (limite EPP: R$ 4,8M)")

    if status_temporal == "URGENTE":
        obs.append(f"Prazo URGENTE — apenas {dias_restantes} dias restantes para submissão")
    elif status_temporal == "IMINENTE" and dias_restantes and dias_restantes <= 7:
        obs.append(f"Prazo curto — apenas {dias_restantes} dias restantes para submissão")

    if valor and valor > 5_000_000:
        obs.append(f"Obra de grande porte ({fmt_valor(valor)}) — verificar capacidade operacional e financeira")

    if dist_km and dist_km > 400:
        obs.append(f"Distância elevada da sede ({dist_km:.0f} km) — considerar custos de mobilização")

    if "integrada" in (regime_exec or "").lower():
        obs.append("Contratação integrada — requer elaboração de projeto básico/executivo pela contratada")

    if "presencial" in (modalidade or "").lower():
        obs.append(f"Modalidade presencial — exige deslocamento até {municipio}/{uf} para a sessão")

    if competitive:
        comp_level = competitive.get("competition_level", "")
        if comp_level == "MUITO_ALTA":
            obs.append("Nível de competição MUITO ALTO no histórico do órgão — concorrência acirrada")

    if not obs:
        obs.append("Sem alertas críticos identificados")

    observacoes = ". ".join(obs)

    # --- NÍVEL DIFICULDADE ---
    difficulty_score = 0

    if valor and valor > 8_000_000:
        difficulty_score += 2
    elif valor and valor > 3_000_000:
        difficulty_score += 1

    if "integrada" in (regime_exec or "").lower():
        difficulty_score += 2

    if dist_km and dist_km > 400:
        difficulty_score += 1

    if "presencial" in (modalidade or "").lower():
        difficulty_score += 1

    if me_epp_exclusive:
        difficulty_score += 2  # Can't participate

    if difficulty_score >= 4:
        nivel = "ALTO"
    elif difficulty_score >= 2:
        nivel = "MÉDIO"
    else:
        nivel = "BAIXO"

    # --- RECOMENDAÇÃO ---
    # NÃO PARTICIPAR reasons
    nao_participar_reasons = []

    if me_epp_exclusive and not IS_ME_EPP:
        nao_participar_reasons.append("exclusiva ME/EPP e empresa não se enquadra")

    # Aquisição de materiais (not obra/serviço de engenharia)
    obj_lower = objeto.lower()
    is_aquisicao_material = ("aquisição de material" in obj_lower or "aquisicao de material" in obj_lower) and \
                            "obra" not in obj_lower and "execução" not in obj_lower and "execucao" not in obj_lower

    if is_aquisicao_material and "construção" not in obj_lower and "construcao" not in obj_lower:
        # Pure material acquisition — not engineering company's core
        if "engenharia" not in obj_lower:
            pass  # Could still be relevant for construction materials

    # Check if it's maintenance of air conditioning (not core business)
    is_non_core = False
    if "ar condicionado" in obj_lower or "ar-condicionado" in obj_lower:
        is_non_core = True
        nao_participar_reasons.append("serviço de manutenção de ar condicionado fora do escopo principal (CNAE 4222701)")

    # Check for isolated painting services (not part of a larger construction project)
    has_obra_real = ("execução de obra" in obj_lower or "execucao de obra" in obj_lower or
                     "obras de" in obj_lower or "obra de" in obj_lower) and \
                    "mão de obra" not in obj_lower and "mao de obra" not in obj_lower
    if "pintura" in obj_lower and not has_obra_real and "paviment" not in obj_lower and "construção" not in obj_lower and "construcao" not in obj_lower:
        is_non_core = True
        nao_participar_reasons.append("serviço de pintura isolado — baixa aderência ao perfil de engenharia de infraestrutura (CNAE 4222701)")

    if "limpeza de bueiros" in obj_lower or "desobstrução de galeria" in obj_lower:
        # This is actually related to water/sewer infrastructure
        pass

    if status_temporal == "SEM_DATA" and not data_encerramento and not data_abertura:
        # Can't submit if no dates
        pass  # Still recommend if otherwise good

    if nao_participar_reasons:
        recomendacao = "NÃO PARTICIPAR"
    else:
        recomendacao = "PARTICIPAR"

    # --- CUSTO LOGÍSTICO NOTA ---
    custo_log = classify_logistics(dist_km, modalidade)

    analise = {
        "resumo_objeto": resumo,
        "requisitos_tecnicos": req_tec,
        "requisitos_habilitacao": req_hab,
        "qualificacao_economica": qual_eco,
        "prazo_execucao": prazo,
        "garantias": garantias,
        "criterio_julgamento": criterio_julg,
        "data_sessao": data_sessao,
        "prazo_proposta": prazo_proposta,
        "visita_tecnica": visita,
        "exclusividade_me_epp": exclusividade,
        "regime_execucao": regime_exec,
        "consorcio": consorcio,
        "observacoes_criticas": observacoes,
        "nivel_dificuldade": nivel,
        "recomendacao_acao": recomendacao,
        "custo_logistico_nota": custo_log,
        "_source": source,
        "_reviewed": False,
    }

    return analise


def main():
    print(f"Loading {FILE}...")
    with open(FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    top20 = data["top20"]
    print(f"Found {len(top20)} editais in top20")

    for i, edital in enumerate(top20):
        _id = edital["_id"]
        analise = generate_analise(edital)
        edital["analise"] = analise
        rec = analise["recomendacao_acao"]
        src = analise["_source"]
        print(f"  [{i:2d}] {_id:35s} | {rec:16s} | {analise['nivel_dificuldade']:6s} | {src}")

    print(f"\nWriting back to {FILE}...")
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Done! All 20 analyses generated.")

    # Summary
    participar = sum(1 for e in top20 if e["analise"]["recomendacao_acao"] == "PARTICIPAR")
    nao = sum(1 for e in top20 if e["analise"]["recomendacao_acao"] == "NÃO PARTICIPAR")
    limited = sum(1 for e in top20 if e["analise"]["_source"] == "claude_limited")
    print(f"\nResumo: {participar} PARTICIPAR, {nao} NÃO PARTICIPAR, {limited} com análise limitada")


if __name__ == "__main__":
    main()
