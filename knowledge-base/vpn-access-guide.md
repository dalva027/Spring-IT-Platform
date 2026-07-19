---
title: VPN Access Guide (GlobalConnect)
category: NETWORKING
tags: [vpn, globalconnect, remote-access, split-tunneling, connectivity]
---

# VPN Access Guide (GlobalConnect)

This article covers installing, configuring, and troubleshooting the company VPN client, **GlobalConnect**. All remote employees must connect through GlobalConnect to reach internal resources such as the intranet (https://intranet.internal.example), file shares, and internal development environments.

## Who needs VPN access

- All remote and hybrid employees accessing internal systems.
- Contractors with an approved access request (submitted by their manager via the Helpdesk portal at https://helpdesk.internal.example).
- On-site employees generally do NOT need VPN while on the CORP-WIFI network.

## Installing the GlobalConnect client

### Windows

1. Open the Software Center (Start menu > "Company Software Center").
2. Search for **GlobalConnect VPN** and click Install.
3. Reboot when prompted.
4. Launch GlobalConnect from the system tray and enter the gateway address: `vpn-east.internal.example` (Americas/EMEA) or `vpn-west.internal.example` (APAC).
5. Sign in with your company email and password, then approve the MFA push notification.

### macOS

1. Open **Self Service** from the Applications folder.
2. Install **GlobalConnect VPN** from the "Network" category.
3. When macOS prompts "GlobalConnect would like to add VPN configurations", click **Allow**. If you miss this prompt, go to System Settings > Privacy & Security and approve the extension.
4. Enter the gateway address and sign in with company credentials + MFA.

## Split tunneling behavior

GlobalConnect uses **split tunneling** by default:

- Traffic to internal ranges (10.0.0.0/8, `*.internal.example`) goes through the VPN tunnel.
- General internet traffic (streaming, personal browsing) goes directly out your home connection.

Implications:

- Speed tests run outside the tunnel and do not reflect VPN performance.
- Internal DNS names only resolve while connected.
- Do not manually change proxy or DNS settings to "fix" split tunneling; this breaks internal name resolution. If a specific internal site fails, open a Helpdesk ticket instead.

## Common disconnect causes and fixes

### 1. Wi-Fi power saving (most common on laptops)

Windows may power down the Wi-Fi adapter during idle periods, dropping the tunnel.

1. Open Device Manager > Network adapters > your Wi-Fi adapter > Properties.
2. On the **Power Management** tab, uncheck "Allow the computer to turn off this device to save power".
3. In Control Panel > Power Options > Change plan settings > Advanced, set **Wireless Adapter Settings > Power Saving Mode** to "Maximum Performance".
4. Reboot and retest.

### 2. MTU issues (connects, then pages hang or large transfers stall)

Symptoms: VPN shows connected, small pages load, but large files, video calls, or Git pushes stall.

1. Test with: `ping -f -l 1350 intranet.internal.example` (Windows) or `ping -D -s 1350 intranet.internal.example` (macOS).
2. If 1350 succeeds but 1450 fragments/fails, you likely have an MTU problem on your home network.
3. Lower your home router MTU to 1400, or ask the Service Desk to apply the "low-MTU" GlobalConnect profile to your account.

### 3. IKEv2 vs SSL fallback

GlobalConnect prefers **IKEv2 (UDP 500/4500)** for performance and falls back to **SSL/TLS (TCP 443)** when UDP is blocked.

- If your connection is stable but slow, check the client's "Tunnel Type" indicator. "SSL" means UDP is being blocked (common on hotel/café/guest networks and some ISP routers).
- To force SSL mode temporarily: GlobalConnect > Settings > Transport > "Prefer SSL". Revert to Auto when back on a normal network.
- Repeated silent drops every few minutes on IKEv2 often indicate a NAT timeout on the home router; forcing SSL is a valid workaround.

### 4. Home router issues

1. Reboot the router and modem (power off 30 seconds).
2. Disable "SIP ALG" and any "VPN passthrough inspection" features if present; they frequently corrupt IKEv2 traffic.
3. If double-NAT is in play (ISP modem/router + your own router), put the ISP device in bridge mode.
4. Test from a phone hotspot: if VPN is stable on hotspot but not home Wi-Fi, the issue is the home network, not the company VPN.

### 5. Stale client or certificate

1. Check GlobalConnect > About. Minimum supported version is listed on the intranet VPN page.
2. Update via Software Center / Self Service.
3. If you see "certificate invalid" errors, select **Refresh Credentials** in the client menu, or reboot. Persistent certificate errors require a Helpdesk ticket.

## Collecting logs before opening a ticket

1. Reproduce the problem (attempt a connection or wait for a drop).
2. In GlobalConnect: gear icon > **Troubleshooting** > **Collect Logs**. This creates a `.zip` on your Desktop (e.g., `GlobalConnect-Logs-<date>.zip`).
3. Note the timestamp of the failure, your location/network (home, hotel, hotspot), and tunnel type (IKEv2 or SSL).
4. Attach the zip and details to your Helpdesk ticket at https://helpdesk.internal.example.

## When to escalate

Open a ticket in the Helpdesk portal (category: Networking > VPN) and include logs when:

- You cannot sign in at all and password + MFA work fine on other services (possible account/VPN entitlement issue).
- Disconnects persist after completing the power-saving, router, and hotspot isolation steps above.
- You see "Maximum sessions reached" or gateway errors referencing capacity.
- Multiple colleagues in your region report simultaneous failures — report it as a possible outage so the Network team (via Service Desk, ext. 4357) can check gateway health.

Severity guidance: total inability to work remotely = High; intermittent drops with workaround (SSL mode/hotspot) = Medium.

## Frequently asked questions

### Do I need VPN while in the office?

No. On CORP-WIFI or a wired office port you reach internal resources directly. GlobalConnect detects the office network and shows "Internal network — tunnel not required". Leaving it connected in the office is harmless but adds latency.

### Can I use the VPN on my personal computer?

No. GlobalConnect performs a device posture check and only permits company-managed devices with the endpoint security agent installed. Personal-device access to email is available through the browser at https://mail.internal.example without VPN.

### Does the VPN slow down my video calls?

Company video conferencing traffic is excluded from the tunnel by the split-tunnel policy, so calls take your direct home path. If calls degrade only when the VPN is up, collect logs and open a ticket — that is not expected behavior.

### How long can I stay connected?

Sessions last up to 12 hours, after which you must re-authenticate with MFA. Idle sessions disconnect after 2 hours.

### Can I connect from abroad?

Yes, from most countries; a small embargoed-country list is blocked at the gateway. For business travel to restricted regions, request a travel exception through the Helpdesk (category: Security > Travel) at least 5 business days in advance.

## Quick reference

| Item | Value |
|---|---|
| Client name | GlobalConnect (Software Center / Self Service) |
| Gateways | vpn-east.internal.example, vpn-west.internal.example |
| Transports | IKEv2 (UDP 500/4500) preferred, SSL (TCP 443) fallback |
| Session length | 12 h max, 2 h idle timeout |
| Log collection | Gear icon > Troubleshooting > Collect Logs |
| Support | https://helpdesk.internal.example, Service Desk ext. 4357 |
