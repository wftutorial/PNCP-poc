import { Metadata } from 'next';
import ContentPageLayout from '../components/ContentPageLayout';
import Link from 'next/link';

export const metadata: Metadata = {
  title:
    'Como identificar licitacoes com maior chance de vitoria | SmartLic',
  description:
    'Aprenda a priorizar oportunidades de licitacao usando criterios de aderencia, viabilidade e competicao estimada.',
  alternates: {
    canonical: 'https://smartlic.tech/como-priorizar-oportunidades',
  },
};

const articleSchema = {
  '@context': 'https://schema.org',
  '@type': 'Article',
  headline: 'Como identificar licitacoes com maior chance de vitoria',
  description:
    'Framework pratico para priorizar oportunidades de licitacao usando criterios de aderencia, viabilidade e competicao.',
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
    '@id': 'https://smartlic.tech/como-priorizar-oportunidades',
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
      name: 'Como priorizar oportunidades',
      item: 'https://smartlic.tech/como-priorizar-oportunidades',
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
    href: '/como-filtrar-editais',
    title: 'Como filtrar editais de licitacao',
  },
];

export default function ComoPriorizarOportunidades() {
  return (
    <ContentPageLayout
      breadcrumbLabel="Como priorizar oportunidades"
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

      <h1>Como identificar licitacoes com maior chance de vitoria</h1>

      <p className="lead text-lg">
        Encontrar licitacoes e facil. Saber quais priorizar e o que gera
        resultado. Uma empresa com recursos limitados — e todas tem — precisa
        concentrar esforcos nos editais onde a probabilidade de vitoria e a
        margem esperada justificam o investimento. Participar de tudo nao e
        estrategia; e dispersao.
      </p>

      <h2>Por que priorizacao importa mais que volume</h2>

      <p>
        Existe uma crenca persistente no mercado B2G de que participar de mais
        licitacoes automaticamente aumenta as chances de vencer. A matematica
        conta outra historia.
      </p>

      <p>
        Uma empresa que participa de 30 licitacoes por mes com preparacao
        superficial tem taxa de sucesso tipica de 3-5%. A mesma empresa
        participando de 8 licitacoes com preparacao aprofundada pode alcancar
        25-35% de sucesso. O resultado liquido e melhor com menos participacoes
        — desde que sejam as corretas.
      </p>

      <p>
        O custo de preparacao por licitacao cai quando voce participa de menos
        editais com mais dedicacao. A qualidade da proposta sobe. A equipe
        trabalha com menos pressao e mais foco.{' '}
        <Link href="/como-evitar-prejuizo-licitacao">
          E os riscos de prejuizo diminuem drasticamente
        </Link>
        .
      </p>

      <h2>Criterios de priorizacao</h2>

      <p>
        Priorizar oportunidades exige um framework objetivo. Opiniao e
        &quot;feeling&quot; nao escalam. Os tres eixos fundamentais de
        priorizacao sao:
      </p>

      <h3>Aderencia ao perfil</h3>
      <p>
        Quao alinhado o edital esta com o que sua empresa faz de melhor? Isso
        inclui setor de atuacao, tipo de servico ou produto, porte do contrato
        e complexidade tecnica. Uma aderencia alta significa que voce pode
        apresentar atestados solidos, equipe qualificada e experiencia
        comprovada — fatores que pesam em qualquer avaliacao.
      </p>

      <h3>Viabilidade operacional</h3>
      <p>
        Voce consegue executar esse contrato com qualidade e margem saudavel?
        A viabilidade considera quatro fatores:{' '}
        <Link href="/como-avaliar-licitacao">
          modalidade, prazo, valor e geografia
        </Link>
        . Um edital pode ser altamente aderente ao seu perfil, mas inviavel
        por estar em uma regiao onde voce nao tem infraestrutura.
      </p>

      <h3>Competicao estimada</h3>
      <p>
        Quantas empresas provavelmente vao participar e quao forte e a
        competicao? Pregoes eletronicos com criterio de menor preco em setores
        comoditizados atraem dezenas de concorrentes. Concorrencias tecnicas
        em nichos especializados podem ter 3-5 participantes. A probabilidade
        de vitoria muda drasticamente.
      </p>

      <h2>Como avaliar a viabilidade de cada oportunidade</h2>

      <p>
        Para cada edital pre-filtrado, aplique uma avaliacao estruturada com
        pontuacao:
      </p>

      <ul>
        <li>
          <strong>Modalidade (peso 30%):</strong> pregao eletronico com menor
          preco pontua baixo para empresas que competem por qualidade.
          Concorrencia com tecnica e preco pontua alto para quem tem
          diferenciais tecnicos.
        </li>
        <li>
          <strong>Prazo (peso 25%):</strong> quanto tempo ha para preparar a
          proposta? Prazo apertado reduz a pontuacao pois limita a qualidade
          da preparacao.
        </li>
        <li>
          <strong>Faixa de valor (peso 25%):</strong> o valor esta na faixa
          ideal da empresa? Muito acima ou muito abaixo reduz a pontuacao.
        </li>
        <li>
          <strong>Geografia (peso 20%):</strong> o orgao esta em uma regiao
          onde a empresa opera com eficiencia? Regioes distantes sem presenca
          local reduzem a pontuacao.
        </li>
      </ul>

      <p>
        A soma ponderada desses fatores gera um indice de viabilidade que pode
        ser classificado em tres niveis: alta, media e baixa. Priorize os
        editais com viabilidade alta e aderencia alta.
      </p>

      <h2>Framework de decisao: participar, monitorar ou descartar</h2>

      <p>
        Com a aderencia e a viabilidade avaliadas, cada oportunidade cai em uma
        de tres categorias:
      </p>

      <ul>
        <li>
          <strong>Participar:</strong> aderencia alta + viabilidade alta.
          Dedique recursos completos para preparar a melhor proposta
          possivel.
        </li>
        <li>
          <strong>Monitorar:</strong> aderencia alta + viabilidade media, ou
          aderencia media + viabilidade alta. Acompanhe o edital e reavalie
          se as condicoes mudarem (esclarecimentos, aditivos).
        </li>
        <li>
          <strong>Descartar:</strong> qualquer combinacao com aderencia baixa
          ou viabilidade baixa. Nao invista tempo — passe para o proximo.
        </li>
      </ul>

      <p>
        Esse framework elimina decisoes emocionais (&quot;parece bom, vamos
        tentar&quot;) e substitui por criterios objetivos e replicaveis.
      </p>

      <h2>Exemplo pratico: 3 licitacoes, qual priorizar?</h2>

      <p>
        Uma empresa de materiais eletricos com sede em Sao Paulo, faixa de
        valor ideal de R$ 200k a R$ 1,5M, encontra tres editais na mesma
        semana:
      </p>

      <h3>Edital A — Pregao Eletronico, R$ 450 mil</h3>
      <p>
        Fornecimento de material eletrico para hospital em Campinas/SP.
        Criterio: menor preco. Prazo: 12 dias.
      </p>
      <ul>
        <li>Aderencia: <strong>Alta</strong> — core business</li>
        <li>Modalidade: Media — pregao menor preco, competicao acirrada</li>
        <li>Valor: <strong>Alto</strong> — dentro da faixa ideal</li>
        <li>Prazo: <strong>Alto</strong> — 12 dias e suficiente</li>
        <li>Geografia: <strong>Alta</strong> — mesma UF, 100 km da sede</li>
      </ul>
      <p>
        <strong>Decisao: PARTICIPAR</strong> — viabilidade alta em todos os
        eixos
      </p>

      <h3>Edital B — Concorrencia, R$ 3,2 milhoes</h3>
      <p>
        Instalacao eletrica completa de escola em Manaus/AM. Criterio: tecnica
        e preco. Prazo: 25 dias.
      </p>
      <ul>
        <li>Aderencia: Media — inclui servicos de instalacao alem do fornecimento</li>
        <li>Modalidade: <strong>Alta</strong> — tecnica e preco favorece experiencia</li>
        <li>Valor: Baixo — acima da faixa ideal (R$ 3,2M vs limite de R$ 1,5M)</li>
        <li>Prazo: <strong>Alto</strong> — 25 dias e confortavel</li>
        <li>Geografia: Baixa — Manaus exige logistica complexa</li>
      </ul>
      <p>
        <strong>Decisao: DESCARTAR</strong> — valor fora da faixa + logistica
        inviavel
      </p>

      <h3>Edital C — Pregao Eletronico, R$ 180 mil</h3>
      <p>
        Material eletrico para reforma de edificio publico no Rio de
        Janeiro/RJ. Criterio: menor preco. Prazo: 8 dias.
      </p>
      <ul>
        <li>Aderencia: <strong>Alta</strong> — core business</li>
        <li>Modalidade: Media — pregao menor preco</li>
        <li>Valor: Media — ligeiramente abaixo da faixa ideal</li>
        <li>Prazo: Baixo — 8 dias e apertado para proposta completa</li>
        <li>Geografia: <strong>Alta</strong> — RJ, logistica viavel</li>
      </ul>
      <p>
        <strong>Decisao: MONITORAR</strong> — prazo apertado e o fator
        limitante. Se um aditivo ampliar o prazo, reclassifique para
        &quot;participar&quot;.
      </p>

      <p>
        Sem esse framework, a empresa provavelmente tentaria participar dos
        tres editais, diluindo recursos e reduzindo a qualidade de todas as
        propostas.{' '}
        <Link href="/como-filtrar-editais">
          Veja como a filtragem inteligente automatiza a primeira etapa desse
          processo
        </Link>
        .
      </p>

      {/* CTA Section */}
      <div className="not-prose mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-lg p-8 text-center border border-brand-blue/20">
        <p className="text-lg font-semibold text-ink mb-2">
          Priorize com dados, nao com intuicao
        </p>
        <p className="text-ink-secondary mb-6">
          O SmartLic avalia a viabilidade de cada edital com 4 criterios
          ponderados e classifica automaticamente em alta, media e baixa.
        </p>
        <Link
          href="/signup?source=content-priorizar"
          className="inline-block bg-brand-navy hover:bg-brand-blue-hover text-white font-semibold px-6 py-3 rounded-button transition-all hover:scale-[1.02] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2"
        >
          Comece Gratis
        </Link>
      </div>
    </ContentPageLayout>
  );
}
