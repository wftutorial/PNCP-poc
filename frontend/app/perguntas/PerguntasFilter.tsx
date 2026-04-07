'use client';

import { useState } from 'react';
import Link from 'next/link';
import { type QuestionCategory, CATEGORY_META, type Question } from '@/lib/questions';

const ALL_CATEGORIES = Object.keys(CATEGORY_META) as QuestionCategory[];

export default function PerguntasFilter({ questions }: { questions: Question[] }) {
  const [activeCategory, setActiveCategory] = useState<QuestionCategory | 'all'>('all');
  const [search, setSearch] = useState('');

  const filtered = questions.filter((q) => {
    const matchesCategory = activeCategory === 'all' || q.category === activeCategory;
    const matchesSearch = search === '' || q.title.toLowerCase().includes(search.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const grouped = ALL_CATEGORIES.reduce((acc, cat) => {
    const catQuestions = filtered.filter((q) => q.category === cat);
    if (catQuestions.length > 0) acc[cat] = catQuestions;
    return acc;
  }, {} as Record<QuestionCategory, Question[]>);

  return (
    <div>
      {/* Search */}
      <div className="mb-6">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar perguntas..."
          className="w-full max-w-md px-4 py-2 rounded-lg border border-[var(--border)] bg-surface-0 text-ink-primary placeholder:text-ink-muted focus:outline-none focus:ring-2 focus:ring-brand-blue/30"
        />
      </div>

      {/* Category tabs */}
      <div className="flex flex-wrap gap-2 mb-8">
        <button
          onClick={() => setActiveCategory('all')}
          className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
            activeCategory === 'all'
              ? 'bg-brand-blue text-white'
              : 'bg-surface-1 text-ink-secondary hover:bg-surface-2'
          }`}
        >
          Todas ({questions.length})
        </button>
        {ALL_CATEGORIES.map((cat) => {
          const count = questions.filter((q) => q.category === cat).length;
          return (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                activeCategory === cat
                  ? 'bg-brand-blue text-white'
                  : 'bg-surface-1 text-ink-secondary hover:bg-surface-2'
              }`}
            >
              {CATEGORY_META[cat].label} ({count})
            </button>
          );
        })}
      </div>

      {/* Question list grouped by category */}
      {Object.entries(grouped).map(([cat, catQuestions]) => (
        <div key={cat} className="mb-10">
          <h2 className="text-xl font-bold text-ink-primary mb-1">
            {CATEGORY_META[cat as QuestionCategory].label}
          </h2>
          <p className="text-sm text-ink-muted mb-4">
            {CATEGORY_META[cat as QuestionCategory].description}
          </p>
          <div className="space-y-3">
            {catQuestions.map((q) => (
              <Link
                key={q.slug}
                href={`/perguntas/${q.slug}`}
                className="block p-4 rounded-xl border border-[var(--border)] hover:border-brand-blue/30 hover:shadow-sm transition-all"
              >
                <h3 className="text-base font-semibold text-ink-primary">{q.title}</h3>
                <p className="text-sm text-ink-secondary mt-1 line-clamp-2">
                  {q.answer.slice(0, 150)}...
                </p>
                {q.legalBasis && (
                  <span className="inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full bg-amber-50 text-amber-700">
                    {q.legalBasis}
                  </span>
                )}
              </Link>
            ))}
          </div>
        </div>
      ))}

      {filtered.length === 0 && (
        <p className="text-center text-ink-muted py-12">
          Nenhuma pergunta encontrada para &quot;{search}&quot;.
        </p>
      )}
    </div>
  );
}
