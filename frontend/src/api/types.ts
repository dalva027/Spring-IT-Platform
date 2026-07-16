export type Role = 'REQUESTER' | 'AGENT' | 'ADMIN';

export type TicketStatus = 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';

export type TicketPriority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export interface UserResponse {
  id: number;
  email: string;
  fullName: string;
  role: Role;
  createdAt: string;
}

export interface AuthResponse {
  token: string;
  user: UserResponse;
}

export interface TicketResponse {
  id: number;
  title: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  requesterId: number;
  assigneeId: number | null;
  createdAt: string;
  updatedAt: string;
  slaDueAt: string;
}

export interface CommentResponse {
  id: number;
  ticketId: number;
  authorId: number;
  body: string;
  createdAt: string;
}

export interface StatusHistoryResponse {
  id: number;
  fromStatus: TicketStatus | null;
  toStatus: TicketStatus;
  changedBy: number;
  changedAt: string;
}

export interface AgingReportRow {
  status: TicketStatus;
  ticketCount: number;
  oldestAgeHours: number;
}

/** Spring Data PagedModel envelope: metadata is nested under `page`. */
export interface Page<T> {
  content: T[];
  page: {
    size: number;
    number: number;
    totalElements: number;
    totalPages: number;
  };
}

/** Mirrors TicketStatus.ALLOWED_TRANSITIONS in ticket-service. */
export const ALLOWED_TRANSITIONS: Record<TicketStatus, TicketStatus[]> = {
  OPEN: ['IN_PROGRESS', 'CLOSED'],
  IN_PROGRESS: ['OPEN', 'RESOLVED'],
  RESOLVED: ['OPEN', 'CLOSED'],
  CLOSED: [],
};

export const TICKET_STATUSES: TicketStatus[] = ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'];
export const TICKET_PRIORITIES: TicketPriority[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

/** SLA window in hours per priority (informational; the backend derives slaDueAt). */
export const SLA_HOURS: Record<TicketPriority, number> = {
  CRITICAL: 2,
  HIGH: 8,
  MEDIUM: 24,
  LOW: 72,
};

export function statusLabel(status: TicketStatus): string {
  return status === 'IN_PROGRESS' ? 'In progress' : status.charAt(0) + status.slice(1).toLowerCase();
}
