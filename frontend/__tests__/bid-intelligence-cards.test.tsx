/**
 * STORY-259 AC23 — Bid Intelligence Cards tests
 * Tests CompatibilityBadge, ActionLabel, and DeepAnalysisModal components.
 */
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";

// ─── Mocks ────────────────────────────────────────────────────────────────────

// jest.config has resetMocks:true which resets mock.calls and implementations,
// but does NOT remove properties from global. We assign a fresh jest.fn() each
// time in beforeEach so we get a clean mock per test.

beforeEach(() => {
  global.fetch = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => ({}),
  } as unknown as Response);
});

afterEach(() => {
  jest.clearAllMocks();
});

// ─── Import components ────────────────────────────────────────────────────────
import CompatibilityBadge from "../components/CompatibilityBadge";
import ActionLabel from "../components/ActionLabel";
import DeepAnalysisModal from "../components/DeepAnalysisModal";

// ─── CompatibilityBadge ───────────────────────────────────────────────────────
describe("CompatibilityBadge (STORY-259 AC23)", () => {
  it("renders green (emerald) styling for compatibility >= 70%", () => {
    render(<CompatibilityBadge compatibilidade_pct={70} />);

    const badge = screen.getByTestId("compatibility-badge");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-emerald-100");
    expect(badge).toHaveClass("text-emerald-700");
  });

  it("renders green styling for a high value like 95%", () => {
    render(<CompatibilityBadge compatibilidade_pct={95} />);

    const badge = screen.getByTestId("compatibility-badge");
    expect(badge).toHaveClass("bg-emerald-100");
    expect(badge.textContent).toContain("95%");
  });

  it("renders yellow (amber) styling for compatibility 40–69%", () => {
    render(<CompatibilityBadge compatibilidade_pct={55} />);

    const badge = screen.getByTestId("compatibility-badge");
    expect(badge).toHaveClass("bg-amber-100");
    expect(badge).toHaveClass("text-amber-700");
  });

  it("renders yellow styling at the boundary of 40%", () => {
    render(<CompatibilityBadge compatibilidade_pct={40} />);

    const badge = screen.getByTestId("compatibility-badge");
    expect(badge).toHaveClass("bg-amber-100");
  });

  it("renders gray (slate) styling for compatibility < 40%", () => {
    render(<CompatibilityBadge compatibilidade_pct={20} />);

    const badge = screen.getByTestId("compatibility-badge");
    expect(badge).toHaveClass("bg-slate-100");
    expect(badge).toHaveClass("text-slate-600");
  });

  it("renders gray styling at 0% compatibility", () => {
    render(<CompatibilityBadge compatibilidade_pct={0} />);

    const badge = screen.getByTestId("compatibility-badge");
    expect(badge).toHaveClass("bg-slate-100");
    expect(badge.textContent).toContain("0%");
  });

  it("renders nothing (null) when compatibilidade_pct is undefined", () => {
    const { container } = render(<CompatibilityBadge />);
    expect(container.firstChild).toBeNull();
  });

  it("renders nothing (null) when compatibilidade_pct is null", () => {
    const { container } = render(<CompatibilityBadge compatibilidade_pct={null} />);
    expect(container.firstChild).toBeNull();
  });

  it("displays the rounded percentage value in the badge text", () => {
    render(<CompatibilityBadge compatibilidade_pct={72.7} />);

    const badge = screen.getByTestId("compatibility-badge");
    // Should round to 73
    expect(badge.textContent).toContain("73%");
  });

  it("has a title attribute describing compatibility level", () => {
    render(<CompatibilityBadge compatibilidade_pct={80} />);

    const badge = screen.getByTestId("compatibility-badge");
    expect(badge).toHaveAttribute("title", expect.stringContaining("80%"));
  });
});

// ─── ActionLabel ──────────────────────────────────────────────────────────────
describe("ActionLabel (STORY-259 AC23)", () => {
  it("renders PARTICIPAR label with green (emerald) styling", () => {
    render(<ActionLabel acao_recomendada="PARTICIPAR" />);

    const label = screen.getByTestId("action-label");
    expect(label).toBeInTheDocument();
    expect(label.textContent).toContain("PARTICIPAR");
    expect(label).toHaveClass("bg-emerald-100");
    expect(label).toHaveClass("text-emerald-700");
  });

  it("renders AVALIAR COM CAUTELA label with yellow (amber) styling", () => {
    render(<ActionLabel acao_recomendada="AVALIAR COM CAUTELA" />);

    const label = screen.getByTestId("action-label");
    expect(label.textContent).toContain("AVALIAR COM CAUTELA");
    expect(label).toHaveClass("bg-amber-100");
    expect(label).toHaveClass("text-amber-700");
  });

  it("renders NÃO PARTICIPAR label with gray (slate) styling", () => {
    render(<ActionLabel acao_recomendada="NÃO PARTICIPAR" />);

    const label = screen.getByTestId("action-label");
    expect(label.textContent).toContain("NÃO PARTICIPAR");
    expect(label).toHaveClass("bg-slate-100");
    expect(label).toHaveClass("text-slate-600");
  });

  it("is case-insensitive and normalizes to uppercase", () => {
    render(<ActionLabel acao_recomendada="participar" />);

    const label = screen.getByTestId("action-label");
    expect(label.textContent).toContain("PARTICIPAR");
  });

  it("renders nothing when acao_recomendada is undefined", () => {
    const { container } = render(<ActionLabel />);
    expect(container.firstChild).toBeNull();
  });

  it("renders nothing when acao_recomendada is null", () => {
    const { container } = render(<ActionLabel acao_recomendada={null} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders nothing for an unrecognized action value", () => {
    const { container } = render(<ActionLabel acao_recomendada="DESCONHECIDO" />);
    expect(container.firstChild).toBeNull();
  });

  it("has an aria-label attribute describing the action", () => {
    render(<ActionLabel acao_recomendada="PARTICIPAR" />);

    const label = screen.getByTestId("action-label");
    expect(label).toHaveAttribute("aria-label", expect.stringContaining("PARTICIPAR"));
  });
});

// ─── DeepAnalysisModal ────────────────────────────────────────────────────────
describe("DeepAnalysisModal (STORY-259 AC23)", () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
    bidId: "bid-123",
    searchId: "search-456",
  };

  it("does not render when isOpen is false", () => {
    const { container } = render(
      <DeepAnalysisModal {...defaultProps} isOpen={false} />
    );

    expect(container.firstChild).toBeNull();
  });

  it("renders the modal overlay when isOpen is true", async () => {
    render(<DeepAnalysisModal {...defaultProps} />);

    expect(screen.getByTestId("deep-analysis-modal")).toBeInTheDocument();
  });

  it("shows loading skeleton while fetching analysis", async () => {
    (global.fetch as jest.Mock).mockReturnValueOnce(new Promise(() => {}));

    render(<DeepAnalysisModal {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByTestId("loading-skeleton")).toBeInTheDocument();
    });
  });

  it("calls onClose when the close button is clicked", async () => {
    const onClose = jest.fn();
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ score: 5, decisao: "Avaliar" }),
    });

    render(<DeepAnalysisModal {...defaultProps} onClose={onClose} />);

    const closeBtn = await screen.findByTestId("modal-close");
    fireEvent.click(closeBtn);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("calls onClose when Escape key is pressed", async () => {
    const onClose = jest.fn();

    render(<DeepAnalysisModal {...defaultProps} onClose={onClose} />);

    fireEvent.keyDown(document, { key: "Escape" });

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("displays analysis content after successful fetch", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        score: 8,
        decisao: "Recomendar participacao",
        acao_recomendada: "PARTICIPAR",
        compatibilidade_pct: 82,
      }),
    });

    render(<DeepAnalysisModal {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByTestId("analysis-content")).toBeInTheDocument();
    });

    expect(screen.getByText("Recomendar participacao")).toBeInTheDocument();
    expect(screen.getByTestId("score-badge")).toBeInTheDocument();
  });

  it("calls the analysis endpoint with correct bidId when opened", async () => {
    // This test verifies the error-path fetch call is made correctly.
    // The component calls fetch when mounted with isOpen=true.
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      text: async () => JSON.stringify({ detail: "Servico indisponivel" }),
    });

    render(<DeepAnalysisModal {...defaultProps} />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("bid-123"),
        expect.objectContaining({ method: "POST" })
      );
    });
  });

  it("calls fetch with search_id in request body", async () => {
    render(<DeepAnalysisModal {...defaultProps} searchId="search-xyz" />);

    await waitFor(() => {
      const calls = (global.fetch as jest.Mock).mock.calls;
      const firstCall = calls[0];
      const bodyStr = firstCall[1]?.body as string;
      const body = JSON.parse(bodyStr);
      expect(body.search_id).toBe("search-xyz");
    });
  });

  it("calls onAddToPipeline with bidId when add-to-pipeline button is clicked", async () => {
    const onAddToPipeline = jest.fn();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ score: 7, decisao: "Participar" }),
    });

    render(
      <DeepAnalysisModal
        {...defaultProps}
        onAddToPipeline={onAddToPipeline}
      />
    );

    // Wait for analysis content so loading=false and button is enabled
    await screen.findByTestId("analysis-content");

    const addBtn = screen.getByTestId("add-to-pipeline-btn");
    fireEvent.click(addBtn);

    expect(onAddToPipeline).toHaveBeenCalledWith("bid-123");
  });

  it("shows bid object text when bidData is provided", async () => {
    (global.fetch as jest.Mock).mockReturnValueOnce(new Promise(() => {}));

    render(
      <DeepAnalysisModal
        {...defaultProps}
        bidData={{ objeto: "Aquisicao de uniformes escolares", orgao: "SEMEC", uf: "PA" }}
      />
    );

    expect(screen.getByText(/aquisicao de uniformes escolares/i)).toBeInTheDocument();
  });

  it("fallback: shows existing CompatibilityBadge styling when analysis unavailable", () => {
    // CompatibilityBadge is a standalone component — test it renders without modal
    render(<CompatibilityBadge compatibilidade_pct={65} />);

    const badge = screen.getByTestId("compatibility-badge");
    // In the absence of deep analysis, badge still shows the existing percentage
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("bg-amber-100"); // 40-69% = yellow
  });
});
