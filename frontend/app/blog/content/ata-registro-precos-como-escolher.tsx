import Link from 'next/link';
import BlogInlineCTA from '../components/BlogInlineCTA';

/**
 * STORY-262 B2G-14: Ata de Registro de Precos — Como Escolher
 * Target: 2,500-3,000 words | Category: Empresas B2G
 */
export default function AtaRegistroPrecoComoEscolher() {
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
                name: 'O fornecedor e obrigado a fornecer toda a quantidade registrada na ARP?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Sim. Conforme o art. 83 da Lei 14.133/2021, o fornecedor registrado e obrigado a fornecer ate o quantitativo maximo registrado, nas condicoes estabelecidas na ata. A recusa injustificada pode resultar em sancoes previstas nos arts. 155 a 163 da mesma lei, incluindo impedimento de licitar.',
                },
              },
              {
                '@type': 'Question',
                name: 'E possivel pedir reequilibrio economico-financeiro durante a vigencia da ARP?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Sim. O art. 82, inciso VI, da Lei 14.133/2021 preve a revisao dos precos registrados quando houver alteracao de fato que eleve o custo do bem ou servico. O fornecedor deve comprovar documentalmente o aumento dos custos, apresentando planilha detalhada e indices de referencia. O orgao gerenciador tem discricionariedade para aceitar ou negar o pedido.',
                },
              },
              {
                '@type': 'Question',
                name: 'Qual a diferenca entre ARP e contrato direto por licitacao convencional?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Na licitacao convencional, o contrato e firmado com quantidade e prazo definidos. Na ARP, o orgao registra precos e quantitativos estimados, mas nao ha obrigacao de aquisicao minima por parte da Administracao. O fornecedor, por outro lado, e obrigado a fornecer quando demandado. Isso cria uma assimetria de risco que precisa ser avaliada.',
                },
              },
              {
                '@type': 'Question',
                name: 'Orgaos nao participantes podem aderir a ARP?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Sim, conforme o art. 86 da Lei 14.133/2021, orgaos nao participantes podem aderir a ARP mediante autorizacao do orgao gerenciador, desde que nao ultrapasse os limites legais. As adesoes sao limitadas a 50% do quantitativo registrado para orgaos federais, e a legislacao estadual e municipal pode estabelecer regras proprias.',
                },
              },
              {
                '@type': 'Question',
                name: 'Quando devo recusar participar de uma ARP?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Recuse quando o volume estimado exceder sua capacidade de entrega, quando a margem entre o preco registrado e seu custo atualizado for inferior a 8-10%, quando houver alta volatilidade de custos sem clausula de reequilibrio adequada, ou quando o orgao gerenciador tiver historico de demandas irregulares e atrasos no pagamento.',
                },
              },
            ],
          }),
        }}
      />

      <p className="text-base sm:text-xl leading-relaxed text-ink">
        A Ata de Registro de Precos e um dos instrumentos mais utilizados nas
        compras publicas brasileiras, e tambem um dos menos compreendidos por
        fornecedores. Muitas empresas tratam toda ARP como uma oportunidade
        automatica de receita, sem avaliar os riscos especificos desse modelo
        de contratacao. O resultado e previsivel: fornecedores que se
        comprometem com precos que nao sustentam, volumes que nao conseguem
        atender e obrigacoes que desconheciam ao registrar a proposta. Este
        artigo apresenta os 6 criterios objetivos para avaliar se uma ARP
        realmente vale sua participacao, fundamentados na Lei 14.133/2021 e na
        pratica do mercado B2G.
      </p>

      <h2>O que e uma ARP e por que e diferente de licitacao convencional</h2>

      <p>
        O Sistema de Registro de Precos (SRP) esta disciplinado nos artigos
        82 a 86 da Lei 14.133/2021 (Nova Lei de Licitacoes). Diferentemente
        da licitacao convencional, onde a Administracao contrata uma quantidade
        definida com prazo certo, o SRP registra precos e condições para
        aquisicoes futuras, sem compromisso de quantidade minima por parte do
        orgao comprador.
      </p>

      <p>
        Na pratica, isso significa que o fornecedor registrado se obriga a
        manter o preco e a disponibilidade durante toda a vigencia da ata (ate
        12 meses, conforme o art. 84 da Lei 14.133/2021), enquanto a
        Administracao pode comprar tudo, parte ou nada do que foi registrado.
        Essa assimetria e o ponto central que diferencia a ARP de um contrato
        convencional e que exige avaliacao cuidadosa antes da participacao.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Dados de referencia: Registro de Precos no Brasil</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• Em 2025, aproximadamente 42% das contratacoes publicadas no PNCP utilizaram o Sistema de Registro de Precos, totalizando mais de 500 mil processos (Fonte: Painel de Compras do Governo Federal, consolidado dez/2025).</li>
          <li>• A vigencia media das ARPs registradas em 2025 foi de 10,3 meses, com 68% das atas tendo vigencia de 12 meses (Fonte: Painel PNCP, Estatisticas de Compras, 2025).</li>
          <li>• O Tribunal de Contas da Uniao registrou aumento de 27% nos pedidos de reequilibrio economico-financeiro em ARPs entre 2023 e 2025, refletindo a volatilidade de custos no periodo (Fonte: TCU, Relatorio de Auditoria em Compras Publicas, 2025).</li>
        </ul>
      </div>

      <h2>Vantagens reais da ARP para o fornecedor</h2>

      <p>
        Antes de analisar os riscos, e importante reconhecer as vantagens
        genuinas que a ARP oferece ao fornecedor bem posicionado.
      </p>

      <p>
        <strong>Previsibilidade de demanda estimada.</strong> Embora nao haja
        garantia de compra, a ARP fornece uma estimativa de demanda que permite
        planejamento de producao, estoque e logistica. Fornecedores que
        compreendem o padrao de consumo do orgao gerenciador podem antecipar
        pedidos e otimizar sua operacao.
      </p>

      <p>
        <strong>Relacionamento institucional.</strong> Estar registrado em uma
        ARP cria um vinculo formal com o orgao comprador. Quando a demanda
        surge, o fornecedor registrado e o primeiro a ser acionado. Isso
        elimina a necessidade de competir novamente por cada pedido individual
        durante a vigencia da ata.
      </p>

      <p>
        <strong>Possibilidade de adesoes.</strong> Conforme o art. 86 da Lei
        14.133/2021, orgaos nao participantes da licitacao original podem aderir
        a ARP, ampliando o volume potencial de vendas sem nova competicao. Para
        o fornecedor, cada adesao representa receita adicional com custo
        comercial zero.
      </p>

      <h2>Riscos subestimados da ARP</h2>

      <p>
        Os riscos da ARP sao sistematicamente subestimados por fornecedores,
        especialmente aqueles com pouca experiencia no modelo. Os tres riscos
        principais sao:
      </p>

      <p>
        <strong>Obrigacao de fornecimento unilateral.</strong> O art. 83 da Lei
        14.133/2021 estabelece que o fornecedor registrado e obrigado a fornecer
        ate o quantitativo maximo registrado. A recusa injustificada sujeita a
        empresa as sancoes dos arts. 155 a 163, incluindo multa, impedimento de
        licitar e ate declaracao de inidoneidade. Nao existe a opcao de
        &ldquo;desistir&rdquo; de uma ARP vigente sem consequencias.
      </p>

      <p>
        <strong>Volume incerto.</strong> A Administracao pode demandar 100% do
        quantitativo registrado ou 0%. O fornecedor que dimensionou sua operacao
        para atender o volume total pode ficar com estoque parado. O que
        dimensionou para atender o minimo pode nao ter capacidade quando a
        demanda cheia se materializar.
      </p>

      <p>
        <strong>Defasagem de precos.</strong> Em atas com vigencia de 12 meses,
        a variacao de custos de insumos pode corroer a margem do fornecedor.
        O pedido de reequilibrio e um direito, mas sua concessao depende de
        comprovacao documental rigorosa e da discricionariedade do orgao. Nao
        ha garantia de aprovacao, nem de celeridade no processo.
      </p>

      <BlogInlineCTA slug="ata-registro-precos-como-escolher" campaign="b2g" />

      <h2>Os 6 criterios para avaliar uma ARP</h2>

      <p>
        A decisao de participar de uma ARP deve ser baseada em criterios
        objetivos, nao em otimismo. Os seis criterios a seguir formam um
        framework de avaliacao que pode ser aplicado a qualquer ARP, independente
        do setor ou do porte da empresa. Esse tipo de analise estruturada e o
        que diferencia empresas que participam de{' '}
        <Link href="/blog/escolher-editais-maior-probabilidade-vitoria">
          editais com maior probabilidade de vitoria
        </Link>.
      </p>

      <h3>Criterio 1: Volume estimado vs. capacidade de entrega</h3>

      <p>
        O primeiro criterio e o mais fundamental: a empresa tem capacidade
        operacional para atender o volume maximo registrado? Nao o volume
        medio, nao o volume esperado, mas o volume maximo. Porque a
        Administracao pode exigir tudo de uma vez, e a recusa injustificada
        gera sancao.
      </p>

      <p>
        A avaliacao deve considerar nao apenas a capacidade de producao, mas
        tambem logistica de entrega, capacidade de armazenamento, e fluxo de
        caixa para antecipar custos antes do pagamento. Se o volume maximo
        da ARP excede 70% da capacidade operacional da empresa (considerando
        outros contratos ativos), o risco e elevado.
      </p>

      <h3>Criterio 2: Preco registrado vs. custo atualizado</h3>

      <p>
        O preco proposto no momento da licitacao era competitivo e rentavel.
        Mas entre a proposta e o primeiro pedido podem se passar semanas ou
        meses. A pergunta correta nao e &ldquo;o preco esta bom hoje?&rdquo;
        mas &ldquo;o preco estara viavel daqui a 6 meses?&rdquo;.
      </p>

      <p>
        A recomendacao e calcular a margem liquida considerando o cenario de
        custos projetado para o periodo da ata. Se a margem projetada for
        inferior a 8% no pior cenario, a ARP representa risco financeiro
        relevante. Em setores com alta volatilidade de insumos (alimentos,
        materiais eletricos, combustiveis), a margem de seguranca deve ser
        ainda maior.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Exemplo pratico: calculo de margem em ARP de materiais de escritorio</p>
        <p className="text-sm text-ink-secondary mb-3">
          Uma empresa avalia uma ARP para fornecimento de materiais de
          escritorio a orgaos federais. O preco registrado para o kit basico
          e de R$ 85,00 por unidade. O volume maximo registrado e de 12.000
          unidades em 12 meses.
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• <strong>Custo atual do kit:</strong> R$ 68,00 (margem atual: 20%)</li>
          <li>• <strong>Projecao de custo em 6 meses:</strong> R$ 74,00 (inflacao de insumos + frete, estimativa conservadora baseada em IPCA acumulado de 5,2% e reajuste de frete rodoviario)</li>
          <li>• <strong>Projecao de custo em 12 meses:</strong> R$ 79,00</li>
          <li>• <strong>Margem no pior cenario (12 meses):</strong> (85 - 79) / 85 = 7,1%</li>
          <li>• <strong>Decisao:</strong> Margem abaixo de 8% no cenario projetado. Participar somente se a ARP contiver clausula de reequilibrio clara e o orgao tiver historico de aceitar pedidos de revisao.</li>
        </ul>
      </div>

      <h3>Criterio 3: Quantidade de participantes (diluicao)</h3>

      <p>
        Em ARPs com multiplos fornecedores registrados, o volume total e
        distribuido entre os participantes. Quanto mais fornecedores, menor
        o volume garantido para cada um. A avaliacao deve considerar quantos
        fornecedores o edital preve registrar e qual a regra de distribuicao
        (rodizio, preferencia por ordem de classificacao, ou demanda livre).
      </p>

      <p>
        ARPs que registram mais de 5 fornecedores para o mesmo item diluem
        significativamente o volume individual. Se o edital nao especifica
        criterio de distribuicao, o risco de volume baixo e real, e o
        fornecedor pode manter obrigacao contratual para um volume que nunca
        se materializa.
      </p>

      <h3>Criterio 4: Orgao gerenciador e historico de demanda</h3>

      <p>
        O comportamento do orgao gerenciador e um indicador preditivo
        importante. Orgaos com historico consistente de consumo tendem a
        demandar volumes proximos ao estimado. Orgaos com historico de atas
        subutilizadas representam risco de volume ocioso.
      </p>

      <p>
        A verificacao pode ser feita consultando contratacoes anteriores do
        mesmo orgao no PNCP, verificando se houve atas para o mesmo objeto
        nos anos anteriores e qual foi o percentual efetivamente demandado.
        Essa analise de historico e um dos fatores que o{' '}
        <Link href="/features">
          SmartLic incorpora na avaliacao de viabilidade
        </Link>{' '}
        de cada oportunidade.
      </p>

      <h3>Criterio 5: Prazo de vigencia vs. volatilidade de custos</h3>

      <p>
        Atas com vigencia de 12 meses em setores com alta volatilidade de
        custos sao inerentemente mais arriscadas do que atas de 6 meses em
        setores estaveis. A avaliacao deve cruzar o prazo da ata com a
        previsibilidade dos custos dos insumos principais.
      </p>

      <p>
        Em setores como alimentos e combustiveis, onde os precos podem variar
        20% ou mais em 12 meses, a vigencia longa e um fator de risco critico.
        Em setores como papelaria e mobiliario, onde a variacao de custos e
        mais moderada, o risco da vigencia longa e menor. As{' '}
        <Link href="/blog/clausulas-escondidas-editais-licitacao">
          clausulas do edital que impactam essa avaliacao
        </Link>{' '}
        precisam ser analisadas com atencao. Quem acompanha o mercado sabe
        que{' '}
        <Link href="/blog/nova-geracao-ferramentas-mercado-licitacoes">
          novas ferramentas que estão mudando o mercado de licitações
        </Link>{' '}
        ja automatizam parte dessa analise de clausulas e vigencia.
      </p>

      <h3>Criterio 6: Clausula de reequilibrio</h3>

      <p>
        O sexto criterio e frequentemente o mais negligenciado: como o edital
        trata o reequilibrio economico-financeiro? A Lei 14.133/2021, no art.
        82, inciso VI, preve a possibilidade de revisao de precos, mas a
        implementacao pratica varia significativamente entre orgaos.
      </p>

      <p>
        Verifique se o edital especifica: (a) qual indice de referencia sera
        utilizado para avaliar pedidos de reequilibrio, (b) qual o prazo maximo
        para resposta ao pedido, (c) se ha previsao de reequilibrio automatico
        por indice ou apenas por solicitacao fundamentada, e (d) se ha
        precedentes de reequilibrio concedido pelo mesmo orgao em atas
        anteriores.
      </p>

      <p>
        Um edital que menciona reequilibrio apenas de forma generica, sem
        definir indice, prazo ou procedimento, oferece baixa seguranca ao
        fornecedor. Em contrapartida, editais com clausula detalhada de
        reequilibrio reduzem significativamente o risco de defasagem.
      </p>

      <h2>Quando recusar uma ARP</h2>

      <p>
        A decisao de nao participar de uma ARP e tao importante quanto a
        decisao de participar. Recuse quando:
      </p>

      <p>
        <strong>O volume maximo excede sua capacidade.</strong> Se voce nao
        consegue atender 100% do quantitativo registrado considerando seus
        outros contratos ativos, o risco de inadimplencia e real. E a
        consequencia e sancao administrativa.
      </p>

      <p>
        <strong>A margem projetada e insuficiente.</strong> Se o calculo de
        margem no cenario pessimista (custo maximo projetado vs. preco
        registrado) indica margem liquida inferior a 8%, a ARP pode se
        transformar em contrato deficitario.
      </p>

      <p>
        <strong>O orgao tem historico problematico.</strong> Orgaos com
        historico de atrasos no pagamento superiores a 60 dias, ou com
        historico de negar sistematicamente pedidos de reequilibrio, representam
        risco financeiro desproporcional.
      </p>

      <p>
        <strong>A volatilidade do setor e incompativel com o prazo.</strong>{' '}
        Ata de 12 meses para itens cujos insumos variam mais de 15% ao ano,
        sem clausula de reequilibrio robusta, e uma aposta contra o fornecedor.
      </p>

      <p>
        O artigo sobre{' '}
        <Link href="/blog/disputar-todas-licitacoes-matematica-real">
          a matematica real de disputar todas as licitacoes
        </Link>{' '}
        aprofunda o raciocinio quantitativo por tras dessa seletividade.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Checklist rapido: avaliacao de ARP em 10 minutos</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• Volume maximo registrado cabe na sua capacidade operacional? (Sim/Nao)</li>
          <li>• Margem liquida projetada no pior cenario de custos e superior a 8%? (Sim/Nao)</li>
          <li>• Ha menos de 5 fornecedores registrados para o mesmo item? (Sim/Nao)</li>
          <li>• O orgao gerenciador tem historico de demanda consistente? (Sim/Nao)</li>
          <li>• A vigencia da ata e compativel com a volatilidade dos seus custos? (Sim/Nao)</li>
          <li>• O edital tem clausula de reequilibrio detalhada com indice de referencia? (Sim/Nao)</li>
          <li>• <strong>Resultado:</strong> 5 ou 6 respostas &ldquo;Sim&rdquo; = ARP viavel. 3 ou 4 = Requer analise aprofundada. Menos de 3 = Recusar.</li>
        </ul>
      </div>

      <h2>Consideracoes sobre a Lei 14.133/2021</h2>

      <p>
        A Nova Lei de Licitacoes trouxe mudancas relevantes para o SRP que
        impactam diretamente a avaliacao do fornecedor. O art. 82 estabelece
        que o SRP sera adotado preferencialmente quando a Administracao nao
        puder definir previamente o quantitativo a ser demandado, quando for
        conveniente a aquisicao parcelada, ou quando atender a mais de um
        orgao.
      </p>

      <p>
        O art. 84 limita a vigencia da ARP a 12 meses, prorrogavel por igual
        periodo (totalizando 24 meses). O art. 86 disciplina as adesoes por
        orgaos nao participantes, limitando-as a 50% do quantitativo
        registrado no ambito federal. Essas regras devem ser consideradas no
        calculo de volume potencial total.
      </p>

      <p>
        Um ponto frequentemente ignorado e que a Lei 14.133/2021 exige que o
        edital contenha o quantitativo maximo de cada item, vedada a
        indicacao de quantitativo minimo (art. 82, par. 5). Isso reforça a
        assimetria do modelo: o fornecedor se compromete com o maximo, a
        Administracao nao se compromete com nenhum minimo.
      </p>

      {/* CTA — BEFORE FAQ */}
      <div className="not-prose mt-8 sm:mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-xl p-5 sm:p-8 text-center border border-brand-blue/20">
        <p className="text-lg sm:text-xl font-bold text-ink mb-2">
          Filtre ARPs por viabilidade real
        </p>
        <p className="text-sm sm:text-base text-ink-secondary mb-4 sm:mb-6 max-w-lg mx-auto">
          O SmartLic analisa modalidade, valor, prazo e regiao de cada
          oportunidade. Identifique rapidamente quais ARPs valem sua
          participacao e quais devem ser descartadas.
        </p>
        <Link
          href="/signup?source=blog&article=ata-registro-precos-como-escolher&utm_source=blog&utm_medium=cta&utm_content=ata-registro-precos-como-escolher&utm_campaign=b2g"
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

      <h3>O fornecedor e obrigado a fornecer toda a quantidade registrada na ARP?</h3>
      <p>
        Sim. Conforme o art. 83 da Lei 14.133/2021, o fornecedor registrado e
        obrigado a fornecer ate o quantitativo maximo registrado, nas condicoes
        estabelecidas na ata. A recusa injustificada pode resultar em sancoes
        previstas nos arts. 155 a 163 da mesma lei, incluindo multa,
        impedimento de licitar e declaracao de inidoneidade. Por isso, a
        avaliacao de capacidade operacional antes da participacao e
        indispensavel.
      </p>

      <h3>E possivel pedir reequilibrio economico-financeiro durante a vigencia da ARP?</h3>
      <p>
        Sim. O art. 82, inciso VI, da Lei 14.133/2021 preve a revisao dos
        precos registrados quando houver alteracao de fato que eleve o custo
        do bem ou servico. O fornecedor deve comprovar documentalmente o
        aumento dos custos, apresentando planilha detalhada e indices de
        referencia aceitos pelo orgao. E importante notar que o orgao
        gerenciador tem discricionariedade para aceitar ou negar o pedido,
        e o processo pode levar semanas ou meses.
      </p>

      <h3>Qual a diferenca entre ARP e contrato direto por licitacao convencional?</h3>
      <p>
        Na licitacao convencional, o contrato e firmado com quantidade definida,
        prazo de execucao e valor total estabelecido. O orgao se compromete a
        adquirir e o fornecedor se compromete a entregar. Na ARP, ha uma
        assimetria fundamental: o orgao registra quantidades estimadas sem
        obrigacao de compra minima, enquanto o fornecedor se obriga a fornecer
        ate o quantitativo maximo quando demandado. Essa assimetria transfere
        o risco de demanda para o fornecedor.
      </p>

      <h3>Orgaos nao participantes podem aderir a ARP?</h3>
      <p>
        Sim, conforme o art. 86 da Lei 14.133/2021. Orgaos nao participantes
        podem aderir a ARP mediante autorizacao do orgao gerenciador e
        aceitacao do fornecedor, desde que respeitados os limites legais. No
        ambito federal, as adesoes sao limitadas a 50% do quantitativo
        registrado. Para o fornecedor, as adesoes podem representar
        oportunidade de receita adicional, mas tambem ampliam o volume total
        de obrigacao, o que deve ser considerado no dimensionamento de
        capacidade.
      </p>

      <h3>Quando devo recusar participar de uma ARP?</h3>
      <p>
        Recuse quando o volume maximo estimado exceder sua capacidade de
        entrega considerando outros contratos ativos, quando a margem liquida
        projetada para o pior cenario de custos for inferior a 8-10%, quando
        houver alta volatilidade de custos no seu setor sem clausula de
        reequilibrio adequada no edital, ou quando o orgao gerenciador tiver
        historico de demandas irregulares e atrasos significativos no
        pagamento. A seletividade na participacao e um indicador de maturidade
        operacional.
      </p>
      {/* TODO: Link para página programática de setor — MKT-003 */}
      {/* TODO: Link para página programática de cidade — MKT-005 */}
    </>
  );
}
