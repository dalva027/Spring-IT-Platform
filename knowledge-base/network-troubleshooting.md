---
title: Network Troubleshooting Guide
category: NETWORKING
tags: [wifi, ethernet, dns, connectivity, proxy]
---

# Network Troubleshooting Guide

This article covers "no internet", slow Wi-Fi, DNS problems, proxy settings, and office access-point roaming issues, plus the evidence the Network team needs when you escalate. Office wireless is **CORP-WIFI** (staff) and **CORP-GUEST** (visitors/personal devices).

## Quick triage: is it you, your device, or the network?

1. Check other devices on the same network. If your phone (on Wi-Fi, not cellular) also fails, the network/ISP is the likely cause.
2. Check other networks for your device: hotspot test. If your laptop works on a phone hotspot, the problem is the original network, not the laptop.
3. Check scope with colleagues nearby (office) or the IT status page at https://intranet.internal.example/it-status. Multiple users affected = report as outage, skip individual troubleshooting.

## No internet at all

1. Confirm the physical basics: Wi-Fi toggle on, airplane mode off, ethernet cable clicked in at both ends, dock power connected.
2. Look at the network icon state:
   - "No networks found" → adapter/driver issue: reboot; if persistent, reinstall the Wi-Fi driver from Software Center.
   - Connected but "No internet" → continue below.
3. Restart the machine (resolves the majority of adapter and stack issues).
4. Renew your address and flush DNS:
   - Windows: `ipconfig /release` then `ipconfig /renew` then `ipconfig /flushdns`
   - macOS: toggle Wi-Fi off/on; flush DNS with `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
5. Windows only: `netsh winsock reset` then reboot, if the stack appears corrupted (all apps fail but ping works).
6. Home users: power-cycle modem and router (off 30 seconds). Office users: do NOT reboot office network gear — report it instead.

## Ethernet vs Wi-Fi isolation steps

When performance or connectivity is flaky, isolate which path is at fault:

1. If docked, test with the ethernet cable directly in the laptop (bypassing the dock). Docks are a very common hidden cause of "network" problems.
2. Disable Wi-Fi while testing ethernet (and vice versa) so Windows cannot silently switch interfaces mid-test: Settings > Network > Wi-Fi off.
3. Compare results:
   - Ethernet good, Wi-Fi bad → wireless problem (see Slow Wi-Fi / roaming below).
   - Both bad on one machine, others fine → local device (drivers, security agent, proxy).
   - Both bad on multiple machines → upstream network; escalate as outage.
4. Try a different ethernet cable and wall port before blaming anything else — cables fail more often than switches.

## Slow Wi-Fi

1. Check the basics: distance to the access point, microwave ovens, metal cabinets, and USB-3 devices next to the laptop (they radiate in the 2.4 GHz band).
2. Confirm you are on **CORP-WIFI**, not CORP-GUEST — guest is rate-limited by design and blocks internal resources.
3. Forget and rejoin the network: Settings > Wi-Fi > Manage known networks > CORP-WIFI > Forget, then reconnect (re-authenticates and often lands you on a better band).
4. Check the link: Windows `netsh wlan show interfaces` — note **Signal** (want >60%) and **Receive rate**. macOS: Option-click the Wi-Fi menu icon for RSSI (want better than -67 dBm) and Tx Rate.
5. Run a quick throughput sanity check, then test the same thing on ethernet to quantify the difference.
6. Home Wi-Fi: prefer the 5 GHz band, move the router off the floor/out of cabinets, and reboot it weekly. GlobalConnect VPN adds some overhead but should not halve your speed — if it does, see the MTU section of the VPN Access Guide.

## DNS problems

Symptoms: "server not found" errors while ping to an IP (e.g., `ping 1.1.1.1`) works.

1. Flush the cache (commands in "No internet" above).
2. Test resolution explicitly: `nslookup intranet.internal.example`. Note which DNS server answered.
3. Internal names (`*.internal.example`) only resolve on the office network or over VPN — off-VPN failures for internal names are expected behavior, not an outage.
4. Do NOT hard-code public DNS (8.8.8.8 etc.) on a company laptop — it breaks internal resolution and split-tunnel VPN. Remove any manual DNS entries: adapter settings should be "Obtain DNS automatically".
5. If one specific site fails to resolve for everyone, report it with the `nslookup` output.

## Proxy settings

Company laptops receive proxy configuration automatically. Misconfigured manual proxies cause "browser fails but ping works" symptoms.

1. Windows: Settings > Network & Internet > Proxy → "Automatically detect settings" ON, manual proxy OFF (unless the intranet proxy page for your region says otherwise).
2. macOS: System Settings > Network > (adapter) > Details > Proxies → only Auto Proxy Discovery checked, unless regionally directed.
3. Command-line tools honor separate settings: check `HTTP_PROXY`/`HTTPS_PROXY` environment variables and `git config --global --get http.proxy` if browsers work but git/npm/pip fail.
4. Never install third-party "proxy switcher" tools; they conflict with the security agent.

## Office AP roaming issues

Symptoms: video calls drop or freeze when walking between rooms; connection stalls for 10–30 seconds in specific spots, then recovers.

1. Note the exact locations where drops occur (room names/desk numbers) — the Network team maps these to specific access points.
2. Update the Wi-Fi driver from Software Center; old drivers roam poorly ("sticky client" behavior, clinging to a distant AP).
3. Windows advanced tweak (only if directed by IT): Device Manager > Wi-Fi adapter > Advanced > set **Roaming Aggressiveness** to Medium-High.
4. As a meeting-saving workaround, toggling Wi-Fi off/on forces reconnection to the nearest AP.
5. Persistent dead zones or roaming drops are infrastructure issues — escalate with locations and timestamps; do not just live with it.

## Evidence to collect before escalating

Attach these to your ticket — they cut resolution time dramatically:

1. `ping -n 20 10.0.0.1` (Windows; use your gateway from `ipconfig`) — shows local loss/latency. macOS: `ping -c 20 <gateway>`.
2. `ping -n 20 intranet.internal.example` — internal path.
3. `tracert intranet.internal.example` (Windows) or `traceroute` (macOS) — where the path breaks; capture even if it completes.
4. `ipconfig /all` output (Windows) or `ifconfig` + Wi-Fi details (macOS).
5. Timestamps of failures, location (office room / home / hotel), connection type (Wi-Fi/ethernet/dock), and whether VPN was up.

Paste text output rather than screenshots where possible.

## When to escalate

Open a Helpdesk ticket at https://helpdesk.internal.example (category: Networking) when:

- Multiple users or an entire office area are affected — call the Service Desk (ext. 4357) instead of just ticketing; this is treated as an outage.
- Your device fails on ethernet AND Wi-Fi in the office while colleagues work normally, after a reboot and driver update (possible port/switch or device certificate issue).
- Traceroute shows loss beginning at a specific internal hop consistently.
- Roaming drops recur in the same office locations (include the location list).
- A wall port is physically damaged or dead (include the port label, e.g., `3F-B-114`).

Severity: whole-team outage = Critical (call). Single user hard-down = High. Slow-but-working = Medium with evidence attached.

## Frequently asked questions

### Why does CORP-GUEST work but CORP-WIFI does not?

CORP-WIFI authenticates your device certificate; CORP-GUEST is an open captive portal. If only CORP-WIFI fails, your device certificate is likely expired or the machine has fallen out of management — reboot on ethernet (or hotspot + VPN) for an hour so it can renew, then retry. Persistent failure needs a Helpdesk ticket (category: Networking > Wireless) noting "cert/auth failure".

### Should visitors use CORP-GUEST?

Yes — CORP-GUEST is for visitors and personal devices. The daily access code is available at reception. Never share your CORP-WIFI credentials or plug visitor devices into wall ports.

### Is it OK to use my own router or switch at my desk?

No. Personal network equipment (routers, unmanaged switches, Wi-Fi extenders) in the office is prohibited — rogue devices trigger port shutdowns by the network access control system. If you need more ports at a desk, request them via the Helpdesk.

### My network drops exactly when the VPN connects.

That points at the tunnel, not the LAN — see the MTU and IKEv2/SSL sections of the VPN Access Guide before filing a network ticket.

### What is an acceptable speed in the office?

Wired desks should see near line-rate to internal services; Wi-Fi varies with occupancy but sustained sub-20 Mbps on CORP-WIFI with good signal is worth reporting with the evidence set above.

## Quick reference

| Item | Value |
|---|---|
| Office SSIDs | CORP-WIFI (staff, cert-based), CORP-GUEST (visitors, rate-limited) |
| Status page | https://intranet.internal.example/it-status |
| DNS flush (Windows) | `ipconfig /flushdns` |
| DNS flush (macOS) | `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder` |
| Evidence set | ping to gateway, ping to intranet, tracert/traceroute, ipconfig /all, timestamps |
| Tickets | https://helpdesk.internal.example (Networking); outages: call ext. 4357 |
