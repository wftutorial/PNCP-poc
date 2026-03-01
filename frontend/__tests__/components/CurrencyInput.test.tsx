import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CurrencyInput } from '@/components/ui/CurrencyInput';

describe('CurrencyInput', () => {
  const defaultProps = {
    value: '',
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with R$ prefix', () => {
    render(<CurrencyInput {...defaultProps} />);
    expect(screen.getByText('R$')).toBeInTheDocument();
    expect(screen.getByTestId('currency-input')).toBeInTheDocument();
  });

  // AC26: Typing "1500000" → display "1.500.000", form state = 1500000
  it('formats typed digits with thousands separators', () => {
    const onChange = jest.fn();
    render(<CurrencyInput value="" onChange={onChange} />);
    const input = screen.getByTestId('currency-input');
    fireEvent.change(input, { target: { value: '1500000' } });
    expect(onChange).toHaveBeenCalledWith('1500000');
    // The displayed value should be formatted
    expect(input).toHaveValue('1.500.000');
  });

  // AC27: Pasting "R$ 2.500.000,00" → display "2.500.000", form state = 2500000
  it('handles paste of formatted BRL string', () => {
    const onChange = jest.fn();
    render(<CurrencyInput value="" onChange={onChange} />);
    const input = screen.getByTestId('currency-input');
    const clipboardData = {
      getData: () => 'R$ 2.500.000,00',
    };
    fireEvent.paste(input, { clipboardData });
    expect(onChange).toHaveBeenCalledWith('2500000');
    expect(input).toHaveValue('2.500.000');
  });

  // AC23: Backspace works correctly
  it('handles backspace by removing last digit', () => {
    const onChange = jest.fn();
    render(<CurrencyInput value="1500000" onChange={onChange} />);
    const input = screen.getByTestId('currency-input');
    // Simulate typing which removes last char
    fireEvent.change(input, { target: { value: '1.500.00' } });
    expect(onChange).toHaveBeenCalledWith('150000');
  });

  // AC24: Form state is raw numeric
  it('returns raw numeric string without formatting', () => {
    const onChange = jest.fn();
    render(<CurrencyInput value="" onChange={onChange} />);
    const input = screen.getByTestId('currency-input');
    fireEvent.change(input, { target: { value: '50000' } });
    expect(onChange).toHaveBeenCalledWith('50000');
  });

  // Empty input — clearing a value
  it('handles clearing input back to empty', () => {
    const onChange = jest.fn();
    render(<CurrencyInput value="50000" onChange={onChange} />);
    const input = screen.getByTestId('currency-input');
    // Clear the input
    fireEvent.change(input, { target: { value: '' } });
    expect(onChange).toHaveBeenCalledWith('');
  });

  // Syncs with external value
  it('syncs display when external value changes', () => {
    const { rerender } = render(<CurrencyInput value="" onChange={jest.fn()} />);
    rerender(<CurrencyInput value="250000" onChange={jest.fn()} />);
    expect(screen.getByTestId('currency-input')).toHaveValue('250.000');
  });

  // Placeholder
  it('shows placeholder when empty', () => {
    render(<CurrencyInput value="" onChange={jest.fn()} placeholder="0,00" />);
    expect(screen.getByTestId('currency-input')).toHaveAttribute('placeholder', '0,00');
  });

  // Custom id
  it('supports custom id for label association', () => {
    render(<CurrencyInput value="" onChange={jest.fn()} id="test-id" />);
    expect(screen.getByTestId('currency-input')).toHaveAttribute('id', 'test-id');
  });

  // aria-label
  it('has aria-label for accessibility', () => {
    render(<CurrencyInput value="" onChange={jest.fn()} />);
    expect(screen.getByTestId('currency-input')).toHaveAttribute('aria-label', 'Valor em reais');
  });

  // inputMode numeric
  it('uses numeric inputMode for mobile keyboards', () => {
    render(<CurrencyInput value="" onChange={jest.fn()} />);
    expect(screen.getByTestId('currency-input')).toHaveAttribute('inputMode', 'numeric');
  });
});
