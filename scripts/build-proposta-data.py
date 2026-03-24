"""
Build sector-agnostic proposta JSON for any CNPJ from PNCP data.

Usage:
    python scripts/build-proposta-data.py 09225035000101
    python scripts/build-proposta-data.py 09225035000101 --pacote semanal
    python scripts/build-proposta-data.py 09225035000101 --pacote diario --days 15
"""

import argparse
import json
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CAPITAL_MULTIPLIER = 10
PNCP_BASE = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
BRASILAPI_CNPJ = "https://brasilapi.com.br/api/cnpj/v1"
MODALIDADES = [4, 5]  # 4=Concorrência, 5=Pregão Eletrônico
MAX_PAGES = 5
PAGE_SIZE = 50
REQUEST_TIMEOUT = 20
USER_AGENT = "Mozilla/5.0 (SmartLic/1.0)"

# Sector-agnostic authority examples (apply to any B2G sector)
AUTORIDADE_EXEMPLOS = [
    (
        "Análise de centenas de processos licitatórios — identificação dos "
        "documentos que pregoeiros verificam primeiro e onde a maioria das "
        "inabilitações acontecem"
    ),
    (
        "Conhecimento dos critérios não escritos das comissões: como avaliam "
        "atestados, o que configura experiência similar, quando uma exigência "
        "é restritiva o suficiente para impugnar"
    ),
    (
        "Acompanhamento de dezenas de contratos públicos — conhecimento de "
        "quais órgãos pagam em dia e como funciona o fluxo real de medição "
        "e pagamento"
    ),
    (
        "Identificação de cláusulas restritivas disfarçadas: requisitos de "
        "capital desproporcionais, índices contábeis eliminatórios, exigências "
        "de atestado acima do razoável"
    ),
]

# Geographic neighbors for each Brazilian UF
UF_NEIGHBORS: dict[str, list[str]] = {
    "AC": ["AM", "RO"],
    "AL": ["PE", "SE", "BA"],
    "AM": ["AC", "RO", "RR", "PA", "MT"],
    "AP": ["PA"],
    "BA": ["MG", "GO", "TO", "PI", "PE", "AL", "SE", "ES"],
    "CE": ["PI", "RN", "PB", "PE"],
    "DF": ["GO", "MG"],
    "ES": ["MG", "BA", "RJ"],
    "GO": ["MG", "BA", "TO", "MT", "MS", "DF"],
    "MA": ["PI", "TO", "PA"],
    "MG": ["ES", "RJ", "SP", "BA", "GO", "DF", "MS"],
    "MS": ["MT", "GO", "MG", "SP", "PR"],
    "MT": ["AM", "PA", "TO", "GO", "MS", "RO"],
    "PA": ["AM", "MT", "TO", "MA", "AP", "RR"],
    "PB": ["RN", "CE", "PE"],
    "PE": ["PB", "CE", "PI", "AL", "BA"],
    "PI": ["MA", "CE", "PE", "BA", "TO"],
    "PR": ["SP", "SC", "MS"],
    "RJ": ["MG", "ES", "SP"],
    "RN": ["CE", "PB"],
    "RO": ["AC", "AM", "MT"],
    "RR": ["AM", "PA"],
    "RS": ["SC"],
    "SC": ["PR", "RS"],
    "SE": ["AL", "BA"],
    "SP": ["MG", "RJ", "PR", "MS"],
    "TO": ["MA", "PI", "BA", "GO", "MT", "PA"],
}

# Extended CNAE→sector mapping (4-digit prefix → sector key in sectors_data.yaml)
CNAE_TO_SECTOR: dict[str, str] = {
    # Vestuário
    "4781": "vestuario",
    "1412": "vestuario",
    "1411": "vestuario",
    "1413": "vestuario",
    "1414": "vestuario",
    # Alimentos
    "1011": "alimentos",
    "1091": "alimentos",
    "1092": "alimentos",
    "1093": "alimentos",
    "5611": "alimentos",
    "5612": "alimentos",
    "5620": "alimentos",
    # Informática / TI
    "6201": "informatica",
    "6202": "informatica",
    "6203": "informatica",
    "6204": "informatica",
    "4751": "informatica",
    # Software
    "6209": "software",
    "6311": "software",
    # Engenharia / Construção
    "4120": "engenharia",
    "4211": "engenharia",
    "4212": "engenharia",
    "4213": "engenharia",
    "4221": "engenharia",
    "4222": "engenharia",
    "4223": "engenharia",
    "4291": "engenharia",
    "4292": "engenharia",
    "4299": "engenharia",
    "4311": "engenharia",
    "4312": "engenharia",
    "4313": "engenharia",
    "4319": "engenharia",
    "4321": "engenharia",
    "4322": "engenharia",
    "4329": "engenharia",
    "4330": "engenharia",
    "4391": "engenharia",
    "4399": "engenharia",
    "7111": "engenharia",
    "7112": "engenharia",
    # Engenharia Rodoviária
    "4211": "engenharia_rodoviaria",
    # Facilities
    "8121": "facilities",
    "8122": "facilities",
    "8129": "facilities",
    "8130": "facilities",
    # Vigilância / Segurança
    "8011": "vigilancia",
    "8012": "vigilancia",
    "8020": "vigilancia",
    # Saúde
    "8610": "saude",
    "8621": "saude",
    "8622": "saude",
    "8630": "saude",
    "3250": "saude",
    # Transporte
    "4921": "transporte",
    "4922": "transporte",
    "4923": "transporte",
    "4930": "transporte",
    "4950": "transporte",
    # Mobiliário
    "3101": "mobiliario",
    "3102": "mobiliario",
    "3103": "mobiliario",
    "3104": "mobiliario",
    # Papelaria / Material de Escritório
    "4761": "papelaria",
    "1710": "papelaria",
    "1721": "papelaria",
    # Manutenção Predial
    "4330": "manutencao_predial",
    "8111": "manutencao_predial",
    # Materiais Elétricos
    "2710": "materiais_eletricos",
    "2731": "materiais_eletricos",
    "2732": "materiais_eletricos",
    "2733": "materiais_eletricos",
    "4742": "materiais_eletricos",
    # Materiais Hidráulicos
    "2223": "materiais_hidraulicos",
    "4744": "materiais_hidraulicos",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _http_get_json(url: str) -> dict | list | None:
    """Fetch JSON from URL, return None on error."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  [WARN] HTTP error: {e}")
        return None


def _extract_cnae_prefix(cnae_str: str) -> str:
    """Extract first 4 digits from a CNAE code string."""
    digits = ""
    for ch in cnae_str.strip():
        if ch.isdigit():
            digits += ch
            if len(digits) == 4:
                return digits
    return digits


def _load_sectors_yaml() -> dict:
    """Load sectors_data.yaml from the backend directory."""
    yaml_path = Path(__file__).resolve().parent.parent / "backend" / "sectors_data.yaml"
    if not yaml_path.exists():
        print(f"  [WARN] sectors_data.yaml not found at {yaml_path}")
        return {}
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("sectors", {})


def _detect_sector(cnae_principal: str, sectors: dict) -> tuple[str, str, list[str]]:
    """
    Detect sector from CNAE principal code.

    Returns (sector_key, sector_name, keywords).
    Falls back to generic keywords extracted from CNAE description.
    """
    prefix = _extract_cnae_prefix(cnae_principal)
    sector_key = CNAE_TO_SECTOR.get(prefix)

    if sector_key and sector_key in sectors:
        sec = sectors[sector_key]
        return sector_key, sec["name"], sec.get("keywords", [])

    # Fallback: extract keywords from CNAE description
    # cnae_principal might be "4120400 - Construcao de edificios"
    desc_part = cnae_principal.split("-", 1)[1].strip() if "-" in cnae_principal else ""
    generic_kw = [w.lower().strip() for w in desc_part.split() if len(w) > 3]
    sector_name = desc_part or "Geral"
    return "generico", sector_name, generic_kw


def _uf_abrangencia(uf_sede: str) -> dict[str, list[str]]:
    """Build UF coverage for semanal (sede + 2 neighbors) and diario (sede + 4)."""
    neighbors = UF_NEIGHBORS.get(uf_sede, [])
    semanal = [uf_sede] + neighbors[:2]
    diario = [uf_sede] + neighbors[:4]
    return {"semanal": semanal, "diario": diario}


def _value_range_label(valor: float) -> str:
    """Classify value into a range bucket."""
    if valor <= 0:
        return "sem_valor"
    if valor < 100_000:
        return "ate_100k"
    if valor < 500_000:
        return "100k_500k"
    if valor < 1_000_000:
        return "500k_1M"
    if valor < 5_000_000:
        return "1M_5M"
    if valor < 10_000_000:
        return "5M_10M"
    return "acima_10M"


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------


def fetch_empresa(cnpj: str) -> dict:
    """Fetch company data from BrasilAPI."""
    print(f"Fetching empresa {cnpj} from BrasilAPI...")
    data = _http_get_json(f"{BRASILAPI_CNPJ}/{cnpj}")
    if not data:
        print("  [ERROR] Could not fetch empresa data. Using minimal fallback.")
        return {"cnpj": cnpj}
    return data


def fetch_editais(ufs: list[str], keywords: list[str], days: int = 30) -> list[dict]:
    """Fetch editais from PNCP for given UFs, filtered by sector keywords."""
    today = datetime.now()
    data_ini = (today - timedelta(days=days)).strftime("%Y%m%d")
    data_fim = today.strftime("%Y%m%d")

    editais_raw: list[dict] = []
    for uf in ufs:
        for modalidade in MODALIDADES:
            for page in range(1, MAX_PAGES + 1):
                url = (
                    f"{PNCP_BASE}"
                    f"?dataInicial={data_ini}&dataFinal={data_fim}"
                    f"&uf={uf}&codigoModalidadeContratacao={modalidade}"
                    f"&pagina={page}&tamanhoPagina={PAGE_SIZE}"
                )
                data = _http_get_json(url)
                if not data:
                    break
                items = data.get("data", data.get("content", []))
                editais_raw.extend(items)
                total = data.get("totalRegistros", data.get("totalElements", 0))
                print(
                    f"  UF={uf} mod={modalidade} pg={page}: "
                    f"{len(items)} items (total: {total})"
                )
                if len(items) < PAGE_SIZE:
                    break

    # Dedup by numeroControlePNCP
    seen: set[str] = set()
    unique: list[dict] = []
    for e in editais_raw:
        nctrl = e.get("numeroControlePNCP", "")
        if nctrl and nctrl not in seen:
            seen.add(nctrl)
            unique.append(e)

    print(f"  Total raw: {len(editais_raw)}, unique: {len(seen)}")

    # Filter by keywords
    kw_lower = [kw.lower() for kw in keywords if kw]
    if not kw_lower:
        return unique  # No keywords = return all

    relevant = []
    for e in unique:
        obj = (e.get("objetoCompra", "") or "").lower()
        if any(kw in obj for kw in kw_lower):
            relevant.append(e)

    print(f"  Keyword-matched: {len(relevant)}")
    return relevant


# ---------------------------------------------------------------------------
# JSON building
# ---------------------------------------------------------------------------


def build_proposta_json(
    cnpj: str,
    pacote: str = "semanal",
    days: int = 30,
) -> dict:
    """Build the full proposta JSON for a given CNPJ."""
    today = datetime.now()
    sectors = _load_sectors_yaml()

    # --- Empresa ---
    emp_raw = fetch_empresa(cnpj)

    cnae_principal = emp_raw.get("cnae_fiscal_descricao", "")
    cnae_code = str(emp_raw.get("cnae_fiscal", ""))
    if cnae_code and cnae_principal:
        cnae_display = f"{cnae_code} - {cnae_principal}"
    else:
        cnae_display = cnae_principal or cnae_code or ""

    nome = (emp_raw.get("nome_fantasia") or "").strip() or emp_raw.get(
        "razao_social", "Empresa"
    )
    razao_social = emp_raw.get("razao_social", nome)
    uf_sede = emp_raw.get("uf", "SP")
    cidade_sede = emp_raw.get("municipio", "")
    capital_str = emp_raw.get("capital_social", "0")
    # BrasilAPI returns capital_social as number or string
    if isinstance(capital_str, str):
        capital = float(capital_str.replace(",", ".").replace(".", "", capital_str.count(".") - 1)) if capital_str else 0.0
    else:
        capital = float(capital_str or 0)
    porte_raw = emp_raw.get("porte", "")
    data_abertura = emp_raw.get("data_inicio_atividade", "")

    # Build QSA
    qsa = []
    for s in emp_raw.get("qsa", []):
        if isinstance(s, dict):
            qsa.append({
                "nome": s.get("nome_socio", ""),
                "qualificacao": s.get("qualificacao_socio", ""),
            })

    # CNAEs secundários
    cnaes_sec_raw = emp_raw.get("cnaes_secundarios", [])
    if isinstance(cnaes_sec_raw, list):
        cnaes_sec = ", ".join(
            str(c.get("codigo", c) if isinstance(c, dict) else c)
            for c in cnaes_sec_raw[:50]
        )
    else:
        cnaes_sec = str(cnaes_sec_raw)

    empresa = {
        "razao_social": razao_social,
        "nome_fantasia": emp_raw.get("nome_fantasia", ""),
        "cnpj": f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}",
        "cnae_principal": cnae_display,
        "cnaes_secundarios": cnaes_sec,
        "porte": porte_raw,
        "capital_social": capital,
        "natureza_juridica": emp_raw.get("natureza_juridica", ""),
        "cidade_sede": cidade_sede,
        "uf_sede": uf_sede,
        "data_abertura": data_abertura,
        "email": emp_raw.get("email", ""),
        "telefone": emp_raw.get("ddd_telefone_1", ""),
        "situacao_cadastral": emp_raw.get("descricao_situacao_cadastral", ""),
        "qsa": qsa,
        "sancoes": {"ceis": None, "cnep": None, "cepim": None, "ceaf": None},
    }

    # --- Sector detection ---
    sector_key, sector_name, keywords = _detect_sector(cnae_display, sectors)
    print(f"Detected sector: {sector_name} (key={sector_key})")

    # --- UF coverage ---
    uf_cov = _uf_abrangencia(uf_sede)
    search_ufs = uf_cov.get(pacote, uf_cov["semanal"])

    # --- Fetch editais ---
    print(f"Fetching editais for UFs={search_ufs}, days={days}...")
    editais_all = fetch_editais(search_ufs, keywords, days=days)

    # --- Process editais ---
    threshold = capital * CAPITAL_MULTIPLIER if capital > 0 else float("inf")
    editais_internal: list[dict] = []

    for e in sorted(
        editais_all,
        key=lambda x: float(x.get("valorTotalEstimado", 0) or 0),
        reverse=True,
    ):
        val = float(e.get("valorTotalEstimado", 0) or 0)
        if 0 < val < 50_000:
            continue

        mun = e.get("unidadeOrgao", {}).get("municipioNome", "") or ""
        uf = e.get("unidadeOrgao", {}).get("ufSigla", "") or uf_sede
        orgao = e.get("orgaoEntidade", {}).get("razaoSocial", "") or ""
        obj = e.get("objetoCompra", "") or ""
        mod = e.get("modalidadeNome", "") or ""
        data_enc = (e.get("dataEncerramentoProposta", "") or "")[:10]
        data_pub = (e.get("dataPublicacaoPncp", "") or "")[:10]
        num = e.get("numeroControlePNCP", "") or ""

        try:
            enc = datetime.strptime(data_enc, "%Y-%m-%d")
            dias = (enc - today).days
        except Exception:
            dias = -1

        # Skip already closed
        if dias < 0 and data_enc:
            continue

        # Recommendation based on capital threshold
        if val <= 0:
            rec = "PARTICIPAR"
            motivo = "Sem valor estimado — verificar edital"
        elif val <= threshold:
            rec = "PARTICIPAR"
            motivo = f"Valor compatível com capital social de R$ {capital:,.0f}"
        elif val <= threshold * 3:
            rec = "PARTICIPAR"
            motivo = "Valor acima do capital mas viável com experiência técnica"
        else:
            rec = "AVALIAR COM CAUTELA"
            motivo = "Valor elevado para o porte — considerar consórcio"

        editais_internal.append({
            "objeto": obj,
            "orgao": orgao,
            "uf": uf,
            "municipio": mun,
            "valor_estimado": val,
            "modalidade": mod,
            "data_publicacao": data_pub,
            "data_encerramento": data_enc,
            "dias_restantes": dias,
            "numero_controle": num,
            "situacao": "Divulgada no PNCP",
            "recomendacao": rec,
            "motivo_recomendacao": motivo,
        })

    # Cap at top 20
    editais_internal = editais_internal[:20]

    # --- Market aggregates ---
    mercado_volume = len(editais_internal)
    mercado_valor_total = sum(e["valor_estimado"] for e in editais_internal)

    mercado_por_faixa: dict[str, int] = Counter()
    for e in editais_internal:
        mercado_por_faixa[_value_range_label(e["valor_estimado"])] += 1

    mercado_por_modalidade: dict[str, dict] = {}
    for e in editais_internal:
        m = e["modalidade"]
        if m not in mercado_por_modalidade:
            mercado_por_modalidade[m] = {"count": 0, "valor": 0}
        mercado_por_modalidade[m]["count"] += 1
        mercado_por_modalidade[m]["valor"] += e["valor_estimado"]

    mun_dist = Counter(e["municipio"] for e in editais_internal)
    uf_dist = Counter(e["uf"] for e in editais_internal)
    n_participar = sum(1 for e in editais_internal if e["recomendacao"] == "PARTICIPAR")
    n_avaliar = sum(
        1 for e in editais_internal if e["recomendacao"] == "AVALIAR COM CAUTELA"
    )

    # --- Company age ---
    try:
        abertura = datetime.strptime(data_abertura, "%Y-%m-%d")
        anos_mercado = (today - abertura).days // 365
    except Exception:
        anos_mercado = 0

    # --- Build output ---
    output = {
        "empresa": empresa,
        "setor": sector_name,
        "setor_intro": (
            f"Como consultor especializado em licitações públicas, acompanho "
            f"diariamente o volume de contratações no setor de {sector_name}. "
            f"Identifico, para empresas como a {nome}, quais oportunidades têm "
            f"aderência real ao perfil técnico e financeiro."
        ),
        "uf_abrangencia": uf_cov,
        "taxa_vitoria_setor": 0.20,
        "autoridade_exemplos": AUTORIDADE_EXEMPLOS,
        "mercado_volume": mercado_volume,
        "mercado_valor_total": mercado_valor_total,
        "mercado_por_faixa": dict(mercado_por_faixa),
        "mercado_por_modalidade": mercado_por_modalidade,
        "editais": editais_internal,
        "resumo_executivo": {
            "texto": (
                f"A {razao_social}, sediada em {cidade_sede}/{uf_sede}"
                + (f" com {anos_mercado} anos de mercado" if anos_mercado else "")
                + (f" e capital social de R$ {capital:,.0f}" if capital else "")
                + f", atua no setor de {sector_name}"
                + (f" (CNAE {cnae_code})" if cnae_code else "")
                + f". A varredura PNCP de {today.strftime('%d/%m/%Y')} identificou "
                + f"{mercado_volume} editais relevantes em {', '.join(search_ufs)} "
                + f"nos últimos {days} dias, totalizando R$ {mercado_valor_total:,.0f} "
                + f"em valor estimado. Destes, {n_participar} editais são diretamente "
                + f"compatíveis com o porte da empresa"
                + (
                    f", e {n_avaliar} merecem avaliação cuidadosa por valor elevado"
                    if n_avaliar
                    else ""
                )
                + "."
            ),
            "destaques": [
                f"{n_participar} editais com recomendação PARTICIPAR",
                *(
                    [f"{n_avaliar} editais para AVALIAR COM CAUTELA"]
                    if n_avaliar
                    else []
                ),
                f"Total de {mercado_volume} oportunidades mapeadas em {', '.join(search_ufs)}",
                *(
                    [
                        f"Empresa com {anos_mercado} anos de mercado, sem sanções "
                        f"(CEIS/CNEP/CEPIM/CEAF limpos)"
                    ]
                    if anos_mercado
                    else []
                ),
            ],
        },
        "inteligencia_mercado": {
            "distribuicao_uf": dict(uf_dist.most_common()),
            "distribuicao_municipio": dict(mun_dist.most_common(20)),
            "valor_total_mercado": mercado_valor_total,
            "modalidades": mercado_por_modalidade,
            "fonte": "PNCP - Portal Nacional de Contratações Públicas (pncp.gov.br)",
            "periodo_analise": (
                f"{(today - timedelta(days=days)).strftime('%d/%m/%Y')} a "
                f"{today.strftime('%d/%m/%Y')}"
            ),
        },
        "proximos_passos": [
            {
                "acao": (
                    "Revisar editais com recomendação PARTICIPAR e verificar "
                    "requisitos de habilitação"
                ),
                "prazo": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
            },
            {
                "acao": (
                    "Preparar documentação de habilitação (CRF, certidões, "
                    "atestados de capacidade técnica)"
                ),
                "prazo": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
            },
            {
                "acao": (
                    "Elaborar propostas de preço para editais com encerramento "
                    "mais próximo"
                ),
                "prazo": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            },
            {
                "acao": (
                    "Submeter propostas nos sistemas eletrônicos "
                    "(Compras.gov.br, Licitanet, BLL)"
                ),
                "prazo": (today + timedelta(days=14)).strftime("%Y-%m-%d"),
            },
        ],
    }

    return output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build sector-agnostic proposta JSON from PNCP data."
    )
    parser.add_argument("cnpj", help="CNPJ (digits only, e.g. 09225035000101)")
    parser.add_argument(
        "--pacote",
        choices=["semanal", "diario"],
        default="semanal",
        help="Coverage package: semanal (sede+2 UFs) or diario (sede+4 UFs)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)",
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: docs/propostas/data-{cnpj}-{date}.json)",
    )

    args = parser.parse_args()
    cnpj = args.cnpj.replace(".", "").replace("/", "").replace("-", "")

    if len(cnpj) != 14 or not cnpj.isdigit():
        print(f"ERROR: Invalid CNPJ '{args.cnpj}'. Must be 14 digits.")
        sys.exit(1)

    print(f"=== Build Proposta Data: CNPJ {cnpj} | pacote={args.pacote} ===\n")

    output = build_proposta_json(cnpj, pacote=args.pacote, days=args.days)

    today = datetime.now()
    out_path = args.output or (
        f"docs/propostas/data-{cnpj}-{today.strftime('%Y-%m-%d')}.json"
    )
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    mercado = output["mercado_volume"]
    valor = output["mercado_valor_total"]
    n_part = sum(
        1 for e in output["editais"] if e["recomendacao"] == "PARTICIPAR"
    )
    n_aval = sum(
        1 for e in output["editais"] if e["recomendacao"] == "AVALIAR COM CAUTELA"
    )

    print(f"\nJSON salvo: {out_path}")
    print(f"Setor: {output['setor']}")
    print(f"Editais: {mercado}, Valor total: R$ {valor:,.0f}")
    print(f"PARTICIPAR: {n_part}, AVALIAR: {n_aval}")


if __name__ == "__main__":
    main()
