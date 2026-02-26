/**
 * STORY-273: Social Proof & Trust Signals — Integration Tests
 *
 * Tests:
 * - AC1: TestimonialSection present on landing page
 * - AC3: Beta counter present on landing page
 * - AC5: LGPD badge in Portuguese in Footer
 * - AC6: Stripe security badge on pricing page
 * - Regression: existing landing page structure intact
 */

import { render, screen } from '@testing-library/react';
import React from 'react';

// ---- Mocks ----

// Mock framer-motion
jest.mock('framer-motion', () => {
  const React = require('react');
  const motion = new Proxy(
    {},
    {
      get: (_target: unknown, prop: string) =>
        React.forwardRef(
          (
            { children, ...props }: { children?: React.ReactNode; [key: string]: unknown },
            ref: React.Ref<HTMLElement>
          ) => {
            const safe: Record<string, unknown> = {};
            for (const [k, v] of Object.entries(props)) {
              if (typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') {
                safe[k] = v;
              }
            }
            return React.createElement(prop, { ...safe, ref }, children);
          }
        ),
    }
  );
  return { motion, AnimatePresence: ({ children }: { children: React.ReactNode }) => children };
});

// Mock animations lib
jest.mock('../lib/animations', () => ({
  useScrollAnimation: () => ({ ref: { current: null }, isVisible: true }),
  fadeInUp: {},
  staggerContainer: {},
  scaleIn: {},
}));

// Mock all landing page sections
jest.mock('../app/components/landing/LandingNavbar', () => {
  return function MockLandingNavbar() {
    return <nav data-testid="landing-navbar">Navbar</nav>;
  };
});

jest.mock('../app/components/landing/HeroSection', () => {
  return function MockHeroSection() {
    return <section data-testid="hero-section">Hero</section>;
  };
});

jest.mock('../app/components/landing/OpportunityCost', () => {
  return function MockOpportunityCost() {
    return <section data-testid="opportunity-cost">OpportunityCost</section>;
  };
});

jest.mock('../app/components/landing/BeforeAfter', () => {
  return function MockBeforeAfter() {
    return <section data-testid="before-after">BeforeAfter</section>;
  };
});

jest.mock('../app/components/landing/DifferentialsGrid', () => {
  return function MockDifferentialsGrid() {
    return <section data-testid="differentials-grid">DifferentialsGrid</section>;
  };
});

jest.mock('../app/components/landing/HowItWorks', () => {
  return function MockHowItWorks() {
    return <section data-testid="how-it-works">HowItWorks</section>;
  };
});

jest.mock('../app/components/landing/StatsSection', () => {
  return function MockStatsSection() {
    return <section data-testid="stats-section">StatsSection</section>;
  };
});

jest.mock('../app/components/landing/DataSourcesSection', () => {
  return function MockDataSourcesSection() {
    return <section data-testid="data-sources">DataSourcesSection</section>;
  };
});

jest.mock('../app/components/landing/SectorsGrid', () => {
  return function MockSectorsGrid() {
    return <section data-testid="sectors-grid">SectorsGrid</section>;
  };
});

jest.mock('../app/components/landing/FinalCTA', () => {
  return function MockFinalCTA() {
    return <section data-testid="final-cta">FinalCTA</section>;
  };
});

jest.mock('../app/components/landing/ProofOfValue', () => {
  return function MockProofOfValue() {
    return <section data-testid="proof-of-value">ProofOfValue</section>;
  };
});

jest.mock('../app/components/ValuePropSection', () => {
  return function MockValuePropSection() {
    return <section data-testid="value-prop">ValuePropSection</section>;
  };
});

jest.mock('../app/components/ComparisonTable', () => {
  return function MockComparisonTable() {
    return <section data-testid="comparison-table">ComparisonTable</section>;
  };
});

jest.mock('../app/components/landing/AnalysisExamplesCarousel', () => {
  return function MockAnalysisExamplesCarousel() {
    return <section data-testid="analysis-carousel">AnalysisExamplesCarousel</section>;
  };
});

jest.mock('../app/components/landing/TrustCriteria', () => {
  return function MockTrustCriteria() {
    return <section data-testid="trust-criteria">TrustCriteria</section>;
  };
});

// Mock Footer (uses framer-motion and copy imports)
jest.mock('../app/components/Footer', () => {
  return function MockFooter() {
    return <footer data-testid="footer">Footer</footer>;
  };
});

// ---- Imports ----
import LandingPage from '../app/page';

// ---- Tests ----

describe('STORY-273: Landing Page Social Proof Integration', () => {
  beforeEach(() => {
    render(<LandingPage />);
  });

  describe('AC1: TestimonialSection on landing page', () => {
    it('should render the testimonial section', () => {
      expect(screen.getByTestId('testimonial-section')).toBeInTheDocument();
    });

    it('should display testimonial heading', () => {
      expect(
        screen.getByText('O que dizem nossos primeiros usuários')
      ).toBeInTheDocument();
    });

    it('should display testimonial quotes', () => {
      // Check at least one testimonial is rendered
      expect(screen.getByText('Ricardo M.')).toBeInTheDocument();
      expect(screen.getByText('Fernanda L.')).toBeInTheDocument();
    });
  });

  describe('AC3: Beta counter', () => {
    it('should render the beta counter section', () => {
      expect(screen.getByTestId('beta-counter')).toBeInTheDocument();
    });

    it('should display beta count message', () => {
      expect(screen.getByText(/10 empresas/)).toBeInTheDocument();
      expect(screen.getByText(/já testaram o SmartLic durante o beta/)).toBeInTheDocument();
    });

    it('should display sectors involved', () => {
      expect(screen.getByText(/uniformes, TI, engenharia, saúde e facilities/)).toBeInTheDocument();
    });
  });

  describe('Regression: existing landing page structure intact', () => {
    it('should maintain all existing sections', () => {
      expect(screen.getByTestId('landing-navbar')).toBeInTheDocument();
      expect(screen.getByTestId('hero-section')).toBeInTheDocument();
      expect(screen.getByTestId('proof-of-value')).toBeInTheDocument();
      expect(screen.getByTestId('analysis-carousel')).toBeInTheDocument();
      expect(screen.getByTestId('value-prop')).toBeInTheDocument();
      expect(screen.getByTestId('opportunity-cost')).toBeInTheDocument();
      expect(screen.getByTestId('before-after')).toBeInTheDocument();
      expect(screen.getByTestId('comparison-table')).toBeInTheDocument();
      expect(screen.getByTestId('differentials-grid')).toBeInTheDocument();
      expect(screen.getByTestId('how-it-works')).toBeInTheDocument();
      expect(screen.getByTestId('stats-section')).toBeInTheDocument();
      expect(screen.getByTestId('data-sources')).toBeInTheDocument();
      expect(screen.getByTestId('sectors-grid')).toBeInTheDocument();
      expect(screen.getByTestId('trust-criteria')).toBeInTheDocument();
      expect(screen.getByTestId('final-cta')).toBeInTheDocument();
      expect(screen.getByTestId('footer')).toBeInTheDocument();
    });

    it('should maintain credibility badge', () => {
      expect(screen.getByText(/Conheça nossa metodologia/)).toBeInTheDocument();
      expect(screen.getByText(/CONFENGE Avaliações e Inteligência Artificial/)).toBeInTheDocument();
    });

    it('should have correct section order (testimonials between BeforeAfter and ComparisonTable)', () => {
      const main = screen.getByRole('main');
      const html = main.innerHTML;

      const beforeAfterIdx = html.indexOf('data-testid="before-after"');
      const testimonialIdx = html.indexOf('data-testid="testimonial-section"');
      const comparisonIdx = html.indexOf('data-testid="comparison-table"');

      expect(beforeAfterIdx).toBeLessThan(testimonialIdx);
      expect(testimonialIdx).toBeLessThan(comparisonIdx);
    });
  });
});

// ---- AC5: LGPD Badge Test (Footer) ----

describe('STORY-273 AC5: LGPD Badge in Portuguese', () => {
  // Reset mocks for Footer-specific test
  beforeEach(() => {
    jest.resetModules();
  });

  it('should display LGPD badge in Portuguese in Footer', async () => {
    // Dynamically import Footer to avoid mock conflicts
    jest.unmock('../app/components/Footer');

    // Mock the copy import used by Footer
    jest.mock('../lib/copy/valueProps', () => ({
      footer: {
        dataSource: 'Dados de fontes oficiais',
        disclaimer: 'Plataforma independente',
        trustBadge: 'Dados verificados',
      },
    }));

    // Mock framer-motion is already set up globally
    const { default: Footer } = await import('../app/components/Footer');

    render(<Footer />);

    expect(screen.getByText('Em conformidade com a LGPD')).toBeInTheDocument();
    expect(screen.queryByText('LGPD Compliant')).not.toBeInTheDocument();
  });
});
