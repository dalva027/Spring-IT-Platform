import { useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { createTicketFromAssist } from '../api/endpoints';
import { streamAssist } from '../api/aiStream';
import type { AnalysisResponse } from '../api/types';
import { AI_PIPELINE_STEPS } from '../api/types';
import { PriorityBadge } from '../components/badges';
import { ErrorMessage } from '../components/feedback';

type Phase = 'idle' | 'running' | 'done' | 'error';
type StepState = 'pending' | 'running' | 'done' | 'skipped';

export function AssistantPage() {
  const [issueText, setIssueText] = useState('');
  const [phase, setPhase] = useState<Phase>('idle');
  const [error, setError] = useState<string | null>(null);
  const [started, setStarted] = useState<Set<string>>(new Set());
  const [ended, setEnded] = useState<Set<string>>(new Set());
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [creatingTicket, setCreatingTicket] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  function stepState(node: string): StepState {
    if (ended.has(node)) return 'done';
    if (started.has(node)) return 'running';
    if (phase === 'done' || phase === 'error') return 'skipped';
    return 'pending';
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (phase === 'running' || issueText.trim().length < 5) return;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setPhase('running');
    setError(null);
    setStarted(new Set());
    setEnded(new Set());
    setResult(null);

    await streamAssist(
      issueText.trim(),
      {
        onEvent: (assistEvent) => {
          const node = typeof assistEvent.data.node === 'string' ? assistEvent.data.node : '';
          if (assistEvent.type === 'node_start' && node) {
            setStarted((prev) => new Set(prev).add(node));
          } else if (assistEvent.type === 'node_end' && node) {
            setEnded((prev) => new Set(prev).add(node));
          } else if (assistEvent.type === 'result') {
            setResult(assistEvent.data as unknown as AnalysisResponse);
            setPhase('done');
          } else if (assistEvent.type === 'error') {
            setError(String(assistEvent.data.message ?? 'The AI pipeline failed'));
            setPhase('error');
          }
        },
        onDone: () => {
          setPhase((current) => (current === 'running' ? 'done' : current));
        },
        onError: (message) => {
          setError(message);
          setPhase('error');
        },
      },
      controller.signal,
    );
  }

  async function handleCreateTicketAnyway() {
    if (!result) return;
    setCreatingTicket(true);
    setError(null);
    try {
      setResult(await createTicketFromAssist(result.requestId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create the ticket');
    } finally {
      setCreatingTicket(false);
    }
  }

  const outcome = result?.escalation?.outcome ?? null;

  return (
    <div className="narrow-page assistant-page">
      <h1>Get help</h1>
      <p className="assistant-intro">
        Describe your problem in plain language. A pipeline of AI agents will classify it, search
        company docs and past tickets, suggest fixes, and open a ticket if needed.
      </p>

      <form className="card form" onSubmit={handleSubmit}>
        {error && <ErrorMessage message={error} />}
        <label>
          What's going on?
          <textarea
            value={issueText}
            onChange={(e) => setIssueText(e.target.value)}
            maxLength={10000}
            rows={4}
            placeholder="e.g. My VPN disconnects every 10 minutes when working from home"
            required
            minLength={5}
            disabled={phase === 'running'}
          />
        </label>
        <div className="form-actions">
          <button type="submit" className="btn-primary" disabled={phase === 'running'}>
            {phase === 'running' ? 'Agents working…' : 'Ask the AI helpdesk'}
          </button>
        </div>
      </form>

      {phase !== 'idle' && (
        <section className="card ai-timeline-card">
          <h2>Agent progress</h2>
          <ol className="ai-timeline">
            {AI_PIPELINE_STEPS.map((step) => {
              const state = stepState(step.node);
              return (
                <li key={step.node} className={`ai-step ai-step-${state}`}>
                  <span className="ai-step-marker" aria-hidden="true" />
                  <span className="ai-step-label">{step.label}</span>
                  <span className="ai-step-status">
                    {state === 'running' && 'working…'}
                    {state === 'done' && '✓'}
                    {state === 'skipped' && 'skipped'}
                  </span>
                </li>
              );
            })}
          </ol>
        </section>
      )}

      {result && (
        <section className="card ai-result">
          <h2>Result</h2>

          {result.classification && (
            <p className="ai-result-line">
              <span className={`badge ai-category-${result.classification.category.toLowerCase()}`}>
                {result.classification.category}
              </span>{' '}
              <PriorityBadge priority={result.classification.suggested_priority} />
              <span className="detail-sub"> {result.classification.rationale}</span>
            </p>
          )}

          {outcome && (
            <p className="ai-result-line">
              <span className={`badge ai-outcome-${outcome.toLowerCase()}`}>
                {outcome.replace('_', ' ')}
              </span>
              {result.escalation?.assignment_hint && (
                <span className="detail-sub"> {result.escalation.assignment_hint}</span>
              )}
            </p>
          )}

          {result.troubleshooting && result.troubleshooting.steps.length > 0 && (
            <>
              <h3>Try these steps</h3>
              <ol className="ai-steps-list">
                {result.troubleshooting.steps.map((step, index) => (
                  <li key={index}>{step}</li>
                ))}
              </ol>
            </>
          )}

          {result.docHits && result.docHits.length > 0 && (
            <>
              <h3>Sources</h3>
              <ul className="ai-sources">
                {result.docHits.map((hit, index) => (
                  <li key={index}>
                    {hit.title}
                    {hit.heading ? ` — ${hit.heading}` : ''}
                  </li>
                ))}
              </ul>
            </>
          )}

          {result.ticketHits && result.ticketHits.length > 0 && (
            <>
              <h3>Similar past tickets</h3>
              <ul className="ai-sources">
                {result.ticketHits.map((hit) => (
                  <li key={hit.ticketId}>
                    <Link to={`/tickets/${hit.ticketId}`}>#{hit.ticketId}</Link> {hit.title}
                  </li>
                ))}
              </ul>
            </>
          )}

          {result.externalIssues && result.externalIssues.length > 0 && (
            <p className="ai-result-line detail-sub">
              External issues:{' '}
              {result.externalIssues.map((issue) => `${issue.provider} ${issue.key}`).join(', ')}
            </p>
          )}

          {result.ticketId ? (
            <p className="ai-result-line">
              Ticket <Link to={`/tickets/${result.ticketId}`}>#{result.ticketId}</Link> was created
              for you.
            </p>
          ) : (
            outcome === 'SOLVED' && (
              <div className="form-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleCreateTicketAnyway}
                  disabled={creatingTicket}
                >
                  {creatingTicket ? 'Creating…' : 'Create ticket anyway'}
                </button>
              </div>
            )
          )}
        </section>
      )}
    </div>
  );
}
