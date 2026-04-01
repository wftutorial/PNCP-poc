/**
 * DEBT-204 Track 3: BannerStack unit tests
 * AC17: Max 2 banners visible simultaneously
 * AC18: Non-error banners auto-dismiss after 5 seconds
 * AC19: 5 simultaneous banners → only 2 visible in DOM
 */

import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BannerStack, BannerItem } from "../app/buscar/components/BannerStack";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeItem(
  id: string,
  type: BannerItem["type"],
  label: string,
  priority?: number
): BannerItem {
  return {
    id,
    type,
    content: <div data-testid={`content-${id}`}>{label}</div>,
    priority,
  };
}

// ---------------------------------------------------------------------------
// Basic rendering
// ---------------------------------------------------------------------------

describe("BannerStack — basic rendering", () => {
  it("renders nothing when banners array is empty", () => {
    const { container } = render(<BannerStack banners={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders a single banner without expand toggle", () => {
    const banners = [makeItem("b1", "info", "Info message")];
    render(<BannerStack banners={banners} />);
    expect(screen.getByText("Info message")).toBeInTheDocument();
    expect(screen.queryByTestId("banner-stack-toggle")).toBeNull();
  });

  it("renders exactly maxVisible (2) banners by default when given more", () => {
    const banners = [
      makeItem("b1", "info", "Info 1"),
      makeItem("b2", "info", "Info 2"),
      makeItem("b3", "info", "Info 3"),
    ];
    render(<BannerStack banners={banners} />);

    // Top 2 visible
    expect(screen.getByText("Info 1")).toBeInTheDocument();
    expect(screen.getByText("Info 2")).toBeInTheDocument();

    // 3rd is in the overflow section (rendered but hidden via CSS)
    // It should exist in the DOM but the overflow region should have aria-hidden=true
    const overflow = screen.getByTestId("banner-stack-overflow");
    expect(overflow).toHaveAttribute("aria-hidden", "true");
  });

  it("respects custom maxVisible prop", () => {
    const banners = [
      makeItem("b1", "info", "Info 1"),
      makeItem("b2", "info", "Info 2"),
      makeItem("b3", "info", "Info 3"),
      makeItem("b4", "info", "Info 4"),
    ];
    render(<BannerStack banners={banners} maxVisible={3} />);

    // With maxVisible=3, toggle shows only 1 extra
    const toggle = screen.getByTestId("banner-stack-toggle");
    expect(toggle).toHaveTextContent("+1");
  });
});

// ---------------------------------------------------------------------------
// Priority ordering: error > warning > info > success
// ---------------------------------------------------------------------------

describe("BannerStack — severity priority ordering", () => {
  it("shows error banners before warning before info before success", () => {
    const banners = [
      makeItem("s1", "success", "Success msg"),
      makeItem("i1", "info", "Info msg"),
      makeItem("w1", "warning", "Warning msg"),
      makeItem("e1", "error", "Error msg"),
    ];
    render(<BannerStack banners={banners} />);

    // With maxVisible=2, top 2 should be error + warning
    expect(screen.getByTestId("content-e1")).toBeInTheDocument();
    expect(screen.getByTestId("content-w1")).toBeInTheDocument();

    // info and success are in overflow (hidden)
    const overflow = screen.getByTestId("banner-stack-overflow");
    expect(overflow).toHaveAttribute("aria-hidden", "true");
    expect(overflow).toContainElement(screen.getByTestId("content-i1"));
    expect(overflow).toContainElement(screen.getByTestId("content-s1"));
  });

  it("orders same-severity banners by priority value (higher first)", () => {
    const banners = [
      makeItem("low", "warning", "Low priority warning", 0),
      makeItem("high", "warning", "High priority warning", 10),
      makeItem("mid", "warning", "Mid priority warning", 5),
    ];
    render(<BannerStack banners={banners} maxVisible={1} />);

    // Only the highest-priority warning should be in the top slot
    // The overflow region should be aria-hidden and contain the other two
    expect(screen.getByTestId("content-high")).toBeInTheDocument();
    const overflow = screen.getByTestId("banner-stack-overflow");
    expect(overflow).toContainElement(screen.getByTestId("content-mid"));
    expect(overflow).toContainElement(screen.getByTestId("content-low"));
  });
});

// ---------------------------------------------------------------------------
// Expand / collapse
// ---------------------------------------------------------------------------

describe("BannerStack — expand/collapse", () => {
  it("shows expand toggle when there are more banners than maxVisible", () => {
    const banners = [
      makeItem("b1", "info", "Info 1"),
      makeItem("b2", "info", "Info 2"),
      makeItem("b3", "info", "Info 3"),
    ];
    render(<BannerStack banners={banners} />);

    const toggle = screen.getByTestId("banner-stack-toggle");
    expect(toggle).toBeInTheDocument();
    expect(toggle).toHaveTextContent("Ver mais alertas (+1)");
  });

  it("does NOT show expand toggle when banners <= maxVisible", () => {
    const banners = [
      makeItem("b1", "info", "Info 1"),
      makeItem("b2", "info", "Info 2"),
    ];
    render(<BannerStack banners={banners} />);
    expect(screen.queryByTestId("banner-stack-toggle")).toBeNull();
  });

  it("expands overflow section on toggle click", () => {
    const banners = [
      makeItem("b1", "error", "Error msg"),
      makeItem("b2", "warning", "Warning msg"),
      makeItem("b3", "info", "Info msg"),
    ];
    render(<BannerStack banners={banners} />);

    const toggle = screen.getByTestId("banner-stack-toggle");
    expect(toggle).toHaveAttribute("aria-expanded", "false");

    fireEvent.click(toggle);

    expect(toggle).toHaveAttribute("aria-expanded", "true");
    const overflow = screen.getByTestId("banner-stack-overflow");
    expect(overflow).toHaveAttribute("aria-hidden", "false");
  });

  it("collapses overflow section on second toggle click", () => {
    const banners = [
      makeItem("b1", "error", "Error msg"),
      makeItem("b2", "warning", "Warning msg"),
      makeItem("b3", "info", "Info msg"),
    ];
    render(<BannerStack banners={banners} />);

    const toggle = screen.getByTestId("banner-stack-toggle");

    // Expand
    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute("aria-expanded", "true");

    // Collapse
    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    const overflow = screen.getByTestId("banner-stack-overflow");
    expect(overflow).toHaveAttribute("aria-hidden", "true");
  });

  it('toggle label changes to "Ocultar alertas" when expanded', () => {
    const banners = [
      makeItem("b1", "info", "Info 1"),
      makeItem("b2", "info", "Info 2"),
      makeItem("b3", "info", "Info 3"),
    ];
    render(<BannerStack banners={banners} />);

    const toggle = screen.getByTestId("banner-stack-toggle");
    fireEvent.click(toggle);
    expect(toggle).toHaveTextContent("Ocultar alertas");
  });
});

// ---------------------------------------------------------------------------
// Accessibility: aria-live
// ---------------------------------------------------------------------------

describe("BannerStack — aria-live on visible banners", () => {
  it("sets aria-live=assertive on error banners", () => {
    const banners = [makeItem("e1", "error", "Error msg")];
    render(<BannerStack banners={banners} />);

    const wrapper = screen.getByTestId("banner-item-e1");
    expect(wrapper).toHaveAttribute("aria-live", "assertive");
  });

  it("sets aria-live=polite on warning banners", () => {
    const banners = [makeItem("w1", "warning", "Warning msg")];
    render(<BannerStack banners={banners} />);

    const wrapper = screen.getByTestId("banner-item-w1");
    expect(wrapper).toHaveAttribute("aria-live", "polite");
  });

  it("sets aria-live=polite on info banners", () => {
    const banners = [makeItem("i1", "info", "Info msg")];
    render(<BannerStack banners={banners} />);

    const wrapper = screen.getByTestId("banner-item-i1");
    expect(wrapper).toHaveAttribute("aria-live", "polite");
  });

  it("sets aria-live=polite on success banners", () => {
    const banners = [makeItem("s1", "success", "Success msg")];
    render(<BannerStack banners={banners} />);

    const wrapper = screen.getByTestId("banner-item-s1");
    expect(wrapper).toHaveAttribute("aria-live", "polite");
  });

  it("visible banners have aria-live present", () => {
    const banners = [
      makeItem("e1", "error", "Error msg"),
      makeItem("w1", "warning", "Warning msg"),
    ];
    render(<BannerStack banners={banners} />);

    expect(screen.getByTestId("banner-item-e1")).toHaveAttribute("aria-live");
    expect(screen.getByTestId("banner-item-w1")).toHaveAttribute("aria-live");
  });
});

// ---------------------------------------------------------------------------
// Edge cases
// ---------------------------------------------------------------------------

describe("BannerStack — edge cases", () => {
  it("shows +N count matching the number of hidden banners", () => {
    const banners = [
      makeItem("b1", "error", "Error"),
      makeItem("b2", "warning", "Warning"),
      makeItem("b3", "info", "Info 1"),
      makeItem("b4", "info", "Info 2"),
      makeItem("b5", "success", "Success"),
    ];
    render(<BannerStack banners={banners} />);

    const toggle = screen.getByTestId("banner-stack-toggle");
    // 5 banners, maxVisible=2 → 3 hidden
    expect(toggle).toHaveTextContent("+3");
  });

  it("renders with custom className on container", () => {
    const banners = [makeItem("b1", "info", "Info")];
    render(<BannerStack banners={banners} className="mt-4 custom-class" />);
    const container = screen.getByTestId("banner-stack");
    expect(container).toHaveClass("custom-class");
  });

  it("renders with custom data-testid", () => {
    const banners = [makeItem("b1", "info", "Info")];
    render(<BannerStack banners={banners} data-testid="my-banner-stack" />);
    expect(screen.getByTestId("my-banner-stack")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// AC19: 5 simultaneous banners — only 2 visible in DOM
// ---------------------------------------------------------------------------

describe("BannerStack — AC19: 5 banners → max 2 visible", () => {
  it("renders exactly 2 banner-item elements in the visible slot when 5 are provided", () => {
    const banners = [
      makeItem("b1", "error", "Error 1"),
      makeItem("b2", "warning", "Warning 1"),
      makeItem("b3", "info", "Info 1"),
      makeItem("b4", "info", "Info 2"),
      makeItem("b5", "success", "Success 1"),
    ];
    render(<BannerStack banners={banners} />);

    // The top-level container's direct banner wrappers (the 2 visible ones)
    // are NOT inside the overflow div. Count banner-item-* that are NOT
    // children of banner-stack-overflow.
    const overflow = screen.getByTestId("banner-stack-overflow");
    const allItems = screen.getAllByTestId(/^banner-item-/);
    const visibleItems = allItems.filter((el) => !overflow.contains(el));

    expect(visibleItems).toHaveLength(2);
  });

  it("the 2 visible banners are the highest-severity ones (error + warning)", () => {
    const banners = [
      makeItem("b1", "error", "Error msg"),
      makeItem("b2", "warning", "Warning msg"),
      makeItem("b3", "info", "Info msg"),
      makeItem("b4", "info", "Info 2"),
      makeItem("b5", "success", "Success msg"),
    ];
    render(<BannerStack banners={banners} />);

    const overflow = screen.getByTestId("banner-stack-overflow");
    const allItems = screen.getAllByTestId(/^banner-item-/);
    const visibleItems = allItems.filter((el) => !overflow.contains(el));

    const visibleIds = visibleItems.map((el) =>
      el.getAttribute("data-testid")?.replace("banner-item-", "")
    );
    expect(visibleIds).toContain("b1");
    expect(visibleIds).toContain("b2");
  });

  it("overflow region contains the remaining 3 hidden banners", () => {
    const banners = [
      makeItem("b1", "error", "Error"),
      makeItem("b2", "warning", "Warning"),
      makeItem("b3", "info", "Info 1"),
      makeItem("b4", "info", "Info 2"),
      makeItem("b5", "success", "Success"),
    ];
    render(<BannerStack banners={banners} />);

    const overflow = screen.getByTestId("banner-stack-overflow");
    expect(overflow).toContainElement(screen.getByTestId("banner-item-b3"));
    expect(overflow).toContainElement(screen.getByTestId("banner-item-b4"));
    expect(overflow).toContainElement(screen.getByTestId("banner-item-b5"));
  });
});

// ---------------------------------------------------------------------------
// AC18: Auto-dismiss non-error banners after 5 seconds
// ---------------------------------------------------------------------------

describe("BannerStack — AC18: auto-dismiss non-error banners", () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    act(() => {
      jest.runOnlyPendingTimers();
    });
    jest.useRealTimers();
  });

  it("removes a non-error banner after autoDismissMs elapses", () => {
    const banners = [makeItem("i1", "info", "Info message")];
    render(<BannerStack banners={banners} autoDismissMs={5000} />);

    expect(screen.getByText("Info message")).toBeInTheDocument();

    act(() => {
      jest.advanceTimersByTime(5000);
    });

    expect(screen.queryByText("Info message")).not.toBeInTheDocument();
  });

  it("does NOT auto-dismiss error banners after 5 seconds", () => {
    const banners = [makeItem("e1", "error", "Error message")];
    render(<BannerStack banners={banners} autoDismissMs={5000} />);

    expect(screen.getByText("Error message")).toBeInTheDocument();

    act(() => {
      jest.advanceTimersByTime(10000);
    });

    expect(screen.getByText("Error message")).toBeInTheDocument();
  });

  it("auto-dismisses warning banners after the timeout", () => {
    const banners = [makeItem("w1", "warning", "Warning message")];
    render(<BannerStack banners={banners} autoDismissMs={5000} />);

    expect(screen.getByText("Warning message")).toBeInTheDocument();

    act(() => {
      jest.advanceTimersByTime(5000);
    });

    expect(screen.queryByText("Warning message")).not.toBeInTheDocument();
  });

  it("auto-dismisses success banners after the timeout", () => {
    const banners = [makeItem("s1", "success", "Success message")];
    render(<BannerStack banners={banners} autoDismissMs={5000} />);

    expect(screen.getByText("Success message")).toBeInTheDocument();

    act(() => {
      jest.advanceTimersByTime(5000);
    });

    expect(screen.queryByText("Success message")).not.toBeInTheDocument();
  });

  it("does NOT dismiss before the timeout elapses", () => {
    const banners = [makeItem("i1", "info", "Info message")];
    render(<BannerStack banners={banners} autoDismissMs={5000} />);

    act(() => {
      jest.advanceTimersByTime(4999);
    });

    expect(screen.getByText("Info message")).toBeInTheDocument();
  });

  it("keeps error banner while dismissing colocated non-error banners", () => {
    const banners = [
      makeItem("e1", "error", "Persistent error"),
      makeItem("i1", "info", "Transient info"),
    ];
    render(<BannerStack banners={banners} autoDismissMs={5000} />);

    act(() => {
      jest.advanceTimersByTime(5000);
    });

    expect(screen.getByText("Persistent error")).toBeInTheDocument();
    expect(screen.queryByText("Transient info")).not.toBeInTheDocument();
  });

  it("disables auto-dismiss when autoDismissMs=0", () => {
    const banners = [makeItem("i1", "info", "Info message")];
    render(<BannerStack banners={banners} autoDismissMs={0} />);

    act(() => {
      jest.advanceTimersByTime(60000);
    });

    expect(screen.getByText("Info message")).toBeInTheDocument();
  });

  it("respects custom autoDismissMs value", () => {
    const banners = [makeItem("i1", "info", "Info message")];
    render(<BannerStack banners={banners} autoDismissMs={2000} />);

    act(() => {
      jest.advanceTimersByTime(1999);
    });
    expect(screen.getByText("Info message")).toBeInTheDocument();

    act(() => {
      jest.advanceTimersByTime(1);
    });
    expect(screen.queryByText("Info message")).not.toBeInTheDocument();
  });
});
