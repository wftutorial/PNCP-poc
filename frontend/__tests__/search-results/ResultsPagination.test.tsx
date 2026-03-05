/**
 * TD-007 AC5: ResultsPagination sub-component tests.
 * Tests rendering with correct props, null return for zero items,
 * and default scrollTargetId behavior.
 */

import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

// --- Mocks ---

jest.mock("../../components/ui/Pagination", () => ({
  Pagination: function Mock({
    totalItems,
    currentPage,
    pageSize,
    onPageChange,
    onPageSizeChange,
    scrollTargetId,
  }: any) {
    return (
      <div
        data-testid="pagination-component"
        data-total={totalItems}
        data-page={currentPage}
        data-size={pageSize}
        data-scroll-target={scrollTargetId}
      >
        <button
          data-testid="page-change-btn"
          onClick={() => onPageChange(2)}
        >
          Go to page 2
        </button>
        <button
          data-testid="page-size-change-btn"
          onClick={() => onPageSizeChange(20)}
        >
          Size 20
        </button>
      </div>
    );
  },
}));

import { ResultsPagination } from "../../app/buscar/components/search-results/ResultsPagination";

describe("ResultsPagination", () => {
  const defaultProps = {
    totalItems: 50,
    currentPage: 1,
    pageSize: 10 as const,
    onPageChange: jest.fn(),
    onPageSizeChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  // --- Basic rendering ---

  it("renders Pagination component when totalItems > 0", () => {
    render(<ResultsPagination {...defaultProps} />);
    expect(screen.getByTestId("pagination-component")).toBeInTheDocument();
  });

  it("passes totalItems to Pagination component", () => {
    render(<ResultsPagination {...defaultProps} totalItems={100} />);
    expect(screen.getByTestId("pagination-component")).toHaveAttribute(
      "data-total",
      "100"
    );
  });

  it("passes currentPage to Pagination component", () => {
    render(<ResultsPagination {...defaultProps} currentPage={3} />);
    expect(screen.getByTestId("pagination-component")).toHaveAttribute(
      "data-page",
      "3"
    );
  });

  it("passes pageSize to Pagination component", () => {
    render(<ResultsPagination {...defaultProps} pageSize={20} />);
    expect(screen.getByTestId("pagination-component")).toHaveAttribute(
      "data-size",
      "20"
    );
  });

  // --- Null return for zero/negative items ---

  it("returns null when totalItems is 0", () => {
    const { container } = render(
      <ResultsPagination {...defaultProps} totalItems={0} />
    );
    expect(container.firstChild).toBeNull();
  });

  it("returns null when totalItems is negative", () => {
    const { container } = render(
      <ResultsPagination {...defaultProps} totalItems={-1} />
    );
    expect(container.firstChild).toBeNull();
  });

  // --- Default scrollTargetId ---

  it("uses default scrollTargetId 'results-top' when not provided", () => {
    render(<ResultsPagination {...defaultProps} />);
    expect(screen.getByTestId("pagination-component")).toHaveAttribute(
      "data-scroll-target",
      "results-top"
    );
  });

  it("uses custom scrollTargetId when provided", () => {
    render(
      <ResultsPagination {...defaultProps} scrollTargetId="custom-scroll-id" />
    );
    expect(screen.getByTestId("pagination-component")).toHaveAttribute(
      "data-scroll-target",
      "custom-scroll-id"
    );
  });

  // --- Callbacks ---

  it("calls onPageChange when Pagination triggers page change", () => {
    const onPageChange = jest.fn();
    render(
      <ResultsPagination {...defaultProps} onPageChange={onPageChange} />
    );
    screen.getByTestId("page-change-btn").click();
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it("calls onPageSizeChange when Pagination triggers size change", () => {
    const onPageSizeChange = jest.fn();
    render(
      <ResultsPagination
        {...defaultProps}
        onPageSizeChange={onPageSizeChange}
      />
    );
    screen.getByTestId("page-size-change-btn").click();
    expect(onPageSizeChange).toHaveBeenCalledWith(20);
  });

  // --- Different page sizes ---

  it("works with pageSize=20", () => {
    render(<ResultsPagination {...defaultProps} pageSize={20} totalItems={200} />);
    const comp = screen.getByTestId("pagination-component");
    expect(comp).toHaveAttribute("data-size", "20");
    expect(comp).toHaveAttribute("data-total", "200");
  });

  it("works with pageSize=50", () => {
    render(<ResultsPagination {...defaultProps} pageSize={50} totalItems={500} />);
    expect(screen.getByTestId("pagination-component")).toHaveAttribute(
      "data-size",
      "50"
    );
  });
});
