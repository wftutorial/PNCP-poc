import Link from 'next/link';

/**
 * STORY-262 B2G-11: Como Identificar Orgaos com Maior Risco de Atraso no Pagamento
 * Target: 2,000-2,500 words | Cluster: inteligencia em licitacoes
 */
export default function OrgaosRiscoAtrasoPagamentoLicitacao() {
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
                name: 'Como consultar o historico de pagamento de um orgao publico antes de participar de uma licitacao?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'As principais fontes sao o Portal da Transparencia (transparencia.gov.br) para orgaos federais, os portais de transparencia estaduais e municipais, e o SIAFI (Sistema Integrado de Administracao Financeira) para consulta de empenhos e pagamentos do governo federal. No Portal da Transparencia, acesse Despesas > Pagamentos e filtre pelo orgao. Verifique o tempo medio entre a emissao da nota de empenho e o pagamento efetivo nos ultimos 12 meses.',
                },
              },
              {
                '@type': 'Question',
                name: 'O que sao restos a pagar e por que sao um indicador de risco?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Restos a pagar sao despesas empenhadas em um exercicio financeiro que nao foram pagas ate 31 de dezembro. Dividem-se em processados (servico prestado, aguardando pagamento) e nao processados (ainda em execucao). Um volume alto de restos a pagar processados indica que o orgao tem dividas reconhecidas sem recursos para pagar, sinalizando risco de atraso para novos contratos. Em 2024, os restos a pagar do governo federal totalizaram R$ 232,4 bilhoes.',
                },
              },
              {
                '@type': 'Question',
                name: 'Orgaos federais pagam mais rapido que estaduais e municipais?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Em geral, sim. Orgaos federais operam com o Tesouro Nacional como fonte pagadora, o que garante maior previsibilidade. O prazo medio de pagamento em orgaos federais e de 30 a 45 dias. Em orgaos estaduais, varia de 45 a 90 dias dependendo da saude fiscal do estado. Em municipios, a variacao e maior: de 30 dias em municipios superavitarios a mais de 180 dias em municipios com dificuldades fiscais.',
                },
              },
              {
                '@type': 'Question',
                name: 'E possivel incluir clausula de correcao monetaria no contrato para compensar atrasos?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Sim. A Lei 14.133/2021 (Nova Lei de Licitacoes) preve em seu artigo 92, inciso V, a obrigatoriedade de clausula de atualizacao financeira em contratos. Alem disso, o artigo 137 permite a suspensao do contrato pelo fornecedor em caso de atraso superior a 2 meses nos pagamentos devidos pela Administracao. Na pratica, porem, acionar essas clausulas gera desgaste na relacao com o orgao.',
                },
              },
            ],
          }),
        }}
      />

      <p className="text-base sm:text-xl leading-relaxed text-ink">
        No mercado de licitacoes publicas, a obsessao com a adjudicacao
        ofusca um risco igualmente critico: a capacidade do orgao contratante
        de honrar os pagamentos no prazo. Ganhar um pregao e assinar um
        contrato de R$ 500 mil nao significa receber R$ 500 mil. Para
        empresas B2G que dependem de fluxo de caixa previsivel, avaliar o
        risco de inadimplencia do orgao antes de participar de uma licitacao
        e tao importante quanto avaliar a competitividade do preco.
      </p>

      <p>
        Neste artigo, apresentamos um framework pratico com 5 indicadores
        objetivos para classificar o risco de atraso no pagamento de orgaos
        publicos, com as fontes oficiais de consulta e criterios de
        classificacao que podem ser incorporados na sua triagem de editais.
      </p>

      <h2>O risco que ninguem avalia: receber e tao importante quanto ganhar</h2>

      <p>
        A maioria das empresas que participa de licitacoes avalia preco,
        prazo, concorrencia e requisitos tecnicos antes de decidir disputar
        um pregao. Poucas, no entanto, investigam se o orgao contratante
        tem historico de pagar em dia. Esse e um ponto cego que pode
        transformar um contrato aparentemente lucrativo em um problema de
        fluxo de caixa.
      </p>

      <p>
        O impacto financeiro e direto. Uma empresa que fornece mercadorias
        ou presta servicos sob contrato publico arca com os custos de
        producao, logistica e folha de pagamento antes de receber. Quando o
        pagamento atrasa 60, 90 ou 120 dias alem do prazo contratual, a
        empresa precisa financiar o capital de giro com recursos proprios ou
        credito bancario, corroendo a margem do contrato.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Dados de referencia: inadimplencia e atrasos no setor publico</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            &bull; Em 2024, o estoque de restos a pagar inscritos do governo federal totalizou R$ 232,4 bilhoes,
            dos quais R$ 148,7 bilhoes eram processados (despesa ja reconhecida, aguardando pagamento). Esse
            volume cresceu 11,3% em relacao a 2023 (Fonte: Tesouro Nacional, Relatorio de Avaliacao de Receitas
            e Despesas Primarias, 4o bimestre de 2024).
          </li>
          <li>
            &bull; Segundo levantamento da Confederacao Nacional de Municipios (CNM), 38% dos municipios
            brasileiros encerraram 2023 com deficit orcamentario, comprometendo a capacidade de pagamento
            de contratos vigentes (Fonte: CNM, Estudo sobre Financas Municipais, 2024).
          </li>
          <li>
            &bull; O prazo medio de pagamento a fornecedores pelo governo federal foi de 37 dias em 2024, mas
            a mediana por orgao varia de 18 dias (orgaos militares) a 73 dias (universidades federais), indicando
            disparidade significativa entre unidades gestoras (Fonte: Portal da Transparencia, dados de execucao
            orcamentaria, 2024).
          </li>
        </ul>
      </div>

      <h2>Onde consultar historico de pagamento de orgaos publicos</h2>

      <p>
        Antes de detalhar os indicadores de risco, e importante conhecer as
        fontes oficiais de dados. Todas sao publicas e gratuitas:
      </p>

      <h3>Portal da Transparencia (transparencia.gov.br)</h3>

      <p>
        Principal fonte para orgaos federais. Permite consultar despesas por
        orgao, por favorecido (CNPJ do fornecedor) e por periodo. A secao
        &ldquo;Despesas&rdquo; mostra o ciclo completo: empenho, liquidacao
        e pagamento. A diferenca de datas entre liquidacao e pagamento revela
        o prazo efetivo de pagamento do orgao. E possivel exportar dados em
        CSV para analise quantitativa.
      </p>

      <h3>SIAFI (Sistema Integrado de Administracao Financeira)</h3>

      <p>
        O SIAFI e o sistema de execucao orcamentaria do governo federal. Embora
        o acesso direto seja restrito a usuarios credenciados, os dados
        consolidados sao publicados no Portal da Transparencia e no Tesouro
        Gerencial. Para analises mais detalhadas, o Tesouro Gerencial
        (tesourogerencial.tesouro.gov.br) oferece cubos OLAP com cruzamentos
        por orgao, funcao, subfuncao e natureza de despesa.
      </p>

      <h3>Portais estaduais e municipais de transparencia</h3>

      <p>
        A Lei de Acesso a Informacao (Lei 12.527/2011) obriga todos os entes
        federativos a manter portais de transparencia. A qualidade dos dados
        varia significativamente. Estados como Sao Paulo, Minas Gerais e
        Parana mantem portais com dados detalhados de execucao orcamentaria.
        Municipios menores frequentemente publicam apenas o minimo legal, o
        que dificulta a analise.
      </p>

      <h3>Tribunal de Contas (TCU, TCEs, TCMs)</h3>

      <p>
        Os tribunais de contas publicam relatorios de auditoria, contas
        anuais e pareceres sobre a gestao fiscal dos orgaos. O TCU
        disponibiliza dados no portal <em>Contas Publicas</em>. Processos
        de tomada de contas especial (TCE) contra um orgao indicam problemas
        graves de gestao financeira.
      </p>

      <h2>5 indicadores de risco de atraso no pagamento</h2>

      <p>
        Com base nas fontes acima, e possivel construir uma avaliacao de
        risco estruturada para cada orgao. Os cinco indicadores a seguir
        cobrem as dimensoes financeira, orcamentaria e de gestao que mais
        impactam a pontualidade dos pagamentos.
      </p>

      <h3>Indicador 1: Volume de restos a pagar processados</h3>

      <p>
        Restos a pagar processados sao despesas em que o servico ja foi
        prestado ou a mercadoria ja foi entregue, mas o pagamento nao foi
        efetuado dentro do exercicio financeiro. Um volume crescente de
        restos a pagar processados em relacao ao orcamento total do orgao
        indica que as obrigacoes estao se acumulando mais rapido do que a
        capacidade de pagamento.
      </p>

      <p>
        <strong>Como medir:</strong> divida o valor de restos a pagar
        processados pelo orcamento anual do orgao. Acima de 15% e sinal de
        alerta; acima de 25% e risco elevado.
      </p>

      <h3>Indicador 2: Prazo medio entre liquidacao e pagamento</h3>

      <p>
        No ciclo orcamentario, a liquidacao confirma que o fornecedor cumpriu
        sua obrigacao contratual. O pagamento e a transferencia efetiva de
        recursos. O prazo entre liquidacao e pagamento e o indicador mais
        direto de pontualidade. No Portal da Transparencia, e possivel
        calcular esse prazo para orgaos federais consultando as datas de
        liquidacao e pagamento de contratos recentes.
      </p>

      <p>
        <strong>Como medir:</strong> calcule a mediana do prazo
        liquidacao-pagamento nos ultimos 6 meses. Ate 30 dias: regular.
        De 30 a 60 dias: atencao. Acima de 60 dias: risco.
      </p>

      <h3>Indicador 3: Historico de contingenciamento orcamentario</h3>

      <p>
        Contingenciamento e o bloqueio temporario de dotacoes orcamentarias
        pelo Poder Executivo para cumprir metas fiscais. Orgaos
        frequentemente contingenciados tendem a atrasar pagamentos nos
        periodos de restricao, que tipicamente ocorrem no segundo semestre.
        Universidades, institutos de pesquisa e orgaos de saude sao
        historicamente mais afetados por contingenciamentos.
      </p>

      <p>
        <strong>Como medir:</strong> consulte os decretos de programacao
        orcamentaria e financeira publicados pelo Ministerio do Planejamento.
        Compare o orcamento aprovado (LOA) com o orcamento efetivamente
        liberado para cada orgao.
      </p>

      <h3>Indicador 4: Empenhos cancelados ou anulados</h3>

      <p>
        O cancelamento de notas de empenho e um sinal preocupante. Indica que
        o orgao nao conseguiu ou nao quis honrar compromissos ja assumidos. Um
        volume elevado de empenhos anulados em relacao ao total emitido
        sugere problemas de planejamento orcamentario ou restricoes de caixa.
      </p>

      <p>
        <strong>Como medir:</strong> no Portal da Transparencia, filtre por
        orgao e verifique a proporcao de empenhos com situacao
        &ldquo;cancelado&rdquo; ou &ldquo;anulado&rdquo; nos ultimos 12
        meses. Acima de 10% e sinal de alerta.
      </p>

      <h3>Indicador 5: Tomadas de contas especiais (TCE) em andamento</h3>

      <p>
        A instauracao de tomada de contas especial pelo Tribunal de Contas
        indica irregularidade na gestao de recursos publicos. Orgaos com
        TCEs em andamento apresentam risco institucional elevado, pois a
        situacao sugere problemas sistemicos de gestao que frequentemente
        afetam a pontualidade dos pagamentos.
      </p>

      <p>
        <strong>Como medir:</strong> consulte o portal do TCU (pesquisa de
        processos) ou do TCE do respectivo estado. A existencia de mais de
        uma TCE em andamento contra o mesmo orgao nos ultimos 3 anos e
        indicador de risco elevado.
      </p>

      <h2>Classificacao de risco: verde, amarelo, vermelho</h2>

      <div className="not-prose my-6 sm:my-8 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Exemplo pratico: classificacao de risco de um orgao</p>
        <div className="space-y-3 text-sm text-ink-secondary">
          <p>
            <strong>Cenario:</strong> Sua empresa esta avaliando um pregao de R$ 320 mil publicado por uma
            universidade federal no Nordeste. Antes de investir tempo na proposta, voce consulta os 5
            indicadores:
          </p>
          <ul className="space-y-1.5">
            <li>&bull; Restos a pagar processados / orcamento: 22% (amarelo)</li>
            <li>&bull; Prazo medio liquidacao-pagamento: 54 dias (amarelo)</li>
            <li>&bull; Contingenciamento no exercicio atual: sim, 18% do orcamento bloqueado (amarelo)</li>
            <li>&bull; Empenhos cancelados nos ultimos 12 meses: 7% (verde)</li>
            <li>&bull; TCEs em andamento: nenhuma (verde)</li>
          </ul>
          <p className="mt-2">
            <strong>Resultado:</strong> 3 indicadores amarelos e 2 verdes = classificacao geral AMARELA.
          </p>
          <p>
            <strong>Decisao:</strong> O orgao nao apresenta risco critico, mas o prazo de pagamento estimado
            e de 45 a 70 dias. Antes de participar, a empresa deve: (1) verificar se sua margem comporta o
            custo financeiro de 60 dias de capital de giro, estimado em R$ 3.200 (taxa CDI sobre R$ 320 mil
            por 2 meses); (2) considerar clausula de atualizacao financeira conforme Art. 92 da Lei
            14.133/2021.
          </p>
        </div>
      </div>

      <p>
        A classificacao segue uma logica simples baseada na contagem de
        indicadores em cada faixa:
      </p>

      <p>
        <strong>Verde (risco baixo):</strong> pelo menos 4 dos 5 indicadores
        verdes. O orgao demonstra capacidade de pagamento consistente.
        Participacao recomendada sem restricoes adicionais.
      </p>

      <p>
        <strong>Amarelo (risco moderado):</strong> 2 ou 3 indicadores
        amarelos. O orgao apresenta sinais de pressao orcamentaria.
        Participacao recomendada com ajuste de preco para compensar o custo
        financeiro do atraso esperado e com atencao redobrada a clausulas
        de reajuste e correcao monetaria.
      </p>

      <p>
        <strong>Vermelho (risco elevado):</strong> 2 ou mais indicadores
        vermelhos, ou 1 vermelho combinado com 2 ou mais amarelos. O orgao
        tem alta probabilidade de atraso significativo nos pagamentos. A
        participacao so e recomendada se o contrato tiver margem suficiente
        para absorver atrasos de 90 a 180 dias e se a empresa tiver capital
        de giro para sustentar a operacao sem esse recebimento.
      </p>

      <h2>Como incorporar a analise de risco na triagem de editais</h2>

      <p>
        A avaliacao de risco de pagamento deve ser integrada ao processo de
        triagem de editais, nao tratada como etapa separada. Na pratica,
        isso significa que cada oportunidade identificada pelo{' '}
        <Link href="/buscar">
          sistema de busca
        </Link>{' '}
        recebe, alem da avaliacao de viabilidade tecnica e comercial, uma
        nota de risco financeiro do orgao contratante.
      </p>

      <p>
        Para empresas que utilizam ferramentas de inteligencia em licitacoes,
        o fator geografico ja oferece uma primeira camada de triagem. Orgaos
        localizados em municipios com deficit orcamentario recorrente ou em
        estados com historico de contingenciamento elevado recebem pontuacao
        menor na avaliacao de viabilidade geografica. Essa analise
        automatizada nao substitui a consulta direta aos indicadores
        orcamentarios, mas funciona como filtro inicial para direcionar a
        investigacao aprofundada.
      </p>

      <p>
        O fluxo recomendado e o seguinte: a ferramenta de busca identifica
        os editais relevantes por setor e regiao. A{' '}
        <Link href="/blog/escolher-editais-maior-probabilidade-vitoria">
          analise de viabilidade
        </Link>{' '}
        filtra por competitividade e aderencia tecnica. O analista entao
        aplica os 5 indicadores de risco financeiro aos editais
        pre-qualificados, eliminando aqueles com classificacao vermelha (a
        menos que haja justificativa estrategica para aceitar o risco).
      </p>

      <h3>Integrando risco financeiro ao custo da proposta</h3>

      <p>
        Quando o orgao e classificado como amarelo, o custo financeiro do
        atraso esperado deve ser incorporado na formacao de preco da
        proposta. A formula e direta: custo financeiro = valor do contrato
        x taxa de juros mensal x numero estimado de meses de atraso. Esse
        custo deve ser somado a margem, nao absorvido por ela.
      </p>

      <p>
        Empresas que nao fazem esse calculo descobrem tarde demais que um
        contrato &ldquo;vencido&rdquo; com margem de 12% se transformou em
        prejuizo liquido quando o pagamento atrasou 120 dias. A disciplina
        de precificar o risco de inadimplencia antes de enviar a proposta e
        uma das praticas que separam{' '}
        <Link href="/blog/custo-invisivel-disputar-pregoes-errados">
          empresas lucrativas de empresas que faturam muito e lucram pouco
        </Link>.
      </p>

      <h2>Fontes de dados complementares</h2>

      <p>
        Alem dos portais oficiais, duas fontes complementares podem enriquecer
        a avaliacao de risco:
      </p>

      <p>
        <strong>CADIN (Cadastro Informatico de Creditos nao Quitados):</strong>{' '}
        embora voltado para devedores do governo federal, consultar se o orgao
        tem fornecedores inscritos no CADIN pode indicar inadimplencia
        sistemica com o setor privado.
      </p>

      <p>
        <strong>Relatorios de gestao fiscal (LRF):</strong> a Lei de
        Responsabilidade Fiscal obriga entes federativos a publicar
        bimestralmente relatorios de execucao orcamentaria. Esses
        relatorios, disponibilizados nos portais das secretarias de
        fazenda, revelam a saude fiscal do ente e sua capacidade de honrar
        compromissos.
      </p>

      {/* CTA — BEFORE FAQ */}
      <div className="not-prose mt-8 sm:mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-xl p-5 sm:p-8 text-center border border-brand-blue/20">
        <p className="text-lg sm:text-xl font-bold text-ink mb-2">
          Avalie a viabilidade geografica e institucional com o SmartLic
        </p>
        <p className="text-sm sm:text-base text-ink-secondary mb-4 sm:mb-6 max-w-lg mx-auto">
          O SmartLic avalia cada oportunidade com 4 criterios objetivos, incluindo
          viabilidade geografica, ajudando sua equipe a priorizar orgaos com
          melhor historico de execucao orcamentaria.
        </p>
        <Link
          href="/signup?source=blog&article=orgaos-risco-atraso-pagamento-licitacao&utm_source=blog&utm_medium=article&utm_campaign=b2g"
          className="inline-block bg-brand-navy hover:bg-brand-blue-hover text-white font-semibold px-5 sm:px-6 py-2.5 sm:py-3 rounded-button text-sm sm:text-base transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          Comece Gratis
        </Link>
      </div>

      <h2>Perguntas Frequentes</h2>

      <h3>Como consultar o historico de pagamento de um orgao publico antes de participar de uma licitacao?</h3>
      <p>
        As principais fontes sao o Portal da Transparencia
        (transparencia.gov.br) para orgaos federais, os portais de
        transparencia estaduais e municipais, e o SIAFI para consulta de
        empenhos e pagamentos do governo federal. No Portal da
        Transparencia, acesse Despesas, depois Pagamentos, e filtre pelo
        orgao. Verifique o tempo medio entre a emissao da nota de empenho
        e o pagamento efetivo nos ultimos 12 meses.
      </p>

      <h3>O que sao restos a pagar e por que sao um indicador de risco?</h3>
      <p>
        Restos a pagar sao despesas empenhadas em um exercicio financeiro
        que nao foram pagas ate 31 de dezembro. Dividem-se em processados
        (servico prestado, aguardando pagamento) e nao processados (ainda
        em execucao). Um volume alto de restos a pagar processados indica
        que o orgao tem dividas reconhecidas sem recursos para pagar,
        sinalizando risco de atraso para novos contratos. Em 2024, os
        restos a pagar do governo federal totalizaram R$ 232,4 bilhoes.
      </p>

      <h3>Orgaos federais pagam mais rapido que estaduais e municipais?</h3>
      <p>
        Em geral, sim. Orgaos federais operam com o Tesouro Nacional como
        fonte pagadora, o que garante maior previsibilidade. O prazo medio
        de pagamento em orgaos federais e de 30 a 45 dias. Em orgaos
        estaduais, varia de 45 a 90 dias dependendo da saude fiscal do
        estado. Em municipios, a variacao e maior: de 30 dias em municipios
        superavitarios a mais de 180 dias em municipios com dificuldades
        fiscais.
      </p>

      <h3>E possivel incluir clausula de correcao monetaria no contrato para compensar atrasos?</h3>
      <p>
        Sim. A Lei 14.133/2021 (Nova Lei de Licitacoes) preve em seu
        artigo 92, inciso V, a obrigatoriedade de clausula de atualizacao
        financeira em contratos. Alem disso, o artigo 137 permite a
        suspensao do contrato pelo fornecedor em caso de atraso superior
        a 2 meses nos pagamentos devidos pela Administracao. Na pratica,
        porem, acionar essas clausulas gera desgaste na relacao com o
        orgao e pode prejudicar a empresa em futuras licitacoes.
      </p>
    </>
  );
}
