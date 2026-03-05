/**
 * TD-007 AC4: ResultsHeader sub-component tests.
 * Tests opportunity count display, singular/plural forms,
 * "de X analisadas" suffix, personalized analysis badge,
 * and filter context line with confidence distribution.
 */

import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import type { BuscaResult } from "../../app/types";
import type { FilterSummary } from "../../hooks/useSearchSSE";

import { ResultsHeader } from "../../app/buscar/components/search-results/ResultsHeader";

// --- Mock factory ---

function createMockResult(overrides: Partial<BuscaResult> = {}): BuscaResult {
  return {
    resumo: {
      resumo_executivo: "Resumo de teste",
      total_oportunidades: 5,
      valor_total: 250000,
      recomendacoes: [],
      destaques: [],
      insight_setorial: null,
      alerta_urgencia: null,
      alertas_urgencia: [],
      ...overrides?.resumo,
    } as any,
    licitacoes: overrides?.licitacoes ?? [
      { id: "1", objeto: "Objeto 1", uf: "SP", confidence: "high" } as any,
      { id: "2", objeto: "Objeto 2", uf: "RJ", confidence: "medium" } as any,
      { id: "3", objeto: "Objeto 3", uf: "MG", confidence: "low" } as any,
    ],
    download_id: null,
    download_url: null,
    total_raw: 100,
    total_filtrado: 5,
    filter_stats: null,
    termos_utilizados: null,
    stopwords_removidas: null,
    excel_available: true,
    upgrade_message: null,
    source_stats: null,
    ultima_atualizacao: "2026-03-01T12:00:00Z",
    llm_source: "keyword",
    ...overrides,
  } as BuscaResult;
}

function createFilterSummary(overrides: Partial<FilterSummary> = {}): FilterSummary {
  return {
    totalRaw: 100,
    totalFiltered: 5,
    rejectedKeyword: 70,
    rejectedValue: 20,
    rejectedLlm: 5,
    ...overrides,
  };
}

describe("ResultsHeader", () => {
  // --- Opportunity count ---

  it("renders opportunity count from result.resumo.total_oportunidades", () => {
    const result = createMockResult();
    render(<ResultsHeader result={result} rawCount={0} />);
    const header = screen.getByTestId("results-header");
    expect(header).toHaveTextContent("5");
  });

  it("shows 'oportunidades selecionadas' for multiple results", () => {
    const result = createMockResult();
    render(<ResultsHeader result={result} rawCount={0} />);
    const header = screen.getByTestId("results-header");
    expect(header).toHaveTextContent("5 oportunidades selecionadas");
  });

  it("shows 'oportunidade selecionada' for single result", () => {
    const result = createMockResult({
      resumo: { total_oportunidades: 1, valor_total: 50000 } as any,
    });
    render(<ResultsHeader result={result} rawCount={0} />);
    const header = screen.getByTestId("results-header");
    expect(header).toHaveTextContent("1 oportunidade selecionada");
  });

  // --- "de X analisadas" suffix ---

  it("shows 'de X analisadas' when rawCount > 0", () => {
    const result = createMockResult();
    render(<ResultsHeader result={result} rawCount={200} />);
    const header = screen.getByTestId("results-header");
    expect(header).toHaveTextContent("de 200 analisadas");
  });

  it("does not show 'de X analisadas' when rawCount is 0", () => {
    const result = createMockResult();
    render(<ResultsHeader result={result} rawCount={0} />);
    const header = screen.getByTestId("results-header");
    expect(header.textContent).not.toContain("analisadas");
  });

  it("formats large rawCount with pt-BR locale", () => {
    const result = createMockResult();
    render(<ResultsHeader result={result} rawCount={1930} />);
    const header = screen.getByTestId("results-header");
    // pt-BR locale uses period as thousands separator
    expect(header).toHaveTextContent("1.930 analisadas");
  });

  // --- Personalized analysis badge ---

  it("shows personalized analysis badge when profile complete and has results", () => {
    const result = createMockResult();
    render(
      <ResultsHeader result={result} rawCount={0} isProfileComplete={true} />
    );
    expect(
      screen.getByTestId("personalized-analysis-badge")
    ).toBeInTheDocument();
    expect(screen.getByText("Análise personalizada")).toBeInTheDocument();
  });

  it("does not show badge when profile incomplete", () => {
    const result = createMockResult();
    render(
      <ResultsHeader result={result} rawCount={0} isProfileComplete={false} />
    );
    expect(
      screen.queryByTestId("personalized-analysis-badge")
    ).not.toBeInTheDocument();
  });

  it("does not show badge when total_oportunidades is 0", () => {
    const result = createMockResult({
      resumo: { total_oportunidades: 0, valor_total: 0 } as any,
    });
    render(
      <ResultsHeader result={result} rawCount={0} isProfileComplete={true} />
    );
    expect(
      screen.queryByTestId("personalized-analysis-badge")
    ).not.toBeInTheDocument();
  });

  it("defaults to showing badge (isProfileComplete defaults to true)", () => {
    const result = createMockResult();
    render(<ResultsHeader result={result} rawCount={0} />);
    expect(
      screen.getByTestId("personalized-analysis-badge")
    ).toBeInTheDocument();
  });

  // --- Filter context line ---

  it("shows filter context line when filterSummary is present and totalRaw > 0", () => {
    const result = createMockResult();
    const filterSummary = createFilterSummary({ totalRaw: 100, totalFiltered: 5 });
    render(
      <ResultsHeader
        result={result}
        rawCount={100}
        filterSummary={filterSummary}
      />
    );
    expect(screen.getByTestId("filter-context-line")).toBeInTheDocument();
    expect(screen.getByText(/Analisamos 100 oportunidades/)).toBeInTheDocument();
    expect(screen.getByText(/selecionamos 5 compatíveis/)).toBeInTheDocument();
  });

  it("shows 'compatível' singular when 1 result in filter context", () => {
    const result = createMockResult({
      resumo: { total_oportunidades: 1, valor_total: 50000 } as any,
      licitacoes: [
        { id: "1", objeto: "Obj 1", uf: "SP", confidence: "high" } as any,
      ],
    });
    const filterSummary = createFilterSummary({ totalRaw: 50, totalFiltered: 1 });
    render(
      <ResultsHeader
        result={result}
        rawCount={50}
        filterSummary={filterSummary}
      />
    );
    const contextLine = screen.getByTestId("filter-context-line");
    expect(contextLine).toHaveTextContent("selecionamos 1 compatível");
  });

  it("does not show filter context line when filterSummary is null", () => {
    const result = createMockResult();
    render(
      <ResultsHeader result={result} rawCount={100} filterSummary={null} />
    );
    expect(
      screen.queryByTestId("filter-context-line")
    ).not.toBeInTheDocument();
  });

  it("does not show filter context line when filterSummary.totalRaw is 0", () => {
    const result = createMockResult();
    const filterSummary = createFilterSummary({ totalRaw: 0 });
    render(
      <ResultsHeader
        result={result}
        rawCount={0}
        filterSummary={filterSummary}
      />
    );
    expect(
      screen.queryByTestId("filter-context-line")
    ).not.toBeInTheDocument();
  });

  // --- Confidence distribution ---

  it("shows confidence distribution when licitacoes have confidence values", () => {
    const result = createMockResult({
      licitacoes: [
        { id: "1", objeto: "Obj 1", uf: "SP", confidence: "high" } as any,
        { id: "2", objeto: "Obj 2", uf: "RJ", confidence: "high" } as any,
        { id: "3", objeto: "Obj 3", uf: "MG", confidence: "medium" } as any,
        { id: "4", objeto: "Obj 4", uf: "RS", confidence: "low" } as any,
      ],
      resumo: { total_oportunidades: 4, valor_total: 200000 } as any,
    });
    const filterSummary = createFilterSummary({ totalRaw: 50 });
    render(
      <ResultsHeader
        result={result}
        rawCount={50}
        filterSummary={filterSummary}
      />
    );
    // Should show distribution: "2 alta, 1 média, 1 baixa"
    const contextLine = screen.getByTestId("filter-context-line");
    expect(contextLine).toHaveTextContent("2 alta");
    expect(contextLine).toHaveTextContent("1 média");
    expect(contextLine).toHaveTextContent("1 baixa");
  });

  it("does not show confidence distribution when no licitacoes have confidence", () => {
    const result = createMockResult({
      licitacoes: [
        { id: "1", objeto: "Obj 1", uf: "SP" } as any,
      ],
      resumo: { total_oportunidades: 1, valor_total: 50000 } as any,
    });
    const filterSummary = createFilterSummary({ totalRaw: 50 });
    render(
      <ResultsHeader
        result={result}
        rawCount={50}
        filterSummary={filterSummary}
      />
    );
    // Confidence section should not appear (no parenthesized confidence text)
    const contextLine = screen.getByTestId("filter-context-line");
    expect(contextLine.textContent).not.toMatch(/\d+ alta/);
    expect(contextLine.textContent).not.toMatch(/\d+ média/);
    expect(contextLine.textContent).not.toMatch(/\d+ baixa/);
  });

  it("shows only high confidence count when only high-confidence items exist", () => {
    const result = createMockResult({
      licitacoes: [
        { id: "1", objeto: "Obj 1", uf: "SP", confidence: "high" } as any,
        { id: "2", objeto: "Obj 2", uf: "RJ", confidence: "high" } as any,
      ],
      resumo: { total_oportunidades: 2, valor_total: 100000 } as any,
    });
    const filterSummary = createFilterSummary({ totalRaw: 30 });
    render(
      <ResultsHeader
        result={result}
        rawCount={30}
        filterSummary={filterSummary}
      />
    );
    const contextLine = screen.getByTestId("filter-context-line");
    expect(contextLine).toHaveTextContent("2 alta");
    expect(contextLine.textContent).not.toMatch(/\d+ média/);
    expect(contextLine.textContent).not.toMatch(/\d+ baixa/);
  });
});
