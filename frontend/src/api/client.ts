const AUTH_API = import.meta.env.VITE_AUTH_API_URL ?? 'http://localhost:8081';
const TICKET_API = import.meta.env.VITE_TICKET_API_URL ?? 'http://localhost:8082';

const TOKEN_KEY = 'helpdesk.token';

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (token === null) {
    localStorage.removeItem(TOKEN_KEY);
  } else {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

type UnauthorizedHandler = () => void;
let onUnauthorized: UnauthorizedHandler | null = null;

/** Registered by AuthContext so an expired token logs the user out globally. */
export function setUnauthorizedHandler(handler: UnauthorizedHandler | null): void {
  onUnauthorized = handler;
}

async function request<T>(base: string, path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
    ...(options.headers as Record<string, string>),
  };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${base}${path}`, { ...options, headers });
  } catch {
    throw new ApiError(0, 'Cannot reach the server. Is the backend running?');
  }

  if (response.status === 401 && token) {
    onUnauthorized?.();
    throw new ApiError(401, 'Your session has expired. Please sign in again.');
  }

  if (!response.ok) {
    throw new ApiError(response.status, await extractMessage(response));
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

async function extractMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body?.message === 'string' && body.message) return body.message;
    if (typeof body?.error === 'string' && body.error) return body.error;
    // Bean-validation errors arrive as a field->message map
    if (body && typeof body === 'object') {
      const parts = Object.entries(body)
        .filter(([, v]) => typeof v === 'string')
        .map(([field, msg]) => `${field}: ${msg}`);
      if (parts.length > 0) return parts.join('; ');
    }
  } catch {
    // fall through to generic message
  }
  return `Request failed (HTTP ${response.status})`;
}

export const authApi = {
  get: <T>(path: string) => request<T>(AUTH_API, path),
  post: <T>(path: string, body: unknown) =>
    request<T>(AUTH_API, path, { method: 'POST', body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(AUTH_API, path, { method: 'PATCH', body: JSON.stringify(body) }),
};

export const ticketApi = {
  get: <T>(path: string) => request<T>(TICKET_API, path),
  post: <T>(path: string, body: unknown) =>
    request<T>(TICKET_API, path, { method: 'POST', body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(TICKET_API, path, { method: 'PATCH', body: JSON.stringify(body) }),
};
