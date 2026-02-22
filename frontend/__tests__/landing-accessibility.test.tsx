/**
 * UX-344 — Landing Page: Accessible Counters
 * Verifies aria-labels on animated/static counters so screen readers
 * read the correct final values (not the animation start value "0").
 */
import React from 'react';
import { render, screen } from '@testing-library/react';

// ---- Mocks ----

// Mock framer-motion — pass through children
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

// Mock animations lib — always visible so counters render immediately
jest.mock('../lib/animations', () => ({
  useScrollAnimation: () => ({ ref: { current: null }, isVisible: true }),
  fadeInUp: {},
  staggerContainer: {},
  scaleIn: {},
}));

// Mock GlassCard — render a div preserving aria attrs
jest.mock('../app/components/ui/GlassCard', () => ({
  GlassCard: ({
    children,
    role,
    'aria-label': ariaLabel,
  }: {
    children: React.ReactNode;
    role?: string;
    'aria-label'?: string;
  }) => (
    <div role={role} aria-label={ariaLabel}>
      {children}
    </div>
  ),
}));

// Mock GradientButton
jest.mock('../app/components/ui/GradientButton', () => ({
  GradientButton: ({ children }: { children: React.ReactNode }) => (
    <button>{children}</button>
  ),
}));

// Mock useInView for StatsSection
jest.mock('../app/hooks/useInView', () => ({
  useInView: () => ({ ref: { current: null }, isInView: true }),
}));

// ---- Imports (after mocks) ----
import HeroSection from '../app/components/landing/HeroSection';
import StatsSection from '../app/components/landing/StatsSection';

// ---- Tests ----

describe('UX-344 — Landing Page Accessible Counters', () => {
  describe('AC1+AC4: HeroSection counters have aria-label with final values', () => {
    it('renders aria-label="15 setores especializados"', () => {
      render(<HeroSection />);
      expect(
        screen.getByRole('text', { name: '15 setores especializados' })
      ).toBeInTheDocument();
    });

    it('renders aria-label="87% de editais descartados"', () => {
      render(<HeroSection />);
      expect(
        screen.getByRole('text', { name: '87% de editais descartados' })
      ).toBeInTheDocument();
    });

    it('renders aria-label="27 UFs cobertas"', () => {
      render(<HeroSection />);
      expect(
        screen.getByRole('text', { name: '27 UFs cobertas' })
      ).toBeInTheDocument();
    });
  });

  describe('AC4: Animated values are aria-hidden', () => {
    it('hides the animated number span from screen readers', () => {
      const { container } = render(<HeroSection />);
      const hiddenEls = container.querySelectorAll('[aria-hidden="true"]');
      // 3 badges × (icon + content div) = at least 6 aria-hidden elements
      expect(hiddenEls.length).toBeGreaterThanOrEqual(6);
    });
  });

  describe('AC2: StatsSection counters have aria-label with final values', () => {
    it('renders aria-label="15 setores especializados"', () => {
      render(<StatsSection />);
      expect(
        screen.getByRole('text', { name: '15 setores especializados' })
      ).toBeInTheDocument();
    });

    it('renders aria-label="1000+ regras de filtragem"', () => {
      render(<StatsSection />);
      expect(
        screen.getByRole('text', { name: '1000+ regras de filtragem' })
      ).toBeInTheDocument();
    });

    it('renders aria-label="27 estados cobertos"', () => {
      render(<StatsSection />);
      expect(
        screen.getByRole('text', { name: '27 estados cobertos' })
      ).toBeInTheDocument();
    });

    it('renders aria-label for "Sob demanda" stat', () => {
      render(<StatsSection />);
      expect(
        screen.getByRole('text', {
          name: 'Sob demanda análises quando você precisar',
        })
      ).toBeInTheDocument();
    });
  });

  describe('AC2+AC4: StatsSection values are aria-hidden', () => {
    it('hides static number divs from screen readers', () => {
      const { container } = render(<StatsSection />);
      const hiddenEls = container.querySelectorAll('[aria-hidden="true"]');
      // 4 stat cards × 2 inner divs (number + label) = 8 aria-hidden elements
      expect(hiddenEls.length).toBeGreaterThanOrEqual(8);
    });
  });

  describe('AC3: Screen reader reads correct values regardless of animation state', () => {
    it('aria-label contains final value even when counter shows 0', () => {
      render(<HeroSection />);
      const badge = screen.getByRole('text', { name: '15 setores especializados' });
      expect(badge).toHaveAttribute('aria-label', '15 setores especializados');
    });
  });
});
