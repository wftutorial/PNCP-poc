/**
 * Tests for STORY-356 — Pipeline limit enforcement frontend handling.
 *
 * AC4: Frontend shows "Limite" state when backend returns 403 PIPELINE_LIMIT_EXCEEDED.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AddToPipelineButton } from '../../app/components/AddToPipelineButton';
import type { LicitacaoItem } from '../../app/types';

// Mock usePipeline hook
const mockAddItem = jest.fn();
jest.mock('../../hooks/usePipeline', () => ({
  usePipeline: () => ({
    addItem: mockAddItem,
    items: [],
    alerts: [],
    loading: false,
    error: null,
    total: 0,
    fetchItems: jest.fn(),
    fetchAlerts: jest.fn(),
    updateItem: jest.fn(),
    removeItem: jest.fn(),
  }),
}));

describe('STORY-356: Pipeline limit enforcement', () => {
  const mockLicitacao: LicitacaoItem = {
    pncp_id: "12345678-1-000001/2026",
    objeto: "Aquisicao de uniformes",
    orgao: "Prefeitura de Sao Paulo",
    uf: "SP",
    municipio: "Sao Paulo",
    valor: 150000,
    modalidade: "Pregao Eletronico",
    data_publicacao: "2026-02-01",
    data_abertura: "2026-02-15",
    data_encerramento: "2026-03-01",
    status_display: "Recebendo Proposta",
    link: "https://pncp.gov.br/app/editais/12345",
    relevance_score: 0.95,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows "Limite" when pipeline limit exceeded (AC4)', async () => {
    const limitError = new Error("Limite de 5 itens no pipeline atingido.");
    (limitError as any).isPipelineLimitExceeded = true;
    (limitError as any).limit = 5;
    (limitError as any).current = 5;
    mockAddItem.mockRejectedValue(limitError);

    render(<AddToPipelineButton licitacao={mockLicitacao} />);
    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(screen.getByText('Limite')).toBeInTheDocument();
    });
  });

  it('shows orange styling for limit state', async () => {
    const limitError = new Error("Limite de 5 itens no pipeline atingido.");
    (limitError as any).isPipelineLimitExceeded = true;
    (limitError as any).limit = 5;
    (limitError as any).current = 5;
    mockAddItem.mockRejectedValue(limitError);

    render(<AddToPipelineButton licitacao={mockLicitacao} />);
    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      const button = screen.getByRole('button');
      expect(button.className).toContain('bg-orange-100');
    });
  });

  it('shows limit message in title attribute', async () => {
    const limitError = new Error("Limite de 5 itens no pipeline atingido.");
    (limitError as any).isPipelineLimitExceeded = true;
    (limitError as any).limit = 5;
    (limitError as any).current = 5;
    mockAddItem.mockRejectedValue(limitError);

    render(<AddToPipelineButton licitacao={mockLicitacao} />);
    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('title', 'Limite de 5 itens no pipeline atingido.');
    });
  });

  it('resets to idle after 4 seconds', async () => {
    jest.useFakeTimers();
    const limitError = new Error("Limite de 5 itens no pipeline atingido.");
    (limitError as any).isPipelineLimitExceeded = true;
    mockAddItem.mockRejectedValue(limitError);

    render(<AddToPipelineButton licitacao={mockLicitacao} />);
    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(screen.getByText('Limite')).toBeInTheDocument();
    });

    jest.advanceTimersByTime(4000);

    await waitFor(() => {
      expect(screen.getByText('Pipeline')).toBeInTheDocument();
    });

    jest.useRealTimers();
  });

  it('distinguishes limit error from upgrade error', async () => {
    // Upgrade error (no isPipelineLimitExceeded flag)
    mockAddItem.mockRejectedValue(new Error('Pipeline nao disponivel no seu plano.'));

    render(<AddToPipelineButton licitacao={mockLicitacao} />);
    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(screen.getByText('Upgrade')).toBeInTheDocument();
    });
  });
});
