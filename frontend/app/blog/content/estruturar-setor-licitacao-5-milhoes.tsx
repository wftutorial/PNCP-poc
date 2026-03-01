import Link from 'next/link';
import BlogInlineCTA from '../components/BlogInlineCTA';

/**
 * STORY-262 B2G-07: Como Estruturar um Setor de Licitação Enxuto para Faturar R$ 5 Milhões por Ano
 * Target: 3,000–3,500 words
 */
export default function EstruturarSetorLicitacao5Milhoes() {
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
                name: 'Quantas pessoas precisa ter um setor de licitação para faturar R$ 5 milhões por ano?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Um setor de licitação enxuto e bem estruturado pode faturar R$ 5 milhões anuais com 2 a 3 profissionais dedicados: um analista de editais (triagem e compliance), um especialista em propostas (precificação e documentação) e, opcionalmente, um gestor de contratos. A chave está na automação da triagem e na especialização de cada papel, não no volume de pessoas.',
                },
              },
              {
                '@type': 'Question',
                name: 'Qual o salário médio de um analista de licitações no Brasil?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Segundo dados consolidados de plataformas de emprego como Glassdoor e Catho (2025), o salário médio de um analista de licitações no Brasil varia entre R$ 3.200 e R$ 5.800 por mês, dependendo da região e do porte da empresa. Em capitais como São Paulo e Brasília, profissionais seniores podem alcançar R$ 7.000 a R$ 9.000 mensais.',
                },
              },
              {
                '@type': 'Question',
                name: 'Quais KPIs devo acompanhar no setor de licitação?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Os KPIs essenciais de um setor de licitação são: taxa de adjudicação (meta acima de 20%), valor médio dos contratos ganhos, custo por proposta elaborada, tempo médio entre publicação do edital e envio da proposta, volume de editais triados versus propostas efetivamente enviadas, e valor total do pipeline ativo. O acompanhamento mensal desses indicadores permite ajustes rápidos na estratégia.',
                },
              },
              {
                '@type': 'Question',
                name: 'É possível terceirizar parte do setor de licitação?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Sim. A triagem de editais e a organização documental são as atividades mais terceirizáveis, podendo ser delegadas a consultorias especializadas ou ferramentas de automação. A precificação e a elaboração da proposta técnica, por envolverem conhecimento específico do negócio, devem permanecer internas. A gestão de contratos também pode ser parcialmente terceirizada, especialmente em empresas com volume alto de contratos simultâneos.',
                },
              },
              {
                '@type': 'Question',
                name: 'Qual o investimento inicial para montar um setor de licitação?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'O investimento inicial para um setor de licitação enxuto (2 pessoas + ferramentas) gira em torno de R$ 12.000 a R$ 18.000 mensais, considerando salários, encargos e ferramentas de monitoramento. Esse investimento se paga com um a dois contratos adjudicados por trimestre, dependendo do ticket médio do setor de atuação.',
                },
              },
            ],
          }),
        }}
      />

      <p className="text-base sm:text-xl leading-relaxed text-ink">
        Faturar R$ 5 milhoes por ano com licitacoes publicas nao exige uma equipe de 10 pessoas,
        um departamento inteiro ou anos de experiencia previa no mercado B2G. Exige, sim, uma
        estrutura enxuta, processos bem definidos e a capacidade de filtrar oportunidades com
        criterio. Neste artigo, apresentamos o modelo operacional que empresas de medio porte
        utilizam para alcancar esse patamar com apenas 2 a 3 profissionais dedicados — e como
        a tecnologia elimina os gargalos que, historicamente, exigiam mais pessoas.
      </p>

      <p>
        O mercado de compras publicas no Brasil movimentou R$ 1,4 trilhao entre 2023 e 2024,
        segundo dados do Painel de Compras do Governo Federal. Desse montante, mais de 60% foi
        operado por meio de pregoes eletronicos, acessiveis a empresas de qualquer porte. O
        volume de oportunidades e abundante — o que falta na maioria das empresas nao e mercado,
        mas capacidade operacional para capturar essas oportunidades de forma sistematica.
      </p>

      <h2>O modelo enxuto: 2 a 3 pessoas mais tecnologia</h2>

      <p>
        A estrutura tradicional de um setor de licitacao em empresas de medio porte geralmente
        envolve 4 a 6 pessoas: analistas juniores para monitoramento, analistas plenos para
        elaboracao de propostas, um coordenador e apoio administrativo. Esse modelo gera custos
        fixos elevados e, paradoxalmente, nao garante resultados proporcionais ao investimento.
      </p>

      <p>
        O modelo enxuto inverte essa logica. Em vez de contratar mais pessoas para processar
        mais editais, ele combina especializacao de papeis com automacao de tarefas repetitivas.
        A estrutura se resume a tres funcoes complementares, das quais a terceira e opcional
        nos primeiros anos de operacao.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Dados de referencia: custos do modelo enxuto vs. tradicional</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• Modelo tradicional (5 pessoas): R$ 35.000 a R$ 55.000/mes em salarios e encargos (fonte: Glassdoor Brasil, mediana salarial 2025 para analistas de licitacao)</li>
          <li>• Modelo enxuto (2-3 pessoas + ferramentas): R$ 12.000 a R$ 22.000/mes incluindo software de monitoramento</li>
          <li>• Ticket medio de contratos publicos por pregao eletronico: R$ 180.000 a R$ 450.000, variando por setor (fonte: Painel de Compras Governamentais, 2024)</li>
          <li>• Taxa de adjudicacao media do mercado: 8% a 12% (fonte: pesquisa Bidding Analytics, 2024)</li>
        </ul>
      </div>

      <h2>Papel 1: Analista de editais — triagem e compliance</h2>

      <p>
        O analista de editais e a primeira linha de defesa contra desperdicio de recursos. Sua
        funcao central e separar oportunidades viaveis de editais que nao merecem investimento
        de tempo. Essa triagem precisa ser rapida, sistematica e baseada em criterios objetivos
        — nao em intuicao.
      </p>

      <h3>Responsabilidades principais</h3>

      <p>
        O analista de editais e responsavel pelo monitoramento diario de publicacoes nos portais
        PNCP, ComprasGov e Portal de Compras Publicas; pela triagem inicial com base em
        alinhamento setorial, faixa de valor e regiao geografica; pela verificacao de requisitos
        de habilitacao (atestados tecnicos, certidoes, qualificacao economica); e pela
        alimentacao do pipeline de oportunidades com editais pre-qualificados. Para entender
        como organizar esse pipeline de forma eficiente,{' '}
        <Link href="/blog/pipeline-licitacoes-funil-comercial">
          veja nosso guia sobre funil comercial em licitacoes
        </Link>.
      </p>

      <h3>Perfil e faixa salarial</h3>

      <p>
        O perfil ideal combina formacao em Administracao, Direito ou areas correlatas com
        experiencia pratica em leitura de editais. Segundo dados da Catho e Glassdoor
        atualizados em 2025, a faixa salarial para analistas de licitacao no Brasil e:
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Faixas salariais — Analista de Licitacoes (2025)</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• Junior (0-2 anos): R$ 2.800 a R$ 4.200/mes (fonte: Catho, mediana nacional 2025)</li>
          <li>• Pleno (2-5 anos): R$ 4.500 a R$ 6.500/mes (fonte: Glassdoor, mediana nacional 2025)</li>
          <li>• Senior (5+ anos): R$ 6.500 a R$ 9.000/mes, podendo chegar a R$ 11.000 em Brasilia e Sao Paulo</li>
        </ul>
      </div>

      <p>
        No modelo enxuto, um analista pleno e suficiente. A automacao da triagem inicial
        permite que essa pessoa dedique tempo a analise qualitativa dos editais pre-filtrados,
        em vez de gastar horas lendo publicacoes irrelevantes.
      </p>

      <h2>Papel 2: Especialista em propostas — precificacao e documentacao</h2>

      <p>
        Se o analista define quais licitacoes merecem atencao, o especialista em propostas
        define como competir. Essa funcao exige conhecimento tecnico profundo do setor de
        atuacao da empresa, dominio de precificacao competitiva e experiencia com a elaboracao
        de documentos que atendam rigorosamente aos requisitos do edital.
      </p>

      <h3>Responsabilidades principais</h3>

      <p>
        O especialista em propostas e responsavel pela composicao de precos com margem de
        seguranca e competitividade; pela elaboracao da proposta tecnica, quando exigida; pela
        montagem e conferencia do envelope de habilitacao; pelo acompanhamento da sessao
        publica (pregao eletronico) e interposicao de recursos quando pertinente; e pela
        analise pos-resultado para retroalimentar os criterios de triagem.
      </p>

      <h3>Perfil e faixa salarial</h3>

      <p>
        O especialista em propostas geralmente tem formacao na area tecnica do setor da empresa
        (engenharia para obras, TI para software, nutricao para alimentacao) combinada com
        experiencia em licitacoes. A faixa salarial e ligeiramente superior a do analista,
        refletindo a especializacao tecnica: R$ 5.500 a R$ 8.500 para perfil pleno, podendo
        ultrapassar R$ 10.000 para seniors em setores de alta complexidade como engenharia e
        saude (fonte: Glassdoor Brasil, 2025).
      </p>

      <h2>Papel 3 (opcional): Gestor de contratos</h2>

      <p>
        Nos primeiros anos de operacao, a gestao de contratos pode ser absorvida pelo
        especialista em propostas ou pelo gestor geral da empresa. Conforme o volume de
        contratos ativos cresce — tipicamente acima de 5 contratos simultaneos —, a dedicacao
        de uma pessoa a essa funcao torna-se necessaria.
      </p>

      <h3>Quando contratar</h3>

      <p>
        O indicador mais confiavel e o numero de contratos ativos simultaneos. Ate 4 contratos,
        a gestao pode ser absorvida pela equipe existente. Entre 5 e 8 contratos, a dedicacao
        parcial (meio periodo) ja se justifica. Acima de 8 contratos, a dedicacao integral
        evita atrasos em entregas, multas contratuais e perda de reputacao junto aos orgaos
        contratantes.
      </p>

      <p>
        O gestor de contratos acompanha prazos de entrega, processos de medicao, emissao de
        notas fiscais, e antecipa renovacoes ou aditivos. A faixa salarial e similar a do
        analista pleno: R$ 4.500 a R$ 7.500 mensais.
      </p>

      <h2>A cadeia operacional: prospecao, triagem, analise, proposta e acompanhamento</h2>

      <p>
        O setor de licitacao enxuto opera em cinco etapas sequenciais, cada uma com
        responsavel e criterios claros de transicao. A eficiencia do setor depende da
        fluidez dessa cadeia — um gargalo em qualquer etapa compromete o resultado final.
      </p>

      <h3>Etapa 1: Prospecao</h3>

      <p>
        A prospecao consiste no monitoramento diario de novas publicacoes nos portais de
        compras publicas. Em um modelo manual, essa etapa consome entre 1 e 3 horas diarias.
        Com ferramentas automatizadas de monitoramento, o tempo cai para 15 a 30 minutos
        de revisao de alertas ja filtrados por setor e regiao.
      </p>

      <h3>Etapa 2: Triagem</h3>

      <p>
        Dos editais identificados na prospecao, a triagem seleciona aqueles que atendem aos
        criterios minimos da empresa: alinhamento setorial, faixa de valor compativel,
        regiao geografica viavel, e ausencia de requisitos de habilitacao inalcancaveis.
        A taxa de aprovacao tipica nessa etapa e de 15% a 25% — ou seja, a cada 100 editais
        monitorados, entre 15 e 25 passam para analise detalhada.
      </p>

      <h3>Etapa 3: Analise detalhada</h3>

      <p>
        Os editais aprovados na triagem passam por analise completa: leitura integral do
        edital e anexos, verificacao de requisitos de habilitacao, levantamento de historico
        do orgao contratante e avaliacao de competitividade. Essa etapa e conduzida pelo
        analista de editais com apoio do especialista em propostas.
      </p>

      <BlogInlineCTA slug="estruturar-setor-licitacao-5-milhoes" campaign="b2g" />

      <h3>Etapa 4: Elaboracao da proposta</h3>

      <p>
        Somente os editais aprovados na analise detalhada recebem investimento de elaboracao
        de proposta. O especialista em propostas conduz a precificacao, a redacao tecnica e
        a montagem documental. O tempo medio de elaboracao varia de 8 a 40 horas, dependendo
        da complexidade do objeto.
      </p>

      <h3>Etapa 5: Acompanhamento</h3>

      <p>
        Apos o envio da proposta, o acompanhamento inclui participacao na sessao publica,
        resposta a diligencias, interposicao ou contrarrazao de recursos, e assinatura do
        contrato em caso de adjudicacao.
      </p>

      <h2>Ferramentas essenciais: da planilha ao sistema</h2>

      <p>
        O estagio de maturidade das ferramentas utilizadas pelo setor de licitacao tem
        impacto direto na produtividade. A maioria das empresas inicia com planilhas e
        migra para sistemas especializados conforme o volume de operacao justifica o
        investimento.
      </p>

      <h3>Estagio 1: Planilha e busca manual</h3>

      <p>
        No estagio inicial, a equipe busca editais diretamente nos portais (PNCP, ComprasNet,
        portais estaduais) e registra oportunidades em planilhas. Esse modelo funciona para
        ate 10 a 15 editais acompanhados simultaneamente, mas colapsa rapidamente com o
        aumento de volume.
      </p>

      <h3>Estagio 2: Alertas e monitoramento automatizado</h3>

      <p>
        Ferramentas de monitoramento que agregam publicacoes de multiplos portais e enviam
        alertas filtrados por setor eliminam a etapa de busca manual. O ganho tipico e de
        60% a 70% do tempo de prospecao.
      </p>

      <h3>Estagio 3: Inteligencia e classificacao por IA</h3>

      <p>
        No estagio mais avancado, ferramentas como o{' '}
        <Link href="/features">SmartLic</Link> vao alem do monitoramento: classificam
        editais por relevancia setorial usando inteligencia artificial, avaliam viabilidade
        com base em quatro criterios objetivos (modalidade, prazo, valor e geografia) e
        organizam o pipeline de oportunidades em formato visual. Isso permite que a equipe
        enxuta se concentre exclusivamente nas etapas que exigem julgamento humano —
        analise detalhada e elaboracao de propostas.
      </p>

      <h2>KPIs do setor de licitacao</h2>

      <p>
        Um setor de licitacao sem metricas opera no escuro. Os indicadores a seguir permitem
        que a gestao identifique gargalos, ajuste a estrategia e projete resultados com
        maior previsibilidade. O acompanhamento deve ser mensal, com revisao trimestral
        de metas.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">KPIs essenciais do setor de licitacao</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• <strong>Taxa de adjudicacao:</strong> percentual de propostas enviadas que resultam em contrato. Meta minima: 20%. Empresas de alto desempenho operam entre 25% e 35% (fonte: Bidding Analytics, 2024)</li>
          <li>• <strong>Volume de pipeline:</strong> soma do valor estimado de todos os editais em acompanhamento ativo. Deve ser de 3x a 5x a meta de faturamento anual</li>
          <li>• <strong>Custo por proposta:</strong> custo total do setor dividido pelo numero de propostas enviadas no periodo. Referencia de mercado: R$ 2.500 a R$ 8.000 por proposta</li>
          <li>• <strong>Tempo medio de resposta:</strong> dias entre publicacao do edital e envio da proposta. Quanto menor, maior a chance de identificar pendencias a tempo</li>
          <li>• <strong>Taxa de triagem:</strong> percentual de editais monitorados que passam para analise. Referencia: 15% a 25%</li>
          <li>• <strong>Valor medio por contrato:</strong> acompanhamento por setor e modalidade para calibrar as faixas de valor buscadas</li>
        </ul>
      </div>

      <p>
        O acompanhamento desses indicadores permite identificar rapidamente se o setor esta
        investindo tempo nos editais certos. Uma taxa de adjudicacao abaixo de 15%
        consistentemente indica problemas na triagem ou na precificacao.{' '}
        <Link href="/blog/como-aumentar-taxa-vitoria-licitacoes">
          Veja estrategias especificas para aumentar a taxa de vitoria
        </Link>.
      </p>

      <h2>Meta de R$ 5 milhoes: o funil reverso</h2>

      <p>
        Para atingir R$ 5 milhoes em contratos publicos por ano, e preciso construir o
        raciocinio de tras para frente — o funil reverso. Esse exercicio revela quantos
        editais o setor precisa monitorar, triar, analisar e licitar para alcancar a meta.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Exemplo pratico: funil reverso para R$ 5 milhoes/ano</p>
        <div className="text-sm text-ink-secondary space-y-3">
          <p><strong>Premissas (setor de materiais eletricos, regiao Sudeste):</strong></p>
          <ul className="space-y-1 ml-4">
            <li>• Ticket medio por contrato: R$ 250.000</li>
            <li>• Taxa de adjudicacao estimada: 22%</li>
            <li>• Taxa de aprovacao na triagem: 20%</li>
            <li>• Taxa de conversao analise detalhada para proposta: 60%</li>
          </ul>
          <p><strong>Calculo reverso:</strong></p>
          <ul className="space-y-1 ml-4">
            <li>• Meta anual: R$ 5.000.000</li>
            <li>• Contratos necessarios: R$ 5.000.000 / R$ 250.000 = <strong>20 contratos</strong></li>
            <li>• Propostas necessarias: 20 / 0,22 = <strong>91 propostas/ano</strong> (aproximadamente 8 por mes)</li>
            <li>• Editais em analise detalhada: 91 / 0,60 = <strong>152 editais analisados/ano</strong></li>
            <li>• Editais triados: 152 / 0,20 = <strong>760 editais triados/ano</strong> (63 por mes)</li>
          </ul>
          <p><strong>Resultado:</strong> o setor precisa monitorar e triar aproximadamente 63 editais por mes para sustentar um pipeline que gere 20 contratos de R$ 250 mil ao longo do ano. Com triagem automatizada, esse volume e perfeitamente gerenciavel por 2 pessoas.</p>
        </div>
      </div>

      <p>
        Esse calculo evidencia por que a triagem automatizada e tao critica. Triar 63 editais
        por mes manualmente — lendo cada um para verificar alinhamento setorial, requisitos
        de habilitacao e viabilidade — consome dezenas de horas. Com classificacao automatizada,
        o analista recebe apenas os 12 a 15 editais que ja passaram pelo filtro de relevancia
        e viabilidade, concentrando o esforco humano na analise que realmente importa.
      </p>

      <p>
        Cabe observar que o exemplo acima assume um ticket medio de R$ 250.000, tipico de
        setores como materiais eletricos, mobiliario e informatica. Para setores com tickets
        maiores — como engenharia civil (R$ 500.000 a R$ 2.000.000) — o numero de contratos
        necessarios cai proporcionalmente, mas a complexidade de cada proposta aumenta. O
        modelo enxuto se aplica em ambos os cenarios; o que muda e a distribuicao de tempo
        entre triagem e elaboracao.
      </p>

      <h2>Cronograma de implantacao</h2>

      <p>
        Montar um setor de licitacao nao e um projeto de meses. Uma empresa que ja tem
        conhecimento do seu setor e experiencia comercial pode ter o departamento operacional
        em 4 a 6 semanas, seguindo um cronograma realista.
      </p>

      <h3>Semana 1 a 2: Definicao de escopo e contratacao</h3>

      <p>
        Definir os setores e regioes de atuacao prioritarios, os criterios minimos de triagem
        (faixa de valor, modalidades, requisitos de habilitacao) e iniciar o processo de
        selecao do analista de editais. Paralelamente, configurar as ferramentas de
        monitoramento.
      </p>

      <h3>Semana 3 a 4: Operacao assistida</h3>

      <p>
        O analista inicia a operacao com supervisao proxima. Os primeiros editais triados
        servem como calibragem dos criterios. E comum que as primeiras semanas revelem
        ajustes necessarios nos filtros — setores muito amplos, faixas de valor inadequadas,
        ou regioes com poucos editais relevantes.
      </p>

      <h3>Semana 5 a 6: Primeira proposta e ajustes</h3>

      <p>
        O envio da primeira proposta e o marco real de inicio de operacao. A partir desse
        ponto, o ciclo de feedback entre triagem, analise e resultado comeca a gerar dados
        para refinamento continuo dos criterios.
      </p>

      <h2>Erros mais comuns na estruturacao</h2>

      <p>
        A experiencia de empresas que passaram por esse processo revela padroes recorrentes
        de erro que devem ser evitados desde o inicio.
      </p>

      <p>
        O primeiro erro e tentar cobrir muitos setores simultaneamente. Empresas que atuam
        em tres ou quatro setores devem priorizar um ou dois no inicio e expandir conforme
        o setor ganha maturidade operacional. O segundo erro e nao definir criterios de
        triagem antes de comecar — o que resulta em analisar editais que nunca deveriam
        ter chegado a mesa do analista. O terceiro erro e negligenciar a retroalimentacao:
        sem analisar por que perdeu ou ganhou cada licitacao, o setor nao evolui.
      </p>

      <p>
        Empresas que mantem uma disciplina de analise pos-resultado — registrando o motivo
        de cada vitoria e derrota — apresentam evolucao consistente na taxa de adjudicacao
        ao longo de 6 a 12 meses. Para entender quais fatores diferenciam empresas com
        alta taxa de vitoria,{' '}
        <Link href="/blog/empresas-vencem-30-porcento-pregoes">
          leia nossa analise sobre empresas que vencem 30% dos pregoes
        </Link>. Vale tambem conhecer{' '}
        <Link href="/blog/escalar-consultoria-sem-depender-horas-tecnicas">
          como consultorias escalam sem depender de horas tecnicas
        </Link>{' '}
        — o modelo enxuto descrito aqui tem paralelos diretos com a estrutura
        que assessorias de licitacao adotam para crescer com eficiencia.
      </p>

      <h2>O papel da tecnologia na viabilidade do modelo enxuto</h2>

      <p>
        O modelo de 2 a 3 pessoas so e viavel porque a tecnologia absorve as tarefas de
        maior volume e menor valor agregado. Sem automacao, o mesmo resultado exigiria 4 a
        6 pessoas — o que inviabiliza o retorno sobre investimento para empresas de medio
        porte.
      </p>

      <p>
        As tres areas de maior impacto da automacao no setor de licitacao sao: a prospecao
        (monitoramento automatizado de multiplos portais), a triagem (classificacao por
        relevancia e viabilidade) e o controle de pipeline (visao consolidada de todas as
        oportunidades em andamento com prazos e status). O{' '}
        <Link href="/planos">SmartLic</Link> cobre essas tres areas em uma unica plataforma,
        permitindo que a equipe enxuta opere com a mesma eficiencia de departamentos maiores.
      </p>

      {/* CTA — BEFORE FAQ */}
      <div className="not-prose mt-8 sm:mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-xl p-5 sm:p-8 text-center border border-brand-blue/20">
        <p className="text-lg sm:text-xl font-bold text-ink mb-2">
          Automatize a triagem e libere sua equipe para o que importa
        </p>
        <p className="text-sm sm:text-base text-ink-secondary mb-4 sm:mb-6 max-w-lg mx-auto">
          O SmartLic monitora PNCP, ComprasGov e Portal de Compras Publicas, classifica editais por
          setor e viabilidade, e organiza seu pipeline de oportunidades — para que sua equipe
          enxuta foque em elaborar propostas vencedoras.
        </p>
        <Link
          href="/signup?source=blog&article=estruturar-setor-licitacao-5-milhoes&utm_source=blog&utm_medium=cta&utm_content=estruturar-setor-licitacao-5-milhoes&utm_campaign=b2g"
          className="inline-block bg-brand-navy hover:bg-brand-blue-hover text-white font-semibold px-5 sm:px-6 py-2.5 sm:py-3 rounded-button text-sm sm:text-base transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          Teste Grátis por 14 Dias
        </Link>
        <p className="text-xs text-ink-secondary mt-3">
          Sem cartão de crédito.{' '}
          <Link href="/planos" className="underline hover:text-ink">
            Ver planos
          </Link>
        </p>
      </div>

      <h2>Perguntas Frequentes</h2>

      <h3>Quantas pessoas precisa ter um setor de licitacao para faturar R$ 5 milhoes por ano?</h3>
      <p>
        Um setor de licitacao enxuto e bem estruturado pode faturar R$ 5 milhoes anuais com 2 a 3
        profissionais dedicados: um analista de editais (triagem e compliance), um especialista em
        propostas (precificacao e documentacao) e, opcionalmente, um gestor de contratos. A chave
        esta na automacao da triagem e na especializacao de cada papel, nao no volume de pessoas.
      </p>

      <h3>Qual o salario medio de um analista de licitacoes no Brasil?</h3>
      <p>
        Segundo dados consolidados de plataformas de emprego como Glassdoor e Catho (2025), o
        salario medio de um analista de licitacoes no Brasil varia entre R$ 3.200 e R$ 5.800 por
        mes, dependendo da regiao e do porte da empresa. Em capitais como Sao Paulo e Brasilia,
        profissionais seniores podem alcancar R$ 7.000 a R$ 9.000 mensais.
      </p>

      <h3>Quais KPIs devo acompanhar no setor de licitacao?</h3>
      <p>
        Os KPIs essenciais sao: taxa de adjudicacao (meta acima de 20%), valor medio dos contratos
        ganhos, custo por proposta elaborada, tempo medio entre publicacao e envio da proposta,
        volume de editais triados versus propostas enviadas, e valor total do pipeline ativo. O
        acompanhamento mensal desses indicadores permite ajustes rapidos na estrategia.
      </p>

      <h3>E possivel terceirizar parte do setor de licitacao?</h3>
      <p>
        Sim. A triagem de editais e a organizacao documental sao as atividades mais terceirizaveis,
        podendo ser delegadas a consultorias especializadas ou ferramentas de automacao. A
        precificacao e a elaboracao da proposta tecnica, por envolverem conhecimento especifico do
        negocio, devem permanecer internas.
      </p>

      <h3>Qual o investimento inicial para montar um setor de licitacao?</h3>
      <p>
        O investimento inicial para um setor de licitacao enxuto (2 pessoas + ferramentas) gira em
        torno de R$ 12.000 a R$ 18.000 mensais, considerando salarios, encargos e ferramentas de
        monitoramento. Esse investimento se paga com um a dois contratos adjudicados por trimestre,
        dependendo do ticket medio do setor de atuacao.
      </p>

      {/* TODO: Link para página programática de setor — MKT-003 */}
      {/* TODO: Link para página programática de cidade — MKT-005 */}
    </>
  );
}
