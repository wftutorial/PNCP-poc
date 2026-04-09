#!/usr/bin/env python3
"""Parse concatenated PNCP JSON responses, filter for construction, output top candidates."""
import json, sys

# Read all JSON objects from concatenated input
raw = sys.stdin.read()
decoder = json.JSONDecoder()
chunks = []
pos = 0
while pos < len(raw):
    raw_stripped = raw[pos:].lstrip()
    if not raw_stripped:
        break
    try:
        obj, end = decoder.raw_decode(raw_stripped)
        chunks.append(obj)
        pos += len(raw) - len(raw_stripped) - pos + end
    except json.JSONDecodeError:
        pos += 1

kw = ['construc', 'obra', 'reform', 'engenharia', 'paviment', 'edificac', 'predial',
      'infraestrutura', 'drenagem', 'saneamento', 'restaura', 'manutenc']
all_found = []

for raw_obj in chunks:
    items = raw_obj.get('data', []) if isinstance(raw_obj, dict) else raw_obj
    if not isinstance(items, list):
        continue
    for item in items:
        obj = (item.get('objetoCompra', '') or '').lower()
        if any(k in obj for k in kw):
            enc = item.get('dataEncerramentoProposta', '') or ''
            if enc >= '2026-03-12':
                ue = item.get('unidadeOrgao', {}) or {}
                oe = item.get('orgaoEntidade', {}) or {}
                all_found.append({
                    'objeto': item.get('objetoCompra', '')[:250],
                    'orgao': oe.get('razaoSocial', '')[:80],
                    'cnpj_orgao': oe.get('cnpj', ''),
                    'uf': ue.get('ufSigla', ''),
                    'cidade': ue.get('municipioNome', ''),
                    'valor': item.get('valorTotalEstimado', 0) or 0,
                    'encerramento': enc[:10],
                    'ano': item.get('anoCompra', ''),
                    'seq': item.get('sequencialCompra', ''),
                    'modalidade': item.get('modalidadeNome', ''),
                    'link': item.get('linkSistemaOrigem', '') or '',
                    'pncp': item.get('numeroControlePNCP', ''),
                })

# Dedup
seen = set()
unique = []
for f in all_found:
    key = f['pncp']
    if key and key not in seen:
        seen.add(key)
        unique.append(f)
    elif not key:
        unique.append(f)

# Stats
ufs = {}
for f in unique:
    ufs[f['uf']] = ufs.get(f['uf'], 0) + 1

vals = [f['valor'] for f in unique if f['valor'] > 0]
print(f'Total editais abertos construcao: {len(unique)}')
print(f'By UF: {dict(sorted(ufs.items(), key=lambda x: -x[1]))}')
if vals:
    sv = sorted(vals)
    print(f'Valor min: R${min(vals):,.2f} | max: R${max(vals):,.2f} | mediana: R${sv[len(sv)//2]:,.2f}')
    print(f'Valor total em jogo: R${sum(vals):,.2f}')

# Prioritize PR/SC/SP/RS/MG
priority_ufs = {'PR', 'SC', 'SP', 'RS', 'MG', 'RJ'}
prioritized = sorted(unique, key=lambda x: (0 if x['uf'] in priority_ufs else 1, -x['valor']))

print(f'\n=== TOP 25 EDITAIS (prioridade Sul/Sudeste + valor) ===')
for i, f in enumerate(prioritized[:25]):
    v = f'R${f["valor"]:,.2f}' if f['valor'] > 0 else 'Sigiloso'
    print(f'\n{i+1}. [{f["uf"]}] {f["cidade"]} | {v} | Enc: {f["encerramento"]} | {f["modalidade"]}')
    print(f'   {f["objeto"][:160]}')
    print(f'   Orgao: {f["orgao"][:60]}')
    print(f'   Link PNCP: https://pncp.gov.br/app/editais/{f["cnpj_orgao"]}/{f["ano"]}/{f["seq"]}')

# Save JSON
with open('D:/pncp-poc/docs/reports/pncp_construction_results.json', 'w', encoding='utf-8') as out:
    json.dump(prioritized, out, ensure_ascii=False, indent=2)
print(f'\nSaved {len(prioritized)} editais')
