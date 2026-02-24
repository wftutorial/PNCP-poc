import Link from 'next/link';

/**
 * STORY-262 B2G-08: O Custo Invisivel de Disputar Pregoes Errados
 * Target: 2,000–2,500 words
 */
export default function CustoInvisivelDisputarPregoesErrados() {
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
                name: 'Quanto custa participar de um pregao eletronico do inicio ao fim?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'O custo total de participacao em um pregao eletronico inclui horas de analise do edital (8 a 24 horas de trabalho qualificado), emissao e renovacao de certidoes (R$ 200 a R$ 1.500 por processo), elaboracao da proposta (4 a 16 horas), acompanhamento da sessao publica e eventuais recursos. Considerando o custo-hora de profissionais de licitacao (R$ 45 a R$ 80/hora), cada participacao custa entre R$ 1.800 e R$ 6.500 em recursos diretos, antes de considerar custos de garantia e custo de oportunidade.',
                },
              },
              {
                '@type': 'Question',
                name: 'Qual a taxa media de vitoria em pregoes eletronicos no Brasil?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'A taxa media de adjudicacao em pregoes eletronicos no Brasil situa-se entre 8% e 15%, segundo dados de mercado e analises do Painel de Compras Governamentais. Isso significa que uma empresa que participa de 20 pregoes por ano pode esperar vencer entre 1 e 3, dependendo do setor e da qualidade da sua selecao de editais. Empresas com processos estruturados de triagem alcancam taxas entre 20% e 35%.',
                },
              },
              {
                '@type': 'Question',
                name: 'Como identificar um pregao que nao vale a pena disputar?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Os principais indicadores de um pregao de baixa viabilidade sao: objeto com baixo alinhamento setorial (a empresa atende apenas parcialmente o escopo), valor estimado fora da faixa de competitividade da empresa, requisitos de habilitacao que exigem atestados ou qualificacoes que a empresa nao possui, prazo de entrega incompativel com a capacidade operacional, e historico do orgao contratante com atraso de pagamento. Ferramentas de analise de viabilidade podem avaliar esses criterios automaticamente.',
                },
              },
              {
                '@type': 'Question',
                name: 'Qual o custo de oportunidade de disputar pregoes errados?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'O custo de oportunidade e o custo mais significativo e mais dificil de mensurar. Cada hora investida em um pregao sem viabilidade e uma hora que poderia ser dedicada a um edital com alta probabilidade de vitoria. Em termos praticos, uma empresa que desperdicou 200 horas anuais em pregoes que perdeu poderia ter alocado esse tempo para elaborar propostas mais competitivas para editais com maior alinhamento, potencialmente gerando 2 a 4 contratos adicionais.',
                },
              },
            ],
          }),
        }}
      />

      <p className="text-base sm:text-xl leading-relaxed text-ink">
        Participar de licitacoes publicas tem um custo. Esse custo e evidente quando
        se ganha — a margem operacional do contrato absorve o investimento em prospeccao,
        analise e elaboracao. Mas quando se perde, o custo nao desaparece. Ele apenas
        deixa de ser contabilizado. A maioria das empresas B2G nao mensura quanto gasta
        por ano em pregoes que nunca tinham viabilidade real de vitoria — e o valor e
        significativamente maior do que a intuicao sugere.
      </p>

      <h2>Os custos que ninguem contabiliza</h2>

      <p>
        Quando uma empresa decide participar de um pregao, uma cadeia de custos se inicia.
        Cada etapa consome recursos — humanos, financeiros e de tempo — que so sao
        recuperados em caso de adjudicacao. O problema e que, com uma taxa media de
        adjudicacao entre 8% e 15% no mercado brasileiro (fonte: Painel de Compras
        Governamentais, dados consolidados 2023-2024), a maior parte desses investimentos
        nunca gera retorno.
      </p>

      <p>
        O que torna esses custos particularmente danosos e sua invisibilidade contabil. Eles
        nao aparecem em uma linha separada do demonstrativo financeiro. Estao diluidos em
        salarios, despesas administrativas e custos gerais de operacao. Para enxerga-los, e
        preciso decompor o custo de cada participacao em seus componentes.
      </p>

      <h2>Custo 1: Horas de analise de edital</h2>

      <p>
        Antes de decidir participar, alguem precisa ler o edital. Um edital de pregao
        eletronico tem, em media, entre 30 e 80 paginas, incluindo anexos, termos de
        referencia e minutas de contrato. A leitura qualificada — aquela que identifica
        requisitos de habilitacao, condicoes de execucao, prazos e riscos — consome entre
        2 e 6 horas de trabalho de um profissional experiente.
      </p>

      <p>
        Considerando o custo-hora de um analista de licitacoes pleno (R$ 45 a R$ 80/hora,
        incluindo encargos, segundo dados salariais da Glassdoor Brasil, 2025), cada analise
        de edital custa entre R$ 90 e R$ 480 em trabalho qualificado. Se a empresa analisa
        10 editais para decidir participar de 3, sao de R$ 900 a R$ 4.800 apenas na fase
        de avaliacao — antes de redigir uma unica proposta.
      </p>

      <h2>Custo 2: Documentacao e certidoes</h2>

      <p>
        A habilitacao em pregoes eletronicos exige um conjunto de documentos que precisam
        estar atualizados: certidoes negativas de debitos (federal, estadual, municipal,
        trabalhista, FGTS), atestados de capacidade tecnica, balanco patrimonial, e em
        alguns casos, certidoes especificas do setor de atuacao. O custo direto de
        emissao e renovacao desse pacote documental varia entre R$ 200 e R$ 1.500 por
        processo, dependendo do numero de certidoes exigidas e da necessidade de
        autenticacao ou reconhecimento de firma.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Dados de referencia: custos documentais por processo</p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>• Certidoes negativas de debitos (CND federal, estadual, municipal, FGTS, trabalhista): R$ 0 a R$ 150 em taxas (variam por UF e cartorio)</li>
          <li>• Autenticacao e reconhecimento de firma: R$ 50 a R$ 200 por conjunto documental (fonte: tabela de custas cartorias, 2024)</li>
          <li>• Atestados de capacidade tecnica (quando exigem registro no CREA/CRA): R$ 150 a R$ 400 por atestado registrado</li>
          <li>• Tempo de organizacao do pacote documental: 4 a 8 horas de trabalho administrativo</li>
          <li>• Custo total por participacao (documentacao): R$ 200 a R$ 1.500 em custos diretos + 4 a 8 horas de trabalho</li>
        </ul>
      </div>

      <p>
        O custo documental nao e trivial quando multiplicado pelo numero de pregoes disputados
        ao longo do ano. Uma empresa que participa de 30 pregoes/ano investe entre R$ 6.000 e
        R$ 45.000 apenas em documentacao — independentemente do resultado.
      </p>

      <h2>Custo 3: Oportunidades perdidas (custo de oportunidade)</h2>

      <p>
        Esse e, possivelmente, o custo mais significativo e o mais dificil de mensurar. Cada
        hora que o analista de editais ou o especialista em propostas dedica a um pregao de
        baixa viabilidade e uma hora que nao esta sendo investida em um edital com alta
        probabilidade de vitoria.
      </p>

      <p>
        O custo de oportunidade se manifesta de duas formas: editais com bom potencial que
        nao foram analisados a tempo porque a equipe estava ocupada com pregoes errados, e
        propostas que poderiam ter sido mais competitivas se a equipe tivesse dedicado mais
        tempo a elaboracao. Em ambos os casos, o resultado e receita que deixou de existir.
        Para entender como evitar esse ciclo,{' '}
        <Link href="/blog/erro-operacional-perder-contratos-publicos">
          leia nossa analise sobre erros operacionais que custam contratos
        </Link>.
      </p>

      <h2>Custo 4: Desgaste da equipe e turnover</h2>

      <p>
        Profissionais de licitacao que passam semanas elaborando propostas para pregoes
        que sistematicamente perdem experimentam um efeito cumulativo de frustracao. O
        desgaste e real e mensuravel: segundo pesquisa do Instituto Brasileiro de
        Governanca Corporativa (IBGC, 2023), a taxa de turnover em funcoes administrativas
        ligadas a processos repetitivos e burocraticos e 30% superior a media do mercado.
      </p>

      <p>
        O custo de substituicao de um profissional qualificado em licitacoes — incluindo
        recrutamento, treinamento e periodo de ramp-up — equivale a 3 a 5 meses de
        salario. Para um analista pleno que recebe R$ 5.500/mes, isso representa entre
        R$ 16.500 e R$ 27.500 por substituicao.
      </p>

      <h2>Custo 5: Garantias e caucoes bloqueadas</h2>

      <p>
        Determinadas modalidades de licitacao exigem garantia de proposta (geralmente 1%
        a 5% do valor estimado) ou caucao para participacao. Enquanto a empresa esta
        participando do processo, esses valores ficam bloqueados — indisponiveis para
        capital de giro ou investimento em outras oportunidades.
      </p>

      <p>
        Para uma empresa que participa de multiplos pregoes simultaneamente com garantias,
        o montante bloqueado pode comprometer a liquidez. A titulo de exemplo: garantias
        de 1% em 5 pregoes de R$ 500.000 representam R$ 25.000 imobilizados, que em
        alguns casos ficam retidos por 60 a 90 dias apos o encerramento do processo.
      </p>

      <h2>Custo 6: Risco reputacional em desistencias</h2>

      <p>
        Quando uma empresa vence um pregao e depois desiste — porque percebeu tardiamente
        que o preco nao e viavel ou que nao atende aos requisitos de execucao —, o dano
        reputacional junto ao orgao contratante e concreto. A Lei 14.133/2021 preve
        sancoes que incluem impedimento de licitar e contratar com a administracao publica
        por periodo de ate 3 anos (Art. 156), alem de multas.
      </p>

      <p>
        Mesmo sem sancao formal, a desistencia gera um registro negativo no SICAF (Sistema
        de Cadastramento Unificado de Fornecedores) que pode ser consultado por outros
        orgaos. O custo indireto e a perda de confianca de orgaos contratantes que, em
        processos futuros, podem questionar a capacidade da empresa.
      </p>

      <h2>O calculo consolidado: quanto custa errar 10 pregoes por ano</h2>

      <p>
        Para tangibilizar o impacto, vamos consolidar os custos de participar de 10
        pregoes sem viabilidade real de vitoria ao longo de um ano. Esse e um cenario
        conservador — muitas empresas B2G participam de 20 a 40 pregoes anuais com
        taxa de adjudicacao inferior a 10%.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">Exemplo pratico: custo consolidado de 10 pregoes perdidos por ano</p>
        <div className="text-sm text-ink-secondary space-y-3">
          <p><strong>Premissas:</strong></p>
          <ul className="space-y-1 ml-4">
            <li>• 10 pregoes disputados sem viabilidade adequada</li>
            <li>• Custo-hora do analista: R$ 55/hora (media pleno, com encargos)</li>
            <li>• Tempo medio de analise por edital: 4 horas</li>
            <li>• Tempo medio de elaboracao de proposta: 12 horas</li>
            <li>• Custo documental medio: R$ 600 por processo</li>
          </ul>
          <p><strong>Custos diretos:</strong></p>
          <ul className="space-y-1 ml-4">
            <li>• Analise de editais: 10 x 4h x R$ 55 = <strong>R$ 2.200</strong></li>
            <li>• Elaboracao de propostas: 10 x 12h x R$ 55 = <strong>R$ 6.600</strong></li>
            <li>• Documentacao: 10 x R$ 600 = <strong>R$ 6.000</strong></li>
            <li>• Acompanhamento de sessoes: 10 x 3h x R$ 55 = <strong>R$ 1.650</strong></li>
          </ul>
          <p><strong>Subtotal direto: R$ 16.450</strong></p>
          <p><strong>Custos indiretos estimados:</strong></p>
          <ul className="space-y-1 ml-4">
            <li>• Custo de oportunidade (190 horas desviadas): equivalente a 2-3 propostas para editais viaveis = <strong>R$ 500.000 a R$ 750.000 em contratos potenciais nao perseguidos</strong></li>
            <li>• Impacto no turnover (estimativa conservadora): <strong>R$ 5.000 a R$ 10.000/ano</strong></li>
          </ul>
          <p><strong>Custo total estimado: R$ 21.450 a R$ 26.450 em custos diretos + R$ 500.000 a R$ 750.000 em receita potencial perdida.</strong></p>
        </div>
      </div>

      <p>
        O custo direto de R$ 21.000 a R$ 26.000 por ano pode parecer gerenciavel para uma
        empresa de medio porte. Mas o custo de oportunidade — a receita que deixou de ser
        buscada — e o que realmente impacta o faturamento. Se metade das 190 horas
        desperdicadas tivesse sido redirecionada para editais de alta viabilidade, o
        retorno potencial superaria em ordens de grandeza o custo direto.{' '}
        <Link href="/blog/disputar-todas-licitacoes-matematica-real">
          Veja a matematica completa de por que disputar todas as licitacoes gera prejuizo
        </Link>.
      </p>

      <h2>Como reduzir esses custos estruturalmente</h2>

      <p>
        A solucao nao e participar de menos licitacoes — e participar das licitacoes certas.
        A diferenca esta na qualidade da triagem. Empresas que implementam processos
        estruturados de analise de viabilidade antes de decidir participar conseguem
        redirecionar recursos dos pregoes de baixa probabilidade para os de alta
        probabilidade.
      </p>

      <p>
        Tres acoes concretas reduzem o custo de participacao em pregoes errados: primeiro,
        definir criterios objetivos de triagem (alinhamento setorial, faixa de valor,
        requisitos de habilitacao, historico do orgao); segundo, automatizar a fase de
        prospecao e triagem inicial para que a equipe humana avalie apenas editais
        pre-qualificados; terceiro, acompanhar metricas de eficiencia (taxa de
        adjudicacao, custo por proposta) para identificar e corrigir desvios
        rapidamente. Para entender como equipes gastam 40 horas por mes em editais
        que descartam,{' '}
        <Link href="/blog/equipe-40-horas-mes-editais-descartados">
          leia nosso diagnostico sobre triagem manual
        </Link>.
      </p>

      {/* CTA — BEFORE FAQ */}
      <div className="not-prose mt-8 sm:mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-xl p-5 sm:p-8 text-center border border-brand-blue/20">
        <p className="text-lg sm:text-xl font-bold text-ink mb-2">
          Elimine pregoes de baixa viabilidade automaticamente
        </p>
        <p className="text-sm sm:text-base text-ink-secondary mb-4 sm:mb-6 max-w-lg mx-auto">
          O SmartLic analisa cada edital com base em 4 criterios de viabilidade e classifica
          relevancia setorial por IA — para que sua equipe invista tempo apenas em pregoes
          com chance real de retorno.
        </p>
        <Link
          href="/signup?source=blog&article=custo-invisivel-disputar-pregoes-errados&utm_source=blog&utm_medium=article&utm_campaign=b2g"
          className="inline-block bg-brand-navy hover:bg-brand-blue-hover text-white font-semibold px-5 sm:px-6 py-2.5 sm:py-3 rounded-button text-sm sm:text-base transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          Comece Gratis
        </Link>
      </div>

      <h2>Perguntas Frequentes</h2>

      <h3>Quanto custa participar de um pregao eletronico do inicio ao fim?</h3>
      <p>
        O custo total de participacao em um pregao eletronico inclui horas de analise do edital
        (8 a 24 horas de trabalho qualificado), emissao e renovacao de certidoes (R$ 200 a
        R$ 1.500 por processo), elaboracao da proposta (4 a 16 horas), acompanhamento da sessao
        publica e eventuais recursos. Considerando o custo-hora de profissionais de licitacao
        (R$ 45 a R$ 80/hora), cada participacao custa entre R$ 1.800 e R$ 6.500 em recursos
        diretos, antes de considerar custos de garantia e custo de oportunidade.
      </p>

      <h3>Qual a taxa media de vitoria em pregoes eletronicos no Brasil?</h3>
      <p>
        A taxa media de adjudicacao em pregoes eletronicos no Brasil situa-se entre 8% e 15%,
        segundo dados de mercado e analises do Painel de Compras Governamentais. Isso significa
        que uma empresa que participa de 20 pregoes por ano pode esperar vencer entre 1 e 3,
        dependendo do setor e da qualidade da sua selecao de editais. Empresas com processos
        estruturados de triagem alcancam taxas entre 20% e 35%.
      </p>

      <h3>Como identificar um pregao que nao vale a pena disputar?</h3>
      <p>
        Os principais indicadores de um pregao de baixa viabilidade sao: objeto com baixo
        alinhamento setorial, valor estimado fora da faixa de competitividade da empresa,
        requisitos de habilitacao que exigem atestados ou qualificacoes que a empresa nao
        possui, prazo de entrega incompativel com a capacidade operacional, e historico do
        orgao contratante com atraso de pagamento. Ferramentas de analise de viabilidade
        podem avaliar esses criterios automaticamente.
      </p>

      <h3>Qual o custo de oportunidade de disputar pregoes errados?</h3>
      <p>
        O custo de oportunidade e o custo mais significativo e mais dificil de mensurar. Cada
        hora investida em um pregao sem viabilidade e uma hora que poderia ser dedicada a um
        edital com alta probabilidade de vitoria. Em termos praticos, uma empresa que
        desperdicou 200 horas anuais em pregoes que perdeu poderia ter alocado esse tempo
        para elaborar propostas mais competitivas para editais com maior alinhamento,
        potencialmente gerando 2 a 4 contratos adicionais.
      </p>
    </>
  );
}
