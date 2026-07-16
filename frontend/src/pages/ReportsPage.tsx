import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchAgingReport, fetchSlaBreaches } from '../api/endpoints';
import type { AgingReportRow, TicketResponse } from '../api/types';
import { useUserDirectory } from '../auth/UserDirectoryContext';
import { PriorityBadge, StatusBadge, formatDateTime, formatDuration } from '../components/badges';
import { EmptyState, ErrorMessage, Spinner } from '../components/feedback';

export function ReportsPage() {
  const { displayName } = useUserDirectory();
  const [breaches, setBreaches] = useState<TicketResponse[] | null>(null);
  const [aging, setAging] = useState<AgingReportRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([fetchSlaBreaches(), fetchAgingReport()])
      .then(([breachData, agingData]) => {
        if (cancelled) return;
        setBreaches(breachData);
        setAging(agingData);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load reports');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) return <ErrorMessage message={error} />;
  if (!breaches || !aging) return <Spinner label="Loading reports…" />;

  return (
    <div>
      <h1>Reports</h1>

      <section className="card report-section">
        <h2>Ticket aging</h2>
        {aging.length === 0 ? (
          <EmptyState message="No active tickets." />
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Tickets</th>
                  <th>Oldest</th>
                </tr>
              </thead>
              <tbody>
                {aging.map((row) => (
                  <tr key={row.status}>
                    <td>
                      <StatusBadge status={row.status} />
                    </td>
                    <td>{row.ticketCount}</td>
                    <td>{formatDuration(row.oldestAgeHours * 60 * 60 * 1000)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="card report-section">
        <h2>
          SLA breaches{' '}
          {breaches.length > 0 && <span className="badge priority-critical">{breaches.length}</span>}
        </h2>
        {breaches.length === 0 ? (
          <EmptyState message="No active tickets past their SLA deadline. 🎉" />
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Due</th>
                  <th>Overdue by</th>
                  <th>Assignee</th>
                </tr>
              </thead>
              <tbody>
                {breaches.map((ticket) => (
                  <tr key={ticket.id}>
                    <td>{ticket.id}</td>
                    <td className="cell-title">
                      <Link to={`/tickets/${ticket.id}`}>{ticket.title}</Link>
                    </td>
                    <td>
                      <StatusBadge status={ticket.status} />
                    </td>
                    <td>
                      <PriorityBadge priority={ticket.priority} />
                    </td>
                    <td>{formatDateTime(ticket.slaDueAt)}</td>
                    <td className="sla sla-breached">
                      {formatDuration(Date.now() - new Date(ticket.slaDueAt).getTime())}
                    </td>
                    <td>{displayName(ticket.assigneeId)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

    </div>
  );
}
