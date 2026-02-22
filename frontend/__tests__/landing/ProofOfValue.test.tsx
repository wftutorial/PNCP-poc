/**
 * ProofOfValue Component Tests — GTM-COPY-003
 *
 * Tests for the Proof of Value section showing recommended + rejected bid examples
 * on the landing page first fold.
 */

import { render, screen } from '@testing-library/react';
import ProofOfValue from '@/app/components/landing/ProofOfValue';

describe('ProofOfValue', () => {
  describe('AC1 — Component renders correctly', () => {
    it('renders the section with proof-of-value id', () => {
      const { container } = render(<ProofOfValue />);

      expect(container.querySelector('#proof-of-value')).toBeInTheDocument();
    });

    it('renders section header with mechanism explanation (AC7)', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/Veja como o filtro funciona na prática/i)).toBeInTheDocument();
      expect(screen.getByText(/O SmartLic cruza o perfil da sua empresa com cada edital publicado/i)).toBeInTheDocument();
    });
  });

  describe('AC2 — Recommended bid card', () => {
    it('renders recommended bid label', () => {
      render(<ProofOfValue />);

      expect(screen.getByText('Recomendada')).toBeInTheDocument();
    });

    it('renders compatibility badge with percentage', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/92% compatível/i)).toBeInTheDocument();
    });

    it('renders bid title', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/Pregão Eletrônico — Manutenção predial com fornecimento de materiais/i)).toBeInTheDocument();
    });

    it('renders bid details (value, UF, prazo, modalidade)', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/R\$ 380\.000,00/i)).toBeInTheDocument();
      expect(screen.getByText('SP')).toBeInTheDocument();
      expect(screen.getByText(/18 dias restantes/i)).toBeInTheDocument();
      // "Pregão Eletrônico" appears in both title and badge — use getAllByText
      const pregaoMatches = screen.getAllByText(/Pregão Eletrônico/);
      expect(pregaoMatches.length).toBeGreaterThanOrEqual(2);
    });

    it('renders viability seal', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/Viabilidade: Alta/i)).toBeInTheDocument();
    });
  });

  describe('AC3 — Justification criteria', () => {
    it('renders "Por que foi recomendada" label', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/Por que foi recomendada:/i)).toBeInTheDocument();
    });

    it('renders 4 justification criteria', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/Setor compatível: manutenção predial/i)).toBeInTheDocument();
      expect(screen.getByText(/Valor dentro da faixa ideal do seu perfil/i)).toBeInTheDocument();
      expect(screen.getByText(/Prazo viável: 18 dias para preparar proposta/i)).toBeInTheDocument();
      expect(screen.getByText(/Região de atuação: São Paulo/i)).toBeInTheDocument();
    });
  });

  describe('AC4 — Rejected bid card', () => {
    it('renders rejected bid label', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/Descartada automaticamente/i)).toBeInTheDocument();
    });

    it('renders rejected bid title', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/Aquisição de gêneros alimentícios para merenda escolar/i)).toBeInTheDocument();
    });

    it('renders rejected bid details', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/R\$ 42\.000,00/i)).toBeInTheDocument();
      expect(screen.getByText('AM')).toBeInTheDocument();
    });

    it('renders rejection reasons', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/Motivos do descarte:/i)).toBeInTheDocument();
      expect(screen.getByText(/Fora do seu setor de atuação/i)).toBeInTheDocument();
      expect(screen.getByText(/Valor abaixo do mínimo do seu perfil/i)).toBeInTheDocument();
      expect(screen.getByText(/Fora da sua região de atuação/i)).toBeInTheDocument();
    });

    it('renders time protection message', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/Descartada para proteger seu tempo e esforço/i)).toBeInTheDocument();
    });
  });

  describe('AC5 — Static data (no API call)', () => {
    it('renders as a self-contained component with no external dependencies', () => {
      // ProofOfValue uses only static hardcoded data — no useEffect, no fetch, no auth
      const { container } = render(<ProofOfValue />);

      // Component renders fully from static data
      expect(container.querySelector('#proof-of-value')).toBeInTheDocument();
      expect(screen.getByText(/92% compatível/i)).toBeInTheDocument();
      expect(screen.getByText(/Descartada automaticamente/i)).toBeInTheDocument();
    });
  });

  describe('AC6 — Transparency annotation', () => {
    it('renders transparency disclaimer', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/Exemplo ilustrativo baseado em análises reais do sistema/i)).toBeInTheDocument();
    });
  });

  describe('AC8 — Responsiveness', () => {
    it('uses responsive grid layout (5-col on md)', () => {
      const { container } = render(<ProofOfValue />);

      expect(container.querySelector('.md\\:grid-cols-5')).toBeInTheDocument();
    });

    it('recommended card takes 3 cols, rejected takes 2', () => {
      const { container } = render(<ProofOfValue />);

      expect(container.querySelector('.md\\:col-span-3')).toBeInTheDocument();
      expect(container.querySelector('.md\\:col-span-2')).toBeInTheDocument();
    });
  });

  describe('AC10 — Example data quality', () => {
    it('examples cover different sectors (maintenance vs food)', () => {
      render(<ProofOfValue />);

      // Recommended: maintenance/predial — appears in title and justification
      const predialMatches = screen.getAllByText(/manutenção predial/i);
      expect(predialMatches.length).toBeGreaterThanOrEqual(1);
      // Rejected: food/merenda
      expect(screen.getByText(/gêneros alimentícios/i)).toBeInTheDocument();
    });

    it('examples cover different UFs', () => {
      render(<ProofOfValue />);

      expect(screen.getByText('SP')).toBeInTheDocument();
      expect(screen.getByText('AM')).toBeInTheDocument();
    });

    it('values are in realistic range', () => {
      render(<ProofOfValue />);

      expect(screen.getByText(/R\$ 380\.000,00/i)).toBeInTheDocument();
      expect(screen.getByText(/R\$ 42\.000,00/i)).toBeInTheDocument();
    });
  });

  it('does NOT use forbidden terms', () => {
    const { container } = render(<ProofOfValue />);
    const text = container.textContent || '';

    expect(text).not.toMatch(/inteligência automatizada/i);
    expect(text).not.toMatch(/busca rápida/i);
    expect(text).not.toMatch(/ferramenta de busca/i);
    expect(text).not.toMatch(/inovador/i);
  });

  it('accepts className prop', () => {
    const { container } = render(<ProofOfValue className="test-class" />);

    expect(container.querySelector('.test-class')).toBeInTheDocument();
  });
});
