/**
 * DEBT-FE-012: Feature gates configuration tests
 */
import { GATED_FEATURES, isFeatureGated } from "../../lib/feature-gates";

describe("feature-gates (DEBT-FE-012)", () => {
  it("alertas is gated", () => {
    expect(isFeatureGated("alertas")).toBe(true);
    expect(GATED_FEATURES.has("alertas")).toBe(true);
  });

  it("mensagens is NOT gated (ISSUE-028: enabled)", () => {
    expect(isFeatureGated("mensagens")).toBe(false);
    expect(GATED_FEATURES.has("mensagens")).toBe(false);
  });

  it("buscar is not gated", () => {
    expect(isFeatureGated("buscar")).toBe(false);
  });

  it("unknown features are not gated", () => {
    expect(isFeatureGated("nonexistent")).toBe(false);
  });
});
