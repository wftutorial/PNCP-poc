#!/usr/bin/env python3
"""Enrich report data for Compacta Sul Pavimentacao LTDA."""
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INPUT = 'D:/pncp-poc/docs/reports/data-03667661000163-2026-03-18.json'

with open(INPUT, 'r', encoding='utf-8') as f:
    data = json.load(f)

editais = data['editais']
empresa = data['empresa']
capital = empresa.get('capital_social', 0) or 0
anos_atividade = 26  # 2000-2026

# PDF analysis findings (from manual review)
pdf_analysis = {
    23: {
        'analise_documental': (
            'Edital exige garantia de proposta equivalente a 1% do valor estimado (R$ 12.705). '
            'Habilitacao requer registro CREA/CAU, balanco patrimonial dos 2 ultimos exercicios com '
            'indices de Liquidez Corrente e Liquidez Geral minimos de 1,0. Qualificacao tecnica exige '
            'atestado com CAT para: base graduada (873,93 m2), imprimacao (4.247,13 m2), pintura ligacao '
            '(4.247,13 m2) e execucao de pavimento com concreto asfaltico (200,10 m2). Permite somatorio de atestados. '
            'Propostas inexequiveis abaixo de 75% do orcado. Garantia adicional se proposta inferior a 85% do orcado. '
            'Plataforma: BLL (bll.org.br). Prazo de validade da proposta: 60 dias.'
        ),
        'red_flags': [],
        'condicionantes': [
            'Obter garantia de proposta de 1% (R$ 12.705) antes da sessao',
            'Comprovar capacidade tecnica com atestados de pavimentacao asfaltica nos quantitativos minimos',
            'Verificar indices de liquidez corrente e geral no balanco patrimonial'
        ]
    },
    8: {
        'analise_documental': (
            'Edital retificado com nova data de abertura: 26/03/2026 as 8h30. '
            'Objeto: reconstrucao de ponte em concreto armado sobre Arroio da Seca (32m comprimento x 7,50m largura), '
            'ligacao entre Linha Ernesto Alves e Rodovia Municipal (Ponte Villa Wood). Recursos da Defesa Civil Nacional '
            '(Protocolo REC-RS-4310363-20250805-01). Visita tecnica obrigatoria com agendamento no Setor de Engenharia '
            '(fone 51-3754.1100 ou 51-9183-1277) ate 25/03/2026. O atestado de visita e requisito de qualificacao tecnica. '
            'Plataforma: Portal de Compras Publicas.'
        ),
        'red_flags': ['Visita tecnica obrigatoria com prazo ate 25/03/2026 - agendamento imediato necessario'],
        'condicionantes': [
            'Agendar visita tecnica URGENTE ate 25/03/2026',
            'Comprovar experiencia em construcao de pontes em concreto armado',
            'Capital social pode ser insuficiente para exigencia de 10% do valor'
        ]
    },
    3: {
        'analise_documental': (
            'Edital de Concorrencia Eletronica para construcao de pontes no municipio de Marata/RS. '
            'Exige qualificacao tecnico-profissional e tecnico-operacional com declaracoes e atestados. '
            'Nao exige garantia adicional neste processo. '
            'Regime de empreitada por preco global com fornecimento de materiais. '
            'Valor estimado: R$ 1.199.857,98. Encerramento em 22/03/2026.'
        ),
        'red_flags': ['Capital social de R$ 200.000 e inferior ao minimo tipico de 10% (R$ 119.986)'],
        'condicionantes': [
            'Comprovar experiencia em construcao de pontes',
            'Avaliar necessidade de consorcio pelo valor elevado vs. capital social'
        ]
    },
    7: {
        'analise_documental': (
            'Concorrencia Eletronica para regularizacao e capeamento asfaltico em CBUQ da Rua Pinheiros '
            'em Portao/RS, com sinalizacao completa. Estudo de Viabilidade Tecnica inclui utilizacao de '
            'materiais e tecnologias correntes conforme SINAPI/SICRO. Visa otimizar estrutura existente '
            '(paralelepipedo antigo) com capeamento. Valor estimado: R$ 992.841,38.'
        ),
        'red_flags': ['Capital social limitrofe: R$ 200.000 para edital de R$ 992.841'],
        'condicionantes': [
            'Comprovar experiencia em capeamento asfaltico CBUQ',
            'Avaliar carta de fianca bancaria para complementar capital social'
        ]
    },
    20: {
        'analise_documental': (
            'Concorrencia Eletronica para complementacao e execucao de projeto executivo em Cerro Grande do Sul/RS. '
            'Exige atestado de capacitacao tecnico-operacional e profissional com obra de complexidade similar '
            'ao objeto (ponte em concreto pre-moldado protendido). Visita tecnica facultativa. '
            'Prova de capacitacao pode ser em atestados separados ou documento unico. '
            'Valor estimado: R$ 916.959,36.'
        ),
        'red_flags': ['Exigencia especifica de ponte em concreto pre-moldado protendido - especialidade restrita'],
        'condicionantes': [
            'Comprovar experiencia especifica em concreto pre-moldado protendido',
            'Capital social limitrofe - avaliar complementacao'
        ]
    },
    17: {
        'analise_documental': (
            'Concorrencia Eletronica para recapeamento asfaltico em Nova Palma/RS. '
            'Exige manutencao das condicoes de habilitacao durante toda execucao contratual, '
            'incluindo comprovacao mensal de FGTS e INSS. Recebimento provisorio pelo fiscal '
            'e definitivo por comissao designada. Valor estimado: R$ 897.533,44.'
        ),
        'red_flags': ['Capital social limitrofe para valor do edital'],
        'condicionantes': [
            'Comprovar experiencia em recapeamento asfaltico',
            'Manter regularidade fiscal mensal durante execucao'
        ]
    },
    14: {
        'analise_documental': (
            'Concorrencia Eletronica para pavimentacao de trecho de estrada no Travessao Curuzzu em Nova Padua/RS. '
            'Qualificacao tecnica detalhada: registro CREA/CAU (com visto do CREA-RS se de outro estado). '
            'Exige atestado com CAT de obras concluidas, discriminando servicos e quantitativos dos itens '
            '3.1.3, 3.2.1 e 3.3.1 da planilha orcamentaria, com minimo de 50% do quantitativo. '
            'Atestados devem permitir identificacao do atestante com nome, cargo e meios de contato. '
            'Valor estimado: R$ 719.888,86.'
        ),
        'red_flags': [],
        'condicionantes': [
            'Comprovar minimo de 50% dos quantitativos dos itens de maior relevancia',
            'Registro CREA/CAU com visto do CREA-RS se de outra jurisdicao'
        ]
    },
    15: {
        'analise_documental': (
            'Concorrencia Eletronica para elaboracao de Projeto Tecnico Basico de ponte estaiada em Imbe/RS. '
            'Exigencias tecnicas MUITO RESTRITIVAS: atestado de projeto de ponte com mais de 60 metros '
            'de comprimento e mais de 1.000 m2 de area de leito carrocavel, executado em no maximo 45 dias. '
            'Tambem exige atestado de elaboracao de projeto de estruturas pre-fabricadas e atestado de '
            'assessoria em Termo de Referencia e Memorial Descritivo para processo licitatorio. '
            'Natureza do objeto e PROJETO (nao execucao de obra).'
        ),
        'red_flags': [
            'Objeto e elaboracao de PROJETO, nao execucao de obra - fora do perfil operacional da empresa',
            'Exigencia de atestado de ponte com mais de 60m e 1.000 m2 de leito em 45 dias - altamente restritiva',
            'Distancia elevada da sede: 517,5 km'
        ],
        'condicionantes': [
            'Necessario escritorio de engenharia de projetos, nao construtora',
            'Atestados tecnicos muito especificos e restritivos'
        ]
    },
    6: {
        'analise_documental': (
            'Concorrencia Eletronica para recapeamento asfaltico em Nova Palma/RS (segundo edital do municipio). '
            'Mesmas condicoes gerais do edital #17 do mesmo orgao. Exige manutencao de habilitacao '
            'durante execucao com comprovantes mensais de encargos. Valor estimado: R$ 590.696,32. '
            'Proximidade geografica favoravel: 153,5 km da sede em Ijui.'
        ),
        'red_flags': [],
        'condicionantes': [
            'Comprovar experiencia em recapeamento asfaltico',
            'Considerar participacao conjunta com edital #17 do mesmo orgao para otimizar mobilizacao'
        ]
    },
    12: {
        'analise_documental': (
            'Concorrencia para pavimentacao com pedras irregulares de basalto em Palmeira das Missoes/RS. '
            'Qualificacao tecnica exige profissional com atestado, certidoes do conselho profissional, '
            'indicacao de pessoal e aparelhamento. Atestados restritos as parcelas com valor acima de 4% '
            'do total estimado, com quantitativos minimos de ate 50%. Distancia: 103,8 km da sede - favoravel.'
        ),
        'red_flags': [],
        'condicionantes': [
            'Comprovar experiencia em pavimentacao com pedras irregulares de basalto',
            'Atestados de parcelas com valor acima de R$ 20.153 (4% do total)'
        ]
    },
    22: {
        'analise_documental': (
            'Concorrencia PRESENCIAL para reperfilamento asfaltico com CBUQ em Constantina/RS. '
            'Exige registro CREA/CAU atualizado com dados identicos ao contrato social. '
            'Atestado de visita ao local ou declaracao de nao interesse na visita. '
            'Atestado de capacidade tecnica com CAT para servicos compativeis, com metragens similares. '
            'ATENCAO: modalidade presencial requer deslocamento fisico a sessao.'
        ),
        'red_flags': ['Concorrencia PRESENCIAL - exige deslocamento de 179,2 km para sessao publica'],
        'condicionantes': [
            'Preparar procuracao para representante na sessao presencial',
            'Visita tecnica ou declaracao de nao interesse',
            'CREA/CAU com dados identicos ao contrato social vigente'
        ]
    },
    21: {
        'analise_documental': (
            'Concorrencia PRESENCIAL para pavimentacao em regime de empreitada por preco global em Constantina/RS. '
            'Mesmas exigencias do edital #22: CREA/CAU atualizado, visita tecnica ou declaracao, '
            'atestado de capacidade tecnica com CAT para obras semelhantes em metragens compativeis. '
            'Modalidade presencial. Distancia: 179,2 km da sede.'
        ),
        'red_flags': ['Concorrencia PRESENCIAL - exige presenca fisica'],
        'condicionantes': [
            'Mesmo representante pode participar de ambas sessoes (#21 e #22) no mesmo orgao',
            'Comprovar experiencia em pavimentacao com metragens compativeis'
        ]
    },
    27: {
        'analise_documental': (
            'Credenciamento para prestacao de servicos de transporte com caminhao cacamba basculante '
            'tipo toco em Ibiraiaras/RS. Nao e obra de pavimentacao - e servico de transporte. '
            'Exige caminhao com horimetro, operador habilitado e equipamentos de protecao. '
            'Empresa arca com manutencao, lubrificantes, operador e deslocamento. '
            'Prazo longo: 345 dias restantes. Valor: R$ 720.000 (provavelmente total do credenciamento).'
        ),
        'red_flags': ['Objeto e TRANSPORTE com cacamba, nao pavimentacao - compatibilidade parcial'],
        'condicionantes': [
            'Verificar se empresa possui caminhao cacamba toco no ativo',
            'Avaliar se margem do credenciamento compensa custos operacionais'
        ]
    }
}


def recommend(i, edital):
    """Determine recommendation for each edital."""
    valor = edital.get('valor_estimado', 0) or 0
    dias = edital.get('dias_restantes', 0)
    risk = edital.get('risk_score', {})
    vetoed = risk.get('vetoed', False)
    risk_total = risk.get('total', 0)
    hab_status = edital.get('habilitacao_analysis', {}).get('status', '')
    dist_km = edital.get('distancia', {}).get('km', 0)
    municipio = edital.get('municipio', '')
    objeto = edital.get('objeto', '')

    if vetoed:
        rec = 'NÃO RECOMENDADO'
        if i == 24:
            just = ('Capital social insuficiente (R$ 200.000 representa apenas 5% do valor de R$ 4.201.189). '
                    'Objeto e elaboracao de estudos e projetos rodoviarios, fora do perfil operacional de pavimentacao. '
                    'Classificacao de habilitacao: INAPTA.')
        elif i == 25:
            just = ('Capital social insuficiente (R$ 200.000 representa 7% do valor de R$ 2.869.775). '
                    'Contratacao integrada de projetos e obras de recuperacao estrutural em Rio Grande - '
                    'distancia de 523,6 km da sede e complexidade elevada de contratacao integrada.')
        elif i == 26:
            just = ('Capital social insuficiente (R$ 200.000 representa apenas 3% do valor de R$ 5.917.054). '
                    'Objeto e contratacao integrada de estudos e projetos rodoviarios de grande porte em Porto Alegre. '
                    'Classificacao de habilitacao: INAPTA. Valor supera 30 vezes o capital social.')
        else:
            just = f'Edital vetado pelo modelo de risco. Motivos: {risk.get("veto_reasons", [])}'
        return rec, just

    if dias <= 0:
        rec = 'NÃO RECOMENDADO'
        if i == 0:
            just = ('Prazo encerrado (0 dias restantes, encerramento em 19/03/2026). '
                    'Edital de pavimentacao asfaltica CBUQ em Sao Francisco de Paula com valor de R$ 715.893 '
                    'era compativel com o perfil da empresa, porem nao ha mais tempo habil para participacao.')
        elif i == 1:
            just = ('Prazo encerrado (0 dias restantes). Pavimentacao asfaltica da Estrada Geral Linha Sampaio '
                    'em Mato Leitao com valor de R$ 1.347.853 - edital de alto potencial mas sem tempo para preparacao.')
        else:
            just = 'Prazo encerrado (0 dias restantes). Sem tempo habil para participacao.'
        return rec, just

    if i == 15:
        return 'NÃO RECOMENDADO', (
            'Objeto e elaboracao de Projeto Tecnico Basico de ponte estaiada - atividade de escritorio de projetos, '
            'nao de construtora de pavimentacao. Exigencias tecnicas altamente restritivas: projeto de ponte com '
            'mais de 60 metros e mais de 1.000 m2 de leito carrocavel em 45 dias. Distancia elevada: 517,5 km. '
            'Incompativel com o perfil operacional da Compacta Sul.')

    if i == 27:
        return 'AVALIAR COM CAUTELA', (
            'Credenciamento para transporte com caminhao cacamba basculante em Ibiraiaras (257,6 km). '
            'Objeto e servico de transporte, nao pavimentacao - compatibilidade parcial pelo CNAE 4211-1/01. '
            'Prazo amplo (345 dias) e habilitacao APTA sao favoraveis, mas a empresa precisa avaliar se possui '
            'frota de cacambas e se a margem operacional justifica o deslocamento.')

    if i == 9:
        return 'AVALIAR COM CAUTELA', (
            'Edital duplicado referente a mesma ponte Villawood em Imigrante (CCE 008/2026). '
            'Mesmo objeto e valor do edital anterior (#8). Analisar qual publicacao e a vigente. '
            'Valor de R$ 1.498.303 supera 7 vezes o capital social - necessario avaliar consorcio ou fianca.')

    if i == 8:
        return 'AVALIAR COM CAUTELA', (
            'Reconstrucao de ponte em concreto armado (32m x 7,50m) sobre Arroio da Seca em Imigrante. '
            'Recursos de Defesa Civil Nacional. Nova data: 26/03/2026. Visita tecnica OBRIGATORIA '
            'ate 25/03/2026 - agendamento imediato necessario. Capital social limitrofe: R$ 200.000 '
            'para edital de R$ 1.498.303 (7x o capital). Necessario avaliar consorcio ou fianca bancaria. '
            'Distancia: 322,9 km.')

    if i == 10:
        return 'AVALIAR COM CAUTELA', (
            'Calcamento e pavimento intertravado em calcadas de Ivora (R$ 102.198). '
            'Valor baixo limita retorno. Risk score elevado (78) por ser obra de calcamento, '
            'nao pavimentacao rodoviaria tipica. Distancia moderada (161,2 km). '
            'Habilitacao parcialmente apta - verificar atestados de pavimento intertravado.')

    if i == 11:
        return 'AVALIAR COM CAUTELA', (
            'Recuperacao e manutencao de estrada rural em Derrubadas (R$ 47.889). '
            'Valor muito baixo para mobilizacao de equipe a 166,6 km. ROI esperado limitado. '
            'Habilitacao APTA e ponto favoravel. Adequado apenas se a empresa ja tiver equipe na regiao.')

    if i == 20:
        return 'AVALIAR COM CAUTELA', (
            'Complementacao e execucao de projeto em Cerro Grande do Sul (R$ 916.959). '
            'Exige experiencia especifica em ponte de concreto pre-moldado protendido - '
            'especialidade restrita que pode nao constar no acervo da empresa. '
            'Capital social limitrofe (5x o capital). Prazo confortavel: 34 dias. '
            'Distancia: 420,3 km. Habilitacao APTA no pre-calculo, mas CAT especifica e condicionante.')

    if i in [21, 22]:
        if i == 21:
            return 'AVALIAR COM CAUTELA', (
                'Pavimentacao em Constantina por empreitada global (R$ 421.659). '
                'Modalidade PRESENCIAL requer deslocamento de 179,2 km para sessao publica. '
                'Risk score elevado (86). Prazo confortavel: 34 dias. '
                'Possibilidade de participar em ambos editais de Constantina (#21 e #22) na mesma viagem. '
                'Necessario atestado de obra com metragens compativeis.')
        return 'AVALIAR COM CAUTELA', (
            'Reperfilamento asfaltico CBUQ em Constantina (R$ 473.148). '
            'Modalidade PRESENCIAL. Risk score elevado (86). Prazo: 34 dias. '
            'Objeto alinhado com perfil da empresa (CBUQ). '
            'Mesmo orgao do edital #21 - otimizacao logistica possivel. '
            'Necessario CREA/CAU com dados identicos ao contrato social.')

    if i == 23:
        return 'PARTICIPAR', (
            'Pavimentacao asfaltica em concreto betuminoso usinado a quente em Nova Roma do Sul (R$ 1.270.541). '
            'Objeto diretamente alinhado com CNAE principal da empresa (4211-1/01). '
            'Prazo confortavel: 41 dias. Plataforma eletronica BLL. Garantia de proposta: 1% (R$ 12.705). '
            'Exige atestados com CAT de base graduada, imprimacao, pintura ligacao e concreto asfaltico. '
            'Permite somatorio de atestados. Capital social limitrofe (6x o capital) - avaliar fianca bancaria. '
            'Apesar do capital restritivo, e a oportunidade de maior valor com prazo viavel.')

    if i == 6:
        return 'PARTICIPAR', (
            'Recapeamento asfaltico em Nova Palma (R$ 590.696). Proximidade favoravel: 153,5 km da sede. '
            'Objeto alinhado com perfil operacional. Prazo: 7 dias - preparacao urgente necessaria. '
            'Possibilidade de participar em conjunto com edital #17 do mesmo orgao, otimizando mobilizacao. '
            'Capital social compativel para este valor.')

    if i == 17:
        return 'PARTICIPAR', (
            'Recapeamento asfaltico em Nova Palma (R$ 897.533). Distancia favoravel: 153,5 km. '
            'Mesmo municipio do edital #6 - ganho logistico na participacao conjunta. '
            'Prazo: 22 dias. Capital limitrofe (4x o capital) - avaliar complementacao. '
            'Objeto diretamente alinhado com CNAE 4211-1/01.')

    if i == 14:
        return 'PARTICIPAR', (
            'Pavimentacao de estrada no Travessao Curuzzu em Nova Padua (R$ 719.889). '
            'Objeto alinhado com perfil da empresa. Prazo confortavel: 19 dias. '
            'Exige atestado com minimo de 50% dos quantitativos dos itens de maior relevancia. '
            'Capital limitrofe (4x o capital). Distancia: 346,3 km. '
            'Possibilidade de combinar com edital #13 do mesmo municipio (Travessao Bonito).')

    if i == 13:
        return 'PARTICIPAR', (
            'Pavimentacao de estrada no Travessao Bonito em Nova Padua (R$ 365.561). '
            'Valor compativel com capital social. Prazo: 14 dias. '
            'Mesmo municipio do edital #14 - otimizacao logistica. '
            'Objeto de pavimentacao rural alinhado com perfil operacional. Distancia: 346,3 km.')

    if i == 12:
        return 'PARTICIPAR', (
            'Pavimentacao com pedras irregulares de basalto em Palmeira das Missoes (R$ 503.822). '
            'Proximidade geografica favoravel: 103,8 km da sede em Ijui - menor distancia entre os editais. '
            'Prazo: 12 dias. Valor compativel com capital social. '
            'Atestados restritos a parcelas acima de 4% do total. Habilitacao parcialmente apta.')

    if i == 2:
        return 'PARTICIPAR', (
            'Pavimentacao asfaltica em Parai (valor nao informado no sistema). '
            'Prazo: 4 dias - urgencia maxima. Distancia: 255,5 km. '
            'Necessario verificar valor real no edital. Objeto alinhado com perfil operacional.')

    if i == 4:
        return 'PARTICIPAR', (
            'Servicos de pavimentacao em Estancia Velha (R$ 245.471). '
            'Valor compativel com capital social. Habilitacao APTA. Prazo: 6 dias. '
            'Distancia: 394,1 km. Unico edital com habilitacao plenamente apta nesta faixa.')

    if i == 3:
        return 'AVALIAR COM CAUTELA', (
            'Construcao de pontes em Marata (R$ 1.199.858). Capital insuficiente: R$ 200.000 '
            'para edital que exige experiencia em pontes. Prazo: 4 dias - urgencia maxima. '
            'Distancia: 350,1 km. Necessario consorcio ou fianca bancaria para viabilizar.')

    if i == 5:
        return 'AVALIAR COM CAUTELA', (
            'Empreitada global com fornecimento de material em Taquari (R$ 404.641). '
            'Prazo: 6 dias. Distancia: 348,1 km. Capital compativel. '
            'Habilitacao parcialmente apta - verificar requisitos especificos do edital.')

    if i == 7:
        return 'AVALIAR COM CAUTELA', (
            'Capeamento asfaltico CBUQ da Rua Pinheiros em Portao (R$ 992.841). '
            'Objeto alinhado com perfil. Prazo curto: 7 dias - preparacao urgente. '
            'Capital limitrofe (5x o capital). Distancia: 388 km. '
            'Viabilidade tecnica comprovada conforme SINAPI/SICRO. '
            'Necessario atestado de capeamento sobre paralelepipedo.')

    if i == 16:
        return 'AVALIAR COM CAUTELA', (
            'Obra de execucao em Forquetinha (R$ 72.300). Valor baixo limita retorno. '
            'Risk score elevado (76). Prazo: 21 dias. Distancia: 294,8 km. '
            'Custo de participacao pode nao justificar o retorno esperado.')

    if i == 18:
        return 'AVALIAR COM CAUTELA', (
            'Engenharia e arquitetura em Farroupilha (R$ 157.643). Valor medio. '
            'Prazo: 25 dias. Distancia: 377,2 km. Risk score: 76. '
            'Possibilidade de combinar com edital #19 do mesmo municipio.')

    if i == 19:
        return 'AVALIAR COM CAUTELA', (
            'Engenharia e arquitetura em Farroupilha (R$ 236.444). '
            'Prazo: 27 dias. Distancia: 377,2 km. Mesmo municipio do #18. '
            'Otimizacao logistica se participar de ambos.')

    return 'AVALIAR COM CAUTELA', (
        f'Edital requer analise adicional. Risk score: {risk_total}. Prazo: {dias} dias.')


# Process all editais
for i, edital in enumerate(editais):
    valor = edital.get('valor_estimado', 0) or 0
    dias = edital.get('dias_restantes', 0)
    risk = edital.get('risk_score', {})
    risk_total = risk.get('total', 0)
    hab_status = edital.get('habilitacao_analysis', {}).get('status', '')
    dist_km = edital.get('distancia', {}).get('km', 0)
    municipio = edital.get('municipio', '')
    modalidade = edital.get('modalidade', '')
    acervo = edital.get('acervo_status', 'NAO_VERIFICADO')
    cronograma = edital.get('cronograma', [])
    roi = edital.get('roi_potential', {})
    wp = edital.get('win_probability', {})

    rec, just = recommend(i, edital)
    edital['recomendacao'] = rec
    edital['justificativa'] = just

    # PDF-based or generated analysis
    if i in pdf_analysis:
        edital['analise_documental'] = pdf_analysis[i]['analise_documental']
        edital['red_flags_documentais'] = pdf_analysis[i].get('red_flags', [])
        edital['condicionantes'] = pdf_analysis[i].get('condicionantes', [])
    else:
        red_flags = []
        condicionantes = []
        for alerta in edital.get('alertas_criticos', []):
            if alerta.get('severidade') == 'CRITICO':
                red_flags.append(alerta.get('descricao', ''))
            if alerta.get('acao_requerida'):
                condicionantes.append(alerta['acao_requerida'])
        for gap in edital.get('habilitacao_analysis', {}).get('gaps', []):
            if gap not in condicionantes:
                condicionantes.append(gap)

        edital['analise_documental'] = (
            f'Analise baseada nos dados coletados automaticamente. '
            f'Modalidade: {modalidade}. Valor estimado: R$ {valor:,.2f}. '
            f'Distancia da sede: {dist_km} km. Prazo restante: {dias} dias. '
            f'Habilitacao: {hab_status}. Acervo tecnico: nao verificado.')
        edital['red_flags_documentais'] = red_flags[:5]
        edital['condicionantes'] = condicionantes[:5]

    # Analise detalhada
    roi_text = ''
    if roi.get('roi_if_win_max'):
        roi_text = (
            f'Retorno potencial se vencer: R$ {roi["roi_if_win_min"]:,.0f} a R$ {roi["roi_if_win_max"]:,.0f} '
            f'(margem de {roi.get("margin_range", "8%-15%")}). ')

    prob_text = ''
    if wp.get('probability'):
        prob_text = (
            f'Probabilidade estimada de vitoria: {wp["probability"]*100:.1f}% '
            f'({wp.get("confidence", "baixa")} confianca). ')
        if wp.get('multipliers_applied'):
            prob_text += f'Fatores ajustados: {", ".join(wp["multipliers_applied"])}. '

    crono_text = ''
    if cronograma:
        marcos = [f'{c["marco"]} ({c["data"]}, {c["status"]})' for c in cronograma[:3]]
        crono_text = 'Cronograma: ' + '; '.join(marcos) + '. '

    edital['analise_detalhada'] = (
        f'{just} '
        f'{roi_text}'
        f'{prob_text}'
        f'{crono_text}'
        f'Acervo tecnico: {acervo.replace("_", " ").lower()}. '
        f'Score de risco: {risk_total}/100.')

    # Analise resumo
    if rec == 'PARTICIPAR':
        edital['analise_resumo'] = (
            f'PARTICIPAR - {municipio}/{edital.get("uf","RS")}, R$ {valor:,.2f}. '
            f'{edital.get("objeto","")[:100]}. Prazo: {dias} dias.')
    elif rec == 'NÃO RECOMENDADO':
        edital['analise_resumo'] = (
            f'NÃO RECOMENDADO - {municipio}/{edital.get("uf","RS")}, R$ {valor:,.2f}. '
            f'{just[:100]}.')
    else:
        edital['analise_resumo'] = (
            f'AVALIAR COM CAUTELA - {municipio}/{edital.get("uf","RS")}, R$ {valor:,.2f}. '
            f'{just[:100]}.')


# Counts
participar = sum(1 for e in editais if e.get('recomendacao') == 'PARTICIPAR')
cautela = sum(1 for e in editais if e.get('recomendacao') == 'AVALIAR COM CAUTELA')
nao_rec = sum(1 for e in editais if e.get('recomendacao') == 'NÃO RECOMENDADO')

participar_editais = [i for i, e in enumerate(editais) if e.get('recomendacao') == 'PARTICIPAR']
cautela_editais = [i for i, e in enumerate(editais) if e.get('recomendacao') == 'AVALIAR COM CAUTELA']
nao_rec_editais = [i for i, e in enumerate(editais) if e.get('recomendacao') == 'NÃO RECOMENDADO']

valor_participar = sum(editais[i].get('valor_estimado', 0) or 0 for i in participar_editais)
valor_cautela = sum(editais[i].get('valor_estimado', 0) or 0 for i in cautela_editais)

print(f'PARTICIPAR: {participar} (indices: {participar_editais})')
print(f'AVALIAR COM CAUTELA: {cautela} (indices: {cautela_editais})')
print(f'NÃO RECOMENDADO: {nao_rec} (indices: {nao_rec_editais})')
print(f'Total: {participar + cautela + nao_rec}')
print(f'Valor PARTICIPAR: R$ {valor_participar:,.2f}')
print(f'Valor CAUTELA: R$ {valor_cautela:,.2f}')

# Resumo executivo
data['resumo_executivo'] = {
    'empresa': 'COMPACTA SUL PAVIMENTAÇÃO LTDA',
    'cnpj': '03.667.661/0001-63',
    'setor': 'Engenharia Rodoviária e Infraestrutura Viária',
    'data_analise': '2026-03-18',
    'total_editais_analisados': len(editais),
    'recomendacao_participar': participar,
    'recomendacao_avaliar': cautela,
    'recomendacao_nao_recomendado': nao_rec,
    'valor_total_participar': round(valor_participar, 2),
    'valor_total_cautela': round(valor_cautela, 2),
    'perfil_maturidade': 'CRESCIMENTO',
    'capital_social': capital,
    'anos_atividade': anos_atividade,
    'sicaf_status': 'Cadastrado, sem restricoes',
    'sancoes': 'Nenhuma sancao identificada (CEIS, CNEP, CEPIM, CEAF)',
    'tese_estrategica': 'MANTER',
    'tendencia_mercado': 'EXPANSÃO (crescimento de 100% anualizado no setor)',
    'sintese': (
        f'A Compacta Sul Pavimentacao, com sede em Ijui/RS e 26 anos de atividade, esta posicionada '
        f'no segmento de construcao de rodovias e infraestrutura viaria (CNAE 4211-1/01). '
        f'Foram identificados {len(editais)} editais abertos no Rio Grande do Sul, dos quais '
        f'{participar} sao recomendados para participacao (valor total de R$ {valor_participar:,.2f}), '
        f'{cautela} devem ser avaliados com cautela e {nao_rec} nao sao recomendados. '
        f'O principal limitador da empresa e o capital social de R$ 200.000, que restringe a '
        f'participacao em editais acima de R$ 2.000.000, e a ausencia de acervo tecnico comprovado '
        f'nos sistemas consultados. RECOMENDAÇÃO PRIORITÁRIA: a empresa deve regularizar seu acervo '
        f'tecnico junto ao CREA, registrando CATs de obras ja executadas, para ampliar significativamente '
        f'suas chances de habilitacao. O mercado esta em expansao (HHI 0,0033, muito competitivo) '
        f'com desconto medio de 42,9% nas licitacoes, indicando margens saudaveis.'
    ),
    'alertas_gate': [
        {
            'alerta': 'HABILITACAO_HIGH_PARTIAL',
            'tratamento': (
                '79% dos editais (22/28) apresentam habilitacao parcial. Isso reflete a ausencia de '
                'acervo tecnico comprovado no CREA e a necessidade de verificacao de certidoes fiscais. '
                'A empresa possui cadastro SICAF ativo sem restricoes, o que e favoravel. A recomendacao '
                'e focar nos editais classificados como PARTICIPAR e providenciar as CATs pendentes.')
        },
        {
            'alerta': 'ACERVO_MOSTLY_UNVERIFIED',
            'tratamento': (
                'Nenhum dos 28 editais possui acervo tecnico verificado. Isso representa o MAIOR RISCO '
                'de inabilitacao da empresa. A Compacta Sul opera ha 26 anos e certamente possui obras '
                'executadas que podem ser registradas como CAT. Acao imediata: levantar contratos antigos, '
                'solicitar atestados dos contratantes e registrar no CREA/RS.')
        },
        {
            'alerta': 'LOW_PROBABILITY_SPREAD',
            'tratamento': (
                'O spread de probabilidade de 0,2pp indica que o modelo calibra probabilidades muito '
                'proximas entre os editais. Isso ocorre porque a empresa nao possui historico de contratos '
                'governamentais nos bancos de dados consultados, e todos os editais compartilham o mesmo '
                'perfil de risco (acervo nao verificado, mesmo setor). As probabilidades servem como '
                'indicativo relativo e nao como predicao absoluta.')
        }
    ]
}

# Inteligencia de mercado
data['inteligencia_mercado'] = {
    'panorama_setorial': (
        'O setor de engenharia rodoviaria e infraestrutura viaria no Rio Grande do Sul apresenta '
        'expansao significativa em 2026, com crescimento anualizado de 100% no volume de licitacoes. '
        'O indice HHI de 0,0033 indica mercado altamente fragmentado e competitivo, sem concentracao '
        'de fornecedores dominantes. O desconto medio de 42,9% nas contratacoes indica margens saudaveis '
        'e espaco para precificacao competitiva.'),
    'tendencias': [
        'Forte demanda por recapeamento asfaltico e CBUQ em municipios do interior gaucho',
        'Reconstrucao de pontes financiada pela Defesa Civil Nacional apos eventos climaticos',
        'Editais de pavimentacao rural em estradas vicinais - oportunidade para empresas de medio porte',
        'Crescente exigencia de CATs especificas com quantitativos minimos detalhados',
        'Plataformas eletronicas (BLL, Portal de Compras Publicas) dominam - presencial e excecao'
    ],
    'vantagens_competitivas': [
        'Sede em Ijui/RS - posicao central com acesso a diversas regioes do estado',
        'CNAE principal 4211-1/01 (Construcao de Rodovias e Ferrovias) - alinhamento direto',
        '26 anos de atividade - maturidade operacional reconhecida',
        'SICAF cadastrado sem restricoes - pre-requisito atendido',
        'Sem sancoes em nenhuma base de dados (CEIS, CNEP, CEPIM, CEAF)',
        '20 CNAEs secundarios diversificados - flexibilidade para diferentes tipos de obra'
    ],
    'riscos_e_gaps': [
        'Capital social de R$ 200.000 limita participacao em editais acima de R$ 2.000.000',
        'Ausencia de acervo tecnico comprovado nos sistemas - MAIOR RISCO de inabilitacao',
        'Nenhum contrato governamental registrado nos bancos de dados consultados',
        'Perfil de maturidade CRESCIMENTO (score 48/100) - financeiro e historico abaixo da media'
    ],
    'nichos_oportunidade': [
        'Recapeamento asfaltico e CBUQ em municipios ate 300 km de Ijui (menor custo de mobilizacao)',
        'Pavimentacao de estradas rurais e vicinais com pedras irregulares',
        'Obras de conservacao rodoviaria municipal de medio porte (R$ 100.000 a R$ 800.000)',
        'Credenciamentos municipais para servicos de terraplenagem e transporte'
    ],
    'tese_estrategica': (
        'MANTER presenca ativa no mercado de licitacoes gauchas. A empresa possui perfil operacional '
        'adequado para obras de pavimentacao de medio porte. A prioridade imediata e regularizar o acervo '
        'tecnico junto ao CREA para eliminar o principal obstaculo de habilitacao. Com o acervo regularizado, '
        'a taxa de sucesso em habilitacoes pode saltar de 14% (4/28 editais APTA) para potencialmente '
        '70%+ dos editais analisados. O aumento de capital social para R$ 500.000 expandiria o universo '
        'de editais viaveis significativamente. Confianca na tese: ALTA.')
}

# Proximos passos
acao_imediata = []
medio_prazo = []
estrategico = []

# Acao transversal: acervo tecnico
acao_imediata.append({
    'acao': 'Regularizar acervo tecnico junto ao CREA/RS - registrar CATs de obras ja executadas',
    'edital_ref': 'TODOS',
    'editais_afetados': [str(e.get('sequencial_compra', i)) for i, e in enumerate(editais)
                         if e.get('recomendacao') != 'NÃO RECOMENDADO'],
    'orgao': 'CREA/RS',
    'uf': 'RS',
    'municipio': 'Ijui',
    'valor': 0,
    'prazo_proposta': '2026-03-25',
    'dias_restantes': 7,
    'prioridade': 1,
    'prioridade_label': 'URGENTE',
    'recomendacao': 'AÇÃO TRANSVERSAL',
    'link': '',
    'documentos_necessarios': [
        'Contratos de obras anteriores',
        'Atestados de capacidade tecnica de contratantes',
        'ARTs/RRTs das obras executadas',
        'Fotografias e medicoes das obras'
    ],
    'observacao': 'Esta acao afeta TODOS os editais. Sem CATs registradas, o risco de inabilitacao e maximo.'
})

for i in participar_editais:
    e = editais[i]
    dias = e.get('dias_restantes', 0)
    valor = e.get('valor_estimado', 0) or 0

    docs_necessarios = [
        'CND Federal (Receita Federal + Divida Ativa da Uniao)',
        'CRF FGTS (Caixa Economica Federal)',
        'CND Estadual',
        'CND Municipal',
        'CNDT - Certidao Negativa de Debitos Trabalhistas',
        'Certidao Negativa de Falencia',
        'Registro CREA/RS atualizado',
        'Atestado de capacidade tecnica com CAT',
        'Balanco patrimonial dos 2 ultimos exercicios'
    ]
    if valor > capital * 3:
        docs_necessarios.append('Carta de fianca bancaria ou comprovacao de capital minimo')

    item = {
        'acao': f'Preparar proposta para {e.get("orgao", "")} ({e.get("municipio", "")}/{e.get("uf","RS")}) - {e.get("objeto", "")[:100]}',
        'edital_ref': str(e.get('sequencial_compra', i)),
        'editais_afetados': [str(e.get('sequencial_compra', i))],
        'orgao': e.get('orgao', ''),
        'uf': e.get('uf', 'RS'),
        'municipio': e.get('municipio', ''),
        'valor': valor,
        'prazo_proposta': e.get('data_encerramento', ''),
        'dias_restantes': dias,
        'prioridade': 1 if dias <= 7 else 2,
        'prioridade_label': 'URGENTE' if dias <= 7 else 'NORMAL',
        'recomendacao': 'PARTICIPAR',
        'link': e.get('link', ''),
        'documentos_necessarios': docs_necessarios,
        'observacao': e.get('justificativa', '')[:200]
    }
    if dias <= 7:
        acao_imediata.append(item)
    else:
        medio_prazo.append(item)

estrategico.append({
    'acao': 'Avaliar aumento de capital social para R$ 500.000 junto aos socios',
    'edital_ref': 'ESTRATÉGICO',
    'editais_afetados': [],
    'orgao': 'Junta Comercial do RS',
    'uf': 'RS',
    'municipio': 'Ijui',
    'valor': 300000,
    'prazo_proposta': '2026-06-30',
    'dias_restantes': 104,
    'prioridade': 3,
    'prioridade_label': 'ESTRATÉGICO',
    'recomendacao': 'AÇÃO ESTRATÉGICA',
    'link': '',
    'documentos_necessarios': ['Alteracao contratual', 'Comprovante de integralizacao'],
    'observacao': 'Amplia o universo de editais viaveis para valores acima de R$ 2.000.000'
})

data['proximos_passos'] = {
    'acao_imediata': acao_imediata,
    'medio_prazo': medio_prazo,
    'estrategico': estrategico
}

# Cross-reference: no NÃO RECOMENDADO in proximos_passos
nao_rec_seq = {str(editais[i].get('sequencial_compra', i)) for i in nao_rec_editais}
for section in ['acao_imediata', 'medio_prazo', 'estrategico']:
    for item in data['proximos_passos'][section]:
        for ref in item.get('editais_afetados', []):
            if ref in nao_rec_seq and item.get('recomendacao') not in ['AÇÃO TRANSVERSAL', 'AÇÃO ESTRATÉGICA']:
                print(f'WARNING: Descartado edital {ref} in proximos_passos')

# Verify counts
assert participar == data['resumo_executivo']['recomendacao_participar']
assert cautela == data['resumo_executivo']['recomendacao_avaliar']
assert nao_rec == data['resumo_executivo']['recomendacao_nao_recomendado']
assert participar + cautela + nao_rec == len(editais)

# Save
with open(INPUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('\nJSON enriched and saved successfully.')
print(f'File: {INPUT}')
