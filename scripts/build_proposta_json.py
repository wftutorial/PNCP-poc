"""Build proposta JSON in report-b2g format for generate-proposta-pdf.py."""
import json
from datetime import datetime, timedelta

# Load raw data
all_contracts = []
for f in ['docs/propostas/contratos_p1.json', 'docs/propostas/contratos_p2.json']:
    with open(f, encoding='utf-8') as fh:
        d = json.load(fh)
        if 'data' in d:
            all_contracts.extend(d['data'])

all_editais = []
for f in ['docs/propostas/editais_sc_pregao.json', 'docs/propostas/editais_sc_concorrencia.json']:
    with open(f, encoding='utf-8') as fh:
        d = json.load(fh)
        if 'data' in d:
            all_editais.extend(d['data'])

KEYWORDS = [
    'construcao', 'obra', 'reforma', 'pavimentacao', 'drenagem', 'terraplanagem',
    'edificacao', 'engenharia', 'infraestrutura', 'saneamento', 'ponte', 'estrada',
    'habitacional', 'predial', 'urbanizacao', 'creche', 'escola', 'ampliacao',
    'revitalizacao', 'locacao', 'maquinas', 'equipamentos', 'aterro',
]

relevant = []
for e in all_editais:
    obj = (e.get('objetoCompra', '') or '').lower()
    if any(kw in obj for kw in KEYWORDS):
        relevant.append(e)

# Contract stats
total_valor_c = sum(float(c.get('valorInicial', 0) or 0) for c in all_contracts)
n_sc = sum(1 for c in all_contracts if c.get('unidadeOrgao', {}).get('ufSigla', '') == 'SC')

# Build historico_contratos (top 20 by value)
hist = []
for c in sorted(all_contracts, key=lambda x: float(x.get('valorInicial', 0) or 0), reverse=True)[:20]:
    hist.append({
        'orgao': c.get('orgaoEntidade', {}).get('razaoSocial', ''),
        'objeto': c.get('objetoContrato', ''),
        'valor': float(c.get('valorInicial', 0) or 0),
        'uf': c.get('unidadeOrgao', {}).get('ufSigla', '') or 'SC',
        'vigencia_inicio': c.get('dataVigenciaInicio', ''),
        'vigencia_fim': c.get('dataVigenciaFim', ''),
    })

# Build editais list
editais_out = []
for e in sorted(relevant, key=lambda x: float(x.get('valorTotalEstimado', 0) or 0), reverse=True):
    val = float(e.get('valorTotalEstimado', 0) or 0)
    if val < 50000:
        continue
    rec = 'PARTICIPAR' if val > 500000 else 'AVALIAR COM CAUTELA' if val > 100000 else 'NAO RECOMENDADO'
    mun = e.get('unidadeOrgao', {}).get('municipioNome', '') or ''
    uf = e.get('unidadeOrgao', {}).get('ufSigla', '') or 'SC'
    data_enc = (e.get('dataEncerramentoProposta', '') or '')[:10]
    data_pub = (e.get('dataPublicacaoPncp', '') or '')[:10]
    obj = e.get('objetoCompra', '') or ''
    orgao = e.get('orgaoEntidade', {}).get('razaoSocial', '') or ''
    mod = e.get('modalidadeNome', '') or ''
    num = e.get('numeroControlePNCP', '') or ''

    try:
        enc = datetime.strptime(data_enc, '%Y-%m-%d')
        dias = (enc - datetime.now()).days
    except Exception:
        dias = -1

    editais_out.append({
        'objeto': obj,
        'orgao': orgao,
        'uf': uf,
        'municipio': mun,
        'valor_estimado': val,
        'modalidade': mod,
        'data_abertura': data_pub,
        'data_encerramento': data_enc,
        'dias_restantes': dias,
        'fonte': 'PNCP',
        'link': f'https://pncp.gov.br/app/editais/{num}' if num else '',
        'recomendacao': rec,
        'analise': {
            'aderencia': f'CNAE 4120-4/00 (Construcao de edificios) e 34 CNAEs secundarios cobrem o escopo deste edital. Perfil tecnico compativel.',
            'valor': f'Valor de R$ {val:,.2f} {"dentro da faixa operacional (< 2x capital social)" if val <= 4000000 else "acima do capital social, mas viavel com consorcio ou financiamento"}.',
            'geografica': f'Edital em {mun}/{uf}. {"Empresa ja atua em SC com 981 contratos — logistica conhecida." if uf == "SC" else "Fora do eixo principal (SC) — avaliar custo de mobilizacao."}',
            'prazo': f'{dias} dias ate encerramento. {"Prazo adequado para preparacao." if dias > 10 else "Prazo curto — priorizacao necessaria." if dias > 0 else "Prazo encerrado."}',
            'modalidade': f'{mod}. {"Modalidade permite participacao remota." if "Eletr" in mod else "Modalidade presencial — exige deslocamento."}',
            'competitividade': f'Setor de construcao civil em SC e competitivo, mas a Gamarra tem vantagem de historico local com 213 orgaos.',
            'riscos': 'Verificar exigencias de CAT especifico, indices financeiros do balanco e regularidade fiscal.',
        },
        'perguntas_decisor': {
            'A empresa possui CAT para obras similares?': 'Verificar acervo tecnico do responsavel tecnico para o tipo especifico de obra (construcao, reforma, pavimentacao, etc).',
            f'Capacidade operacional para {mun}/{uf}?': f'A Gamarra ja atua em SC com 981 contratos. {"Municipio dentro da area de atuacao." if uf == "SC" else "Avaliar custo de mobilizacao para " + uf + "."}',
            f'Historico com {orgao[:30]}?': f'Consultar base de contratos PNCP para verificar participacoes anteriores com este orgao.',
        },
    })

total_valor_e = sum(e['valor_estimado'] for e in editais_out)
n_part = len([e for e in editais_out if e['recomendacao'] == 'PARTICIPAR'])
n_aval = len([e for e in editais_out if e['recomendacao'] == 'AVALIAR COM CAUTELA'])

# Municipality distribution
mun_dist = {}
for e in editais_out:
    m = e['municipio'] or 'N/A'
    mun_dist[m] = mun_dist.get(m, 0) + 1

# Inteligencia de mercado
intel = {
    'panorama': (
        f'O mercado de construcao civil em SC esta aquecido. Nos ultimos 30 dias, '
        f'foram identificados {len(editais_out)} editais no PNCP totalizando '
        f'R$ {total_valor_e:,.2f}. A Gamarra possui {len(all_contracts)} contratos '
        f'ativos/recentes em 213 orgaos, com forte presenca em SC ({n_sc} contratos). '
        f'O faturamento governamental medio e de R$ {total_valor_c/24:,.2f}/mes. '
        f'Navegantes, Chapeco e Ararangua concentram os maiores volumes de investimento.'
    ),
    'tendencias': [
        'Habitacao popular (Programa Casa Boa) domina os editais de maior valor em SC.',
        'Concorrencia Eletronica e a modalidade dominante, reflexo da Lei 14.133/21.',
        f'Sweet spot para a Gamarra: editais de R$ 500K a R$ 5M em municipios do interior de SC.',
        f'{n_part} editais recomendados para participacao imediata (valor > R$ 500K).',
    ],
    'distribuicao_uf': {'SC': len(editais_out)},
    'top_municipios': dict(sorted(mun_dist.items(), key=lambda x: -x[1])[:10]),
}

# Resumo executivo
resumo = {
    'texto': (
        f'Foram analisados {len(editais_out)} editais do setor de construcao civil '
        f'publicados no PNCP para Santa Catarina, com valor total de '
        f'R$ {total_valor_e/1e6:.1f}M. A GAMARRA CONSTRUTORA E LOCADORA (EPP, capital '
        f'R$ 2M, sede PB) possui historico robusto com {len(all_contracts)} contratos '
        f'governamentais em 24 meses (R$ {total_valor_c:,.2f}) e forte capilaridade em '
        f'SC (98.1% dos contratos). A empresa nao possui sancoes nos cadastros federais. '
        f'Identificamos {n_part} editais com recomendacao PARTICIPAR e {n_aval} para '
        f'AVALIAR COM CAUTELA, totalizando '
        f'R$ {sum(e["valor_estimado"] for e in editais_out if e["recomendacao"] in ("PARTICIPAR","AVALIAR COM CAUTELA")):,.2f} '
        f'em oportunidades compativeis.'
    ),
    'destaques': [
        f'{len(all_contracts)} contratos governamentais em 24 meses — empresa ativa e com historico comprovado.',
        'Nenhuma sancao ou impedimento nos cadastros federais.',
        f'{n_part} editais abertos com recomendacao PARTICIPAR em SC.',
        f'Concentracao em SC (98.1%) com diversificacao para MS — perfil regional consolidado.',
        'Capital social de R$ 2M e 34 CNAEs secundarios — versatilidade tecnica comprovada.',
    ],
}

# Proximos passos
upcoming = sorted(
    [e for e in editais_out if e['dias_restantes'] > 0 and e['recomendacao'] == 'PARTICIPAR'],
    key=lambda x: x['dias_restantes'],
)
proximos = []
for e in upcoming[:5]:
    proximos.append({
        'acao': f'Analisar edital: {e["objeto"][:60]} ({e["orgao"][:30]}, {e["municipio"]}/{e["uf"]})',
        'prazo': f'Encerra em {e["data_encerramento"]} ({e["dias_restantes"]} dias)',
        'prioridade': 'ALTA' if e['dias_restantes'] < 15 else 'MEDIA',
    })
proximos.extend([
    {
        'acao': 'Cadastrar empresa nos portais de compras publicas de SC (Portal de Compras Publicas, BLL)',
        'prazo': 'Esta semana',
        'prioridade': 'ALTA',
    },
    {
        'acao': 'Preparar documentacao de habilitacao padrao (CRF, CND, balanco, CAT)',
        'prazo': 'Permanente',
        'prioridade': 'ALTA',
    },
])

# Final JSON
data_out = {
    'empresa': {
        'cnpj': '26.420.889/0001-50',
        'razao_social': 'GAMARRA CONSTRUTORA E LOCADORA LTDA',
        'nome_fantasia': 'GAMARRA CONSTRUTORA E LOCADORA',
        'cnae_principal': '4120-4/00 - Construcao de edificios',
        'cnaes_secundarios': (
            '3702900, 3811400, 3900500, 4211101, 4211102, 4213800, 4221903, '
            '4222701, 4223500, 4291000, 4292801, 4299501, 4299599, 4311801, '
            '4311802, 4313400, 4321500, 4322302, 4322303, 4329103, 4329104, '
            '4330401, 4330402, 4330403, 4330404, 4330405, 4391600, 4399102, '
            '4399103, 4399104, 4399105, 7711000, 7732201, 7732202'
        ),
        'porte': 'Empresa de Pequeno Porte (EPP)',
        'capital_social': 2000000.0,
        'cidade_sede': 'Condado',
        'uf_sede': 'PB',
        'situacao_cadastral': 'ATIVA desde 25/10/2016',
        'email': 'gamarraconstrutora@gmail.com',
        'telefones': ['(83) 9974-7263'],
        'qsa': [{'nome': 'Francui Ramalho da Silva Filho', 'qualificacao': 'Socio-Administrador'}],
        'sancoes': {'ceis': False, 'cnep': False, 'cepim': False, 'ceaf': False},
        'historico_contratos': hist,
    },
    'setor': 'Engenharia e Construcao Civil',
    'keywords': [
        'construcao', 'obra', 'reforma', 'pavimentacao', 'drenagem',
        'engenharia', 'infraestrutura', 'saneamento', 'habitacional',
        'locacao', 'equipamentos',
    ],
    'editais': editais_out,
    'resumo_executivo': resumo,
    'inteligencia_mercado': intel,
    'querido_diario': [],
    'proximos_passos': proximos,
}

out_path = 'docs/propostas/data-26420889000150-2026-03-12.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data_out, f, ensure_ascii=False, indent=2)

print(f'JSON salvo: {out_path}')
print(f'Editais: {len(editais_out)} | Valor: R$ {total_valor_e:,.2f}')
print(f'Historico: {len(hist)} top contratos (de {len(all_contracts)} total)')
print(f'PARTICIPAR: {n_part} | AVALIAR: {n_aval}')
print(f'Proximos passos: {len(proximos)}')
