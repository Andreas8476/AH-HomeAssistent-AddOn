# 01 — Overview

*[Deutsche Version](../de/01_ueberblick.md) (primary, authoritative)*

## Goal

A Home Assistant integration for the **ASKOHEAT+** PV heating element
(manufacturer [Askoma](https://www.askoma.com)) that reads its local,
unauthenticated REST API on the home network and, later, also controls it.

## Why a custom integration instead of an add-on

ASKOHEAT+ speaks a simple local REST/JSON API (no MQTT, no cloud dependency).
A dedicated **custom integration**
(`custom_components/askoheat_plus/`), installable via HACS/GitHub, is the
idiomatic way to do this — it runs directly inside the Home Assistant
process, creates native entities, and needs no separate Docker container.
Two integrations already present in the same Home Assistant setup solve
structurally the same problem (local device, polling, config flow) and
served as a model:

- [`goecharger_api2`](https://github.com/marq24/ha-goecharger-api2) — go-eCharger EV charger
- [`froeling_lambdatronic_modbus`](https://github.com/GyroGearl00se/ha_froeling_lambdatronic_modbus) — pellet heating system

## Phases

The project is deliberately laid out in steps:

1. **Phase 1 — Reading (this baseline)**: sensors/binary sensors showing the
   device's current state (heater step, power, temperature, status, errors).
   No write access.
2. **Phase 2 — Writing** *(shipped)*: setting heater step, load setpoint and
   feed-in value — via the manufacturer-documented inline commands, as
   `number` entities.
3. **Phase 3 — Dashboard** *(shipped)*: a dedicated Lovelace dashboard using
   Andreas' Askoma render images as a background with live values overlaid.

## Current status

- [x] Phase 1: integration with sensor and binary sensor entities, config
      flow via the UI, polling `gethome.json`.
- [x] Phase 2: control/writing — three `number` entities (target heater
      step, load setpoint, feed-in value) with a built-in keep-alive against
      the 60s auto-revert, plus an automation blueprint to link the feed-in
      value to a meter/inverter, see
      [05_entities.md](05_entities.md) and [10_automation.md](10_automation.md).
- [x] Phase 3: dashboard — a dedicated YAML Lovelace dashboard with two
      image cards (temperature sensors + heater load at the tank, feed-in
      value/load setpoint at the meter cabinet), see [11_dashboard.md](11_dashboard.md).

## Test environment

Local test device on Andreas' home network: `192.168.20.54` (the host is
freely configurable in the integration, not hardcoded).

## Further documents

See [docs/en/](.) — numbered, `02` starts with the API reference. German
original in parallel under [docs/de/](../de/) — German is the primary,
authoritative version; this translation may occasionally lag behind it.

## Author

Developed by Andreas Stegemann in collaboration with Claude (Anthropic,
Sonnet 5) as a coding assistant. A private project, not official ASKOMA AG
software — details see [README.md](../../../../README.md#author).
