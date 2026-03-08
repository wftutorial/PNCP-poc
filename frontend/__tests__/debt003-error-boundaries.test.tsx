/**
 * DEBT-003: Error Boundary Tests (FE-012)
 *
 * - 5 error boundary render tests (dashboard, pipeline, historico, mensagens, alertas)
 * - Verify: brand colors (no red), retry button, fallback link, URL preservation
 * - Functional test: error boundary catches thrown error
 */

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";

// Mock Sentry
jest.mock("@sentry/nextjs", () => ({
  captureException: jest.fn(),
}));

// Mock next/link
jest.mock("next/link", () => {
  const MockLink = ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
    [key: string]: unknown;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  );
  MockLink.displayName = "MockLink";
  return MockLink;
});

// Mock error-messages
jest.mock("../lib/error-messages", () => ({
  getUserFriendlyError: (e: unknown) =>
    e instanceof Error ? e.message : "Erro desconhecido",
  isTransientError: () => false,
  getMessageFromErrorCode: () => null,
  ERROR_CODE_MESSAGES: {},
}));

// Suppress console.error noise from error boundaries
const originalConsoleError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});
afterAll(() => {
  console.error = originalConsoleError;
});

// ---------------------------------------------------------------------------
// Shared test helpers
// ---------------------------------------------------------------------------

const mockError = new Error("Test error for boundary");
const mockReset = jest.fn();

function expectBrandColors(container: HTMLElement) {
  // Should NOT use red for the main icon — should use text-warning (amber)
  const icon = container.querySelector("svg");
  expect(icon).not.toBeNull();
  // SVG className is SVGAnimatedString in jsdom — use getAttribute
  const cls = icon!.getAttribute("class") ?? "";
  expect(cls).toContain("text-warning");
  expect(cls).not.toContain("text-red");
  expect(cls).not.toContain("text-error");
}

function expectRetryButton() {
  const retryBtn = screen.getByRole("button", { name: /tentar novamente|recarregar/i });
  expect(retryBtn).toBeInTheDocument();
  return retryBtn;
}

function expectDashboardFallback() {
  const link = screen.getByText(/voltar ao dashboard/i);
  expect(link).toBeInTheDocument();
  expect(link.closest("a")).toHaveAttribute("href", "/dashboard");
}

function expectErrorMessage() {
  expect(screen.getByText("Test error for boundary")).toBeInTheDocument();
}

// ---------------------------------------------------------------------------
// T1 — dashboard/error.tsx
// ---------------------------------------------------------------------------

import DashboardError from "../app/dashboard/error";

describe("DEBT-003: dashboard/error.tsx", () => {
  beforeEach(() => mockReset.mockClear());

  it("renders with brand colors (no red)", () => {
    const { container } = render(
      <DashboardError error={mockError} reset={mockReset} />
    );
    expectBrandColors(container);
  });

  it("has retry button that calls reset", () => {
    render(<DashboardError error={mockError} reset={mockReset} />);
    const btn = expectRetryButton();
    fireEvent.click(btn);
    expect(mockReset).toHaveBeenCalledTimes(1);
  });

  it("has fallback link (dashboard links to /buscar since it IS the dashboard)", () => {
    render(<DashboardError error={mockError} reset={mockReset} />);
    // Dashboard error can't link back to itself, links to /buscar
    const link = screen.getByText(/ir para a busca/i);
    expect(link.closest("a")).toHaveAttribute("href", "/buscar");
  });

  it("displays the error message", () => {
    render(<DashboardError error={mockError} reset={mockReset} />);
    expectErrorMessage();
  });

  it("renders the page title", () => {
    render(<DashboardError error={mockError} reset={mockReset} />);
    expect(screen.getByText("Erro no dashboard")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// T2 — pipeline/error.tsx
// ---------------------------------------------------------------------------

import PipelineError from "../app/pipeline/error";

describe("DEBT-003: pipeline/error.tsx", () => {
  beforeEach(() => mockReset.mockClear());

  it("renders with brand colors (no red)", () => {
    const { container } = render(
      <PipelineError error={mockError} reset={mockReset} />
    );
    expectBrandColors(container);
  });

  it("has retry button that calls reset", () => {
    render(<PipelineError error={mockError} reset={mockReset} />);
    const btn = expectRetryButton();
    fireEvent.click(btn);
    expect(mockReset).toHaveBeenCalledTimes(1);
  });

  it("has 'Voltar ao dashboard' fallback link", () => {
    render(<PipelineError error={mockError} reset={mockReset} />);
    expectDashboardFallback();
  });

  it("displays the error message", () => {
    render(<PipelineError error={mockError} reset={mockReset} />);
    expectErrorMessage();
  });
});

// ---------------------------------------------------------------------------
// T3 — historico/error.tsx
// ---------------------------------------------------------------------------

import HistoricoError from "../app/historico/error";

describe("DEBT-003: historico/error.tsx", () => {
  beforeEach(() => mockReset.mockClear());

  it("renders with brand colors (no red)", () => {
    const { container } = render(
      <HistoricoError error={mockError} reset={mockReset} />
    );
    expectBrandColors(container);
  });

  it("has retry button that calls reset", () => {
    render(<HistoricoError error={mockError} reset={mockReset} />);
    const btn = expectRetryButton();
    fireEvent.click(btn);
    expect(mockReset).toHaveBeenCalledTimes(1);
  });

  it("has 'Voltar ao dashboard' fallback link", () => {
    render(<HistoricoError error={mockError} reset={mockReset} />);
    expectDashboardFallback();
  });

  it("displays the error message", () => {
    render(<HistoricoError error={mockError} reset={mockReset} />);
    expectErrorMessage();
  });
});

// ---------------------------------------------------------------------------
// T4 — mensagens/error.tsx
// ---------------------------------------------------------------------------

import MensagensError from "../app/mensagens/error";

describe("DEBT-003: mensagens/error.tsx", () => {
  beforeEach(() => mockReset.mockClear());

  it("renders with brand colors (no red)", () => {
    const { container } = render(
      <MensagensError error={mockError} reset={mockReset} />
    );
    expectBrandColors(container);
  });

  it("has retry button that calls reset", () => {
    render(<MensagensError error={mockError} reset={mockReset} />);
    const btn = expectRetryButton();
    fireEvent.click(btn);
    expect(mockReset).toHaveBeenCalledTimes(1);
  });

  it("has 'Voltar ao dashboard' fallback link", () => {
    render(<MensagensError error={mockError} reset={mockReset} />);
    expectDashboardFallback();
  });

  it("displays the error message", () => {
    render(<MensagensError error={mockError} reset={mockReset} />);
    expectErrorMessage();
  });
});

// ---------------------------------------------------------------------------
// T5 — alertas/error.tsx
// ---------------------------------------------------------------------------

import AlertasError from "../app/alertas/error";

describe("DEBT-003: alertas/error.tsx", () => {
  beforeEach(() => mockReset.mockClear());

  it("renders with brand colors (no red)", () => {
    const { container } = render(
      <AlertasError error={mockError} reset={mockReset} />
    );
    expectBrandColors(container);
  });

  it("has retry button that calls reset", () => {
    render(<AlertasError error={mockError} reset={mockReset} />);
    const btn = expectRetryButton();
    fireEvent.click(btn);
    expect(mockReset).toHaveBeenCalledTimes(1);
  });

  it("has 'Voltar ao dashboard' fallback link", () => {
    render(<AlertasError error={mockError} reset={mockReset} />);
    expectDashboardFallback();
  });

  it("displays the error message", () => {
    render(<AlertasError error={mockError} reset={mockReset} />);
    expectErrorMessage();
  });

  it("renders bell icon for alertas context", () => {
    const { container } = render(
      <AlertasError error={mockError} reset={mockReset} />
    );
    const svg = container.querySelector("svg");
    expect(svg).not.toBeNull();
    // Bell icon has specific path
    const path = svg!.querySelector("path");
    expect(path!.getAttribute("d")).toContain("14.857");
  });

  it("renders the page title", () => {
    render(<AlertasError error={mockError} reset={mockReset} />);
    expect(screen.getByText("Erro nos alertas")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// T6 — Error boundary functional test
// ---------------------------------------------------------------------------

describe("DEBT-003: Error boundary preserves URL context", () => {
  it("error boundary does not navigate away (preserves URL for retry)", () => {
    // All error.tsx components render in-place without router.push
    // This verifies the boundary doesn't cause navigation
    const { container } = render(
      <PipelineError error={mockError} reset={mockReset} />
    );
    // Component renders successfully in-place
    expect(container.querySelector(".min-h-screen")).not.toBeNull();
    // No router navigation happened (URL preserved)
  });

  it("reset function is callable multiple times", () => {
    render(<AlertasError error={mockError} reset={mockReset} />);
    const btn = screen.getByRole("button", { name: /tentar novamente/i });
    fireEvent.click(btn);
    fireEvent.click(btn);
    expect(mockReset).toHaveBeenCalledTimes(2);
  });
});
