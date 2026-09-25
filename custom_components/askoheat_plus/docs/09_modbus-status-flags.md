# 09 — Modbus Status-/Error-Flag-Register (Referenz)

Quelle: offizielle Modbus-Registerdoku des Herstellers,
<http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html>.

Diese Register erscheinen auch als einzelne Felder in `gethome.json` (und
anderen JSON-Endpunkten) als rohe Dezimalzahl — z.B. `MODBUS_VAL_STATUS`,
`MODBUS_VAL_STATUS_EXTENDED`, `MODBUS_VAL_ERROR_STATUS`. Die von dieser
Integration genutzten `STATUS_FLAGS.*`-Textfelder in `gethome.json`
(`ACTUAL_VALUES.PUMP_OUTPUT`, `STATUS_FLAGS.RELAYBOARD_CONNECTED`, ...) sind
die bereits vom Gerät in Klartext übersetzte Sicht auf genau diese Bits — diese
Seite dient als Referenz/Cross-Check, nicht als weitere Datenquelle für
Phase 1.

**Beispiel-Abgleich:** beim Testgerät (`192.168.20.54`) stand
`MODBUS_VAL_STATUS = 16` = Binär `00010000` → Low-Byte Bit 4
(`RELAYBOARD_CONNECTED`) gesetzt → passt exakt zum beobachteten
`binary_sensor.ahf280_ti_plus_15_8_relayboard_verbunden = on`.

## `MODBUS_VAL_STATUS` (Adresse 109 / 624)

Aktueller Gesamtstatus. Hinweis in der Herstellerdoku: zum Ein-/Ausschalten der
Heizstäbe wird Register 200 verwendet, nicht dieses (read-only).

**High-Byte:**

| Bit | Name | Bedeutung |
|---|---|---|
| 7 | `ERROR_FLAG` | irgendein Fehler aktiv (siehe `MODBUS_VAL_ERROR_STATUS`) |
| 6 | `TEMP_LIMIT_REACHED` | Temperaturlimit erreicht, Heizstäbe abgeschaltet |
| 5 | `PUMP_FOLLOWUP_ACTIVE` | Pumpen-Nachlaufzeit aktiv |
| 4 | `AUTO_HEATER_OFF_ACTIVE` | automatische Abschaltung aktiv |
| 3 | `LOAD_FEEDIN_ACTIVE` | Einspeisewert aktiv (negativ, reduziert Netzeinspeisung) |
| 2 | `LOAD_SETPOINT_ACTIVE` | Leistungsvorgabe aktiv (gültige positive Werte) |
| 1 | `ANALOG_INPUT_ACTIVE` | 0–10V Analogeingang aktiv |
| 0 | `LEGIO_PROTECTION_ACTIVE` | Legionellenschutz aktiv |

**Low-Byte:**

| Bit | Name | Bedeutung |
|---|---|---|
| 7 | `EMERGENCY_MODE_ACTIVE` | Notbetrieb aktiv |
| 6 | `HEAT_PUMP_REQUEST_ACTIVE` | Wärmepumpen-Anforderung aktiv |
| 5 | `CURRENT_FLOW_PRESENT` | Stromfluss Heizstab 1–3 (interne Sicherheit/Thermostat aktiv) |
| 4 | `RELAYBOARD_CONNECTED` | Relayboard (ASKOHEAT+ 2.0) verbunden |
| 3 | `PUMP_RELAY_ACTIVE` | Relais 4 – Pumpe aktiv |
| 2 | `HEATER3_RELAY_ACTIVE` | Relais 3 – Heizstab 3 aktiv |
| 1 | `HEATER2_RELAY_ACTIVE` | Relais 2 – Heizstab 2 aktiv |
| 0 | `HEATER1_RELAY_ACTIVE` | Relais 1 – Heizstab 1 aktiv |

## `MODBUS_VAL_STATUS_EXTENDED` (Adresse 698, ab Firmware 5.0.0 / ASKOHEAT+ 2.0)

**High-Byte:**

| Bit | Name | Bedeutung |
|---|---|---|
| 7 | `ERROR_FLAG` | irgendein Fehler aktiv |
| 6 | `HEATER_LOCK_ACTIVE` | Sperreingang "Lock Heater" aktiv |
| 5 | `EW_SPERRE_ACTIVE` | EVU-/EW-Sperre aktiv |
| 4 | `FEEDIN_TIME_LOCKED` | Einspeise-Zeitfenster gesperrt |
| 1 | `CURRENT_FLOW_FLAG_2` | Stromfluss rechts (Heizstäbe 5, 6, 7) |
| 0 | `CURRENT_FLOW_FLAG_1` | Stromfluss links (Heizstäbe 1, 2, 3) |

**Low-Byte:**

| Bit | Name | Bedeutung |
|---|---|---|
| 7 | `HEATER6_RELAY_ACTIVE` | Relais 8 – Heizstab 6 aktiv |
| 6 | `HEATER5_RELAY_ACTIVE` | Relais 7 – Heizstab 5 aktiv |
| 5 | `HEATER4_RELAY_ACTIVE` | Relais 6 – Heizstab 4 aktiv |
| 2 | `HEATER3_RELAY_ACTIVE` | Relais 3 – Heizstab 3 aktiv |
| 1 | `HEATER2_RELAY_ACTIVE` | Relais 2 – Heizstab 2 aktiv |
| 0 | `HEATER1_RELAY_ACTIVE` | Relais 1 – Heizstab 1 aktiv |

`MODBUS_EXT_STATUS` (Adresse 700) liefert laut Doku dieselben Flags wie
`MODBUS_VAL_STATUS` (nicht die Extended-Variante).

## `MODBUS_VAL_ERROR_STATUS` (Adresse 631)

Rücksetzbar über `MODBUS_CMD_CLEAR_TEMP_SENSOR_ERROR` (Register 213) für die
Sensor-Fehler.

**High-Byte:**

| Bit | Name | Bedeutung |
|---|---|---|
| 7 | `WLAN_ERROR` | WLAN-Verbindungsfehler |
| 6 | `LAN_ERROR` | LAN-Verbindungsfehler (Ethernet) |
| 4 | `MODBUS_RTU_ERROR` | Modbus-RTU-Verbindungsfehler (RS485) |
| 3 | `SETTINGS_ERROR` | mindestens eine Einstellung verursacht Fehlfunktion |
| 2 | `LEGIO_ERROR` | Fehler Legionellenschutz (siehe `MODBUS_VAL_LEGIO_STATUS`) |
| 0 | `CURRENT_FLOW_ERROR` | Heizstab aktiviert, aber kein Stromfluss |

**Low-Byte:**

| Bit | Name | Bedeutung |
|---|---|---|
| 7 | `REALTIME_CLOCK_ERROR` | Fehler interne Echtzeituhr (keine NTP-Verbindung) |
| 6 | `TEMP_SETTINGS_ERROR` | Fehler Temperatureinstellungen (kein/ungültiger Sensor) |
| 4 | `SENSOR4_ERROR` | Temperatursensor 4 defekt (Kabelbruch/Fehler) |
| 3 | `SENSOR3_ERROR` | Temperatursensor 3 defekt |
| 2 | `SENSOR2_ERROR` | Temperatursensor 2 defekt |
| 1 | `SENSOR1_ERROR` | Temperatursensor 1 defekt |
| 0 | `SENSOR0_ERROR` | Temperatursensor 0 defekt |

## `MODBUS_VAL_TEMPERATURE_STATUS` (Adresse 632)

**High-Byte** (welche Funktion aktuell das Temperaturlimit setzt):

| Bit | Name | Bedeutung |
|---|---|---|
| 6 | `TEMP_LIMIT_BY_SET_HEATER` | Limit durch "Set Heater Step" |
| 5 | `TEMP_LIMIT_BY_LOAD` | Limit durch Leistungsvorgabe/Einspeisewert |
| 4 | `TEMP_LIMIT_BY_ANALOG` | Limit durch Analogeingang |
| 3 | `TEMP_LIMIT_BY_HPR_EMG` | Limit durch Wärmepumpen-Anforderung/Notbetrieb |
| 2 | `TEMP_LIMIT_BY_LEGIO` | Limit durch Legionellenschutz |
| 1 | `TEMP_LIMIT_BY_LOW_TARIFF` | Limit durch Niedertarif-Modus |
| 0 | `TEMP_LIMIT_BY_MIN_TEMP` | Limit durch Mindesttemperatur-Modus |

**Low-Byte:**

| Bit | Name | Bedeutung |
|---|---|---|
| 6 | `TEMP_LIMIT_REACHED` | Temperaturlimit erreicht, Heizstäbe abgeschaltet |
| 4 | `SENSOR4_AVAILABLE` | Sensor 4 vorhanden (externer PT1000) |
| 3 | `SENSOR3_AVAILABLE` | Sensor 3 vorhanden |
| 2 | `SENSOR2_AVAILABLE` | Sensor 2 vorhanden |
| 1 | `SENSOR1_AVAILABLE` | Sensor 1 vorhanden |
| 0 | `SENSOR0_AVAILABLE` | Sensor 0 vorhanden (intern, PT1000) |

## `MODBUS_VAL_LEGIO_STATUS` / `MODBUS_EXT_LEGIO_STATUS` (Adresse 627 / 703)

| Bit | Name | Bedeutung |
|---|---|---|
| 7 | `LEGIO_SETTINGS_ERROR` | Einstellungen fehlerhaft |
| 6 | `LEGIO_TEMP_UNREACHABLE` | Zieltemperatur nach 240 Minuten nicht erreicht |
| 5 | `LEGIO_NO_SENSOR` | kein gültiger Temperatursensor verbunden |
| 4 | `LEGIO_TEMP_DROP` | unerwarteter Temperaturabfall während Plateau-Timer |
| 2 | `LEGIO_OUTSIDE_INTERVAL` | Temperatur außerhalb Legionellenschutz-Intervall erreicht |
| 1 | `LEGIO_PLATEAU_ACTIVE` | Zieltemperatur erreicht, Plateauzeit aktiv |
| 0 | `LEGIO_HEATING_PHASE` | Aufheizphase (siehe `MODBUS_VAL_LEGIO_COUNTDOWN`) |

## `MODBUS_VAL_ACTUAL_CONTROL_INPUT` (Adresse 626)

Zeigt, welcher Regeleingang den Heizstab aktuell steuert.

**High-Byte:**

| Bit | Name | Bedeutung |
|---|---|---|
| 3 | `SENEC_HOME_ENABLED` | Software-Regeleingang SENEC.Home aktiviert |
| 2 | `SMA_SEMP_ENABLED` | Software-Regeleingang SMA.SEMP aktiviert |
| 1 | `AUTO_HEATER_OFF_CTRL` | Heizstab aktuell durch Auto-Abschaltung gesteuert |
| 0 | `LEGIO_PROTECTION_CTRL` | Heizstab aktuell durch Legionellenschutz gesteuert |

**Low-Byte:**

| Bit | Name | Bedeutung |
|---|---|---|
| 7 | `LOAD_SETPOINT_CTRL` | gesteuert durch Leistungsvorgabe |
| 6 | `LOAD_FEEDIN_CTRL` | gesteuert durch Einspeisewert |
| 5 | `EMERGENCY_MODE_CTRL` | gesteuert durch Notbetrieb |
| 4 | `HPR_CTRL` | gesteuert durch Wärmepumpen-Anforderung |
| 3 | `ANALOG_INPUT_CTRL` | gesteuert durch Analogeingang |
| 2 | `SET_HEATER_STEP_CTRL` | gesteuert durch "Set Heater Step" |
| 1 | `LOW_TARIFF_CTRL` | gesteuert durch Niedertarif-Modus |
| 0 | `MIN_TEMP_CTRL` | gesteuert durch Mindesttemperatur-Modus |

## Mögliche spätere Verwendung

Für Phase 1 bleibt es bei der bereits vom Gerät übersetzten `STATUS_FLAGS.*`-
Klartextsicht in `gethome.json`. Diese Bit-Referenz ist aber die Grundlage,
falls später mal sinnvoll:

- ein "Raw Status"-Diagnose-Sensor (z.B. `MODBUS_VAL_ACTUAL_CONTROL_INPUT`
  decodiert als Text: "wodurch wird der Heizstab gerade geregelt?"),
- präzisere Fehlerdiagnose als der pauschale `ERROR_STATUS`-Text,
- oder Validierung/Tests der `STATUS_FLAGS.*`-Textinterpretation gegen die
  rohen Registerwerte.
