/**
 * STORY-261 AC6 / STORY-262 AC20: Blog article metadata index and utilities
 *
 * Central registry for all blog articles. Provides access patterns
 * used by listing page, dynamic route, RSS feed, and sitemap.
 */

export type BlogCategory = 'Empresas B2G' | 'Consultorias de Licitação';

export interface BlogArticleMeta {
  slug: string;
  title: string;
  description: string;
  category: BlogCategory;
  tags: string[];
  publishDate: string;
  readingTime: string;
  wordCount: number;
  keywords: string[];
  relatedSlugs: string[];
}

/**
 * Calculate reading time based on word count (~200 words/minute).
 */
export function calculateReadingTime(wordCount: number): string {
  const minutes = Math.max(1, Math.ceil(wordCount / 200));
  return `${minutes} min de leitura`;
}

/**
 * Central article metadata registry.
 *
 * STORY-262: 15 B2G articles (empresas-b2g cluster)
 * STORY-263: Consultorias articles (future)
 */
export const BLOG_ARTICLES: BlogArticleMeta[] = [
  // ──────────────────────────────────────────────
  // STORY-262: Empresas B2G — 15 articles
  // ──────────────────────────────────────────────

  // B2G-01
  {
    slug: 'como-aumentar-taxa-vitoria-licitacoes',
    title: 'Como Aumentar sua Taxa de Vitória em Licitações sem Contratar mais Analistas',
    description:
      'Descubra como empresas B2G aumentam de 8% para 25% a taxa de adjudicação em pregões usando análise de viabilidade e triagem inteligente.',
    category: 'Empresas B2G',
    tags: ['taxa de vitória', 'triagem inteligente', 'viabilidade', 'estratégia'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2800),
    wordCount: 2800,
    keywords: [
      'taxa de vitória em licitações',
      'como ganhar mais licitações',
      'eficiência setor de licitação',
      'análise de viabilidade pregão',
    ],
    relatedSlugs: [
      'vale-a-pena-disputar-pregao',
      'reduzir-tempo-analisando-editais-irrelevantes',
      'escolher-editais-maior-probabilidade-vitoria',
    ],
  },

  // B2G-02
  {
    slug: 'erro-operacional-perder-contratos-publicos',
    title: 'O Erro Operacional que Faz Empresas Perderem Contratos Públicos de R$ 150 mil',
    description:
      'Empresas B2G perdem contratos de seis dígitos por falhas de triagem. Conheça o erro operacional mais comum e como corrigi-lo antes do próximo pregão.',
    category: 'Empresas B2G',
    tags: ['erros operacionais', 'contratos públicos', 'triagem', 'viabilidade'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2300),
    wordCount: 2300,
    keywords: [
      'perder licitação por erro',
      'erro em licitação pública',
      'como não perder pregão',
      'falha operacional licitação',
    ],
    relatedSlugs: [
      'custo-invisivel-disputar-pregoes-errados',
      'reduzir-tempo-analisando-editais-irrelevantes',
      'empresas-vencem-30-porcento-pregoes',
    ],
  },

  // B2G-03
  {
    slug: 'vale-a-pena-disputar-pregao',
    title: 'Como Saber se Vale a Pena Disputar um Pregão antes de Investir Horas na Análise',
    description:
      'Aprenda os 4 critérios objetivos para avaliar a viabilidade de um pregão em menos de 5 minutos — antes de comprometer sua equipe com análise completa.',
    category: 'Empresas B2G',
    tags: ['viabilidade', 'avaliação de pregão', 'triagem rápida', 'critérios objetivos'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2800),
    wordCount: 2800,
    keywords: [
      'vale a pena disputar licitação',
      'como avaliar pregão',
      'viabilidade de licitação',
      'análise rápida de edital',
    ],
    relatedSlugs: [
      'como-aumentar-taxa-vitoria-licitacoes',
      'disputar-todas-licitacoes-matematica-real',
      'escolher-editais-maior-probabilidade-vitoria',
    ],
  },

  // B2G-04
  {
    slug: 'clausulas-escondidas-editais-licitacao',
    title: '7 Cláusulas Escondidas em Editais que Eliminam Fornecedores Experientes',
    description:
      'Conheça as 7 cláusulas de edital que mais eliminam empresas qualificadas — e como identificá-las na triagem para evitar propostas inválidas.',
    category: 'Empresas B2G',
    tags: ['cláusulas de edital', 'habilitação', 'Lei 14.133', 'riscos em editais'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2800),
    wordCount: 2800,
    keywords: [
      'cláusulas edital licitação',
      'armadilhas em editais',
      'como ler edital de licitação',
      'erros comuns em licitação',
    ],
    relatedSlugs: [
      'erro-operacional-perder-contratos-publicos',
      'estruturar-setor-licitacao-5-milhoes',
      'empresas-vencem-30-porcento-pregoes',
    ],
  },

  // B2G-05
  {
    slug: 'reduzir-tempo-analisando-editais-irrelevantes',
    title: 'Como Reduzir em 50% o Tempo Gasto Analisando Editais Irrelevantes',
    description:
      'Empresas B2G gastam até 40 horas/mês lendo editais que descartam. Veja como cortar esse tempo pela metade com triagem estruturada.',
    category: 'Empresas B2G',
    tags: ['produtividade', 'triagem de editais', 'eficiência operacional', 'automação'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2300),
    wordCount: 2300,
    keywords: [
      'reduzir tempo analisando editais',
      'otimizar setor de licitação',
      'eficiência em licitações',
      'triagem de editais',
    ],
    relatedSlugs: [
      'equipe-40-horas-mes-editais-descartados',
      'como-aumentar-taxa-vitoria-licitacoes',
      'licitacao-volume-ou-inteligencia',
    ],
  },

  // B2G-06
  {
    slug: 'disputar-todas-licitacoes-matematica-real',
    title: 'Vale a Pena Disputar Todas as Licitações do Seu Segmento? A Matemática Real',
    description:
      'Análise quantitativa: disputar 100% das licitações do seu setor gera prejuízo operacional. Veja os números reais e a estratégia que maximiza o retorno.',
    category: 'Empresas B2G',
    tags: ['ROI em licitações', 'matemática', 'estratégia seletiva', 'análise quantitativa'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2800),
    wordCount: 2800,
    keywords: [
      'quantas licitações participar',
      'estratégia de licitação',
      'ROI em licitações',
      'matemática de licitação',
    ],
    relatedSlugs: [
      'licitacao-volume-ou-inteligencia',
      'vale-a-pena-disputar-pregao',
      'custo-invisivel-disputar-pregoes-errados',
    ],
  },

  // B2G-07
  {
    slug: 'estruturar-setor-licitacao-5-milhoes',
    title: 'Como Estruturar um Setor de Licitação Enxuto para Faturar R$ 5 Milhões por Ano',
    description:
      'Modelo operacional comprovado: como montar um setor de licitação com 2-3 pessoas capaz de gerar R$ 5 milhões/ano em contratos públicos.',
    category: 'Empresas B2G',
    tags: ['setor de licitação', 'modelo operacional', 'equipe enxuta', 'faturamento'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(3200),
    wordCount: 3200,
    keywords: [
      'como montar setor de licitação',
      'estruturar equipe de licitação',
      'faturar com licitações',
      'setor de licitação empresa',
    ],
    relatedSlugs: [
      'pipeline-licitacoes-funil-comercial',
      'como-aumentar-taxa-vitoria-licitacoes',
      'empresas-vencem-30-porcento-pregoes',
    ],
  },

  // B2G-08
  {
    slug: 'custo-invisivel-disputar-pregoes-errados',
    title: 'O Custo Invisível de Disputar Pregões Errados',
    description:
      'Além do tempo perdido: conheça os 6 custos invisíveis de disputar pregões sem análise prévia de viabilidade e o impacto no seu faturamento anual.',
    category: 'Empresas B2G',
    tags: ['custos ocultos', 'prejuízo em licitação', 'análise de viabilidade', 'ROI'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2300),
    wordCount: 2300,
    keywords: [
      'custo de participar de licitação',
      'prejuízo em licitação',
      'custos ocultos licitação',
      'pregão errado',
    ],
    relatedSlugs: [
      'erro-operacional-perder-contratos-publicos',
      'disputar-todas-licitacoes-matematica-real',
      'equipe-40-horas-mes-editais-descartados',
    ],
  },

  // B2G-09
  {
    slug: 'escolher-editais-maior-probabilidade-vitoria',
    title: 'Como Escolher Editais com Maior Probabilidade de Vitória',
    description:
      'Framework prático com 4 indicadores preditivos para selecionar editais onde sua empresa tem vantagem competitiva real — antes de investir na proposta.',
    category: 'Empresas B2G',
    tags: ['seleção de editais', 'indicadores preditivos', 'vantagem competitiva', 'framework'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2800),
    wordCount: 2800,
    keywords: [
      'como escolher licitação',
      'probabilidade de ganhar licitação',
      'selecionar editais',
      'vantagem competitiva licitação',
    ],
    relatedSlugs: [
      'como-aumentar-taxa-vitoria-licitacoes',
      'vale-a-pena-disputar-pregao',
      'disputar-todas-licitacoes-matematica-real',
    ],
  },

  // B2G-10
  {
    slug: 'licitacao-volume-ou-inteligencia',
    title: 'Licitação por Volume ou por Inteligência? Qual Estratégia Dá mais Lucro',
    description:
      'Comparação objetiva entre as estratégias de volume e inteligência em licitações: custos, margens, riscos e casos reais.',
    category: 'Empresas B2G',
    tags: ['estratégia', 'volume vs inteligência', 'margem de lucro', 'comparativo'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2800),
    wordCount: 2800,
    keywords: [
      'estratégia de licitação',
      'volume vs qualidade licitação',
      'como lucrar com licitações',
      'inteligência em licitações',
    ],
    relatedSlugs: [
      'disputar-todas-licitacoes-matematica-real',
      'como-aumentar-taxa-vitoria-licitacoes',
      'reduzir-tempo-analisando-editais-irrelevantes',
    ],
  },

  // B2G-11
  {
    slug: 'orgaos-risco-atraso-pagamento-licitacao',
    title: 'Como Identificar Órgãos com Maior Risco de Atraso no Pagamento',
    description:
      'Guia prático para verificar o histórico de pagamento de órgãos públicos antes de disputar um pregão — com fontes oficiais e indicadores de risco.',
    category: 'Empresas B2G',
    tags: ['risco de pagamento', 'órgãos públicos', 'Portal da Transparência', 'due diligence'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2300),
    wordCount: 2300,
    keywords: [
      'atraso pagamento governo',
      'órgão público paga em dia',
      'risco de pagamento licitação',
      'inadimplência governo',
    ],
    relatedSlugs: [
      'custo-invisivel-disputar-pregoes-errados',
      'escolher-editais-maior-probabilidade-vitoria',
      'clausulas-escondidas-editais-licitacao',
    ],
  },

  // B2G-12
  {
    slug: 'empresas-vencem-30-porcento-pregoes',
    title: 'Empresas que Vencem 30% dos Pregões Fazem Isso Diferente',
    description:
      'Análise de padrões comuns em empresas B2G com taxa de adjudicação acima de 30% — e as 5 práticas que as separam da média do mercado.',
    category: 'Empresas B2G',
    tags: ['benchmark', 'melhores práticas', 'taxa de adjudicação', 'top performers'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2800),
    wordCount: 2800,
    keywords: [
      'como ganhar mais pregões',
      'empresas que vencem licitações',
      'melhores práticas licitação',
      'taxa de adjudicação',
    ],
    relatedSlugs: [
      'como-aumentar-taxa-vitoria-licitacoes',
      'estruturar-setor-licitacao-5-milhoes',
      'licitacao-volume-ou-inteligencia',
    ],
  },

  // B2G-13
  {
    slug: 'pipeline-licitacoes-funil-comercial',
    title: 'Como Organizar seu Pipeline de Licitações como um Funil Comercial',
    description:
      'Adapte o conceito de pipeline comercial B2B para licitações: as 5 etapas, métricas de conversão e como garantir previsibilidade de receita.',
    category: 'Empresas B2G',
    tags: ['pipeline', 'funil comercial', 'gestão de oportunidades', 'métricas'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2800),
    wordCount: 2800,
    keywords: [
      'pipeline de licitações',
      'funil de licitação',
      'gestão de oportunidades licitação',
      'CRM para licitação',
    ],
    relatedSlugs: [
      'estruturar-setor-licitacao-5-milhoes',
      'como-aumentar-taxa-vitoria-licitacoes',
      'empresas-vencem-30-porcento-pregoes',
    ],
  },

  // B2G-14
  {
    slug: 'ata-registro-precos-como-escolher',
    title: 'Ata de Registro de Preços — Como Escolher as que Realmente Valem a Pena',
    description:
      'Nem toda Ata de Registro de Preços é vantajosa. Conheça os 6 critérios para avaliar se uma ARP vale sua adesão — e quando recusar.',
    category: 'Empresas B2G',
    tags: ['ARP', 'ata de registro de preços', 'Lei 14.133', 'avaliação de risco'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2800),
    wordCount: 2800,
    keywords: [
      'ata de registro de preços',
      'ARP licitação',
      'como escolher ata de registro',
      'vale a pena ata de preços',
    ],
    relatedSlugs: [
      'clausulas-escondidas-editais-licitacao',
      'escolher-editais-maior-probabilidade-vitoria',
      'disputar-todas-licitacoes-matematica-real',
    ],
  },

  // B2G-15
  {
    slug: 'equipe-40-horas-mes-editais-descartados',
    title: 'Por Que sua Equipe Passa 40 Horas por Mês Lendo Editais que Descarta',
    description:
      'Análise do problema operacional n.1 em setores de licitação: o custo de 40h/mês em triagem manual. Diagnóstico, causas e solução estruturada.',
    category: 'Empresas B2G',
    tags: ['triagem manual', 'ineficiência operacional', 'custo de oportunidade', 'automação'],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2300),
    wordCount: 2300,
    keywords: [
      'tempo perdido lendo editais',
      'ineficiência setor de licitação',
      'triagem manual de editais',
      'automatizar licitação',
    ],
    relatedSlugs: [
      'reduzir-tempo-analisando-editais-irrelevantes',
      'custo-invisivel-disputar-pregoes-errados',
      'como-aumentar-taxa-vitoria-licitacoes',
    ],
  },

  // ──────────────────────────────────────────────
  // STORY-263: Consultorias de Licitação
  // ──────────────────────────────────────────────

  {
    slug: 'consultoria-licitacao-ferramenta-digital',
    title: 'Ferramentas Digitais para Consultorias de Licitação',
    description:
      'Como consultorias especializadas em licitações podem escalar suas operações com inteligência artificial e automação.',
    category: 'Consultorias de Licitação',
    tags: [
      'consultoria',
      'ferramentas digitais',
      'automação',
      'inteligência artificial',
    ],
    publishDate: '2026-02-24',
    readingTime: calculateReadingTime(2200),
    wordCount: 2200,
    keywords: [
      'consultoria de licitação',
      'ferramenta para licitação',
      'automação licitações públicas',
    ],
    relatedSlugs: [
      'como-aumentar-taxa-vitoria-licitacoes',
      'erro-operacional-perder-contratos-publicos',
    ],
  },
];

export function getArticleBySlug(slug: string): BlogArticleMeta | undefined {
  return BLOG_ARTICLES.find((article) => article.slug === slug);
}

export function getArticlesByCategory(category: string): BlogArticleMeta[] {
  return BLOG_ARTICLES.filter((article) => article.category === category);
}

export function getRelatedArticles(slug: string): BlogArticleMeta[] {
  const article = getArticleBySlug(slug);
  if (!article) return [];
  return article.relatedSlugs
    .map((relSlug) => getArticleBySlug(relSlug))
    .filter((a): a is BlogArticleMeta => a !== undefined);
}

export function getAllSlugs(): string[] {
  return BLOG_ARTICLES.map((article) => article.slug);
}
