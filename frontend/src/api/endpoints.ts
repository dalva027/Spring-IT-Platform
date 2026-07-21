import { aiApi, authApi, ticketApi } from './client';
import type {
  AgingReportRow,
  AnalysisResponse,
  AuthResponse,
  CommentResponse,
  Contact,
  MessageBox,
  MessageResponse,
  Page,
  Role,
  StatusHistoryResponse,
  TicketPriority,
  TicketResponse,
  TicketStatus,
  UserResponse,
} from './types';

// ---- auth-service ----

export function login(email: string, password: string): Promise<AuthResponse> {
  return authApi.post<AuthResponse>('/api/auth/login', { email, password });
}

export function register(email: string, password: string, fullName: string): Promise<AuthResponse> {
  return authApi.post<AuthResponse>('/api/auth/register', { email, password, fullName });
}

export function fetchMe(): Promise<UserResponse> {
  return authApi.get<UserResponse>('/api/users/me');
}

export function fetchUsers(): Promise<UserResponse[]> {
  return authApi.get<UserResponse[]>('/api/users');
}

/** Directory usable by any authenticated user (requesters included) for the message recipient picker. */
export function fetchContacts(): Promise<Contact[]> {
  return authApi.get<Contact[]>('/api/users/contacts');
}

export function updateUserRole(userId: number, role: Role): Promise<UserResponse> {
  return authApi.patch<UserResponse>(`/api/users/${userId}/role`, { role });
}

// ---- ticket-service ----

export interface TicketSearchParams {
  status?: TicketStatus;
  priority?: TicketPriority;
  assigneeId?: number;
  /** Restrict to tickets with no assignee — the inbox / triage queue. */
  unassigned?: boolean;
  page?: number;
  size?: number;
  sort?: string;
}

export function searchTickets(params: TicketSearchParams): Promise<Page<TicketResponse>> {
  const query = new URLSearchParams();
  if (params.status) query.set('status', params.status);
  if (params.priority) query.set('priority', params.priority);
  if (params.assigneeId !== undefined) query.set('assigneeId', String(params.assigneeId));
  if (params.unassigned) query.set('unassigned', 'true');
  if (params.page !== undefined) query.set('page', String(params.page));
  if (params.size !== undefined) query.set('size', String(params.size));
  if (params.sort) query.set('sort', params.sort);
  const qs = query.toString();
  return ticketApi.get<Page<TicketResponse>>(`/api/tickets${qs ? `?${qs}` : ''}`);
}

export function fetchTicket(id: number): Promise<TicketResponse> {
  return ticketApi.get<TicketResponse>(`/api/tickets/${id}`);
}

export function createTicket(
  title: string,
  description: string,
  priority: TicketPriority,
): Promise<TicketResponse> {
  return ticketApi.post<TicketResponse>('/api/tickets', { title, description, priority });
}

export function updateTicketStatus(id: number, status: TicketStatus): Promise<TicketResponse> {
  return ticketApi.patch<TicketResponse>(`/api/tickets/${id}/status`, { status });
}

export function updateTicketAssignee(id: number, assigneeId: number): Promise<TicketResponse> {
  return ticketApi.patch<TicketResponse>(`/api/tickets/${id}/assignee`, { assigneeId });
}

export function fetchComments(ticketId: number): Promise<CommentResponse[]> {
  return ticketApi.get<CommentResponse[]>(`/api/tickets/${ticketId}/comments`);
}

export function addComment(ticketId: number, body: string): Promise<CommentResponse> {
  return ticketApi.post<CommentResponse>(`/api/tickets/${ticketId}/comments`, { body });
}

export function fetchHistory(ticketId: number): Promise<StatusHistoryResponse[]> {
  return ticketApi.get<StatusHistoryResponse[]>(`/api/tickets/${ticketId}/history`);
}

export function fetchSlaBreaches(): Promise<TicketResponse[]> {
  return ticketApi.get<TicketResponse[]>('/api/tickets/reports/sla-breaches');
}

export function fetchAgingReport(): Promise<AgingReportRow[]> {
  return ticketApi.get<AgingReportRow[]>('/api/tickets/reports/aging');
}

// ---- ticket-service: internal messaging ----

export interface SendMessagePayload {
  recipientId: number;
  subject: string;
  body: string;
  ticketId?: number | null;
  parentId?: number | null;
}

export function sendMessage(payload: SendMessagePayload): Promise<MessageResponse> {
  return ticketApi.post<MessageResponse>('/api/messages', payload);
}

export function fetchMessages(box: MessageBox, page = 0): Promise<Page<MessageResponse>> {
  const query = new URLSearchParams({ box, page: String(page), size: '20' });
  return ticketApi.get<Page<MessageResponse>>(`/api/messages?${query.toString()}`);
}

export function fetchMessageThread(id: number): Promise<MessageResponse[]> {
  return ticketApi.get<MessageResponse[]>(`/api/messages/${id}/thread`);
}

export function fetchUnreadCount(): Promise<number> {
  return ticketApi.get<{ count: number }>('/api/messages/unread-count').then((r) => r.count);
}

// ---- ai-service ----

/** Fire-and-forget background analysis of a freshly created ticket. */
export function analyzeTicket(ticketId: number): Promise<{ requestId: string; status: string }> {
  return aiApi.post(`/api/analyze/tickets/${ticketId}`);
}

export function fetchAnalysisByTicket(ticketId: number): Promise<AnalysisResponse> {
  return aiApi.get<AnalysisResponse>(`/api/analyses/by-ticket/${ticketId}`);
}

/** "Create ticket anyway" — resumes a SOLVED assistant run through the API agent. */
export function createTicketFromAssist(requestId: string): Promise<AnalysisResponse> {
  return aiApi.post<AnalysisResponse>(`/api/assist/${requestId}/create-ticket`);
}
