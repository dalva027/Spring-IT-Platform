import { useCallback, useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  addComment,
  fetchComments,
  fetchHistory,
  fetchTicket,
  updateTicketAssignee,
  updateTicketStatus,
} from '../api/endpoints';
import type {
  CommentResponse,
  StatusHistoryResponse,
  TicketResponse,
  TicketStatus,
} from '../api/types';
import { ALLOWED_TRANSITIONS, statusLabel } from '../api/types';
import { useAuth } from '../auth/AuthContext';
import { useUserDirectory } from '../auth/UserDirectoryContext';
import {
  PriorityBadge,
  SlaIndicator,
  StatusBadge,
  formatDateTime,
} from '../components/badges';
import { EmptyState, ErrorMessage, Spinner } from '../components/feedback';

export function TicketDetailPage() {
  const { id } = useParams();
  const ticketId = Number(id);
  const { isAgent } = useAuth();
  const { displayName, agents } = useUserDirectory();

  const [ticket, setTicket] = useState<TicketResponse | null>(null);
  const [comments, setComments] = useState<CommentResponse[]>([]);
  const [history, setHistory] = useState<StatusHistoryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const [commentBody, setCommentBody] = useState('');
  const [postingComment, setPostingComment] = useState(false);
  const [changingStatus, setChangingStatus] = useState(false);
  const [assigneeChoice, setAssigneeChoice] = useState('');
  const [assigning, setAssigning] = useState(false);

  const load = useCallback(async () => {
    setError(null);
    try {
      const [t, c, h] = await Promise.all([
        fetchTicket(ticketId),
        fetchComments(ticketId),
        fetchHistory(ticketId),
      ]);
      setTicket(t);
      setComments(c);
      setHistory(h);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load ticket');
    } finally {
      setLoading(false);
    }
  }, [ticketId]);

  useEffect(() => {
    if (Number.isNaN(ticketId)) {
      setError('Invalid ticket id');
      setLoading(false);
      return;
    }
    setLoading(true);
    void load();
  }, [ticketId, load]);

  async function handleStatusChange(target: TicketStatus) {
    if (!ticket) return;
    setActionError(null);
    setChangingStatus(true);
    try {
      await updateTicketStatus(ticket.id, target);
      await load();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Status change failed');
    } finally {
      setChangingStatus(false);
    }
  }

  async function handleAssign(event: FormEvent) {
    event.preventDefault();
    if (!ticket || !assigneeChoice) return;
    setActionError(null);
    setAssigning(true);
    try {
      await updateTicketAssignee(ticket.id, Number(assigneeChoice));
      setAssigneeChoice('');
      await load();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Assignment failed');
    } finally {
      setAssigning(false);
    }
  }

  async function handleComment(event: FormEvent) {
    event.preventDefault();
    if (!commentBody.trim()) return;
    setActionError(null);
    setPostingComment(true);
    try {
      await addComment(ticketId, commentBody.trim());
      setCommentBody('');
      setComments(await fetchComments(ticketId));
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to post comment');
    } finally {
      setPostingComment(false);
    }
  }

  if (loading) return <Spinner label="Loading ticket…" />;
  if (error) return <ErrorMessage message={error} />;
  if (!ticket) return <ErrorMessage message="Ticket not found" />;

  const transitions = ALLOWED_TRANSITIONS[ticket.status];

  return (
    <div>
      <p className="breadcrumb">
        <Link to="/tickets">← Back to tickets</Link>
      </p>

      <div className="page-header">
        <h1>
          <span className="ticket-number">#{ticket.id}</span> {ticket.title}
        </h1>
      </div>

      {actionError && <ErrorMessage message={actionError} />}

      <div className="detail-grid">
        <div className="detail-main">
          <section className="card">
            <h2>Description</h2>
            <p className="ticket-description">{ticket.description}</p>
          </section>

          <section className="card">
            <h2>Comments ({comments.length})</h2>
            {comments.length === 0 && <EmptyState message="No comments yet." />}
            <ul className="comment-list">
              {comments.map((comment) => (
                <li key={comment.id} className="comment">
                  <div className="comment-meta">
                    <strong>{displayName(comment.authorId)}</strong>
                    <time>{formatDateTime(comment.createdAt)}</time>
                  </div>
                  <p>{comment.body}</p>
                </li>
              ))}
            </ul>
            <form className="comment-form" onSubmit={handleComment}>
              <textarea
                value={commentBody}
                onChange={(e) => setCommentBody(e.target.value)}
                maxLength={5000}
                rows={3}
                placeholder="Write a comment…"
                required
              />
              <button type="submit" className="btn-primary" disabled={postingComment}>
                {postingComment ? 'Posting…' : 'Post comment'}
              </button>
            </form>
          </section>

          <section className="card">
            <h2>Status history</h2>
            {history.length === 0 && <EmptyState message="No status changes yet." />}
            <ul className="history-list">
              {history.map((entry) => (
                <li key={entry.id}>
                  <span className="history-transition">
                    {entry.fromStatus ? statusLabel(entry.fromStatus) : 'Created'} →{' '}
                    <strong>{statusLabel(entry.toStatus)}</strong>
                  </span>
                  <span className="history-meta">
                    by {displayName(entry.changedBy)} · {formatDateTime(entry.changedAt)}
                  </span>
                </li>
              ))}
            </ul>
          </section>
        </div>

        <aside className="detail-side">
          <section className="card">
            <h2>Details</h2>
            <dl className="detail-list">
              <dt>Status</dt>
              <dd>
                <StatusBadge status={ticket.status} />
              </dd>
              <dt>Priority</dt>
              <dd>
                <PriorityBadge priority={ticket.priority} />
              </dd>
              <dt>SLA</dt>
              <dd>
                <SlaIndicator slaDueAt={ticket.slaDueAt} status={ticket.status} />
                <div className="detail-sub">due {formatDateTime(ticket.slaDueAt)}</div>
              </dd>
              <dt>Requester</dt>
              <dd>{displayName(ticket.requesterId)}</dd>
              <dt>Assignee</dt>
              <dd>{displayName(ticket.assigneeId)}</dd>
              <dt>Created</dt>
              <dd>{formatDateTime(ticket.createdAt)}</dd>
              <dt>Updated</dt>
              <dd>{formatDateTime(ticket.updatedAt)}</dd>
            </dl>
          </section>

          {isAgent && (
            <section className="card">
              <h2>Actions</h2>
              {transitions.length > 0 ? (
                <div className="action-buttons">
                  {transitions.map((target) => (
                    <button
                      key={target}
                      type="button"
                      className="btn-secondary"
                      disabled={changingStatus}
                      onClick={() => handleStatusChange(target)}
                    >
                      Move to {statusLabel(target)}
                    </button>
                  ))}
                </div>
              ) : (
                <p className="detail-sub">This ticket is closed — no further transitions.</p>
              )}

              <form className="assign-form" onSubmit={handleAssign}>
                <label>
                  Assign to
                  <select
                    value={assigneeChoice}
                    onChange={(e) => setAssigneeChoice(e.target.value)}
                  >
                    <option value="">Select an agent…</option>
                    {agents.map((agent) => (
                      <option key={agent.id} value={agent.id}>
                        {agent.fullName} ({agent.role})
                      </option>
                    ))}
                  </select>
                </label>
                <button
                  type="submit"
                  className="btn-secondary"
                  disabled={!assigneeChoice || assigning}
                >
                  {assigning ? 'Assigning…' : 'Assign'}
                </button>
              </form>
            </section>
          )}
        </aside>
      </div>
    </div>
  );
}
