"""Search PNCP contract history for a CNPJ using same strategies as collect-report-data.py"""
import asyncio, httpx, json, os, sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv("backend/.env")

CNPJ = sys.argv[1].replace(".", "").replace("/", "").replace("-", "") if len(sys.argv) > 1 else "33750637000154"
CNPJ_FMT = f"{CNPJ[:2]}.{CNPJ[2:5]}.{CNPJ[5:8]}/{CNPJ[8:12]}-{CNPJ[12:14]}"
BASE = "https://pncp.gov.br/api/consulta/v1"
PT_TOKEN = os.environ.get("PORTAL_TRANSPARENCIA_API_KEY", "")


async def fetch_company_profile(client):
    """OpenCNPJ lookup"""
    try:
        r = await client.get(f"https://api.opencnpj.com/v2/{CNPJ}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}


async def strategy_pncp_date(client, start, end, label=""):
    """Strategy 1: PNCP /contratos with date window + cnpjFornecedor"""
    contracts = []
    for page in range(1, 11):
        url = (
            f"{BASE}/contratos"
            f"?dataInicial={start.strftime('%Y%m%d')}"
            f"&dataFinal={end.strftime('%Y%m%d')}"
            f"&cnpjFornecedor={CNPJ}"
            f"&pagina={page}&tamanhoPagina=500"
        )
        try:
            r = await client.get(url, timeout=30)
            if r.status_code != 200:
                print(f"  {label} p={page} -> {r.status_code}")
                break
            data = r.json()
            items = data if isinstance(data, list) else data.get("data", data.get("items", []))
            if not items:
                break
            matched = [
                c for c in items
                if c.get("fornecedor", {}).get("cnpjCpfFornecedor", "").replace(".", "").replace("/", "").replace("-", "") == CNPJ
            ]
            print(f"  {label} p={page}: {len(items)} raw, {len(matched)} matched")
            contracts.extend(matched)
            if len(items) < 500:
                break
        except httpx.ReadTimeout:
            print(f"  {label} p={page}: timeout")
            continue
        except Exception as e:
            print(f"  {label} p={page}: {e}")
            break
    return contracts


async def strategy_razao_social(client, razao):
    """Strategy 2: PNCP /contratacoes by razao social"""
    results = []
    razao_short = razao[:30]
    end_s = datetime.now().strftime("%Y%m%d")
    start_s = (datetime.now() - timedelta(days=730)).strftime("%Y%m%d")
    for mod in [4, 5, 6, 7, 8, 12]:
        url = (
            f"{BASE}/contratacoes/publicacao"
            f"?dataInicial={start_s}&dataFinal={end_s}"
            f"&q={razao_short}"
            f"&codigoModalidadeContratacao={mod}"
            f"&pagina=1&tamanhoPagina=50"
        )
        try:
            r = await client.get(url, timeout=20)
            if r.status_code == 200:
                data = r.json()
                items = data if isinstance(data, list) else data.get("data", data.get("items", []))
                if items:
                    print(f"  razao_social mod={mod}: {len(items)} resultados")
                    results.extend(items)
            else:
                print(f"  razao_social mod={mod}: {r.status_code}")
        except Exception as e:
            print(f"  razao_social mod={mod}: {e}")
    return results


async def strategy_portal_transparencia(client):
    """Strategy 3: Portal da Transparencia federal contracts"""
    if not PT_TOKEN:
        print("  PT: no token")
        return []
    try:
        r = await client.get(
            f"https://api.portaldatransparencia.gov.br/api-de-dados/contratos/cpf-cnpj?cpfCnpj={CNPJ_FMT}&pagina=1",
            headers={"chave-api-dados": PT_TOKEN, "Accept": "application/json"},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return data
        print(f"  PT: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"  PT: {e}")
    return []


async def strategy_comprasgov(client):
    """Strategy 4: ComprasGov"""
    try:
        r = await client.get(
            f"https://dadosabertos.compras.gov.br/modulo-contrato/4.0/contratos?cnpj_contratado={CNPJ_FMT}&pagina=1",
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            items = data.get("resultado", data.get("data", []))
            return items if isinstance(items, list) else []
        print(f"  ComprasGov: {r.status_code}")
    except Exception as e:
        print(f"  ComprasGov: {e}")
    return []


async def main():
    print("=" * 60)
    print(f"Historico de Contratos - CNPJ {CNPJ_FMT}")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30) as client:
        # Company profile
        print("\n[1] Perfil da empresa (OpenCNPJ)")
        emp = await fetch_company_profile(client)
        razao = emp.get("razao_social", "")
        print(f"  Razao Social: {razao}")
        print(f"  Nome Fantasia: {emp.get('nome_fantasia', '-')}")
        print(f"  Porte: {emp.get('porte', '?')}")
        print(f"  Capital Social: {emp.get('capital_social', '?')}")
        print(f"  CNAE: {emp.get('cnae_fiscal', '?')} - {emp.get('cnae_fiscal_descricao', '?')}")
        print(f"  Inicio Atividade: {emp.get('data_inicio_atividade', '?')}")
        print(f"  Situacao: {emp.get('situacao_cadastral', '?')}")
        print(f"  UF: {emp.get('uf', '?')} | Municipio: {emp.get('municipio', '?')}")

        # Strategy 1: PNCP date windows
        print("\n[2] PNCP /contratos (0-12 meses)")
        now = datetime.now()
        c1 = await strategy_pncp_date(client, now - timedelta(days=365), now, "0-12m")

        print("\n[3] PNCP /contratos (12-24 meses)")
        c2 = await strategy_pncp_date(client, now - timedelta(days=730), now - timedelta(days=365), "12-24m")

        print("\n[4] PNCP /contratos (24-48 meses)")
        c3 = await strategy_pncp_date(client, now - timedelta(days=1460), now - timedelta(days=730), "24-48m")

        all_pncp = c1 + c2 + c3

        # Strategy 2: razao social
        print("\n[5] PNCP /contratacoes por razao social")
        if razao:
            contratacoes = await strategy_razao_social(client, razao)
        else:
            contratacoes = []

        # Strategy 3: Portal Transparencia
        print("\n[6] Portal da Transparencia (contratos federais)")
        pt_contracts = await strategy_portal_transparencia(client)
        print(f"  Contratos federais: {len(pt_contracts)}")

        # Strategy 4: ComprasGov
        print("\n[7] ComprasGov")
        cg_contracts = await strategy_comprasgov(client)
        print(f"  ComprasGov: {len(cg_contracts)}")

        # Consolidated
        print("\n" + "=" * 60)
        print(f"CONSOLIDADO")
        print(f"  PNCP /contratos: {len(all_pncp)}")
        print(f"  PNCP /contratacoes (razao social): {len(contratacoes)}")
        print(f"  Portal Transparencia: {len(pt_contracts)}")
        print(f"  ComprasGov: {len(cg_contracts)}")
        print(f"  TOTAL: {len(all_pncp) + len(pt_contracts) + len(cg_contracts)}")

        if all_pncp:
            print(f"\n--- Contratos PNCP ({len(all_pncp)}) ---")
            total_valor = 0
            ufs = set()
            orgaos = set()
            for i, c in enumerate(all_pncp):
                orgao = c.get("orgaoEntidade", {}).get("razaoSocial", "?")[:50]
                obj = c.get("objetoContrato", "")[:70]
                val = c.get("valorInicial", 0) or 0
                uf = c.get("unidadeFederativa", "?")
                vigencia = c.get("dataVigenciaInicio", "?")
                total_valor += float(val) if val else 0
                ufs.add(uf)
                orgaos.add(orgao)
                if i < 30:
                    print(f"  {i+1}. {orgao}")
                    print(f"     {obj}")
                    print(f"     R$ {float(val):,.2f} | UF={uf} | Vigencia: {vigencia}")
            print(f"\n  Valor total: R$ {total_valor:,.2f}")
            print(f"  UFs: {', '.join(sorted(ufs))}")
            print(f"  Orgaos distintos: {len(orgaos)}")

        if pt_contracts:
            print(f"\n--- Contratos Federais ({len(pt_contracts)}) ---")
            for i, c in enumerate(pt_contracts[:15]):
                obj = c.get("objeto", c.get("descricaoObjeto", ""))[:70]
                val = c.get("valorInicial", c.get("valor", "?"))
                orgao = c.get("unidadeGestora", {}).get("nome", "?")[:50]
                print(f"  {i+1}. {orgao}")
                print(f"     {obj}")
                print(f"     R$ {val}")

        if contratacoes:
            print(f"\n--- Contratacoes (razao social) ({len(contratacoes)}) ---")
            for i, c in enumerate(contratacoes[:10]):
                orgao = c.get("orgaoEntidade", {}).get("razaoSocial", "?")[:50]
                obj = c.get("objetoCompra", "")[:70]
                val = c.get("valorTotalEstimado", 0)
                print(f"  {i+1}. {orgao} | {obj} | R$ {val}")


asyncio.run(main())
