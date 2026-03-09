import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import GoogleSheetsExportButton from '@/app/buscar/components/GoogleSheetsExportButton';

// Mock sonner toast — must use jest.fn() inside factory to avoid hoisting issues
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
  },
}));

// Import mocked toast after jest.mock is applied
import { toast as mockToast } from 'sonner';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock window.open
const mockOpen = jest.fn();
window.open = mockOpen;

const defaultProps = {
  licitacoes: [
    { pncp_id: '1', objeto: 'Test', orgao: 'Org', valor: 1000, uf: 'SP' },
  ],
  searchLabel: 'Test - SP',
  session: { access_token: 'valid-token' },
};

describe('GoogleSheetsExportButton', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // AC19: Success → toast + new tab
  it('shows success toast and opens spreadsheet on successful export', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: { get: (k: string) => k === 'content-type' ? 'application/json' : null },
      json: async () => ({
        spreadsheet_url: 'https://docs.google.com/spreadsheets/d/123',
        total_rows: 1,
      }),
    });

    render(<GoogleSheetsExportButton {...defaultProps} />);
    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(mockToast.success).toHaveBeenCalledWith(
        'Planilha criada com sucesso!',
        expect.objectContaining({
          description: expect.stringContaining('1 licitações exportadas'),
        })
      );
    });
    expect(mockOpen).toHaveBeenCalledWith(
      'https://docs.google.com/spreadsheets/d/123',
      '_blank',
      'noopener,noreferrer'
    );
  });

  // AC20: 401 error → toast "Reconecte"
  it('shows reconnect toast on 401 error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      headers: { get: (k: string) => k === 'content-type' ? 'application/json' : null },
      json: async () => ({ detail: 'Google Sheets não autorizado' }),
    });

    // Mock setTimeout to prevent actual redirect
    jest.useFakeTimers();

    render(<GoogleSheetsExportButton {...defaultProps} />);
    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(mockToast.info).toHaveBeenCalledWith(
        'Conectando ao Google Sheets...',
        expect.any(Object)
      );
    });

    jest.useRealTimers();
  });

  // AC17: 403 → "Permissão revogada"
  it('shows permission revoked toast on 403 error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 403,
      headers: { get: (k: string) => k === 'content-type' ? 'application/json' : null },
      json: async () => ({ detail: 'Forbidden' }),
    });

    render(<GoogleSheetsExportButton {...defaultProps} />);
    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith(
        'Falha ao exportar para Google Sheets',
        expect.objectContaining({
          description: expect.stringContaining('permissão'),
        })
      );
    });
  });

  // AC17: 429 → "Limite Google atingido"
  it('shows rate limit toast on 429 error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 429,
      headers: { get: (k: string) => k === 'content-type' ? 'application/json' : null },
      json: async () => ({ detail: 'Rate limited' }),
    });

    render(<GoogleSheetsExportButton {...defaultProps} />);
    fireEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith(
        'Falha ao exportar para Google Sheets',
        expect.objectContaining({
          description: expect.stringContaining('Limite'),
        })
      );
    });
  });

  // Disabled when no results
  it('is disabled when licitacoes is empty', () => {
    render(<GoogleSheetsExportButton {...defaultProps} licitacoes={[]} />);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  // Has aria-label
  it('has aria-label for accessibility', () => {
    render(<GoogleSheetsExportButton {...defaultProps} />);
    expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Exportar para Google Sheets');
  });
});
