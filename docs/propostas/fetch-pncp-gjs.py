"""
Fetch PNCP editais for GJS CONSTRUCOES E COMERCIO LTDA (09.225.035/0001-01)
Busca editais de construcao civil em MG e estados proximos.
"""
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl
import datetime
import re
import sys

CNPJ = "09225035000101"
EMPRESA = "GJS CONSTRUCOES E COMERCIO LTDA"
MUNICIPIO_SEDE = "Tumiritinga/MG"
CNAE = "4120400"

BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

DATA_INICIAL = "20260210"
DATA_FINAL = "20260312"
TAMANHO_PAGINA = 50

MODALIDADES = [
    (4, "Concorrencia"),
    (6, "Pregao"),
]

KEYWORDS = [
    "construcao", "obra", "reforma", "edificacao", "pavimentacao",
    "drenagem", "terraplenagem", "instalacoes", "demolicao",
    "manutencao predial", "construcao civil", "cbuq", "habitacional",
    "ampliacao", "estrutura metalica", "saneamento", "esgoto",
    "recuperacao", "restauracao", "urbanizacao", "infraestrutura",
]

# Priority UFs: MG first, then nearby states
UF_PRIORITY = {
    "MG": 1, "ES": 2, "RJ": 3, "SP": 4, "GO": 5, "BA": 6,
}

def matches_keywords(text):
    if not text:
        return False
    text_lower = text.lower()
    for kw in KEYWORDS:
        if kw in text_lower:
            return True
    return False

def fetch_pncp(modalidade_id, pagina=1):
    params = {
        "dataInicial": DATA_INICIAL,
        "dataFinal": DATA_FINAL,
        "tamanhoPagina": str(TAMANHO_PAGINA),
        "pagina": str(pagina),
        "modalidadeId": str(modalidade_id),
    }
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    print(f"  Fetching: {url}")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def main():
    all_results = []
    filtered = []

    for mod_id, mod_name in MODALIDADES:
        print(f"\n--- Modalidade {mod_id} ({mod_name}) ---")
        pagina = 1
        while pagina <= 5:  # max 5 pages per modalidade
            data = fetch_pncp(mod_id, pagina)
            if data is None:
                print(f"  API returned error/null for page {pagina}. Stopping this modalidade.")
                break

            items = data if isinstance(data, list) else data.get("data", data.get("resultado", []))
            if not items or not isinstance(items, list):
                print(f"  No more results on page {pagina}.")
                break

            print(f"  Page {pagina}: {len(items)} items")
            all_results.extend(items)

            for item in items:
                objeto = item.get("objetoCompra", "") or item.get("objeto", "")
                if matches_keywords(objeto):
                    uf = item.get("unidadeOrgao", {}).get("ufSigla", "") or item.get("uf", "")
                    municipio = item.get("unidadeOrgao", {}).get("municipioNome", "") or item.get("municipio", "")
                    orgao = item.get("orgaoEntidade", {}).get("razaoSocial", "") or item.get("orgao", "")
                    valor = item.get("valorTotalEstimado", 0)

                    filtered.append({
                        "objetoCompra": objeto,
                        "orgao": orgao,
                        "uf": uf,
                        "municipio": municipio,
                        "valorTotalEstimado": valor,
                        "modalidadeNome": item.get("modalidadeNome", mod_name),
                        "dataPublicacaoPncp": item.get("dataPublicacaoPncp", ""),
                        "dataEncerramentoProposta": item.get("dataEncerramentoProposta", ""),
                        "dataAberturaProposta": item.get("dataAberturaProposta", ""),
                        "numeroControlePNCP": item.get("numeroControlePNCP", ""),
                    })

            if len(items) < TAMANHO_PAGINA:
                break
            pagina += 1

    # Sort: prioritize MG and nearby states
    def sort_key(item):
        uf = item.get("uf", "")
        priority = UF_PRIORITY.get(uf, 99)
        valor = item.get("valorTotalEstimado", 0) or 0
        return (priority, -valor)

    filtered.sort(key=sort_key)

    # UF breakdown
    uf_counts = {}
    for item in filtered:
        uf = item.get("uf", "??")
        uf_counts[uf] = uf_counts.get(uf, 0) + 1

    output = {
        "meta": {
            "empresa": EMPRESA,
            "cnpj": CNPJ,
            "cnae": CNAE,
            "municipio_sede": MUNICIPIO_SEDE,
            "data_consulta": datetime.date.today().isoformat(),
            "fontes": [f"PNCP modalidade {m[0]} ({m[1]})" for m in MODALIDADES],
            "periodo": f"{DATA_INICIAL[:4]}-{DATA_INICIAL[4:6]}-{DATA_INICIAL[6:]} a {DATA_FINAL[:4]}-{DATA_FINAL[4:6]}-{DATA_FINAL[6:]}",
            "total_bruto": len(all_results),
            "total_filtrado": len(filtered),
            "keywords_construcao": KEYWORDS,
            "uf_breakdown": uf_counts,
        },
        "resultados": filtered,
    }

    outfile = f"pncp-raw-{CNPJ}.json"
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n=== DONE ===")
    print(f"Total bruto: {len(all_results)}")
    print(f"Filtrados (keywords construcao): {len(filtered)}")
    print(f"UF breakdown: {uf_counts}")
    print(f"Saved to: {outfile}")

if __name__ == "__main__":
    main()
