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

// ---- ai-service ----

export type AiCategory = 'IT' | 'HR' | 'FINANCE' | 'NETWORKING' | 'SECURITY';
export type AiOutcome = 'SOLVED' | 'NEEDS_TECHNICIAN' | 'EMERGENCY';
export type AnalysisStatus = 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface AiClassification {
  category: AiCategory;
  suggested_priority: TicketPriority;
  confidence: number;
  rationale: string;
}

export interface AiDocHit {
  title: string;
  path: string;
  category: string;
  heading: string;
  snippet: string;
  score: number;
}

export interface AiTicketHit {
  ticketId: number;
  title: string;
  snippet: string;
  status: TicketStatus;
  score: number;
}

export interface AiTroubleshooting {
  steps: string[];
  self_serviceable: boolean;
  confidence: number;
}

export interface AiEscalation {
  outcome: AiOutcome;
  ticket_priority: TicketPriority;
  assignment_hint: string;
}

export interface AiExternalIssue {
  provider: string;
  key: string;
  url: string;
  summary: string;
}

export interface AiSummaries {
  ticket_comment: string;
  manager_summary: string;
  resolution_notes: string;
}

export interface AnalysisResponse {
  requestId: string;
  channel: 'assistant' | 'ticket_event';
  status: AnalysisStatus;
  issueText: string;
  userId: number;
  ticketId: number | null;
  classification: AiClassification | null;
  docHits: AiDocHit[] | null;
  ticketHits: AiTicketHit[] | null;
  troubleshooting: AiTroubleshooting | null;
  escalation: AiEscalation | null;
  externalIssues: AiExternalIssue[] | null;
  notifications: { channel: string; status: string }[] | null;
  summaries: AiSummaries | null;
  errors: string[] | null;
  createdAt: string | null;
  updatedAt: string | null;
}

/** Pipeline nodes in visual order, with UI labels. */
export const AI_PIPELINE_STEPS: { node: string; label: string }[] = [
  { node: 'classify', label: 'Classify the issue' },
  { node: 'retrieve_docs', label: 'Search company docs' },
  { node: 'retrieve_tickets', label: 'Search past tickets' },
  { node: 'troubleshoot', label: 'Draft troubleshooting steps' },
  { node: 'escalate', label: 'Decide on escalation' },
  { node: 'api_agent', label: 'Act on the ticket system' },
  { node: 'summarize', label: 'Write summaries' },
];

export function statusLabel(status: TicketStatus): string {
  return status === 'IN_PROGRESS' ? 'In progress' : status.charAt(0) + status.slice(1).toLowerCase();
}
