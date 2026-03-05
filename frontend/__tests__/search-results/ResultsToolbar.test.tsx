/**
 * TD-007 AC3: ResultsToolbar sub-component tests.
 * Tests sort controls, Excel/Sheets/PDF export buttons, sticky bar,
 * skeleton loading, and trial-expired/paywall gating.
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

jest.mock("../../app/components/OrdenacaoSelect", () => ({
  OrdenacaoSelect: function Mock({ value, onChange, disabled }: any) {
    return (
      <select
        data-testid="ordenacao-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        <option value="data_desc">Mais recentes</option>
        <option value="valor_desc">Maior valor</option>
      </select>
    );
  },
}));

jest.mock("../../components/GoogleSheetsExportButton", () => {
  return function Mock({ disabled }: any) {
    return (
      <button data-testid="google-sheets-button" disabled={disabled}>
        Google Sheets
      </button>
    );
  };
});

import { ResultsToolbar } from "../../app/buscar/components/search-results/ResultsToolbar";

// --- Mock factory ---

function createMockResult(overrides: Partial<BuscaResult> = {}): BuscaResult {
  return {
    resumo: {
      resumo_executivo: "Resumo",
      total_oportunidades: 10,
      valor_total: 500000,
      recomendacoes: [],
      destaques: [],
      insight_setorial: null,
      alerta_urgencia: null,
      alertas_urgencia: [],
    } as any,
    licitacoes: [],
    download_id: "download-123",
    download_url: null,
    total_raw: 50,
    total_filtrado: 10,
    filter_stats: null,
    termos_utilizados: null,
    stopwords_removidas: null,
    excel_available: true,
    upgrade_message: null,
    source_stats: null,
    excel_status: null,
    ultima_atualizacao: "2026-03-01T12:00:00Z",
    llm_source: "keyword",
    ...overrides,
  } as BuscaResult;
}

const baseToolbarProps = {
  ordenacao: "data_desc" as any,
  onOrdenacaoChange: jest.fn(),
  loading: false,
  onDownload: jest.fn(),
  downloadLoading: false,
  onRegenerateExcel: jest.fn(),
  excelFailCount: 0,
  excelTimedOut: false,
  planInfo: { capabilities: { allow_excel: true } },
  session: { access_token: "token-123" },
  isTrialExpired: false,
  paywallApplied: false,
  totalBeforePaywall: null,
  sectorName: "Informática",
  ufsSelecionadas: new Set(["SP", "RJ"]),
  onGeneratePdf: jest.fn(),
  pdfLoading: false,
  onSearch: jest.fn(),
};

describe("ResultsToolbar", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // --- Sticky bar and count ---

  it("renders sticky action bar with data-testid", () => {
    const result = createMockResult();
    render(<ResultsToolbar result={result} {...baseToolbarProps} />);
    expect(screen.getByTestId("sticky-action-bar")).toBeInTheDocument();
  });

  it("shows opportunity count in sticky bar", () => {
    const result = createMockResult();
    render(<ResultsToolbar result={result} {...baseToolbarProps} />);
    const countEl = screen.getByTestId("sticky-count");
    expect(countEl).toHaveTextContent("10 oportunidades");
  });

  it("shows singular 'oportunidade' when count is 1", () => {
    const result = createMockResult({
      resumo: { total_oportunidades: 1, valor_total: 50000 } as any,
    });
    render(<ResultsToolbar result={result} {...baseToolbarProps} />);
    expect(screen.getByTestId("sticky-count")).toHaveTextContent(
      "1 oportunidade"
    );
  });

  // --- OrdenacaoSelect ---

  it("renders OrdenacaoSelect with correct value", () => {
    const result = createMockResult();
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        ordenacao={"valor_desc" as any}
      />
    );
    const select = screen.getByTestId("ordenacao-select");
    expect(select).toHaveValue("valor_desc");
  });

  it("calls onOrdenacaoChange when sort changes", () => {
    const onOrdenacaoChange = jest.fn();
    const result = createMockResult();
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        onOrdenacaoChange={onOrdenacaoChange}
      />
    );
    fireEvent.change(screen.getByTestId("ordenacao-select"), {
      target: { value: "valor_desc" },
    });
    expect(onOrdenacaoChange).toHaveBeenCalledWith("valor_desc");
  });

  // --- Excel button states ---

  it("shows Excel download button when plan allows and has download", () => {
    const result = createMockResult({ download_id: "dl-123" });
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        isTrialExpired={false}
        paywallApplied={false}
        totalBeforePaywall={null}
      />
    );
    expect(screen.getByTestId("excel-download-button")).toBeInTheDocument();
  });

  it("shows Excel processing spinner when excel_status is processing", () => {
    const result = createMockResult({
      excel_status: "processing",
      download_id: null,
      download_url: null,
    });
    render(<ResultsToolbar result={result} {...baseToolbarProps} />);
    expect(screen.getByTestId("excel-processing-button")).toBeInTheDocument();
    expect(
      screen.queryByTestId("excel-download-button")
    ).not.toBeInTheDocument();
  });

  it("shows Excel retry button when excel failed and failCount < 2", () => {
    const result = createMockResult({
      excel_status: "failed",
      download_id: null,
      download_url: null,
    });
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        excelFailCount={1}
        excelTimedOut={false}
      />
    );
    expect(screen.getByTestId("excel-retry-button")).toBeInTheDocument();
  });

  it("shows unavailable message after max retries (excelFailCount >= 2)", () => {
    const result = createMockResult({
      excel_status: "failed",
      download_id: null,
      download_url: null,
    });
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        excelFailCount={2}
        excelTimedOut={false}
      />
    );
    expect(screen.getByTestId("excel-unavailable-message")).toBeInTheDocument();
    expect(screen.getByText(/Excel temporariamente indisponível/)).toBeInTheDocument();
  });

  it("shows retry button when excel timed out (excelTimedOut=true)", () => {
    const result = createMockResult({
      excel_status: null,
      download_id: null,
      download_url: null,
    });
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        excelFailCount={0}
        excelTimedOut={true}
      />
    );
    expect(screen.getByTestId("excel-retry-button")).toBeInTheDocument();
  });

  // --- Trial expired gating ---

  it("does not show Excel button when trial expired", () => {
    const result = createMockResult({ download_id: "dl-123" });
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        isTrialExpired={true}
      />
    );
    expect(
      screen.queryByTestId("excel-download-button")
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId("excel-processing-button")
    ).not.toBeInTheDocument();
    expect(
      screen.queryByTestId("excel-retry-button")
    ).not.toBeInTheDocument();
  });

  it("does not show Google Sheets button when trial expired", () => {
    const result = createMockResult();
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        isTrialExpired={true}
      />
    );
    expect(
      screen.queryByTestId("google-sheets-button")
    ).not.toBeInTheDocument();
  });

  // --- Paywall gating ---

  it("does not show Excel when paywallApplied and totalBeforePaywall is set", () => {
    const result = createMockResult({ download_id: "dl-123" });
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        paywallApplied={true}
        totalBeforePaywall={10}
      />
    );
    expect(
      screen.queryByTestId("excel-download-button")
    ).not.toBeInTheDocument();
  });

  it("still shows Google Sheets when paywallApplied (only Excel is blocked)", () => {
    const result = createMockResult({ download_id: "dl-123" });
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        paywallApplied={true}
        totalBeforePaywall={10}
        isTrialExpired={false}
      />
    );
    expect(screen.getByTestId("google-sheets-button")).toBeInTheDocument();
  });

  // --- Google Sheets button ---

  it("shows Google Sheets button when plan allows and not trial expired", () => {
    const result = createMockResult();
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        isTrialExpired={false}
      />
    );
    expect(screen.getByTestId("google-sheets-button")).toBeInTheDocument();
  });

  it("does not show Google Sheets when plan does not allow excel", () => {
    const result = createMockResult();
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        planInfo={{ capabilities: { allow_excel: false } }}
      />
    );
    expect(
      screen.queryByTestId("google-sheets-button")
    ).not.toBeInTheDocument();
  });

  // --- PDF button ---

  it("shows PDF button when session exists and not trial expired", () => {
    const result = createMockResult();
    render(
      <ResultsToolbar
        result={result}
        {...baseToolbarProps}
        session={{ access_token: "token-123" }}
        isTrialExpired={false}
      />
    );
    expect(screen.getByTestId("pdf-report-button")).toBeInTheDocument();
  });

  it("does not show PDF button when session is null", () => {
    const result = createMockResult();
    render(
      <ResultsToolbar result={result} {...baseToolbarProps} session={null} />
    );
    expect(screen.queryByTestId("pdf-report-button")).not.toBeInTheDocument();
  });

  // --- Skeleton loading state ---

  it("shows skeleton loading state when loading=true", () => {
    const result = createMockResult();
    const { container } = render(
      <ResultsToolbar result={result} {...baseToolbarProps} loading={true} />
    );
    const skeleton = container.querySelector(".animate-pulse");
    expect(skeleton).toBeInTheDocument();
  });

  it("does not show skeleton when loading=false", () => {
    const result = createMockResult();
    const { container } = render(
      <ResultsToolbar result={result} {...baseToolbarProps} loading={false} />
    );
    const skeleton = container.querySelector(".animate-pulse");
    expect(skeleton).not.toBeInTheDocument();
  });
});
