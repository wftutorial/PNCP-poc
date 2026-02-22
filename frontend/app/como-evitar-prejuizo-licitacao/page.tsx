import { Metadata } from 'next';
import ContentPageLayout from '../components/ContentPageLayout';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Como evitar prejuizo em licitacoes publicas | SmartLic',
  description:
    'Conheca as 5 causas mais comuns de prejuizo em licitacoes e aprenda como evitar cada uma com exemplos praticos.',
  alternates: {
    canonical: 'https://smartlic.tech/como-evitar-prejuizo-licitacao',
  },
};

const articleSchema = {
  '@context': 'https://schema.org',
  '@type': 'Article',
  headline: 'Como evitar prejuizo em licitacoes publicas',
  description:
    'As 5 causas mais comuns de prejuizo em licitacoes e como evitar cada uma com exemplos praticos.',
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
    '@id': 'https://smartlic.tech/como-evitar-prejuizo-licitacao',
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
      name: 'Como evitar prejuizo em licitacoes',
      item: 'https://smartlic.tech/como-evitar-prejuizo-licitacao',
    },
  ],
};

const RELATED_PAGES = [
  {
    href: '/como-avaliar-licitacao',
    title: 'Como avaliar se uma licitacao vale a pena',
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

export default function ComoEvitarPrejuizo() {
  return (
    <ContentPageLayout
      breadcrumbLabel="Como evitar prejuizo em licitacoes"
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

      <h1>Como evitar prejuizo em licitacoes publicas</h1>

      <p className="lead text-lg">
        Participar da licitacao errada custa mais do que nao participar. Esse e
        um principio que muitas empresas aprendem da forma mais cara: depois de
        investir semanas de trabalho, honorarios de advogados, custos de
        certificacao e horas da equipe tecnica em um edital que nunca deveria
        ter saido da triagem inicial.
      </p>

      <p>
        O mercado de licitacoes publicas no Brasil movimenta centenas de
        bilhoes por ano. Com esse volume, a tentacao de participar de tudo e
        grande. Mas volume sem criterio nao gera resultado — gera prejuizo.
        Abaixo estao as 5 causas mais comuns de perda financeira em licitacoes
        e como evitar cada uma.
      </p>

      <h2>1. Participar sem avaliar viabilidade</h2>

      <p>
        A causa mais frequente de prejuizo e tambem a mais evitavel: entrar em
        uma licitacao sem fazer uma analise minima de viabilidade. Isso acontece
        quando a empresa ve o objeto do edital, identifica que &quot;parece ser
        da area&quot; e comeca a preparar a proposta sem verificar valor,
        regiao, prazos ou requisitos tecnicos.
      </p>

      <p>
        <strong>Exemplo:</strong> Uma empresa de facilities de medio porte
        investiu R$ 35 mil (entre documentacao, certidoes e horas da equipe)
        para participar de um pregao de manutencao predial avaliado em R$ 12
        milhoes. O problema: o edital exigia atestados de capacidade para no
        minimo 50% do valor — R$ 6 milhoes em um unico contrato. A empresa
        nunca havia executado contrato acima de R$ 2 milhoes. Desclassificada
        na fase de habilitacao.
      </p>

      <p>
        <strong>Como evitar:</strong>{' '}
        <Link href="/como-avaliar-licitacao">
          aplique os 5 criterios de avaliacao
        </Link>{' '}
        antes de iniciar qualquer preparacao. Se o edital nao passar nos
        criterios basicos, nao invista um real nele.
      </p>

      <h2>2. Subestimar custos de preparacao</h2>

      <p>
        Preparar uma proposta de licitacao nao e gratuito. Dependendo da
        modalidade e complexidade, os custos incluem:
      </p>

      <ul>
        <li>Certidoes e documentos atualizados (R$ 500 a R$ 2.000)</li>
        <li>Horas da equipe tecnica para elaboracao de proposta (20-80h)</li>
        <li>Honorarios de consultoria juridica (R$ 2.000 a R$ 10.000)</li>
        <li>Garantia de proposta, quando exigida (1-5% do valor)</li>
        <li>Viagens para visita tecnica obrigatoria</li>
      </ul>

      <p>
        <strong>Exemplo:</strong> Uma empresa de software gastou R$ 18 mil
        preparando proposta tecnica detalhada para uma concorrencia de
        informatizacao hospitalar. Perdeu por 0,3 pontos na avaliacao tecnica.
        O investimento nao recuperavel representou quase 40% do lucro do
        trimestre anterior.
      </p>

      <p>
        <strong>Como evitar:</strong> antes de decidir participar, faca uma
        estimativa realista do custo total de preparacao e compare com a margem
        esperada em caso de vitoria. Se o custo de preparacao supera 5% da
        margem liquida estimada, reavalie.
      </p>

      <h2>3. Ignorar requisitos tecnicos incompativeis</h2>

      <p>
        Editais de licitacao frequentemente incluem requisitos tecnicos
        especificos que eliminam participantes na habilitacao. Certificacoes
        obrigatorias, atestados com metragens ou volumes minimos, equipe
        tecnica com formacao especifica — tudo isso precisa ser verificado
        antes de investir na proposta.
      </p>

      <p>
        <strong>Exemplo:</strong> Uma construtora de pequeno porte participou
        de licitacao para reforma de escola. O edital exigia engenheiro civil
        com certificacao em acessibilidade (ABNT NBR 9050) no quadro
        permanente. A empresa tinha o profissional como consultor externo, nao
        como funcionario. Resultado: inabilitada apos todo o investimento de
        preparacao.
      </p>

      <p>
        <strong>Como evitar:</strong> leia o edital completo — especialmente os
        anexos de habilitacao tecnica — antes de iniciar a preparacao. Se
        algum requisito nao pode ser cumprido no prazo disponivel, desista
        cedo.
      </p>

      <h2>4. Competir fora da faixa de valor ideal</h2>

      <p>
        Cada empresa tem uma faixa de valor em que opera com eficiencia e
        margem saudavel. Participar de licitacoes muito acima dessa faixa
        expoe a empresa a riscos de execucao. Participar de licitacoes muito
        abaixo consome recursos que poderiam ser aplicados em oportunidades
        mais rentaveis.
      </p>

      <p>
        <strong>Como evitar:</strong> defina objetivamente a faixa de valor em
        que sua empresa compete melhor. Considere o historico de contratos
        executados com sucesso, o capital de giro disponivel e a capacidade
        operacional.{' '}
        <Link href="/como-priorizar-oportunidades">
          Saiba como priorizar oportunidades dentro da sua faixa ideal
        </Link>
        .
      </p>

      <h2>5. Nao considerar logistica e regiao</h2>

      <p>
        Uma licitacao atraente no papel pode se tornar um pesadelo logistico
        na execucao. Fornecimento continuo para orgaos em regioes remotas,
        manutencao com SLA de 4 horas em cidades a 800 km da base,
        deslocamento de equipe tecnica para estados sem filial — tudo isso
        corroi a margem e pode levar a inadimplencia contratual.
      </p>

      <p>
        <strong>Exemplo:</strong> Uma empresa de vigilancia de Curitiba venceu
        licitacao para seguranca patrimonial em tres unidades no Mato Grosso.
        O custo de implantacao (recrutamento local, treinamento, deslocamento
        de supervisores) ultrapassou em 60% o previsto. O contrato operou no
        prejuizo durante 14 meses ate a rescisao.
      </p>

      <p>
        <strong>Como evitar:</strong> inclua o custo logistico real na analise
        de viabilidade. Se o edital exige presenca fisica, calcule o impacto
        no custo total antes de decidir participar.
      </p>

      <h2>Como um filtro estrategico reduz o risco</h2>

      <p>
        Todas as 5 causas de prejuizo listadas acima tem algo em comum: podem
        ser identificadas <strong>antes</strong> de iniciar a preparacao da
        proposta. O problema e que, com centenas de editais publicados
        diariamente, fazer essa analise manualmente para cada um e humanamente
        impossivel.
      </p>

      <p>
        Um filtro estrategico automatizado resolve isso ao aplicar criterios
        objetivos (setor, valor, regiao, prazo, modalidade) antes que o edital
        chegue a sua mesa. Em vez de analisar 200 editais por semana e
        participar de 20 sem criterio, voce analisa 15 pre-qualificados e
        participa de 5 com alta probabilidade de sucesso.
      </p>

      <p>
        <Link href="/como-filtrar-editais">
          Entenda como funciona a filtragem inteligente de editais
        </Link>{' '}
        e por que ela e diferente de uma simples busca por palavras-chave.
      </p>

      {/* CTA Section */}
      <div className="not-prose mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-lg p-8 text-center border border-brand-blue/20">
        <p className="text-lg font-semibold text-ink mb-2">
          Pare de investir em licitacoes erradas
        </p>
        <p className="text-ink-secondary mb-6">
          O SmartLic filtra, classifica e avalia a viabilidade de cada edital
          automaticamente — antes que voce gaste um centavo.
        </p>
        <Link
          href="/signup?source=content-prejuizo"
          className="inline-block bg-brand-navy hover:bg-brand-blue-hover text-white font-semibold px-6 py-3 rounded-button transition-all hover:scale-[1.02] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2"
        >
          Comece Gratis
        </Link>
      </div>
    </ContentPageLayout>
  );
}
