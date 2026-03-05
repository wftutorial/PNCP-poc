"use client";

import { Pagination } from "../../../../components/ui/Pagination";

interface ResultsPaginationProps {
  totalItems: number;
  currentPage: number;
  pageSize: 10 | 20 | 50;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: 10 | 20 | 50) => void;
  scrollTargetId?: string;
}

/**
 * TD-007 AC5: ResultsPagination — pagination controls with page numbers and navigation.
 * Wraps the Pagination component with SearchResults-specific defaults.
 */
export function ResultsPagination({
  totalItems,
  currentPage,
  pageSize,
  onPageChange,
  onPageSizeChange,
  scrollTargetId = "results-top",
}: ResultsPaginationProps) {
  if (totalItems <= 0) return null;

  return (
    <Pagination
      totalItems={totalItems}
      currentPage={currentPage}
      pageSize={pageSize}
      onPageChange={onPageChange}
      onPageSizeChange={onPageSizeChange}
      scrollTargetId={scrollTargetId}
    />
  );
}
