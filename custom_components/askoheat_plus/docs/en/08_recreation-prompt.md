# 08 — Recreation prompt

*[Deutsche Version](../de/08_neuerstellungs-prompt.md) (primary, authoritative)*

This prompt summarizes context, decisions and architecture so that this
integration (phase 1 — reading) can be rebuilt from scratch even without the
original chat history. Just hand it over as a whole to an AI coding
assistant (e.g. Claude Code).

---

## Prompt (to copy)

> I run Home Assistant OS on a Raspberry Pi 5. I want to build a custom
> integration for my **ASKOHEAT+** PV heating element (manufacturer
> Askoma). The device has a local, unauthenticated REST API (JSON over
> HTTP, no cloud dependency).
>
> **Goal of this first phase:** only read data (sensors). Control (writing)
> and a dashboard with heating-element images are later, separate phases —
> do **not** implement them now.
>
> **Architecture:** a custom integration under
> `custom_components/askoheat_plus/`, HACS-compatible so it can later be
> published on GitHub and installed by anyone. No supervisor add-on. If
> present in the same Home Assistant setup, take existing integrations for
> other local devices with polling + config flow as a model (e.g. a
> go-eCharger or Modbus heating integration) for code style and HA
> conventions (`DataUpdateCoordinator`, `ConfigFlow`, `CoordinatorEntity`).
>
> **Folder structure:** everything — code AND a numbered project doc
> (`01_*.md`, `02_*.md`, ...) — in a single, self-contained folder that can
> later serve 1:1 as a git repo. Since Home Assistant custom integrations
> must live under `<config>/custom_components/<domain>/`, place the repo
> e.g. under `<config>/askoheat_plus/` (with `custom_components/askoheat_plus/`
> as a subfolder, README/LICENSE/hacs.json at repo root level) and mount it
> via a **symlink** at `<config>/custom_components/askoheat_plus`, so Home
> Assistant loads it immediately without duplicating code. The docs live
> directly in the integration folder
> (`custom_components/askoheat_plus/docs/de/`, with a complete English
> translation in parallel under `docs/en/` — German is the primary,
> authoritative version). **Code comments and docstrings throughout the
> Python code must be written in German**, regardless of the documentation
> language.
>
> **API endpoints:** for the regular poll, use **exclusively**
> `GET /gethome.json` (one request per cycle, default interval 30 seconds,
> configurable 10–300s). This endpoint already delivers device master data
> (`ASKOHEAT_PLUS_INFO.*`: article, serial number, versions, `DEVICEID`),
> live values (`ACTUAL_VALUES.*`), setpoints (`SET_INPUTS.*`) and
> status/relays (`STATUS_FLAGS.*`). **Important: don't overload the
> device's ESP32 controller with too many/too frequent requests** — hence
> deliberately only this one endpoint in the regular poll. Fetch four
> further endpoints (`getwizard.json`, `getwizard_status.json`,
> `gettemperature_calibration.json`, `getreg.json`) only **once at
> startup**, not repeatedly (deliberately leave fine-tuning the polling
> frequency for these open, see the changelog).
>
> Some fields are text with an appended unit (e.g. `"0 watts"`, `"25 °C"`)
> — read them via a generic regex number extractor, not via string
> splitting. `getreg.json` contains personal data (name, phone, email)
> under `USER_CONTACT`/`INSTALLER_CONTACT` — do **not** map these as an
> entity/recorder history, only use `EXTRA.*` (PV peak, battery size,
> buffer).
>
> **Technical patterns:**
> - `manifest.json`: `config_flow: true`, `integration_type: "device"`,
>   `iot_class: "local_polling"`, `requirements: []` (only HA's own
>   `aiohttp`).
> - Its own API client (`api.py`) using `async_get_clientsession(hass)`
>   (don't create/close your own session).
> - `AskoheatDataUpdateCoordinator(DataUpdateCoordinator[dict])`, map
>   errors to `UpdateFailed`.
> - `entry.runtime_data` for the coordinator (modern HA convention, not
>   `hass.data[DOMAIN][entry_id]`).
> - Config flow: ask for host (required), port (default 80), polling
>   interval (default 30s); on submit, test-fetch `gethome.json`, set
>   `DEVICEID` as `unique_id` (`async_set_unique_id` +
>   `_abort_if_unique_id_configured`).
> - Entities as declarative `EntityDescription` dataclass lists with a
>   `value_fn` that reads a JSON path, instead of one Python class per
>   sensor.
> - A central `DeviceInfo` on the coordinator (not duplicated per entity).
>
> **Entity scope (phase 1):** heater step, heater load (W), temperature
> (°C), temperature-limit info, target heater step, target feed-in value,
> device status, legionella-protection info, article/serial
> number/versions (diagnostic, disabled by default), precise temperature
> with calibration, TCP/RTU connection status, PV peak, battery size — as
> sensors. Pump active, emergency mode, heater locked, relay board
> connected, current flow — as binary sensors. Deliberately do NOT parse
> the free-text relay counters (`"off (1x on today) (saldo ...)"`)
> individually (too fragile for v1).
>
> **Docs (numbered, in the integration folder):** overview, API reference
> (incl. polling strategy/ESP protection), architecture, installation
> (HACS + manual + local dev symlink), entity reference table, development
> workflow, changelog, and this recreation prompt as the last document.
>
> Before writing code: check whether the target Home Assistant setup
> already has similar custom integrations (local device + polling + config
> flow) and adopt their code style/conventions where sensible. Ask if
> unclear: whether a custom integration or a real supervisor add-on is
> wanted, where the numbered docs should live, whether the available
> sample data comes from a real device or is only generic reference
> material, and which local IP address can be used for testing.

---

## Context useful for rebuilding (but not strictly part of the prompt)

- Source of the API structure: manufacturer docs "ASKOHEAT+ JSON" and
  "Askoheat+ Steuerung via REST API" (Askoma), plus a real sample dump of
  all endpoints from an actual device.
- Decisions came from three clarifying questions at the start: (1) custom
  integration vs. supervisor add-on, (2) where the docs should live, (3)
  real data vs. reference material.
- The endpoint focus on `gethome.json` + 4 secondary endpoints, as well as
  the note on protecting the ESP32, were added by the user afterward, after
  the original plan still called for `_values.json` + `getpar.json`.
