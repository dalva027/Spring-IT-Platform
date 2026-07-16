import { authApi, ticketApi } from './client';
import type {
  AgingReportRow,
  AuthResponse,
  CommentResponse,
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

export function updateUserRole(userId: number, role: Role): Promise<UserResponse> {
  return authApi.patch<UserResponse>(`/api/users/${userId}/role`, { role });
}

// ---- ticket-service ----

export interface TicketSearchParams {
  status?: TicketStatus;
  priority?: TicketPriority;
  assigneeId?: number;
  page?: number;
  size?: number;
  sort?: string;
}

export function searchTickets(params: TicketSearchParams): Promise<Page<TicketResponse>> {
  const query = new URLSearchParams();
  if (params.status) query.set('status', params.status);
  if (params.priority) query.set('priority', params.priority);
  if (params.assigneeId !== undefined) query.set('assigneeId', String(params.assigneeId));
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
