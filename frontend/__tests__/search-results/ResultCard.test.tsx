/**
 * TD-007 AC1: ResultCard sub-component tests.
 * Tests rendering of executive summary, opportunity counts, urgency alerts,
 * recommendations, profile banner, AI transparency label, and paywall CTA.
 */

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import type { BuscaResult } from "../../app/types";

// --- Mocks ---

jest.mock("next/link", () => {
  return function MockLink({ children, href, ...props }: any) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    );
  };
});

jest.mock("../../app/buscar/components/LlmSourceBadge", () => ({
  LlmSourceBadge: function Mock({ llmSource }: any) {
    return (
      <span data-testid="llm-source-badge" data-source={llmSource}>
        LLM
      </span>
    );
  },
}));

import { ResultCard } from "../../app/buscar/components/search-results/ResultCard";

// --- Mock factory ---

/** Base resumo with all required fields filled in */
const BASE_RESUMO = {
  resumo_executivo:
    "Análise de mercado para setor de TI. Segunda sentença do resumo. Terceira sentença.",
  total_oportunidades: 5,
  valor_total: 150000,
  recomendacoes: [] as any[],
  destaques: [] as string[],
  insight_setorial: null as string | null,
  alerta_urgencia: null as string | null,
  alertas_urgencia: [] as string[],
};

/** Merge a partial resumo override with BASE_RESUMO, preserving required numeric fields */
function mergeResumo(resumoOverride?: any): any {
  if (!resumoOverride) return { ...BASE_RESUMO };
  return {
    ...BASE_RESUMO,
    ...resumoOverride,
    // Guarantee numeric fields never become undefined
    total_oportunidades:
      resumoOverride.total_oportunidades !== undefined
        ? resumoOverride.total_oportunidades
        : BASE_RESUMO.total_oportunidades,
    valor_total:
      resumoOverride.valor_total !== undefined
        ? resumoOverride.valor_total
        : BASE_RESUMO.valor_total,
  };
}

function createMockResult(overrides: Partial<BuscaResult> = {}): BuscaResult {
  return {
    resumo: mergeResumo(overrides?.resumo) as any,
    licitacoes: overrides?.licitacoes ?? [
      {
        id: "1",
        orgao: "Org1",
        objeto: "Compra de equipamentos de TI para uso no departamento",
        valor_estimado: 50000,
        uf: "SP",
        link: "https://example.com/edital/1",
        confidence: "high",
      } as any,
    ],
    download_id: null,
    download_url: null,
    total_raw: 10,
    total_filtrado: 5,
    filter_stats: null,
    termos_utilizados: null,
    stopwords_removidas: null,
    excel_available: true,
    upgrade_message: null,
    source_stats: null,
    ultima_atualizacao: "2026-03-01T12:00:00Z",
    llm_source: "keyword",
    // Spread overrides but omit resumo and licitacoes (handled above)
    ...(({ resumo: _r, licitacoes: _l, ...rest }) => rest)(overrides as any),
  } as BuscaResult;
}

const defaultProps = {
  bannerDismissed: false,
  onDismissBanner: jest.fn(),
};

describe("ResultCard", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // --- Rendering basics ---

  it("renders executive summary text", () => {
    const result = createMockResult();
    render(<ResultCard result={result} {...defaultProps} />);
    expect(
      screen.getByText(/Análise de mercado para setor de TI/)
    ).toBeInTheDocument();
  });

  it("renders total opportunities count", () => {
    const result = createMockResult();
    render(<ResultCard result={result} {...defaultProps} />);
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("licitações")).toBeInTheDocument();
  });

  it("renders singular 'licitação' when total_oportunidades is 1", () => {
    const result = createMockResult({
      resumo: { total_oportunidades: 1, valor_total: 50000 } as any,
    });
    render(<ResultCard result={result} {...defaultProps} />);
    expect(screen.getByText("licitação")).toBeInTheDocument();
  });

  it("renders valor total formatted", () => {
    const result = createMockResult();
    render(<ResultCard result={result} {...defaultProps} />);
    expect(screen.getByText(/valor total/)).toBeInTheDocument();
    expect(screen.getByText(/R\$/)).toBeInTheDocument();
  });

  // --- Urgency alerts ---

  it("shows single urgency alert when alerta_urgencia is set and no alertas_urgencia", () => {
    const result = createMockResult({
      resumo: {
        alerta_urgencia: "5 licitações encerram em 24 horas",
        alertas_urgencia: [],
      } as any,
    });
    render(<ResultCard result={result} {...defaultProps} />);
    expect(
      screen.getByText(/5 licitações encerram em 24 horas/)
    ).toBeInTheDocument();
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("shows multiple urgency alerts when alertas_urgencia has items", () => {
    const result = createMockResult({
      resumo: {
        alertas_urgencia: ["Alerta 1: urgente", "Alerta 2: atenção"],
        alerta_urgencia: null,
      } as any,
    });
    render(<ResultCard result={result} {...defaultProps} />);
    expect(screen.getByText("Alerta 1: urgente")).toBeInTheDocument();
    expect(screen.getByText("Alerta 2: atenção")).toBeInTheDocument();
  });

  it("prefers alertas_urgencia over alerta_urgencia when both are present", () => {
    const result = createMockResult({
      resumo: {
        alertas_urgencia: ["Primeiro alerta múltiplo"],
        alerta_urgencia: "Alerta legado único",
      } as any,
    });
    render(<ResultCard result={result} {...defaultProps} />);
    expect(
      screen.getByText("Primeiro alerta múltiplo")
    ).toBeInTheDocument();
    expect(
      screen.queryByText(/Alerta legado único/)
    ).not.toBeInTheDocument();
  });

  // --- Insight setorial ---

  it("shows insight setorial banner when present", () => {
    const result = createMockResult({
      resumo: {
        insight_setorial: "O setor de TI cresceu 15% em 2025",
      } as any,
    });
    render(<ResultCard result={result} {...defaultProps} />);
    expect(screen.getByText(/Contexto do setor:/)).toBeInTheDocument();
    expect(
      screen.getByText(/O setor de TI cresceu 15% em 2025/)
    ).toBeInTheDocument();
  });

  it("does not show insight setorial section when null", () => {
    const result = createMockResult({
      resumo: { insight_setorial: null } as any,
    });
    render(<ResultCard result={result} {...defaultProps} />);
    expect(screen.queryByText(/Contexto do setor:/)).not.toBeInTheDocument();
  });

  // --- Destaques ---

  it("shows destaques list when present", () => {
    const result = createMockResult({
      resumo: {
        destaques: ["Destaque 1: alta demanda", "Destaque 2: bom valor"],
        recomendacoes: [],
      } as any,
    });
    render(<ResultCard result={result} {...defaultProps} />);
    expect(screen.getByText("Destaques:")).toBeInTheDocument();
    expect(screen.getByText("Destaque 1: alta demanda")).toBeInTheDocument();
    expect(screen.getByText("Destaque 2: bom valor")).toBeInTheDocument();
  });

  it("does not show destaques section when empty", () => {
    const result = createMockResult({
      resumo: { destaques: [] } as any,
    });
    render(<ResultCard result={result} {...defaultProps} />);
    expect(screen.queryByText("Destaques:")).not.toBeInTheDocument();
  });

  // --- Trial phase / paywall ---

  it("truncates summary in limited_access trial phase", () => {
    const result = createMockResult();
    render(
      <ResultCard
        result={result}
        trialPhase="limited_access"
        {...defaultProps}
      />
    );
    // Should show truncated text (first 2 sentences + ...)
    const paragraph = screen.getByText(/Análise de mercado para setor de TI/);
    expect(paragraph.textContent).toMatch(/\.\.\.$/);
    // Full third sentence should not appear
    expect(paragraph.textContent).not.toMatch(/Terceira sentença/);
  });

  it("does not truncate summary in full_access phase", () => {
    const result = createMockResult();
    render(
      <ResultCard
        result={result}
        trialPhase="full_access"
        {...defaultProps}
      />
    );
    const paragraph = screen.getByText(/Análise de mercado para setor de TI/);
    expect(paragraph.textContent).toContain("Terceira sentença.");
    expect(paragraph.textContent).not.toMatch(/\.\.\.$/);
  });

  it("shows paywall CTA in limited_access phase", () => {
    const result = createMockResult();
    render(
      <ResultCard
        result={result}
        trialPhase="limited_access"
        {...defaultProps}
      />
    );
    expect(screen.getByTestId("summary-paywall-cta")).toBeInTheDocument();
    expect(screen.getByText("Assinar")).toBeInTheDocument();
    expect(screen.getByText(/Ver análise completa com SmartLic Pro/)).toBeInTheDocument();
  });

  it("does not show paywall CTA in full_access phase", () => {
    const result = createMockResult();
    render(
      <ResultCard
        result={result}
        trialPhase="full_access"
        {...defaultProps}
      />
    );
    expect(screen.queryByTestId("summary-paywall-cta")).not.toBeInTheDocument();
  });

  // --- Profile incomplete banner ---

  it("shows profile incomplete banner when isProfileComplete=false and recomendacoes exist", () => {
    const result = createMockResult({
      resumo: {
        recomendacoes: [
          {
            oportunidade: "Compra TI",
            valor: 50000,
            urgencia: "media",
            acao_sugerida: "Participar",
            justificativa: "Boa oportunidade",
          },
        ],
      } as any,
    });
    render(
      <ResultCard
        result={result}
        isProfileComplete={false}
        bannerDismissed={false}
        onDismissBanner={jest.fn()}
      />
    );
    expect(
      screen.getByTestId("profile-incomplete-banner")
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Complete seu perfil para recomendações mais precisas/)
    ).toBeInTheDocument();
  });

  it("calls onDismissBanner when dismiss button clicked", () => {
    const onDismiss = jest.fn();
    const result = createMockResult({
      resumo: {
        recomendacoes: [
          {
            oportunidade: "Compra TI",
            valor: 50000,
            urgencia: "baixa",
            acao_sugerida: "Participar",
            justificativa: "Boa oportunidade",
          },
        ],
      } as any,
    });
    render(
      <ResultCard
        result={result}
        isProfileComplete={false}
        bannerDismissed={false}
        onDismissBanner={onDismiss}
      />
    );
    fireEvent.click(screen.getByTestId("profile-banner-dismiss"));
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("does not show profile banner when bannerDismissed=true", () => {
    const result = createMockResult({
      resumo: {
        recomendacoes: [
          {
            oportunidade: "Compra TI",
            valor: 50000,
            urgencia: "baixa",
            acao_sugerida: "Participar",
            justificativa: "Boa oportunidade",
          },
        ],
      } as any,
    });
    render(
      <ResultCard
        result={result}
        isProfileComplete={false}
        bannerDismissed={true}
        onDismissBanner={jest.fn()}
      />
    );
    expect(
      screen.queryByTestId("profile-incomplete-banner")
    ).not.toBeInTheDocument();
  });

  it("does not show profile banner when isProfileComplete=true", () => {
    const result = createMockResult({
      resumo: {
        recomendacoes: [
          {
            oportunidade: "Compra TI",
            valor: 50000,
            urgencia: "alta",
            acao_sugerida: "Participar",
            justificativa: "Boa oportunidade",
          },
        ],
      } as any,
    });
    render(
      <ResultCard
        result={result}
        isProfileComplete={true}
        bannerDismissed={false}
        onDismissBanner={jest.fn()}
      />
    );
    expect(
      screen.queryByTestId("profile-incomplete-banner")
    ).not.toBeInTheDocument();
  });

  // --- AI transparency ---

  it("shows AI transparency label when recommendations are present", () => {
    const result = createMockResult({
      resumo: {
        recomendacoes: [
          {
            oportunidade: "Compra TI",
            valor: 50000,
            urgencia: "baixa",
            acao_sugerida: "Participar",
            justificativa: "Boa oportunidade",
          },
        ],
      } as any,
    });
    render(<ResultCard result={result} {...defaultProps} />);
    expect(screen.getByTestId("ai-transparency-label")).toBeInTheDocument();
    expect(
      screen.getByText(/Análise gerada por IA/)
    ).toBeInTheDocument();
  });

  // --- Edital link on recommendations ---

  it("shows edital link when matched bid has a link", () => {
    const result = createMockResult({
      resumo: {
        recomendacoes: [
          {
            oportunidade: "Org1 Compra de equipamentos de TI",
            valor: 50000,
            urgencia: "alta",
            acao_sugerida: "Participar do pregão",
            justificativa: "Alta compatibilidade com perfil",
          },
        ],
      } as any,
      licitacoes: [
        {
          id: "1",
          orgao: "Org1",
          objeto: "Compra de equipamentos de TI para uso no departamento",
          valor_estimado: 50000,
          uf: "SP",
          link: "https://example.com/edital/1",
          confidence: "high",
        } as any,
      ],
    });
    render(<ResultCard result={result} {...defaultProps} />);
    const editLink = screen.getByTestId("rec-edital-link");
    expect(editLink).toBeInTheDocument();
    expect(editLink).toHaveAttribute("href", "https://example.com/edital/1");
    expect(screen.getByText(/Ver edital na fonte oficial/)).toBeInTheDocument();
  });

  // --- Recommendation urgency badges ---

  it("shows urgency badge 'Urgente' for alta urgency", () => {
    const result = createMockResult({
      resumo: {
        recomendacoes: [
          {
            oportunidade: "Oportunidade urgente",
            valor: 100000,
            urgencia: "alta",
            acao_sugerida: "Agir agora",
            justificativa: "Encerra em 1 dia",
          },
        ],
      } as any,
    });
    render(<ResultCard result={result} {...defaultProps} />);
    expect(screen.getByText("Urgente")).toBeInTheDocument();
  });

  it("shows urgency badge 'Atenção' for media urgency", () => {
    const result = createMockResult({
      resumo: {
        recomendacoes: [
          {
            oportunidade: "Oportunidade média",
            valor: 80000,
            urgencia: "media",
            acao_sugerida: "Avaliar",
            justificativa: "Encerra em 5 dias",
          },
        ],
      } as any,
    });
    render(<ResultCard result={result} {...defaultProps} />);
    expect(screen.getByText("Atenção")).toBeInTheDocument();
  });
});
