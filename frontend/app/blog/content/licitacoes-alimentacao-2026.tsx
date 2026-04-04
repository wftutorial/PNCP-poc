import Link from 'next/link';
import BlogInlineCTA from '../components/BlogInlineCTA';

/**
 * SEO GUIA-S5: Licitacoes de Alimentacao 2026 — Guia Completo
 *
 * Content cluster: guias setoriais
 * Target: 3,000+ words | Primary KW: licitacoes alimentacao
 */
export default function LicitacoesAlimentacao2026() {
  return (
    <>
      {/* FAQPage JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: [
              {
                '@type': 'Question',
                name: 'O que é o PNAE e como participar?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'O Programa Nacional de Alimentação Escolar (PNAE) é o maior programa de alimentação escolar do mundo, atendendo mais de 40 milhões de estudantes em escolas públicas. O programa é gerido pelo FNDE (Fundo Nacional de Desenvolvimento da Educação) e executado por estados e municípios. Para participar como fornecedor, a empresa deve se cadastrar junto à prefeitura ou secretaria de educação, atender às exigências sanitárias (alvará, registro no MAPA quando aplicável) e participar de chamadas públicas (para agricultura familiar) ou pregões eletrônicos (para grandes fornecedores). Pelo menos 30% das compras do PNAE devem ser da agricultura familiar.',
                },
              },
              {
                '@type': 'Question',
                name: 'Agricultores familiares podem vender para o governo?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Sim, e há prioridade legal para isso. A Lei 11.947/2009 determina que pelo menos 30% dos recursos do PNAE sejam utilizados na aquisição de alimentos da agricultura familiar, priorizando assentamentos da reforma agrária, comunidades tradicionais, quilombolas e indígenas. A modalidade é a chamada pública (não é licitação convencional), com processo simplificado. O agricultor precisa possuir DAP (Declaração de Aptidão ao Pronaf) ou CAF (Cadastro Nacional da Agricultura Familiar) e estar vinculado a uma cooperativa ou associação.',
                },
              },
              {
                '@type': 'Question',
                name: 'Quais certificações sanitárias são obrigatórias?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'As certificações variam conforme o tipo de alimento. Para alimentos industrializados: registro no MAPA (Ministério da Agricultura) ou na Anvisa, alvará sanitário e Certificado de Boas Práticas de Fabricação. Para refeições prontas: alvará sanitário, registro no CRN (Conselho Regional de Nutricionistas) do responsável técnico, e Manual de Boas Práticas (MBP) com POPs (Procedimentos Operacionais Padronizados). Para agricultura familiar: DAP/CAF, certificação orgânica (se aplicável) e alvará sanitário municipal para produtos beneficiados.',
                },
              },
              {
                '@type': 'Question',
                name: 'Como funciona a chamada pública de alimentação escolar?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'A chamada pública é o instrumento de compra da agricultura familiar para o PNAE, regulamentada pela Resolução FNDE 6/2020. Diferente da licitação, na chamada pública os preços são pesquisados previamente pela entidade executora (prefeitura/secretaria) e os fornecedores se habilitam apresentando projeto de venda com os itens que podem fornecer. A prioridade de seleção segue a ordem: local (município), territorial (região), estadual e nacional. Não há disputa de preço — o preço é definido previamente com base em pesquisa de mercado local.',
                },
              },
              {
                '@type': 'Question',
                name: 'Qual o prazo de pagamento em contratos de alimentação?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Para contratos via licitação (pregão), o prazo legal é de até 30 dias após o atesto da nota fiscal (art. 141 da Lei 14.133/2021). Para chamadas públicas do PNAE, o pagamento deve ocorrer em até 30 dias após a entrega. Na prática, os prazos variam: prefeituras de médio e grande porte pagam em 15 a 30 dias; prefeituras menores podem atrasar 30 a 60 dias, especialmente no segundo semestre. O FNDE repassa recursos do PNAE em 10 parcelas anuais, o que pode gerar sazonalidade nos pagamentos municipais.',
                },
              },
              {
                '@type': 'Question',
                name: 'Como calcular preço competitivo para licitação de alimentação?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'O preço competitivo para licitação de alimentação é composto por: custo dos insumos (alimentos, embalagens), custo de mão de obra (cozinheiros, auxiliares, nutricionista — conforme CCT local), custos logísticos (transporte, cadeia fria se aplicável), custos indiretos (energia, água, gás, aluguel de cozinha industrial) e BDI (15% a 22%). Para refeições prontas, o custo por refeição é a métrica central. Para fornecimento de gêneros alimentícios, o preço unitário por kg/unidade é comparado com a pesquisa de preços do órgão (CEASA, supermercados, atas vigentes).',
                },
              },
            ],
          }),
        }}
      />

      {/* HowTo JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'HowTo',
            name: 'Como participar de licitações de alimentação em 2026',
            description:
              'Passo a passo para empresas e cooperativas que desejam fornecer alimentos, refeições e merenda escolar ao governo via licitações públicas e chamadas públicas.',
            step: [
              {
                '@type': 'HowToStep',
                name: 'Obtenha as certificações sanitárias',
                text: 'Providencie alvará sanitário, registro no MAPA (para alimentos industrializados) e Manual de Boas Práticas com POPs (para refeições prontas).',
              },
              {
                '@type': 'HowToStep',
                name: 'Defina o canal de venda (licitação ou chamada pública)',
                text: 'Agricultura familiar participa via chamada pública (PNAE). Grandes fornecedores participam via pregão eletrônico. Identifique o canal adequado ao seu porte e tipo de produto.',
              },
              {
                '@type': 'HowToStep',
                name: 'Cadastre-se nos portais e junto aos órgãos compradores',
                text: 'Faça cadastro no PNCP, ComprasGov (SICAF) e junto às secretarias de educação e saúde dos municípios-alvo.',
              },
              {
                '@type': 'HowToStep',
                name: 'Estruture a logística de distribuição',
                text: 'Planeje rotas de entrega, cadeia fria (se necessário) e pontos de distribuição antes de participar. Muitos editais exigem entrega em múltiplas escolas ou unidades.',
              },
              {
                '@type': 'HowToStep',
                name: 'Analise viabilidade e participe',
                text: 'Avalie cada edital considerando volume, faixas de preço, logística de entrega e histórico de pagamento do órgão antes de investir na proposta.',
              },
            ],
          }),
        }}
      />

      {/* Opening paragraph */}
      <p className="text-base sm:text-xl leading-relaxed text-ink">
        O governo brasileiro e o maior comprador de alimentos do pais. Entre
        merenda escolar, refeicoes hospitalares, alimentacao de presos, cestas
        basicas e refeicoes para forcas armadas, as compras publicas de
        alimentacao movimentam mais de <strong>R$ 30 bilhoes por ano</strong>,
        considerando todas as esferas. O Programa Nacional de Alimentacao Escolar
        (PNAE) sozinho destina mais de R$ 5,5 bilhoes anuais para alimentar 40
        milhoes de estudantes em 150 mil escolas publicas. Para empresas,
        cooperativas e agricultores familiares, esse mercado oferece demanda
        constante, contratos recorrentes e pagamento garantido por repasse
        federal. Mas participar com competitividade exige conhecer as regras
        especificas do setor -- da chamada publica ao pregao eletronico, das
        exigencias sanitarias a logistica de distribuicao. Este guia cobre tudo
        o que voce precisa saber sobre licitacoes de alimentacao em 2026.
      </p>

      {/* Section 1: Panorama */}
      <h2>Panorama: o governo como maior comprador de alimentos</h2>

      <p>
        A aquisicao publica de alimentos no Brasil ocorre em tres grandes frentes:
        alimentacao escolar (PNAE), alimentacao hospitalar e institucional
        (hospitais, quarteis, presiidos, universidades) e programas de seguranca
        alimentar (cestas basicas, PAA -- Programa de Aquisicao de Alimentos).
        Cada frente tem regulamentacao, modalidades e publicos-alvo distintos, mas
        todas compartilham uma caracteristica: demanda recorrente e previsivel.
      </p>

      <p>
        O PNAE e o programa de maior escala. Criado em 1955 e atualmente
        regulamentado pela Lei 11.947/2009 e pela Resolucao CD/FNDE 6/2020, o
        programa garante alimentacao a todos os alunos matriculados na educacao
        basica publica. Os recursos sao repassados pelo FNDE diretamente aos
        estados, municipios e ao Distrito Federal, que executam as compras --
        predominantemente via chamada publica (para agricultura familiar) e pregao
        eletronico (para demais fornecedores).
      </p>

      <p>
        Alem do PNAE, hospitais publicos demandam refeicoes prontas e insumos
        alimentares em volume significativo. Um hospital de medio porte (300 leitos)
        serve entre 900 e 1.200 refeicoes por dia, incluindo pacientes, acompanhantes
        e funcionarios. Essa demanda gera contratos de servico de alimentacao (empresa
        fornece refeicao pronta) ou de fornecimento de generos alimenticios (hospital
        produz internamente).
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Dados de referencia -- Compras publicas de alimentacao em numeros
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            <strong>Orcamento PNAE 2025:</strong> R$ 5,5 bilhoes (FNDE), atendendo
            40,1 milhoes de estudantes em 150 mil escolas publicas.
          </li>
          <li>
            <strong>Repasse per capita (PNAE):</strong> R$ 0,36 a R$ 2,00 por aluno/dia,
            variando conforme nivel de ensino (creche recebe o maior valor).
          </li>
          <li>
            <strong>Cota agricultura familiar:</strong> no minimo 30% dos recursos
            do PNAE devem ser gastos com agricultura familiar (Lei 11.947/2009, art. 14).
          </li>
          <li>
            <strong>Publicacoes mensais no PNCP (alimentacao):</strong> 3.000 a 6.000
            editais entre pregoes, chamadas publicas e dispensas.
          </li>
          <li>
            <strong>PAA (Programa de Aquisicao de Alimentos):</strong> R$ 1,5 bilhao
            destinados a compra direta da agricultura familiar para programas
            assistenciais e banco de alimentos.
          </li>
        </ul>
      </div>

      {/* Section 2: Tipos de objeto */}
      <h2>Tipos de objeto: merenda, refeicoes, insumos e cestas basicas</h2>

      <h3>Merenda escolar (PNAE)</h3>

      <p>
        A merenda escolar e o objeto mais volumoso em licitacoes de alimentacao.
        Inclui generos alimenticios in natura (frutas, verduras, legumes, ovos,
        leite), produtos industrializados (arroz, feijao, macarrao, oleo, acucar)
        e, em alguns municipios, refeicoes prontas preparadas por empresas
        terceirizadas. O cardapio e elaborado por nutricionista habilitado e deve
        atender as diretrizes do FNDE (no minimo 20% das necessidades nutricionais
        diarias do aluno).
      </p>

      <p>
        As compras de merenda escolar sao realizadas pelas Entidades Executoras
        (EEx) -- prefeituras, secretarias estaduais de educacao e escolas federais.
        Cada EEx tem autonomia para definir o cardapio, os quantitativos e o
        instrumento de compra, desde que respeite as diretrizes nacionais.
      </p>

      <h3>Refeicoes prontas (alimentacao hospitalar e institucional)</h3>

      <p>
        Contratos de fornecimento de refeicoes prontas sao comuns em hospitais,
        universidades, quarteis, presidios e orgaos com restaurantes internos.
        O objeto tipicamente e: &ldquo;contratacao de empresa especializada na
        prestacao de servicos de alimentacao e nutricao, incluindo preparo,
        distribuicao e higienizacao&rdquo;. O fornecedor assume toda a operacao
        da cozinha, incluindo mao de obra (cozinheiros, nutricionistas,
        auxiliares), insumos e equipamentos.
      </p>

      <p>
        Esses contratos sao de alto valor (R$ 1 a R$ 50 milhoes anuais para
        hospitais de grande porte) e longa duracao (12 a 60 meses). Exigem
        infraestrutura significativa: cozinha industrial, equipamentos, equipe
        qualificada e logistica de distribuicao interna.
      </p>

      <h3>Generos alimenticios (fornecimento de insumos)</h3>

      <p>
        Diferente das refeicoes prontas, aqui o fornecedor entrega os alimentos
        e o orgao prepara internamente. Inclui hortifruti, carnes, laticinios,
        graos, enlatados, congelados e produtos de padaria. As licitacoes
        tipicamente utilizam pregao eletronico com criterio de menor preco por
        item ou por lote, e o fornecimento e parcelado ao longo de meses.
      </p>

      <h3>Cestas basicas e kits alimentacao</h3>

      <p>
        Cestas basicas sao adquiridas por orgaos de assistencia social (CRAS,
        Defesa Civil) para distribuicao a familias em situacao de vulnerabilidade.
        Os kits alimentacao ganharam protagonismo durante a pandemia de COVID-19,
        quando substituiram a merenda escolar para alunos em ensino remoto. Embora
        o volume tenha reduzido apos o retorno as aulas presenciais, dispensas e
        pregoes para cestas basicas continuam frequentes em programas assistenciais.
      </p>

      {/* Section 3: PNAE */}
      <h2>PNAE: como funciona e como participar</h2>

      <p>
        O PNAE merece uma secao dedicada por ser o programa de maior escala e o
        que possui regras mais especificas para fornecedores.
      </p>

      <p>
        <strong>Financiamento:</strong> O FNDE repassa recursos diretamente as
        Entidades Executoras em 10 parcelas anuais (fevereiro a novembro). O
        valor e calculado com base no censo escolar do ano anterior, multiplicado
        pelo per capita de cada etapa de ensino: R$ 0,36 (ensino fundamental e
        medio), R$ 0,53 (pre-escola), R$ 1,07 (creche), R$ 0,64 (EJA), R$ 2,00
        (ensino integral). Municipios e estados devem complementar os recursos
        com contrapartida propria.
      </p>

      <p>
        <strong>Regra dos 30%:</strong> A Lei 11.947/2009 determina que no minimo
        30% dos recursos do PNAE sejam utilizados na compra de alimentos da
        agricultura familiar. Na pratica, muitos municipios superam esse percentual
        (40% a 60%), impulsionados pela qualidade dos produtos locais e pela
        facilidade logistica.
      </p>

      <p>
        <strong>Chamada publica:</strong> A modalidade de compra da agricultura
        familiar nao e licitacao convencional. A chamada publica (Resolucao FNDE
        6/2020, art. 24) funciona assim: o municipio publica um edital com os
        itens necessarios e os precos pesquisados (baseados em CEASA, supermercados
        locais e atas vigentes). Agricultores familiares, cooperativas e associacoes
        se habilitam apresentando projeto de venda. A priorizacao e: fornecedores
        locais (municipio) primeiro, depois territoriais, estaduais e nacionais.
        Nao ha disputa de preco -- o preco e definido previamente.
      </p>

      <p>
        <strong>Pregao para grandes fornecedores:</strong> Os 70% restantes dos
        recursos podem ser adquiridos via pregao eletronico convencional, aberto
        a qualquer empresa. Esses pregoes tipicamente cobrem arroz, feijao, oleo,
        carnes congeladas, laticinios industrializados e outros produtos que a
        agricultura familiar local nao consegue suprir em escala.
      </p>

      <p>
        Para entender o funcionamento do portal onde esses editais sao publicados,
        veja{' '}
        <Link href="/blog/pncp-guia-completo-empresas" className="text-brand-navy dark:text-brand-blue hover:underline">
          o guia completo do PNCP para empresas
        </Link>.
      </p>

      {/* Section 4: Modalidades */}
      <h2>Modalidades de compra em alimentacao</h2>

      <p>
        As licitacoes de alimentacao utilizam predominantemente tres instrumentos:
      </p>

      <p>
        <strong>Chamada publica</strong> (exclusiva para agricultura familiar no
        PNAE): processo simplificado, sem disputa de preco. Os precos sao definidos
        previamente pela Entidade Executora com base em pesquisa de mercado. A
        priorizacao e geográfica: local, territorial, estadual, nacional. A
        documentacao exigida e simplificada (DAP/CAF, documentos pessoais, projeto
        de venda).
      </p>

      <p>
        <strong>Pregao eletronico:</strong> modalidade principal para grandes
        fornecedores. Utilizado para compra de generos alimenticios industrializados,
        carnes, laticinios e para contratacao de servicos de alimentacao (refeicoes
        prontas). Criterio de menor preco. Editais publicados no{' '}
        <Link href="/glossario#pregao-eletronico" className="text-brand-navy dark:text-brand-blue hover:underline">
          PNCP e nos portais de compras estaduais
        </Link>.
      </p>

      <p>
        <strong>Dispensa de licitacao:</strong> para compras de ate R$ 59.906,02
        (art. 75, II da Lei 14.133/2021). Comum em municipios pequenos que precisam
        complementar itens de merenda de forma urgente ou em quantidades reduzidas.
        Tambem utilizada em situacoes de emergencia alimentar. Dispensas representam
        cerca de 20% das compras de alimentacao no PNCP.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Faixas de valor tipicas -- Licitacoes de alimentacao
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            <strong>Merenda escolar (municipio pequeno):</strong> R$ 20.000 a
            R$ 200.000 por chamada publica ou pregao. Municipios com menos de
            20 mil habitantes.
          </li>
          <li>
            <strong>Merenda escolar (municipio medio/grande):</strong> R$ 200.000 a
            R$ 5.000.000. Capitais e cidades com mais de 100 mil habitantes.
          </li>
          <li>
            <strong>Merenda escolar (secretaria estadual):</strong> R$ 1.000.000 a
            R$ 50.000.000. Atas de registro de preco para rede estadual completa.
          </li>
          <li>
            <strong>Refeicoes hospitalares:</strong> R$ 500.000 a R$ 50.000.000 por
            ano. Varia conforme porte do hospital e numero de refeicoes/dia.
          </li>
          <li>
            <strong>Cestas basicas (assistencia social):</strong> R$ 10.000 a
            R$ 500.000. Compras pontuais para distribuicao emergencial.
          </li>
          <li>
            <strong>Alimentacao militar/prisional:</strong> R$ 1.000.000 a
            R$ 30.000.000. Contratos de grande porte com requisitos especificos
            de seguranca.
          </li>
        </ul>
      </div>

      {/* Section 5: UFs com maior volume */}
      <h2>UFs com maior volume de licitacoes de alimentacao</h2>

      <p>
        O volume de compras de alimentacao esta correlacionado com o numero de
        alunos matriculados (PNAE), o tamanho da rede hospitalar e a populacao
        em situacao de vulnerabilidade (programas assistenciais).
      </p>

      <p>
        <strong>Sao Paulo</strong> lidera de forma expressiva: maior rede escolar
        do pais (mais de 5,3 milhoes de alunos na rede estadual e municipal),
        maior rede hospitalar e maior numero de CRAS. O orcamento do PNAE
        paulista supera R$ 800 milhoes anuais somando estado e municipios.
      </p>

      <p>
        <strong>Minas Gerais</strong>, com 853 municipios, gera o maior numero
        de chamadas publicas individuais -- cada municipio realiza suas proprias
        compras de merenda. <strong>Bahia</strong> e <strong>Maranhao</strong>
        concentram volumes expressivos de compras do PNAE e programas assistenciais,
        impulsionados pela alta demanda de seguranca alimentar. <strong>Rio Grande
        do Sul</strong> e <strong>Parana</strong> se destacam pela forte participacao
        da agricultura familiar, com cooperativas organizadas e alto percentual de
        compras via chamada publica.
      </p>

      <p>
        Fornecedores de generos alimenticios industrializados encontram as maiores
        oportunidades em capitais e regioes metropolitanas. Ja cooperativas de
        agricultura familiar tem vantagem em municipios menores, onde a logistica
        local e o conhecimento do mercado regional sao diferenciais decisivos.
      </p>

      {/* Section 6: Requisitos */}
      <h2>Requisitos: alvara sanitario, registro no MAPA e boas praticas</h2>

      <p>
        O setor de alimentacao e fortemente regulado por normas sanitarias.
        Os requisitos variam conforme o tipo de produto e o canal de venda.
      </p>

      <h3>Para generos alimenticios industrializados</h3>

      <p>
        Registro do produto no MAPA (Ministerio da Agricultura, Pecuaria e
        Abastecimento) para produtos de origem animal (carnes, laticinios, ovos
        industrializados) ou na Anvisa para demais alimentos industrializados.
        Alvara sanitario da vigilancia sanitaria municipal ou estadual. SIF
        (Servico de Inspecao Federal) ou SIE/SIM (Inspecao Estadual/Municipal)
        para produtos de origem animal. CNPJ com CNAE compativel (4639-7/01 --
        comercio atacadista de produtos alimenticios em geral, ou CNAEs
        especificos conforme o tipo de alimento).
      </p>

      <h3>Para refeicoes prontas (servicos de alimentacao)</h3>

      <p>
        Alvara sanitario da cozinha industrial. Responsavel tecnico nutricionista
        com CRN ativo. Manual de Boas Praticas de Fabricacao (MBP) e Procedimentos
        Operacionais Padronizados (POPs) conforme RDC 216/2004 da Anvisa. Atestados
        de capacidade tecnica comprovando fornecimento anterior de refeicoes em
        escala compativel. Registro no CNPJ com CNAE 5620-1/01 (fornecimento de
        alimentos preparados preponderantemente para empresas) ou 5620-1/02
        (servicos de alimentacao para eventos e recepcoes).
      </p>

      <h3>Para agricultura familiar (PNAE)</h3>

      <p>
        DAP (Declaracao de Aptidao ao Pronaf) ou CAF (Cadastro Nacional da
        Agricultura Familiar) ativo. Vinculacao a cooperativa ou associacao
        (para vendas acima do limite individual de R$ 40.000 por DAP/ano).
        Alvara sanitario municipal para produtos beneficiados (geleias, queijos
        artesanais, conservas). Certificacao organica (se o produto for ofertado
        como organico). Projeto de venda detalhando itens, quantidades, cronograma
        de entrega e preco.
      </p>

      {/* CTA at ~40% */}
      <BlogInlineCTA
        slug="licitacoes-alimentacao-2026"
        campaign="guias"
        ctaHref="/explorar"
        ctaText="Explorar licitacoes gratis"
        ctaMessage="Descubra editais abertos no seu setor — busca gratuita"
      />

      {/* Section 7: Logistica */}
      <h2>Logistica: o desafio da distribuicao para multiplos pontos</h2>

      <p>
        A logistica e o fator que mais diferencia fornecedores de alimentacao
        bem-sucedidos dos que acumulam sancoes contratuais. Diferente de outros
        setores onde a entrega e centralizada (almoxarifado unico), compras de
        alimentacao frequentemente exigem entrega em dezenas ou centenas de pontos
        distintos.
      </p>

      <p>
        No PNAE, a entrega tipicamente ocorre diretamente nas escolas. Um municipio
        de 100 mil habitantes pode ter 40 a 80 escolas, cada uma com cronograma e
        cardapio proprios. O fornecedor precisa de frota (propria ou terceirizada),
        roteirizacao eficiente e capacidade de adaptar entregas semanais conforme
        o cardapio. Em regioes rurais, escolas podem estar a dezenas de quilometros
        da sede do municipio, em estradas nao pavimentadas.
      </p>

      <p>
        Para refeicoes hospitalares, a logistica e interna (a empresa opera a
        cozinha do hospital), mas a complexidade esta na escala: 1.000+ refeicoes
        por dia com exigencias nutricionais especificas para cada paciente (dieta
        normal, hipossodica, pastosa, liquida, enteral). A operacao funciona 365
        dias por ano, incluindo feriados, com margem zero para interrupcao.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Desafios logisticos por tipo de contrato
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            <strong>Merenda escolar:</strong> 40 a 200 pontos de entrega por municipio,
            frequencia semanal ou quinzenal, produtos pereciveis exigem cadeia fria
            parcial (hortifruti, carnes, laticinios).
          </li>
          <li>
            <strong>Refeicoes hospitalares:</strong> operacao 24/7, dietas especiais,
            controle rigoroso de temperatura (hot holding e cold holding), rastreabilidade
            por paciente.
          </li>
          <li>
            <strong>Cestas basicas:</strong> entrega pontual em CRAS, centros comunitarios
            ou diretamente a familias. Volume concentrado em periodos especificos
            (enchentes, secas, calamidades).
          </li>
          <li>
            <strong>Alimentacao militar:</strong> pontos de entrega em quarteis e bases,
            frequentemente em areas de dificil acesso. Requisitos de seguranca para
            acesso as instalacoes.
          </li>
        </ul>
      </div>

      <p>
        Empresas que mapeiam a logistica antes de participar da licitacao tem
        vantagem competitiva significativa. Isso inclui: levantar o numero
        e localizacao dos pontos de entrega (disponivel no edital), calcular o
        custo de frete por rota, verificar a disponibilidade de veiculos
        refrigerados (quando necessario) e negociar com transportadoras locais
        antes de formular o preco. Um estudo logistico previo de 4 a 8 horas pode
        evitar prejuizos de dezenas de milhares de reais ao longo do contrato.
      </p>

      {/* Section 8: Erros comuns */}
      <h2>Erros comuns em licitacoes de alimentacao</h2>

      <h3>Erro 1: Ignorar a validade (shelf life) dos produtos</h3>

      <p>
        Editais de alimentacao frequentemente exigem que produtos industrializados
        tenham validade minima no momento da entrega (tipicamente 2/3 da validade
        total). Um arroz com validade de 12 meses deve ser entregue com no minimo
        8 meses de validade restante. Fornecedores que mantem estoque antigo ou
        compram lotes proximos do vencimento para obter precos menores sao
        surpreendidos na hora da entrega, quando o fiscal rejeita o produto.
        A consequencia e substituicao as custas do fornecedor, multa contratual
        e registro negativo no SICAF.
      </p>

      <h3>Erro 2: Falha na cadeia fria</h3>

      <p>
        Carnes, laticinios, hortifruti e refeicoes prontas exigem controle de
        temperatura durante todo o transporte. Editais especificam faixas de
        temperatura (carne congelada: -18 graus Celsius; resfriados: 0 a 5 graus;
        hortifruti: 8 a 12 graus). A entrega em veiculo sem refrigeracao ou com
        refrigeracao insuficiente resulta em rejeicao imediata. Investir em
        veiculos refrigerados ou em parceria com transportadora especializada e
        prerequisito para atuar nesse segmento.
      </p>

      <h3>Erro 3: Transporte inadequado</h3>

      <p>
        Alem da temperatura, a legislacao sanitaria (RDC 216/2004) exige que o
        transporte de alimentos seja feito em veiculos limpos, exclusivos para
        alimentos (nao compartilhados com produtos quimicos ou outros materiais),
        com bau fechado e em boas condicoes de higiene. Fiscais sanitarios podem
        vistoriar o veiculo no momento da entrega e rejeitar o carregamento se
        as condicoes nao forem adequadas.
      </p>

      <h3>Erro 4: Nao acompanhar a sazonalidade de precos</h3>

      <p>
        Precos de hortifruti e proteinas animais variam significativamente ao
        longo do ano. Um pregao vencido em janeiro com preco de tomate a R$ 3/kg
        pode se tornar inviavel em julho quando o preco sobe para R$ 8/kg. Editais
        com{' '}
        <Link href="/glossario#ata-de-registro-de-precos" className="text-brand-navy dark:text-brand-blue hover:underline">
          ata de registro de precos
        </Link>{' '}
        de 12 meses sao especialmente arriscados para itens com alta volatilidade.
        A recomendacao e incluir margem de seguranca na proposta para absorver
        variacao sazonal ou negociar clausula de reequilibrio economico-financeiro
        no contrato.
      </p>

      <h3>Erro 5: Subestimar os requisitos nutricionais</h3>

      <p>
        Editais de merenda escolar exigem que os alimentos atendam a parametros
        nutricionais especificos (calorias, macronutrientes, sodio, acucar).
        Fornecedores que oferecem produtos fora das especificacoes nutricionais
        (por exemplo, suco com teor de fruta abaixo do minimo exigido, ou biscoito
        com excesso de sodio) tem a entrega rejeitada. Verifique as fichas
        tecnicas dos seus produtos antes de participar. Para entender como
        outros setores lidam com especificacoes tecnicas, veja{' '}
        <Link href="/blog/licitacoes-saude-2026" className="text-brand-navy dark:text-brand-blue hover:underline">
          o guia de licitacoes de saude 2026
        </Link>.
      </p>

      {/* Section 9: Como calcular preco */}
      <h2>Como calcular preco competitivo para licitacao de alimentacao</h2>

      <p>
        A formacao de preco em alimentacao varia conforme o tipo de objeto.
      </p>

      <p>
        <strong>Para generos alimenticios:</strong> O preco unitario (por kg,
        litro ou unidade) e comparado com a pesquisa de precos do orgao, que
        tipicamente utiliza tres fontes: CEASA regional, supermercados locais
        e atas de registro de preco vigentes. O fornecedor precisa operar com
        margem entre 8% e 18% sobre o custo de aquisicao, dependendo do volume
        e da logistica.
      </p>

      <p>
        <strong>Para refeicoes prontas:</strong> O custo por refeicao e a metrica
        central. Inclui insumos alimentares (40% a 55% do custo), mao de obra
        (30% a 40%), equipamentos e utensilios (5% a 8%), energia e gas (3% a 5%),
        e BDI (15% a 22%). O preco medio de uma refeicao pronta em licitacoes
        publicas varia entre R$ 12 e R$ 35, dependendo da composicao do cardapio,
        da regiao e do volume diario.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Exemplo -- Composicao de custo por refeicao hospitalar
        </p>
        <ul className="space-y-1.5 text-sm text-ink-secondary">
          <li>
            <strong>Insumos alimentares:</strong> R$ 9,50 (proteina + guarnição
            + acompanhamento + salada + sobremesa + suco)
          </li>
          <li>
            <strong>Mao de obra (proporcional):</strong> R$ 6,80 (cozinheiro,
            auxiliares, nutricionista, copeiras)
          </li>
          <li>
            <strong>Energia, gas, agua:</strong> R$ 1,20
          </li>
          <li>
            <strong>Equipamentos (depreciacao):</strong> R$ 0,80
          </li>
          <li>
            <strong>Descartaveis e embalagens:</strong> R$ 0,60
          </li>
          <li>
            <strong>Custos indiretos:</strong> R$ 1,50
          </li>
          <li>
            <strong>BDI (18%):</strong> R$ 3,67
          </li>
          <li className="pt-2 font-semibold">
            Custo total por refeicao: R$ 24,07
          </li>
        </ul>
      </div>

      <p>
        Para chamadas publicas do PNAE, o preco nao e disputado -- ele e definido
        pela Entidade Executora com base em pesquisa de mercado. O fornecedor
        aceita ou nao o preco oferecido. Por isso, a competitividade na chamada
        publica nao esta no preco, mas na capacidade de entrega (pontualidade,
        qualidade, variedade) e na priorizacao geografica (local primeiro).
        Entender como a licitacao funciona como{' '}
        <Link href="/blog/como-participar-primeira-licitacao-2026" className="text-brand-navy dark:text-brand-blue hover:underline">
          processo completo para iniciantes
        </Link>{' '}
        pode ajudar a estruturar sua participacao.
      </p>

      {/* Section 10: Tendencias 2026 */}
      <h2>Tendencias para licitacoes de alimentacao em 2026</h2>

      <p>
        <strong>Preferencia por organicos e agroecologicos:</strong> A Resolucao
        FNDE 6/2020 prioriza alimentos organicos e agroecologicos nas compras do
        PNAE, permitindo acrescimo de ate 30% no preco em relacao ao convencional.
        Cooperativas com certificacao organica estao em posicao vantajosa.
      </p>

      <p>
        <strong>Rastreabilidade exigida:</strong> Editais de grande porte estao
        incorporando exigencias de rastreabilidade da cadeia produtiva, incluindo
        origem dos ingredientes, condições de transporte e certificacoes de
        sustentabilidade. A tecnologia blockchain para rastreabilidade alimentar
        comeca a aparecer em editais de dialogos competitivos.
      </p>

      <p>
        <strong>Reducao de ultraprocessados:</strong> O Guia Alimentar para a
        Populacao Brasileira (Ministerio da Saude) orienta a reducao de alimentos
        ultraprocessados na alimentacao escolar. Editais estao gradualmente
        eliminando itens como biscoitos recheados, salgadinhos e bebidas
        acucaradas, privilegiando alimentos in natura e minimamente processados.
        Isso beneficia fornecedores de hortifruti e agricultura familiar.
      </p>

      <p>
        <strong>Compras institucionais via PAA:</strong> O Programa de Aquisicao
        de Alimentos (PAA) esta sendo ampliado, com orcamento crescente para
        compra direta da agricultura familiar destinada a hospitais, restaurantes
        populares e bancos de alimentos. Cooperativas ja cadastradas no PNAE
        podem expandir atuacao para o PAA com documentacao similar.
      </p>

      {/* CTA Section */}
      <div className="not-prose mt-8 sm:mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-xl p-5 sm:p-8 text-center border border-brand-blue/20">
        <p className="text-lg sm:text-xl font-bold text-ink mb-2">
          Monitore editais de alimentacao com o SmartLic -- 14 dias gratis
        </p>
        <p className="text-sm sm:text-base text-ink-secondary mb-4 sm:mb-6 max-w-lg mx-auto">
          O SmartLic agrega editais do PNCP e classifica por setor usando IA.
          Encontre pregoes de merenda escolar, refeicoes hospitalares e
          fornecimento de generos alimenticios compativeis com seu perfil.
        </p>
        <Link
          href="/signup?source=blog&article=licitacoes-alimentacao-2026&utm_source=blog&utm_medium=cta&utm_content=licitacoes-alimentacao-2026&utm_campaign=guias"
          className="inline-block bg-brand-navy hover:bg-brand-blue-hover text-white font-semibold px-5 sm:px-6 py-2.5 sm:py-3 rounded-button text-sm sm:text-base transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          Teste Gratis por 14 Dias
        </Link>
        <p className="text-xs text-ink-secondary mt-3">
          Sem cartao de credito. Veja todas as funcionalidades na{' '}
          <Link href="/features" className="underline hover:text-ink">
            pagina de recursos
          </Link>.
        </p>
      </div>

      {/* FAQ Section */}
      <h2>Perguntas Frequentes</h2>

      <h3>O que e o PNAE e como participar?</h3>
      <p>
        O Programa Nacional de Alimentacao Escolar (PNAE) e o maior programa de
        alimentacao escolar do mundo, atendendo mais de 40 milhoes de estudantes.
        E gerido pelo FNDE e executado por estados e municipios. Para participar
        como fornecedor, cadastre-se junto a prefeitura ou secretaria de educacao,
        atenda as exigencias sanitarias e participe de chamadas publicas (se
        agricultura familiar) ou pregoes eletronicos (demais fornecedores). No
        minimo 30% das compras devem vir da agricultura familiar, conforme a
        Lei 11.947/2009.
      </p>

      <h3>Agricultores familiares podem vender para o governo?</h3>
      <p>
        Sim, e ha prioridade legal. A Lei 11.947/2009 reserva no minimo 30% dos
        recursos do PNAE para a agricultura familiar. A modalidade e a chamada
        publica (processo simplificado, sem disputa de preco). O agricultor precisa
        possuir DAP ou CAF e estar vinculado a cooperativa ou associacao para vendas
        acima de R$ 40.000 por DAP/ano. A priorizacao e geografica: fornecedores
        locais (mesmo municipio) tem preferencia sobre fornecedores de outras regioes.
        Alem do PNAE, o PAA tambem compra da agricultura familiar para programas
        assistenciais.
      </p>

      <h3>Quais certificacoes sanitarias sao obrigatorias?</h3>
      <p>
        Para alimentos industrializados: registro no MAPA ou Anvisa, alvara sanitario
        e Certificado de Boas Praticas. Para refeicoes prontas: alvara sanitario,
        nutricionista com CRN ativo, Manual de Boas Praticas (MBP) e POPs conforme
        RDC 216/2004. Para agricultura familiar: DAP/CAF, alvara sanitario municipal
        para produtos beneficiados, e certificacao organica se aplicavel. Produtos
        de origem animal exigem SIF, SIE ou SIM conforme o ambito de comercializacao.
      </p>

      <h3>Como funciona a chamada publica de alimentacao escolar?</h3>
      <p>
        A chamada publica (Resolucao FNDE 6/2020) e o instrumento de compra da
        agricultura familiar para o PNAE. O municipio publica edital com itens e
        precos pesquisados previamente. Fornecedores se habilitam com projeto de
        venda. Nao ha disputa de preco -- o preco e definido pela pesquisa de
        mercado (CEASA, supermercados, atas). A selecao prioriza: local (municipio),
        territorial, estadual, nacional. O processo e mais simples que uma licitacao
        convencional, com{' '}
        <Link href="/glossario#dispensa" className="text-brand-navy dark:text-brand-blue hover:underline">
          requisitos de documentacao reduzidos
        </Link>.
      </p>

      <h3>Qual o prazo de pagamento em contratos de alimentacao?</h3>
      <p>
        O prazo legal e de ate 30 dias apos o atesto (Lei 14.133/2021, art. 141).
        Na pratica, prefeituras de medio e grande porte pagam em 15 a 30 dias.
        Prefeituras menores podem atrasar 30 a 60 dias, especialmente no segundo
        semestre. O FNDE repassa recursos do PNAE em 10 parcelas anuais (fevereiro
        a novembro), o que pode gerar sazonalidade. Contratos hospitalares federais
        sao mais pontuais (25 a 35 dias). Verificar o historico de pagamento no
        Portal da Transparencia antes de participar e pratica recomendada.
      </p>

      <h3>Como calcular preco competitivo para licitacao de alimentacao?</h3>
      <p>
        Para generos alimenticios, o preco unitario deve ser competitivo em relacao
        a pesquisa do orgao (CEASA, supermercados, atas vigentes), com margem de
        8% a 18% sobre o custo de aquisicao. Para refeicoes prontas, componha o
        custo por refeicao: insumos (40-55%), mao de obra (30-40%), energia e
        equipamentos (8-13%) e BDI (15-22%). Considere a sazonalidade de precos
        de hortifruti e proteinas, e inclua margem de seguranca para itens
        volateis. Compare seu preco final com atas vigentes no PNCP para validar
        competitividade antes de apresentar a proposta.
      </p>
    </>
  );
}
