import Link from 'next/link';

/**
 * STORY-262 B2G-10: Licitacao por Volume ou por Inteligencia
 * Target: 2,500-3,000 words | Cluster: inteligencia em licitacoes
 */
export default function LicitacaoVolumeOuInteligencia() {
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
                name: 'Qual a diferenca entre estrategia de volume e estrategia de inteligencia em licitacoes?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'A estrategia de volume prioriza a quantidade de participacoes, apostando na lei dos grandes numeros para converter contratos. A estrategia de inteligencia prioriza a selecao criteriosa de editais com base em dados de viabilidade, historico do orgao, concorrencia estimada e aderencia tecnica. Empresas de volume tipicamente participam de 30 a 80 pregoes por mes com taxas de vitoria entre 5% e 10%. Empresas de inteligencia participam de 8 a 20 pregoes por mes com taxas entre 20% e 35%.',
                },
              },
              {
                '@type': 'Question',
                name: 'A estrategia de volume funciona para empresas pequenas?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Raramente. Empresas com equipes de 1 a 3 pessoas no setor de licitacoes nao conseguem manter a qualidade das propostas em alto volume de participacoes. O custo operacional por proposta (R$ 800 a R$ 2.500) consome margem de forma desproporcional quando a taxa de vitoria e baixa. Para empresas pequenas, a estrategia de inteligencia seletiva oferece melhor retorno sobre o investimento.',
                },
              },
              {
                '@type': 'Question',
                name: 'E possivel combinar volume e inteligencia?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Sim. O modelo hibrido aplica volume para oportunidades de baixo risco e baixo custo de proposta (como atas de registro de precos e pregoes eletronicos padronizados) e inteligencia seletiva para oportunidades de alto valor ou alta complexidade. Esse modelo exige triagem automatizada para funcionar em escala.',
                },
              },
              {
                '@type': 'Question',
                name: 'Quanto custa em media elaborar uma proposta de licitacao?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'O custo medio varia entre R$ 800 e R$ 2.500 por proposta, considerando horas de analista, documentacao, certidoes, garantias e custos administrativos. Para licitacoes de engenharia ou servicos complexos, esse custo pode ultrapassar R$ 5.000 por proposta. Esse custo operacional e o principal fator na decisao entre volume e inteligencia.',
                },
              },
              {
                '@type': 'Question',
                name: 'Como migrar de uma estrategia de volume para inteligencia sem perder receita?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'A migracao deve ser gradual, em tres fases: primeiro, classificar o portfolio atual de licitacoes por taxa de vitoria historica e margem liquida; segundo, eliminar progressivamente as categorias com pior retorno (comecando pelos 20% com menor taxa de vitoria); terceiro, reinvestir o tempo liberado em analise aprofundada das oportunidades remanescentes. O ciclo completo leva de 3 a 6 meses.',
                },
              },
            ],
          }),
        }}
      />

      <p className="text-base sm:text-xl leading-relaxed text-ink">
        Existem duas escolas de pensamento sobre como competir em licitacoes
        publicas. A primeira defende a participacao massiva: quanto mais pregoes
        a empresa disputa, mais contratos fecha. A segunda argumenta que a
        selecao criteriosa de editais gera mais lucro com menos esforco. As
        duas posicoes tem merito, mas os dados do mercado indicam que a resposta
        nao e tao simples quanto escolher um lado.
      </p>

      <p>
        Neste artigo, analisamos quantitativamente as duas estrategias,
        apresentamos cenarios reais para empresas de diferentes portes e
        propomos um modelo hibrido que captura o melhor de cada abordagem. Se
        voce ja se perguntou se compensa{' '}
        <Link href="/blog/disputar-todas-licitacoes-matematica-real">
          disputar todas as licitacoes do seu segmento
        </Link>, a analise a seguir oferece uma resposta baseada em numeros.
      </p>

      <h2>As duas escolas: volume versus selecao</h2>

      <p>
        A estrategia de volume parte de uma premissa estatistica: se a taxa
        media de vitoria em pregoes eletronicos gira em torno de 8% a 12%, e
        preciso participar de muitas licitacoes para fechar contratos
        suficientes. Com 50 participacoes por mes e uma taxa de 10%, a empresa
        fecha 5 contratos. A logica e linear e intuitiva.
      </p>

      <p>
        A estrategia de inteligencia inverte a equacao. Em vez de aumentar o
        numerador (numero de participacoes), ela melhora o denominador (taxa de
        conversao). Uma empresa que participa de 15 pregoes por mes com taxa de
        30% tambem fecha entre 4 e 5 contratos, mas com um terco do esforco
        operacional.
      </p>

      <p>
        A diferenca fundamental nao esta no resultado bruto (numero de
        contratos), mas no custo para chegar la e na margem liquida que cada
        contrato entrega. E e nessa diferenca que o debate se resolve.
      </p>

      <h2>Perfil da estrategia de volume</h2>

      <h3>Como funciona na pratica</h3>

      <p>
        Empresas que adotam a estrategia de volume tipicamente operam com
        equipes maiores no setor de licitacoes (4 a 8 analistas), utilizam
        ferramentas de busca basicas para captar o maior numero possivel de
        editais e padronizam ao maximo o processo de elaboracao de propostas.
        A premissa e que o custo marginal de cada proposta adicional e baixo
        quando o processo esta industrializado.
      </p>

      <h3>Quando funciona</h3>

      <p>
        A estrategia de volume e viavel em setores com alta padronizacao de
        editais, como materiais de escritorio, informatica basica e alimentos.
        Nesses mercados, o objeto e previsivel, os requisitos de habilitacao
        sao recorrentes e a proposta comercial pode ser montada em poucas
        horas. Empresas com grande capacidade de atendimento geografico
        (cobertura nacional) tambem se beneficiam do volume, pois cada UF
        adicional multiplica oportunidades sem aumentar proporcionalmente o
        custo fixo.
      </p>

      <h3>Os riscos que ninguem menciona</h3>

      <p>
        O problema da estrategia de volume nao aparece no mes seguinte, mas no
        acumulado do ano. Participar de muitas licitacoes sem triagem rigorosa
        gera tres efeitos colaterais. Primeiro, a equipe e sobrecarregada e
        comeca a cometer erros em propostas criticas. Segundo, a margem media
        por contrato tende a cair, porque a empresa aceita oportunidades com
        margens apertadas para manter o volume. Terceiro, o custo de
        participacao em pregoes perdidos se acumula de forma invisivel.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Dados de referencia: custo operacional por proposta</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            &bull; O custo medio de elaboracao de uma proposta para pregao eletronico varia entre R$ 800 e R$ 2.500,
            incluindo horas de analista, documentacao, certidoes e custos administrativos (Fonte: SEBRAE,{' '}
            <em>Cartilha de Licitacoes para Micro e Pequenas Empresas</em>, 2023).
          </li>
          <li>
            &bull; Segundo levantamento do Portal de Compras Governamentais, a taxa media de desclassificacao em
            pregoes eletronicos e de 38%, sendo que 62% das desclassificacoes ocorrem por falhas documentais,
            nao por preco (ComprasGov, Painel de Monitoramento, 2024).
          </li>
          <li>
            &bull; De acordo com o Tribunal de Contas da Uniao (TCU), o valor medio de contratos adjudicados via
            pregao eletronico foi de R$ 287 mil em 2024, com mediana de R$ 78 mil, indicando alta concentracao
            em contratos de valor intermediario (TCU, Relatorio de Fiscalizacao de Aquisicoes, 2024).
          </li>
        </ul>
      </div>

      <h2>Perfil da estrategia de inteligencia</h2>

      <h3>Como funciona na pratica</h3>

      <p>
        A estrategia de inteligencia comeca antes da busca de editais: pela
        definicao rigorosa do perfil de oportunidade ideal. A empresa mapeia
        suas vantagens competitivas reais (preco, capacidade tecnica,
        localizacao, atestados acumulados), define faixas de valor onde sua
        margem e sustentavel e identifica orgaos com historico de pagamento
        regular. So entao inicia a busca, filtrando por criterios objetivos
        antes de investir tempo na analise do edital.
      </p>

      <p>
        Empresas que adotam essa abordagem frequentemente utilizam ferramentas
        de{' '}
        <Link href="/features">
          analise de viabilidade automatizada
        </Link>{' '}
        para puntuar cada oportunidade antes de decidir participar. O objetivo
        nao e encontrar todas as licitacoes disponiveis, mas apenas aquelas
        onde a probabilidade de vitoria e a margem esperada justificam o
        investimento.
      </p>

      <h3>Quando funciona</h3>

      <p>
        A estrategia de inteligencia e mais eficaz em setores de alta
        complexidade tecnica, como engenharia, software, saude e servicos
        especializados. Nesses mercados, cada proposta exige analise
        aprofundada do edital, dimensionamento tecnico e precificacao sob
        medida. O custo por proposta e alto (R$ 2.000 a R$ 5.000 ou mais),
        tornando cada participacao um investimento significativo que precisa
        ser direcionado com criterio.
      </p>

      <h3>As limitacoes reais</h3>

      <p>
        A estrategia de inteligencia tem dois riscos principais. Primeiro,
        a seletividade excessiva pode levar a empresa a recusar oportunidades
        boas por excesso de cautela, resultando em um pipeline muito enxuto
        para sustentar o faturamento desejado. Segundo, a dependencia de dados
        historicos pode criar vieses: a empresa so busca o que ja conhece e
        ignora oportunidades em nichos adjacentes. A calibracao dos filtros de
        triagem e crucial e deve ser revista trimestralmente.
      </p>

      <h2>Comparacao quantitativa: tres cenarios reais</h2>

      <p>
        Para tornar a analise concreta, simulamos tres cenarios com parametros
        realistas para empresas de diferentes portes. Todos os cenarios
        consideram um ciclo anual, com custo operacional medio por proposta
        de R$ 1.500 e margem liquida media de 12% sobre o valor do contrato.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Exemplo pratico: simulacao comparativa anual</p>
        <div className="space-y-4 text-sm text-ink-secondary">
          <div>
            <p className="font-medium text-ink mb-1">Cenario 1 — Pequena empresa (2 analistas)</p>
            <p>
              <strong>Volume:</strong> 25 participacoes/mes = 300/ano. Taxa de vitoria: 8%. Contratos: 24.
              Valor medio: R$ 80 mil. Faturamento bruto: R$ 1,92 milhao. Custo de propostas: R$ 450 mil.
              Margem liquida (12%): R$ 230 mil. <strong>Lucro apos custo de propostas: -R$ 220 mil.</strong>
            </p>
            <p className="mt-1">
              <strong>Inteligencia:</strong> 8 participacoes/mes = 96/ano. Taxa de vitoria: 25%. Contratos: 24.
              Valor medio: R$ 95 mil (editais mais qualificados). Faturamento bruto: R$ 2,28 milhoes. Custo de propostas: R$ 144 mil.
              Margem liquida (12%): R$ 274 mil. <strong>Lucro apos custo de propostas: +R$ 130 mil.</strong>
            </p>
          </div>
          <div>
            <p className="font-medium text-ink mb-1">Cenario 2 — Media empresa (4 analistas)</p>
            <p>
              <strong>Volume:</strong> 50 participacoes/mes = 600/ano. Taxa: 10%. Contratos: 60.
              Valor medio: R$ 120 mil. Faturamento: R$ 7,2 milhoes. Custo propostas: R$ 900 mil.
              Margem (12%): R$ 864 mil. <strong>Saldo: -R$ 36 mil.</strong>
            </p>
            <p className="mt-1">
              <strong>Inteligencia:</strong> 18 participacoes/mes = 216/ano. Taxa: 28%. Contratos: 60.
              Valor medio: R$ 150 mil. Faturamento: R$ 9 milhoes. Custo propostas: R$ 324 mil.
              Margem (12%): R$ 1,08 milhao. <strong>Saldo: +R$ 756 mil.</strong>
            </p>
          </div>
          <div>
            <p className="font-medium text-ink mb-1">Cenario 3 — Grande empresa (8 analistas)</p>
            <p>
              <strong>Volume:</strong> 80 participacoes/mes = 960/ano. Taxa: 12%. Contratos: 115.
              Valor medio: R$ 200 mil. Faturamento: R$ 23 milhoes. Custo propostas: R$ 1,44 milhao.
              Margem (12%): R$ 2,76 milhoes. <strong>Saldo: +R$ 1,32 milhao.</strong>
            </p>
            <p className="mt-1">
              <strong>Hibrido:</strong> 40 participacoes/mes volume + 15 inteligencia = 660/ano. Taxa combinada: 18%.
              Contratos: 119. Valor medio: R$ 220 mil. Faturamento: R$ 26,2 milhoes. Custo propostas: R$ 990 mil.
              Margem (12%): R$ 3,14 milhoes. <strong>Saldo: +R$ 2,15 milhoes.</strong>
            </p>
          </div>
          <p className="text-xs mt-3 text-ink-secondary/70">
            Nota: Simulacao com parametros ilustrativos baseados em medias de mercado. Resultados reais
            variam conforme setor, regiao e competitividade.
          </p>
        </div>
      </div>

      <p>
        Os numeros revelam um padrao consistente: a estrategia de volume pura
        so se sustenta em empresas grandes, com equipes robustas e margens de
        escala. Para pequenas e medias empresas, o custo acumulado de propostas
        perdidas corroi a margem. A estrategia de inteligencia entrega mais
        lucro liquido em todos os cenarios, e o modelo hibrido potencializa os
        resultados para empresas que ja possuem escala.
      </p>

      <h2>O modelo hibrido: volume base com inteligencia seletiva</h2>

      <p>
        A abordagem mais eficaz para empresas B2G maduras nao e escolher entre
        volume e inteligencia, mas combinar ambas em camadas. O modelo hibrido
        funciona assim:
      </p>

      <h3>Camada 1: volume automatizado para oportunidades padrao</h3>

      <p>
        Pregoes eletronicos de menor preco com objetos padronizados (materiais,
        equipamentos catalogados, servicos recorrentes) entram no fluxo de
        volume. A proposta e montada com templates pre-aprovados, documentacao
        padronizada e precificacao baseada em tabela. O tempo de elaboracao
        nao ultrapassa 2 horas por proposta. A triagem e feita por ferramenta
        automatizada, que filtra por setor, UF, faixa de valor e modalidade.
      </p>

      <h3>Camada 2: inteligencia seletiva para oportunidades de alto valor</h3>

      <p>
        Concorrencias, tomadas de preco, pregoes com objeto complexo e
        licitacoes acima de determinado valor (tipicamente R$ 500 mil ou mais)
        recebem analise aprofundada. Cada oportunidade passa por avaliacao de
        viabilidade com multiplos criterios:{' '}
        <Link href="/blog/como-aumentar-taxa-vitoria-licitacoes">
          aderencia tecnica, competitividade de preco, historico do orgao e
          prazo de execucao
        </Link>. Apenas as que atingem um score minimo de viabilidade avancam
        para elaboracao de proposta.
      </p>

      <h3>Camada 3: monitoramento de nicho para oportunidades estrategicas</h3>

      <p>
        Licitacoes em nichos especificos onde a empresa tem vantagem
        competitiva excepcional (por exemplo, um atestado raro ou uma
        localizacao privilegiada) recebem tratamento prioritario
        independentemente do valor. Essas oportunidades representam menos de
        10% do pipeline, mas frequentemente geram as maiores margens.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Benchmark setorial: margem por tipo de contrato</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            &bull; Contratos de materiais padronizados (papelaria, informatica basica): margem liquida media de 6%
            a 10%. Alta concorrencia, baixa diferenciacao (Fonte: IBGE, Pesquisa Industrial Anual, ajustada para
            contratos publicos, 2023).
          </li>
          <li>
            &bull; Contratos de servicos especializados (engenharia, TI, consultoria): margem liquida media de 14%
            a 22%. Menor concorrencia, maior barreira de entrada por exigencias tecnicas (Fonte: Sinduscon/FGV,
            Indice de Custos da Construcao, 2024; dados de mercado setorial).
          </li>
          <li>
            &bull; Atas de registro de precos: margem liquida media de 4% a 8%, compensada pelo volume de
            empenhos ao longo da vigencia de 12 meses (Fonte: Comprasnet, Painel de Atas de Registro de Precos,
            dados consolidados 2023-2024).
          </li>
        </ul>
      </div>

      <h2>Como migrar de volume para inteligencia</h2>

      <p>
        A transicao nao deve ser abrupta. Empresas que cortam o volume de
        participacoes de uma vez correm o risco de criar um vazio no pipeline
        de contratos. A migracao deve ser gradual e orientada por dados, em
        tres fases:
      </p>

      <h3>Fase 1: diagnostico (4 semanas)</h3>

      <p>
        Levante os dados dos ultimos 12 meses: numero de participacoes, taxa
        de vitoria por modalidade, valor medio dos contratos adjudicados,
        custo estimado por proposta e margem liquida por contrato. Classifique
        cada participacao em quatro quadrantes: alta taxa/alta margem
        (manter), alta taxa/baixa margem (otimizar), baixa taxa/alta margem
        (investigar) e baixa taxa/baixa margem (eliminar).
      </p>

      <h3>Fase 2: poda seletiva (8 semanas)</h3>

      <p>
        Elimine primeiro as participacoes do quadrante baixa taxa/baixa margem.
        Essas sao as licitacoes que consomem recursos sem retorno. Tipicamente,
        representam 20% a 30% das participacoes, mas menos de 5% do
        faturamento. Reinvista o tempo liberado em analise mais aprofundada
        das oportunidades nos quadrantes superiores.
      </p>

      <h3>Fase 3: refinamento continuo (12 semanas)</h3>

      <p>
        Implemente um sistema de scoring para todas as novas oportunidades.
        Cada edital recebe uma nota de viabilidade antes de entrar no fluxo de
        elaboracao. Revise o score de corte trimestralmente com base nos
        resultados reais. Ferramentas como o{' '}
        <Link href="/features">
          SmartLic
        </Link>{' '}
        automatizam essa pontuacao, avaliando modalidade, prazo, valor e
        localizacao geografica de cada oportunidade.
      </p>

      <p>
        A migracao completa leva de 3 a 6 meses. Durante esse periodo, e
        normal que o numero de contratos se mantenha estavel enquanto a margem
        liquida aumenta. O ganho de eficiencia aparece primeiro na reducao do
        custo operacional (menos propostas perdidas) e depois no aumento da
        margem media (oportunidades mais qualificadas).
      </p>

      <h2>O papel da tecnologia na transicao</h2>

      <p>
        A estrategia de inteligencia exige dados que a triagem manual nao
        produz com consistencia. Para avaliar viabilidade de forma objetiva,
        a empresa precisa cruzar informacoes de multiplas fontes: portal PNCP,
        Portal de Compras Publicas, ComprasGov, historico de precos
        praticados, dados de concorrentes e metricas internas de desempenho.
      </p>

      <p>
        Fazer esse cruzamento manualmente e possivel, mas nao escala. Uma
        equipe de 3 analistas consegue avaliar no maximo 10 a 15 editais por
        dia com profundidade suficiente. Com ferramentas de inteligencia, o
        mesmo time avalia 50 a 80 editais por dia, aplicando filtros
        automaticos de relevancia setorial e viabilidade antes que qualquer
        analista abra o documento.
      </p>

      <p>
        A diferenca nao e apenas velocidade, mas consistencia. O julgamento
        humano flutua com cansaco, vieses e pressao por metas. Um sistema de
        triagem automatizado aplica os mesmos criterios a cada edital, sem
        excecoes. Isso nao elimina o julgamento humano, mas o direciona para
        as decisoes que realmente importam:{' '}
        <Link href="/blog/reduzir-tempo-analisando-editais-irrelevantes">
          quais dos editais pre-qualificados merecem proposta
        </Link>.
      </p>

      <h2>Indicadores para monitorar a transicao</h2>

      <p>
        Independentemente de qual modelo sua empresa adota, cinco indicadores
        devem ser acompanhados mensalmente para avaliar a eficacia da
        estrategia:
      </p>

      <p>
        <strong>1. Taxa de vitoria por faixa de valor:</strong> segmente seus
        resultados em pelo menos tres faixas (ate R$ 100 mil, R$ 100 mil a
        R$ 500 mil, acima de R$ 500 mil). A taxa de vitoria deve ser maior
        nas faixas onde voce investe mais tempo de analise.
      </p>

      <p>
        <strong>2. Custo por contrato adjudicado:</strong> divida o custo
        total de propostas pelo numero de contratos fechados. Esse numero
        deve cair a medida que a seletividade aumenta.
      </p>

      <p>
        <strong>3. Margem liquida media:</strong> acompanhe se a margem esta
        subindo com a seletividade. Se a margem nao melhora, os criterios de
        triagem precisam ser recalibrados.
      </p>

      <p>
        <strong>4. Tempo medio de elaboracao de proposta:</strong> na
        estrategia de inteligencia, cada proposta recebe mais atencao.
        Monitore se esse tempo adicional esta gerando retorno em taxa de
        vitoria.
      </p>

      <p>
        <strong>5. Pipeline coverage ratio:</strong> a relacao entre o valor
        total das oportunidades no pipeline e a meta de faturamento.
        Mantenha esse ratio acima de 3x para garantir previsibilidade.
      </p>

      {/* CTA — BEFORE FAQ */}
      <div className="not-prose mt-8 sm:mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-xl p-5 sm:p-8 text-center border border-brand-blue/20">
        <p className="text-lg sm:text-xl font-bold text-ink mb-2">
          Migre para inteligencia sem perder oportunidades
        </p>
        <p className="text-sm sm:text-base text-ink-secondary mb-4 sm:mb-6 max-w-lg mx-auto">
          O SmartLic avalia viabilidade automaticamente em 4 criterios objetivos,
          identificando quais editais merecem sua proposta e quais estao consumindo
          recursos sem retorno.
        </p>
        <Link
          href="/signup?source=blog&article=licitacao-volume-ou-inteligencia&utm_source=blog&utm_medium=article&utm_campaign=b2g"
          className="inline-block bg-brand-navy hover:bg-brand-blue-hover text-white font-semibold px-5 sm:px-6 py-2.5 sm:py-3 rounded-button text-sm sm:text-base transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          Comece Gratis
        </Link>
      </div>

      <h2>Perguntas Frequentes</h2>

      <h3>Qual a diferenca entre estrategia de volume e estrategia de inteligencia em licitacoes?</h3>
      <p>
        A estrategia de volume prioriza a quantidade de participacoes,
        apostando na lei dos grandes numeros para converter contratos. A
        estrategia de inteligencia prioriza a selecao criteriosa de editais
        com base em dados de viabilidade, historico do orgao, concorrencia
        estimada e aderencia tecnica. Empresas de volume tipicamente
        participam de 30 a 80 pregoes por mes com taxas de vitoria entre
        5% e 10%. Empresas de inteligencia participam de 8 a 20 pregoes
        por mes com taxas entre 20% e 35%.
      </p>

      <h3>A estrategia de volume funciona para empresas pequenas?</h3>
      <p>
        Raramente. Empresas com equipes de 1 a 3 pessoas no setor de
        licitacoes nao conseguem manter a qualidade das propostas em alto
        volume de participacoes. O custo operacional por proposta (R$ 800
        a R$ 2.500) consome margem de forma desproporcional quando a taxa
        de vitoria e baixa. Para empresas pequenas, a estrategia de
        inteligencia seletiva oferece melhor retorno sobre o investimento.
      </p>

      <h3>E possivel combinar volume e inteligencia?</h3>
      <p>
        Sim. O modelo hibrido aplica volume para oportunidades de baixo
        risco e baixo custo de proposta (como atas de registro de precos e
        pregoes eletronicos padronizados) e inteligencia seletiva para
        oportunidades de alto valor ou alta complexidade. Esse modelo
        exige triagem automatizada para funcionar em escala.
      </p>

      <h3>Quanto custa em media elaborar uma proposta de licitacao?</h3>
      <p>
        O custo medio varia entre R$ 800 e R$ 2.500 por proposta,
        considerando horas de analista, documentacao, certidoes, garantias
        e custos administrativos. Para licitacoes de engenharia ou servicos
        complexos, esse custo pode ultrapassar R$ 5.000 por proposta. Esse
        custo operacional e o principal fator na decisao entre volume e
        inteligencia.
      </p>

      <h3>Como migrar de uma estrategia de volume para inteligencia sem perder receita?</h3>
      <p>
        A migracao deve ser gradual, em tres fases: primeiro, classificar o
        portfolio atual de licitacoes por taxa de vitoria historica e margem
        liquida; segundo, eliminar progressivamente as categorias com pior
        retorno (comecando pelos 20% com menor taxa de vitoria); terceiro,
        reinvestir o tempo liberado em analise aprofundada das oportunidades
        remanescentes. O ciclo completo leva de 3 a 6 meses.
      </p>
    </>
  );
}
