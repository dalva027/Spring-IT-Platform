---
title: Password Reset and Account Lockout Policy
category: SECURITY
tags: [password, reset, lockout, mfa, account-security]
---

# Password Reset and Account Lockout Policy

This article explains how to reset a company password, what the complexity and lockout rules are, how MFA re-enrollment works, and how the Service Desk verifies identity. It applies to all employees and contractors with company accounts.

## Self-service password reset (SSPR)

The fastest way to reset a forgotten or expired password is the self-service portal. No ticket is required.

1. Go to **https://helpdesk.internal.example/reset** from any device (works without VPN).
2. Enter your company email address (e.g., `jsmith@internal.example`).
3. Verify your identity with **two** of your registered methods:
   - MFA push notification or authenticator code
   - SMS one-time code to your registered mobile number
   - Answers to your security questions (legacy accounts only)
4. Choose a new password that meets the complexity rules below.
5. Wait up to 5 minutes for the change to sync, then sign in. Update the saved password on your phone's mail app and on any secondary devices immediately — stale saved passwords are the number-one cause of instant re-lockouts.

If you have never registered SSPR methods, enroll now at https://helpdesk.internal.example/reset/enroll while your account is healthy. Enrollment is mandatory within 7 days of hire.

## Password complexity rules

All company passwords must meet ALL of the following:

- Minimum **14 characters** (passphrases encouraged, e.g., four unrelated words).
- At least one uppercase letter, one lowercase letter, and one number.
- Must NOT contain your username, first name, or last name.
- Must NOT match any of your previous **10** passwords.
- Must NOT appear on the banned-password list (common words, company name, seasons + year, keyboard walks like `Qwerty123!`).
- Passwords expire every **365 days**; you will receive email reminders at 14, 7, and 1 day(s) before expiry.

Recommended: use the company-approved password manager (available in Software Center / Self Service) and let it generate passwords for non-SSO applications.

## Account lockout thresholds

- **5 failed sign-in attempts** within 15 minutes locks the account.
- The lock automatically releases after **15 minutes** — often the quickest fix is simply to wait, then try once with a carefully typed password.
- Repeated lockouts without user activity usually mean a stale saved password on a device (old phone, tablet mail profile, mapped drive, or scheduled task). Update or remove the stale credential.
- Ten lockouts within 24 hours triggers an automatic security review and may temporarily suspend the account; the Security Operations team (secops@internal.example) will contact you.

## MFA re-enrollment

You must re-enroll MFA when you get a new phone, lose your phone, or factory-reset your device.

### If you still have your old phone or a second registered method

1. Sign in to https://helpdesk.internal.example/mfa using the old/secondary method.
2. Choose **Add method** > register the new phone's authenticator app.
3. Set the new phone as default, then remove the old device entry.

### If you have no working MFA method

1. Call the Service Desk at **ext. 4357** (external: number on the intranet contact page) or visit the IT walk-up desk with your badge.
2. Complete identity verification (see below).
3. The Service Desk issues a **Temporary Access Pass (TAP)** valid for 1 hour, which lets you sign in and register the new authenticator at https://helpdesk.internal.example/mfa.
4. TAPs are single-use. If it expires before you finish, call back for a new one.

Manager email approval alone is NOT sufficient for MFA reset — identity verification is always required.

## Service Desk identity verification steps

To prevent social-engineering attacks, Service Desk agents must verify identity before any password or MFA reset performed on a caller's behalf. Expect to be asked for:

1. Full name and employee ID (found on your badge and in the HR portal, PeoplePoint).
2. A live video check against your badge photo, OR in-person badge presentation at the walk-up desk.
3. Confirmation of a one-time code sent to your **manager**, who must confirm the request is legitimate (used when video/walk-up is not possible).

Agents will NEVER ask for your current password. If anyone claiming to be IT asks for your password or an MFA code, refuse and report it per the Security Incident Runbook.

## Never share passwords

- Never share your password with anyone — including IT, your manager, or teammates. There is no legitimate business reason for anyone to know it.
- Never approve an MFA push you did not initiate. Unexpected pushes mean someone has your password: deny the prompt and immediately change your password at https://helpdesk.internal.example/reset, then report to secops@internal.example.
- Never reuse your company password on external websites.
- Shared team credentials for legacy systems must be stored in the approved password manager's shared vault, never in spreadsheets, chat, or email.

## When to escalate

Handle via self-service first; open a Helpdesk ticket (category: Security > Account Access) or call ext. 4357 when:

- SSPR fails with an error (screenshot it) or says your account is not eligible.
- Your account locks repeatedly with no failed attempts on your part after you have updated all saved passwords — request a lockout-source trace; Security can identify which device/IP is sending bad credentials.
- You are locked out AND have no working MFA method (call — a ticket cannot be opened without sign-in).
- You believe your password was phished, guessed, or exposed — this is a **security incident**: reset immediately, then follow the Security Incident Runbook and notify secops@internal.example. Mark the ticket severity High.
- A departed employee's account needs a reset for data access — this requires HR and manager approval and goes through the HR offboarding process, not a standard reset.

## Frequently asked questions

### I changed my password and now my phone keeps locking me out. Why?

Your phone's mail profile, Wi-Fi (CORP-WIFI stores credentials on some devices), and any app with a saved sign-in retry the OLD password automatically — five silent retries lock the account. Update or remove the saved password on every device immediately after a reset, starting with your phone.

### How do I change (not reset) a password I still know?

Press Ctrl+Alt+Del > "Change a password" on Windows, or use https://helpdesk.internal.example/reset and choose "I know my current password". Changing before expiry avoids the forced-change prompt at an inconvenient time.

### Are passphrases really allowed?

Yes, and encouraged. `correct-plum-radio-fence` style passphrases meet the 14-character minimum easily and are far easier to type on a phone than symbol-heavy strings. The complexity checker accepts hyphens and spaces.

### What is a Temporary Access Pass (TAP)?

A short-lived one-time code the Service Desk can issue after identity verification. It substitutes for MFA for a single sign-in so you can register a new authenticator. TAPs expire after 1 hour and cannot be reused.

### Does the Service Desk ever call me first about my password?

Rarely, and they will never ask for the password itself or an MFA code. If you receive an unsolicited "IT" call requesting credentials, hang up and report it to secops@internal.example — this is a common social-engineering pattern.

## Quick reference

| Item | Value |
|---|---|
| Reset portal | https://helpdesk.internal.example/reset |
| SSPR enrollment | https://helpdesk.internal.example/reset/enroll |
| MFA management | https://helpdesk.internal.example/mfa |
| Minimum length / history | 14 characters / last 10 remembered |
| Lockout | 5 failed attempts → 15-minute lock (auto-release) |
| Expiry | 365 days, reminders at 14/7/1 days |
| Service Desk | ext. 4357 |
| Security reports | secops@internal.example |
