import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Pagination } from '@/components/ui/Pagination';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('Pagination', () => {
  const defaultProps = {
    totalItems: 100,
    currentPage: 1,
    pageSize: 20 as const,
    onPageChange: jest.fn(),
    onPageSizeChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.clear();
  });

  // AC33: Renders correctly
  it('renders pagination info, prev/next buttons, and page indicator', () => {
    render(<Pagination {...defaultProps} />);
    expect(screen.getByTestId('pagination-info')).toHaveTextContent('Exibindo 1-20 de 100 oportunidades');
    expect(screen.getByTestId('pagination-prev')).toBeInTheDocument();
    expect(screen.getByTestId('pagination-next')).toBeInTheDocument();
    expect(screen.getByTestId('pagination-page-indicator')).toHaveTextContent('1 de 5');
  });

  // AC33: Navigation
  it('calls onPageChange when next is clicked', () => {
    render(<Pagination {...defaultProps} />);
    fireEvent.click(screen.getByTestId('pagination-next'));
    expect(defaultProps.onPageChange).toHaveBeenCalledWith(2);
  });

  it('calls onPageChange when prev is clicked', () => {
    render(<Pagination {...defaultProps} currentPage={3} />);
    fireEvent.click(screen.getByTestId('pagination-prev'));
    expect(defaultProps.onPageChange).toHaveBeenCalledWith(2);
  });

  // AC33: Prev disabled on page 1
  it('disables prev button on first page', () => {
    render(<Pagination {...defaultProps} currentPage={1} />);
    expect(screen.getByTestId('pagination-prev')).toBeDisabled();
  });

  // AC33: Next disabled on last page
  it('disables next button on last page', () => {
    render(<Pagination {...defaultProps} currentPage={5} />);
    expect(screen.getByTestId('pagination-next')).toBeDisabled();
  });

  // AC33: Page size persistence
  it('persists page size to localStorage on change', () => {
    render(<Pagination {...defaultProps} />);
    fireEvent.change(screen.getByTestId('page-size-select'), { target: { value: '50' } });
    expect(localStorageMock.getItem('smartlic_page_size')).toBe('50');
    expect(defaultProps.onPageSizeChange).toHaveBeenCalledWith(50);
    expect(defaultProps.onPageChange).toHaveBeenCalledWith(1);
  });

  // AC33: Reset page on pageSize change
  it('resets to page 1 when page size changes', () => {
    render(<Pagination {...defaultProps} currentPage={3} />);
    fireEvent.change(screen.getByTestId('page-size-select'), { target: { value: '10' } });
    expect(defaultProps.onPageChange).toHaveBeenCalledWith(1);
  });

  // AC36: Accessibility — aria-label on navigation
  it('has aria-label on prev and next buttons', () => {
    render(<Pagination {...defaultProps} />);
    expect(screen.getByTestId('pagination-prev')).toHaveAttribute('aria-label', 'Página anterior');
    expect(screen.getByTestId('pagination-next')).toHaveAttribute('aria-label', 'Próxima página');
  });

  // AC36: aria-current on page indicator
  it('has aria-current="page" on page indicator', () => {
    render(<Pagination {...defaultProps} />);
    expect(screen.getByTestId('pagination-page-indicator')).toHaveAttribute('aria-current', 'page');
  });

  // AC36: aria-disabled on disabled buttons
  it('has aria-disabled on disabled buttons', () => {
    render(<Pagination {...defaultProps} currentPage={1} />);
    expect(screen.getByTestId('pagination-prev')).toHaveAttribute('aria-disabled', 'true');
  });

  // AC7: Correct display for page 2
  it('shows correct range for page 2', () => {
    render(<Pagination {...defaultProps} currentPage={2} />);
    expect(screen.getByTestId('pagination-info')).toHaveTextContent('Exibindo 21-40 de 100 oportunidades');
  });

  // AC7: Correct display for last page with remainder
  it('shows correct range for last page', () => {
    render(<Pagination {...defaultProps} totalItems={105} currentPage={6} />);
    expect(screen.getByTestId('pagination-info')).toHaveTextContent('Exibindo 101-105 de 105 oportunidades');
  });

  // Navigation role
  it('has role="navigation" for accessibility', () => {
    render(<Pagination {...defaultProps} />);
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  // Does not render when no items
  it('does not render when totalItems is 0', () => {
    const { container } = render(<Pagination {...defaultProps} totalItems={0} />);
    expect(container.innerHTML).toBe('');
  });
});
