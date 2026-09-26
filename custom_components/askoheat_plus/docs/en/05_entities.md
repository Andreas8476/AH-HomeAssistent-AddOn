# 05 — Entity reference

*[Deutsche Version](../de/05_entities.md) (primary, authoritative)*

Sensors and binary sensors (phase 1) are purely display entities (read-only).
`source` says which endpoint the value comes from — `home` is polled
regularly, all others once at startup (see
[02_api-reference.md](02_api-reference.md)). Number entities (phase 2, own
section below) are **writable**.

## Sensors (`sensor.py`)

| Key | Name (EN) | source | Path | Unit/device class | Enabled by default |
|---|---|---|---|---|---|
| `heater_step` | Heater step | home | `ACTUAL_VALUES.ACTUAL_HEATER_STEP` | number | yes |
| `heater_load` | Heater load | home | `ACTUAL_VALUES.ACTUAL_HEATER_LOAD` | W, power | yes |
| `temperature_sensor_0` | Temperature | home | `ACTUAL_VALUES.TEMP_SENSOR_0` | °C, temperature | yes |
| `temperature_sensor_1`..`4` | Temperature sensor 1..4 | home | `ACTUAL_VALUES.TEMP_SENSOR_1`..`4` | °C, temperature | **determined live** — enabled as soon as the probe reports a value (neither "not connected" nor the `9999` sentinel), see below |
| `temperature_limit_info` | Temperature limit | home | `ACTUAL_VALUES.ACTUAL_TEMPERATURE_LIMIT` | text | yes |
| `error_status` | Device status | home | `ASKOHEAT_PLUS_INFO.ERROR_STATUS` | text | yes |
| `legio_info` | Legionella protection | home | `ASKOHEAT_PLUS_INFO.LEGIO_INFO` | text, diagnostic | yes |
| `last_update` | Last update | coordinator | — (coordinator timestamp, no JSON path) | timestamp, diagnostic | yes |
| `article_name` | Article name | home | `ASKOHEAT_PLUS_INFO.ARTICLE_NAME` | text, diagnostic | no |
| `article_number` | Article number | home | `ASKOHEAT_PLUS_INFO.ARTICLE_NUMBER` | text, diagnostic | no |
| `serial_number` | Serial number | home | `ASKOHEAT_PLUS_INFO.SERIAL_NUMBER` | text, diagnostic | no |
| `software_version` | Software version | home | `ASKOHEAT_PLUS_INFO.SOFTWARE_VERSION` | text, diagnostic | no |
| `hardware_version` | Hardware version | home | `ASKOHEAT_PLUS_INFO.HARDWARE_VERSION` | text, diagnostic | no |
| `device_family` | Device family | home | derived from `ASKOHEAT_PLUS_INFO.HARDWARE_VERSION` (prefix) | text, diagnostic | no |
| `max_power` | Max. power | home | `ASKOHEAT_PLUS_INFO.MAX_POWER` | W, diagnostic | no |
| `number_of_heater` | Number of heaters | home | `ASKOHEAT_PLUS_INFO.NUMBER_OF_HEATER` | number, diagnostic | no |
| `number_of_steps` | Number of heater steps | home | `ASKOHEAT_PLUS_INFO.NUMBER_OF_STEPS` | number, diagnostic | no |
| `temperature_precise` | Temperature (precise) | temperature_calibration | `TEMPERATURE_0.VALUE` | °C, 2 decimal places, diagnostic | yes |
| `tcp_connection` | Modbus TCP connection | wizard_status | `MODBUS_INFO.TCP_CONNECTION` | text, diagnostic | no |
| `rtu_connection` | Modbus RTU connection | wizard_status | `MODBUS_INFO.RTU_CONNECTION` | text, diagnostic | no |
| `pv_peak` | PV peak power | registration | `EXTRA.PV_PEAK` | number, diagnostic | no |
| `battery_size` | Battery size | registration | `EXTRA.BATTERY` | number, diagnostic | no |

## Binary sensors (`binary_sensor.py`)

| Key | Name (EN) | Path (in `gethome.json`) | Device class | "on" means |
|---|---|---|---|---|
| `pump_output` | Pump | `ACTUAL_VALUES.PUMP_OUTPUT` | — | pump is running |
| `heater_disabled` | Heater locked | `STATUS_FLAGS.HEATER_DISABLED` | problem | heater is locked |
| `relayboard_connected` | Relay board connected | `STATUS_FLAGS.RELAYBOARD_CONNECTED` | connectivity, diagnostic | relay board connected |
| `current_flow` | Current flow | `STATUS_FLAGS.CURRENT_FLOW` | —, diagnostic | current flow detected |

## Number entities (`number.py`, phase 2 — writable)

Show the current setpoint (`SET_INPUTS.*` from `gethome.json`) **and** set
it on change via the inline-command endpoints documented in
[02_api-reference.md](02_api-reference.md). **Built-in keep-alive:** as long
as the set value is `≠ 0`, it's automatically resent every 45s so it doesn't
fall victim to the device's 60s revert — no manual resending needed. It
stops automatically at `0`.

| Key | Name (EN) | Command endpoint | Range | Unit |
|---|---|---|---|---|
| `heater_step_target` | Target heater step | `heater%20step` | `0`–`NUMBER_OF_STEPS` (dynamic) | — |
| `load_setpoint` | Load setpoint | `load%20setpoint` | `0`–`MAX_POWER` (dynamic) | W |
| `load_feedin` | Feed-in value | `load%20feedin` | `-32768`–`32767` | W |

Replace the earlier, read-only diagnostic sensors `set_heater_step` and
`set_load_feedin` from phase 1 (removed to avoid duplicate entities for the
same value — see [07_changelog.md](07_changelog.md)).

Setting a value manually (via slider/input field in the UI) works
independently of whether an entity is additionally linked — every path
uses the same `number.set_value` service, there's no separate "automatic
mode". `load_feedin` and `load_setpoint` can also be linked directly to
any other entity via the integration's options flow ("⋮ → Configure"), see
[10_automation.md](10_automation.md).

## Switch entity (`switch.py`)

| Key | Name (EN) | Path (display) | On command | Off command |
|---|---|---|---|---|
| `emergency_mode` | Emergency mode | `STATUS_FLAGS.EMERGENCY_MODE` | `on` | `off` |

Corresponds to the physical button on the device (`on`/`off` endpoints with
no parameters, see [02_api-reference.md](02_api-reference.md)) — **no**
60s revert, so no keep-alive needed, unlike the number entities above.
Replaces the same-named, read-only binary sensor from phase 1 (same reason
as the number entities: display + control in one).

## Diagnostic/configuration entities disabled by default

Pure master data (article number, serial number, version numbers, PV peak,
connection diagnostics) is **disabled** by default
(`entity_registry_enabled_default=False`) so the entity list stays clear
day-to-day. Each can be enabled any time in the entity settings.

**Special case `temperature_sensor_1`..`4`:** here the default isn't set
statically but determined live at each setup from the device's current
value — a probe is "enabled" unless it reports `"not connected"` or the
numeric sentinel `9999`. Already-registered, previously disabled sensors
are automatically re-enabled as soon as they report a value live (no
removing/re-adding needed). See `sensor.py`
(`_resolve_temp_sensor_defaults`, `_reenable_now_connected_temp_sensors`).

## Deliberately not mapped (phase 1)

- Free-text relay counters (`STATUS_FLAGS.HEATER_1_RELAY` etc., format
  `"off (1x on today) (saldo +135393 used 0)"`) — too fragile to parse for v1.
- `USER_CONTACT.*` / `INSTALLER_CONTACT.*` from `getreg.json` — personal
  data, deliberately not mapped as an entity/recorder history.
- Full `getwizard.json` dump — only documented as a reference in
  [02_api-reference.md](02_api-reference.md).
- Direct heater-step paths (`0`–`19`) and `128` (grid-lock/emergency stop)
  as separate `button` entities — the "target heater step" `number` entity
  covers the regular use case, grid-lock is a later idea.
