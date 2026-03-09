"use client";

import { useState } from "react";

export function KeywordsInput({
  keywords,
  onChange,
}: {
  keywords: string[];
  onChange: (kws: string[]) => void;
}) {
  const [input, setInput] = useState("");

  const addKeyword = () => {
    const trimmed = input.trim();
    if (trimmed && !keywords.includes(trimmed)) {
      onChange([...keywords, trimmed]);
    }
    setInput("");
  };

  const removeKeyword = (kw: string) => {
    onChange(keywords.filter((k) => k !== kw));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addKeyword();
    }
    if (e.key === "Backspace" && input === "" && keywords.length > 0) {
      removeKeyword(keywords[keywords.length - 1]);
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium text-[var(--ink)] mb-1.5">
        Palavras-chave
      </label>
      <div className="flex flex-wrap gap-1.5 p-2 min-h-[42px] rounded-lg border border-[var(--border)] bg-[var(--surface-0)] focus-within:border-[var(--brand-blue)] focus-within:ring-1 focus-within:ring-[var(--brand-blue)]/20 transition-colors">
        {keywords.map((kw) => (
          <span
            key={kw}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-[var(--brand-blue-subtle)] text-[var(--brand-blue)]"
          >
            {kw}
            <button
              type="button"
              onClick={() => removeKeyword(kw)}
              className="ml-0.5 hover:text-[var(--error)] transition-colors"
              aria-label={`Remover "${kw}"`}
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          </span>
        ))}
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={addKeyword}
          placeholder={keywords.length === 0 ? "Digite e pressione Enter..." : ""}
          className="flex-1 min-w-[120px] border-none outline-none bg-transparent text-sm text-[var(--ink)] placeholder:text-[var(--ink-muted)]"
        />
      </div>
      <p className="text-[11px] text-[var(--ink-muted)] mt-1">
        Pressione Enter ou vírgula para adicionar. Backspace remove a última.
      </p>
    </div>
  );
}
