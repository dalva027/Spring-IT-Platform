interface PaginationProps {
  page: number;
  totalPages: number;
  totalElements: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, totalPages, totalElements, onPageChange }: PaginationProps) {
  if (totalPages <= 1) {
    return <div className="pagination">{totalElements} ticket{totalElements === 1 ? '' : 's'}</div>;
  }
  return (
    <div className="pagination">
      <button type="button" disabled={page === 0} onClick={() => onPageChange(page - 1)}>
        ← Previous
      </button>
      <span>
        Page {page + 1} of {totalPages} ({totalElements} tickets)
      </span>
      <button type="button" disabled={page >= totalPages - 1} onClick={() => onPageChange(page + 1)}>
        Next →
      </button>
    </div>
  );
}
