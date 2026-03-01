"use client";

import { useState, useCallback, useRef, useEffect, type ChangeEvent } from "react";

interface CurrencyInputProps {
  /** Numeric value (unformatted, e.g. 1500000) */
  value: string | number;
  /** Called with raw numeric value as string (e.g. "1500000") */
  onChange: (rawValue: string) => void;
  /** Input placeholder */
  placeholder?: string;
  /** HTML id */
  id?: string;
  /** Additional CSS classes */
  className?: string;
  /** Minimum value */
  min?: number;
}

/**
 * Format a raw numeric string to BRL display format.
 * "1500000" → "1.500.000"
 * "250050" → "250.050"
 */
function formatToBRL(raw: string): string {
  // Remove everything that's not a digit
  const digits = raw.replace(/\D/g, "");
  if (!digits) return "";
  // Add thousands separators
  return Number(digits).toLocaleString("pt-BR");
}

/**
 * Extract raw digits from a pasted/input string.
 * "R$ 2.500.000,00" → "2500000"
 * "1.500.000" → "1500000"
 */
function extractDigits(input: string): string {
  // Remove R$, spaces, dots (thousands sep), commas and decimals
  let cleaned = input.replace(/R\$\s*/g, "").trim();
  // If there's a comma (decimal separator in pt-BR), take only integer part
  const commaIdx = cleaned.indexOf(",");
  if (commaIdx !== -1) {
    cleaned = cleaned.substring(0, commaIdx);
  }
  return cleaned.replace(/\D/g, "");
}

export function CurrencyInput({
  value,
  onChange,
  placeholder = "0",
  id,
  className = "",
  min = 0,
}: CurrencyInputProps) {
  const rawDigits = String(value).replace(/\D/g, "");
  const [displayValue, setDisplayValue] = useState(() => formatToBRL(rawDigits));
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync display when external value changes
  useEffect(() => {
    const digits = String(value).replace(/\D/g, "");
    setDisplayValue(formatToBRL(digits));
  }, [value]);

  const handleChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const input = e.target.value;
      const digits = extractDigits(input);
      const formatted = formatToBRL(digits);
      setDisplayValue(formatted);
      onChange(digits);
    },
    [onChange]
  );

  const handlePaste = useCallback(
    (e: React.ClipboardEvent<HTMLInputElement>) => {
      e.preventDefault();
      const pasted = e.clipboardData.getData("text");
      const digits = extractDigits(pasted);
      const formatted = formatToBRL(digits);
      setDisplayValue(formatted);
      onChange(digits);
    },
    [onChange]
  );

  return (
    <div className="relative">
      <span
        className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-[var(--ink-muted)] pointer-events-none select-none"
        aria-hidden="true"
      >
        R$
      </span>
      <input
        ref={inputRef}
        id={id}
        type="text"
        inputMode="numeric"
        value={displayValue}
        onChange={handleChange}
        onPaste={handlePaste}
        placeholder={placeholder}
        min={min}
        className={`w-full pl-9 pr-3 py-2 rounded-lg border border-[var(--border)] bg-[var(--surface-0)]
                    text-sm text-[var(--ink)] placeholder:text-[var(--ink-muted)]
                    focus:border-[var(--brand-blue)] focus:ring-1 focus:ring-[var(--brand-blue)]/20
                    outline-none transition-colors ${className}`}
        data-testid="currency-input"
        aria-label="Valor em reais"
      />
    </div>
  );
}
