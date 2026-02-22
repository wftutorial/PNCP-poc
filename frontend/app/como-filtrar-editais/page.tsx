import { Metadata } from 'next';
import ContentPageLayout from '../components/ContentPageLayout';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Como filtrar editais de licitacao e focar no que importa | SmartLic',
  description:
    'Entenda por que a busca manual de editais nao funciona e como um filtro inteligente transforma 1.500 publicacoes em 12 oportunidades relevantes.',
  alternates: {
    canonical: 'https://smartlic.tech/como-filtrar-editais',
  },
};

const articleSchema = {
  '@context': 'https://schema.org',
  '@type': 'Article',
  headline: 'Como filtrar editais de licitacao e focar no que importa',
  description:
    'Por que a busca manual de editais nao funciona e como um filtro inteligente transforma milhares de publicacoes em oportunidades relevantes.',
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
    '@id': 'https://smartlic.tech/como-filtrar-editais',
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
      name: 'Como filtrar editais',
      item: 'https://smartlic.tech/como-filtrar-editais',
    },
  ],
};

const RELATED_PAGES = [
  {
    href: '/como-avaliar-licitacao',
    title: 'Como avaliar se uma licitacao vale a pena',
  },
  {
    href: '/como-evitar-prejuizo-licitacao',
    title: 'Como evitar prejuizo em licitacoes',
  },
  {
    href: '/como-priorizar-oportunidades',
    title: 'Como priorizar oportunidades',
  },
];

export default function ComoFiltrarEditais() {
  return (
    <ContentPageLayout
      breadcrumbLabel="Como filtrar editais"
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

      <h1>Como filtrar editais de licitacao e focar no que importa</h1>

      <p className="lead text-lg">
        O problema nao e falta de licitacoes. E excesso de irrelevancia. Todos
        os dias, milhares de editais sao publicados nos portais PNCP,
        ComprasGov e Portal de Compras Publicas. Para uma empresa de
        engenharia, por exemplo, menos de 1% dessas publicacoes sao realmente
        relevantes. O desafio nao e encontrar licitacoes — e separar as que
        importam das que so consomem tempo.
      </p>

      <h2>Por que a busca manual nao funciona</h2>

      <p>
        A maioria das empresas ainda monitora licitacoes da forma tradicional:
        acessa os portais oficiais, digita palavras-chave e navega paginas de
        resultados. Esse processo tem tres problemas estruturais:
      </p>

      <h3>Volume impossivel de processar</h3>
      <p>
        O PNCP sozinho publica milhares de contratacoes por dia. Para cobrir
        todas as 27 UFs com profundidade, seria necessario analisar centenas de
        resultados diariamente. Nenhuma equipe de licitacoes consegue fazer
        isso com consistencia.
      </p>

      <h3>Fontes dispersas</h3>
      <p>
        Nao existe um unico portal que consolide todas as licitacoes do Brasil.
        O PNCP cobre a maioria, mas o Portal de Compras Publicas e o ComprasGov
        publicam editais que nao aparecem no PNCP — e vice-versa. Monitorar
        uma fonte so ja e dificil. Monitorar tres, com formatos diferentes,
        paginacoes diferentes e atualizacoes em horarios diferentes, e
        impraticavel.
      </p>

      <h3>Palavras-chave sao ambiguas</h3>
      <p>
        Buscar por &quot;manutencao&quot; retorna licitacoes de manutencao
        predial, manutencao de veiculos, manutencao de equipamentos medicos,
        manutencao de software e dezenas de outros objetos completamente
        diferentes. A mesma palavra-chave que traz editais relevantes traz
        tambem uma avalanche de ruido.
      </p>

      <h2>O que um bom filtro precisa considerar</h2>

      <p>
        Um filtro eficaz vai alem de palavras-chave. Ele precisa cruzar
        multiplas dimensoes para determinar se um edital e relevante:
      </p>

      <ul>
        <li>
          <strong>Setor de atuacao:</strong> nao apenas o objeto, mas o
          contexto completo do edital. Uma licitacao de &quot;servicos de
          limpeza&quot; pode ser facilities ou pode ser descontaminacao
          industrial — setores completamente diferentes.
        </li>
        <li>
          <strong>Faixa de valor:</strong> filtrar editais que estejam dentro
          da capacidade financeira e operacional da empresa.
        </li>
        <li>
          <strong>Regiao:</strong> focar nas UFs onde a empresa tem presenca
          ou capacidade logistica.
        </li>
        <li>
          <strong>Prazo:</strong> excluir editais com prazo insuficiente para
          preparacao de proposta.
        </li>
        <li>
          <strong>Modalidade:</strong> priorizar modalidades compativeis com
          o perfil da empresa.
        </li>
      </ul>

      <h2>Filtro por palavra-chave vs. filtro por perfil</h2>

      <p>
        A diferenca fundamental entre a busca tradicional e um filtro
        inteligente esta na abordagem:
      </p>

      <p>
        <strong>Filtro por palavra-chave</strong> busca textos que contenham
        termos especificos. E rapido, mas impreciso. A palavra
        &quot;informatica&quot; aparece tanto em editais de compra de
        computadores quanto em editais de cursos de capacitacao em informatica
        basica. O resultado: muito ruido, pouca relevancia.
      </p>

      <p>
        <strong>Filtro por perfil</strong> analisa o edital como um todo e
        compara com o perfil da empresa: setor, faixa de valor, regioes de
        atuacao, historico. Em vez de perguntar &quot;esse edital contem a
        palavra X?&quot;, pergunta &quot;esse edital e compativel com o perfil
        dessa empresa?&quot;. O resultado: menos editais, mais relevancia.
      </p>

      <p>
        <Link href="/como-avaliar-licitacao">
          Veja os 5 criterios usados para avaliar compatibilidade
        </Link>
        .
      </p>

      <h2>Na pratica: de 1.500 para 12</h2>

      <p>Considere o cenario real de uma empresa de mobiliario corporativo:</p>

      <ul>
        <li>
          <strong>Total publicado na semana:</strong> ~1.500 editais nas 3
          fontes oficiais para as 27 UFs
        </li>
        <li>
          <strong>Apos filtro por setor:</strong> 180 editais relacionados a
          mobiliario (12% do total)
        </li>
        <li>
          <strong>Apos filtro por faixa de valor</strong> (R$ 100k a R$ 2M):
          45 editais (3% do total)
        </li>
        <li>
          <strong>Apos filtro por UFs de atuacao</strong> (SP, RJ, MG, PR):
          22 editais (1,5% do total)
        </li>
        <li>
          <strong>Apos classificacao IA de relevancia:</strong> 12 editais
          com alta aderencia (0,8% do total)
        </li>
      </ul>

      <p>
        Esses 12 editais sao os que realmente merecem a atencao da equipe. Os
        outros 1.488 seriam tempo perdido.{' '}
        <Link href="/como-evitar-prejuizo-licitacao">
          E tempo perdido em licitacoes se traduz diretamente em prejuizo
        </Link>
        .
      </p>

      <h2>Como o SmartLic aborda esse problema</h2>

      <p>
        O SmartLic agrega dados de tres fontes oficiais (PNCP, Portal de
        Compras Publicas e ComprasGov) e aplica um pipeline de filtragem em
        multiplas etapas:
      </p>

      <ol>
        <li>
          <strong>Consolidacao:</strong> busca simultanea nas 3 fontes com
          deduplicacao automatica (o mesmo edital pode aparecer em mais de
          um portal)
        </li>
        <li>
          <strong>Filtro por UF e valor:</strong> eliminacao rapida de editais
          fora do escopo geografico e financeiro
        </li>
        <li>
          <strong>Classificacao setorial:</strong> analise por keywords com
          pontuacao de densidade, complementada por classificacao IA para
          editais ambiguos
        </li>
        <li>
          <strong>Avaliacao de viabilidade:</strong> scoring de 4 fatores
          (modalidade, prazo, valor, geografia) para cada edital aprovado
        </li>
      </ol>

      <p>
        O resultado e um conjunto reduzido de editais classificados por
        relevancia e viabilidade — prontos para analise humana qualificada.
      </p>

      {/* CTA Section */}
      <div className="not-prose mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-lg p-8 text-center border border-brand-blue/20">
        <p className="text-lg font-semibold text-ink mb-2">
          Pare de perder tempo com editais irrelevantes
        </p>
        <p className="text-ink-secondary mb-6">
          O SmartLic filtra milhares de licitacoes e entrega apenas as que
          importam para o seu setor, regiao e faixa de valor.
        </p>
        <Link
          href="/signup?source=content-filtrar"
          className="inline-block bg-brand-navy hover:bg-brand-blue-hover text-white font-semibold px-6 py-3 rounded-button transition-all hover:scale-[1.02] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2"
        >
          Comece Gratis
        </Link>
      </div>
    </ContentPageLayout>
  );
}
