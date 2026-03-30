"use client";

import React, { useState, useRef, useCallback, useEffect, useId } from "react";

/** D-04 AC1: Viability factor breakdown */
export interface ViabilityFactors {
  modalidade: number;
  modalidade_label: string;
  timeline: number;
  timeline_label: string;
  value_fit: number;
  value_fit_label: string;
  geography: number;
  geography_label: string;
}

interface ViabilityBadgeProps {
  level?: "alta" | "media" | "baixa" | null;
  score?: number | null;
  factors?: ViabilityFactors | null;
  valueSource?: "estimated" | "missing" | null;
}

/** Factor label for tooltip display */
function factorLine(name: string, score: number, label: string): string {
  return `${name}: ${label} (${score}/100)`;
}

/** D-04 AC8: Viability badge with accessible tooltip showing factor breakdown
 * DEBT-FE-002: Replaces non-accessible title attribute with keyboard+touch tooltip (WCAG 2.1 AA)
 */
export default function ViabilityBadge({
  level,
  score,
  factors,
  valueSource,
}: ViabilityBadgeProps) {
  if (!level) return null;

  const config: Record<
    string,
    {
      label: string;
      ariaLabel: string;
      bg: string;
    }
  > = {
    alta: {
      label: "Viabilidade alta",
      ariaLabel: "Viabilidade alta para sua empresa",
      bg: "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300",
    },
    media: {
      label: "Viabilidade média",
      ariaLabel: "Viabilidade média para sua empresa",
      bg: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300",
    },
    baixa: {
      label: "Viabilidade baixa",
      ariaLabel: "Viabilidade baixa para sua empresa",
      bg: "bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400",
    },
  };

  const c = config[level] ?? config["baixa"];
  if (!c) return null;

  // Build tooltip lines
  const tooltipLines: string[] = [`Viabilidade: ${score ?? "?"}/100`];
  if (factors) {
    tooltipLines.push(
      factorLine("Modalidade", factors.modalidade, factors.modalidade_label),
      factorLine("Prazo", factors.timeline, factors.timeline_label),
      factorLine("Valor", factors.value_fit, factors.value_fit_label),
      factorLine("UF", factors.geography, factors.geography_label),
    );
  }
  if (valueSource === "missing") {
    tooltipLines.push(
      "⚠ Valor estimado não informado pelo órgão — viabilidade pode ser maior",
    );
  }

  // Icon: chart bar for viability (distinct from shield for confidence)
  const icon = (
    <svg
      className="w-3 h-3"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
      />
    </svg>
  );

  return (
    <ViabilityTooltip
      tooltipLines={tooltipLines}
      ariaLabel={c.ariaLabel}
      bg={c.bg}
      level={level}
    >
      {icon}
      {c.label}
    </ViabilityTooltip>
  );
}

/** DEBT-FE-002: Accessible tooltip wrapper
 * - Keyboard accessible (focusable trigger with role=img + aria-label)
 * - Mobile tap-to-toggle support
 * - ARIA: role="tooltip" + aria-describedby linkage
 * - Dismisses on Escape key and outside click
 */
function ViabilityTooltip({
  children,
  tooltipLines,
  ariaLabel,
  bg,
  level,
}: {
  children: React.ReactNode;
  tooltipLines: string[];
  ariaLabel: string;
  bg: string;
  level: string;
}) {
  const [open, setOpen] = useState(false);
  const tooltipId = useId();
  const triggerRef = useRef<HTMLSpanElement>(null);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      setOpen(false);
    } else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      setOpen((prev) => !prev);
    }
  }, []);

  // Dismiss on outside click
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (triggerRef.current && !triggerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  // tooltip text joined for data attribute (test introspection)
  const tooltipText = tooltipLines.join("\n");

  return (
    <span className="relative inline-flex">
      {/* Badge trigger — carries all semantic + accessibility attributes */}
      <span
        ref={triggerRef}
        role="img"
        aria-label={ariaLabel}
        aria-describedby={open ? tooltipId : undefined}
        tabIndex={0}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onKeyDown={handleKeyDown}
        onClick={() => setOpen((prev) => !prev)}
        className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold cursor-default
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-current
          ${bg}`}
        data-testid="viability-badge"
        data-viability-level={level}
        data-tooltip-content={tooltipText}
      >
        {children}
      </span>

      {/* Tooltip panel — WCAG role="tooltip", linked via aria-describedby */}
      {open && (
        <span
          id={tooltipId}
          role="tooltip"
          className={[
            "absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2",
            "w-max max-w-[240px]",
            "bg-gray-900 dark:bg-gray-800 text-white text-[10px] leading-relaxed",
            "rounded-md px-2.5 py-2 shadow-lg",
            "pointer-events-none",
          ].join(" ")}
        >
          {tooltipLines.map((line, i) => (
            <p key={i} className={i === 0 ? "font-semibold mb-1" : "text-gray-300"}>
              {line}
            </p>
          ))}
          {/* Arrow */}
          <span
            aria-hidden="true"
            className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900 dark:border-t-gray-800"
          />
        </span>
      )}
    </span>
  );
}
