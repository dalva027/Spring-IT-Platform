import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  fetchContacts,
  fetchMessageThread,
  fetchMessages,
  sendMessage,
} from '../api/endpoints';
import type { Contact, MessageBox, MessageResponse } from '../api/types';
import { useAuth } from '../auth/AuthContext';
import { formatDateTime } from '../components/badges';
import { EmptyState, ErrorMessage, Spinner } from '../components/feedback';
import { useMessages } from '../messages/MessagesContext';

interface ComposeState {
  recipientId: number | '';
  subject: string;
  body: string;
  ticketId: string;
  parentId: number | null;
  /** When replying the recipient is fixed and the picker is hidden. */
  lockRecipient: boolean;
}

const BLANK_COMPOSE: ComposeState = {
  recipientId: '',
  subject: '',
  body: '',
  ticketId: '',
  parentId: null,
  lockRecipient: false,
};

export function InboxPage() {
  const { user } = useAuth();
  const { refresh: refreshUnread } = useMessages();

  const [box, setBox] = useState<MessageBox>('inbox');
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [thread, setThread] = useState<MessageResponse[] | null>(null);
  const [threadLoading, setThreadLoading] = useState(false);

  const [contacts, setContacts] = useState<Contact[]>([]);
  const [compose, setCompose] = useState<ComposeState | null>(null);
  const [sending, setSending] = useState(false);

  const nameOf = useMemo(() => {
    const byId = new Map(contacts.map((c) => [c.id, c.fullName]));
    return (id: number) => {
      if (user && id === user.id) return 'You';
      return byId.get(id) ?? `User #${id}`;
    };
  }, [contacts, user]);

  useEffect(() => {
    fetchContacts()
      .then(setContacts)
      .catch(() => {
        // Non-fatal: names fall back to "User #id" and compose is still usable.
      });
  }, []);

  const loadList = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchMessages(box)
      .then((data) => setMessages(data.content))
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load messages'))
      .finally(() => setLoading(false));
  }, [box]);

  useEffect(() => {
    setSelectedId(null);
    setThread(null);
    loadList();
  }, [loadList]);

  function openMessage(message: MessageResponse) {
    setSelectedId(message.id);
    setCompose(null);
    setThreadLoading(true);
    setThread(null);
    fetchMessageThread(message.id)
      .then((data) => {
        setThread(data);
        // The thread endpoint marks the opened message read — reflect that locally.
        if (box === 'inbox') {
          setMessages((prev) =>
            prev.map((m) => (m.id === message.id ? { ...m, read: true } : m)),
          );
        }
        refreshUnread();
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load conversation'))
      .finally(() => setThreadLoading(false));
  }

  function startNewMessage() {
    setSelectedId(null);
    setThread(null);
    setCompose({ ...BLANK_COMPOSE });
  }

  function startReply(message: MessageResponse) {
    const other = message.senderId === user?.id ? message.recipientId : message.senderId;
    setCompose({
      recipientId: other,
      subject: message.subject.startsWith('Re: ') ? message.subject : `Re: ${message.subject}`,
      body: '',
      ticketId: message.ticketId ? String(message.ticketId) : '',
      parentId: message.id,
      lockRecipient: true,
    });
  }

  async function submitCompose(e: React.FormEvent) {
    e.preventDefault();
    if (!compose || compose.recipientId === '') return;
    setSending(true);
    setError(null);
    try {
      const sent = await sendMessage({
        recipientId: Number(compose.recipientId),
        subject: compose.subject,
        body: compose.body,
        ticketId: compose.ticketId ? Number(compose.ticketId) : null,
        parentId: compose.parentId,
      });
      setCompose(null);
      refreshUnread();
      if (compose.parentId && selectedId) {
        // Replying: refresh the open conversation in place.
        openMessage({ ...sent, id: selectedId });
      } else {
        // New message: jump to Sent so the user sees it land.
        setBox('sent');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setSending(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Inbox</h1>
        <button type="button" className="btn-primary btn-accent" onClick={startNewMessage}>
          + New message
        </button>
      </div>

      <div className="inbox-tabs">
        <button
          type="button"
          className={`inbox-tab ${box === 'inbox' ? 'inbox-tab--active' : ''}`}
          onClick={() => setBox('inbox')}
        >
          Inbox
        </button>
        <button
          type="button"
          className={`inbox-tab ${box === 'sent' ? 'inbox-tab--active' : ''}`}
          onClick={() => setBox('sent')}
        >
          Sent
        </button>
      </div>

      {error && <ErrorMessage message={error} />}

      <div className="inbox-grid">
        <div className="inbox-list card">
          {loading && <Spinner label="Loading messages…" />}
          {!loading && messages.length === 0 && (
            <EmptyState message={box === 'inbox' ? 'No messages yet.' : 'You have not sent any messages.'} />
          )}
          {!loading &&
            messages.map((message) => {
              const other = box === 'inbox' ? message.senderId : message.recipientId;
              const unread = box === 'inbox' && !message.read;
              return (
                <button
                  type="button"
                  key={message.id}
                  className={`inbox-item ${selectedId === message.id ? 'inbox-item--active' : ''} ${
                    unread ? 'inbox-item--unread' : ''
                  }`}
                  onClick={() => openMessage(message)}
                >
                  <span className="inbox-item__dot" aria-hidden="true" />
                  <span className="inbox-item__main">
                    <span className="inbox-item__top">
                      <span className="inbox-item__party">
                        {box === 'inbox' ? nameOf(other) : `To: ${nameOf(other)}`}
                      </span>
                      <span className="inbox-item__time">{formatDateTime(message.createdAt)}</span>
                    </span>
                    <span className="inbox-item__subject">{message.subject}</span>
                    <span className="inbox-item__snippet">{message.body}</span>
                  </span>
                </button>
              );
            })}
        </div>

        <div className="inbox-pane">
          {compose ? (
            <ComposeForm
              compose={compose}
              contacts={contacts}
              sending={sending}
              onChange={setCompose}
              onSubmit={submitCompose}
              onCancel={() => setCompose(null)}
            />
          ) : threadLoading ? (
            <div className="card">
              <Spinner label="Loading conversation…" />
            </div>
          ) : thread ? (
            <MessageThread thread={thread} nameOf={nameOf} onReply={startReply} />
          ) : (
            <div className="card inbox-empty-pane">
              <EmptyState message="Select a message to read it, or start a new one." />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MessageThread({
  thread,
  nameOf,
  onReply,
}: {
  thread: MessageResponse[];
  nameOf: (id: number) => string;
  onReply: (message: MessageResponse) => void;
}) {
  const latest = thread[thread.length - 1];
  return (
    <div className="card">
      <div className="thread-header">
        <h2>{thread[0]?.subject}</h2>
        {latest?.ticketId && (
          <Link to={`/tickets/${latest.ticketId}`} className="thread-ticket-link">
            Ticket #{latest.ticketId}
          </Link>
        )}
      </div>
      <ul className="thread-list">
        {thread.map((message) => (
          <li key={message.id} className="thread-message">
            <div className="thread-message__meta">
              <strong>{nameOf(message.senderId)}</strong>
              <span>→ {nameOf(message.recipientId)}</span>
              <span className="thread-message__time">{formatDateTime(message.createdAt)}</span>
            </div>
            <p className="thread-message__body">{message.body}</p>
          </li>
        ))}
      </ul>
      <div className="form-actions">
        <button type="button" className="btn-primary" onClick={() => onReply(latest)}>
          Reply
        </button>
      </div>
    </div>
  );
}

function ComposeForm({
  compose,
  contacts,
  sending,
  onChange,
  onSubmit,
  onCancel,
}: {
  compose: ComposeState;
  contacts: Contact[];
  sending: boolean;
  onChange: (next: ComposeState) => void;
  onSubmit: (e: React.FormEvent) => void;
  onCancel: () => void;
}) {
  return (
    <form className="card form" onSubmit={onSubmit}>
      <h2>{compose.parentId ? 'Reply' : 'New message'}</h2>
      {compose.lockRecipient ? (
        <p className="compose-to">
          To: <strong>{contacts.find((c) => c.id === compose.recipientId)?.fullName ?? 'the sender'}</strong>
        </p>
      ) : (
        <label>
          To
          <select
            value={compose.recipientId}
            onChange={(e) =>
              onChange({ ...compose, recipientId: e.target.value ? Number(e.target.value) : '' })
            }
            required
          >
            <option value="">Select a recipient…</option>
            {contacts.map((contact) => (
              <option key={contact.id} value={contact.id}>
                {contact.fullName} ({contact.role.toLowerCase()})
              </option>
            ))}
          </select>
        </label>
      )}
      <label>
        Subject
        <input
          type="text"
          value={compose.subject}
          maxLength={200}
          onChange={(e) => onChange({ ...compose, subject: e.target.value })}
          required
        />
      </label>
      <label>
        Message
        <textarea
          rows={6}
          value={compose.body}
          maxLength={5000}
          onChange={(e) => onChange({ ...compose, body: e.target.value })}
          required
        />
      </label>
      <label>
        Related ticket # (optional)
        <input
          type="number"
          min={1}
          value={compose.ticketId}
          onChange={(e) => onChange({ ...compose, ticketId: e.target.value })}
        />
      </label>
      <div className="form-actions">
        <button type="button" className="btn-secondary" onClick={onCancel} disabled={sending}>
          Cancel
        </button>
        <button type="submit" className="btn-primary" disabled={sending || compose.recipientId === ''}>
          {sending ? 'Sending…' : 'Send'}
        </button>
      </div>
    </form>
  );
}
