import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import HeroSection from '@/app/components/landing/HeroSection';

describe('HeroSection', () => {
  it('renders headline with financial impact positioning (GTM-COPY-001 AC1)', () => {
    render(<HeroSection />);

    expect(screen.getByText(/Pare de perder dinheiro/i)).toBeInTheDocument();
    expect(screen.getByText(/com licitações erradas/i)).toBeInTheDocument();
  });

  it('renders subheadline explaining filtering mechanism (GTM-COPY-001 AC2)', () => {
    render(<HeroSection />);

    expect(screen.getByText(/O SmartLic analisa cada edital contra o perfil da sua empresa/i)).toBeInTheDocument();
    expect(screen.getByText(/justificativa objetiva/i)).toBeInTheDocument();
  });

  it('renders primary CTA with action verb (GTM-COPY-002 AC1)', () => {
    render(<HeroSection />);

    const primaryCTA = screen.getByRole('button', { name: /Ver oportunidades para meu setor/i });
    expect(primaryCTA).toBeInTheDocument();
  });

  it('renders stats badges with trust signals (AC4)', () => {
    render(<HeroSection />);

    expect(screen.getByText(/setores especializados/i)).toBeInTheDocument();
    expect(screen.getByText(/de editais descartados/i)).toBeInTheDocument();
    expect(screen.getByText(/UFs cobertas/i)).toBeInTheDocument();
  });

  it('renders secondary CTA button linking to proof-of-value', () => {
    render(<HeroSection />);

    const secondaryCTA = screen.getByRole('button', { name: /Ver exemplo de análise real/i });
    expect(secondaryCTA).toBeInTheDocument();
  });

  it('scrolls to proof-of-value section when secondary CTA is clicked', async () => {
    const user = userEvent.setup();

    const mockScrollIntoView = jest.fn();
    const mockElement = { scrollIntoView: mockScrollIntoView };
    jest.spyOn(document, 'getElementById').mockReturnValue(mockElement as any);

    render(<HeroSection />);

    const secondaryCTA = screen.getByRole('button', { name: /Ver exemplo de análise real/i });
    await user.click(secondaryCTA);

    expect(document.getElementById).toHaveBeenCalledWith('proof-of-value');
    expect(mockScrollIntoView).toHaveBeenCalledWith({
      behavior: 'smooth',
      block: 'start',
    });
  });

  it('does NOT use forbidden terms (AC11)', () => {
    const { container } = render(<HeroSection />);
    const text = container.textContent || '';

    expect(text).not.toMatch(/economize.*tempo/i);
    expect(text).not.toMatch(/busca rápida/i);
    expect(text).not.toMatch(/ferramenta de busca/i);
    expect(text).not.toMatch(/planilha automatizada/i);
    expect(text).not.toMatch(/10h\/semana/i);
    // GTM-COPY-001 banned phrases
    expect(text).not.toMatch(/inteligência automatizada/i);
    expect(text).not.toMatch(/inovador/i);
  });

  it('uses design system tokens for styling', () => {
    const { container } = render(<HeroSection />);

    expect(container.querySelector('.text-ink')).toBeInTheDocument();
    expect(container.querySelector('.text-gradient')).toBeInTheDocument();
  });
});
