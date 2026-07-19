import { useEffect, useState } from 'react';
import { fetchAnalysisByTicket } from '../api/endpoints';
import { ApiError } from '../api/client';
import type { AnalysisResponse } from '../api/types';
import { PriorityBadge } from './badges';

const POLL_INTERVAL_MS = 3000;
const MAX_POLLS = 20; // stop polling after ~60s

/**
 * AI-insights card on the ticket detail page. The analysis is produced
 * asynchronously after ticket creation, so poll briefly while it is missing
 * or still RUNNING; render nothing if no analysis ever appears.
 */
export function AiInsightsCard({ ticketId }: { ticketId: number }) {
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [gone, setGone] = useState(false);

  useEffect(() => {
    let polls = 0;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let cancelled = false;

    async function poll() {
      polls += 1;
      try {
        const result = await fetchAnalysisByTicket(ticketId);
        if (cancelled) return;
        setAnalysis(result);
        if (result.status === 'RUNNING' && polls < MAX_POLLS) {
          timer = setTimeout(poll, POLL_INTERVAL_MS);
        }
      } catch (err) {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 404 && polls < MAX_POLLS) {
          timer = setTimeout(poll, POLL_INTERVAL_MS);
        } else {
          setGone(true);
        }
      }
    }

    void poll();
    return () => {
      cancelled = true;
      if (timer !== undefined) clearTimeout(timer);
    };
  }, [ticketId]);

  if (gone || analysis === null) return null;

  return (
    <section className="card ai-insights">
      <h2>AI insights</h2>

      {analysis.status === 'RUNNING' && (
        <p className="detail-sub">The AI agents are still analyzing this ticket…</p>
      )}
      {analysis.status === 'FAILED' && (
        <p className="detail-sub">The AI analysis failed for this ticket.</p>
      )}

      {analysis.classification && (
        <p className="ai-result-line">
          <span className={`badge ai-category-${analysis.classification.category.toLowerCase()}`}>
            {analysis.classification.category}
          </span>{' '}
          <PriorityBadge priority={analysis.classification.suggested_priority} />
        </p>
      )}

      {analysis.escalation && (
        <p className="ai-result-line">
          <span className={`badge ai-outcome-${analysis.escalation.outcome.toLowerCase()}`}>
            {analysis.escalation.outcome.replace('_', ' ')}
          </span>
          {analysis.escalation.assignment_hint && (
            <span className="detail-sub"> {analysis.escalation.assignment_hint}</span>
          )}
        </p>
      )}

      {analysis.troubleshooting && analysis.troubleshooting.steps.length > 0 && (
        <>
          <h3>Suggested steps</h3>
          <ol className="ai-steps-list">
            {analysis.troubleshooting.steps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ol>
        </>
      )}

      {analysis.summaries?.manager_summary && (
        <>
          <h3>Summary</h3>
          <p className="detail-sub">{analysis.summaries.manager_summary}</p>
        </>
      )}

      {analysis.externalIssues && analysis.externalIssues.length > 0 && (
        <p className="detail-sub">
          External issues:{' '}
          {analysis.externalIssues.map((issue) => `${issue.provider} ${issue.key}`).join(', ')}
        </p>
      )}
    </section>
  );
}
