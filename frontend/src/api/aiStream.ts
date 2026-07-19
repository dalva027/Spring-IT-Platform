/**
 * SSE client for POST /api/assist/stream on ai-service.
 *
 * Uses fetch + ReadableStream instead of EventSource: EventSource cannot send
 * an Authorization header, and putting the JWT in the URL would leak it into
 * logs and proxies.
 */
import { AI_API, getToken } from './client';
import type { AnalysisResponse } from './types';

export type AssistEventType = 'started' | 'node_start' | 'node_end' | 'result' | 'error';

export interface AssistEvent {
  type: AssistEventType;
  data: Record<string, unknown> & Partial<AnalysisResponse> & { node?: string; label?: string };
}

export interface AssistStreamHandlers {
  onEvent: (event: AssistEvent) => void;
  onDone?: () => void;
  onError?: (message: string) => void;
}

export async function streamAssist(
  issueText: string,
  handlers: AssistStreamHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const token = getToken();
  let response: Response;
  try {
    response = await fetch(`${AI_API}/api/assist/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ issue_text: issueText }),
      signal,
    });
  } catch (err) {
    if (signal?.aborted) return;
    handlers.onError?.(err instanceof Error ? err.message : 'Cannot reach the AI service');
    return;
  }

  if (!response.ok || !response.body) {
    handlers.onError?.(
      response.status === 401
        ? 'Your session has expired. Please sign in again.'
        : `AI service request failed (HTTP ${response.status})`,
    );
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      // SSE frames are separated by a blank line.
      let boundary = buffer.indexOf('\n\n');
      while (boundary !== -1) {
        const frame = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        dispatchFrame(frame, handlers);
        boundary = buffer.indexOf('\n\n');
      }
    }
  } catch (err) {
    if (!signal?.aborted) {
      handlers.onError?.(err instanceof Error ? err.message : 'Stream interrupted');
      return;
    }
  }
  handlers.onDone?.();
}

function dispatchFrame(frame: string, handlers: AssistStreamHandlers): void {
  let eventType = 'message';
  const dataLines: string[] = [];
  for (const line of frame.split('\n')) {
    if (line.startsWith(':')) continue; // heartbeat comment
    if (line.startsWith('event:')) eventType = line.slice(6).trim();
    else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim());
  }
  if (dataLines.length === 0) return;
  try {
    const data = JSON.parse(dataLines.join('\n'));
    handlers.onEvent({ type: eventType as AssistEventType, data });
  } catch {
    // ignore malformed frames
  }
}
