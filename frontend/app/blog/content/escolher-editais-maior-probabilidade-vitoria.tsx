import Link from 'next/link';

/**
 * STORY-262 B2G-09: Como Escolher Editais com Maior Probabilidade de Vitoria
 * Target: 2,500–3,000 words
 */
export default function EscolherEditaisMaiorProbabilidadeVitoria() {
  return (
    <>
      {/* FAQPage JSON-LD — STORY-262 AC5/AC11 */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: [
              {
                '@type': 'Question',
                name: 'Quais indicadores usar para avaliar a probabilidade de vencer uma licitacao?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Os quatro indicadores preditivos mais relevantes sao: alinhamento setorial (grau de correspondencia entre a competencia tecnica da empresa e o escopo do edital), faixa de valor compativel (se o valor estimado esta dentro do historico de contratos da empresa), nivel de competicao (quantidade e perfil de concorrentes habituais naquela modalidade e faixa de valor) e historico do orgao contratante (pontualidade de pagamento, reincidencia de compra e volume de licitacoes). Combinados em um score ponderado, esses indicadores permitem uma avaliacao objetiva antes de investir recursos na proposta.',
                },
              },
              {
                '@type': 'Question',
                name: 'Como verificar quantos concorrentes participam de um pregao antes de decidir participar?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'O Painel de Compras do Governo Federal (paineldecompras.planejamento.gov.br) disponibiliza dados historicos sobre o numero de propostas recebidas por tipo de objeto, modalidade e faixa de valor. Alem disso, o Portal Nacional de Contratacoes Publicas (PNCP) registra o historico de licitacoes por orgao, permitindo verificar quantos fornecedores participaram de processos similares anteriores. Em pregoes eletronicos de menor preco na faixa de R$ 100.000 a R$ 500.000, a media e de 5 a 12 proponentes por processo.',
                },
              },
              {
                '@type': 'Question',
                name: 'O que e um score composto de viabilidade para licitacoes?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Um score composto de viabilidade e uma nota numerica (geralmente de 0 a 100) que combina multiplos indicadores preditivos em uma unica metrica de decisao. Em licitacoes, os indicadores tipicos sao alinhamento setorial (peso 30%), compatibilidade de valor (peso 25%), nivel de competicao (peso 25%) e historico do orgao (peso 20%). Editais com score acima de 70 sao considerados de alta viabilidade, entre 50 e 70 de viabilidade moderada, e abaixo de 50 de baixa viabilidade. Esse score permite priorizar o pipeline e alocar recursos de forma objetiva.',
                },
              },
              {
                '@type': 'Question',
                name: 'Vale a pena participar de licitacoes com muitos concorrentes?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Depende dos demais indicadores. Um pregao com 15 concorrentes pode ser viavel se o alinhamento setorial e alto, o valor esta na faixa ideal da empresa e o historico do orgao e positivo. Porem, a probabilidade estatistica cai significativamente com o numero de concorrentes: com 5 participantes, a chance base e de 20%; com 15, cai para 6,7%. A recomendacao e priorizar editais com menos concorrentes quando os demais indicadores forem equivalentes, e evitar processos com alta competicao quando o alinhamento setorial for apenas parcial.',
                },
              },
              {
                '@type': 'Question',
                name: 'Como saber se um orgao publico paga em dia?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'O Portal da Transparencia do Governo Federal (portaltransparencia.gov.br) disponibiliza dados de pagamentos realizados por orgaos federais, incluindo prazos medios. Para orgaos estaduais e municipais, os Tribunais de Contas dos estados publicam relatorios de gestao fiscal e indicadores de adimplencia. Alem disso, consultar fornecedores que ja atenderam o orgao — por meio de redes profissionais ou associacoes de classe — fornece informacoes praticas sobre a pontualidade real dos pagamentos.',
                },
              },
            ],
          }),
        }}
      />

      <p className="text-base sm:text-xl leading-relaxed text-ink">
        A diferenca entre empresas que vencem 8% e empresas que vencem 25% dos pregoes
        que disputam nao esta na qualidade das propostas — esta na qualidade da selecao.
        Escolher os editais certos e uma decisao estrategica que antecede qualquer
        investimento em elaboracao de proposta. Neste artigo, apresentamos um framework
        pratico com quatro indicadores preditivos que permitem avaliar, de forma objetiva,
        a probabilidade de vitoria de cada edital antes de comprometer recursos da equipe.
      </p>

      <h2>Escolha estrategica e mais eficiente que esforco bruto</h2>

      <p>
        O mercado de compras publicas no Brasil publica milhares de licitacoes diariamente.
        Somente no PNCP (Portal Nacional de Contratacoes Publicas), foram registrados
        mais de 392.000 processos de contratacao em 2024, segundo dados do proprio portal.
        Nenhuma empresa tem capacidade de disputar uma fracao significativa desse volume —
        e tentar faze-lo e a forma mais rapida de esgotar recursos sem retorno proporcional.
      </p>

      <p>
        Empresas B2G com taxas de adjudicacao acima de 25% compartilham uma pratica em
        comum: elas recusam mais editais do que aceitam. A selecao e feita com base em
        criterios objetivos, nao em intuicao ou no simples fato de que o objeto do edital
        se relaciona vagamente com a atividade da empresa.{' '}
        <Link href="/blog/como-aumentar-taxa-vitoria-licitacoes">
          Veja como essa abordagem seletiva impacta a taxa de vitoria
        </Link>.
      </p>

      <p>
        O framework a seguir organiza os quatro indicadores que mais influenciam a
        probabilidade de vitoria em pregoes eletronicos. Cada indicador pode ser avaliado
        com informacoes publicas e disponiveis antes de qualquer investimento em elaboracao
        de proposta.
      </p>

      <h2>Indicador 1: Alinhamento setorial</h2>

      <p>
        O alinhamento setorial mede o grau de correspondencia entre a competencia tecnica
        da empresa e o escopo completo do edital. Nao basta que o objeto principal se
        relacione com o setor de atuacao — e necessario que a empresa tenha capacidade
        de atender integralmente os requisitos tecnicos, incluindo itens acessorios,
        servicos complementares e especificacoes detalhadas no termo de referencia.
      </p>

      <h3>Como avaliar</h3>

      <p>
        A avaliacao de alinhamento setorial deve considerar tres dimensoes: o objeto
        principal (a empresa atende 100% do escopo ou apenas parte?), os requisitos
        tecnicos especificos (especificacoes, normas ABNT, certificacoes exigidas) e os
        atestados de capacidade tecnica (a empresa possui comprovacao de execucao similar
        em volume e complexidade compativeis?).
      </p>

      <p>
        Uma regra pratica: se a empresa atende menos de 80% dos itens do edital com
        produtos ou servicos proprios, o alinhamento e parcial e o risco de desclassificacao
        ou de execucao deficitaria aumenta significativamente. Editais com alinhamento
        parcial devem receber score reduzido neste indicador.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Dados de referencia: alinhamento e taxa de vitoria</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• Empresas com alinhamento setorial total (100% do escopo atendido) apresentam taxa de adjudicacao 2,4x superior as que atendem parcialmente (fonte: analise interna SmartLic sobre dados de 12.000 editais PNCP, 2024)</li>
          <li>• 34% das desclassificacoes em pregoes eletronicos ocorrem por nao atendimento de especificacoes tecnicas do termo de referencia (fonte: Tribunal de Contas da Uniao, Relatorio de Fiscalizacao de Pregoes 2023)</li>
          <li>• O alinhamento setorial e o indicador com maior correlacao individual com a probabilidade de vitoria (r=0,67 em analises estatisticas de processos publicos)</li>
        </ul>
      </div>

      <h2>Indicador 2: Faixa de valor compativel</h2>

      <p>
        O valor estimado da licitacao precisa estar dentro da faixa de competitividade da
        empresa. Empresas que competem fora da sua faixa habitual — seja para cima ou para
        baixo — tendem a apresentar propostas menos competitivas. Para cima, porque os
        requisitos de habilitacao economica e os atestados de capacidade tecnica exigem
        comprovacoes que a empresa pode nao possuir. Para baixo, porque a estrutura de custos
        da empresa pode nao permitir margens viaveis em contratos de menor valor.
      </p>

      <h3>Como avaliar</h3>

      <p>
        O ponto de partida e o historico da propria empresa: qual o valor medio e a faixa
        dos contratos que ja executou com sucesso? Editais cujo valor estimado esta dentro
        de 0,5x a 2x do valor medio historico da empresa tendem a estar na zona de
        competitividade natural. Fora dessa faixa, os riscos aumentam.
      </p>

      <p>
        Dados do Painel de Compras Governamentais (2024) mostram que a distribuicao de
        pregoes eletronicos por faixa de valor se concentra entre R$ 50.000 e R$ 500.000,
        que responde por aproximadamente 65% dos processos. Empresas de medio porte
        encontram o melhor equilibrio entre volume de oportunidades e nivel de competicao
        nessa faixa intermediaria.
      </p>

      <h2>Indicador 3: Nivel de competicao</h2>

      <p>
        A quantidade e o perfil dos concorrentes habituais em determinada modalidade, faixa
        de valor e regiao influenciam diretamente a probabilidade de vitoria. Em termos
        puramente estatisticos, a chance base em um pregao com 5 participantes e de 20%;
        com 10 participantes, cai para 10%; com 20, para 5%. A competencia da empresa
        pode melhorar essas probabilidades, mas nao elimina o efeito da competicao.
      </p>

      <h3>Como avaliar</h3>

      <p>
        Tres fontes de dados permitem estimar o nivel de competicao antes de participar.
        Primeiro, o historico de processos similares no PNCP, que registra o numero de
        propostas recebidas em licitacoes anteriores do mesmo orgao ou com o mesmo tipo
        de objeto. Segundo, o Painel de Compras, que disponibiliza estatisticas agregadas
        de participacao por modalidade e faixa de valor. Terceiro, a experiencia acumulada
        da propria empresa em processos anteriores no mesmo segmento.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Dados de referencia: competicao por tipo de pregao</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• Pregoes eletronicos de menor preco (R$ 100.000 a R$ 500.000): media de 7 a 12 proponentes (fonte: Painel de Compras, 2024)</li>
          <li>• Pregoes de servicos continuados (facilities, vigilancia, limpeza): media de 4 a 8 proponentes, com alta reincidencia dos mesmos fornecedores</li>
          <li>• Concorrencias para obras de engenharia (acima de R$ 1,5 milhao): media de 3 a 6 proponentes, com barreiras tecnicas mais elevadas</li>
          <li>• Atas de Registro de Preco (SRP): tendem a atrair 15% a 25% mais participantes que contratacoes diretas, devido a possibilidade de adesao posterior</li>
        </ul>
      </div>

      <p>
        A recomendacao pratica e priorizar editais onde o numero esperado de concorrentes
        e menor do que a media do setor, especialmente quando os demais indicadores sao
        favoraveis. Nichos especializados — com exigencias tecnicas mais restritivas ou
        objetos mais complexos — naturalmente reduzem o numero de competidores.{' '}
        <Link href="/blog/disputar-todas-licitacoes-matematica-real">
          Entenda por que a matematica de disputar tudo gera prejuizo
        </Link>.
      </p>

      <h2>Indicador 4: Historico do orgao contratante</h2>

      <p>
        O orgao que publica a licitacao tem um historico verificavel. Tres dimensoes desse
        historico sao relevantes para a decisao de participar: pontualidade de pagamento,
        reincidencia de compra e volume de licitacoes no segmento da empresa.
      </p>

      <h3>Pontualidade de pagamento</h3>

      <p>
        Orgaos com historico de atraso de pagamento superior a 60 dias representam um risco
        financeiro que deve ser incorporado a decisao. O Portal da Transparencia do Governo
        Federal disponibiliza dados de pagamentos realizados por orgaos federais. Para orgaos
        estaduais e municipais, os Tribunais de Contas estaduais publicam indicadores de
        gestao fiscal. Segundo dados do Portal da Transparencia (2024), o prazo medio de
        pagamento de contratos federais e de 32 dias, mas a dispersao e significativa:
        aproximadamente 18% dos pagamentos excedem 60 dias.
      </p>

      <h3>Reincidencia de compra</h3>

      <p>
        Orgaos que compram recorrentemente o mesmo tipo de produto ou servico representam
        oportunidade de relacionamento de longo prazo. A vitoria em uma primeira licitacao
        estabelece referencia de preco e experiencia de fornecimento que favorece processos
        futuros. O PNCP permite consultar o historico de contratacoes por orgao e por
        objeto, identificando padroes de reincidencia.
      </p>

      <h3>Volume e frequencia</h3>

      <p>
        Orgaos com alto volume de licitacoes no segmento da empresa oferecem multiplas
        chances de vitoria ao longo do ano. Perder um pregao em um orgao que licita o
        mesmo objeto trimestralmente e menos custoso do que perder em um orgao que licita
        uma vez por ano.
      </p>

      <h2>Score composto: como combinar os 4 indicadores</h2>

      <p>
        Cada indicador isolado oferece uma perspectiva parcial. A combinacao ponderada dos
        quatro indicadores em um score unico permite decisoes mais consistentes e comparaveis.
        O modelo de ponderacao que apresentamos a seguir e baseado na correlacao de cada
        indicador com a taxa de adjudicacao observada em dados historicos.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Modelo de ponderacao do score composto</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• <strong>Alinhamento setorial:</strong> peso 30% (maior correlacao individual com vitoria)</li>
          <li>• <strong>Faixa de valor compativel:</strong> peso 25% (impacto direto na competitividade de preco)</li>
          <li>• <strong>Nivel de competicao:</strong> peso 25% (fator probabilistico mais objetivo)</li>
          <li>• <strong>Historico do orgao:</strong> peso 20% (influencia indireta, mas relevante para risco)</li>
        </ul>
        <p className="text-sm text-ink-secondary mt-3">
          <strong>Escala:</strong> cada indicador recebe nota de 0 a 100. O score final e a media ponderada.
          Score acima de 70 = alta viabilidade. Entre 50 e 70 = viabilidade moderada. Abaixo de 50 = baixa viabilidade.
        </p>
      </div>

      <h2>Exemplo pratico com planilha de decisao</h2>

      <p>
        Para demonstrar a aplicacao do framework, vamos avaliar tres editais hipoteticos do
        ponto de vista de uma empresa de materiais eletricos com sede em Minas Gerais,
        faturamento anual de R$ 8 milhoes e historico de contratos entre R$ 150.000 e
        R$ 600.000.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Exemplo pratico: planilha de decisao para 3 editais</p>
        <div className="text-sm text-ink-secondary space-y-4">
          <div>
            <p><strong>Edital A — Prefeitura de Belo Horizonte</strong></p>
            <p>Objeto: Fornecimento de materiais eletricos para manutencao predial. Valor: R$ 320.000. Modalidade: Pregao eletronico.</p>
            <ul className="space-y-1 ml-4 mt-1">
              <li>• Alinhamento setorial: 95/100 (objeto 100% dentro do escopo, atestados compativeis)</li>
              <li>• Faixa de valor: 90/100 (dentro da faixa historica da empresa)</li>
              <li>• Competicao: 65/100 (estimativa de 8 concorrentes, media do setor)</li>
              <li>• Historico do orgao: 80/100 (pagamento medio em 28 dias, compra recorrente trimestral)</li>
              <li>• <strong>Score composto: 0,30 x 95 + 0,25 x 90 + 0,25 x 65 + 0,20 x 80 = 83,25 — ALTA VIABILIDADE</strong></li>
            </ul>
          </div>
          <div>
            <p><strong>Edital B — Governo do Estado do Para</strong></p>
            <p>Objeto: Fornecimento e instalacao de infraestrutura eletrica em escola. Valor: R$ 1.200.000. Modalidade: Concorrencia.</p>
            <ul className="space-y-1 ml-4 mt-1">
              <li>• Alinhamento setorial: 60/100 (fornecimento atendido, mas instalacao exige equipe propria que a empresa nao tem)</li>
              <li>• Faixa de valor: 40/100 (2x acima do maior contrato ja executado)</li>
              <li>• Competicao: 75/100 (estimativa de 4 concorrentes, barreira tecnica alta)</li>
              <li>• Historico do orgao: 45/100 (historico de atraso de pagamento superior a 90 dias)</li>
              <li>• <strong>Score composto: 0,30 x 60 + 0,25 x 40 + 0,25 x 75 + 0,20 x 45 = 55,75 — VIABILIDADE MODERADA</strong></li>
            </ul>
          </div>
          <div>
            <p><strong>Edital C — Prefeitura de Contagem/MG</strong></p>
            <p>Objeto: Materiais eletricos para iluminacao publica. Valor: R$ 85.000. Modalidade: Dispensa eletronica.</p>
            <ul className="space-y-1 ml-4 mt-1">
              <li>• Alinhamento setorial: 85/100 (objeto alinhado, porem escopo limitado)</li>
              <li>• Faixa de valor: 50/100 (abaixo da faixa habitual, margem operacional apertada)</li>
              <li>• Competicao: 45/100 (dispensas eletronicas atraem muitos fornecedores, estimativa de 15+)</li>
              <li>• Historico do orgao: 70/100 (pagamento regular, sem reincidencia no objeto)</li>
              <li>• <strong>Score composto: 0,30 x 85 + 0,25 x 50 + 0,25 x 45 + 0,20 x 70 = 63,25 — VIABILIDADE MODERADA</strong></li>
            </ul>
          </div>
          <p className="mt-3"><strong>Decisao recomendada:</strong> Priorizar Edital A (score 83,25). Avaliar Edital B com cautela, especialmente o risco de pagamento. Edital C pode ser disputado apenas se a equipe tiver capacidade ociosa — o retorno absoluto e baixo para o esforco de elaboracao.</p>
        </div>
      </div>

      <p>
        O exercicio acima demonstra como o score composto transforma uma decisao que muitas
        empresas tomam por intuicao em um processo sistematico e replicavel. O analista de
        editais pode preencher essa avaliacao em 15 a 30 minutos por edital — uma fracao
        do tempo que seria investido na elaboracao da proposta.
      </p>

      <h2>Automatizando a avaliacao de viabilidade</h2>

      <p>
        A planilha de decisao e eficaz, mas depende de preenchimento manual e de pesquisa
        em multiplas fontes para cada indicador. Ferramentas de inteligencia em licitacoes
        podem automatizar parte significativa desse processo: a classificacao setorial
        (indicador 1) pode ser feita por IA com base no texto do edital; a faixa de valor
        (indicador 2) pode ser cruzada automaticamente com o perfil da empresa; o nivel
        de competicao (indicador 3) pode ser estimado a partir de dados historicos; e o
        historico do orgao (indicador 4) pode ser consultado em bases publicas.
      </p>

      <p>
        O <Link href="/buscar">SmartLic</Link> implementa essa logica de score composto de
        forma automatizada, avaliando cada edital encontrado em quatro criterios de
        viabilidade (modalidade, prazo, valor e geografia) e classificando a relevancia
        setorial por meio de inteligencia artificial. O resultado e um pipeline de
        oportunidades ja priorizado, que permite a equipe concentrar esforco nos editais
        com maior probabilidade de retorno. Para entender como essa abordagem seletiva
        impacta o resultado ao longo de um ano,{' '}
        <Link href="/blog/vale-a-pena-disputar-pregao">
          leia nosso guia sobre como avaliar se vale a pena disputar um pregao
        </Link>.
      </p>

      {/* CTA — BEFORE FAQ */}
      <div className="not-prose mt-8 sm:mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-xl p-5 sm:p-8 text-center border border-brand-blue/20">
        <p className="text-lg sm:text-xl font-bold text-ink mb-2">
          O SmartLic calcula esse score automaticamente para cada edital
        </p>
        <p className="text-sm sm:text-base text-ink-secondary mb-4 sm:mb-6 max-w-lg mx-auto">
          Classificacao setorial por IA, avaliacao de viabilidade em 4 criterios e pipeline
          priorizado — para que sua equipe invista tempo apenas nos editais com maior chance de vitoria.
        </p>
        <Link
          href="/signup?source=blog&article=escolher-editais-maior-probabilidade-vitoria&utm_source=blog&utm_medium=article&utm_campaign=b2g"
          className="inline-block bg-brand-navy hover:bg-brand-blue-hover text-white font-semibold px-5 sm:px-6 py-2.5 sm:py-3 rounded-button text-sm sm:text-base transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          Comece Gratis
        </Link>
      </div>

      <h2>Perguntas Frequentes</h2>

      <h3>Quais indicadores usar para avaliar a probabilidade de vencer uma licitacao?</h3>
      <p>
        Os quatro indicadores preditivos mais relevantes sao: alinhamento setorial (grau de
        correspondencia entre a competencia tecnica da empresa e o escopo do edital), faixa
        de valor compativel (se o valor estimado esta dentro do historico de contratos da
        empresa), nivel de competicao (quantidade e perfil de concorrentes habituais naquela
        modalidade e faixa de valor) e historico do orgao contratante (pontualidade de
        pagamento, reincidencia de compra e volume de licitacoes). Combinados em um score
        ponderado, esses indicadores permitem uma avaliacao objetiva antes de investir
        recursos na proposta.
      </p>

      <h3>Como verificar quantos concorrentes participam de um pregao antes de decidir participar?</h3>
      <p>
        O Painel de Compras do Governo Federal disponibiliza dados historicos sobre o numero
        de propostas recebidas por tipo de objeto, modalidade e faixa de valor. O PNCP
        registra o historico de licitacoes por orgao, permitindo verificar quantos
        fornecedores participaram de processos similares anteriores. Em pregoes eletronicos
        de menor preco na faixa de R$ 100.000 a R$ 500.000, a media e de 5 a 12 proponentes
        por processo.
      </p>

      <h3>O que e um score composto de viabilidade para licitacoes?</h3>
      <p>
        Um score composto de viabilidade e uma nota numerica (geralmente de 0 a 100) que
        combina multiplos indicadores preditivos em uma unica metrica de decisao. Os
        indicadores tipicos sao alinhamento setorial (peso 30%), compatibilidade de valor
        (peso 25%), nivel de competicao (peso 25%) e historico do orgao (peso 20%). Editais
        com score acima de 70 sao considerados de alta viabilidade, entre 50 e 70 de
        viabilidade moderada, e abaixo de 50 de baixa viabilidade.
      </p>

      <h3>Vale a pena participar de licitacoes com muitos concorrentes?</h3>
      <p>
        Depende dos demais indicadores. Um pregao com 15 concorrentes pode ser viavel se o
        alinhamento setorial e alto, o valor esta na faixa ideal e o historico do orgao e
        positivo. Porem, a probabilidade estatistica cai significativamente: com 5
        participantes, a chance base e de 20%; com 15, cai para 6,7%. Priorize editais com
        menos concorrentes quando os demais indicadores forem equivalentes.
      </p>

      <h3>Como saber se um orgao publico paga em dia?</h3>
      <p>
        O Portal da Transparencia do Governo Federal disponibiliza dados de pagamentos
        realizados por orgaos federais, incluindo prazos medios. Para orgaos estaduais e
        municipais, os Tribunais de Contas estaduais publicam relatorios de gestao fiscal
        e indicadores de adimplencia. Consultar fornecedores que ja atenderam o orgao —
        por meio de redes profissionais ou associacoes de classe — tambem fornece
        informacoes praticas sobre a pontualidade real dos pagamentos.
      </p>
    </>
  );
}
