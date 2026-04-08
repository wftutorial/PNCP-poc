/**
 * DEBT-08 AC2 (TD-056): jest-axe automated a11y tests — 10 critical components.
 *
 * Uses axe-core via jest-axe to detect WCAG 2.1 AA violations at the DOM level.
 * Each test renders a component and asserts toHaveNoViolations().
 *
 * Components under test:
 *  1. EmptyState           — shared empty state UI
 *  2. EmptyResults         — buscar zero-results state
 *  3. PlanCard             — pricing card (PricingCard equivalent)
 *  4. PlanToggle           — billing period toggle
 *  5. ViabilityBadge       — AI viability score badge
 *  6. LlmSourceBadge       — AI summary provenance badge
 *  7. LicitacaoCard        — individual bid result card
 *  8. ResultCard           — executive summary card
 *  9. FilterPanel          — buscar filter sidebar
 * 10. LoginForm            — authentication form
 */

import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

// ─── Mock next/link so it renders a plain <a> in jsdom ───────────────────────
jest.mock('next/link', () => {
  const MockLink = ({ href, children, ...rest }: { href: string; children: React.ReactNode; [key: string]: unknown }) => (
    <a href={href} {...rest}>{children}</a>
  );
  MockLink.displayName = 'MockLink';
  return MockLink;
});

// ─── Mock lucide-react icons to avoid SVG complexities ───────────────────────
jest.mock('lucide-react', () => ({
  ArrowRight: (props: React.SVGProps<SVGSVGElement>) => <svg aria-hidden="true" {...props} />,
  MapPin: (props: React.SVGProps<SVGSVGElement>) => <svg aria-hidden="true" {...props} />,
  ChevronDown: (props: React.SVGProps<SVGSVGElement>) => <svg aria-hidden="true" {...props} />,
  Filter: (props: React.SVGProps<SVGSVGElement>) => <svg aria-hidden="true" {...props} />,
  Eye: (props: React.SVGProps<SVGSVGElement>) => <svg aria-hidden="true" {...props} />,
  EyeOff: (props: React.SVGProps<SVGSVGElement>) => <svg aria-hidden="true" {...props} />,
  AlertCircle: (props: React.SVGProps<SVGSVGElement>) => <svg aria-hidden="true" {...props} />,
}));

// ─── Mock framer-motion to avoid animation complexity ────────────────────────
jest.mock('framer-motion', () => ({
  motion: new Proxy({}, {
    get: (_target, tag) => {
      const Tag = tag as string;
      const Component = ({ children, ...rest }: React.HTMLAttributes<HTMLElement> & { children?: React.ReactNode }) => {
        const safeProps = Object.fromEntries(
          Object.entries(rest).filter(([k]) => !k.startsWith('animate') && !k.startsWith('initial') && !k.startsWith('exit') && !k.startsWith('whileHover') && !k.startsWith('transition') && !k.startsWith('variants'))
        );
        return React.createElement(Tag, safeProps, children);
      };
      Component.displayName = `motion.${Tag}`;
      return Component;
    },
  }),
  AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// ─── Sub-component mocks (for FilterPanel dependencies) ──────────────────────
jest.mock('../../app/buscar/components/StatusFilter', () => ({
  StatusFilter: ({ value, onChange }: { value: string; onChange: (v: unknown) => void }) => (
    <div role="group" aria-label="Status filter">
      <select value={value} onChange={(e) => onChange(e.target.value)} aria-label="Status">
        <option value="abertas">Abertas</option>
      </select>
    </div>
  ),
}));

jest.mock('../../app/buscar/components/ModalidadeFilter', () => ({
  ModalidadeFilter: () => (
    <div role="group" aria-label="Modalidade filter">
      <fieldset><legend>Modalidade</legend></fieldset>
    </div>
  ),
}));

jest.mock('../../app/buscar/components/ValorFilter', () => ({
  ValorFilter: () => (
    <div role="group" aria-label="Valor filter">
      <label htmlFor="valor-min">Valor mínimo</label>
      <input id="valor-min" type="number" />
    </div>
  ),
}));

jest.mock('../../app/components/EsferaFilter', () => ({
  EsferaFilter: () => (
    <div role="group" aria-label="Esfera filter">
      <fieldset><legend>Esfera</legend></fieldset>
    </div>
  ),
}));

jest.mock('../../app/components/MunicipioFilter', () => ({
  MunicipioFilter: () => (
    <div role="group" aria-label="Município filter">
      <fieldset><legend>Município</legend></fieldset>
    </div>
  ),
}));

// ─── Mock @dnd-kit for PipelineCard (used in LicitacaoCard area) ─────────────
jest.mock('@dnd-kit/sortable', () => ({
  useSortable: () => ({
    attributes: {},
    listeners: {},
    setNodeRef: jest.fn(),
    transform: null,
    transition: undefined,
    isDragging: false,
  }),
}));

jest.mock('@dnd-kit/utilities', () => ({
  CSS: { Transform: { toString: jest.fn(() => '') } },
}));

// ─── Mock lib/format-currency ────────────────────────────────────────────────
jest.mock('../../lib/format-currency', () => ({
  formatCurrencyBR: (v: number) => `R$ ${v.toFixed(2)}`,
}));

// ─── Mock date-fns (needed by LicitacaoCard + PipelineCard) ──────────────────
jest.mock('date-fns', () => ({
  differenceInDays: jest.fn(() => 5),
  differenceInHours: jest.fn(() => 120),
  isPast: jest.fn(() => false),
  parseISO: jest.fn((d: string) => new Date(d)),
  format: jest.fn(() => '15/03/2026'),
}));

// ─── axe config shared across tests ─────────────────────────────────────────
const axeConfig = {
  rules: {
    // color-contrast requires actual CSS rendering (not available in jsdom)
    'color-contrast': { enabled: false },
  },
};

// =============================================================================
// 1. EmptyState
// =============================================================================
import { EmptyState } from '../../components/EmptyState';

describe('A11y — EmptyState', () => {
  it('has no WCAG 2.1 AA violations', async () => {
    const { container } = render(
      <EmptyState
        icon={<span aria-hidden="true">📭</span>}
        title="Nenhuma busca realizada"
        description="Comece buscando licitações para o seu setor."
        ctaLabel="Buscar agora"
        ctaHref="/buscar"
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });
});

// =============================================================================
// 2. EmptyResults
// =============================================================================
import { EmptyResults } from '../../app/buscar/components/EmptyResults';

describe('A11y — EmptyResults', () => {
  it('has no WCAG 2.1 AA violations', async () => {
    const { container } = render(
      <EmptyResults
        totalRaw={0}
        sectorName="Construção Civil"
        ufCount={5}
        onScrollToTop={jest.fn()}
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });
});

// =============================================================================
// 3. PlanCard (PricingCard)
// =============================================================================
import { PlanCard } from '../../components/subscriptions/PlanCard';

describe('A11y — PlanCard (PricingCard)', () => {
  it('has no WCAG 2.1 AA violations — monthly billing', async () => {
    const { container } = render(
      <PlanCard
        id="smartlic_pro"
        name="SmartLic Pro"
        monthlyPrice={397}
        billingPeriod="monthly"
        features={['1000 buscas/mês', 'Excel export', 'Pipeline Kanban']}
        highlighted
        onSelect={jest.fn()}
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });

  it('has no WCAG 2.1 AA violations — annual billing', async () => {
    const { container } = render(
      <PlanCard
        id="smartlic_pro"
        name="SmartLic Pro"
        monthlyPrice={397}
        billingPeriod="annual"
        features={['1000 buscas/mês', 'Excel export', 'Pipeline Kanban']}
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });
});

// =============================================================================
// 4. PlanToggle
// =============================================================================
import { PlanToggle } from '../../components/subscriptions/PlanToggle';

describe('A11y — PlanToggle', () => {
  it('has no WCAG 2.1 AA violations', async () => {
    const { container } = render(
      <PlanToggle
        value="monthly"
        onChange={jest.fn()}
        discounts={{ semiannual: 10, annual: 25 }}
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });
});

// =============================================================================
// 5. ViabilityBadge
// =============================================================================
import ViabilityBadge from '../../components/ViabilityBadge';

describe('A11y — ViabilityBadge', () => {
  it('has no WCAG 2.1 AA violations — alta', async () => {
    const { container } = render(
      <ViabilityBadge
        level="alta"
        score={85}
        factors={{
          modalidade: 90,
          modalidade_label: 'Pregão Eletrônico',
          timeline: 80,
          timeline_label: '15 dias',
          value_fit: 75,
          value_fit_label: 'Dentro do range',
          geography: 95,
          geography_label: 'SP',
        }}
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });

  it('has no WCAG 2.1 AA violations — baixa', async () => {
    const { container } = render(
      <ViabilityBadge level="baixa" score={30} />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });
});

// =============================================================================
// 6. LlmSourceBadge
// =============================================================================
import { LlmSourceBadge } from '../../app/buscar/components/LlmSourceBadge';

describe('A11y — LlmSourceBadge', () => {
  it('has no violations — ai source', async () => {
    const { container } = render(<LlmSourceBadge llmSource="ai" />);
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });

  it('has no violations — fallback source', async () => {
    const { container } = render(<LlmSourceBadge llmSource="fallback" />);
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });

  it('has no violations — processing state', async () => {
    const { container } = render(<LlmSourceBadge llmSource="processing" />);
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });
});

// =============================================================================
// 7. LicitacaoCard (ResultCard equivalent — individual bid card)
// =============================================================================
import LicitacaoCard from '../../app/components/LicitacaoCard';
import type { LicitacaoItem } from '../../app/types';

const mockLicitacao: LicitacaoItem = {
  objeto: 'Pregão Eletrônico para aquisição de uniformes escolares',
  orgao: 'Secretaria Municipal de Educação',
  uf: 'SP',
  municipio: 'São Paulo',
  modalidade: 'Pregão Eletrônico',
  link: 'https://pncp.gov.br/app/editais/00001-0001-2026',
  pncp_id: '00001-0001-2026',
  valor: 150000,
  data_abertura: '2026-04-15',
  data_encerramento: '2026-04-20',
  data_publicacao: '2026-04-01',
  dias_restantes: 12,
  matched_terms: ['uniforme', 'escola'],
  _source: 'pncp',
  relevance_source: 'keyword',
  confidence: 'high',
  viability_score: 82,
  viability_level: 'alta',
  viability_factors: null,
  numero_compra: '001/2026',
  cnpj_orgao: '01.001.001/0001-01',
  supplier_sanctions: null,
};

describe('A11y — LicitacaoCard', () => {
  it('has no WCAG 2.1 AA violations', async () => {
    const { container } = render(
      <LicitacaoCard
        licitacao={mockLicitacao}
        matchedKeywords={['uniforme']}
        status="aberta"
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });
});

// =============================================================================
// 8. ResultCard (executive summary card)
// =============================================================================
import { ResultCard } from '../../app/buscar/components/search-results/ResultCard';
import type { BuscaResult } from '../../app/types';

const mockBuscaResult = {
  llm_source: 'ai' as const,
  resumo: {
    resumo_executivo: 'Foram encontradas 5 licitações relevantes para o setor de construção civil.',
    total_oportunidades: 5,
    valor_total: 750000,
    insight_setorial: 'O mercado de construção civil em SP apresenta crescimento.',
    recomendacoes: [],
    destaques: [],
    alertas_urgencia: [],
  },
  licitacoes: [],
  download_id: null,
  total_raw: 10,
  total_filtrado: 5,
  filter_stats: null,
  termos_utilizados: ['construção'],
  stopwords_removidas: [],
  excel_available: true,
  upgrade_message: null,
  sources_used: ['pncp'],
  source_stats: null,
  is_partial: false,
} as unknown as BuscaResult;

describe('A11y — ResultCard', () => {
  it('has no WCAG 2.1 AA violations — full access', async () => {
    const { container } = render(
      <ResultCard
        result={mockBuscaResult}
        trialPhase="full_access"
        isProfileComplete
        bannerDismissed={false}
        onDismissBanner={jest.fn()}
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });

  it('has no WCAG 2.1 AA violations — limited access (paywall overlay)', async () => {
    const { container } = render(
      <ResultCard
        result={mockBuscaResult}
        trialPhase="limited_access"
        isProfileComplete={false}
        bannerDismissed={false}
        onDismissBanner={jest.fn()}
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });
});

// =============================================================================
// 9. FilterPanel
// =============================================================================
import FilterPanel from '../../app/buscar/components/FilterPanel';

describe('A11y — FilterPanel', () => {
  it('has no WCAG 2.1 AA violations', async () => {
    const { container } = render(
      <FilterPanel
        locationFiltersOpen={false}
        setLocationFiltersOpen={jest.fn()}
        esferas={[]}
        setEsferas={jest.fn()}
        ufsSelecionadas={new Set(['SP', 'RJ'])}
        municipios={[]}
        setMunicipios={jest.fn()}
        advancedFiltersOpen={false}
        setAdvancedFiltersOpen={jest.fn()}
        status="abertas"
        setStatus={jest.fn()}
        modalidades={[]}
        setModalidades={jest.fn()}
        valorMin={null}
        setValorMin={jest.fn()}
        valorMax={null}
        setValorMax={jest.fn()}
        setValorValid={jest.fn()}
        loading={false}
        clearResult={jest.fn()}
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });

  it('has no violations with open location filters', async () => {
    const { container } = render(
      <FilterPanel
        locationFiltersOpen
        setLocationFiltersOpen={jest.fn()}
        esferas={['federal']}
        setEsferas={jest.fn()}
        ufsSelecionadas={new Set(['SP'])}
        municipios={[]}
        setMunicipios={jest.fn()}
        advancedFiltersOpen={false}
        setAdvancedFiltersOpen={jest.fn()}
        status="abertas"
        setStatus={jest.fn()}
        modalidades={[4, 6]}
        setModalidades={jest.fn()}
        valorMin={10000}
        setValorMin={jest.fn()}
        valorMax={500000}
        setValorMax={jest.fn()}
        setValorValid={jest.fn()}
        loading={false}
        clearResult={jest.fn()}
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });
});

// =============================================================================
// 10. LoginForm
// =============================================================================
import { LoginForm } from '../../app/login/components/LoginForm';

const mockReactHookForm = {
  register: jest.fn().mockReturnValue({
    name: 'email',
    onChange: jest.fn(),
    onBlur: jest.fn(),
    ref: jest.fn(),
  }),
  handleSubmit: jest.fn((fn: (data: unknown) => void) => (e: React.FormEvent) => {
    e?.preventDefault?.();
    fn({ email: 'test@example.com', password: 'password123' });
  }),
  formState: { errors: {} },
};

// Mock Button component — strip non-HTML props before forwarding to <button>
jest.mock('../../components/ui/button', () => ({
  Button: ({ children, loading: _loading, asChild: _asChild, variant: _variant, size: _size, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { children?: React.ReactNode; loading?: boolean; asChild?: boolean; variant?: string; size?: string }) => (
    <button type="button" {...props}>{children}</button>
  ),
}));

describe('A11y — LoginForm', () => {
  it('has no WCAG 2.1 AA violations — password mode', async () => {
    const { container } = render(
      <LoginForm
        form={mockReactHookForm}
        mode="password"
        onModeChange={jest.fn()}
        loading={false}
        error={null}
        success={false}
        onSubmit={jest.fn()}
        onGoogleSignIn={jest.fn()}
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });

  it('has no WCAG 2.1 AA violations — with error state', async () => {
    const { container } = render(
      <LoginForm
        form={mockReactHookForm}
        mode="password"
        onModeChange={jest.fn()}
        loading={false}
        error="Email ou senha incorretos. Tente novamente."
        success={false}
        onSubmit={jest.fn()}
        onGoogleSignIn={jest.fn()}
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });

  it('has no WCAG 2.1 AA violations — magic link mode', async () => {
    const { container } = render(
      <LoginForm
        form={mockReactHookForm}
        mode="magic"
        onModeChange={jest.fn()}
        loading={false}
        error={null}
        success={false}
        onSubmit={jest.fn()}
        onGoogleSignIn={jest.fn()}
      />
    );
    const results = await axe(container, axeConfig);
    expect(results).toHaveNoViolations();
  });
});
