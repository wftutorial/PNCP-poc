/**
 * NavigationShell Component Tests — FE-025
 *
 * Tests: renders on protected routes, hidden on public routes, auth loading state.
 */

import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import { NavigationShell } from "@/components/NavigationShell";

// Mock next/navigation
const mockUsePathname = jest.fn();
jest.mock("next/navigation", () => ({
  usePathname: () => mockUsePathname(),
  useRouter: () => ({ push: jest.fn(), replace: jest.fn(), prefetch: jest.fn() }),
}));

// Mock AuthProvider
const mockUseAuth = jest.fn();
jest.mock("../../app/components/AuthProvider", () => ({
  useAuth: () => mockUseAuth(),
}));

// Mock Sidebar and BottomNav to keep tests focused on NavigationShell logic
jest.mock("@/components/Sidebar", () => ({
  Sidebar: () => <aside data-testid="sidebar-mock" />,
}));

jest.mock("@/components/BottomNav", () => ({
  BottomNav: () => <nav data-testid="bottom-nav-mock" />,
}));

// Mock MfaEnforcementBanner
jest.mock("@/components/auth/MfaEnforcementBanner", () => ({
  MfaEnforcementBanner: () => null,
}));

const mockSession = { user: { id: "user-1", email: "test@example.com" } };

describe("NavigationShell", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("public routes — no navigation chrome", () => {
    const publicRoutes = ["/", "/login", "/signup", "/planos", "/ajuda", "/blog"];

    publicRoutes.forEach((route) => {
      it(`renders children without navigation on ${route}`, () => {
        mockUsePathname.mockReturnValue(route);
        mockUseAuth.mockReturnValue({ session: mockSession, loading: false });

        render(
          <NavigationShell>
            <main data-testid="page-content">Content</main>
          </NavigationShell>
        );

        expect(screen.getByTestId("page-content")).toBeInTheDocument();
        expect(screen.queryByTestId("sidebar-mock")).not.toBeInTheDocument();
        expect(screen.queryByTestId("bottom-nav-mock")).not.toBeInTheDocument();
      });
    });
  });

  describe("protected routes — with navigation chrome", () => {
    const protectedRoutes = [
      "/buscar",
      "/dashboard",
      "/pipeline",
      "/historico",
      "/conta",
      "/admin",
    ];

    protectedRoutes.forEach((route) => {
      it(`renders sidebar on ${route} when authenticated`, () => {
        mockUsePathname.mockReturnValue(route);
        mockUseAuth.mockReturnValue({ session: mockSession, loading: false });

        render(
          <NavigationShell>
            <main data-testid="page-content">Content</main>
          </NavigationShell>
        );

        expect(screen.getByTestId("sidebar-mock")).toBeInTheDocument();
        expect(screen.getByTestId("bottom-nav-mock")).toBeInTheDocument();
        expect(screen.getByTestId("page-content")).toBeInTheDocument();
      });
    });

    it("renders on nested protected routes like /conta/plano", () => {
      mockUsePathname.mockReturnValue("/conta/plano");
      mockUseAuth.mockReturnValue({ session: mockSession, loading: false });

      render(
        <NavigationShell>
          <main data-testid="page-content">Nested</main>
        </NavigationShell>
      );

      expect(screen.getByTestId("sidebar-mock")).toBeInTheDocument();
    });

    it("renders on /admin sub-routes", () => {
      mockUsePathname.mockReturnValue("/admin/cache");
      mockUseAuth.mockReturnValue({ session: mockSession, loading: false });

      render(
        <NavigationShell>
          <main data-testid="page-content">Admin page</main>
        </NavigationShell>
      );

      expect(screen.getByTestId("sidebar-mock")).toBeInTheDocument();
    });
  });

  describe("auth loading state", () => {
    it("hides navigation while auth is loading even on protected route", () => {
      mockUsePathname.mockReturnValue("/buscar");
      mockUseAuth.mockReturnValue({ session: null, loading: true });

      render(
        <NavigationShell>
          <main data-testid="page-content">Loading...</main>
        </NavigationShell>
      );

      // While loading, render children but no nav chrome
      expect(screen.getByTestId("page-content")).toBeInTheDocument();
      expect(screen.queryByTestId("sidebar-mock")).not.toBeInTheDocument();
      expect(screen.queryByTestId("bottom-nav-mock")).not.toBeInTheDocument();
    });
  });

  describe("unauthenticated user", () => {
    it("hides navigation on protected route when no session", () => {
      mockUsePathname.mockReturnValue("/buscar");
      mockUseAuth.mockReturnValue({ session: null, loading: false });

      render(
        <NavigationShell>
          <main data-testid="page-content">Content</main>
        </NavigationShell>
      );

      expect(screen.getByTestId("page-content")).toBeInTheDocument();
      expect(screen.queryByTestId("sidebar-mock")).not.toBeInTheDocument();
    });
  });

  describe("logged-area footer", () => {
    it("renders footer links on authenticated protected routes", () => {
      mockUsePathname.mockReturnValue("/dashboard");
      mockUseAuth.mockReturnValue({ session: mockSession, loading: false });

      render(
        <NavigationShell>
          <div>Dashboard</div>
        </NavigationShell>
      );

      expect(screen.getByTestId("logged-footer")).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /termos/i })).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /privacidade/i })).toBeInTheDocument();
    });

    it("does not render footer on public routes", () => {
      mockUsePathname.mockReturnValue("/");
      mockUseAuth.mockReturnValue({ session: mockSession, loading: false });

      render(
        <NavigationShell>
          <div>Landing</div>
        </NavigationShell>
      );

      expect(screen.queryByTestId("logged-footer")).not.toBeInTheDocument();
    });
  });
});
