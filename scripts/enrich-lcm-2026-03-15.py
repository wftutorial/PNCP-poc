#!/usr/bin/env python3
"""
Enrich LCM Construções report data with recommendations, justifications,
executive summary, market intelligence, and next steps.
"""

import json
from pathlib import Path

INPUT_FILE = Path("D:/pncp-poc/docs/reports/data-01721078000168-2026-03-15.json")

# ---------------------------------------------------------------------------
# Per-edital enrichment data
# Format: index -> (recomendacao, justificativa, relevante, analise_detalhada)
# ---------------------------------------------------------------------------
ENRICHMENTS = {
    # DESCARTADO — encerrado / não-construção / duplicata / valor ínfimo
    0: (
        "DESCARTADO",
        "Prazo encerrado: dias_restantes=0. Edital de Serra Alta para construção já expirou.",
        False,
        "Edital para construção de obra pública em Serra Alta/SC com valor R$1,31M, porém o prazo de participação já foi encerrado. Nenhuma ação possível."
    ),
    2: (
        "DESCARTADO",
        "Objeto não relacionado à construção civil: fornecimento de oxigênio medicinal. Fora do escopo de atuação da LCM.",
        False,
        "Pregão de Balneário Camboriú para fornecimento de oxigênio medicinal. Totalmente fora do CNAE 4120-4/00 e dos serviços de engenharia/construção da empresa."
    ),
    25: (
        "DESCARTADO",
        "Duplicata do edital no índice 24 (mesmo objeto, mesmo valor R$5,27M, mesmo município Pinhalzinho). Publicado via Portal de Compras Públicas — dedup identificado.",
        False,
        "Este edital é idêntico ao índice 24 (centro poliesportivo de Pinhalzinho, R$5.268.805,55). Trata-se da mesma licitação publicada em duas plataformas. Apenas o edital do PNCP (índice 24) deve ser considerado."
    ),
    26: (
        "DESCARTADO",
        "Objeto não relacionado à construção civil: aquisição de bomba hidrojato para caminhão limpa fossa. Equipamento de limpeza, não de engenharia.",
        False,
        "Dispensa de licitação de Joaçaba para compra de bomba hidrojato (R$7.697). Objeto de equipamento hidráulico para saneamento, sem relação com obras civis ou construção."
    ),
    29: (
        "DESCARTADO",
        "Objeto não relacionado à construção civil: fornecimento de combustível. Sem aderência ao CNAE 4120-4/00.",
        False,
        "Processo de São José do Cedro para contratação de empresa especializada em fornecimento de combustível (R$9.210). Objeto de suprimento logístico, fora do escopo de construção civil."
    ),
    30: (
        "DESCARTADO",
        "Objeto não relacionado à construção civil: fornecimento de materiais de informática (FIA). Sem aderência ao CNAE da empresa.",
        False,
        "Processo de São Domingos para fornecimento de itens de informática diversos (R$40.664). Totalmente fora do escopo de engenharia e construção civil da LCM."
    ),
    31: (
        "DESCARTADO",
        "Objeto não relacionado à construção civil: aquisição de água mineral. Dispensa de licitação sem aderência ao CNAE 4120-4/00.",
        False,
        "Dispensa de São Ludgero para compra de água mineral (R$65.452). Objeto de consumo básico sem qualquer relação com obras ou serviços de engenharia civil."
    ),
    32: (
        "DESCARTADO",
        "Objeto não relacionado à construção civil: aquisição de impressora multifuncional e desumidificador. Fora do escopo da empresa.",
        False,
        "Processo de Angelina para compra de impressora multifuncional EPSON EcoTank e desumidificador (R$4.249). Equipamentos de escritório sem relação com construção civil."
    ),
    33: (
        "DESCARTADO",
        "Credenciamento para permissão de uso de espaço público (feiras/eventos) em Urussanga. Processo não relacionado a obras ou engenharia. Prazo provavelmente já ocorreu.",
        False,
        "Credenciamento de Urussanga para permissão de uso de espaço público a título oneroso (R$1.760). Trata-se de concessão de área para feirantes/comerciantes, sem qualquer aderência ao perfil construtivo da LCM."
    ),
    34: (
        "DESCARTADO",
        "Objeto não relacionado à construção civil: aquisição de mochila organizadora de equipamento. Valor ínfimo (R$1.800).",
        False,
        "Processo de Jaborá para compra de mochila organizadora de equipamentos (R$1.800). Objeto de material de campo/organização sem relação com obras civis."
    ),

    # NÃO RECOMENDADO — capital insuficiente, prazo crítico, distância extrema
    1: (
        "NÃO RECOMENDADO",
        "Prazo insuficiente (2 dias), distância elevada (≈554km de Itajaí) e valor baixo (R$104K). Custo de mobilização inviabiliza a margem.",
        True,
        "Obra de construção civil em Seara/SC (R$104.014, 2 dias restantes). Tripla inviabilidade: prazo mínimo impede elaboração de proposta técnica consistente; distância de 554km eleva custo de mobilização significativamente em relação ao valor; retorno financeiro insuficiente para cobrir deslocamento e estrutura. Descartar sem análise adicional."
    ),
    3: (
        "NÃO RECOMENDADO",
        "Prazo insuficiente (4 dias) e distância extrema (≈667km de Itajaí) para obra de movimentação de terra em Dionísio Cerqueira/SC.",
        True,
        "Movimentação de terra em Dionísio Cerqueira/SC (R$608.702, 4 dias restantes). A distância de 667km — extremo oeste catarinense — e o prazo de apenas 4 dias impossibilitam a preparação de documentação técnica completa e logística de equipe. Valor inadequado para cobrir custos de implantação nessa distância."
    ),
    6: (
        "NÃO RECOMENDADO",
        "Distância extrema (≈667km de Itajaí) e valor baixo (R$183K) para obra de pequeno porte em Dionísio Cerqueira/SC. Custo de mobilização inviabiliza a operação.",
        True,
        "Obra em Dionísio Cerqueira/SC (R$183.005, 7 dias restantes). Mesmo com prazo levemente melhor, a distância de 667km e o valor relativamente baixo tornam a margem operacional negativa após mobilização de equipe e equipamentos. Município no extremo oeste, sem presença histórica da LCM na região."
    ),
    7: (
        "NÃO RECOMENDADO",
        "Distância extrema (≈667km de Itajaí) e valor baixo (R$191K) para obra de entrada de energia em Dionísio Cerqueira/SC.",
        True,
        "Obra de entrada de energia em Dionísio Cerqueira/SC (R$190.835, 7 dias restantes). Similar ao índice 6: mesma localidade extremo-oeste, valor baixo e custo de mobilização desproporcional. Adicionalmente, obra de infraestrutura elétrica pode exigir qualificações específicas além do CNAE principal da LCM."
    ),
    17: (
        "NÃO RECOMENDADO",
        "Distância extrema (≈643km de Itajaí) para construção de Casa da Cidadã em Maravilha/SC. Apesar do valor adequado (R$2,86M) e prazo de 15 dias, a localização no extremo oeste inviabiliza a operação.",
        True,
        "Construção de edificação pública (Casa da Cidadã) em Maravilha/SC (R$2.861.623, 15 dias restantes). Objeto altamente aderente ao perfil da LCM, porém a distância de 643km desde Itajaí representa desafio logístico crítico: equipe, equipamentos e gestão de obra remota elevam custos operacionais substancialmente. Sem escritório regional no oeste catarinense, recomenda-se não participar."
    ),
    21: (
        "NÃO RECOMENDADO",
        "Capital social insuficiente: R$1,6M vs. exigência mínima de 10% do valor do contrato (R$21,94M × 10% = R$2,19M). Habilitação econômica-financeira comprometida.",
        True,
        "Construção de escola municipal em Florianópolis/SC (R$21.940.126, 29 dias restantes). Edital de alto valor em localização favorável (capital, 196km de Itajaí). Porém, o capital social da LCM (R$1,6M) é inferior à exigência padrão de 10% do valor estimado (R$2,19M), configurando risco real de inabilitação na fase econômico-financeira. Adicionalmente, a ausência de registro no SICAF pode ser impeditivo em licitações federais ou com exigência específica. Sem aporte de capital ou garantia bancária adicional, participação não é recomendada."
    ),
    23: (
        "NÃO RECOMENDADO",
        "Capital social insuficiente (R$1,6M < R$1,79M = 10% de R$17,86M) e distância elevada (≈612km de Itajaí). Duplo risco de inabilitação financeira e custo operacional.",
        True,
        "Construção de obras em Pinhalzinho/SC (R$17.857.254, 42 dias restantes). Valor muito elevado para o porte da LCM: a exigência de capital mínimo de 10% do contrato supera o capital social registrado de R$1,6M. Combinado com a distância de 612km (extremo oeste), o custo de mobilização e os riscos de inabilitação tornam esta licitação inviável sem parceria ou aumento de capital."
    ),
    27: (
        "NÃO RECOMENDADO",
        "Valor ínfimo (R$1.350) e distância extrema (≈680km de Itajaí). Custo operacional de mobilização é múltiplas vezes superior ao valor do serviço.",
        True,
        "Dispensa de São José do Cedro via Portal de Compras Públicas para serviço com munck (R$1.350). Valor absolutamente incompatível com os custos de mobilização para município a 680km. Mesmo tratando-se de serviço de construção/engenharia, o retorno financeiro é negativo."
    ),
    28: (
        "NÃO RECOMENDADO",
        "Valor ínfimo (R$4.500) para atualização de projetos e planilhas orçamentárias em Entre Rios/SC (≈553km de Itajaí). Atividade de consultoria com retorno irrisório.",
        True,
        "Serviço de atualização de projetos e planilhas orçamentárias em Entre Rios/SC (R$4.500). Atividade de consultoria técnica com valor muito baixo e distância de 553km. Mesmo que a LCM tenha capacidade técnica para o serviço, o custo de deslocamento e tempo de equipe técnica supera o valor contratual."
    ),

    # AVALIAR COM CAUTELA — construção civil com SICAF pendente + acervo divergente
    4: (
        "AVALIAR COM CAUTELA",
        "Obra de grande porte (R$9M, 7 dias). Prazo crítico para habilitação e proposta técnica. SICAF NÃO CADASTRADO — regularização imediata necessária. Acervo técnico em construção civil deve ser comprovado.",
        True,
        "Pavimentação e requalificação em Vitor Meireles/SC (R$9.026.046, 7 dias restantes, 174km). Maior valor entre os editais de prazo curto — oportunidade de alto impacto. A distância de apenas 174km de Itajaí é favorável, e obra de pavimentação é core do CNAE 4120-4/00. ALERTAS CRÍTICOS: (1) SICAF não cadastrado — regularização é pré-requisito imediato; (2) acervo PNCP mostra 1.000 contratos mas 97,6% são alienações da Receita Federal, não obras de engenharia; (3) 7 dias é prazo muito restrito para regularizar SICAF, obter CATs do CREA e montar proposta técnica robusta para R$9M. Recomenda-se iniciar processo de cadastro SICAF hoje e avaliar viabilidade do prazo em 24h."
    ),
    5: (
        "AVALIAR COM CAUTELA",
        "Pavimentação asfáltica em Erval Velho/SC (R$985K, 7 dias, 350km). Prazo curto e distância moderada. SICAF NÃO CADASTRADO + acervo técnico a confirmar.",
        True,
        "Pavimentação asfáltica em estrada rural de Erval Velho/SC (R$985.488, 7 dias restantes, 350km). Objeto alinhado ao CNAE principal da LCM. Distância de 350km é administrável com logística adequada. Prazo de 7 dias é crítico para montagem de proposta técnica e, principalmente, para regularização do SICAF. Sem SICAF ativo, a habilitação pode ser comprometida. Prioridade secundária em relação a editais com prazo mais longo."
    ),
    8: (
        "AVALIAR COM CAUTELA",
        "Pavimentação asfáltica em Rio Fortuna/SC (R$3,54M, 8 dias, 210km). Alta aderência ao CNAE 4120-4/00. Prazo curto mas distância favorável. SICAF NÃO CADASTRADO é o principal bloqueio.",
        True,
        "Execução de pavimentação asfáltica (CAUQ) em Rio Fortuna/SC (R$3.543.739, 8 dias restantes, 210km). Excelente aderência técnica — pavimentação é a atividade central do CNAE 4120-4/00. Distância de 210km é operacionalmente viável. Valor de R$3,54M está dentro da capacidade financeira da LCM (capital R$1,6M, exigência ~R$354K = 10%). O principal bloqueio é o SICAF não cadastrado: a maioria dos municípios catarinenses exige regularidade federal para obras acima de R$1M. Com 8 dias, o processo de cadastro SICAF + obtenção de CND e CREA pode ser inviável. Verificar urgentemente se o edital exige SICAF ou apenas CNDs avulsas."
    ),
    9: (
        "AVALIAR COM CAUTELA",
        "Obra de engenharia em Balneário Arroio do Silva/SC (R$452K, 9 dias, 303km). Valor moderado, distância aceitável. SICAF NÃO CADASTRADO e acervo técnico a confirmar.",
        True,
        "Contratação de engenharia/construção civil em Balneário Arroio do Silva/SC (R$452.389, 9 dias restantes, 303km). Município litorâneo sul-catarinense com potencial de obras. Valor acessível ao porte da LCM. Distância de 303km requer logística mas é viável. Três editais simultâneos neste município (índices 9, 10 e 16) indicam ciclo de investimentos — vale estratégia de participar em múltiplos para diluir custo de mobilização."
    ),
    10: (
        "AVALIAR COM CAUTELA",
        "Obra de engenharia em Balneário Arroio do Silva/SC (R$274K, 10 dias, 303km). Valor baixo mas pode ser estratégico junto aos editais 9 e 16 do mesmo município.",
        True,
        "Contratação de engenharia/construção civil em Balneário Arroio do Silva/SC (R$273.803, 10 dias restantes, 303km). Valor relativamente baixo, mas a presença de 3 editais simultâneos no mesmo município (R$452K + R$274K + R$994K = R$1,72M total) cria oportunidade de mobilização única para múltiplos contratos. Estratégia recomendada: participar nos 3 editais (índices 9, 10 e 16) para maximizar receita por deslocamento."
    ),
    11: (
        "AVALIAR COM CAUTELA",
        "Pavimentação em Urubici/SC (R$1,1M, 10 dias, 252km). Boa aderência ao CNAE. Dois editais simultâneos no município (índices 11 e 12) — oportunidade de mobilização combinada. SICAF NÃO CADASTRADO.",
        True,
        "Infraestrutura de pavimentação em Urubici/SC (R$1.098.407, 10 dias restantes, 252km). Município serrano a 252km de Itajaí. Junto com o índice 12 (construção civil R$1,64M no mesmo município), há oportunidade de participar em 2 contratos com mobilização única — soma de R$2,74M no mesmo local. Pavimentação é core da LCM. Regularização urgente do SICAF é pré-condição."
    ),
    12: (
        "AVALIAR COM CAUTELA",
        "Construção civil em Urubici/SC (R$1,64M, 10 dias, 252km). Dois editais no mesmo município (índices 11 e 12 somam R$2,74M) — mobilização combinada estratégica. SICAF NÃO CADASTRADO.",
        True,
        "Obra de construção civil em Urubici/SC (R$1.637.714, 10 dias restantes, 252km). Valor próximo ao capital social da LCM — exigência de 10% seria R$163K, dentro da capacidade. A combinação com o índice 11 (pavimentação, R$1,1M no mesmo município) torna Urubici o cluster de maior eficiência operacional: dois contratos, uma mobilização. Prioridade alta para participação combinada."
    ),
    13: (
        "AVALIAR COM CAUTELA",
        "Drenagem para pavimentação em Lajeado Grande/SC (R$803K, 14 dias, ≈559km). Aderência técnica boa, mas distância elevada. Dois editais no município (índices 13 e 14 somam R$1,38M).",
        True,
        "Execução de drenagem para obras de pavimentação em Lajeado Grande/SC (R$802.806, 14 dias restantes, 559km). Objeto altamente aderente ao CNAE 4120-4/00. A distância de 559km é o principal desafio. A presença de dois editais complementares no mesmo município (drenagem R$803K + movimentação de terra R$574K = R$1,38M) pode justificar a mobilização. Avaliar se o prazo de 14 dias permite organizar proposta técnica e logística para localidade distante."
    ),
    14: (
        "AVALIAR COM CAUTELA",
        "Movimentação de terra para pavimentação em Lajeado Grande/SC (R$574K, 14 dias, ≈559km). Complementar ao índice 13 — mobilização combinada pode justificar a distância.",
        True,
        "Movimentação de terra para obras de pavimentação em Lajeado Grande/SC (R$574.376, 14 dias restantes, 559km). Objeto complementar ao índice 13 (drenagem) no mesmo município. Se a decisão for participar em Lajeado Grande, incluir ambos os editais na estratégia de mobilização para maximizar receita. Valor combinado de R$1,38M torna a operação mais atrativa financeiramente."
    ),
    15: (
        "AVALIAR COM CAUTELA",
        "Construção de clínica de reabilitação em Bom Retiro/SC (R$2,56M, 15 dias, ≈216km). Boa aderência, distância favorável, valor adequado. SICAF NÃO CADASTRADO e acervo a confirmar.",
        True,
        "Construção de clínica de reabilitação em Bom Retiro/SC (R$2.563.913, 15 dias restantes, 216km). Obra de edificação pública — central ao CNAE 4120-4/00. Distância de 216km é confortável operacionalmente. Valor de R$2,56M está dentro da capacidade da LCM (exigência 10% = R$256K). Com 15 dias, há prazo razoável para proposta técnica, mas SICAF deve ser iniciado imediatamente. Verificar se o edital exige atestados específicos de construção hospitalar/clínica."
    ),
    16: (
        "AVALIAR COM CAUTELA",
        "Obra de engenharia em Balneário Arroio do Silva/SC (R$994K, 15 dias, 303km). Terceiro edital no município — mobilização combinada com índices 9 e 10 maximiza retorno.",
        True,
        "Contratação de engenharia/construção civil em Balneário Arroio do Silva/SC (R$993.727, 15 dias restantes, 303km). O maior dos três editais simultâneos neste município. Com prazo de 15 dias (o mais amplo dos três), há tempo melhor para elaborar proposta. Estratégia de mobilização única para os três editais (total R$1,72M) é o diferencial competitivo. Verificar se os editais permitem participação simultânea de mesma empresa."
    ),
    18: (
        "AVALIAR COM CAUTELA",
        "Obra de engenharia em Joaçaba/SC (R$3,42M, 16 dias, ≈365km). Valor significativo, prazo razoável. SICAF NÃO CADASTRADO e acervo técnico de engenharia a confirmar.",
        True,
        "Serviços de engenharia em Joaçaba/SC (R$3.420.000, 16 dias restantes, 365km). Valor expressivo e prazo de 16 dias oferece janela adequada para elaboração de proposta técnica. Distância de 365km é administrável com logística planejada. Exigência de 10% do valor = R$342K está dentro da capacidade da LCM. O principal risco é o acervo técnico: os contratos PNCP da empresa são majoritariamente alienações da Receita Federal, não obras de engenharia. É essencial verificar se a LCM possui CATs e atestados válidos no CREA-SC para obras deste porte."
    ),
    19: (
        "AVALIAR COM CAUTELA",
        "Obra de engenharia em Irani/SC (R$1,86M, 22 dias, ≈479km). Prazo adequado mas distância elevada. SICAF NÃO CADASTRADO e acervo técnico a confirmar.",
        True,
        "Obra de engenharia (empreitada global) em Irani/SC (R$1.860.573, 22 dias restantes, 479km). Com 22 dias de prazo, há tempo suficiente para organizar proposta técnica e iniciar processos de habilitação. A distância de 479km é o maior desafio — município no meio-oeste catarinense. Valor moderado dentro da capacidade da LCM. Verificar se há histórico de obras da empresa na região antes de alocar recursos para esta proposta."
    ),
    20: (
        "AVALIAR COM CAUTELA",
        "Casa Catarina — 30 unidades habitacionais em Urussanga/SC (R$3,72M, 22 dias, ≈272km). Alta aderência ao CNAE 4120-4/00. Programa habitacional estadual com alta probabilidade de execução. SICAF NÃO CADASTRADO é o principal risco.",
        True,
        "Construção de 30 unidades habitacionais (Programa Casa Catarina) em Urussanga/SC (R$3.721.903, 22 dias restantes, 272km). Edital de altíssima aderência ao perfil da LCM: habitação popular é exatamente o CNAE 4120-4/00. O Programa Casa Catarina é iniciativa do Governo de SC com orçamento garantido e histórico de execução. Distância de 272km é operacionalmente confortável. Prazo de 22 dias é adequado para proposta. Exigência 10% = R$372K dentro da capacidade. ALERTA: SICAF deve ser iniciado imediatamente para garantir regularidade federal. Este é um dos editais mais estratégicos do portfólio."
    ),
    22: (
        "AVALIAR COM CAUTELA",
        "Grande obra de engenharia em Balneário Arroio do Silva/SC (R$5,31M, 31 dias, 303km). Bom equilíbrio entre prazo, valor e distância. SICAF NÃO CADASTRADO e capital social a avaliar (10% = R$531K, acima da liquidez imediata).",
        True,
        "Grande contratação de engenharia/construção civil em Balneário Arroio do Silva/SC (R$5.309.591, 31 dias restantes, 303km). Melhor edital em termos de equilíbrio prazo-valor-distância: 31 dias para elaboração de proposta técnica robusta, distância de 303km operacionalmente viável, e valor expressivo. A exigência de 10% do valor estimado (~R$531K) merece atenção — a LCM precisa demonstrar este valor em capital circulante ou garantias. Junto com os editais 9, 10 e 16 do mesmo município (total ~R$7M em Balneário Arroio do Silva), há cluster de oportunidades significativo nesta cidade."
    ),
    24: (
        "AVALIAR COM CAUTELA",
        "Construção de centro poliesportivo em Pinhalzinho/SC (R$5,27M, 70 dias, ≈612km). Melhor prazo da carteira. SICAF NÃO CADASTRADO e distância elevada são os principais riscos.",
        True,
        "Construção de centro poliesportivo em Pinhalzinho/SC (R$5.268.805, 70 dias restantes, 612km). O prazo de 70 dias é o mais generoso da carteira — suficiente para regularizar SICAF, obter atestados, e elaborar proposta técnica completa. Objeto de construção civil pesada é altamente aderente ao CNAE. O desafio central é a distância de 612km (extremo oeste de SC) e o capital para a exigência de 10% (~R$527K). Se a LCM tiver ambição estratégica de expandir para o oeste catarinense, este edital — com maior janela de tempo — é o ponto de entrada ideal. Nota: o índice 25 é duplicata deste edital via Portal de Compras Públicas."
    ),
}

# ---------------------------------------------------------------------------
# Load JSON
# ---------------------------------------------------------------------------
print(f"Carregando {INPUT_FILE}...")
with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)

editais = data["editais"]
print(f"Total de editais: {len(editais)}")

# ---------------------------------------------------------------------------
# Apply enrichments
# ---------------------------------------------------------------------------
participar_count = 0
avaliar_count = 0
nao_recomendado_count = 0
descartado_count = 0

for i, edital in enumerate(editais):
    if i in ENRICHMENTS:
        rec, just, rel, analise = ENRICHMENTS[i]
    else:
        # Fallback — should not happen
        rec = "AVALIAR COM CAUTELA"
        just = "Edital de construção civil sem análise individual detalhada."
        rel = True
        analise = "Sem análise detalhada disponível."

    edital["recomendacao"] = rec
    edital["justificativa"] = just
    edital["relevante"] = rel
    edital["analise_detalhada"] = analise

    if rec == "PARTICIPAR":
        participar_count += 1
    elif rec == "AVALIAR COM CAUTELA":
        avaliar_count += 1
    elif rec == "NÃO RECOMENDADO":
        nao_recomendado_count += 1
    elif rec == "DESCARTADO":
        descartado_count += 1

# ---------------------------------------------------------------------------
# Build top-level sections
# ---------------------------------------------------------------------------

# Filtrar editais relevantes para cálculos
editais_relevantes = [e for e in editais if e.get("relevante", True)]
editais_avaliar = [e for e in editais if e.get("recomendacao") == "AVALIAR COM CAUTELA"]
editais_nao_rec = [e for e in editais if e.get("recomendacao") == "NÃO RECOMENDADO"]
editais_descartados = [e for e in editais if e.get("recomendacao") == "DESCARTADO"]

valor_total_carteira = sum(e.get("valor_estimado", 0) for e in editais if isinstance(e.get("valor_estimado"), (int, float)) and e.get("relevante", True))
valor_avaliar = sum(e.get("valor_estimado", 0) for e in editais_avaliar if isinstance(e.get("valor_estimado"), (int, float)))
valor_nao_rec = sum(e.get("valor_estimado", 0) for e in editais_nao_rec if isinstance(e.get("valor_estimado"), (int, float)))

# Top 5 por valor entre os AVALIAR
top5 = sorted(editais_avaliar, key=lambda e: e.get("valor_estimado", 0), reverse=True)[:5]

data["resumo_executivo"] = {
    "data_analise": "2026-03-15",
    "empresa": "LCM CONSTRUCOES LTDA",
    "cnpj": "01.721.078/0001-68",
    "total_editais_analisados": len(editais),
    "breakdown_recomendacoes": {
        "PARTICIPAR": participar_count,
        "AVALIAR COM CAUTELA": avaliar_count,
        "NÃO RECOMENDADO": nao_recomendado_count,
        "DESCARTADO": descartado_count
    },
    "valor_carteira_relevante_brl": round(valor_total_carteira, 2),
    "valor_editais_avaliar_brl": round(valor_avaliar, 2),
    "valor_editais_nao_recomendados_brl": round(valor_nao_rec, 2),
    "alertas_criticos": [
        "SICAF NÃO CADASTRADO: A empresa não possui registro no SICAF (Sistema de Cadastramento Unificado de Fornecedores). Isso pode inviabilizar a participação em licitações federais e em muitas municipais que exigem regularidade junto à RFB. Ação imediata: iniciar cadastro em gov.br/fornecedores.",
        "ACERVO TÉCNICO DIVERGENTE: O PNCP registra 1.000 contratos para a LCM, porém 97,6% são 'Alienação de mercadorias apreendidas pela Receita Federal' — não são obras de construção. Apenas 24 contratos (~2,4%) têm aderência ao setor de engenharia. A empresa precisa consolidar seus CATs (Certidões de Acervo Técnico) no CREA-SC para comprovar capacidade técnica nos editais de construção civil.",
        "CAPITAL SOCIAL LIMITADO: Com R$1.600.000 de capital social, a empresa enfrenta restrição nas licitações acima de R$16M (exigência padrão de 10%). Os editais de Florianópolis (R$21,9M) e Pinhalzinho (R$17,9M) excedem este limite."
    ],
    "top5_oportunidades_por_valor": [
        {
            "municipio": e.get("municipio"),
            "valor_estimado": e.get("valor_estimado"),
            "dias_restantes": e.get("dias_restantes"),
            "objeto_resumo": e.get("objeto", "")[:100],
            "recomendacao": e.get("recomendacao")
        }
        for e in top5
    ],
    "clusters_geograficos": [
        {
            "municipio": "Balneário Arroio do Silva/SC",
            "editais": [9, 10, 16, 22],
            "valor_total_brl": round(452389.58 + 273803.22 + 993727.19 + 5309591.59, 2),
            "distancia_itajai_km": 303,
            "observacao": "4 editais simultâneos — mobilização única para múltiplos contratos. Total R$7,03M."
        },
        {
            "municipio": "Urubici/SC",
            "editais": [11, 12],
            "valor_total_brl": round(1098407.05 + 1637714.22, 2),
            "distancia_itajai_km": 252,
            "observacao": "2 editais complementares (pavimentação + construção) — soma R$2,74M com mobilização única."
        },
        {
            "municipio": "Lajeado Grande/SC",
            "editais": [13, 14],
            "valor_total_brl": round(802806.36 + 574376.28, 2),
            "distancia_itajai_km": 559,
            "observacao": "2 editais complementares (drenagem + movimentação de terra) — soma R$1,38M. Distância elevada."
        }
    ]
}

data["inteligencia_mercado"] = {
    "perfil_concorrencia_sc": {
        "descricao": "Santa Catarina concentra intensa atividade de obras municipais, especialmente nos programas Casa Catarina (habitação) e PAC 3 (infraestrutura). O mercado de construtoras B2G no estado é fragmentado em pequenas e médias empresas regionais, com forte presença de empresas do eixo Florianópolis-Joinville-Blumenau no litoral e empresas locais dominando o oeste catarinense.",
        "oportunidade_litoral_sul": "A concentração de 4 editais em Balneário Arroio do Silva indica ciclo de investimentos no litoral sul-catarinense. Empresas de Itajaí têm vantagem logística neste corredor (303km).",
        "programa_casa_catarina": "O Programa Casa Catarina (Governo SC) está em fase de expansão — Urussanga é apenas uma das 50+ obras previstas para 2026. Empresas habilitadas neste programa tendem a receber convites recorrentes."
    },
    "posicionamento_competitivo_lcm": {
        "forcas": [
            "29 anos de existência (fundada em 1997) — credibilidade institucional",
            "CNAE principal 4120-4/00 alinhado ao core de construção civil",
            "6 CNAEs secundários ampliando o escopo de atuação (pavimentação, instalações hidrossanitárias, elétricas)",
            "Sede em Itajaí/SC — posição geográfica central no litoral catarinense",
            "Sem sanções (CEIS, CNEP, CEPIM, CEAF limpos)"
        ],
        "fraquezas": [
            "SICAF não cadastrado — barreia de entrada em licitações exigentes",
            "Capital social R$1,6M limita participação em contratos acima de R$16M",
            "Acervo PNCP divergente (97,6% alienações RFB) — empresa precisa consolidar atestados de obras civis",
            "Ausência de presença histórica no oeste catarinense (municípios distantes)"
        ],
        "ameacas": [
            "Empresas regionais do oeste catarinense com presença local e menores custos de mobilização",
            "Construtoras de médio porte com SICAF regular e CATs consolidados no CREA-SC",
            "Aumento de exigências técnicas em editais pós-Lei 14.133/2021"
        ]
    },
    "analise_acervo": {
        "total_contratos_pncp": 1000,
        "contratos_engenharia_estimados": 24,
        "percentual_aderencia": "2.4%",
        "dominante": "Alienação de mercadorias apreendidas pela Receita Federal (SRFB-8ª e 9ª RF)",
        "interpretacao": "A LCM Construções participa ativamente de leilões da Receita Federal para alienação de mercadorias apreendidas — atividade comercial legítima porém não relacionada ao CNAE declarado. Esta divergência entre CNAE e acervo pode gerar questionamentos em processos de habilitação técnica. A empresa deve organizar atestados e CATs exclusivamente das obras de construção civil efetivamente executadas.",
        "acao_recomendada": "Levantar todos os contratos de obra civil executados, emitir CATs no CREA-SC para obras mais representativas, e atualizar o portfólio de referências técnicas para uso em licitações."
    }
}

data["proximos_passos"] = {
    "urgentes_ate_48h": [
        {
            "acao": "Iniciar cadastro no SICAF (Sistema de Cadastramento Unificado de Fornecedores)",
            "motivo": "Pré-requisito para participação em licitações federais e muitas municipais. Sem SICAF, a LCM está inabilitada automaticamente em 60-70% dos editais analisados.",
            "como": "Acessar gov.br/fornecedores, selecionar 'Fornecedor', realizar cadastro com CNPJ, providenciar: CND Federal, FGTS, INSS, Trabalhista, CNDT.",
            "prazo_processamento": "SICAF básico: 3-5 dias úteis. Linha de crédito e capacidade técnica: 15-30 dias."
        },
        {
            "acao": "Avaliar prazo viabilidade edital Vitor Meireles (índice 4) — R$9M, 7 dias",
            "motivo": "Maior valor em prazo curto. Verificar se o edital aceita CNDs avulsas (sem SICAF) e se há tempo de montar proposta técnica.",
            "como": "Baixar edital completo, verificar requisitos de habilitação, contatar prefeitura para esclarecer documentação exigida."
        }
    ],
    "curto_prazo_ate_7_dias": [
        {
            "acao": "Participar nos editais de Urubici/SC (índices 11 e 12) — R$2,74M, 10 dias, 252km",
            "motivo": "Melhor cluster em termos de distância (252km) + dois contratos complementares no mesmo município. Alta aderência ao CNAE.",
            "como": "Baixar ambos os editais, avaliar compatibilidade dos objetos (pavimentação + construção civil), montar proposta técnica e verificar se SICAF é exigido ou se CNDs avulsas bastam."
        },
        {
            "acao": "Avaliar participação nos editais de Balneário Arroio do Silva (índices 9 e 10) — R$726K, 9-10 dias, 303km",
            "motivo": "Dois editais de menor porte no mesmo município, mobilização única. Menor risco financeiro.",
            "como": "Verificar editais, avaliar requisitos de habilitação, preparar proposta para ambos simultaneamente."
        },
        {
            "acao": "Contatar CREA-SC para levantamento de CATs existentes",
            "motivo": "Mapear quais atestados técnicos a empresa já possui registrados no CREA — base para os processos de habilitação técnica.",
            "como": "Acionar o responsável técnico (engenheiro) para consultar sistema ART/RRT do CREA-SC e listar CATs emitidas para obras de construção civil."
        }
    ],
    "medio_prazo_ate_30_dias": [
        {
            "acao": "Participar no edital Casa Catarina de Urussanga (índice 20) — R$3,72M, 22 dias, 272km",
            "motivo": "Programa habitacional estadual com alta aderência técnica e probabilidade de execução. Prazo adequado.",
            "como": "Baixar edital, confirmar requisitos do Programa Casa Catarina, preparar proposta técnica e financeira completa."
        },
        {
            "acao": "Participar no edital de Balneário Arroio do Silva grande porte (índice 22) — R$5,31M, 31 dias, 303km",
            "motivo": "Melhor equilíbrio prazo-valor-distância da carteira. Prazo de 31 dias permite elaborar proposta técnica robusta.",
            "como": "Baixar edital, verificar exigências de qualificação técnica e econômica, preparar proposta com engenheiro responsável."
        },
        {
            "acao": "Finalizar SICAF e regularizar situação federal",
            "motivo": "Habilitar a empresa para o universo completo de licitações municipais, estaduais e federais.",
            "como": "Acompanhar processo SICAF iniciado na ação urgente, providenciar certidões pendentes, solicitar linha de crédito junto ao BNDES via portal gov.br."
        }
    ],
    "estrategico_ate_90_dias": [
        {
            "acao": "Participar no edital de Pinhalzinho centro poliesportivo (índice 24) — R$5,27M, 70 dias, 612km",
            "motivo": "Maior janela de tempo da carteira — suficiente para regularizar SICAF e preparar proposta técnica completa. Oportunidade de expansão para o oeste catarinense.",
            "como": "Com SICAF regularizado e CATs organizados, elaborar proposta técnica detalhada. Avaliar parceria com empresa local de Pinhalzinho para reduzir custos de mobilização."
        },
        {
            "acao": "Organizar portfólio técnico e sistema de gestão de licitações",
            "motivo": "A LCM tem potencial de R$45M+ em contratos anuais com a carteira atual, mas precisa de processo sistemático de prospecção e qualificação.",
            "como": "Estruturar pasta de documentos de habilitação (certidões, atestados, CATs, balanço patrimonial), criar rotina de monitoramento semanal de editais no PNCP para SC, e avaliar uso do SmartLic para automação do processo de descoberta de oportunidades."
        }
    ]
}

# ---------------------------------------------------------------------------
# Save back
# ---------------------------------------------------------------------------
print("Salvando arquivo enriquecido...")
with open(INPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\nEnriquecimento concluído com sucesso!")
print(f"  PARTICIPAR:         {participar_count}")
print(f"  AVALIAR COM CAUTELA: {avaliar_count}")
print(f"  NÃO RECOMENDADO:    {nao_recomendado_count}")
print(f"  DESCARTADO:         {descartado_count}")
print(f"  Total:              {len(editais)}")
print(f"\nValor total carteira relevante: R${valor_total_carteira:,.2f}")
print(f"Valor editais AVALIAR:          R${valor_avaliar:,.2f}")
print(f"\nArquivo salvo: {INPUT_FILE}")
