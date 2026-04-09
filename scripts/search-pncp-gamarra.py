#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Search PNCP for construction bids relevant to GAMARRA CONSTRUTORA E LOCADORA LTDA"""

import json, urllib.request, time, sys, io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

KEYWORDS = [
    'construcao', 'construção', 'reforma', 'obra', 'pavimentacao', 'pavimentação',
    'engenharia', 'edificacao', 'edificação', 'ampliacao', 'ampliação',
    'demolicao', 'demolição', 'terraplanagem', 'drenagem', 'saneamento',
    'asfalto', 'asfaltamento', 'recapeamento', 'alvenaria', 'concreto',
    'impermeabilizacao', 'impermeabilização', 'instalacao eletrica',
    'instalacao hidraulica', 'pintura predial', 'cobertura metalica',
    'revitalizacao', 'revitalização', 'restauracao', 'restauração',
    'manutencao predial', 'manutenção predial', 'locacao de equipamento',
    'locação de equipamento', 'locacao de maquina', 'locação de máquina',
    'escavacao', 'escavação', 'aterro',
    'urbanizacao', 'urbanização', 'calcamento', 'calçamento',
    'infraestrutura', 'sondagem', 'topografia'
]

DATA_FINAL = '20260311'
DATA_INICIAL = '20260209'
BASE = 'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao'

all_results = []
seen = set()

for mod in [4, 5, 6, 8]:
    mod_name = {4:'Concorrência', 5:'Pregão Eletrônico', 6:'Pregão Presencial', 8:'Inexigibilidade'}[mod]
    print(f'Buscando modalidade {mod} ({mod_name})...', flush=True)
    for page in range(1, 11):
        url = f'{BASE}?dataInicial={DATA_INICIAL}&dataFinal={DATA_FINAL}&codigoModalidadeContratacao={mod}&pagina={page}&tamanhoPagina=50'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SmartLic/1.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            items = data.get('data', [])
            if not items:
                print(f'  Pagina {page}: 0 items, parando', flush=True)
                break
            count = 0
            for item in items:
                obj = (item.get('objetoCompra') or '').lower()
                if any(kw in obj for kw in KEYWORDS):
                    key = item.get('numeroControlePNCP', '')
                    if key and key not in seen:
                        seen.add(key)
                        orgao = item.get('orgaoEntidade', {})
                        all_results.append({
                            'objeto': item.get('objetoCompra', ''),
                            'orgao': orgao.get('razaoSocial', ''),
                            'cnpjOrgao': orgao.get('cnpj', item.get('cnpjCompra', '')),
                            'uf': item.get('unidadeOrgao', {}).get('ufSigla', ''),
                            'municipio': item.get('unidadeOrgao', {}).get('municipioNome', ''),
                            'valorEstimado': item.get('valorTotalEstimado', 0),
                            'modalidade': mod_name,
                            'dataAbertura': item.get('dataAberturaProposta', ''),
                            'dataEncerramento': item.get('dataEncerramentoProposta', ''),
                            'dataPublicacao': item.get('dataPublicacaoPncp', ''),
                            'anoCompra': item.get('anoCompra', ''),
                            'sequencialCompra': item.get('sequencialCompra', ''),
                            'cnpjCompra': orgao.get('cnpj', ''),
                            'numeroControlePNCP': key,
                            'linkSistemaOrigem': item.get('linkSistemaOrigem', ''),
                            'fonte': 'PNCP'
                        })
                        count += 1
            print(f'  Pagina {page}: {len(items)} items, {count} construcao', flush=True)
            if len(items) < 50:
                break
        except Exception as e:
            print(f'Error page {page} mod {mod}: {e}', flush=True)
            break
        time.sleep(0.5)

print(f'\n=== TOTAL RESULTADOS PNCP (construcao): {len(all_results)} ===\n', flush=True)

all_results.sort(key=lambda x: float(x.get('valorEstimado') or 0), reverse=True)

for i, r in enumerate(all_results):
    valor = float(r.get('valorEstimado') or 0)
    valor_str = f'R$ {valor:,.2f}' if valor > 0 else 'Nao informado'
    obj_clean = r['objeto'].replace('\u200b', '').strip()[:200]
    cnpj = r.get('cnpjCompra') or r.get('cnpjOrgao','')
    ano = r.get('anoCompra','')
    seq = r.get('sequencialCompra','')
    link = f'https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}' if cnpj and ano and seq else ''

    print(f'\n--- Edital {i+1} ---')
    print(f'Objeto: {obj_clean}')
    print(f'Orgao: {r["orgao"]}')
    print(f'UF: {r["uf"]} | Municipio: {r["municipio"]}')
    print(f'Valor: {valor_str}')
    print(f'Modalidade: {r["modalidade"]}')
    print(f'Abertura: {r["dataAbertura"]} | Encerramento: {r["dataEncerramento"]}')
    print(f'PNCP: {r["numeroControlePNCP"]}')
    print(f'Ano/Seq: {ano}/{seq}')
    if link:
        print(f'Link: {link}')

with open('docs/reports/pncp-results-26420889000150.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
print(f'\nSalvo em docs/reports/pncp-results-26420889000150.json')
