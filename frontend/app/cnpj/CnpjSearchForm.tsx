'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';

function formatCnpj(value: string): string {
  const digits = value.replace(/\D/g, '').slice(0, 14);
  if (digits.length <= 2) return digits;
  if (digits.length <= 5) return `${digits.slice(0, 2)}.${digits.slice(2)}`;
  if (digits.length <= 8) return `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5)}`;
  if (digits.length <= 12) return `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5, 8)}/${digits.slice(8)}`;
  return `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5, 8)}/${digits.slice(8, 12)}-${digits.slice(12)}`;
}

export default function CnpjSearchForm() {
  const [cnpj, setCnpj] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const digits = cnpj.replace(/\D/g, '');
    if (digits.length !== 14) {
      setError('CNPJ deve ter 14 dígitos');
      return;
    }
    setError('');
    router.push(`/cnpj/${digits}`);
  };

  return (
    <form onSubmit={handleSubmit} className="not-prose mt-8 max-w-lg mx-auto">
      <div className="flex gap-3">
        <div className="flex-1">
          <label htmlFor="cnpj-input" className="sr-only">CNPJ</label>
          <input
            id="cnpj-input"
            type="text"
            value={cnpj}
            onChange={(e) => {
              setCnpj(formatCnpj(e.target.value));
              setError('');
            }}
            placeholder="00.000.000/0000-00"
            className="w-full rounded-lg border border-gray-300 px-4 py-3 text-gray-900 text-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            maxLength={18}
            inputMode="numeric"
          />
        </div>
        <button
          type="submit"
          className="px-6 py-3 rounded-lg font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-colors whitespace-nowrap"
        >
          Consultar
        </button>
      </div>
      {error && <p className="text-red-600 text-sm mt-2">{error}</p>}
      <p className="text-sm text-gray-500 mt-3">
        Digite o CNPJ da empresa que deseja consultar.
        Exemplo: 09.225.035/0001-01
      </p>
    </form>
  );
}
