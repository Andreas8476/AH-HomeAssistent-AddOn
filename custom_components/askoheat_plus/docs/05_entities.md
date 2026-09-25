# 05 — Entity-Referenz

Sensoren und Binary-Sensoren (Phase 1) sind reine Anzeige-Entities (read-only).
`source` gibt an, aus welchem Endpunkt der Wert stammt — `home` wird
regelmäßig gepollt, alle anderen einmalig beim Start (siehe
[02_api-referenz.md](02_api-referenz.md)). Number-Entities (Phase 2, eigener
Abschnitt unten) sind **schreibbar**.

## Sensoren (`sensor.py`)

| Key | Name (DE) | source | Pfad | Einheit/Device Class | Standardmäßig aktiv |
|---|---|---|---|---|---|
| `heater_step` | Heizstufe | home | `ACTUAL_VALUES.ACTUAL_HEATER_STEP` | Zahl | ja |
| `heater_load` | Heizleistung | home | `ACTUAL_VALUES.ACTUAL_HEATER_LOAD` | W, power | ja |
| `temperature_sensor_0` | Temperatur | home | `ACTUAL_VALUES.TEMP_SENSOR_0` | °C, temperature | ja |
| `temperature_limit_info` | Temperaturlimit | home | `ACTUAL_VALUES.ACTUAL_TEMPERATURE_LIMIT` | Text | ja |
| `error_status` | Gerätestatus | home | `ASKOHEAT_PLUS_INFO.ERROR_STATUS` | Text | ja |
| `legio_info` | Legionellenschutz | home | `ASKOHEAT_PLUS_INFO.LEGIO_INFO` | Text, diagnostic | ja |
| `article_name` | Artikelname | home | `ASKOHEAT_PLUS_INFO.ARTICLE_NAME` | Text, diagnostic | nein |
| `article_number` | Artikelnummer | home | `ASKOHEAT_PLUS_INFO.ARTICLE_NUMBER` | Text, diagnostic | nein |
| `serial_number` | Seriennummer | home | `ASKOHEAT_PLUS_INFO.SERIAL_NUMBER` | Text, diagnostic | nein |
| `software_version` | Software-Version | home | `ASKOHEAT_PLUS_INFO.SOFTWARE_VERSION` | Text, diagnostic | nein |
| `hardware_version` | Hardware-Version | home | `ASKOHEAT_PLUS_INFO.HARDWARE_VERSION` | Text, diagnostic | nein |
| `max_power` | Max. Leistung | home | `ASKOHEAT_PLUS_INFO.MAX_POWER` | W, diagnostic | nein |
| `number_of_heater` | Anzahl Heizstäbe | home | `ASKOHEAT_PLUS_INFO.NUMBER_OF_HEATER` | Zahl, diagnostic | nein |
| `number_of_steps` | Anzahl Heizstufen | home | `ASKOHEAT_PLUS_INFO.NUMBER_OF_STEPS` | Zahl, diagnostic | nein |
| `temperature_precise` | Temperatur (präzise) | temperature_calibration | `TEMPERATURE_0.VALUE` | °C, 2 Nachkommastellen, diagnostic | ja |
| `tcp_connection` | Modbus TCP Verbindung | wizard_status | `MODBUS_INFO.TCP_CONNECTION` | Text, diagnostic | nein |
| `rtu_connection` | Modbus RTU Verbindung | wizard_status | `MODBUS_INFO.RTU_CONNECTION` | Text, diagnostic | nein |
| `pv_peak` | PV-Spitzenleistung | registration | `EXTRA.PV_PEAK` | Zahl, diagnostic | nein |
| `battery_size` | Batteriegröße | registration | `EXTRA.BATTERY` | Zahl, diagnostic | nein |

## Binary Sensoren (`binary_sensor.py`)

| Key | Name (DE) | Pfad (in `gethome.json`) | Device Class | "on" bedeutet |
|---|---|---|---|---|
| `pump_output` | Pumpe | `ACTUAL_VALUES.PUMP_OUTPUT` | — | Pumpe läuft |
| `emergency_mode` | Notbetrieb | `STATUS_FLAGS.EMERGENCY_MODE` | problem | Notbetrieb aktiv |
| `heater_disabled` | Heizstab gesperrt | `STATUS_FLAGS.HEATER_DISABLED` | problem | Heizstab ist gesperrt |
| `relayboard_connected` | Relayboard verbunden | `STATUS_FLAGS.RELAYBOARD_CONNECTED` | connectivity, diagnostic | Relayboard verbunden |
| `current_flow` | Stromfluss | `STATUS_FLAGS.CURRENT_FLOW` | —, diagnostic | Stromfluss erkannt |

## Number-Entities (`number.py`, Phase 2 — schreibbar)

Zeigen den aktuellen Sollwert (`SET_INPUTS.*` aus `gethome.json`) an **und**
setzen ihn beim Ändern über die in [02_api-referenz.md](02_api-referenz.md)
dokumentierten Inline-Command-Endpunkte. **Wichtig:** vom Gerät nach ~60s ohne
erneutes Senden automatisch zurückgesetzt (siehe dort).

| Key | Name (DE) | Command-Endpunkt | Bereich | Einheit |
|---|---|---|---|---|
| `heater_step_target` | Ziel-Heizstufe | `heater%20step` | `0`–`NUMBER_OF_STEPS` (dynamisch) | — |
| `load_setpoint` | Leistungsvorgabe | `load%20setpoint` | `0`–`MAX_POWER` (dynamisch) | W |
| `load_feedin` | Einspeisewert | `load%20feedin` | `-32768`–`32767` | W |

Ersetzen die früheren, rein lesenden Diagnose-Sensoren `set_heater_step` und
`set_load_feedin` aus Phase 1 (entfernt, um doppelte Entities für denselben
Wert zu vermeiden — siehe [07_changelog.md](07_changelog.md)).

## Diagnose-/Konfigurations-Entities standardmäßig deaktiviert

Reine Stammdaten (Artikelnummer, Seriennummer, Versionsnummern, PV-Peak,
Verbindungsdiagnose) sind standardmäßig **deaktiviert**
(`entity_registry_enabled_default=False`), damit die Entity-Liste im Alltag
übersichtlich bleibt. Sie lassen sich pro Entity in den Einstellungen
jederzeit aktivieren.

## Bewusst nicht abgebildet (Phase 1)

- Freitextige Relais-Zähler (`STATUS_FLAGS.HEATER_1_RELAY` etc., Format
  `"off (1x on today) (saldo +135393 used 0)"`) — zu fragiles Parsing für v1.
- `USER_CONTACT.*` / `INSTALLER_CONTACT.*` aus `getreg.json` — personenbezogene
  Daten, bewusst nicht als Entity/Recorder-Historie abgebildet.
- Voller `getwizard.json`-Dump — nur als Referenz in
  [02_api-referenz.md](02_api-referenz.md) dokumentiert.
- Direkte Heizstufen-Pfade (`0`–`19`) und `128` (EW-Sperre/Notaus) als separate
  `button`-Entities — die `number`-Entity "Ziel-Heizstufe" deckt den regulären
  Anwendungsfall ab, EW-Sperre ist eine spätere Idee.
- Automatisches Keep-Alive gegen den 60s-Verfall der gesetzten Werte —
  bewusste Design-Entscheidung, siehe [02_api-referenz.md](02_api-referenz.md).
