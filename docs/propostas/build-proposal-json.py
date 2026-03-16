"""Build proposal JSON from real PNCP data for GJS Construcoes."""
import json
import datetime

with open('docs/propostas/pncp-mg-construcao-09225035000101.json', 'r', encoding='utf-8') as f:
    mg_data = json.load(f)

editais_raw = mg_data['editais']
today = datetime.date(2026, 3, 12)

vale_rio_doce = [
    'Tumiritinga', 'Governador Valadares', 'Caratinga', 'Ipatinga',
    'Inhapim', 'Conselheiro Pena', 'Aimores', 'Resplendor',
    'Alpercata', 'Campanario', 'Periquito', 'Fernandes Tourinho',
    'Galileia', 'Sao Jose da Safira', 'Divino das Laranjeiras',
    'Almenara', 'Nanuque', 'Teofilo Otoni', 'Carlos Chagas',
    'Mantena', 'Espera Feliz', 'Manhuacu', 'Manhumirim',
    'Pedra do Anta', 'Pedra Dourada', 'Vicosa', 'Ninheira',
]


def classify_edital(e):
    val = float(e.get('valorTotalEstimado', 0) or 0)
    mun = e.get('municipio', '')
    enc_str = (e.get('dataEncerramentoProposta', '') or '')[:10]
    try:
        enc = datetime.date.fromisoformat(enc_str) if enc_str else None
    except Exception:
        enc = None
    is_expired = enc and enc < today
    is_nearby = any(v.lower() in mun.lower() for v in vale_rio_doce)
    is_me_compatible = val <= 5_000_000
    is_stretch = 5_000_000 < val <= 15_000_000

    if is_expired:
        return 'NAO RECOMENDADO', 'Prazo de propostas encerrado'
    elif is_nearby and is_me_compatible:
        return 'PARTICIPAR', 'Edital na regiao do Vale do Rio Doce, valor compativel com porte ME'
    elif e.get('uf') == 'MG' and is_me_compatible:
        return 'PARTICIPAR', 'Edital em MG, valor compativel com porte ME'
    elif is_nearby and is_stretch:
        return 'AVALIAR COM CAUTELA', 'Valor acima do padrao ME mas regiao proxima - avaliar consorcio'
    elif e.get('uf') == 'MG' and is_stretch:
        return 'AVALIAR COM CAUTELA', 'Valor alto para ME - considerar consorcio ou subcontratacao'
    elif e.get('uf') == 'MG':
        return 'AVALIAR COM CAUTELA', 'Valor elevado - requer consorcio'
    else:
        return 'NAO RECOMENDADO', 'Fora do estado de MG'


editais_analyzed = []
for e in editais_raw:
    rec, motivo = classify_edital(e)
    val = float(e.get('valorTotalEstimado', 0) or 0)
    mun = e.get('municipio', '')
    is_nearby = any(v.lower() in mun.lower() for v in vale_rio_doce)
    mod = e.get('modalidadeNome', '')

    analise_parts = []
    if 'Pregao' in mod or 'Preg' in mod:
        analise_parts.append('Modalidade Pregao Eletronico - favorece ME/EPP')
    elif 'Concorr' in mod:
        analise_parts.append('Modalidade Concorrencia - exige qualificacao tecnica')
    if val <= 1_000_000:
        analise_parts.append('Valor acessivel para ME')
    elif val <= 5_000_000:
        analise_parts.append('Valor moderado dentro da faixa ME')
    else:
        analise_parts.append('Valor alto - avaliar consorcio')
    if is_nearby:
        analise_parts.append('Proxima a sede - custo de mobilizacao baixo')
    else:
        analise_parts.append('Considerar custos de deslocamento')

    editais_analyzed.append({
        'objeto': e['objetoCompra'],
        'orgao': e['orgao'],
        'uf': e['uf'],
        'municipio': mun,
        'valor_estimado': val,
        'modalidade': mod,
        'data_publicacao': (e.get('dataPublicacaoPncp', '') or '')[:10],
        'data_encerramento': (e.get('dataEncerramentoProposta', '') or '')[:10],
        'data_abertura': (e.get('dataAberturaProposta', '') or '')[:10],
        'numero_controle': e.get('numeroControlePNCP', ''),
        'situacao': e.get('situacaoCompraNome', ''),
        'recomendacao': rec,
        'motivo_recomendacao': motivo,
        'analise_estrategica': ' | '.join(analise_parts),
    })

# Remove expired editais — they have no place in a commercial proposal
editais_analyzed = [
    e for e in editais_analyzed if e['recomendacao'] != 'NAO RECOMENDADO'
]

rec_order = {'PARTICIPAR': 0, 'AVALIAR COM CAUTELA': 1}
editais_analyzed.sort(
    key=lambda x: (rec_order.get(x['recomendacao'], 9), -x['valor_estimado'])
)

participar = [e for e in editais_analyzed if e['recomendacao'] == 'PARTICIPAR']
avaliar = [e for e in editais_analyzed if e['recomendacao'] == 'AVALIAR COM CAUTELA']
nao_rec = [e for e in editais_analyzed if e['recomendacao'] == 'NAO RECOMENDADO']
val_participar = sum(e['valor_estimado'] for e in participar)
val_avaliar = sum(e['valor_estimado'] for e in avaliar)
val_total = sum(e['valor_estimado'] for e in editais_analyzed)

mun_dist = {}
for e in editais_analyzed:
    m = e['municipio']
    if m not in mun_dist:
        mun_dist[m] = {'count': 0, 'valor': 0}
    mun_dist[m]['count'] += 1
    mun_dist[m]['valor'] += e['valor_estimado']

mod_dist = {}
for e in editais_analyzed:
    m = e['modalidade']
    if m not in mod_dist:
        mod_dist[m] = {'count': 0, 'valor': 0}
    mod_dist[m]['count'] += 1
    mod_dist[m]['valor'] += e['valor_estimado']

proposal = {
    'empresa': {
        'razao_social': 'GJS CONSTRUCOES E COMERCIO LTDA',
        'nome_fantasia': '',
        'cnpj': '09.225.035/0001-01',
        'cnae_principal': '4120400 - Construcao de edificios',
        'cnaes_secundarios': (
            '4211101, 4211102, 4212000, 4213800, 4221903, 4292801, 4299501, '
            '4299599, 4311801, 4311802, 4312600, 4313400, 4319300, 4321500, '
            '4322301, 4322302, 4330401, 4330404, 4330405, 4391600, 4399103, '
            '4399104, 4399105, 4511101, 4520006, 4530703, 4530705, 4541203, '
            '4541206, 4635401, 4649408, 4713002, 4721102, 4723700, 4729699, '
            '4741500, 4742300, 4743100, 4744001, 4744003, 4744099, 4751201, '
            '4751202, 4752100, 4753900, 4754701, 4754703, 4755501, 4755502, '
            '4755503, 4756300, 4757100, 4759801, 4759899, 4761001, 4761003, '
            '4763601, 4771701, 4772500, 4773300, 4781400, 4782201, 4789005, '
            '4789007, 4789008, 4789099, 4924800, 4930201, 5620102, 5620104, '
            '7020400, 7111100, 7112000, 7119701, 7711000, 7719599, 7731400, '
            '7732202, 7739003, 8122200, 8130300, 8219999, 8230002, 8599604'
        ),
        'porte': 'Microempresa (ME)',
        'capital_social': 1200000,
        'natureza_juridica': 'Sociedade Empresaria Limitada',
        'cidade_sede': 'Tumiritinga',
        'uf_sede': 'MG',
        'data_abertura': '2007-11-27',
        'email': 'GJS.SERVICOS.LTDA@HOTMAIL.COM',
        'telefone': '(33) 98479858',
        'qsa': [
            {'nome': 'JULIANO SOUZA VICENTE', 'qualificacao': 'Socio-Administrador'}
        ],
        'sancoes': {'ceis': None, 'cnep': None, 'cepim': None, 'ceaf': None},
        'historico_contratos': [],
    },
    'setor': 'Construcao Civil e Obras de Engenharia',
    'editais': editais_analyzed,
    'resumo_executivo': {
        'texto': (
            'A GJS Construcoes e Comercio LTDA, ME sediada em Tumiritinga/MG '
            'com 18 anos de mercado e capital social de R$ 1,2M, atua no setor '
            'de construcao civil (CNAE 4120400) com 86 CNAEs secundarios '
            'abrangendo pavimentacao, infraestrutura, instalacoes eletricas/'
            'hidraulicas e comercio de materiais. A varredura PNCP identificou '
            '%d editais de construcao em MG publicados entre 10/02/2026 e '
            '12/03/2026, totalizando R$ %s em valor estimado. Destes, %d '
            'editais (R$ %s) sao diretamente compativeis com o porte e '
            'localizacao da empresa, e %d editais (R$ %s) merecem avaliacao '
            'cuidadosa. Destaque para a concentracao de oportunidades na regiao '
            'do Vale do Rio Doce e Zona da Mata, proximas a sede da empresa.'
        ) % (
            len(editais_analyzed), '{:,.0f}'.format(val_total),
            len(participar), '{:,.0f}'.format(val_participar),
            len(avaliar), '{:,.0f}'.format(val_avaliar),
        ),
        'destaques': [
            '%d editais com recomendacao PARTICIPAR, somando R$ %s' % (
                len(participar), '{:,.0f}'.format(val_participar)
            ),
            '%d editais para AVALIAR COM CAUTELA, somando R$ %s' % (
                len(avaliar), '{:,.0f}'.format(val_avaliar)
            ),
            'Total de %d oportunidades mapeadas em MG, R$ %s' % (
                len(editais_analyzed), '{:,.0f}'.format(val_total)
            ),
            'Empresa com 18 anos de mercado, sem sancoes (CEIS/CNEP/CEPIM/CEAF limpos)',
            '86 CNAEs secundarios - ampla capacidade de atendimento',
        ],
    },
    'inteligencia_mercado': {
        'tendencias': (
            'Forte demanda por obras de infraestrutura urbana (pavimentacao, drenagem) em municipios de medio porte de MG. '
            'Programas habitacionais gerando editais de construcao de unidades habitacionais. '
            'Obras de reforma e ampliacao de equipamentos publicos (escolas, UBS, pracas) em alta. '
            'Concorrencia Eletronica (Lei 14.133/2021) como principal modalidade para obras. '
            'Preferencia para ME/EPP em pregoes ate R$ 80.000 e tratamento diferenciado em licitacoes maiores.'
        ),
        'distribuicao_uf': {'MG': len(editais_analyzed)},
        'distribuicao_municipio': {
            k: v['count']
            for k, v in sorted(mun_dist.items(), key=lambda x: -x[1]['count'])[:15]
        },
        'valor_total_mercado': val_total,
        'modalidades': {
            k: {'count': v['count'], 'valor': v['valor']}
            for k, v in mod_dist.items()
        },
        'fonte': 'PNCP - Portal Nacional de Contratacoes Publicas (pncp.gov.br)',
        'periodo_analise': '10/02/2026 a 12/03/2026',
    },
    'proximos_passos': [
        {
            'acao': 'Revisar editais com recomendacao PARTICIPAR e verificar requisitos de habilitacao',
            'prazo': '2026-03-14',
        },
        {
            'acao': 'Preparar documentacao de habilitacao (CRF, certidoes, atestados de capacidade tecnica)',
            'prazo': '2026-03-17',
        },
        {
            'acao': 'Elaborar propostas de preco para editais com encerramento mais proximo',
            'prazo': '2026-03-19',
        },
        {
            'acao': 'Submeter propostas nos sistemas eletronicos (Compras.gov.br, Licitanet, BLL)',
            'prazo': '2026-03-21',
        },
        {
            'acao': 'Agendar reuniao de alinhamento para acompanhamento de sessoes publicas',
            'prazo': '2026-03-24',
        },
    ],
}

with open(
    'docs/propostas/data-09225035000101-2026-03-12.json', 'w', encoding='utf-8'
) as f:
    json.dump(proposal, f, ensure_ascii=False, indent=2)

print('Proposal JSON saved!')
print(f'  PARTICIPAR: {len(participar)} editais, R$ {val_participar:,.2f}')
print(f'  AVALIAR: {len(avaliar)} editais, R$ {val_avaliar:,.2f}')
print(f'  NAO RECOMENDADO: {len(nao_rec)} editais')
print(f'  Total: {len(editais_analyzed)} editais, R$ {val_total:,.2f}')
print()
print('Top PARTICIPAR:')
for e in participar[:8]:
    print(
        f'  R$ {e["valor_estimado"]:>12,.0f} | {e["municipio"]:>20} | '
        f'{e["data_encerramento"]} | {e["objeto"][:60]}'
    )
