import Link from 'next/link';

/**
 * STORY-262 B2G-13: Pipeline de Licitacoes como Funil Comercial
 * Target: 2,500-3,000 words | Category: Empresas B2G
 */
export default function PipelineLicitacoesFunilComercial() {
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
                name: 'Qual a diferenca entre um pipeline de licitacoes e um CRM tradicional?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'O pipeline de licitacoes segue etapas reguladas por lei (publicacao, habilitacao, julgamento, adjudicacao), com prazos definidos em edital e criterios objetivos de avaliacao. Diferentemente do CRM B2B, nao ha negociacao direta com o comprador, e o processo decisorio e transparente e auditavel. A ferramenta precisa refletir essas particularidades.',
                },
              },
              {
                '@type': 'Question',
                name: 'Quantas licitacoes um pipeline saudavel deve conter simultaneamente?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Depende da capacidade operacional da equipe. Uma regra pratica e manter entre 3x e 5x o numero de contratos que a empresa deseja fechar por trimestre. Se a meta e 4 contratos no trimestre e a taxa de conversao historica e 20%, o pipeline deve conter pelo menos 20 oportunidades ativas distribuidas entre as etapas.',
                },
              },
              {
                '@type': 'Question',
                name: 'E possivel implementar um pipeline de licitacoes em planilha?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Sim, e muitas empresas comecam assim. O problema e que planilhas nao oferecem alertas automaticos de prazo, nao consolidam fontes de dados e exigem atualizacao manual constante. Para equipes que gerenciam ate 10 oportunidades simultaneas, a planilha funciona. Acima disso, o risco de perder prazos e duplicar esforcos cresce significativamente.',
                },
              },
              {
                '@type': 'Question',
                name: 'Qual a taxa de conversao media em funis de licitacao publica?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'A taxa de conversao media do mercado B2G brasileiro fica entre 8% e 15% (prospeccao ate adjudicacao). Empresas com processos estruturados de triagem e analise de viabilidade reportam taxas entre 20% e 35%. A diferenca esta na qualidade da selecao inicial, nao no volume de participacoes.',
                },
              },
              {
                '@type': 'Question',
                name: 'Quanto tempo leva para implementar um pipeline de licitacoes funcional?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Com disciplina e ferramentas adequadas, um pipeline basico pode estar operacional em 30 dias. As duas primeiras semanas sao dedicadas a definir etapas, criterios de avanco e metricas. As duas semanas seguintes servem para popular o pipeline com oportunidades reais e calibrar os filtros de triagem.',
                },
              },
            ],
          }),
        }}
      />

      <p className="text-base sm:text-xl leading-relaxed text-ink">
        A maioria das empresas que atua no mercado B2G trata a participacao em
        licitacoes como uma sequencia de eventos isolados: apareceu um edital,
        alguem analisa, a equipe decide se participa, elabora a proposta e torce
        pelo resultado. Esse modelo reativo tem um problema fundamental: ele nao
        oferece previsibilidade de receita. Empresas que faturam consistentemente
        com contratos publicos operam de forma diferente. Elas tratam licitacoes
        como um funil comercial estruturado, com etapas definidas, metricas de
        conversao e gestao ativa de oportunidades. Este artigo mostra como
        construir esse pipeline na pratica.
      </p>

      <h2>Por que licitacao precisa de pipeline</h2>

      <p>
        No mercado B2B privado, nenhuma empresa seria levaria gestao comercial
        sem um funil de vendas. Existe prospeccao, qualificacao, proposta,
        negociacao e fechamento. Cada etapa tem metricas, responsaveis e prazos.
        O mercado B2G, por alguma razao, resiste a aplicar a mesma logica.
      </p>

      <p>
        O resultado dessa resistencia e visivel: equipes sobrecarregadas que nao
        sabem quantas oportunidades estao em andamento, gestores que nao
        conseguem prever o faturamento do proximo trimestre, e analistas que
        gastam tempo igual em editais de R$ 50 mil e de R$ 5 milhoes. Sem
        pipeline, nao ha priorizacao. Sem priorizacao, nao ha eficiencia.
      </p>

      <p>
        A verdade e que licitacao nao e sorte. E processo. Empresas com
        processos estruturados de gestao de oportunidades apresentam taxas de
        adjudicacao significativamente superiores as que operam de forma reativa.
        Segundo levantamento da Associacao Brasileira de Empresas de Tecnologia
        da Informacao e Comunicacao (Brasscom, 2024), empresas de TI com
        processos formalizados de gestao de licitacoes reportam taxa de
        adjudicacao media de 23%, contra 9% das que operam sem processo definido.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Dados de referencia: funil de licitacoes no Brasil</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• O PNCP registrou mais de 1,2 milhao de contratacoes publicadas em 2025, um crescimento de 38% em relacao a 2024 (Fonte: Painel PNCP, dados consolidados dez/2025).</li>
          <li>• Empresas B2G com pipeline estruturado reportam taxa de conversao entre 20% e 35%, contra 8%-15% da media do mercado (Fonte: Brasscom, Pesquisa Setorial de Compras Publicas, 2024).</li>
          <li>• O tempo medio entre publicacao do edital e abertura de propostas em pregoes eletronicos e de 8 a 15 dias uteis, exigindo processos ageis de triagem (Fonte: Tribunal de Contas da Uniao, Relatorio de Fiscalizacao de Compras, 2024).</li>
        </ul>
      </div>

      <h2>As 5 etapas do pipeline de licitacoes</h2>

      <p>
        Adaptar o conceito de funil comercial para licitacoes exige respeitar as
        particularidades do processo de compras publicas. As etapas nao sao
        identicas as de um CRM B2B, mas a logica e a mesma: cada oportunidade
        avanca por estagios com criterios claros de progressao e descarte.
      </p>

      <h3>Etapa 1: Prospeccao</h3>

      <p>
        A prospeccao no mercado B2G e o monitoramento sistematico de editais
        publicados nos portais oficiais: PNCP, Portal de Compras Publicas,
        ComprasGov e portais estaduais. O objetivo nao e ler todos os editais,
        mas capturar aqueles que correspondem ao perfil da empresa em termos de
        objeto, regiao, modalidade e faixa de valor.
      </p>

      <p>
        Nessa etapa, o volume e alto e a qualidade e baixa. Uma empresa do setor
        de informatica que monitora 10 estados pode encontrar 200 a 500
        publicacoes relevantes por semana. O papel da prospeccao e alimentar o
        funil, nao qualificar. A qualificacao vem na etapa seguinte. Ferramentas
        de{' '}
        <Link href="/features">
          busca multi-fonte com classificacao setorial
        </Link>{' '}
        automatizam essa etapa e reduzem o esforco manual de captura.
      </p>

      <h3>Etapa 2: Triagem</h3>

      <p>
        A triagem e o filtro mais critico do pipeline. Aqui, cada oportunidade
        capturada na prospeccao e avaliada contra criterios objetivos de
        viabilidade. Os quatro fatores fundamentais sao: adequacao da modalidade,
        prazo disponivel para preparacao, faixa de valor compativel com o porte
        da empresa e viabilidade geografica.
      </p>

      <p>
        O objetivo da triagem e eliminar rapidamente as oportunidades
        inadeqdadas. Uma triagem eficiente descarta entre 60% e 80% dos editais
        capturados na prospeccao. Isso nao e desperdicio de prospeccao; e
        exatamente o funcionamento esperado de um funil. O artigo sobre{' '}
        <Link href="/blog/como-aumentar-taxa-vitoria-licitacoes">
          como aumentar a taxa de vitoria
        </Link>{' '}
        detalha os criterios de triagem que impactam diretamente a conversao.
      </p>

      <h3>Etapa 3: Analise</h3>

      <p>
        As oportunidades que sobrevivem a triagem entram na fase de analise
        detalhada. Aqui, a equipe le o edital completo, verifica requisitos de
        habilitacao, analisa o termo de referencia, levanta custos e avalia a
        competitividade da empresa para aquele objeto especifico.
      </p>

      <p>
        A analise e a etapa mais intensiva em tempo e conhecimento tecnico. Um
        edital complexo pode exigir 4 a 8 horas de analise detalhada. Por isso,
        a qualidade da triagem na etapa anterior e tao importante: cada edital
        que chega a analise sem merecimento consome recursos que poderiam ser
        aplicados em oportunidades melhores.
      </p>

      <h3>Etapa 4: Proposta</h3>

      <p>
        Com a analise positiva, a equipe elabora a proposta comercial e reune a
        documentacao de habilitacao. Essa etapa envolve precificacao, redacao
        tecnica, coleta de certidoes e atestados, e revisao final antes do
        envio. O prazo entre a decisao de participar e a data de abertura e
        frequentemente curto, o que exige processos internos ageis.
      </p>

      <p>
        Empresas com pipeline estruturado mantem documentacao-base atualizada
        permanentemente (certidoes, atestados, balancos), reduzindo o tempo de
        preparacao de proposta em ate 40%. Essa pratica transforma a etapa de
        proposta de um gargalo em uma operacao previsivel.
      </p>

      <h3>Etapa 5: Acompanhamento</h3>

      <p>
        Apos o envio da proposta, a oportunidade entra em acompanhamento.
        Isso inclui monitorar a sessao publica, responder a diligencias,
        acompanhar recursos e impugnacoes, e validar o resultado da
        adjudicacao. O acompanhamento nao termina na adjudicacao: a
        homologacao, a assinatura do contrato e o primeiro faturamento
        completam o ciclo.
      </p>

      <p>
        Um erro comum e abandonar o acompanhamento apos a adjudicacao. Contratos
        podem ser anulados, recursos podem reverter resultados, e atrasos na
        homologacao podem afetar o planejamento financeiro. O pipeline so
        considera a oportunidade concluida quando ha contrato assinado.
      </p>

      <h2>Metricas de cada etapa</h2>

      <p>
        Um pipeline sem metricas e apenas uma lista organizada. O valor real do
        funil esta na capacidade de medir a eficiencia de cada etapa e
        identificar gargalos. As metricas essenciais sao tres: taxa de
        conversao entre etapas, tempo medio de permanencia em cada estagio e
        volume de oportunidades ativas.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Benchmarks de conversao por etapa (referencia para empresas B2G de medio porte)</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• <strong>Prospeccao para Triagem:</strong> 100% (toda oportunidade capturada e triada)</li>
          <li>• <strong>Triagem para Analise:</strong> 20% a 40% (60%-80% descartados na triagem)</li>
          <li>• <strong>Analise para Proposta:</strong> 50% a 70% (analise detalhada elimina inadequacoes tecnicas)</li>
          <li>• <strong>Proposta para Adjudicacao:</strong> 15% a 30% (concorrencia e preco definem o resultado)</li>
          <li>• <strong>Conversao total (Prospeccao a Adjudicacao):</strong> 3% a 8% e normal; acima de 15% indica processo maduro</li>
        </ul>
      </div>

      <p>
        O tempo medio de permanencia em cada etapa tambem e revelador. Se
        oportunidades ficam presas na etapa de analise por mais de 5 dias uteis,
        ha um gargalo de capacidade tecnica. Se a taxa de conversao entre triagem
        e analise esta acima de 60%, a triagem esta frouxa e permite editais de
        baixa qualidade avancar.
      </p>

      <h2>O dashboard do setor de licitacao: o que medir</h2>

      <p>
        Alem das metricas por etapa, o gestor do setor de licitacao precisa de
        indicadores consolidados que permitam tomada de decisao estrategica.
        Esses indicadores devem ser acompanhados semanalmente e revisados
        mensalmente.
      </p>

      <h3>Indicadores de volume</h3>

      <p>
        Quantidade de oportunidades ativas no pipeline, distribuidas por etapa.
        Um pipeline saudavel tem formato de funil: muitas oportunidades nas
        etapas iniciais e poucas nas finais. Se o formato e de cilindro (mesmo
        volume em todas as etapas), a triagem nao esta funcionando. Se e de funil
        invertido (mais propostas do que prospeccoes), ha risco de secagem do
        pipeline em semanas futuras.
      </p>

      <h3>Indicadores de valor</h3>

      <p>
        Valor total estimado das oportunidades em cada etapa, ponderado pela
        probabilidade de conversao. Uma oportunidade na etapa de analise com
        valor estimado de R$ 500 mil e probabilidade de 30% representa
        R$ 150 mil em receita potencial ponderada. A soma de todas as
        oportunidades ponderadas fornece a previsao de receita do pipeline.
      </p>

      <h3>Indicadores de velocidade</h3>

      <p>
        Tempo medio do ciclo completo (da prospeccao a adjudicacao) e tempo
        medio por etapa. Reduzir o tempo de ciclo sem comprometer a qualidade
        da analise e o objetivo central. Empresas que monitoram velocidade
        conseguem identificar rapidamente quando uma oportunidade esta
        estagnada e requer acao.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Exemplo pratico: pipeline de empresa de facilities</p>
        <p className="text-sm text-ink-secondary mb-3">
          Uma empresa de facilities com faturamento anual de R$ 8 milhoes em
          contratos publicos opera com o seguinte pipeline:
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• <strong>Prospeccao:</strong> 120 editais capturados por mes (monitoramento de 12 UFs)</li>
          <li>• <strong>Triagem:</strong> 35 aprovados (taxa de aprovacao de 29%)</li>
          <li>• <strong>Analise:</strong> 20 analisados em detalhe (57% da triagem)</li>
          <li>• <strong>Proposta:</strong> 12 propostas enviadas (60% da analise)</li>
          <li>• <strong>Adjudicacao:</strong> 3 contratos fechados por mes (25% das propostas)</li>
        </ul>
        <p className="text-sm text-ink-secondary mt-3">
          Conversao total: 2,5% (3/120). Valor medio por contrato: R$ 220 mil.
          Receita mensal: R$ 660 mil. O pipeline permite prever que, mantendo o
          volume de prospeccao e as taxas de conversao, o faturamento anual
          sera de aproximadamente R$ 7,9 milhoes. Qualquer desvio nas metricas
          intermediarias acende um alerta antes que o impacto chegue ao
          faturamento.
        </p>
      </div>

      <h2>Ferramentas: planilha vs. sistema dedicado</h2>

      <p>
        A pergunta mais comum ao implementar um pipeline de licitacoes e qual
        ferramenta usar. A resposta depende do estagio da empresa e do volume
        de oportunidades gerenciadas.
      </p>

      <h3>Planilha (ate 15 oportunidades simultaneas)</h3>

      <p>
        Para equipes pequenas que gerenciam ate 15 oportunidades ativas, uma
        planilha bem estruturada funciona. O modelo deve conter: identificacao
        do edital (numero, orgao, UF), objeto resumido, valor estimado, data de
        abertura, etapa atual, responsavel, proxima acao e data limite.
        O problema da planilha aparece na escala: sem alertas automaticos, sem
        consolidacao de fontes e sem visao de pipeline, a gestao manual se
        torna fragil e dependente de disciplina individual.
      </p>

      <h3>Sistema dedicado (acima de 15 oportunidades)</h3>

      <p>
        Acima de 15 oportunidades simultaneas, um sistema dedicado oferece
        vantagens decisivas: visao kanban com drag-and-drop entre etapas,
        alertas automaticos de prazo, integracao com fontes de dados (PNCP,
        portais), metricas consolidadas e historico completo. O{' '}
        <Link href="/features">
          SmartLic
        </Link>{' '}
        integra pipeline com busca multi-fonte e classificacao por IA, permitindo
        que a oportunidade seja movida da prospeccao a triagem com dados de
        viabilidade ja preenchidos.
      </p>

      <p>
        A transicao de planilha para sistema dedicado deve acontecer quando a
        equipe percebe que esta perdendo prazos, duplicando analises ou nao
        consegue responder rapidamente a pergunta: &ldquo;quantas oportunidades
        temos ativas e qual o valor total do pipeline?&rdquo;. Se a resposta
        exige mais de 30 segundos, a planilha ja nao e suficiente.
      </p>

      <h2>Como implementar em 30 dias</h2>

      <p>
        A implementacao de um pipeline de licitacoes nao precisa ser um projeto
        de meses. Com foco e disciplina, e possivel ter um funil funcional em
        quatro semanas.
      </p>

      <h3>Semana 1: Definicao de etapas e criterios</h3>

      <p>
        Reuna a equipe e defina as etapas do pipeline (as cinco descritas
        anteriormente servem como modelo-base). Para cada etapa, estabeleca os
        criterios de avanco e os criterios de descarte. Documente em uma pagina.
        Nao complique: a primeira versao sera ajustada com o uso.
      </p>

      <h3>Semana 2: Configuracao da ferramenta</h3>

      <p>
        Escolha a ferramenta (planilha ou sistema) e configure as colunas,
        etapas e campos obrigatorios. Se usar planilha, crie um modelo-padrao
        com validacoes. Se usar um sistema como o SmartLic, configure os filtros
        de busca para alimentar automaticamente a etapa de prospeccao.
      </p>

      <h3>Semana 3: Populacao e calibracao</h3>

      <p>
        Popule o pipeline com todas as oportunidades ativas e recentes.
        Classifique cada uma na etapa correta. Execute o processo de triagem
        pela primeira vez usando os criterios definidos na semana 1. Ajuste os
        criterios conforme a realidade: se a triagem esta descartando
        oportunidades que deveriam avancar (ou aprovando as que deveriam ser
        descartadas), recalibre os parametros.
      </p>

      <h3>Semana 4: Metricas e rotina</h3>

      <p>
        Estabeleca a rotina de atualizacao do pipeline. Uma reuniao semanal de
        15 minutos para revisar o funil e suficiente. Defina quem e responsavel
        por cada etapa. Comece a medir as taxas de conversao e os tempos de
        permanencia. Apos 30 dias, voce tera dados suficientes para o primeiro
        ajuste estruturado.
      </p>

      <p>
        O artigo sobre{' '}
        <Link href="/blog/estruturar-setor-licitacao-5-milhoes">
          como estruturar um setor de licitacao
        </Link>{' '}
        complementa essa implementacao com o modelo operacional e a definicao de
        papeis da equipe. E para entender o que diferencia as empresas com
        melhores resultados, veja a analise de{' '}
        <Link href="/blog/empresas-vencem-30-porcento-pregoes">
          empresas que vencem 30% dos pregoes
        </Link>.
      </p>

      <h2>Erros comuns na gestao de pipeline</h2>

      <p>
        Mesmo com o pipeline implementado, alguns erros recorrentes comprometem
        sua eficacia. Os mais frequentes sao:
      </p>

      <p>
        <strong>Nao descartar oportunidades.</strong> O medo de perder uma
        licitacao leva equipes a manter oportunidades inadviaveis no pipeline,
        inflando artificialmente o volume e distorcendo as metricas. Um pipeline
        eficiente descarta ativamente. Se uma oportunidade nao atende aos
        criterios de triagem, ela deve sair do funil.
      </p>

      <p>
        <strong>Nao atualizar o status.</strong> Um pipeline desatualizado e
        pior do que nao ter pipeline, porque gera falsa confianca. A
        atualizacao deve ser diaria ou, no minimo, a cada movimentacao
        relevante (avancar etapa, descartar, receber resultado).
      </p>

      <p>
        <strong>Tratar todas as oportunidades igualmente.</strong> Um edital de
        R$ 2 milhoes em uma modalidade favoravel nao deve receber o mesmo nivel
        de atencao que um de R$ 80 mil em uma modalidade desconhecida. O
        pipeline deve permitir priorizacao por valor e probabilidade.
      </p>

      <p>
        <strong>Nao usar os dados historicos.</strong> Apos 3 a 6 meses de
        operacao, o pipeline gera dados suficientes para identificar padroes:
        quais tipos de edital a empresa vence mais, quais regioes sao mais
        rentaveis, quais modalidades tem melhor conversao. Ignorar esses dados e
        desperdicar o principal ativo do pipeline.
      </p>

      <h2>Do pipeline a previsibilidade de receita</h2>

      <p>
        O beneficio final de um pipeline bem gerenciado nao e organizacao: e
        previsibilidade. Quando a empresa sabe que precisa de 100 oportunidades
        na prospeccao para gerar 3 contratos no final do funil, ela pode
        planejar investimentos, contratacoes e fluxo de caixa com base em dados
        reais.
      </p>

      <p>
        Essa previsibilidade transforma o setor de licitacao de um centro de
        custo reativo em um motor de receita previsivel. E isso muda a forma
        como a diretoria enxerga o mercado publico: nao mais como uma aposta,
        mas como um canal comercial com metricas gerenciaveis.
      </p>

      {/* CTA — BEFORE FAQ */}
      <div className="not-prose mt-8 sm:mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-xl p-5 sm:p-8 text-center border border-brand-blue/20">
        <p className="text-lg sm:text-xl font-bold text-ink mb-2">
          O SmartLic tem pipeline integrado com drag-and-drop
        </p>
        <p className="text-sm sm:text-base text-ink-secondary mb-4 sm:mb-6 max-w-lg mx-auto">
          Gerencie oportunidades da prospeccao a adjudicacao com visao kanban,
          alertas de prazo e metricas automaticas. Integrado com busca
          multi-fonte e classificacao por IA.
        </p>
        <Link
          href="/signup?source=blog&article=pipeline-licitacoes-funil-comercial&utm_source=blog&utm_medium=article&utm_campaign=b2g"
          className="inline-block bg-brand-navy hover:bg-brand-blue-hover text-white font-semibold px-5 sm:px-6 py-2.5 sm:py-3 rounded-button text-sm sm:text-base transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          Comece Gratis
        </Link>
      </div>

      <h2>Perguntas Frequentes</h2>

      <h3>Qual a diferenca entre um pipeline de licitacoes e um CRM tradicional?</h3>
      <p>
        O pipeline de licitacoes segue etapas reguladas por lei (publicacao,
        habilitacao, julgamento, adjudicacao), com prazos definidos em edital e
        criterios objetivos de avaliacao. Diferentemente do CRM B2B, nao ha
        negociacao direta com o comprador, e o processo decisorio e
        transparente e auditavel. A ferramenta precisa refletir essas
        particularidades, como prazos legais e modalidades especificas.
      </p>

      <h3>Quantas licitacoes um pipeline saudavel deve conter simultaneamente?</h3>
      <p>
        Depende da capacidade operacional da equipe. Uma regra pratica e manter
        entre 3x e 5x o numero de contratos que a empresa deseja fechar por
        trimestre. Se a meta e 4 contratos no trimestre e a taxa de conversao
        historica e 20%, o pipeline deve conter pelo menos 20 oportunidades
        ativas distribuidas entre as etapas.
      </p>

      <h3>E possivel implementar um pipeline de licitacoes em planilha?</h3>
      <p>
        Sim, e muitas empresas comecam assim. A planilha funciona para equipes
        que gerenciam ate 10-15 oportunidades simultaneas. Acima disso, a
        ausencia de alertas automaticos, a falta de consolidacao de fontes de
        dados e a necessidade de atualizacao manual constante tornam a planilha
        um gargalo operacional. A transicao para um sistema dedicado deve
        ocorrer quando a equipe percebe que esta perdendo prazos ou duplicando
        esforcos.
      </p>

      <h3>Qual a taxa de conversao media em funis de licitacao publica?</h3>
      <p>
        A taxa de conversao media do mercado B2G brasileiro fica entre 8% e
        15% considerando o funil completo (prospeccao ate adjudicacao). Empresas
        com processos estruturados de triagem e analise de viabilidade reportam
        taxas entre 20% e 35%. A diferenca esta primariamente na qualidade da
        selecao inicial, nao no volume de participacoes.
      </p>

      <h3>Quanto tempo leva para implementar um pipeline de licitacoes funcional?</h3>
      <p>
        Com disciplina e ferramentas adequadas, um pipeline basico pode estar
        operacional em 30 dias. As duas primeiras semanas sao dedicadas a
        definir etapas, criterios de avanco e metricas. As duas semanas
        seguintes servem para popular o pipeline com oportunidades reais e
        calibrar os filtros de triagem. Apos 3 meses de operacao, os dados
        historicos permitem otimizacoes mais profundas.
      </p>
    </>
  );
}
