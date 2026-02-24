/**
 * GTM-POLISH-002: Pipeline Mobile Tabs
 *
 * T2: Pipeline tabs render in mobile viewport — all 5 stage tabs appear
 * T3: "Mover para..." dropdown works as alternative to drag-and-drop
 * T4: Badge count on each tab reflects correct item count per stage
 */

import React from "react";
import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import "@testing-library/jest-dom";

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

jest.mock("sonner", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
  },
}));

// ---------------------------------------------------------------------------
// Imports (after mocks)
// ---------------------------------------------------------------------------

import { PipelineMobileTabs } from "../../app/pipeline/PipelineMobileTabs";
import type { PipelineItem, PipelineStage } from "../../app/pipeline/types";
import { STAGES_ORDER, STAGE_CONFIG } from "../../app/pipeline/types";
import { toast } from "sonner";

// ---------------------------------------------------------------------------
// Test data helpers
// ---------------------------------------------------------------------------

let _idCounter = 0;

function makeItem(overrides: Partial<PipelineItem> = {}): PipelineItem {
  _idCounter += 1;
  return {
    id: `item-${_idCounter}`,
    user_id: "user-1",
    pncp_id: `pncp-${_idCounter}`,
    objeto: `Licitação objeto ${_idCounter}`,
    orgao: "Prefeitura Municipal",
    uf: "SP",
    valor_estimado: 100_000,
    data_encerramento: "2026-04-01T23:59:59",
    link_pncp: `https://pncp.gov.br/app/editais/${_idCounter}`,
    stage: "descoberta",
    notes: null,
    created_at: "2026-02-24T08:00:00",
    updated_at: "2026-02-24T08:00:00",
    ...overrides,
  };
}

/** Build a set of items spread across stages */
function makeMixedItems(): PipelineItem[] {
  _idCounter = 0;
  return [
    makeItem({ stage: "descoberta" }),
    makeItem({ stage: "descoberta" }),
    makeItem({ stage: "descoberta" }),
    makeItem({ stage: "analise" }),
    makeItem({ stage: "analise" }),
    makeItem({ stage: "preparando" }),
    makeItem({ stage: "enviada" }),
    makeItem({ stage: "enviada" }),
    // "resultado" intentionally has 0 items
  ];
}

// ---------------------------------------------------------------------------
// T2 — Pipeline tabs render in mobile viewport
// ---------------------------------------------------------------------------

describe("GTM-POLISH-002 T2: pipeline tabs render in mobile viewport", () => {
  const mockOnUpdateItem = jest.fn().mockResolvedValue(undefined);
  const mockOnRemoveItem = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    _idCounter = 0;
  });

  it("renders the pipeline-mobile-tabs wrapper", () => {
    render(
      <PipelineMobileTabs
        items={[]}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    expect(screen.getByTestId("pipeline-mobile-tabs")).toBeInTheDocument();
  });

  it("renders exactly 5 stage tabs", () => {
    render(
      <PipelineMobileTabs
        items={[]}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    const tabs = screen.getAllByRole("tab");
    expect(tabs).toHaveLength(5);
  });

  it.each(STAGES_ORDER)("renders tab for stage '%s'", (stage) => {
    render(
      <PipelineMobileTabs
        items={[]}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    expect(screen.getByTestId(`pipeline-tab-${stage}`)).toBeInTheDocument();
  });

  it("tab labels match STAGE_CONFIG", () => {
    render(
      <PipelineMobileTabs
        items={[]}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    for (const stage of STAGES_ORDER) {
      expect(screen.getByText(STAGE_CONFIG[stage].label)).toBeInTheDocument();
    }
  });

  it("defaults to 'descoberta' as active tab (aria-selected=true)", () => {
    render(
      <PipelineMobileTabs
        items={[]}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    const descobertaTab = screen.getByTestId("pipeline-tab-descoberta");
    expect(descobertaTab).toHaveAttribute("aria-selected", "true");
  });

  it("non-active tabs have aria-selected=false", () => {
    render(
      <PipelineMobileTabs
        items={[]}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    for (const stage of STAGES_ORDER.filter((s) => s !== "descoberta")) {
      expect(screen.getByTestId(`pipeline-tab-${stage}`)).toHaveAttribute("aria-selected", "false");
    }
  });

  it("clicking a tab changes the active tab", () => {
    render(
      <PipelineMobileTabs
        items={[]}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    const analiseTab = screen.getByTestId("pipeline-tab-analise");
    fireEvent.click(analiseTab);

    expect(analiseTab).toHaveAttribute("aria-selected", "true");
    expect(screen.getByTestId("pipeline-tab-descoberta")).toHaveAttribute("aria-selected", "false");
  });

  it("shows empty state message when active tab has no items", () => {
    render(
      <PipelineMobileTabs
        items={[]}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    // descoberta has 0 items — expect empty message
    expect(screen.getByText(/Nenhum item em Descoberta/i)).toBeInTheDocument();
  });

  it("shows pipeline cards when active tab has items", () => {
    const items = [makeItem({ stage: "descoberta" }), makeItem({ stage: "descoberta" })];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    const cards = screen.getAllByTestId("pipeline-mobile-card");
    expect(cards).toHaveLength(2);
  });

  it("cards from non-active tabs are not rendered", () => {
    const items = [
      makeItem({ stage: "descoberta" }),
      makeItem({ stage: "analise" }),   // not visible by default
    ];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    // Only the descoberta card should be visible
    const cards = screen.getAllByTestId("pipeline-mobile-card");
    expect(cards).toHaveLength(1);
  });

  it("switching tabs shows the correct cards", () => {
    const items = [
      makeItem({ stage: "descoberta", objeto: "Descoberta Item" }),
      makeItem({ stage: "analise", objeto: "Analise Item" }),
    ];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    // Initially on descoberta
    expect(screen.getByText("Descoberta Item")).toBeInTheDocument();
    expect(screen.queryByText("Analise Item")).not.toBeInTheDocument();

    // Switch to analise
    fireEvent.click(screen.getByTestId("pipeline-tab-analise"));

    expect(screen.queryByText("Descoberta Item")).not.toBeInTheDocument();
    expect(screen.getByText("Analise Item")).toBeInTheDocument();
  });

  it("renders card with item objeto as title", () => {
    const items = [makeItem({ stage: "descoberta", objeto: "Compra de mobiliário escolar" })];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    expect(screen.getByText("Compra de mobiliário escolar")).toBeInTheDocument();
  });

  it("renders card with UF badge", () => {
    const items = [makeItem({ stage: "descoberta", uf: "RJ" })];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    expect(screen.getByText("RJ")).toBeInTheDocument();
  });

  it("renders tabpanel container", () => {
    render(
      <PipelineMobileTabs
        items={[]}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    expect(screen.getByRole("tabpanel")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// T3 — "Mover para..." works as alternative to drag-and-drop
// ---------------------------------------------------------------------------

describe("GTM-POLISH-002 T3: Mover para... button replaces drag-and-drop", () => {
  const mockOnUpdateItem = jest.fn().mockResolvedValue(undefined);
  const mockOnRemoveItem = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    _idCounter = 0;
    (toast.success as jest.Mock).mockClear();
    (toast.error as jest.Mock).mockClear();
  });

  it("renders a move-to-button on each card", () => {
    const items = [makeItem({ stage: "descoberta" }), makeItem({ stage: "descoberta" })];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    const moveButtons = screen.getAllByTestId("move-to-button");
    expect(moveButtons).toHaveLength(2);
  });

  it("move-to dropdown is hidden by default", () => {
    const items = [makeItem({ stage: "descoberta" })];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    // Dropdown options should not be visible before clicking
    for (const stage of STAGES_ORDER.filter((s) => s !== "descoberta")) {
      expect(screen.queryByTestId(`move-to-${stage}`)).not.toBeInTheDocument();
    }
  });

  it("clicking move-to-button opens the dropdown", () => {
    const items = [makeItem({ stage: "descoberta" })];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    fireEvent.click(screen.getByTestId("move-to-button"));

    // Other stages should now be visible as options
    for (const stage of STAGES_ORDER.filter((s) => s !== "descoberta")) {
      expect(screen.getByTestId(`move-to-${stage}`)).toBeInTheDocument();
    }
  });

  it("dropdown does NOT show the current stage as a move target", () => {
    const items = [makeItem({ stage: "descoberta" })];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    fireEvent.click(screen.getByTestId("move-to-button"));

    // The current stage should NOT appear in move targets
    expect(screen.queryByTestId("move-to-descoberta")).not.toBeInTheDocument();
  });

  it("clicking a stage option calls onUpdateItem with correct stage", async () => {
    const items = [makeItem({ stage: "descoberta", id: "item-move-1" })];
    _idCounter = 0; // reset after makeItem

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    fireEvent.click(screen.getByTestId("move-to-button"));
    fireEvent.click(screen.getByTestId("move-to-analise"));

    await waitFor(() => {
      expect(mockOnUpdateItem).toHaveBeenCalledWith("item-move-1", { stage: "analise" });
    });
  });

  it("shows success toast after moving item", async () => {
    const items = [makeItem({ stage: "descoberta", id: "item-toast-1" })];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    fireEvent.click(screen.getByTestId("move-to-button"));
    fireEvent.click(screen.getByTestId("move-to-preparando"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        expect.stringContaining(STAGE_CONFIG["preparando"].label)
      );
    });
  });

  it("shows error toast when onUpdateItem rejects", async () => {
    const failingUpdate = jest.fn().mockRejectedValue(new Error("Network error"));
    const items = [makeItem({ stage: "descoberta" })];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={failingUpdate}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    fireEvent.click(screen.getByTestId("move-to-button"));
    fireEvent.click(screen.getByTestId("move-to-enviada"));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Erro ao mover item");
    });
  });

  it("dropdown closes after selecting a stage", async () => {
    const items = [makeItem({ stage: "descoberta" })];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    fireEvent.click(screen.getByTestId("move-to-button"));
    expect(screen.getByTestId("move-to-analise")).toBeInTheDocument();

    fireEvent.click(screen.getByTestId("move-to-analise"));

    // After click the dropdown should be gone (movingItemId reset to null)
    await waitFor(() => {
      expect(screen.queryByTestId("move-to-analise")).not.toBeInTheDocument();
    });
  });

  it("clicking move-to-button again closes an already-open dropdown (toggle)", () => {
    const items = [makeItem({ stage: "descoberta" })];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    const moveBtn = screen.getByTestId("move-to-button");

    // Open
    fireEvent.click(moveBtn);
    expect(screen.getByTestId("move-to-analise")).toBeInTheDocument();

    // Toggle closed
    fireEvent.click(moveBtn);
    expect(screen.queryByTestId("move-to-analise")).not.toBeInTheDocument();
  });

  it("clicking Remover calls onRemoveItem with item id", () => {
    const items = [makeItem({ stage: "descoberta", id: "item-remove-1" })];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    fireEvent.click(screen.getByText("Remover"));
    expect(mockOnRemoveItem).toHaveBeenCalledWith("item-remove-1");
  });

  it("only one dropdown open at a time — opening a second closes the first", () => {
    const items = [
      makeItem({ stage: "descoberta" }),
      makeItem({ stage: "descoberta" }),
    ];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    const moveButtons = screen.getAllByTestId("move-to-button");

    // Open first
    fireEvent.click(moveButtons[0]);
    expect(screen.getAllByTestId("move-to-analise")).toHaveLength(1);

    // Open second — movingItemId changes, first closes
    fireEvent.click(moveButtons[1]);
    // Still 1 dropdown shown (the second one), not 2
    expect(screen.getAllByTestId("move-to-analise")).toHaveLength(1);
  });
});

// ---------------------------------------------------------------------------
// T4 — Badge count correct on each tab
// ---------------------------------------------------------------------------

describe("GTM-POLISH-002 T4: badge count on each tab", () => {
  const mockOnUpdateItem = jest.fn().mockResolvedValue(undefined);
  const mockOnRemoveItem = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    _idCounter = 0;
  });

  it("shows correct count for each stage (mixed items)", () => {
    const items = makeMixedItems();
    // descoberta: 3, analise: 2, preparando: 1, enviada: 2, resultado: 0

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    expect(screen.getByTestId("pipeline-tab-count-descoberta")).toHaveTextContent("3");
    expect(screen.getByTestId("pipeline-tab-count-analise")).toHaveTextContent("2");
    expect(screen.getByTestId("pipeline-tab-count-preparando")).toHaveTextContent("1");
    expect(screen.getByTestId("pipeline-tab-count-enviada")).toHaveTextContent("2");
    expect(screen.getByTestId("pipeline-tab-count-resultado")).toHaveTextContent("0");
  });

  it("shows 0 on all badges when items list is empty", () => {
    render(
      <PipelineMobileTabs
        items={[]}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    for (const stage of STAGES_ORDER) {
      expect(screen.getByTestId(`pipeline-tab-count-${stage}`)).toHaveTextContent("0");
    }
  });

  it("badge count updates reactively when items change", () => {
    const items = [makeItem({ stage: "descoberta" })];

    const { rerender } = render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    expect(screen.getByTestId("pipeline-tab-count-descoberta")).toHaveTextContent("1");

    // Add another item
    const moreItems = [
      ...items,
      makeItem({ stage: "descoberta" }),
      makeItem({ stage: "descoberta" }),
    ];

    rerender(
      <PipelineMobileTabs
        items={moreItems}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    expect(screen.getByTestId("pipeline-tab-count-descoberta")).toHaveTextContent("3");
  });

  it("badge count is independent per stage — one stage does not affect another", () => {
    const items = [
      makeItem({ stage: "descoberta" }),
      makeItem({ stage: "descoberta" }),
      makeItem({ stage: "resultado" }),
      makeItem({ stage: "resultado" }),
      makeItem({ stage: "resultado" }),
    ];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    expect(screen.getByTestId("pipeline-tab-count-descoberta")).toHaveTextContent("2");
    expect(screen.getByTestId("pipeline-tab-count-analise")).toHaveTextContent("0");
    expect(screen.getByTestId("pipeline-tab-count-resultado")).toHaveTextContent("3");
  });

  it("badge counts all five stages at once — no stage is missing a badge", () => {
    render(
      <PipelineMobileTabs
        items={[]}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    for (const stage of STAGES_ORDER) {
      const badge = screen.getByTestId(`pipeline-tab-count-${stage}`);
      expect(badge).toBeInTheDocument();
    }
  });

  it("tab with highest count still shows correct badge after switching active tab", () => {
    const items = Array.from({ length: 7 }, () => makeItem({ stage: "preparando" }));

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    // Switch active tab to preparando
    fireEvent.click(screen.getByTestId("pipeline-tab-preparando"));

    // Badge count should still be 7 (counts all items, not just displayed)
    expect(screen.getByTestId("pipeline-tab-count-preparando")).toHaveTextContent("7");
  });

  it("card count in tabpanel matches the tab badge count for active tab", () => {
    const items = [
      makeItem({ stage: "analise" }),
      makeItem({ stage: "analise" }),
      makeItem({ stage: "analise" }),
    ];

    render(
      <PipelineMobileTabs
        items={items}
        onUpdateItem={mockOnUpdateItem}
        onRemoveItem={mockOnRemoveItem}
      />
    );

    // Switch to analise
    fireEvent.click(screen.getByTestId("pipeline-tab-analise"));

    const badge = screen.getByTestId("pipeline-tab-count-analise");
    const cards = screen.getAllByTestId("pipeline-mobile-card");

    expect(badge).toHaveTextContent("3");
    expect(cards).toHaveLength(3);
  });
});
