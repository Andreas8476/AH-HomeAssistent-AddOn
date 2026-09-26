# 02 — API reference

*[Deutsche Version](../de/02_api-referenz.md) (primary, authoritative)*

Source: manufacturer docs "ASKOHEAT+ JSON" and "Askoheat+ Steuerung via REST
API" (Askoma Confluence export, handed to the project as an attachment), plus
a real sample dump of all endpoints from one of Andreas' own devices
(`b4:8a:0a:49:5b:9c`, IP `.53` in the dump; the test device for this
integration is `192.168.20.54`).

For the meaning of the individual bits in the status/error fields
(`MODBUS_VAL_STATUS`, `MODBUS_VAL_STATUS_EXTENDED`, `MODBUS_VAL_ERROR_STATUS`,
...) see the dedicated reference [09_modbus-status-flags.md](09_modbus-status-flags.md)
(source: official Modbus register documentation).

Basics: all endpoints are plain, **unauthenticated** `GET` requests to
`http://<host>/<endpoint>`, response is JSON. There are dozens of endpoints
(`getall.json`, `_values.json`, `getcon.json`, `getsenec.json`, ...) — this
integration deliberately uses only a subset, see below.

## Polling strategy (protecting the ESP32)

The ASKOHEAT+ runs on an ESP32. The device's own web UI polls its "home" page
every 2 seconds according to the manufacturer docs — so that's the reference
point for "safe". This integration is deliberately much more conservative:

| Endpoint | Use | Interval |
|---|---|---|
| `gethome.json` | Main poll: device master data + live values + setpoints + status/relays in one response | Coordinator interval, default **30s**, configurable 10–300s |
| `getwizard_status.json` | Connection diagnostics (TCP/RTU/SENEC/SMA) | once at setup |
| `gettemperature_calibration.json` | precise temperature values (2 decimal places) + calibration offsets | once at setup |
| `getreg.json` | installation data (`EXTRA.*`: PV peak, battery size, buffer storage) | once at setup |
| `getwizard.json` | full config dump (large) — reference/diagnostics | not fetched automatically in phase 1 |

**Open point:** the four secondary endpoints are currently loaded only once
when the integration starts, not repeated. Whether/how often they should be
re-fetched (e.g. on reconnect, or their own slow interval of, say, 15–30
minutes) is deliberately not yet decided — see
[07_changelog.md](07_changelog.md).

## Why exactly these 5 endpoints

Scoped down at Andreas' request, because `gethome.json` (the data source for
the device's own "Home" page) already contains almost everything needed for
an overview — and the remaining four each deliver targeted extra info that
`gethome.json` doesn't have (calibration, connection diagnostics, installation
metadata, full raw configuration).

## `gethome.json` — structure (excerpt, relevant fields)

```
TYPE
ASKOHEAT_PLUS_INFO.
    DEVICEID                  # MAC-style ID, used as unique_id
    ARTICLE_NAME / ARTICLE_NUMBER / SERIAL_NUMBER
    HARDWARE_VERSION / SOFTWARE_VERSION
    HEATER_1_POWER..HEATER_6_POWER, NUMBER_OF_STEPS, NUMBER_OF_HEATER, MAX_POWER
    ERROR_STATUS               # "fine" or an error text
    LEGIO_INFO                 # "disabled" or a status text
ACTUAL_VALUES.
    ACTUAL_HEATER_STEP         # current heater step (number)
    ACTUAL_HEATER_LOAD         # current power in watts (plain number)
    ACTUAL_HEATER_LOAD_WATTS   # same info as text ("0 watts")
    ACTUAL_TEMPERATURE_LIMIT   # text, e.g. "none (current 25 °C)"
    TEMP_SENSOR_0..4           # text with unit, e.g. "25 °C" / "not connected"
    PUMP_OUTPUT                # "active" / "not active"
SET_INPUTS.
    SET_HEATER_STEP, SET_LOAD_SETPOINT, SET_LOAD_FEEDIN   # setpoints (relevant to phase 2)
STATUS_FLAGS.
    ERROR, EMERGENCY_MODE, HEATER_DISABLED, RELAYBOARD_CONNECTED, CURRENT_FLOW, ...
    HEATER_1_RELAY..HEATER_6_RELAY   # free text "off (1x on today) (saldo +135393 used 0)"
```

Fields like `"0 watts"`, `"25 °C"` are **text with an appended unit** — the
integration reads them via a generic number extractor
(`api.extract_number`, regex `-?\d+(?:[.,]\d+)?`), not via string splitting.

## Setting values (inline commands, implemented since phase 2)

Since firmware 4.6.2, values can be set via GET on a URL-encoded JSON
structure, e.g. `curl 'http://askoheat.local/%7B%22MODBUS_CMD_SET_HEATER_STEP%22:%223%22%7D'`
(equivalent to `{"MODBUS_CMD_SET_HEATER_STEP":"3"}`). This integration
instead uses the more legible path endpoints with a query parameter
recommended in the manufacturer docs ("Askoheat+ Steuerung via REST API",
section "Hilfsmittel zur Installation") — less fragile than URL-encoded JSON
in the path:

| Number entity | Endpoint | Equivalent to |
|---|---|---|
| Target heater step | `heater%20step?value=x` | `MODBUS_CMD_SET_HEATER_STEP` |
| Load setpoint | `load%20setpoint?value=nnn` | `MODBUS_CMD_LOAD_SETPOINT_VALUE` |
| Feed-in value | `load%20feedin?value=nnn` | `MODBUS_CMD_LOAD_FEEDIN_VALUE` |

Implemented in `api.py` (`AskoheatApiClient.async_send_command`) and
`number.py` (`AskoheatNumber.async_set_native_value`).

There are also **parameter-less** commands that correspond exactly to the
physical button on the device — no `?value=`, no 60s revert (the device
keeps the state until the next press, like a real button):

| Switch entity | Endpoint (on) | Endpoint (off) |
|---|---|---|
| Emergency mode | `on` | `off` |

Implemented in `api.py` (`AskoheatApiClient.async_send_bare_command`) and
`switch.py` (`AskoheatSwitch`).

**Important — automatic revert after 60 seconds, prevented via keep-alive:**
according to the manufacturer docs, the Askoheat+ automatically clears a
value set this way after 60 seconds if it isn't resent by a (or another)
controlling device — the device **explicitly expects** a continuously
controlling device. Unlike read polling (see "Polling strategy" above),
periodically resending here is manufacturer-intended behavior, not an extra
risk for the ESP32.

Each number entity (`number.py`) therefore remembers the last value it sent
and automatically resends it via `async_track_time_interval` every
`NUMBER_KEEPALIVE_INTERVAL` (default **45 seconds**, safely under the 60s
window) — for as long as the value is `≠ 0`. If the value is set to `0` (or
the entity is removed/the integration unloaded), the keep-alive stops
immediately. A value set through Home Assistant therefore stays active until
explicitly changed — no manual repetition/automation needed just to keep it
alive. For the automatic **source** of the feed-in value (e.g. from a
meter/inverter) see [10_automation.md](10_automation.md).

Value ranges of the number entities: target heater step `0`–`NUMBER_OF_STEPS`
(dynamic from the device, fallback 19), load setpoint `0`–`MAX_POWER`
(dynamic, fallback 20000 W), feed-in value `-32768`–`32767` (int16 range,
negative = feed-in/surplus, positive = draw).

## Writing installer settings (`POST /server1/`, since phase 4)

Settings other than the three inline commands above (legionella protection,
low tariff, feed-in window, heat pump request, auto heater-off, auto
reboot — the same fields also returned by `getwizard.json` and shown by the
device's own web UI under `extended.html`) are **not** set via the inline
command endpoints, but through a separate POST endpoint.

Found by analyzing the device's own JavaScript files (`Jbootloader.js`:
`xBASEURL="/server1/"`; `Jxfunc.js`:
`sendBatchChanges`/`sendPayloadOnce`/`sendDataOnly`) and **verified live
against the test device** (with Andreas' explicit authorization, since `.54`
is his test device):

```
POST http://<host>/server1/
Content-Type: application/json
Body: {"<WIZARD_KEY>": "<VALUE>"}
```

Confirmed behavior:

- **Pure merge, no replace:** only the keys given in the body change, every
  other value in `getwizard.json` stays untouched. Verified via a full
  before/after diff of every field after a no-op write (`AUTO_REBOOT_HOUR`
  written back unchanged) — the only difference was the naturally ticking
  `SOFTWARE_UPDATE` countdown text.
- **No 60s revert:** unlike the inline commands above, values set this way
  persist permanently. Verified by setting, waiting 65s, then re-reading —
  the value was still there. No keep-alive needed for these entities.
- The response is the full, updated `getwizard.json` dump (not just an echo
  of the sent fields) — `AskoheatWizardNumber`/`AskoheatWizardTime` use this
  to update `coordinator.secondary.wizard` immediately, without waiting for
  the next poll.
- Values are sent as JSON **strings** (even plain numbers, e.g. `"3"` not
  `3`) — matching the format the device itself uses when returning them in
  `getwizard.json`.

Implemented in `api.py` (`AskoheatApiClient.async_write_wizard`), `number.py`
(`AskoheatWizardNumber`) and `time.py` (`AskoheatWizardTime`). Entity list:
[05_entities.md](05_entities.md). Communication timeout is deliberately kept
read-only, see there.

Andreas' note: not every value has this readable REST path — some are
instead set via `curl 'http://<host>/{"<VARIABLE>":"<VALUE>"}'` (JSON
directly in the URL path, no `/server1/` prefix). For every installer
setting mapped in this integration so far, though, `POST /server1/` has
confirmed to be a working, consistent path.

## Privacy note on `getreg.json`

Besides `EXTRA.*` (installation data), `getreg.json` also contains
`USER_CONTACT.*` and `INSTALLER_CONTACT.*` with real names, phone number and
email address. This integration does read this endpoint, but **deliberately
only maps `EXTRA.*`** as entities — the contact fields never end up in the
recorder history.
