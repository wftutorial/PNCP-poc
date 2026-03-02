import { render, screen, waitFor } from '@testing-library/react';

// Mock useInView — jsdom has no IntersectionObserver
jest.mock('../../app/hooks/useInView', () => ({
  useInView: () => ({ ref: { current: null }, isInView: true }),
}));

// STORY-351 AC7: Mock fetch for discard-rate endpoint
const mockFetch = jest.fn();
beforeEach(() => {
  mockFetch.mockReset();
  global.fetch = mockFetch;
});

import StatsSection from '@/app/components/landing/StatsSection';

describe('StatsSection', () => {
  it('renders section title', () => {
    mockFetch.mockResolvedValue({ ok: true, json: () => Promise.resolve({ discard_rate_pct: 0, sample_size: 0 }) });
    render(<StatsSection />);

    expect(screen.getByText(/Impacto real no mercado de licitações/i)).toBeInTheDocument();
  });

  it('renders hero stat — 15 setores (with counter animation)', async () => {
    mockFetch.mockResolvedValue({ ok: true, json: () => Promise.resolve({ discard_rate_pct: 0, sample_size: 0 }) });
    render(<StatsSection />);

    // Wait for counter animation to complete (1200ms)
    await waitFor(() => {
      expect(screen.getByText('15')).toBeInTheDocument();
    }, { timeout: 3000 });
    expect(screen.getByText(/setores especializados/i)).toBeInTheDocument();
  });

  it('renders dynamic discard rate from API (STORY-351 AC4/AC6)', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ discard_rate_pct: 91.2, sample_size: 150 }),
    });
    render(<StatsSection />);

    // Wait for API fetch + counter animation
    await waitFor(() => {
      expect(screen.getByText('91%')).toBeInTheDocument();
    }, { timeout: 3000 });
    expect(screen.getByText(/de editais descartados/i)).toBeInTheDocument();
  });

  it('shows fallback "A maioria" when API returns no data (STORY-351 AC4)', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ discard_rate_pct: 0, sample_size: 0 }),
    });
    render(<StatsSection />);

    await waitFor(() => {
      expect(screen.getByText('A maioria')).toBeInTheDocument();
    }, { timeout: 3000 });
    expect(screen.getByText(/de editais descartados/i)).toBeInTheDocument();
  });

  it('shows fallback "A maioria" when API fails (STORY-351 AC4)', async () => {
    mockFetch.mockRejectedValue(new Error('Network error'));
    render(<StatsSection />);

    await waitFor(() => {
      expect(screen.getByText('A maioria')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('shows loading state before API responds (STORY-351 AC6)', () => {
    // Never resolve the fetch
    mockFetch.mockReturnValue(new Promise(() => {}));
    render(<StatsSection />);

    // Loading pulse element should be present
    const pulseEl = document.querySelector('.animate-pulse');
    expect(pulseEl).toBeInTheDocument();
  });

  it('renders 3 supporting stats with counter animation (SAB-006 AC2/AC6)', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ discard_rate_pct: 87.5, sample_size: 100 }),
    });
    render(<StatsSection />);

    // Wait for counter animation to complete
    await waitFor(() => {
      expect(screen.getByText('88%')).toBeInTheDocument();
    }, { timeout: 3000 });

    expect(screen.getByText(/de editais descartados/i)).toBeInTheDocument();

    expect(screen.getByText('1000+')).toBeInTheDocument();
    expect(screen.getByText(/regras de filtragem/i)).toBeInTheDocument();

    expect(screen.getByText('27')).toBeInTheDocument();
    expect(screen.getByText(/estados cobertos/i)).toBeInTheDocument();
  });

  it('starts counters at 0 before animation (SAB-006 AC6 — FOUC fix)', () => {
    mockFetch.mockReturnValue(new Promise(() => {}));
    render(<StatsSection />);

    // Initial render: counters start at 0 but section has opacity: 0 → no FOUC
    const zeros = screen.getAllByText('0');
    expect(zeros.length).toBeGreaterThan(0);
  });

  it('uses hero number layout', () => {
    mockFetch.mockResolvedValue({ ok: true, json: () => Promise.resolve({ discard_rate_pct: 0, sample_size: 0 }) });
    const { container } = render(<StatsSection />);

    const heroNumber = container.querySelector('.text-5xl, .text-6xl, .text-7xl, .lg\\:text-7xl');
    expect(heroNumber).toBeInTheDocument();
  });

  it('uses design system tokens', () => {
    mockFetch.mockResolvedValue({ ok: true, json: () => Promise.resolve({ discard_rate_pct: 0, sample_size: 0 }) });
    const { container } = render(<StatsSection />);

    expect(container.querySelector('.text-brand-navy')).toBeInTheDocument();
    expect(container.querySelector('.text-brand-blue')).toBeInTheDocument();
    expect(container.querySelector('.bg-brand-blue-subtle\\/50')).toBeInTheDocument();
  });

  it('uses tabular-nums for numerical data', () => {
    mockFetch.mockResolvedValue({ ok: true, json: () => Promise.resolve({ discard_rate_pct: 0, sample_size: 0 }) });
    const { container } = render(<StatsSection />);

    const tabularNums = container.querySelectorAll('.tabular-nums');
    expect(tabularNums.length).toBeGreaterThan(0);
  });

  it('has accessible aria-labels for all stats', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ discard_rate_pct: 0, sample_size: 0 }),
    });
    render(<StatsSection />);

    // Wait for fetch to settle
    await waitFor(() => {
      expect(screen.getByText('A maioria')).toBeInTheDocument();
    }, { timeout: 3000 });

    expect(screen.getByRole('text', { name: '15 setores especializados' })).toBeInTheDocument();
    expect(screen.getByRole('text', { name: 'A maioria dos editais descartados' })).toBeInTheDocument();
    expect(screen.getByRole('text', { name: '1000+ regras de filtragem' })).toBeInTheDocument();
    expect(screen.getByRole('text', { name: '27 estados cobertos' })).toBeInTheDocument();
  });

  it('has dynamic aria-label when API returns data (STORY-351)', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ discard_rate_pct: 92.0, sample_size: 50 }),
    });
    render(<StatsSection />);

    await waitFor(() => {
      expect(screen.getByRole('text', { name: '92% de editais descartados' })).toBeInTheDocument();
    }, { timeout: 3000 });
  });
});
