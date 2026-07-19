"""Prompt templates for the helpdesk pipeline nodes."""

import json
from typing import Any


def classify_prompt(issue_text: str) -> str:
    return f"""You are the triage agent of an internal IT helpdesk.
Classify the employee's issue into exactly one category:
- IT: workstations, software, email clients, printers, peripherals
- HR: onboarding, benefits, badge access, HR processes
- FINANCE: expenses, reimbursements, corporate cards, invoices
- NETWORKING: VPN, Wi-Fi, connectivity, DNS, network shares
- SECURITY: phishing, malware, compromised credentials, lost devices, incidents

Also suggest a ticket priority (LOW, MEDIUM, HIGH, CRITICAL) based on impact and
urgency, a confidence between 0 and 1, and a one-sentence rationale.

Employee issue:
\"\"\"{issue_text}\"\"\""""


def troubleshoot_prompt(
    issue_text: str,
    classification: dict[str, Any],
    doc_hits: list[dict[str, Any]],
    ticket_hits: list[dict[str, Any]],
) -> str:
    docs = "\n\n".join(
        f"[{hit['title']} — {hit.get('heading', '')}]\n{hit['snippet']}" for hit in doc_hits
    ) or "(no relevant documents found)"
    tickets = "\n".join(
        f"- Ticket #{hit['ticketId']} ({hit['status']}): {hit['title']}" for hit in ticket_hits
    ) or "(no similar past tickets)"
    return f"""You are the troubleshooting agent of an internal IT helpdesk.
The issue was classified as {classification.get('category')} \
(suggested priority {classification.get('suggested_priority')}).

Company knowledge-base excerpts:
{docs}

Similar past tickets:
{tickets}

Employee issue:
\"\"\"{issue_text}\"\"\"

Produce 3-7 concrete, ordered troubleshooting steps the employee can try,
grounded in the knowledge-base excerpts when applicable (mention the document
name in the step when you use one). Set self_serviceable=true only if a
non-technical employee can realistically fix this alone, and a confidence
between 0 and 1."""


def escalate_prompt(
    issue_text: str, classification: dict[str, Any], troubleshooting: dict[str, Any]
) -> str:
    return f"""You are the escalation agent of an internal IT helpdesk.
Decide the outcome for this issue:
- SOLVED: the troubleshooting steps almost certainly resolve it, no technician needed
- NEEDS_TECHNICIAN: a human agent should take over via a ticket
- EMERGENCY: active security incident, outage, or data-loss risk needing immediate attention

Classification: {json.dumps(classification)}
Troubleshooting plan: {json.dumps(troubleshooting)}

Employee issue:
\"\"\"{issue_text}\"\"\"

Also pick the final ticket_priority (LOW, MEDIUM, HIGH, CRITICAL — EMERGENCY
outcomes must be CRITICAL) and a short assignment_hint describing which team or
skill set should own the ticket."""


def summarize_prompt(state: dict[str, Any]) -> str:
    return f"""You are the reporting agent of an internal IT helpdesk. Based on the
analysis below, write three texts:
- ticket_comment: a concise, friendly note for the ticket thread aimed at the
  assigned technician (what was tried, what to check next)
- manager_summary: 2-3 sentences for a manager: impact, category, current state
- resolution_notes: bullet-style notes suitable for a future knowledge-base entry

Analysis:
- Issue: {state.get('issue_text', '')}
- Classification: {json.dumps(state.get('classification') or {})}
- Troubleshooting: {json.dumps(state.get('troubleshooting') or {})}
- Escalation: {json.dumps(state.get('escalation') or {})}
- Ticket id: {state.get('ticket_id')}"""
