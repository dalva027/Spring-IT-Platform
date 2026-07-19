---
title: Printers and Peripherals Troubleshooting
category: IT
tags: [printer, badge-release, dock, monitor, usb]
---

# Printers and Peripherals Troubleshooting

This article covers office printing (including badge-release "PrintAnywhere" printers), driver problems, stuck print queues, and the most common monitor, docking station, and USB device issues.

## Office printing overview

- Office floors use shared multifunction printers on the **PrintAnywhere** badge-release system: you print to a single queue and release the job at ANY printer by tapping your badge.
- The universal queue is installed by default on company laptops as **"PrintAnywhere (Follow-Me)"**. If missing, install it from Software Center (Windows) or Self Service (macOS) — search "PrintAnywhere".
- Direct-to-device queues (e.g., `PRN-3F-EAST`) exist for label/specialty printers only; normal documents should always go to the Follow-Me queue.
- Jobs held in the Follow-Me queue expire after **8 hours** if not released.

## Printer shows "Offline"

1. Check the physical printer: powered on, no error on its panel (paper jam, toner door open), network cable attached. Fix trivial issues (paper, jams per the on-screen guide) yourself; toner cartridges are in the supply cabinet near each print station.
2. On your machine, confirm you are on the office network or VPN — the print system is internal-only. Printing fails silently off-VPN.
3. Windows: Settings > Bluetooth & devices > Printers & scanners > select the printer > make sure "Use Printer Offline" is NOT enabled (Printer menu in the queue window).
4. Restart the local print spooler:
   - Windows: Win+R > `services.msc` > right-click **Print Spooler** > Restart. (Or admin PowerShell: `Restart-Service Spooler`.)
   - macOS: System Settings > Printers & Scanners > right-click the printer list > "Reset printing system" (re-add PrintAnywhere from Self Service afterward).
5. Send a fresh test page. If YOUR queue is fine but the physical device is faulted, report the device (see escalation) — do not troubleshoot printer hardware beyond jams and paper.

## Clearing a stuck print queue

Symptoms: jobs stuck at "Spooling"/"Error – Printing", nothing prints, deleting the job does nothing.

### Windows

1. Open the queue (Settings > Printers & scanners > printer > Open print queue) and Cancel All Documents. Wait 30 seconds.
2. If jobs will not delete: stop the spooler and purge manually —
   1. Admin PowerShell: `Stop-Service Spooler`
   2. Delete all files in `C:\Windows\System32\spool\PRINTERS`
   3. `Start-Service Spooler`
3. Reprint the document. Very large or corrupted PDFs are the usual cause — try "Print as image" in the PDF viewer's advanced print dialog for stubborn files.

### macOS

1. Open the printer queue from System Settings > Printers & Scanners, select the stuck job, and delete it.
2. If the queue is wedged, pause and resume the printer, or "Reset printing system" as a last resort.

## Driver reinstall

Use when printing produces garbage characters, blank pages, wrong paper sizes, or the queue errors immediately on every job.

1. Remove the printer: Settings > Printers & scanners > select > Remove (macOS: minus button).
2. Windows: also remove the old driver — Win+R > `printmanagement.msc` > Drivers, or Settings > Printers & scanners > Print server properties > Drivers > remove the PrintAnywhere driver package.
3. Reboot.
4. Reinstall "PrintAnywhere" from Software Center / Self Service. Do NOT download drivers from vendor websites — the managed package contains the correct badge-release configuration.
5. Print a test page and release it at the nearest printer.

## Badge-release (PrintAnywhere) issues

1. **Badge tap does nothing / "Card not recognized"**: your badge may not be linked yet. At the printer panel choose **Login with PIN**, sign in with company credentials once, and tap the badge when prompted to associate it. Future taps will work.
2. **Job not listed at the printer**: confirm the job went to "PrintAnywhere (Follow-Me)" and not a direct queue (check the printer name in the app's print dialog); remember jobs expire after 8 hours.
3. **Job listed but prints elsewhere or not at all**: the device may have a stuck engine — tap Release at a different printer (any floor works) and report the faulty one.
4. **New/replacement badge**: the link follows your account after you do the PIN login once with the new badge.
5. Secure documents: jobs only print while you stand at the device — but collect immediately; abandoned confidential printouts are a security policy violation.

## Monitor issues

1. No signal: reseat both ends of the video cable; try the other port on the dock; power-cycle the monitor.
2. Detected but black / flickering: swap the cable (spares in the supply cabinet) — flicker is a cable or dock issue far more often than a monitor fault.
3. Wrong resolution or scaling: Windows Settings > Display > set native resolution; update graphics driver via Software Center if native is not offered.
4. Only one of two monitors works on a dock: check the dock's supported lane configuration — some docks limit resolution with two monitors over USB-C; update dock firmware from Software Center ("Dock Firmware Utility").

## Docking station issues

Docks cause a large share of "laptop", "network", and "monitor" tickets. Golden rule: reproduce the problem without the dock before blaming anything else.

1. Full power cycle: unplug the dock from power AND laptop for 60 seconds, reconnect power first, then the laptop.
2. Use the laptop's charging-capable port (usually left-rear USB-C) — wrong ports cause "connected, not charging" and dropped peripherals.
3. Update dock firmware via the "Dock Firmware Utility" in Software Center; most random disconnect complaints are fixed by firmware.
4. If peripherals drop when the laptop lid closes, check Windows power settings: Control Panel > Power Options > "Choose what closing the lid does" > When plugged in: Do nothing.
5. A dock that is hot to the touch and rebooting itself is failing hardware — request a swap.

## USB device issues

1. Try a different port, then a different cable, then another computer — this three-step isolates device vs port vs machine in under two minutes.
2. Prefer ports directly on the laptop over dock/hub ports for problem devices (webcams and audio devices are bandwidth-sensitive).
3. Windows Device Manager: entries with a yellow warning under USB controllers — right-click > Uninstall device, then unplug/replug to redetect.
4. Unknown or found USB storage devices must NOT be plugged in — hand them to Security (see the Security Incident Runbook).
5. Personal USB storage is blocked by policy on company laptops; use the approved cloud storage for file transfer. The block is expected behavior, not a fault.

## When to escalate

Open a Helpdesk ticket at https://helpdesk.internal.example (category: IT > Printing or IT > Hardware):

- Physical printer faults beyond paper/jams/toner: error codes on the panel, grinding noises, repeated jams in the same spot — include the printer's asset label (e.g., `PRN-3F-EAST`) and the panel error code.
- Printing fails for MULTIPLE people on a floor — likely the print server or the device; call ext. 4357 and report the location so a technician is dispatched.
- Badge release fails at every printer after the PIN-association step (account/badge sync issue).
- Driver reinstall done and output is still corrupted (attach a photo of the output and the document type).
- Failing docks, monitors, or peripherals after the isolation steps above — hardware swaps are fulfilled from floor stock, usually same day; include your asset tag and desk location.
- Anything involving a found/suspicious USB device — that goes to Security (ext. 7233), not the Helpdesk.

## Frequently asked questions

### Can I print from my phone or personal laptop?

No. PrintAnywhere only accepts jobs from managed devices on the internal network. From a phone, email the document to yourself and print from your laptop, or use the web-upload page at https://intranet.internal.example/print (managed accounts only, PDF/Office files up to 50 MB).

### How do I print in color or on A3/tabloid?

The Follow-Me queue defaults to duplex grayscale to reduce waste. Choose color or large paper in the print dialog's Properties/Presets before printing; the release station shows the job's finishing options before you confirm. Color volume is reported per department — use it when it matters, not by default.

### Can I get a personal desktop printer?

Only with a business justification approved by your department head (e.g., HR handling confidential physical documents). Personal printers are otherwise not supported or supplied; the badge-release fleet is the standard.

### Scanning and copying

All PrintAnywhere devices scan to your own email address ("Scan to Me" appears after badge tap) — scans to your own address need no setup. Scan-to-folder destinations for teams are requested via Helpdesk (IT > Printing > Scan Destination).

### Working from home — can I use my home printer?

Home printers on personal networks are outside IT support, but nothing blocks connecting one directly via USB. Confidential documents must not be printed at home unless your role has a documented exception — check the data handling policy on the intranet.

### My laptop has too few ports. Can I get a hub?

USB-C hubs and adapters are standard-peripheral items — request via Helpdesk (IT > Hardware Request) with no approval needed, or collect from floor stock at the IT walk-up desk.

## Quick reference

| Item | Value |
|---|---|
| Badge-release system | PrintAnywhere — queue "PrintAnywhere (Follow-Me)" |
| Job retention | 8 hours, then auto-deleted |
| First badge use | Login with PIN once at the panel, then tap to associate |
| Spooler purge (Windows) | Stop Spooler service, clear `C:\Windows\System32\spool\PRINTERS`, start service |
| Driver source | Software Center / Self Service ONLY (never vendor sites) |
| Dock firmware | "Dock Firmware Utility" in Software Center |
| Support | https://helpdesk.internal.example (IT > Printing / Hardware), ext. 4357 |
