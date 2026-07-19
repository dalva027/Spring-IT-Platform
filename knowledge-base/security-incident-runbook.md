---
title: Security Incident Runbook for Employees
category: SECURITY
tags: [phishing, malware, incident-response, lost-device, credential-compromise]
---

# Security Incident Runbook for Employees

This runbook tells every employee exactly what to do (and what NOT to do) when something security-related goes wrong: phishing, suspected malware, a lost or stolen device, or a compromised account. When in doubt, report it — a false alarm costs minutes; an unreported incident can cost weeks.

## Emergency contacts

| Channel | When to use |
|---|---|
| **Security hotline: ext. 7233** (external number on the intranet Security page) | Active/urgent incidents: malware behavior in progress, stolen device, confirmed compromise. Staffed 24/7. |
| **secops@internal.example** | Non-urgent reports, follow-ups, questions |
| **"Report Phishing" button** in Outlook / OWA | All suspicious emails |
| Helpdesk portal (https://helpdesk.internal.example, category: Security > Incident) | Formal ticket; the hotline will open one for you on urgent calls |

Never assume "someone else already reported it."

## Severity levels

- **SEV-1 (Critical)**: active malware/ransomware behavior, confirmed account takeover, stolen device with sensitive data, data visibly leaving the company. → Call ext. 7233 immediately.
- **SEV-2 (High)**: credentials entered on a phishing site, lost (not confirmed stolen) device, unexpected MFA prompts, malware alert from the endpoint agent. → Call ext. 7233 or ticket within 1 hour.
- **SEV-3 (Medium)**: phishing email received but NOT interacted with, suspicious USB device found, policy violations observed. → Report Phishing button / ticket same day.
- **SEV-4 (Low)**: general questions, requests for security review of a tool or vendor. → Ticket or secops@internal.example.

Employees do not need to classify perfectly — describe what happened and Security Operations will set the severity.

## Phishing: reporting suspicious email

1. Do not click links, open attachments, reply, or forward to colleagues to ask "is this legit?".
2. Click the **Report Phishing** button in Outlook or OWA (Home ribbon / message "..." menu). This sends the full message with headers to Security Operations and removes it from your inbox.
3. If the button is unavailable, forward the email **as an attachment** to secops@internal.example, then delete it.
4. If you already clicked a link but entered nothing: report via the button anyway and mention the click in a follow-up to secops@internal.example.
5. If you entered your password or approved an MFA prompt: this is **credential compromise** — jump to that section now. Time matters.
6. Suspicious text messages (smishing) or phone calls impersonating IT/executives: report to secops@internal.example with a screenshot or summary. Real IT will never ask for your password or MFA codes.

## Suspected malware on your device

Symptoms: ransom notes, files renamed with strange extensions, security agent alerts, the fan spinning at 100% with an unknown process, browser hijacked, pop-ups outside the browser.

1. **Disconnect from the network immediately — do NOT power off.**
   - Unplug the ethernet cable and turn off Wi-Fi (airplane mode).
   - Powering off destroys the in-memory evidence forensics needs and, with ransomware, can make recovery harder. Leave the machine ON but isolated.
2. Do not log into anything else from the affected machine, and do not plug in USB drives.
3. From a DIFFERENT device (phone, another laptop), call the security hotline **ext. 7233**.
4. Write down what you observed: time, what you clicked/installed/opened last, exact alert text, filenames.
5. Follow the analyst's instructions. They may take remote control via the endpoint agent or ask you to bring/ship the device in.
6. If credentials were used on that machine recently, expect Security to force a password reset — this is normal containment.

## Lost or stolen device

Applies to laptops, phones with company email, tablets, and hardware security keys.

1. Report within **1 hour** of noticing: call ext. 7233 (24/7). After hours still call — do not wait for morning.
2. Provide: device type, asset tag if known (sticker on the underside; also listed in the Helpdesk portal under My Assets), last known location and time, and whether it was locked.
3. Security will remotely lock/wipe the device and revoke its sessions and certificates. Change your password at https://helpdesk.internal.example/reset from another device.
4. If stolen, file a police report (Security will tell you if needed for the region) and send the report number to secops@internal.example.
5. Lost badge? Report to the front desk AND open a Security > Badge ticket so it is deactivated.
6. If the device turns up later, tell Security BEFORE using it again — it must be checked and re-trusted first.

## Credential compromise

You typed your password on a suspicious site, someone shoulder-surfed it, you approved an MFA push you did not initiate, or you get "new sign-in" alerts you do not recognize.

1. Immediately change your password at **https://helpdesk.internal.example/reset** from a known-good device. Do this FIRST — before reporting — if you can; every minute counts.
2. Deny any pending MFA prompts. Never approve a push "to make it stop" — that is exactly the attacker's goal (MFA fatigue attack).
3. Call ext. 7233 or email secops@internal.example (SEV-2). Security will revoke active sessions and tokens and review sign-in logs with you.
4. Review your account for attacker persistence with the analyst: mail forwarding rules, newly registered MFA devices, app passwords.
5. If the same password was used on any personal site (it should not be), change it there too.

## Do-NOT-do list

1. Do NOT power off a machine showing malware/ransomware behavior — disconnect it from the network instead.
2. Do NOT pay, negotiate, or communicate with any ransom demand.
3. Do NOT forward phishing emails to coworkers — report via the button.
4. Do NOT investigate on your own: no scanning tools, no "hacking back", no opening the suspicious attachment in a personal VM.
5. Do NOT delete suspicious emails or files before Security has seen them (the Report Phishing button preserves them correctly).
6. Do NOT plug in found USB drives — hand them to Security.
7. Do NOT share incident details on chat channels, social media, or with external parties; communications are coordinated by Security and Legal.
8. Do NOT approve MFA prompts you did not initiate.
9. Do NOT keep working on a device you suspect is compromised, "just to finish one thing."

## What happens after you report

1. Acknowledgement: hotline is immediate; tickets/mailbox within 1 business hour for SEV-1/2, 1 business day for SEV-3/4.
2. Containment: Security may isolate your device, reset credentials, or revoke sessions — cooperate even if it interrupts work; your manager will be informed for anything disruptive.
3. You may be asked for a short written timeline of events. Plain, honest detail helps; reporting a mistake (clicking a link, using a weak password) never results in punishment — the company's policy is no-blame reporting to keep incidents visible.
4. Closure: you will be told when the incident is closed and if any follow-up training is assigned.

## When to escalate

- Any SEV-1/SEV-2 symptom: call **ext. 7233** — do not rely on a ticket alone.
- No acknowledgement of a SEV-2 report within 1 hour: call the hotline and reference your ticket number.
- You reported phishing but colleagues are still receiving the same message: reply to secops@internal.example noting "campaign ongoing" so a tenant-wide purge can be run.
- You are unsure whether something is an incident at all: report it as SEV-4 — Security explicitly prefers over-reporting.

## Recognizing common attack patterns

### Phishing tells

1. Urgency and threats ("account closes in 24 hours", "CEO needs gift cards now").
2. Sender display name matches a colleague but the address is external (hover to check the real address; external mail carries the [EXTERNAL] banner).
3. Links whose visible text differs from the real destination (hover before ever clicking).
4. Unexpected attachments, especially .zip, .html, or macro-enabled Office files.
5. Requests to move the conversation to personal channels (SMS, personal email, chat apps).

### MFA fatigue

Bursts of push notifications, sometimes with a call "from IT" telling you to approve one. Deny all, change your password, report — never approve to silence it.

### QR-code phishing (quishing)

Posters or emails with QR codes leading to credential pages. Treat QR codes like links: if unexpected, do not scan; report the email or tell Security where the poster is.

### Tech-support scams

Browser pop-ups with alarm sounds claiming infection and a support number. Close the browser (Task Manager if needed); never call the number or install remote-access tools. If anything was installed, treat as suspected malware (disconnect, do not power off, call ext. 7233).

## Frequently asked questions

### I reported a real email as phishing by mistake.

No harm done — Security releases false positives back to your inbox, usually within a few hours. When unsure, reporting is always the right call.

### Will I get in trouble for clicking a phishing link?

No. The company operates no-blame reporting: the only reportable failure is hiding an incident. Prompt reports routinely turn potential SEV-1s into non-events.

### Can I test suspicious files myself in a sandbox?

No — see the do-not-do list. Personal analysis can tip off attackers, spread the sample, or destroy evidence. Hand everything to Security Operations.

### The suspicious email is in a shared mailbox. Who reports it?

Whoever sees it first, using the Report Phishing button from within the shared mailbox. Note the shared mailbox name in a follow-up to secops@internal.example so the purge covers it.

## Quick reference

| Item | Value |
|---|---|
| 24/7 security hotline | ext. 7233 (external number on intranet Security page) |
| Report mailbox | secops@internal.example |
| Phishing | "Report Phishing" button in Outlook/OWA |
| Malware rule | Disconnect from network; do NOT power off |
| Lost/stolen device | Call ext. 7233 within 1 hour |
| Credential compromise | Reset first at https://helpdesk.internal.example/reset, then report |
| Ticket category | Security > Incident at https://helpdesk.internal.example |
