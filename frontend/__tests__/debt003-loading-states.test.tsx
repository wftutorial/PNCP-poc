/**
 * DEBT-003: Loading States Tests (FE-002)
 *
 * - 5 snapshot tests for loading.tsx files
 * - Layout structure verification (CLS prevention)
 * - Shimmer animation presence
 */

import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

// ---------------------------------------------------------------------------
// T1 — buscar/loading.tsx
// ---------------------------------------------------------------------------

import BuscarLoading from "../app/buscar/loading";

describe("DEBT-003: buscar/loading.tsx", () => {
  it("renders with data-testid=buscar-loading", () => {
    render(<BuscarLoading />);
    expect(screen.getByTestId("buscar-loading")).toBeInTheDocument();
  });

  it("renders search form skeleton (filter inputs area)", () => {
    const { container } = render(<BuscarLoading />);
    // Should have UF grid skeleton (27 shimmer cells)
    const testEl = screen.getByTestId("buscar-loading");
    // grid-cols-9 with 27 items = UF grid
    const ufGrid = testEl.querySelector(".grid-cols-9");
    expect(ufGrid).not.toBeNull();
    expect(ufGrid!.children.length).toBe(27);
  });

  it("renders 3 result card skeletons", () => {
    render(<BuscarLoading />);
    const resultArea = screen.getByRole("status");
    expect(resultArea).toBeInTheDocument();
    // 3 cards with rounded-card class
    const cards = resultArea.querySelectorAll(".rounded-card");
    expect(cards.length).toBe(3);
  });

  it("has shimmer animation elements", () => {
    const { container } = render(<BuscarLoading />);
    const shimmers = container.querySelectorAll(".animate-shimmer");
    expect(shimmers.length).toBeGreaterThan(0);
  });

  it("matches snapshot", () => {
    const { container } = render(<BuscarLoading />);
    expect(container.firstChild).toMatchSnapshot();
  });
});

// ---------------------------------------------------------------------------
// T2 — dashboard/loading.tsx
// ---------------------------------------------------------------------------

import DashboardLoading from "../app/dashboard/loading";

describe("DEBT-003: dashboard/loading.tsx", () => {
  it("renders with data-testid=dashboard-loading", () => {
    render(<DashboardLoading />);
    expect(screen.getByTestId("dashboard-loading")).toBeInTheDocument();
  });

  it("renders 3 stats cards in a grid", () => {
    render(<DashboardLoading />);
    const el = screen.getByTestId("dashboard-loading");
    // First grid: stats cards (3 items)
    const statsGrid = el.querySelector(".grid.grid-cols-1.sm\\:grid-cols-2.lg\\:grid-cols-3");
    expect(statsGrid).not.toBeNull();
    const cards = statsGrid!.querySelectorAll(".rounded-card");
    expect(cards.length).toBe(3);
  });

  it("renders 2 chart skeletons", () => {
    render(<DashboardLoading />);
    const el = screen.getByTestId("dashboard-loading");
    const chartGrid = el.querySelector(".grid.grid-cols-1.lg\\:grid-cols-2.gap-6.mb-8");
    expect(chartGrid).not.toBeNull();
    const chartCards = chartGrid!.querySelectorAll(".rounded-card");
    expect(chartCards.length).toBe(2);
  });

  it("matches snapshot", () => {
    const { container } = render(<DashboardLoading />);
    expect(container.firstChild).toMatchSnapshot();
  });
});

// ---------------------------------------------------------------------------
// T3 — pipeline/loading.tsx
// ---------------------------------------------------------------------------

import PipelineLoading from "../app/pipeline/loading";

describe("DEBT-003: pipeline/loading.tsx", () => {
  it("renders with data-testid=pipeline-loading", () => {
    render(<PipelineLoading />);
    expect(screen.getByTestId("pipeline-loading")).toBeInTheDocument();
  });

  it("renders 5 kanban column skeletons", () => {
    render(<PipelineLoading />);
    const el = screen.getByTestId("pipeline-loading");
    const columns = el.querySelectorAll(".flex-shrink-0.w-64");
    expect(columns.length).toBe(5);
  });

  it("first column (Descoberta) has 3 card skeletons, others have 2", () => {
    render(<PipelineLoading />);
    const el = screen.getByTestId("pipeline-loading");
    const columns = el.querySelectorAll(".flex-shrink-0.w-64");
    // First column: 3 cards
    expect(columns[0].querySelectorAll(".rounded-lg").length).toBe(3);
    // Second column: 2 cards
    expect(columns[1].querySelectorAll(".rounded-lg").length).toBe(2);
  });

  it("matches snapshot", () => {
    const { container } = render(<PipelineLoading />);
    expect(container.firstChild).toMatchSnapshot();
  });
});

// ---------------------------------------------------------------------------
// T4 — (protected)/loading.tsx
// ---------------------------------------------------------------------------

import ProtectedLoading from "../app/(protected)/loading";

describe("DEBT-003: (protected)/loading.tsx", () => {
  it("renders with data-testid=protected-loading", () => {
    render(<ProtectedLoading />);
    expect(screen.getByTestId("protected-loading")).toBeInTheDocument();
  });

  it("renders header skeleton with logo and avatar placeholders", () => {
    render(<ProtectedLoading />);
    const el = screen.getByTestId("protected-loading");
    const header = el.querySelector("header");
    expect(header).not.toBeNull();
    // Logo + 3 right-side icons
    const shimmers = header!.querySelectorAll(".animate-shimmer");
    expect(shimmers.length).toBeGreaterThanOrEqual(2);
  });

  it("renders content area with 3 card skeletons", () => {
    render(<ProtectedLoading />);
    const contentArea = screen.getByRole("status");
    expect(contentArea).toBeInTheDocument();
    const cards = contentArea.querySelectorAll(".rounded-card");
    expect(cards.length).toBe(3);
  });

  it("fills full viewport height", () => {
    render(<ProtectedLoading />);
    const el = screen.getByTestId("protected-loading");
    expect(el).toHaveClass("min-h-screen");
  });

  it("matches snapshot", () => {
    const { container } = render(<ProtectedLoading />);
    expect(container.firstChild).toMatchSnapshot();
  });
});

// ---------------------------------------------------------------------------
// T5 — historico/loading.tsx
// ---------------------------------------------------------------------------

import HistoricoLoading from "../app/historico/loading";

describe("DEBT-003: historico/loading.tsx", () => {
  it("renders with data-testid=historico-loading", () => {
    render(<HistoricoLoading />);
    expect(screen.getByTestId("historico-loading")).toBeInTheDocument();
  });

  it("renders filter bar skeleton", () => {
    render(<HistoricoLoading />);
    const el = screen.getByTestId("historico-loading");
    // Filter bar: flex row with input skeletons
    const filterBar = el.querySelector(".flex.flex-col.sm\\:flex-row");
    expect(filterBar).not.toBeNull();
  });

  it("renders 4 session card skeletons", () => {
    render(<HistoricoLoading />);
    const contentArea = screen.getByRole("status");
    const cards = contentArea.querySelectorAll(".rounded-card");
    expect(cards.length).toBe(4);
  });

  it("session cards have UF badge skeletons", () => {
    render(<HistoricoLoading />);
    const contentArea = screen.getByRole("status");
    const firstCard = contentArea.querySelector(".rounded-card");
    // Each card has 5 UF badge shimmers in a flex-wrap container
    const badgeContainer = firstCard!.querySelector(".flex.flex-wrap.gap-1\\.5");
    expect(badgeContainer).not.toBeNull();
    expect(badgeContainer!.children.length).toBe(5);
  });

  it("matches snapshot", () => {
    const { container } = render(<HistoricoLoading />);
    expect(container.firstChild).toMatchSnapshot();
  });
});
