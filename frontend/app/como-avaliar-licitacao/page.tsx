import { Metadata } from 'next';
import ContentPageLayout from '../components/ContentPageLayout';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Como avaliar se uma licitacao vale a pena? | SmartLic',
  description:
    'Aprenda os 5 criterios praticos para avaliar se uma licitacao publica vale o investimento de tempo e recursos da sua empresa.',
  alternates: {
    canonical: 'https://smartlic.tech/como-avaliar-licitacao',
  },
};

const articleSchema = {
  '@context': 'https://schema.org',
  '@type': 'Article',
  headline: 'Como avaliar se uma licitacao vale a pena?',
  description:
    'Criterios praticos para avaliar se uma licitacao publica vale o investimento de tempo e recursos.',
  author: {
    '@type': 'Organization',
    name: 'SmartLic',
    url: 'https://smartlic.tech',
  },
  publisher: {
    '@type': 'Organization',
    name: 'SmartLic',
    logo: {
      '@type': 'ImageObject',
      url: 'https://smartlic.tech/logo.png',
    },
  },
  datePublished: '2026-02-22',
  dateModified: '2026-02-22',
  mainEntityOfPage: {
    '@type': 'WebPage',
    '@id': 'https://smartlic.tech/como-avaliar-licitacao',
  },
};

const breadcrumbSchema = {
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    {
      '@type': 'ListItem',
      position: 1,
      name: 'Inicio',
      item: 'https://smartlic.tech',
    },
    {
      '@type': 'ListItem',
      position: 2,
      name: 'Como avaliar uma licitacao',
      item: 'https://smartlic.tech/como-avaliar-licitacao',
    },
  ],
};

const RELATED_PAGES = [
  {
    href: '/como-evitar-prejuizo-licitacao',
    title: 'Como evitar prejuizo em licitacoes',
  },
  {
    href: '/como-filtrar-editais',
    title: 'Como filtrar editais de licitacao',
  },
  {
    href: '/como-priorizar-oportunidades',
    title: 'Como priorizar oportunidades',
  },
];

export default function ComoAvaliarLicitacao() {
  return (
    <ContentPageLayout
      breadcrumbLabel="Como avaliar uma licitacao"
      relatedPages={RELATED_PAGES}
    >
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />

      <h1>Como avaliar se uma licitacao vale a pena?</h1>

      <p className="lead text-lg">
        Toda empresa que atua no mercado publico ja enfrentou a mesma situacao:
        investir semanas preparando uma proposta para uma licitacao que, no
        final, nao fazia sentido. O custo de participar de uma licitacao errada
        vai alem do dinheiro gasto com documentacao e certidoes — inclui o tempo
        da equipe, o desgaste operacional e a oportunidade perdida de focar em
        editais melhores.
      </p>

      <p>
        A diferenca entre empresas que crescem de forma consistente no mercado
        B2G e as que vivem de resultados esporadicos geralmente esta na
        capacidade de <strong>avaliar antes de participar</strong>. Neste guia,
        voce vai conhecer 5 criterios praticos que podem ser aplicados a
        qualquer edital para determinar se ele vale o investimento.
      </p>

      <h2>1. Compatibilidade setorial</h2>

      <p>
        O primeiro filtro e o mais obvio, mas frequentemente ignorado por conta
        da pressao por volume: <strong>o edital e do seu segmento?</strong>
      </p>

      <p>
        Muitas empresas tentam participar de licitacoes tangenciais ao seu ramo
        de atividade, acreditando que a diversificacao aumenta as chances. Na
        pratica, o resultado e o oposto. Editais fora do seu setor principal
        exigem adaptacoes tecnicas, equipes que voce nao tem, e referencias que
        nao pode comprovar.
      </p>

      <p>
        <strong>Como avaliar:</strong> verifique se o objeto da licitacao esta
        diretamente relacionado ao seu CNAE principal e se voce possui atestados
        de capacidade tecnica compativeis. Se precisar subcontratar mais de 30%
        do escopo, provavelmente nao e para voce.
      </p>

      <h2>2. Faixa de valor</h2>

      <p>
        O valor estimado da licitacao precisa estar na faixa em que sua empresa
        opera com conforto. Uma empresa acostumada a contratos de R$ 200 mil
        participar de uma licitacao de R$ 5 milhoes enfrenta desafios de
        garantia, capital de giro e capacidade de execucao que podem
        inviabilizar o contrato mesmo em caso de vitoria.
      </p>

      <p>
        Da mesma forma, licitacoes com valor muito baixo podem nao justificar o
        custo de preparacao da proposta. O tempo gasto montando documentacao
        para um pregao de R$ 15 mil e praticamente o mesmo de um de R$ 500 mil.
      </p>

      <p>
        <strong>Como avaliar:</strong> defina a faixa de valor ideal para sua
        empresa considerando porte, capital de giro e historico de contratos
        executados. Foque em editais que estejam entre 50% e 300% do seu
        contrato medio.
      </p>

      <h2>3. Prazo para preparacao</h2>

      <p>
        Uma licitacao com prazo de entrega de propostas em 5 dias uteis exige
        uma analise completamente diferente de uma com 30 dias. O prazo
        determina se ha tempo para:
      </p>

      <ul>
        <li>Analisar o edital completo e seus anexos</li>
        <li>Solicitar esclarecimentos (se necessario)</li>
        <li>Obter certidoes e documentos atualizados</li>
        <li>Elaborar a proposta tecnica e comercial</li>
        <li>Revisar e validar internamente</li>
      </ul>

      <p>
        <strong>Como avaliar:</strong> se o prazo restante nao permite cumprir
        todas as etapas acima com qualidade, o risco de apresentar uma proposta
        incompleta ou com erros e alto.{' '}
        <Link href="/como-evitar-prejuizo-licitacao">
          Propostas apressadas sao uma das principais causas de prejuizo em
          licitacoes
        </Link>
        .
      </p>

      <h2>4. Viabilidade geografica</h2>

      <p>
        A localizacao do orgao contratante impacta diretamente a viabilidade
        operacional e financeira do contrato. Uma empresa sediada em Sao Paulo
        que vence uma licitacao para fornecimento continuo no Amazonas precisa
        considerar custos de logistica, deslocamento de equipe e tempo de
        resposta.
      </p>

      <p>
        <strong>Como avaliar:</strong> calcule o custo logistico real (frete,
        deslocamento, hospedagem) e inclua na analise de margem. Se o custo
        logistico consome mais de 15% da margem esperada, a viabilidade fica
        comprometida.
      </p>

      <h2>5. Modalidade e competicao</h2>

      <p>
        A modalidade da licitacao define as regras do jogo. Um pregao eletronico
        com criterio de menor preco tende a uma competicao acirrada por
        centavos. Uma concorrencia com tecnica e preco valoriza diferenciais
        qualitativos. Um dialogo competitivo permite propor solucoes inovadoras.
      </p>

      <p>
        <strong>Como avaliar:</strong> identifique a modalidade e o criterio de
        julgamento. Se e um pregao por menor preco no seu setor mais
        competitivo, a margem sera apertada. Se inclui avaliacao tecnica, suas
        certificacoes e experiencia comprovada se tornam vantagem.{' '}
        <Link href="/como-priorizar-oportunidades">
          Entenda como priorizar oportunidades com base nesses criterios
        </Link>
        .
      </p>

      <h2>Exemplo pratico: analise de uma licitacao real</h2>

      <p>
        Considere o seguinte cenario: Pregao Eletronico para aquisicao de
        equipamentos de informatica para um hospital universitario, valor
        estimado de R$ 1,2 milhao, em Minas Gerais, com prazo de 18 dias para
        submissao.
      </p>

      <p>Para uma empresa de TI sediada em Belo Horizonte:</p>

      <ul>
        <li>
          <strong>Compatibilidade setorial:</strong> Alta — equipamentos de
          informatica e o core business
        </li>
        <li>
          <strong>Faixa de valor:</strong> Adequada — dentro do historico de
          contratos da empresa (R$ 500k a R$ 2M)
        </li>
        <li>
          <strong>Prazo:</strong> Suficiente — 18 dias permitem analise
          completa e elaboracao de proposta
        </li>
        <li>
          <strong>Geografia:</strong> Viavel — mesma UF, custo logistico
          minimo
        </li>
        <li>
          <strong>Modalidade:</strong> Pregao eletronico (menor preco) —
          competicao previsivel, margens conhecidas
        </li>
      </ul>

      <p>
        <strong>Resultado:</strong> 5 de 5 criterios positivos. Esta e uma
        licitacao que merece dedicacao total da equipe. Agora compare com uma
        licitacao de obras civis de R$ 8 milhoes no Acre para a mesma empresa —
        nenhum criterio seria atendido.
      </p>

      <h2>O custo de avaliar manualmente</h2>

      <p>
        Aplicar esses 5 criterios a cada edital leva entre 30 e 60 minutos. Com
        milhares de licitacoes publicadas diariamente nos portais PNCP,
        ComprasGov e Portal de Compras Publicas, uma analise manual e
        simplesmente inviavel para quem quer cobrir todo o territorio nacional.
      </p>

      <p>
        E exatamente esse o problema que ferramentas de inteligencia em
        licitacoes resolvem: automatizar a triagem inicial para que sua equipe
        foque apenas nos editais que realmente valem a pena.{' '}
        <Link href="/como-filtrar-editais">
          Veja como funciona a filtragem inteligente de editais
        </Link>
        .
      </p>

      {/* CTA Section */}
      <div className="not-prose mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-lg p-8 text-center border border-brand-blue/20">
        <p className="text-lg font-semibold text-ink mb-2">
          Descubra quais licitacoes valem a pena para o seu setor
        </p>
        <p className="text-ink-secondary mb-6">
          O SmartLic aplica esses 5 criterios automaticamente a cada edital,
          usando IA e dados de 3 fontes oficiais.
        </p>
        <Link
          href="/signup?source=content-avaliar"
          className="inline-block bg-brand-navy hover:bg-brand-blue-hover text-white font-semibold px-6 py-3 rounded-button transition-all hover:scale-[1.02] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2"
        >
          Comece Gratis
        </Link>
      </div>
    </ContentPageLayout>
  );
}
