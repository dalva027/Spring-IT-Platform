import { useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { searchTickets } from '../api/endpoints';
import type { Page, TicketPriority, TicketResponse, TicketStatus } from '../api/types';
import { TICKET_PRIORITIES, TICKET_STATUSES, statusLabel } from '../api/types';
import { useAuth } from '../auth/AuthContext';
import { useUserDirectory } from '../auth/UserDirectoryContext';
import { PriorityBadge, SlaIndicator, StatusBadge, formatDateTime } from '../components/badges';
import { EmptyState, ErrorMessage, Spinner } from '../components/feedback';
import { Pagination } from '../components/Pagination';

export function TicketsPage() {
  const { user, isAgent } = useAuth();
  const { displayName } = useUserDirectory();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [result, setResult] = useState<Page<TicketResponse> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const status = (searchParams.get('status') as TicketStatus | null) ?? undefined;
  const priority = (searchParams.get('priority') as TicketPriority | null) ?? undefined;
  const mine = searchParams.get('mine') === '1';
  const unassigned = searchParams.get('unassigned') === '1';
  const page = Number(searchParams.get('page') ?? '0');

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    searchTickets({
      status,
      priority,
      // "Unassigned" and "assigned to me" are mutually exclusive queues.
      assigneeId: mine && !unassigned && user ? user.id : undefined,
      unassigned,
      page,
      size: 20,
      sort: 'createdAt,desc',
    })
      .then((data) => {
        if (!cancelled) setResult(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load tickets');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [status, priority, mine, unassigned, page, user]);

  function toggleQueue(key: 'mine' | 'unassigned', on: boolean) {
    const next = new URLSearchParams(searchParams);
    // The two queue filters are mutually exclusive.
    next.delete('mine');
    next.delete('unassigned');
    if (on) next.set(key, '1');
    next.delete('page');
    setSearchParams(next);
  }

  function updateParam(key: string, value: string) {
    const next = new URLSearchParams(searchParams);
    if (value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
    next.delete('page');
    setSearchParams(next);
  }

  function goToPage(nextPage: number) {
    const next = new URLSearchParams(searchParams);
    if (nextPage > 0) {
      next.set('page', String(nextPage));
    } else {
      next.delete('page');
    }
    setSearchParams(next);
  }

  return (
    <div>
      <div className="page-header">
        <h1>{mine ? 'My Tickets' : unassigned ? 'Unassigned' : 'Tickets'}</h1>
        <Link to="/tickets/new" className="btn-primary btn-accent">
          + New ticket
        </Link>
      </div>

      <div className="filters">
        <label>
          Status
          <select value={status ?? ''} onChange={(e) => updateParam('status', e.target.value)}>
            <option value="">All</option>
            {TICKET_STATUSES.map((s) => (
              <option key={s} value={s}>
                {statusLabel(s)}
              </option>
            ))}
          </select>
        </label>
        <label>
          Priority
          <select value={priority ?? ''} onChange={(e) => updateParam('priority', e.target.value)}>
            <option value="">All</option>
            {TICKET_PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        {isAgent && (
          <>
            <label className="filter-checkbox">
              <input
                type="checkbox"
                checked={mine}
                onChange={(e) => toggleQueue('mine', e.target.checked)}
              />
              Assigned to me
            </label>
            <label className="filter-checkbox">
              <input
                type="checkbox"
                checked={unassigned}
                onChange={(e) => toggleQueue('unassigned', e.target.checked)}
              />
              Unassigned
            </label>
          </>
        )}
      </div>

      {loading && <Spinner label="Loading tickets…" />}
      {error && <ErrorMessage message={error} />}
      {!loading && !error && result && result.content.length === 0 && (
        <EmptyState
          message={
            unassigned
              ? 'No unassigned tickets — every ticket has an owner.'
              : 'No tickets match these filters.'
          }
        />
      )}

      {!loading && !error && result && result.content.length > 0 && (
        <>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>SLA</th>
                  {isAgent && <th>Requester</th>}
                  <th>Assignee</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {result.content.map((ticket) => (
                  <tr
                    key={ticket.id}
                    className="row-link"
                    onClick={() => navigate(`/tickets/${ticket.id}`)}
                  >
                    <td>{ticket.id}</td>
                    <td className="cell-title">
                      <Link to={`/tickets/${ticket.id}`} onClick={(e) => e.stopPropagation()}>
                        {ticket.title}
                      </Link>
                    </td>
                    <td>
                      <StatusBadge status={ticket.status} />
                    </td>
                    <td>
                      <PriorityBadge priority={ticket.priority} />
                    </td>
                    <td>
                      <SlaIndicator slaDueAt={ticket.slaDueAt} status={ticket.status} />
                    </td>
                    {isAgent && <td>{displayName(ticket.requesterId)}</td>}
                    <td>{displayName(ticket.assigneeId)}</td>
                    <td>{formatDateTime(ticket.createdAt)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination
            page={result.page.number}
            totalPages={result.page.totalPages}
            totalElements={result.page.totalElements}
            onPageChange={goToPage}
          />
        </>
      )}
    </div>
  );
}
