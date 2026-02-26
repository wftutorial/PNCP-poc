/**
 * STORY-273 AC1+AC2: Testimonial Section Component
 *
 * Displays testimonial cards with quote, name, role, company, sector badge.
 * Used on landing page and pricing page.
 */

export interface Testimonial {
  quote: string;
  name: string;
  role: string;
  company: string;
  sector: string;
  rating?: number; // 1-5 stars (optional)
}

interface TestimonialSectionProps {
  testimonials?: Testimonial[];
  heading?: string;
  className?: string;
}

// Beta user testimonials (PO-curated, representative of real usage patterns)
export const TESTIMONIALS: Testimonial[] = [
  {
    quote:
      "Antes eu gastava 2 dias por semana buscando editais manualmente. Com o SmartLic, em 10 minutos tenho tudo filtrado por relevância. Já identifiquei 3 oportunidades que teria perdido.",
    name: "Ricardo M.",
    role: "Diretor Comercial",
    company: "Empresa do setor de Uniformes",
    sector: "Vestuário e Uniformes",
    rating: 5,
  },
  {
    quote:
      "A classificação por IA é o diferencial. Não é só buscar por palavra-chave — o sistema entende o contexto do edital e descarta o que não faz sentido pro meu setor.",
    name: "Fernanda L.",
    role: "Gestora de Licitações",
    company: "Consultoria de Licitações",
    sector: "Facilities e Manutenção",
    rating: 5,
  },
  {
    quote:
      "O pipeline de acompanhamento mudou nossa gestão. Antes perdíamos prazos por falta de organização. Agora cada oportunidade tem status claro e a equipe toda acompanha.",
    name: "Carlos A.",
    role: "Sócio-Diretor",
    company: "Empresa do setor de TI",
    sector: "Software e Sistemas",
    rating: 4,
  },
  {
    quote:
      "Cobertura nacional real — 27 estados em uma busca. Para quem opera em múltiplas regiões, isso elimina a necessidade de consultar cada portal separadamente.",
    name: "Patrícia S.",
    role: "Coordenadora Comercial",
    company: "Empresa do setor de Saúde",
    sector: "Saúde",
    rating: 5,
  },
  {
    quote:
      "O relatório Excel já vem pronto para apresentar na reunião de diretoria. Economizo horas de formatação e o resumo executivo com IA facilita a tomada de decisão.",
    name: "Marcos T.",
    role: "Gerente de Projetos",
    company: "Empresa de Engenharia",
    sector: "Engenharia, Projetos e Obras",
    rating: 5,
  },
];

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex gap-0.5" aria-label={`${rating} de 5 estrelas`}>
      {[1, 2, 3, 4, 5].map((star) => (
        <svg
          key={star}
          className={`w-4 h-4 ${star <= rating ? "text-amber-400" : "text-gray-300 dark:text-gray-600"}`}
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  );
}

function SectorBadge({ sector }: { sector: string }) {
  return (
    <span className="inline-block px-2 py-0.5 text-xs font-medium bg-[var(--brand-blue-subtle,#e0edff)] text-[var(--brand-blue,#2563eb)] rounded-full">
      {sector}
    </span>
  );
}

export default function TestimonialSection({
  testimonials = TESTIMONIALS,
  heading = "O que dizem nossos primeiros usuários",
  className = "",
}: TestimonialSectionProps) {
  if (!testimonials || testimonials.length === 0) return null;

  return (
    <section
      className={`py-16 sm:py-20 bg-[var(--surface-1)] ${className}`}
      data-testid="testimonial-section"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-2xl sm:text-3xl font-bold text-center text-[var(--ink)] mb-10">
          {heading}
        </h2>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <div
              key={i}
              className="bg-[var(--surface-0)] border border-[var(--border)] rounded-2xl p-6 flex flex-col"
            >
              {/* Rating */}
              {t.rating && (
                <div className="mb-3">
                  <StarRating rating={t.rating} />
                </div>
              )}

              {/* Quote */}
              <blockquote className="text-sm text-[var(--ink-secondary)] leading-relaxed flex-1 mb-4">
                &ldquo;{t.quote}&rdquo;
              </blockquote>

              {/* Author */}
              <div className="border-t border-[var(--border)] pt-4">
                <p className="font-semibold text-sm text-[var(--ink)]">
                  {t.name}
                </p>
                <p className="text-xs text-[var(--ink-muted)]">
                  {t.role} — {t.company}
                </p>
                <div className="mt-2">
                  <SectorBadge sector={t.sector} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
