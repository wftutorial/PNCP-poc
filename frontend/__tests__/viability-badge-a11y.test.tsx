/**
 * DEBT-202 AC: axe-core zero violations for ViabilityBadge.
 *
 * Validates WCAG 2.1 AA compliance programmatically using axe-core.
 * Covers: alta, média, baixa levels — each with and without factors.
 */

import React from "react";
import { render } from "@testing-library/react";
import axe from "axe-core";
import ViabilityBadge from "../components/ViabilityBadge";
import type { ViabilityFactors } from "../components/ViabilityBadge";

const mockFactors: ViabilityFactors = {
  modalidade: 100,
  modalidade_label: "Ótimo",
  timeline: 80,
  timeline_label: "12 dias",
  value_fit: 100,
  value_fit_label: "Ideal",
  geography: 100,
  geography_label: "Sua região",
};

/** Run axe on a rendered container and return any violations. */
async function runAxe(container: HTMLElement) {
  const results = await axe.run(container, {
    runOnly: {
      type: "tag",
      values: ["wcag2a", "wcag2aa"],
    },
  });
  return results.violations;
}

describe("ViabilityBadge — axe-core WCAG 2.1 AA", () => {
  it("zero violations: level=alta with factors", async () => {
    const { container } = render(
      <ViabilityBadge level="alta" score={85} factors={mockFactors} />
    );
    const violations = await runAxe(container);
    expect(violations).toHaveLength(0);
  });

  it("zero violations: level=media with factors", async () => {
    const { container } = render(
      <ViabilityBadge level="media" score={55} factors={mockFactors} />
    );
    const violations = await runAxe(container);
    expect(violations).toHaveLength(0);
  });

  it("zero violations: level=baixa with factors", async () => {
    const { container } = render(
      <ViabilityBadge level="baixa" score={25} factors={mockFactors} />
    );
    const violations = await runAxe(container);
    expect(violations).toHaveLength(0);
  });

  it("zero violations: level=alta without factors (score only)", async () => {
    const { container } = render(
      <ViabilityBadge level="alta" score={90} factors={null} />
    );
    const violations = await runAxe(container);
    expect(violations).toHaveLength(0);
  });

  it("zero violations: valueSource=missing warning variant", async () => {
    const { container } = render(
      <ViabilityBadge
        level="media"
        score={55}
        factors={mockFactors}
        valueSource="missing"
      />
    );
    const violations = await runAxe(container);
    expect(violations).toHaveLength(0);
  });

  it("renders nothing (null) when level is undefined — axe passes on empty container", async () => {
    const { container } = render(
      <ViabilityBadge level={undefined} score={undefined} factors={undefined} />
    );
    const violations = await runAxe(container);
    expect(violations).toHaveLength(0);
  });
});
