/**
 * LandingNavbar Component Tests
 * STORY-223 AC21-AC24: Auth-aware CTA rendering
 * DEBT-v3-S2 AC20: Updated for RSC + client island architecture.
 *
 * LandingNavbar is now an RSC that delegates interactive parts to NavbarClientIsland.tsx.
 * Tests focus on the client islands (NavbarAuthCTA, NavScrollButton, NavbarMobileControls)
 * since RSCs render static HTML that is always present.
 *
 * Tests:
 * - AC21: Component uses useAuth hook (via NavbarAuthCTA)
 * - AC22: Logged-in user sees "Ir para Busca" button
 * - AC23: Not-logged-in user sees "Entrar" and "Comece Gratis" (UX-345)
 * - AC24: Loading state has no layout shift (placeholder rendered)
 */

import { render, screen } from '@testing-library/react';
import { NavbarAuthCTA, NavScrollButton } from '@/app/components/landing/NavbarClientIsland';

// Mock useAuth hook
const mockUseAuth = jest.fn();

jest.mock('../../app/components/AuthProvider', () => ({
  useAuth: () => mockUseAuth(),
}));

// Mock Next.js Link component
jest.mock('next/link', () => {
  return function MockLink({ children, href, className }: { children: React.ReactNode; href: string; className?: string }) {
    return <a href={href} className={className}>{children}</a>;
  };
});

describe('LandingNavbar — NavbarAuthCTA (client island)', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('AC21: useAuth integration', () => {
    it('should call useAuth hook', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        loading: false,
      });

      render(<NavbarAuthCTA />);

      expect(mockUseAuth).toHaveBeenCalled();
    });
  });

  describe('AC24: Loading state - no layout shift', () => {
    it('should render placeholder div during loading to prevent layout shift', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        loading: true,
      });

      const { container } = render(<NavbarAuthCTA />);

      // Check for placeholder div with width
      const placeholder = container.querySelector('.w-\\[160px\\]');
      expect(placeholder).toBeInTheDocument();

      // Should NOT show Entrar or Comece Gratis during loading
      expect(screen.queryByRole('link', { name: /Entrar/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('link', { name: /Comece Gratis/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('link', { name: /Ir para Busca/i })).not.toBeInTheDocument();
    });
  });

  describe('AC23: Not-logged-in user state (UX-345 updated copy)', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: null,
        loading: false,
      });
    });

    it('should show "Entrar" link when not authenticated', () => {
      render(<NavbarAuthCTA />);

      const entrarLink = screen.getByRole('link', { name: /Entrar/i });
      expect(entrarLink).toBeInTheDocument();
      expect(entrarLink).toHaveAttribute('href', '/login');
    });

    it('should show "Comece Gratis" link when not authenticated', () => {
      render(<NavbarAuthCTA />);

      const signupLink = screen.getByRole('link', { name: /Comece Gratis/i });
      expect(signupLink).toBeInTheDocument();
      expect(signupLink).toHaveAttribute('href', '/signup?source=header-cta');
    });

    it('should NOT show "Ir para Busca" when not authenticated', () => {
      render(<NavbarAuthCTA />);

      expect(screen.queryByRole('link', { name: /Ir para Busca/i })).not.toBeInTheDocument();
    });
  });

  describe('AC22: Logged-in user state', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: { email: 'test@example.com', id: '123' },
        loading: false,
      });
    });

    it('should show "Ir para Busca" button when authenticated', () => {
      render(<NavbarAuthCTA />);

      const buscarLink = screen.getByRole('link', { name: /Ir para Busca/i });
      expect(buscarLink).toBeInTheDocument();
      expect(buscarLink).toHaveAttribute('href', '/buscar');
    });

    it('should NOT show "Entrar" link when authenticated', () => {
      render(<NavbarAuthCTA />);

      expect(screen.queryByRole('link', { name: /Entrar/i })).not.toBeInTheDocument();
    });

    it('should NOT show "Comece Gratis" link when authenticated', () => {
      render(<NavbarAuthCTA />);

      expect(screen.queryByRole('link', { name: /Comece Gratis/i })).not.toBeInTheDocument();
    });

    it('should maintain button styling consistency for logged-in state', () => {
      render(<NavbarAuthCTA />);

      const buscarLink = screen.getByRole('link', { name: /Ir para Busca/i });

      // Check that button has the primary CTA styling classes
      const className = buscarLink.className;
      expect(className).toContain('bg-brand-navy');
      expect(className).toContain('text-white');
      expect(className).toContain('rounded-button');
      expect(className).toContain('font-medium');
    });
  });
});

describe('LandingNavbar — NavScrollButton (client island)', () => {
  it('should render Como Funciona button', () => {
    render(<NavScrollButton sectionId="como-funciona" label="Como Funciona" />);

    const btn = screen.getByRole('button', { name: /Como Funciona/i });
    expect(btn).toBeInTheDocument();
  });
});

describe('LandingNavbar — Static RSC elements', () => {
  // These test the RSC output. Since RSC imports client islands,
  // we test LandingNavbar as a whole (it renders fine in Jest since
  // there's no actual server boundary in test — all code runs in jsdom).
  // Import the full component for integration-level checks.
  beforeEach(() => {
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
    });
  });

  // We import dynamically to avoid module-level execution issues
  // with the RSC that imports client islands
  const LandingNavbar = require('@/app/components/landing/LandingNavbar').default;

  it('should always show SmartLic logo', () => {
    render(<LandingNavbar />);

    const logo = screen.getByRole('link', { name: /SmartLic/i });
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute('href', '/');
    expect(logo).toHaveTextContent('SmartLic.tech');
  });

  it('should show Planos link', () => {
    render(<LandingNavbar />);

    const planosLink = screen.getByRole('link', { name: /^Planos$/i });
    expect(planosLink).toBeInTheDocument();
    expect(planosLink).toHaveAttribute('href', '/planos');
  });

  it('should show Como Funciona button', () => {
    render(<LandingNavbar />);

    const comoFuncionaBtn = screen.getByRole('button', { name: /Como Funciona/i });
    expect(comoFuncionaBtn).toBeInTheDocument();
  });

  it('should render sticky header', () => {
    const { container } = render(<LandingNavbar />);

    const header = container.querySelector('header');
    expect(header).toHaveClass('sticky');
    expect(header).toHaveClass('top-0');
    expect(header).toHaveClass('z-50');
  });
});
