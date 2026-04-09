#!/usr/bin/env python3
"""Enrich report JSON with strategic analysis for each edital."""
import json
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default=None)
    args = parser.parse_args()

    with open(args.input, encoding='utf-8') as f:
        data = json.load(f)

    output = args.output or args.input
    empresa = data['empresa']
    capital = empresa['capital_social']  # 2,000,000

    irrelevant_keywords = [
        'permissão remunerada de uso',
        'permissão de uso para exploração comercial',
        'oxigênio medicinal',
        'segurança privada',
        'junta rotativa',
        'materiais de higiene',
        'videomonitoramento',
        'dedetização',
        'atividades recreativas',
        'material de limpeza',
    ]

    for i, e in enumerate(data['editais']):
        obj_lower = e.get('objeto', '').lower()
        dist = e.get('distancia', {}).get('km', None)
        valor = e.get('valor_estimado', 0)
        dias = e.get('dias_restantes', None)
        modalidade = e.get('modalidade', '')
        rs = e.get('risk_score', {})
        score = rs.get('total', 50)

        # Check if irrelevant
        is_irrelevant = False
        for kw in irrelevant_keywords:
            if kw in obj_lower:
                is_irrelevant = True
                break

        if 'concessão' in obj_lower and ('abastecimento de água' in obj_lower or 'esgotamento sanitário' in obj_lower):
            is_irrelevant = True
        if 'manutenção e limpeza de vias' in obj_lower or 'limpeza urbana' in obj_lower:
            is_irrelevant = True

        if is_irrelevant:
            e['recomendacao'] = 'DESCARTADO'
            e['justificativa'] = 'Objeto não relacionado ao perfil de engenharia e construção civil da empresa.'
            e['relevante'] = False
            continue

        e['relevante'] = True
        analise_parts = []

        # Aderência
        eng_keywords = ['pavimentação', 'construção', 'reforma', 'obra', 'engenharia', 'drenagem',
                        'edificação', 'unidades habitacionais', 'bloquetamento', 'calçamento',
                        'saneamento', 'asfalto', 'asfáltica', 'projeto']
        aderencia = sum(1 for kw in eng_keywords if kw in obj_lower)
        aderencia_nivel = 'Alta' if aderencia >= 3 else ('Média' if aderencia >= 1 else 'Baixa')
        analise_parts.append(f'Aderência ao perfil: {aderencia_nivel}')

        # Valor vs capital
        if valor > 0:
            ratio = valor / capital
            if ratio > 10:
                analise_parts.append(f'Valor (R${valor:,.2f}) muito acima do capital social (R${capital:,.2f}) — fator {ratio:.1f}x. Pode haver exigência de patrimônio líquido incompatível.')
            elif ratio > 3:
                analise_parts.append(f'Valor (R${valor:,.2f}) significativo em relação ao capital social (R${capital:,.2f}) — fator {ratio:.1f}x.')
            else:
                analise_parts.append(f'Valor (R${valor:,.2f}) compatível com capital social (R${capital:,.2f}) — fator {ratio:.1f}x.')
        else:
            analise_parts.append('Valor estimado sigiloso — análise de compatibilidade financeira prejudicada.')

        # Distância
        if dist:
            dur = e.get('distancia', {}).get('duracao_horas', 0)
            if dist > 700:
                analise_parts.append(f'Distância: {dist:.0f} km ({dur:.1f}h) — logística complexa, custos de mobilização elevados.')
            elif dist > 400:
                analise_parts.append(f'Distância: {dist:.0f} km ({dur:.1f}h) — distância moderada, requer planejamento logístico.')
            else:
                analise_parts.append(f'Distância: {dist:.0f} km ({dur:.1f}h) — distância razoável.')

        # Prazo
        if dias is not None:
            if dias <= 3:
                analise_parts.append(f'Prazo crítico: apenas {dias} dias restantes. Tempo insuficiente para preparar documentação e proposta adequada.')
            elif dias <= 7:
                analise_parts.append(f'Prazo apertado: {dias} dias restantes. Necessário iniciar preparação imediata.')
            elif dias <= 30:
                analise_parts.append(f'Prazo adequado: {dias} dias restantes para preparação.')
            else:
                analise_parts.append(f'Prazo confortável: {dias} dias restantes.')

        # Modalidade
        if 'eletrônica' in modalidade.lower():
            analise_parts.append(f'Modalidade {modalidade} — disputa online, sem necessidade de deslocamento para sessão.')
        elif 'presencial' in modalidade.lower():
            analise_parts.append(f'Modalidade {modalidade} — requer presença física na sessão.')

        e['analise_detalhada'] = '\n'.join(analise_parts)

        # Recommendation
        if dias is not None and dias <= 2:
            e['recomendacao'] = 'NÃO RECOMENDADO'
            e['justificativa'] = f'Prazo de {dias} dias insuficiente para preparar documentação técnica e proposta competitiva. Risco alto de proposta incompleta.'
        elif valor > capital * 15:
            e['recomendacao'] = 'NÃO RECOMENDADO'
            e['justificativa'] = f'Valor estimado R${valor:,.2f} é {valor/capital:.0f}x o capital social da empresa (R${capital:,.2f}). Provável exigência de patrimônio líquido/garantias incompatíveis.'
        elif dist and dist > 750 and valor < 500000:
            e['recomendacao'] = 'NÃO RECOMENDADO'
            e['justificativa'] = f'Distância de {dist:.0f} km combinada com valor baixo (R${valor:,.2f}) torna operação financeiramente inviável pelos custos de mobilização.'
        elif score >= 70 and (dist is None or dist < 600) and valor > 100000 and (dias is None or dias > 15):
            e['recomendacao'] = 'PARTICIPAR'
            e['justificativa'] = f'Score de viabilidade {score}/100, valor compatível com porte da empresa, prazo adequado para preparação. Objeto alinhado com CNAEs da empresa.'
        elif score >= 70 and (dias is None or dias > 30):
            e['recomendacao'] = 'PARTICIPAR'
            dist_note = f' Avaliar custos logísticos considerando distância de {dist:.0f} km.' if dist else ''
            e['justificativa'] = f'Score de viabilidade {score}/100, prazo confortável para preparação.{dist_note}'
        else:
            e['recomendacao'] = 'AVALIAR COM CAUTELA'
            reasons = []
            if dias is not None and dias <= 7:
                reasons.append(f'prazo apertado ({dias} dias)')
            if dist and dist > 600:
                reasons.append(f'distância significativa ({dist:.0f} km)')
            if valor > capital * 5:
                reasons.append(f'valor elevado em relação ao capital ({valor/capital:.1f}x)')
            if valor == 0:
                reasons.append('valor estimado sigiloso')
            if not reasons:
                reasons.append('análise detalhada dos requisitos de habilitação necessária')
            e['justificativa'] = f'Objeto compatível com perfil da empresa, mas atenção: {", ".join(reasons)}.'

    # Summary
    relevant = [e for e in data['editais'] if e.get('relevante', True) and e.get('recomendacao') != 'DESCARTADO']
    participar = [e for e in relevant if e.get('recomendacao') == 'PARTICIPAR']
    avaliar = [e for e in relevant if e.get('recomendacao') == 'AVALIAR COM CAUTELA']
    nao_rec = [e for e in relevant if e.get('recomendacao') == 'NÃO RECOMENDADO']
    descartados = [e for e in data['editais'] if e.get('recomendacao') == 'DESCARTADO']

    valor_total = sum(e.get('valor_estimado', 0) for e in relevant)
    valor_participar = sum(e.get('valor_estimado', 0) for e in participar)

    data['resumo_executivo'] = {
        'total_editais_encontrados': len(data['editais']),
        'editais_relevantes': len(relevant),
        'editais_descartados': len(descartados),
        'participar': len(participar),
        'avaliar_cautela': len(avaliar),
        'nao_recomendado': len(nao_rec),
        'valor_total_oportunidades': valor_total,
        'valor_recomendado': valor_participar,
        'setores_identificados': [data['setor']],
        'ufs': list(set(e.get('uf', '') for e in relevant)),
        'modalidades': list(set(e.get('modalidade', '') for e in relevant)),
    }

    data['inteligencia_mercado'] = {
        'panorama': f'Foram identificados {len(relevant)} editais de engenharia e construção civil abertos em MG nos últimos 30 dias, totalizando R${valor_total:,.2f} em oportunidades. O mercado apresenta forte concentração em obras de habitação popular (Programa MCMV-FNHIS SUB-50), pavimentação asfáltica e reformas de equipamentos públicos.',
        'tendencias': 'Destaque para o Programa MCMV-FNHIS SUB-50 com múltiplos editais de construção de unidades habitacionais (20-50 UH) em municípios do interior de MG, valores entre R$2,8M e R$6,8M, modalidade concorrência (eletrônica e presencial). Pavimentação asfáltica continua como demanda relevante. Regime de contratação integrada (projeto + execução) é frequente nos editais habitacionais.',
        'vantagens_competitivas': f'A empresa {empresa["razao_social"]} ({empresa["nome_fantasia"]}) possui CNAEs compatíveis com todos os objetos identificados (4120400-Construção de edifícios, 4211101-Obras de urbanização, 4211102-Pavimentação, etc.). Capital social de R${capital:,.2f} é adequado para obras até ~R$6M. SICAF cadastrado e sem sanções são pré-requisitos atendidos.',
        'oportunidades_nicho': 'Os editais do Programa MCMV-FNHIS SUB-50 representam oportunidade significativa: são múltiplos editais com escopo padronizado (unidades habitacionais), prazos longos (45-88 dias), e valores compatíveis com o porte da empresa. A repetitividade do objeto permite ganho de escala e padronização de propostas.',
        'recomendacao_geral': 'Priorizar editais MCMV-FNHIS com prazo longo e distância razoável. Considerar estabelecer base operacional regional para atender múltiplos editais simultaneamente. Pavimentação asfáltica é segundo foco estratégico.'
    }

    data['proximos_passos'] = [
        {'acao': 'Preparar documentação base para editais MCMV-FNHIS (CAT, atestados, proposta-modelo)', 'prioridade': 'URGENTE', 'prazo': '5 dias'},
        {'acao': 'Avaliar editais com prazo < 7 dias — decidir participação imediata ou descarte', 'prioridade': 'URGENTE', 'prazo': '1 dia'},
        {'acao': 'Solicitar certidões atualizadas (FGTS, Débitos Federais, Estadual, Municipal)', 'prioridade': 'ALTA', 'prazo': '3 dias'},
        {'acao': 'Verificar disponibilidade de responsável técnico com CAT compatível', 'prioridade': 'ALTA', 'prazo': '3 dias'},
        {'acao': 'Estudar editais MCMV de Pedra do Anta, Itamonte, Natércia e Miradouro (prazo > 60 dias)', 'prioridade': 'MÉDIA', 'prazo': '15 dias'},
        {'acao': 'Avaliar custos de mobilização para municípios prioritários (calcular BDI ajustado)', 'prioridade': 'MÉDIA', 'prazo': '7 dias'},
    ]

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'JSON enriquecido salvo em: {output}')
    print(f'Relevantes: {len(relevant)} | PARTICIPAR: {len(participar)} | AVALIAR: {len(avaliar)} | NÃO REC: {len(nao_rec)} | DESCARTADOS: {len(descartados)}')
    print(f'Valor total: R${valor_total:,.2f} | Valor PARTICIPAR: R${valor_participar:,.2f}')

if __name__ == '__main__':
    main()
