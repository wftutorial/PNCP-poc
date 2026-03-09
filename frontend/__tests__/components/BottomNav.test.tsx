/**
 * BottomNav Component Tests — FE-025
 *
 * Tests: renders mobile nav items, active state, icon display, drawer open/close.
 */

import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { BottomNav } from "@/components/BottomNav";

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
    "aria-label": ariaLabel,
    onClick,
  }: {
    children: React.ReactNode;
    href: string;
    className?: string;
    "aria-current"?: string;
    "aria-label"?: string;
    onClick?: () => void;
  }) {
    return (
      <a href={href} className={className} aria-current={ariaCurrent} aria-label={ariaLabel} onClick={onClick}>
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

describe("BottomNav", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAuth.mockReturnValue({ signOut: mockSignOut, session: null, loading: false });
    mockUsePlan.mockReturnValue({ planInfo: null });
    mockUsePathname.mockReturnValue("/buscar");
  });

  describe("main nav bar", () => {
    it("renders the bottom nav container", () => {
      render(<BottomNav />);

      expect(screen.getByTestId("bottom-nav")).toBeInTheDocument();
    });

    it("renders main navigation items", () => {
      render(<BottomNav />);

      // MAIN_ITEMS: Busca, Pipeline, Hist., Dash
      expect(screen.getByRole("link", { name: /busca/i })).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /pipeline/i })).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /histórico/i })).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /dashboard/i })).toBeInTheDocument();
    });

    it("renders the 'Mais' button to open drawer", () => {
      render(<BottomNav />);

      expect(screen.getByTestId("bottom-nav-more")).toBeInTheDocument();
      expect(screen.getByText("Mais")).toBeInTheDocument();
    });

    it("renders correct hrefs for main items", () => {
      render(<BottomNav />);

      expect(screen.getByRole("link", { name: /busca/i })).toHaveAttribute("href", "/buscar");
      expect(screen.getByRole("link", { name: /pipeline/i })).toHaveAttribute("href", "/pipeline");
      expect(screen.getByRole("link", { name: /histórico/i })).toHaveAttribute("href", "/historico");
    });
  });

  describe("active state", () => {
    it("marks /buscar link as active when on /buscar", () => {
      mockUsePathname.mockReturnValue("/buscar");
      render(<BottomNav />);

      const buscarLink = screen.getByRole("link", { name: /busca/i });
      expect(buscarLink).toHaveAttribute("aria-current", "page");
    });

    it("does not mark other main items as active when on /buscar", () => {
      mockUsePathname.mockReturnValue("/buscar");
      render(<BottomNav />);

      const pipelineLink = screen.getByRole("link", { name: /pipeline/i });
      expect(pipelineLink).not.toHaveAttribute("aria-current", "page");
    });

    it("marks /pipeline as active when on /pipeline", () => {
      mockUsePathname.mockReturnValue("/pipeline");
      render(<BottomNav />);

      const pipelineLink = screen.getByRole("link", { name: /pipeline/i });
      expect(pipelineLink).toHaveAttribute("aria-current", "page");
    });

    it("marks /dashboard as active when on /dashboard", () => {
      mockUsePathname.mockReturnValue("/dashboard");
      render(<BottomNav />);

      const dashLink = screen.getByRole("link", { name: /dashboard/i });
      expect(dashLink).toHaveAttribute("aria-current", "page");
    });
  });

  describe("icons", () => {
    it("renders SVG icons in nav items", () => {
      const { container } = render(<BottomNav />);

      const svgs = container.querySelectorAll("svg");
      // At minimum 4 main items + "Mais" button = 5 SVGs
      expect(svgs.length).toBeGreaterThanOrEqual(5);
    });
  });

  describe("drawer open/close", () => {
    it("drawer is hidden by default", () => {
      render(<BottomNav />);

      expect(screen.queryByTestId("bottom-nav-drawer")).not.toBeInTheDocument();
    });

    it("opens drawer when 'Mais' is clicked", () => {
      render(<BottomNav />);

      fireEvent.click(screen.getByTestId("bottom-nav-more"));

      expect(screen.getByTestId("bottom-nav-drawer")).toBeInTheDocument();
    });

    it("drawer contains Minha Conta and Ajuda links", () => {
      render(<BottomNav />);

      fireEvent.click(screen.getByTestId("bottom-nav-more"));

      expect(screen.getByRole("link", { name: /minha conta/i })).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /ajuda/i })).toBeInTheDocument();
    });

    it("drawer contains logout button", () => {
      render(<BottomNav />);

      fireEvent.click(screen.getByTestId("bottom-nav-more"));

      expect(screen.getByRole("button", { name: /sair/i })).toBeInTheDocument();
    });

    it("closes drawer when backdrop is clicked", () => {
      render(<BottomNav />);

      fireEvent.click(screen.getByTestId("bottom-nav-more"));
      expect(screen.getByTestId("bottom-nav-drawer")).toBeInTheDocument();

      // Click the backdrop (aria-hidden div behind the panel)
      const backdrop = screen.getByTestId("bottom-nav-drawer").querySelector('[aria-hidden="true"]');
      expect(backdrop).toBeTruthy();
      fireEvent.click(backdrop!);

      expect(screen.queryByTestId("bottom-nav-drawer")).not.toBeInTheDocument();
    });

    it("closes drawer on Escape key", () => {
      render(<BottomNav />);

      fireEvent.click(screen.getByTestId("bottom-nav-more"));
      expect(screen.getByTestId("bottom-nav-drawer")).toBeInTheDocument();

      fireEvent.keyDown(document, { key: "Escape" });

      expect(screen.queryByTestId("bottom-nav-drawer")).not.toBeInTheDocument();
    });

    it("calls signOut and closes drawer when logout is clicked", () => {
      render(<BottomNav />);

      fireEvent.click(screen.getByTestId("bottom-nav-more"));
      fireEvent.click(screen.getByRole("button", { name: /sair/i }));

      expect(mockSignOut).toHaveBeenCalledTimes(1);
      expect(screen.queryByTestId("bottom-nav-drawer")).not.toBeInTheDocument();
    });

    it("has dialog role and aria-modal on drawer", () => {
      render(<BottomNav />);

      fireEvent.click(screen.getByTestId("bottom-nav-more"));

      const drawer = screen.getByRole("dialog");
      expect(drawer).toHaveAttribute("aria-modal", "true");
    });
  });

  describe("past_due badge in drawer", () => {
    it("shows red dot on Minha Conta when subscription is past_due", () => {
      mockUsePlan.mockReturnValue({
        planInfo: { subscription_status: "past_due" },
      });

      render(<BottomNav />);
      fireEvent.click(screen.getByTestId("bottom-nav-more"));

      expect(screen.getByTestId("conta-past-due-badge-mobile")).toBeInTheDocument();
    });

    it("does not show red dot when subscription is active", () => {
      mockUsePlan.mockReturnValue({
        planInfo: { subscription_status: "active" },
      });

      render(<BottomNav />);
      fireEvent.click(screen.getByTestId("bottom-nav-more"));

      expect(screen.queryByTestId("conta-past-due-badge-mobile")).not.toBeInTheDocument();
    });
  });

  describe("accessibility", () => {
    it("has accessible label on bottom nav", () => {
      render(<BottomNav />);

      expect(screen.getByRole("navigation", { name: /navegação mobile/i })).toBeInTheDocument();
    });

    it("renders a spacer to avoid content hidden behind nav", () => {
      const { container } = render(<BottomNav />);

      // The spacer div exists to push content above the fixed bar
      const spacer = container.querySelector('[aria-hidden="true"].h-16');
      expect(spacer).toBeInTheDocument();
    });
  });
});
