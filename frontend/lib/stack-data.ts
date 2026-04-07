/**
 * S8: Tech stack data for /stack page.
 * Metrics are real production values from SmartLic.
 * Last updated: 2026-04-07 — Update quarterly or when metrics change significantly.
 */

export type StackCategory = 'database' | 'infra' | 'frontend' | 'backend' | 'email' | 'ai' | 'cache' | 'billing';

export interface StackMetric {
  label: string;
  value: string;
}

export interface StackTool {
  id: string;
  name: string;
  category: StackCategory;
  url: string;
  description: string;
  metrics: StackMetric[];
}

export const CATEGORY_LABELS: Record<StackCategory, string> = {
  database: 'Banco de Dados',
  infra: 'Infraestrutura',
  frontend: 'Frontend',
  backend: 'Backend',
  email: 'Email',
  ai: 'Inteligência Artificial',
  cache: 'Cache & Resiliência',
  billing: 'Cobrança',
};

export const CATEGORY_COLORS: Record<StackCategory, string> = {
  database: 'bg-emerald-100 text-emerald-800',
  infra: 'bg-purple-100 text-purple-800',
  frontend: 'bg-blue-100 text-blue-800',
  backend: 'bg-orange-100 text-orange-800',
  email: 'bg-pink-100 text-pink-800',
  ai: 'bg-yellow-100 text-yellow-800',
  cache: 'bg-red-100 text-red-800',
  billing: 'bg-indigo-100 text-indigo-800',
};

export const STACK_TOOLS: StackTool[] = [
  {
    id: 'supabase',
    name: 'Supabase',
    category: 'database',
    url: 'https://supabase.com',
    description: 'Banco PostgreSQL com Auth, RLS multi-tenant e APIs auto-geradas.',
    metrics: [
      { label: 'Linhas em pncp_raw_bids', value: '40.000+' },
      { label: 'RLS multi-tenant', value: 'Ativo' },
      { label: 'Setup Auth', value: '15 min' },
    ],
  },
  {
    id: 'railway',
    name: 'Railway',
    category: 'infra',
    url: 'https://railway.app',
    description: 'Deploy monorepo com web + worker, zero downtime e auto-deploy via GitHub.',
    metrics: [
      { label: 'Arquitetura', value: 'Monorepo web+worker' },
      { label: 'Downtime', value: '0' },
      { label: 'Keep-alive', value: '75s' },
    ],
  },
  {
    id: 'nextjs',
    name: 'Next.js',
    category: 'frontend',
    url: 'https://nextjs.org',
    description: 'Framework React com ISR para 7.000+ páginas e performance 99.',
    metrics: [
      { label: 'Páginas ISR', value: '7.000+' },
      { label: 'LCP', value: '< 2,5s' },
      { label: 'Perf score', value: '99' },
    ],
  },
  {
    id: 'fastapi',
    name: 'FastAPI',
    category: 'backend',
    url: 'https://fastapi.tiangolo.com',
    description: 'API Python async com 49 endpoints, tipagem Pydantic e Gunicorn.',
    metrics: [
      { label: 'Endpoints', value: '49' },
      { label: 'p95 latência', value: '< 200ms' },
      { label: 'Gunicorn timeout', value: '180s' },
    ],
  },
  {
    id: 'resend',
    name: 'Resend',
    category: 'email',
    url: 'https://resend.com',
    description: 'Emails transacionais com templates React e integração rápida.',
    metrics: [
      { label: 'Tipo', value: 'Transacional' },
      { label: 'Integração', value: '30 min' },
      { label: 'Templates', value: '5' },
    ],
  },
  {
    id: 'openai',
    name: 'OpenAI',
    category: 'ai',
    url: 'https://openai.com',
    description: 'GPT-4.1-nano para classificação setorial e resumos de editais.',
    metrics: [
      { label: 'Modelo', value: 'GPT-4.1-nano' },
      { label: 'Precisão classificação', value: '85%' },
      { label: 'Custo/chamada', value: '$0,002' },
    ],
  },
  {
    id: 'redis',
    name: 'Redis',
    category: 'cache',
    url: 'https://redis.io',
    description: 'Cache L1 com TTL 4h, circuit breaker e rate limiting.',
    metrics: [
      { label: 'Cache L1', value: '4h TTL' },
      { label: 'Circuit breaker', value: 'Ativo' },
      { label: 'Rate limiting', value: 'Ativo' },
    ],
  },
  {
    id: 'stripe',
    name: 'Stripe',
    category: 'billing',
    url: 'https://stripe.com',
    description: 'Cobrança com 3 períodos, webhook auto-sync e pro-rata automática.',
    metrics: [
      { label: 'Períodos de cobrança', value: '3' },
      { label: 'Webhook sync', value: 'Automático' },
      { label: 'Pro-rata', value: 'Automática' },
    ],
  },
];
