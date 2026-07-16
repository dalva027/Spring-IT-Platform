import type { TicketPriority, TicketStatus } from '../api/types';
import { statusLabel } from '../api/types';

export function StatusBadge({ status }: { status: TicketStatus }) {
  return <span className={`badge status-${status.toLowerCase()}`}>{statusLabel(status)}</span>;
}

export function PriorityBadge({ priority }: { priority: TicketPriority }) {
  return <span className={`badge priority-${priority.toLowerCase()}`}>{priority}</span>;
}

export function RoleBadge({ role }: { role: string }) {
  return <span className={`badge role-${role.toLowerCase()}`}>{role}</span>;
}

/** Time remaining until (or elapsed since) the SLA deadline, colored by urgency. */
export function SlaIndicator({ slaDueAt, status }: { slaDueAt: string; status: TicketStatus }) {
  if (status === 'RESOLVED' || status === 'CLOSED') {
    return <span className="sla sla-done">—</span>;
  }
  const remainingMs = new Date(slaDueAt).getTime() - Date.now();
  if (remainingMs < 0) {
    return <span className="sla sla-breached">Breached {formatDuration(-remainingMs)} ago</span>;
  }
  const cls = remainingMs < 2 * 60 * 60 * 1000 ? 'sla-warning' : 'sla-ok';
  return <span className={`sla ${cls}`}>{formatDuration(remainingMs)} left</span>;
}

export function formatDuration(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  if (hours < 48) return `${hours}h ${minutes % 60}m`;
  return `${Math.floor(hours / 24)}d ${hours % 24}h`;
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
