# 09 — Modbus status/error flag registers (reference)

*[Deutsche Version](../de/09_modbus-status-flags.md) (primary, authoritative)*

Source: the manufacturer's official Modbus register documentation,
<http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html>.

These registers also appear as individual fields in `gethome.json` (and
other JSON endpoints) as raw decimal numbers — e.g. `MODBUS_VAL_STATUS`,
`MODBUS_VAL_STATUS_EXTENDED`, `MODBUS_VAL_ERROR_STATUS`. The `STATUS_FLAGS.*`
text fields in `gethome.json` used by this integration
(`ACTUAL_VALUES.PUMP_OUTPUT`, `STATUS_FLAGS.RELAYBOARD_CONNECTED`, ...) are
the device's own plain-text translation of exactly these bits — this page
serves as a reference/cross-check, not as a further data source for phase 1.

**Example cross-check:** on the test device (`192.168.20.54`),
`MODBUS_VAL_STATUS = 16` = binary `00010000` → low-byte bit 4
(`RELAYBOARD_CONNECTED`) set → matches exactly the observed
`binary_sensor.ahf280_ti_plus_15_8_relayboard_verbunden = on`.

## `MODBUS_VAL_STATUS` (address 109 / 624)

Current overall status. Note in the manufacturer docs: register 200 is used
to turn the heating elements on/off, not this one (read-only).

**High byte:**

| Bit | Name | Meaning |
|---|---|---|
| 7 | `ERROR_FLAG` | some error is active (see `MODBUS_VAL_ERROR_STATUS`) |
| 6 | `TEMP_LIMIT_REACHED` | temperature limit reached, heating elements switched off |
| 5 | `PUMP_FOLLOWUP_ACTIVE` | pump follow-up time active |
| 4 | `AUTO_HEATER_OFF_ACTIVE` | automatic shutdown active |
| 3 | `LOAD_FEEDIN_ACTIVE` | feed-in value active (negative, reduces grid feed-in) |
| 2 | `LOAD_SETPOINT_ACTIVE` | load setpoint active (valid positive values) |
| 1 | `ANALOG_INPUT_ACTIVE` | 0–10V analog input active |
| 0 | `LEGIO_PROTECTION_ACTIVE` | legionella protection active |

**Low byte:**

| Bit | Name | Meaning |
|---|---|---|
| 7 | `EMERGENCY_MODE_ACTIVE` | emergency mode active |
| 6 | `HEAT_PUMP_REQUEST_ACTIVE` | heat pump request active |
| 5 | `CURRENT_FLOW_PRESENT` | current flow heater 1–3 (internal safety/thermostat active) |
| 4 | `RELAYBOARD_CONNECTED` | relay board (ASKOHEAT+ 2.0) connected |
| 3 | `PUMP_RELAY_ACTIVE` | relay 4 – pump active |
| 2 | `HEATER3_RELAY_ACTIVE` | relay 3 – heater 3 active |
| 1 | `HEATER2_RELAY_ACTIVE` | relay 2 – heater 2 active |
| 0 | `HEATER1_RELAY_ACTIVE` | relay 1 – heater 1 active |

## `MODBUS_VAL_STATUS_EXTENDED` (address 698, from firmware 5.0.0 / ASKOHEAT+ 2.0)

**High byte:**

| Bit | Name | Meaning |
|---|---|---|
| 7 | `ERROR_FLAG` | some error is active |
| 6 | `HEATER_LOCK_ACTIVE` | "Lock Heater" lock input active |
| 5 | `EW_SPERRE_ACTIVE` | utility/grid lock active |
| 4 | `FEEDIN_TIME_LOCKED` | feed-in time window locked |
| 1 | `CURRENT_FLOW_FLAG_2` | current flow right (heaters 5, 6, 7) |
| 0 | `CURRENT_FLOW_FLAG_1` | current flow left (heaters 1, 2, 3) |

**Low byte:**

| Bit | Name | Meaning |
|---|---|---|
| 7 | `HEATER6_RELAY_ACTIVE` | relay 8 – heater 6 active |
| 6 | `HEATER5_RELAY_ACTIVE` | relay 7 – heater 5 active |
| 5 | `HEATER4_RELAY_ACTIVE` | relay 6 – heater 4 active |
| 2 | `HEATER3_RELAY_ACTIVE` | relay 3 – heater 3 active |
| 1 | `HEATER2_RELAY_ACTIVE` | relay 2 – heater 2 active |
| 0 | `HEATER1_RELAY_ACTIVE` | relay 1 – heater 1 active |

`MODBUS_EXT_STATUS` (address 700) delivers, per the docs, the same flags as
`MODBUS_VAL_STATUS` (not the extended variant).

## `MODBUS_VAL_ERROR_STATUS` (address 631)

Resettable via `MODBUS_CMD_CLEAR_TEMP_SENSOR_ERROR` (register 213) for the
sensor errors.

**High byte:**

| Bit | Name | Meaning |
|---|---|---|
| 7 | `WLAN_ERROR` | WiFi connection error |
| 6 | `LAN_ERROR` | LAN connection error (Ethernet) |
| 4 | `MODBUS_RTU_ERROR` | Modbus RTU connection error (RS485) |
| 3 | `SETTINGS_ERROR` | at least one setting causes a malfunction |
| 2 | `LEGIO_ERROR` | legionella protection error (see `MODBUS_VAL_LEGIO_STATUS`) |
| 0 | `CURRENT_FLOW_ERROR` | heater activated but no current flow |

**Low byte:**

| Bit | Name | Meaning |
|---|---|---|
| 7 | `REALTIME_CLOCK_ERROR` | internal real-time clock error (no NTP connection) |
| 6 | `TEMP_SETTINGS_ERROR` | temperature settings error (no/invalid sensor) |
| 4 | `SENSOR4_ERROR` | temperature sensor 4 faulty (broken wire/error) |
| 3 | `SENSOR3_ERROR` | temperature sensor 3 faulty |
| 2 | `SENSOR2_ERROR` | temperature sensor 2 faulty |
| 1 | `SENSOR1_ERROR` | temperature sensor 1 faulty |
| 0 | `SENSOR0_ERROR` | temperature sensor 0 faulty |

## `MODBUS_VAL_TEMPERATURE_STATUS` (address 632)

**High byte** (which function currently sets the temperature limit):

| Bit | Name | Meaning |
|---|---|---|
| 6 | `TEMP_LIMIT_BY_SET_HEATER` | limit via "Set Heater Step" |
| 5 | `TEMP_LIMIT_BY_LOAD` | limit via load setpoint/feed-in value |
| 4 | `TEMP_LIMIT_BY_ANALOG` | limit via analog input |
| 3 | `TEMP_LIMIT_BY_HPR_EMG` | limit via heat pump request/emergency mode |
| 2 | `TEMP_LIMIT_BY_LEGIO` | limit via legionella protection |
| 1 | `TEMP_LIMIT_BY_LOW_TARIFF` | limit via low-tariff mode |
| 0 | `TEMP_LIMIT_BY_MIN_TEMP` | limit via minimum-temperature mode |

**Low byte:**

| Bit | Name | Meaning |
|---|---|---|
| 6 | `TEMP_LIMIT_REACHED` | temperature limit reached, heating elements switched off |
| 4 | `SENSOR4_AVAILABLE` | sensor 4 present (external PT1000) |
| 3 | `SENSOR3_AVAILABLE` | sensor 3 present |
| 2 | `SENSOR2_AVAILABLE` | sensor 2 present |
| 1 | `SENSOR1_AVAILABLE` | sensor 1 present |
| 0 | `SENSOR0_AVAILABLE` | sensor 0 present (internal, PT1000) |

## `MODBUS_VAL_LEGIO_STATUS` / `MODBUS_EXT_LEGIO_STATUS` (address 627 / 703)

| Bit | Name | Meaning |
|---|---|---|
| 7 | `LEGIO_SETTINGS_ERROR` | settings are faulty |
| 6 | `LEGIO_TEMP_UNREACHABLE` | target temperature not reached after 240 minutes |
| 5 | `LEGIO_NO_SENSOR` | no valid temperature sensor connected |
| 4 | `LEGIO_TEMP_DROP` | unexpected temperature drop during the plateau timer |
| 2 | `LEGIO_OUTSIDE_INTERVAL` | temperature reached outside the legionella-protection interval |
| 1 | `LEGIO_PLATEAU_ACTIVE` | target temperature reached, plateau time active |
| 0 | `LEGIO_HEATING_PHASE` | heating-up phase (see `MODBUS_VAL_LEGIO_COUNTDOWN`) |

## `MODBUS_VAL_ACTUAL_CONTROL_INPUT` (address 626)

Shows which control input currently drives the heating element.

**High byte:**

| Bit | Name | Meaning |
|---|---|---|
| 3 | `SENEC_HOME_ENABLED` | software control input SENEC.Home enabled |
| 2 | `SMA_SEMP_ENABLED` | software control input SMA.SEMP enabled |
| 1 | `AUTO_HEATER_OFF_CTRL` | heater currently controlled by auto-shutoff |
| 0 | `LEGIO_PROTECTION_CTRL` | heater currently controlled by legionella protection |

**Low byte:**

| Bit | Name | Meaning |
|---|---|---|
| 7 | `LOAD_SETPOINT_CTRL` | controlled via load setpoint |
| 6 | `LOAD_FEEDIN_CTRL` | controlled via feed-in value |
| 5 | `EMERGENCY_MODE_CTRL` | controlled via emergency mode |
| 4 | `HPR_CTRL` | controlled via heat pump request |
| 3 | `ANALOG_INPUT_CTRL` | controlled via analog input |
| 2 | `SET_HEATER_STEP_CTRL` | controlled via "Set Heater Step" |
| 1 | `LOW_TARIFF_CTRL` | controlled via low-tariff mode |
| 0 | `MIN_TEMP_CTRL` | controlled via minimum-temperature mode |

## Possible future use

For phase 1, we stick with the device's own translated `STATUS_FLAGS.*`
plain-text view in `gethome.json`. This bit reference is, however, the
basis should the following ever become useful later:

- a "raw status" diagnostic sensor (e.g. decoding
  `MODBUS_VAL_ACTUAL_CONTROL_INPUT` as text: "what's currently controlling
  the heater?"),
- more precise error diagnostics than the blanket `ERROR_STATUS` text,
- or validating/testing the `STATUS_FLAGS.*` text interpretation against
  the raw register values.
