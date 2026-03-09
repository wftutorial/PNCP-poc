/**
 * CRIT-016 Bug 4: Defensive Rendering — Undefined/Unexpected Props
 *
 * AC11: ViabilityBadge fallback for unknown level
 * AC12: UfProgressGrid fallback for unknown config
 * AC13: ViabilityBadge with level=undefined doesn't crash
 *
 * NOTE: OperationalStateBanner tests removed — component deprecated and deleted (STORY-284 AC6).
 */

import React from "react";
import { render } from "@testing-library/react";
import "@testing-library/jest-dom";
import ViabilityBadge from "../components/ViabilityBadge";
import { UfProgressGrid } from "../app/buscar/components/UfProgressGrid";

describe("CRIT-016 Bug 4: Defensive Rendering", () => {
  // ===========================================================================
  // AC13 + AC11: ViabilityBadge
  // ===========================================================================

  describe("ViabilityBadge", () => {
    it("returns null when level is undefined", () => {
      const { container } = render(<ViabilityBadge level={undefined} />);
      expect(container.firstChild).toBeNull();
    });

    it("returns null when level is null", () => {
      const { container } = render(<ViabilityBadge level={null} />);
      expect(container.firstChild).toBeNull();
    });

    it("renders fallback (baixa) for unknown level value", () => {
      const { container } = render(
        <ViabilityBadge level={"garbage" as any} score={42} />
      );
      // Should render (not crash) — fallback to baixa config
      expect(container.firstChild).not.toBeNull();

      const badge = container.querySelector("[data-testid='viability-badge']");
      expect(badge).toBeInTheDocument();

      // Baixa config uses gray classes
      expect(badge?.className).toMatch(/gray/);
    });

    it("renders alta correctly", () => {
      const { container } = render(
        <ViabilityBadge level="alta" score={85} />
      );
      const badge = container.querySelector("[data-testid='viability-badge']");
      expect(badge).toBeInTheDocument();
      expect(badge?.className).toMatch(/emerald/);
      expect(badge?.getAttribute("data-viability-level")).toBe("alta");
    });

    it("renders media correctly", () => {
      const { container } = render(
        <ViabilityBadge level="media" score={55} />
      );
      const badge = container.querySelector("[data-testid='viability-badge']");
      expect(badge).toBeInTheDocument();
      expect(badge?.className).toMatch(/yellow/);
    });

    it("renders baixa correctly", () => {
      const { container } = render(
        <ViabilityBadge level="baixa" score={25} />
      );
      const badge = container.querySelector("[data-testid='viability-badge']");
      expect(badge).toBeInTheDocument();
      expect(badge?.className).toMatch(/gray/);
    });
  });

  // ===========================================================================
  // AC12: UfProgressGrid
  // ===========================================================================

  describe("UfProgressGrid", () => {
    it("renders valid statuses without crashing", () => {
      const ufStatuses = new Map([
        ["SP", { status: "success" as const, count: 10 }],
        ["RJ", { status: "pending" as const }],
        ["MG", { status: "failed" as const }],
      ]);

      const { container } = render(
        <UfProgressGrid ufStatuses={ufStatuses} totalFound={10} />
      );
      expect(container.textContent).toMatch(/SP/);
      expect(container.textContent).toMatch(/RJ/);
      expect(container.textContent).toMatch(/MG/);
    });

    it("uses fallback for unknown status type (doesn't crash)", () => {
      const ufStatuses = new Map([
        ["SP", { status: "unknown_garbage" as any, count: 5 }],
      ]);

      const { container } = render(
        <UfProgressGrid ufStatuses={ufStatuses} totalFound={5} />
      );
      // Should render without TypeError
      expect(container.firstChild).not.toBeNull();
      expect(container.textContent).toMatch(/SP/);
    });

    it("handles mixed valid and invalid statuses", () => {
      const ufStatuses = new Map([
        ["SP", { status: "success" as const, count: 10 }],
        ["RJ", { status: "broken" as any, count: 0 }],
        ["MG", { status: "recovered" as const, count: 8 }],
      ]);

      const { container } = render(
        <UfProgressGrid ufStatuses={ufStatuses} totalFound={18} />
      );
      expect(container.textContent).toMatch(/SP/);
      expect(container.textContent).toMatch(/RJ/);
      expect(container.textContent).toMatch(/MG/);
    });

    it("handles empty map", () => {
      const { container } = render(
        <UfProgressGrid ufStatuses={new Map()} totalFound={0} />
      );
      expect(container.firstChild).not.toBeNull();
    });
  });
});
