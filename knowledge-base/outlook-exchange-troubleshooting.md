---
title: Outlook and Exchange Troubleshooting
category: IT
tags: [outlook, exchange, email, calendar, owa]
---

# Outlook and Exchange Troubleshooting

This article covers the most common Outlook desktop issues reported to the Service Desk: connection failures, the "Trying to connect..." status, corrupted local cache (OST), profile problems, shared mailboxes, and calendar sync. Company mailboxes are hosted on Exchange Online; webmail is available at https://mail.internal.example (OWA).

## First step: isolate client vs server with OWA

Before any client-side repair, always check Outlook on the Web:

1. Open a browser and sign in at https://mail.internal.example.
2. Send yourself a test message and open your calendar.
3. Interpret the result:
   - **OWA works, desktop Outlook does not** → problem is local (client, profile, OST, network). Continue with this article.
   - **OWA also fails** → problem is account or server side (password expired, mailbox issue, service outage). Check the status banner on https://intranet.internal.example/it-status, then open a Helpdesk ticket.

## Outlook stuck on "Trying to connect..." or "Disconnected"

1. Confirm general internet access (open any external website).
2. If remote, confirm GlobalConnect VPN state. Note: Exchange Online does not require VPN, but a half-connected VPN tunnel can black-hole traffic — fully disconnect or fully connect and retest.
3. Check bottom-right status bar. If it says "Working Offline", go to **Send/Receive** tab and click **Work Offline** to toggle it off.
4. Restart Outlook. If unchanged, restart the machine (clears stuck authentication tokens).
5. Check for a stale credential prompt hidden behind other windows (Alt+Tab).
6. Clear cached credentials: Windows > Credential Manager > Windows Credentials > remove entries starting with `MicrosoftOffice16_` and `MicrosoftOfficeAccount`, then reopen Outlook and sign in.
7. Run Outlook in safe mode to rule out add-ins: Win+R > `outlook.exe /safe`. If it connects in safe mode, disable add-ins via File > Options > Add-ins > COM Add-ins > Go, then re-enable one at a time.

## Rebuilding the OST (local cache)

Symptoms of a corrupted OST: Outlook hangs on "Loading Profile", search returns nothing, folders show old content, or you see errors like "The file ...ost is in use and cannot be accessed" or repeated crashes when opening specific folders.

1. Close Outlook completely (check Task Manager for lingering `OUTLOOK.EXE`).
2. Open the OST location: Win+R > `%localappdata%\Microsoft\Outlook`.
3. Rename the `.ost` file for your mailbox (e.g., `user@internal.example.ost` → `user@internal.example.ost.old`). Do not delete it until the rebuild succeeds.
4. Reopen Outlook. It will rebuild the cache from the server; a large mailbox can take 30–60 minutes to fully sync. Search results are incomplete until sync finishes.
5. Once confirmed healthy for a few days, delete the `.old` file to reclaim disk space.

Note: OST rebuild does not lose data — everything lives on the server. Any items in local-only PST files are separate and unaffected.

## Recreating the Outlook profile

Use this when OST rebuild does not help, or errors mention "The set of folders cannot be opened" / "Cannot start Microsoft Outlook".

### Windows

1. Close Outlook.
2. Control Panel > **Mail (Microsoft Outlook)** > Show Profiles.
3. Click **Add**, name it e.g. `Fresh2026`, and complete the sign-in (email + password + MFA).
4. Set "Always use this profile" to the new profile.
5. Open Outlook, verify mail flow, then remove the old profile from the same dialog.

### macOS (New Outlook)

1. Outlook menu > Settings > Accounts > select the account > minus (–) to remove.
2. Quit and reopen Outlook, then re-add the account with company credentials.

## Shared mailbox issues

- **Shared mailbox missing**: shared mailboxes auto-map within 24 hours of access being granted. If missing after 24h, restart Outlook; if still missing, verify the grant in the original Helpdesk ticket.
- **"You do not have permission" when sending as the shared mailbox**: Send As / Send on Behalf are separate permissions from mailbox access. Request the specific permission via Helpdesk (category: IT > Email > Shared Mailbox).
- **Shared mailbox shows stale content**: shared mailboxes are cached too. File > Account Settings > double-click your account > More Settings > Advanced > uncheck "Download shared folders", restart Outlook. This forces online mode for shared folders.
- Access requests for shared mailboxes must be approved by the mailbox owner listed in the address book.

## Calendar sync problems

1. Compare desktop Outlook against OWA (https://mail.internal.example/calendar). OWA is the source of truth — if OWA is correct, it is a client cache issue: rebuild the OST (above).
2. Missing meeting updates: check Deleted Items and the "Conflicts" folder (visible in folder list when issues exist).
3. Delegates: if an assistant manages your calendar, ensure only ONE person processes each invite. Both delegate and owner acting on the same invite causes duplicates or disappearing meetings.
4. Room bookings that vanish usually mean the room mailbox declined (double-booking or policy limit) — check for a decline message in the organizer's inbox.
5. Mobile calendar out of sync: remove and re-add the account in the mobile mail app after confirming OWA is correct.

## When to escalate

Open a Helpdesk ticket (https://helpdesk.internal.example, category: IT > Email) when:

- OWA itself fails or shows a mailbox error — include the exact error text and timestamp (possible server-side issue; do not attempt client repairs).
- Profile recreation and OST rebuild have both been done and the issue persists.
- You see repeated password prompts that MFA-approved sign-ins do not clear (possible Conditional Access issue — include your device name).
- Mail is delayed by more than 30 minutes company-wide, or bounce messages (NDRs) reference internal recipients — attach the full NDR.
- A shared mailbox permission was approved but never appeared after 24 hours.

Include: screenshots of the error, whether OWA works, Outlook version (File > Office Account), and what steps from this article you already completed. For urgent executive/deadline situations call the Service Desk at ext. 4357.

## Frequently asked questions

### Why does search miss recent emails?

Local search depends on the Windows/macOS index and the OST cache. After an OST rebuild, wait for sync to finish. If search stays broken: Windows Settings > Search > Searching Windows > Advanced indexing options > Rebuild the index (allow several hours). OWA search queries the server directly and is a good cross-check.

### My mailbox is full — what now?

Standard mailboxes are 100 GB. At 90 GB you get warnings; at 100 GB sending stops. Empty Deleted Items and Junk, sort by size (Filter > Sort by Size), and archive old mail with the built-in Online Archive (enabled on request via Helpdesk, category IT > Email > Archive).

### How big can attachments be?

35 MB total per message. For anything larger, share a link from the approved cloud storage instead of attaching — links also respect access permissions if the file is forwarded.

### Can I get email on my personal phone?

Yes, via the managed mail profile only: install the company portal app, which provisions the mail profile with a work-data container. Adding the account directly in the native mail app is blocked by policy.

### Why do external emails show a banner?

All mail from outside the company is stamped with an [EXTERNAL] banner. It cannot be disabled — it exists so that a "colleague" mailing from an outside address is immediately visible. Treat unexpected external mail claiming to be internal as phishing (see the Security Incident Runbook).

### Recalling a message — does it work?

Only for unread messages to internal recipients using desktop Outlook, and it is unreliable. Assume a sent message cannot be pulled back; if sensitive data went to the wrong recipient, report it to secops@internal.example per the Security Incident Runbook.

## Quick reference

| Item | Value |
|---|---|
| Webmail (OWA) | https://mail.internal.example |
| Service status | https://intranet.internal.example/it-status |
| OST location (Windows) | %localappdata%\Microsoft\Outlook |
| Safe mode | Win+R > `outlook.exe /safe` |
| Mailbox / attachment limits | 100 GB / 35 MB |
| Support | https://helpdesk.internal.example (IT > Email), ext. 4357 |
