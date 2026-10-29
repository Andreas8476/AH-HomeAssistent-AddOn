# 14 — Community & outreach

*[Deutsche Version](../de/14_community.md) (primary, authoritative)*

Where the project was presented, what text was used there and where it is
listed as a directory entry. Simply add new forums/platforms to the table and
as a section of their own below it.

## Overview

| Where | Link | Date | Status |
|---|---|---|---|
| Home Assistant Community Forum (English), category "Share your Projects → Custom Integrations" | <https://community.home-assistant.io/t/askoheat-askoma-pv-heating-element-custom-integration-local-no-cloud/1030960> | 2026-10-29 | published, no replies yet (as of publication) |
| HACS default store (listing requested) | <https://github.com/hacs/default/pull/12952> | 2026-10-29 | pull request open, waiting for review by the HACS maintainers |

Further planned places (not done yet): German-language Home Assistant forum,
photovoltaic forums (heating element/self-consumption section), a note to
Askoma asking them to link the project.

## Who answers, where?

- **Bugs and wishes:** preferably as an issue on GitHub
  (<https://github.com/Andreas8476/AH-HomeAssistent-AddOn/issues>).
- **Forum and pull request:** check regularly for questions and answer
  there. Don't change the pull request at `hacs/default` while it is running.
- **For bugs/improvement requests coming from replies:** fix in the repo,
  publish a new release (see [13_updating.md](13_updating.md)).

## Home Assistant Community Forum (English)

- **Title:** `ASKOHEAT+ (Askoma PV heating element) custom integration – local, no cloud`
- **Category:** Share your Projects → Custom Integrations
- **Tags:** energy, custom-template, heater
- **Attached images:** `HA_AH_Ausschnitt_Dashboard.png`,
  `HA_AH_Ausschnitt_Einstellungen.png` (from `product_pics/`)
- **Note on the text:** it states that the integration was developed with
  the help of Claude (AI assistant) — identical to the README.

Published text (as of 2026-10-29, v0.10.1):

```markdown
Hi everyone,

I built a custom integration for the **ASKOHEAT+ PV heating element by Askoma** and wanted to share it. It talks directly to the device over its local interface, so no cloud is needed.

**What it can do**
- Read all values: temperatures (sensors 0–4), heating power, heater step, status and errors
- Control: heater step, load setpoint, feed-in value, emergency mode
- Link the feed-in value or load setpoint to your meter or inverter sensor without any automation. You can pick the source right in the dashboard.
- Configure all temperature functions of the device's web UI from Home Assistant: heat pump request, minimum temperature, low tariff, feed-in value, load setpoint, heater step, legionella protection (switches, temperatures, time windows, sensor selection)
- Ready-made dashboard with images of the heating element and history graphs, generated automatically per device
- Several devices at once

**Installation:** via HACS as a custom repository (step-by-step guide in the repo, also for beginners). HACS shows updates as usual. I have also submitted it for the HACS default store.

**Tested** with two devices (a flange heater with 19 stages and a 5.2 kW variant). I would be especially happy about feedback from other models.

Repo, docs and screenshots: https://github.com/Andreas8476/AH-HomeAssistent-AddOn

The documentation is available in German and English. The integration was developed with the help of Claude (an AI assistant).

Questions, bugs and wishes are welcome here or as an issue on GitHub.
```

## German text (for German forums, not published yet)

**Title:** `ASKOHEAT+ (Askoma PV-Heizstab) in Home Assistant – lokal, ohne Cloud`

The German text is in [the German version of this document](../de/14_community.md#deutschsprachiger-text-für-deutsche-foren-noch-nicht-veröffentlicht).

## HACS default store

> [!IMPORTANT]
> Leave the pull request at `hacs/default` **unchanged** until the maintainers have decided, and
> answer any questions there.

- **Pull request:** <https://github.com/hacs/default/pull/12952> (entry
  `Andreas8476/AH-HomeAssistent-AddOn` in the file `integration`).
- **Submitted:** 2026-10-29, with release v0.10.1 (created after the first
  green runs of the HACS action and hassfest, as the template requires).
- **Next:** review by the HACS maintainers, turnaround not predictable. Once
  accepted, ASKOHEAT+ appears directly in the HACS search without adding a
  custom repository — then simplify [04_installation.md](04_installation.md)
  accordingly.

## Adding a new place (template)

```markdown
## <Name of the platform>

- **Link:** <URL>
- **Date:** <YYYY-MM-DD>
- **Category/tags:** …
- **Notes:** (rules of the platform, attached images, …)
- **Text:** (paste the published text here)
```
