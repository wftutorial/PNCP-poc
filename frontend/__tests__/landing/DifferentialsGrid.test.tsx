import { render, screen } from '@testing-library/react';
import DifferentialsGrid from '@/app/components/landing/DifferentialsGrid';

describe('DifferentialsGrid', () => {
  it('renders section title with risk elimination positioning (GTM-COPY-001 AC6)', () => {
    render(<DifferentialsGrid />);

    expect(screen.getByText(/Cada funcionalidade elimina um risco real/i)).toBeInTheDocument();
  });

  it('renders subtitle focused on waste reduction', () => {
    render(<DifferentialsGrid />);

    expect(screen.getByText(/Menos ruído, menos desperdício, mais retorno/i)).toBeInTheDocument();
  });

  it('renders 4 value differentials with correct titles (GTM-COPY-001 AC6)', () => {
    render(<DifferentialsGrid />);

    expect(screen.getByText('FOCO NO QUE PAGA')).toBeInTheDocument();
    expect(screen.getByText('DESCARTE SEM LER 100 PÁGINAS')).toBeInTheDocument();
    expect(screen.getByText('DECISÃO COM DADOS, NÃO ACHISMO')).toBeInTheDocument();
    expect(screen.getByText('NENHUM EDITAL INVISÍVEL')).toBeInTheDocument();
  });

  it('renders bullet points for each differential (AC6)', () => {
    render(<DifferentialsGrid />);

    // FOCO NO QUE PAGA
    expect(screen.getByText(/Cruza cada edital com o perfil da sua empresa/i)).toBeInTheDocument();
    expect(screen.getByText(/Descarta automaticamente o que não se encaixa/i)).toBeInTheDocument();
    expect(screen.getByText(/Direciona esforço para editais com retorno real/i)).toBeInTheDocument();

    // DESCARTE SEM LER 100 PÁGINAS
    expect(screen.getByText(/Avaliação objetiva de cada edital por IA/i)).toBeInTheDocument();
    expect(screen.getByText(/Justificativa para cada recomendação/i)).toBeInTheDocument();
    expect(screen.getByText(/Decisão em segundos, não em horas/i)).toBeInTheDocument();

    // DECISÃO COM DADOS, NÃO ACHISMO
    expect(screen.getByText(/Critérios objetivos de compatibilidade/i)).toBeInTheDocument();
    expect(screen.getByText(/Dados verificados de fontes oficiais/i)).toBeInTheDocument();
    expect(screen.getByText(/Justificativa transparente/i)).toBeInTheDocument();

    // NENHUM EDITAL INVISÍVEL
    expect(screen.getByText(/27 estados cobertos automaticamente/i)).toBeInTheDocument();
    expect(screen.getByText(/Fontes oficiais consolidadas/i)).toBeInTheDocument();
    expect(screen.getByText(/Se existe e é compatível, você sabe/i)).toBeInTheDocument();
  });

  it('uses 1+3 asymmetric layout', () => {
    const { container } = render(<DifferentialsGrid />);

    expect(container.querySelector('.lg\\:col-span-4')).toBeInTheDocument();

    const smallCards = container.querySelectorAll('.lg\\:col-span-1');
    expect(smallCards.length).toBe(3);
  });

  it('does NOT use forbidden terms (AC11)', () => {
    const { container } = render(<DifferentialsGrid />);
    const text = container.textContent || '';

    expect(text).not.toMatch(/busca rápida/i);
    expect(text).not.toMatch(/ferramenta de busca/i);
    expect(text).not.toMatch(/planilha automatizada/i);
    expect(text).not.toMatch(/inteligência automatizada/i);
  });

  it('uses design system colors', () => {
    const { container } = render(<DifferentialsGrid />);

    expect(container.querySelector('.bg-brand-navy')).toBeInTheDocument();
    expect(container.querySelector('.bg-surface-1')).toBeInTheDocument();
  });
});
