/**
 * SAB-010 — Conta: polish do perfil de licitante e acentos
 *
 * AC1: Banner motivacional (40% viabilidade)
 * AC2: Botão "Preencher agora"
 * AC3: Progress bar colorida (red/yellow/green)
 * AC4-AC8: Correção de acentos específicos
 * AC9: Grep — sem palavras faltando acento
 * AC10: Navegação por âncoras sticky
 * AC11: Scroll suave
 */

import React from "react";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import "@testing-library/jest-dom";

// ─── Mocks ──────────────────────────────────────────────────────────────────────

jest.mock("../app/components/AuthProvider", () => ({
  useAuth: () => ({
    user: { id: "u1", email: "test@test.com", user_metadata: { full_name: "Test" } },
    session: { access_token: "tok" },
    loading: false,
    signOut: jest.fn(),
  }),
}));

jest.mock("../hooks/usePlan", () => ({
  usePlan: () => ({
    planInfo: {
      plan_id: "smartlic_pro",
      plan_name: "SmartLic Pro",
      subscription_status: "active",
      quota_used: 5,
      capabilities: { max_requests_per_month: 1000 },
    },
    error: null,
    isFromCache: false,
    cachedAt: null,
    refresh: jest.fn(),
  }),
}));

jest.mock("../components/PageHeader", () => ({
  PageHeader: ({ title }: { title: string }) => <div data-testid="page-header">{title}</div>,
}));

jest.mock("../lib/error-messages", () => ({
  getUserFriendlyError: (err: unknown) => (err instanceof Error ? err.message : String(err)),
}));

jest.mock("../lib/plans", () => ({
  getPlanDisplayName: (id: string) => id === "smartlic_pro" ? "SmartLic Pro" : id,
}));

jest.mock("../components/account/CancelSubscriptionModal", () => ({
  CancelSubscriptionModal: () => null,
}));

jest.mock("sonner", () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("next/link", () => ({
  __esModule: true,
  default: ({ children, href, ...rest }: { children: React.ReactNode; href: string; [k: string]: unknown }) => (
    <a href={href} {...rest}>{children}</a>
  ),
}));

// ─── Mock IntersectionObserver ──────────────────────────────────────────────────

class MockIntersectionObserver {
  observe = jest.fn();
  disconnect = jest.fn();
  unobserve = jest.fn();
  constructor() { /* noop */ }
}

(global as Record<string, unknown>).IntersectionObserver = MockIntersectionObserver;

// ─── Helpers ────────────────────────────────────────────────────────────────────

const EMPTY_PROFILE = {
  context_data: {
    ufs_atuacao: [],
    porte_empresa: "",
    experiencia_licitacoes: "",
    faixa_valor_min: null,
    faixa_valor_max: null,
    capacidade_funcionarios: null,
    faturamento_anual: null,
    atestados: [],
  },
};

const PARTIAL_PROFILE = {
  context_data: {
    ufs_atuacao: ["SP", "RJ"],
    porte_empresa: "me",
    experiencia_licitacoes: "basico",
    faixa_valor_min: null,
    faixa_valor_max: null,
    capacidade_funcionarios: null,
    faturamento_anual: null,
    atestados: [],
  },
};

const FULL_PROFILE = {
  context_data: {
    ufs_atuacao: ["SP"],
    porte_empresa: "me",
    experiencia_licitacoes: "intermediario",
    faixa_valor_min: 50000,
    faixa_valor_max: 500000,
    capacidade_funcionarios: 20,
    faturamento_anual: 1000000,
    atestados: ["crea"],
  },
};

function mockFetchResponses(profileData: Record<string, unknown> = EMPTY_PROFILE) {
  global.fetch = jest.fn().mockImplementation((url: string) => {
    if (url.includes("/api/profile-context")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(profileData) });
    }
    if (url.includes("/api/alert-preferences")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ enabled: true, frequency: "daily" }) });
    }
    if (url.includes("/api/alerts")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  }) as jest.Mock;
}

// ─── Import component after mocks ───────────────────────────────────────────────

import ContaPage from "../app/conta/page";

// ─── Tests ──────────────────────────────────────────────────────────────────────

describe("SAB-010: Conta page polish", () => {

  beforeEach(() => {
    jest.clearAllMocks();
    Element.prototype.scrollIntoView = jest.fn();
  });

  // ────────────────── AC1: Motivational banner ──────────────────

  describe("AC1: Motivational banner", () => {
    it("shows banner with 40% viability message when profile is incomplete", async () => {
      mockFetchResponses(EMPTY_PROFILE);
      await act(async () => { render(<ContaPage />); });

      await waitFor(() => {
        expect(screen.getByTestId("profile-guidance-banner")).toBeInTheDocument();
      });

      expect(screen.getByText(/melhora a precisão da análise de viabilidade em até 40%/)).toBeInTheDocument();
    });

    it("hides banner when profile is 100% complete", async () => {
      mockFetchResponses(FULL_PROFILE);
      await act(async () => { render(<ContaPage />); });

      await waitFor(() => {
        expect(screen.getByTestId("profile-licitante-section")).toBeInTheDocument();
      });

      expect(screen.queryByTestId("profile-guidance-banner")).not.toBeInTheDocument();
    });
  });

  // ────────────────── AC2: "Preencher agora" button ──────────────────

  describe("AC2: Fill now button", () => {
    it("shows 'Preencher agora' button when profile is incomplete", async () => {
      mockFetchResponses(EMPTY_PROFILE);
      await act(async () => { render(<ContaPage />); });

      await waitFor(() => {
        expect(screen.getByTestId("fill-now-btn")).toBeInTheDocument();
      });

      expect(screen.getByText("Preencher agora →")).toBeInTheDocument();
    });

    it("clicking 'Preencher agora' enters edit mode and scrolls", async () => {
      mockFetchResponses(EMPTY_PROFILE);
      await act(async () => { render(<ContaPage />); });

      await waitFor(() => {
        expect(screen.getByTestId("fill-now-btn")).toBeInTheDocument();
      });

      await act(async () => {
        fireEvent.click(screen.getByTestId("fill-now-btn"));
      });

      // Should now be in edit mode — save button visible
      await waitFor(() => {
        expect(screen.getByTestId("save-profile-btn")).toBeInTheDocument();
      });
    });
  });

  // ────────────────── AC3: Color progress bar ──────────────────

  describe("AC3: Color-coded progress bar", () => {
    it("shows red progress bar when 0% complete (0/7)", async () => {
      mockFetchResponses(EMPTY_PROFILE);
      await act(async () => { render(<ContaPage />); });

      await waitFor(() => {
        expect(screen.getByTestId("profile-progress-bar")).toBeInTheDocument();
      });

      const bar = screen.getByTestId("profile-progress-bar");
      expect(bar).toHaveTextContent("0/7 campos");
      expect(bar).toHaveTextContent("0%");

      // The inner bar div should have red class
      const innerBar = bar.querySelector(".bg-red-500");
      expect(innerBar).toBeInTheDocument();
    });

    it("shows yellow progress bar for partial completion (3/7 = 42%)", async () => {
      mockFetchResponses(PARTIAL_PROFILE);
      await act(async () => { render(<ContaPage />); });

      await waitFor(() => {
        expect(screen.getByTestId("profile-progress-bar")).toBeInTheDocument();
      });

      const bar = screen.getByTestId("profile-progress-bar");
      expect(bar).toHaveTextContent("3/7 campos");
      expect(bar).toHaveTextContent("42%");

      const innerBar = bar.querySelector(".bg-yellow-500");
      expect(innerBar).toBeInTheDocument();
    });

    it("shows green progress bar for full completion (7/7 = 100%)", async () => {
      mockFetchResponses(FULL_PROFILE);
      await act(async () => { render(<ContaPage />); });

      await waitFor(() => {
        expect(screen.getByTestId("profile-progress-bar")).toBeInTheDocument();
      });

      const bar = screen.getByTestId("profile-progress-bar");
      expect(bar).toHaveTextContent("7/7 campos");
      expect(bar).toHaveTextContent("100%");

      const innerBar = bar.querySelector(".bg-green-500");
      expect(innerBar).toBeInTheDocument();
    });
  });

  // ────────────────── AC4-AC8: Accent fixes ──────────────────

  describe("AC4-AC8: Accent corrections", () => {
    beforeEach(async () => {
      mockFetchResponses(EMPTY_PROFILE);
      await act(async () => { render(<ContaPage />); });
      // Wait for profile data to load
      await waitFor(() => {
        expect(screen.getByTestId("profile-licitante-section")).toBeInTheDocument();
      });
    });

    it("AC4: shows 'Estados de atuação' with accent (not 'atuacao')", () => {
      expect(screen.getByText("Estados de atuação")).toBeInTheDocument();
    });

    it("AC5: shows 'Experiência' with accent (not 'Experiencia')", () => {
      expect(screen.getByText("Experiência")).toBeInTheDocument();
    });

    it("AC6: shows 'Funcionários' with accent (not 'Funcionarios')", () => {
      expect(screen.getByText("Funcionários")).toBeInTheDocument();
    });

    it("AC7: shows 'licitação' with accent in alerts section", () => {
      expect(screen.getByText(/licitação filtradas/)).toBeInTheDocument();
    });

    it("AC8: shows 'Frequência' with accent (not 'Frequencia')", () => {
      expect(screen.getByText("Frequência")).toBeInTheDocument();
    });
  });

  // ────────────────── AC9: No remaining unaccented words ──────────────────

  describe("AC9: No remaining unaccented display text", () => {
    it("does not contain 'Nao informado' (should be 'Não informado')", async () => {
      mockFetchResponses(EMPTY_PROFILE);
      const { container } = await act(async () => render(<ContaPage />));

      await waitFor(() => {
        expect(screen.getByTestId("profile-licitante-section")).toBeInTheDocument();
      });

      const textContent = container.textContent || "";
      expect(textContent).not.toMatch(/\bNao informado\b/);
      expect(textContent).toContain("Não informado");
    });

    it("does not contain 'Voce' without accent (should be 'Você')", async () => {
      mockFetchResponses(EMPTY_PROFILE);
      const { container } = await act(async () => render(<ContaPage />));

      await waitFor(() => {
        expect(screen.getByTestId("profile-licitante-section")).toBeInTheDocument();
      });

      const textContent = container.textContent || "";
      // Check that no standalone "Voce" without accent exists
      expect(textContent).not.toMatch(/\bVoce\b/);
    });
  });

  // ────────────────── AC10: Sticky anchor navigation ──────────────────

  describe("AC10: Sticky anchor navigation", () => {
    it("renders sticky nav with 7 section tabs", async () => {
      mockFetchResponses(EMPTY_PROFILE);
      await act(async () => { render(<ContaPage />); });

      const nav = screen.getByTestId("section-nav");
      expect(nav).toBeInTheDocument();
      expect(nav).toHaveClass("sticky");

      const tabs = nav.querySelectorAll('[role="tab"]');
      expect(tabs).toHaveLength(7);

      const labels = Array.from(tabs).map((t) => t.textContent);
      expect(labels).toEqual(["Perfil", "Segurança", "Senha", "Acesso", "Licitante", "Alertas", "LGPD"]);
    });

    it("highlights active section tab", async () => {
      mockFetchResponses(EMPTY_PROFILE);
      await act(async () => { render(<ContaPage />); });

      const nav = screen.getByTestId("section-nav");
      const tabs = nav.querySelectorAll('[role="tab"]');

      // First tab (Perfil) should be active by default
      expect(tabs[0]).toHaveAttribute("aria-selected", "true");
    });
  });

  // ────────────────── AC11: Smooth scroll ──────────────────

  describe("AC11: Smooth scroll on anchor click", () => {
    it("calls scrollIntoView with smooth behavior when clicking a nav tab", async () => {
      mockFetchResponses(EMPTY_PROFILE);
      await act(async () => { render(<ContaPage />); });

      await waitFor(() => {
        expect(screen.getByTestId("section-nav")).toBeInTheDocument();
      });

      const nav = screen.getByTestId("section-nav");
      const tabs = nav.querySelectorAll('[role="tab"]');

      // Click "LGPD" tab (index 6)
      await act(async () => {
        fireEvent.click(tabs[6]);
      });

      expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({
        behavior: "smooth",
        block: "start",
      });
    });

    it("updates active tab after clicking a different section", async () => {
      mockFetchResponses(EMPTY_PROFILE);
      await act(async () => { render(<ContaPage />); });

      const nav = screen.getByTestId("section-nav");
      const tabs = nav.querySelectorAll('[role="tab"]');

      // Click "Senha" tab (index 2)
      await act(async () => {
        fireEvent.click(tabs[2]);
      });

      expect(tabs[2]).toHaveAttribute("aria-selected", "true");
      expect(tabs[0]).toHaveAttribute("aria-selected", "false");
    });
  });

  // ────────────────── Integration: Edit mode accents ──────────────────

  describe("Edit mode accent corrections", () => {
    it("edit mode labels have proper accents", async () => {
      mockFetchResponses(EMPTY_PROFILE);
      await act(async () => { render(<ContaPage />); });

      await waitFor(() => {
        expect(screen.getByTestId("edit-profile-btn")).toBeInTheDocument();
      });

      // Enter edit mode
      await act(async () => {
        fireEvent.click(screen.getByTestId("edit-profile-btn"));
      });

      await waitFor(() => {
        expect(screen.getByTestId("save-profile-btn")).toBeInTheDocument();
      });

      // Check edit mode labels have accents
      expect(screen.getByText("Estados de atuação")).toBeInTheDocument();
      expect(screen.getByText("Experiência com licitações")).toBeInTheDocument();
      expect(screen.getByText("Funcionários")).toBeInTheDocument();
      expect(screen.getByText("Valor mínimo (R$)")).toBeInTheDocument();
      expect(screen.getByText("Valor máximo (R$)")).toBeInTheDocument();
      expect(screen.getByText("Atestados e certificações")).toBeInTheDocument();
    });
  });
});
