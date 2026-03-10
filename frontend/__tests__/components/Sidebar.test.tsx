/**
 * Sidebar Component Tests — FE-025
 *
 * Tests: renders nav items, active state highlighting, collapse toggle, logout button.
 */

import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { Sidebar } from "@/components/Sidebar";

// Mock next/navigation
const mockUsePathname = jest.fn();
jest.mock("next/navigation", () => ({
  usePathname: () => mockUsePathname(),
  useRouter: () => ({ push: jest.fn(), replace: jest.fn(), prefetch: jest.fn() }),
}));

// Mock next/link
jest.mock("next/link", () => {
  return function MockLink({
    children,
    href,
    className,
    "aria-current": ariaCurrent,
  }: {
    children: React.ReactNode;
    href: string;
    className?: string;
    "aria-current"?: string;
  }) {
    return (
      <a href={href} className={className} aria-current={ariaCurrent}>
        {children}
      </a>
    );
  };
});

// Mock AuthProvider
const mockSignOut = jest.fn();
const mockUseAuth = jest.fn();
jest.mock("../../app/components/AuthProvider", () => ({
  useAuth: () => mockUseAuth(),
}));

// Mock usePlan
const mockUsePlan = jest.fn();
jest.mock("../../hooks/usePlan", () => ({
  usePlan: () => mockUsePlan(),
}));

// Mock storage utility
jest.mock("../../lib/storage", () => ({
  safeSetItem: jest.fn(),
  safeGetItem: jest.fn(() => null),
  safeRemoveItem: jest.fn(),
}));

// Provide a localStorage mock
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(window, "localStorage", { value: localStorageMock });

describe("Sidebar", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.clear();

    mockUseAuth.mockReturnValue({ signOut: mockSignOut, session: null, loading: false });
    mockUsePlan.mockReturnValue({ planInfo: null });
    mockUsePathname.mockReturnValue("/buscar");
  });

  describe("navigation items", () => {
    it("renders all primary navigation items", () => {
      render(<Sidebar />);

      expect(screen.getByRole("link", { name: /buscar/i })).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /dashboard/i })).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /pipeline/i })).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /histórico/i })).toBeInTheDocument();
    });

    it("renders secondary navigation items", () => {
      render(<Sidebar />);

      expect(screen.getByRole("link", { name: /minha conta/i })).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /ajuda/i })).toBeInTheDocument();
    });

    it("renders correct href for each nav item", () => {
      mockUsePathname.mockReturnValue("/dashboard");
      render(<Sidebar />);

      expect(screen.getByRole("link", { name: /buscar/i })).toHaveAttribute("href", "/buscar");
      expect(screen.getByRole("link", { name: /dashboard/i })).toHaveAttribute("href", "/dashboard");
      expect(screen.getByRole("link", { name: /pipeline/i })).toHaveAttribute("href", "/pipeline");
      expect(screen.getByRole("link", { name: /minha conta/i })).toHaveAttribute("href", "/conta");
    });
  });

  describe("active state highlighting", () => {
    it("marks current page link as aria-current=page", () => {
      mockUsePathname.mockReturnValue("/buscar");
      render(<Sidebar />);

      const buscarLink = screen.getByRole("link", { name: /buscar/i });
      expect(buscarLink).toHaveAttribute("aria-current", "page");
    });

    it("does not mark other links as current", () => {
      mockUsePathname.mockReturnValue("/buscar");
      render(<Sidebar />);

      const dashboardLink = screen.getByRole("link", { name: /dashboard/i });
      expect(dashboardLink).not.toHaveAttribute("aria-current", "page");
    });

    it("marks /conta as active when on /conta/plano", () => {
      mockUsePathname.mockReturnValue("/conta/plano");
      render(<Sidebar />);

      const contaLink = screen.getByRole("link", { name: /minha conta/i });
      expect(contaLink).toHaveAttribute("aria-current", "page");
    });

    it("matches /buscar exactly — does not highlight for /buscar/qualquercoisa", () => {
      mockUsePathname.mockReturnValue("/buscar/alguma-coisa");
      render(<Sidebar />);

      const buscarLink = screen.getByRole("link", { name: /buscar/i });
      // /buscar uses exact match, so /buscar/alguma-coisa should NOT be active
      expect(buscarLink).not.toHaveAttribute("aria-current", "page");
    });
  });

  describe("collapse toggle", () => {
    it("renders the collapse toggle button", () => {
      render(<Sidebar />);

      expect(screen.getByTestId("sidebar-toggle")).toBeInTheDocument();
    });

    it("has aria-label 'Recolher menu' when expanded", () => {
      render(<Sidebar />);

      const toggle = screen.getByTestId("sidebar-toggle");
      expect(toggle).toHaveAttribute("aria-label", "Recolher menu");
    });

    it("hides nav labels after collapsing", () => {
      render(<Sidebar />);

      // Labels are visible when expanded
      expect(screen.getByText("Buscar")).toBeInTheDocument();

      fireEvent.click(screen.getByTestId("sidebar-toggle"));

      // Labels disappear when collapsed (hidden by conditional rendering)
      expect(screen.queryByText("Buscar")).not.toBeInTheDocument();
    });

    it("updates aria-label to 'Expandir menu' after collapse", () => {
      render(<Sidebar />);

      fireEvent.click(screen.getByTestId("sidebar-toggle"));

      const toggle = screen.getByTestId("sidebar-toggle");
      expect(toggle).toHaveAttribute("aria-label", "Expandir menu");
    });

    it("restores labels after expanding again", () => {
      render(<Sidebar />);

      const toggle = screen.getByTestId("sidebar-toggle");
      fireEvent.click(toggle); // collapse
      fireEvent.click(toggle); // expand

      expect(screen.getByText("Buscar")).toBeInTheDocument();
    });
  });

  describe("logout button", () => {
    it("renders the sign out button", () => {
      render(<Sidebar />);

      expect(screen.getByRole("button", { name: /sair/i })).toBeInTheDocument();
    });

    it("calls signOut when logout button is clicked", () => {
      render(<Sidebar />);

      fireEvent.click(screen.getByRole("button", { name: /sair/i }));

      expect(mockSignOut).toHaveBeenCalledTimes(1);
    });
  });

  describe("past_due badge", () => {
    it("shows red dot on Minha Conta when subscription is past_due", () => {
      mockUsePlan.mockReturnValue({
        planInfo: { subscription_status: "past_due" },
      });
      render(<Sidebar />);

      expect(screen.getByTestId("conta-past-due-badge")).toBeInTheDocument();
    });

    it("does not show red dot when subscription is active", () => {
      mockUsePlan.mockReturnValue({
        planInfo: { subscription_status: "active" },
      });
      render(<Sidebar />);

      expect(screen.queryByTestId("conta-past-due-badge")).not.toBeInTheDocument();
    });
  });

  describe("accessibility", () => {
    it("has a nav landmark with accessible label", () => {
      render(<Sidebar />);

      expect(screen.getByRole("navigation", { name: /navegação principal/i })).toBeInTheDocument();
    });

    it("renders as aside element", () => {
      const { container } = render(<Sidebar />);

      expect(container.querySelector("aside")).toBeInTheDocument();
    });
  });
});
