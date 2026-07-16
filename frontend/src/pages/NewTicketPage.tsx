import { useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { createTicket } from '../api/endpoints';
import type { TicketPriority } from '../api/types';
import { SLA_HOURS, TICKET_PRIORITIES } from '../api/types';
import { ErrorMessage } from '../components/feedback';

export function NewTicketPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<TicketPriority>('MEDIUM');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const ticket = await createTicket(title, description, priority);
      navigate(`/tickets/${ticket.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create ticket');
      setSubmitting(false);
    }
  }

  return (
    <div className="narrow-page">
      <h1>New ticket</h1>
      <form className="card form" onSubmit={handleSubmit}>
        {error && <ErrorMessage message={error} />}
        <label>
          Title
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={200}
            placeholder="Short summary of the problem"
            required
          />
        </label>
        <label>
          Description
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            maxLength={10000}
            rows={8}
            placeholder="What happened? What did you expect? Since when?"
            required
          />
        </label>
        <label>
          Priority
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as TicketPriority)}
          >
            {TICKET_PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p} — {SLA_HOURS[p]}h SLA
              </option>
            ))}
          </select>
        </label>
        <div className="form-actions">
          <button type="button" className="btn-ghost" onClick={() => navigate(-1)}>
            Cancel
          </button>
          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? 'Creating…' : 'Create ticket'}
          </button>
        </div>
      </form>
    </div>
  );
}
