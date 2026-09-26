# 05 — Entity-Referenz

*[English version](../en/05_entities.md)*

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
| `temperature_sensor_1`..`4` | Temperatur Sensor 1..4 | home | `ACTUAL_VALUES.TEMP_SENSOR_1`..`4` | °C, temperature | **live ermittelt** — aktiv, sobald der Fühler einen Wert liefert (weder "not connected" noch der Sentinel `9999`), siehe unten |
| `temperature_limit_info` | Temperaturlimit | home | `ACTUAL_VALUES.ACTUAL_TEMPERATURE_LIMIT` | Text | ja |
| `error_status` | Gerätestatus | home | `ASKOHEAT_PLUS_INFO.ERROR_STATUS` | Text | ja |
| `legio_info` | Legionellenschutz | home | `ASKOHEAT_PLUS_INFO.LEGIO_INFO` | Text, diagnostic | ja |
| `last_update` | Letzte Aktualisierung | coordinator | — (Zeitstempel des Coordinators, kein JSON-Pfad) | timestamp, diagnostic | ja |
| `article_name` | Artikelname | home | `ASKOHEAT_PLUS_INFO.ARTICLE_NAME` | Text, diagnostic | nein |
| `article_number` | Artikelnummer | home | `ASKOHEAT_PLUS_INFO.ARTICLE_NUMBER` | Text, diagnostic | nein |
| `serial_number` | Seriennummer | home | `ASKOHEAT_PLUS_INFO.SERIAL_NUMBER` | Text, diagnostic | nein |
| `software_version` | Software-Version | home | `ASKOHEAT_PLUS_INFO.SOFTWARE_VERSION` | Text, diagnostic | nein |
| `hardware_version` | Hardware-Version | home | `ASKOHEAT_PLUS_INFO.HARDWARE_VERSION` | Text, diagnostic | nein |
| `device_family` | Gerätefamilie | home | abgeleitet aus `ASKOHEAT_PLUS_INFO.HARDWARE_VERSION` (Präfix) | Text, diagnostic | nein |
| `max_power` | Max. Leistung | home | `ASKOHEAT_PLUS_INFO.MAX_POWER` | W, diagnostic | nein |
| `number_of_heater` | Anzahl Heizstäbe | home | `ASKOHEAT_PLUS_INFO.NUMBER_OF_HEATER` | Zahl, diagnostic | nein |
| `number_of_steps` | Anzahl Heizstufen | home | `ASKOHEAT_PLUS_INFO.NUMBER_OF_STEPS` | Zahl, diagnostic | nein |
| `temperature_precise` | Temperatur (präzise) | temperature_calibration | `TEMPERATURE_0.VALUE` | °C, 2 Nachkommastellen, diagnostic | ja |
| `tcp_connection` | Modbus TCP Verbindung | wizard_status | `MODBUS_INFO.TCP_CONNECTION` | Text, diagnostic | nein |
| `rtu_connection` | Modbus RTU Verbindung | wizard_status | `MODBUS_INFO.RTU_CONNECTION` | Text, diagnostic | nein |
| `pv_peak` | PV-Spitzenleistung | registration | `EXTRA.PV_PEAK` | Zahl, diagnostic | nein |
| `battery_size` | Batteriegröße | registration | `EXTRA.BATTERY` | Zahl, diagnostic | nein |
| `communication_timeout_heater_off` / `communication_timeout_reset` | Kommunikations-Timeout (Heizstab aus/Reset) | wizard | `COMMUNICATION_TIMEOUT_HEATER_OFF`/`_RESET` | Zahl (Einheit unbestätigt), diagnostic | nein |

**Hinweis zu den `communication_timeout_*`-Sensoren:** bewusst read-only
belassen (Andreas' ausdrücklicher Wunsch) — ein Fehlwert hier könnte die
Geräte-Kommunikation lahmlegen. Alle anderen ursprünglich hier gelisteten
Installer-Einstellungen (Legionellenschutz, Niedertarif, Einspeise-
Zeitfenster, Wärmepumpen-Anforderung, Auto-Abschaltung, Auto-Reboot) sind
jetzt schreibbare `number`-/`time`-Entities, siehe die entsprechenden
Abschnitte unten.

`getwizard.json` (der volle Installer-Konfigurations-Dump, Quelle für
`source: wizard`) wird wie die anderen Sekundär-Endpunkte nur einmalig beim
Integrations-Start geladen. Nach einem Schreibzugriff über eine der unten
dokumentierten `number`-/`time`-Entities wird der lokale Cache aber sofort
mit der vollständigen Geräte-Antwort aktualisiert — die Werte sind also nur
dann veraltet, wenn die Einstellung stattdessen direkt über die Geräte-
eigene Weboberfläche (`extended.html`) geändert wurde, ohne über Home
Assistant zu laufen.

## Binary Sensoren (`binary_sensor.py`)

| Key | Name (DE) | Pfad (in `gethome.json`) | Device Class | "on" bedeutet |
|---|---|---|---|---|
| `pump_output` | Pumpe | `ACTUAL_VALUES.PUMP_OUTPUT` | — | Pumpe läuft |
| `heater_disabled` | Heizstab gesperrt | `STATUS_FLAGS.HEATER_DISABLED` | problem | Heizstab ist gesperrt |
| `relayboard_connected` | Relayboard verbunden | `STATUS_FLAGS.RELAYBOARD_CONNECTED` | connectivity, diagnostic | Relayboard verbunden |
| `current_flow` | Stromfluss | `STATUS_FLAGS.CURRENT_FLOW` | —, diagnostic | Stromfluss erkannt |

## Number-Entities (`number.py`, Phase 2 — schreibbar)

Zeigen den aktuellen Sollwert (`SET_INPUTS.*` aus `gethome.json`) an **und**
setzen ihn beim Ändern über die in [02_api-referenz.md](02_api-referenz.md)
dokumentierten Inline-Command-Endpunkte. **Keep-Alive eingebaut:** solange der
gesetzte Wert `≠ 0` ist, wird er automatisch alle 45s erneut gesendet, damit
er nicht dem geräteseitigen 60s-Verfall zum Opfer fällt — kein manuelles
Nachsetzen nötig. Bei `0` stoppt das Keep-Alive automatisch.

| Key | Name (DE) | Command-Endpunkt | Bereich | Einheit |
|---|---|---|---|---|
| `heater_step_target` | Ziel-Heizstufe | `heater%20step` | `0`–`NUMBER_OF_STEPS` (dynamisch) | — |
| `load_setpoint` | Leistungsvorgabe | `load%20setpoint` | `0`–`MAX_POWER` (dynamisch) | W |
| `load_feedin` | Einspeisewert | `load%20feedin` | `-32768`–`32767` | W |

Ersetzen die früheren, rein lesenden Diagnose-Sensoren `set_heater_step` und
`set_load_feedin` aus Phase 1 (entfernt, um doppelte Entities für denselben
Wert zu vermeiden — siehe [07_changelog.md](07_changelog.md)).

Manuelles Setzen (per Slider/Eingabefeld in der UI) funktioniert unabhängig
davon, ob eine Entity zusätzlich verknüpft ist — alle Wege nutzen denselben
`number.set_value`-Service, es gibt keinen gesonderten "Automatik-Modus".
`load_feedin` und `load_setpoint` lassen sich zusätzlich direkt über den
Options-Flow der Integration ("⋮ → Konfigurieren") mit einer beliebigen
anderen Entity verknüpfen, siehe [10_automatisierung.md](10_automatisierung.md).

## Number-Entities: Installer-Einstellungen (`number.py`, schreibbar)

Zusätzlich zu den drei Steuer-Entities oben: schreibbare Installer-
Einstellungen aus `getwizard.json`, geschrieben über `POST /server1/` (siehe
[02_api-referenz.md](02_api-referenz.md), "Installer-Einstellungen
schreiben"). **Kein Keep-Alive nötig** — anders als bei den SET_INPUTS-Werten
oben verfallen diese Werte nicht nach 60s (live gegen das Testgerät
verifiziert, siehe [07_changelog.md](07_changelog.md)).

| Key | Name (DE) | Wizard-Schlüssel | Bereich | Einheit |
|---|---|---|---|---|
| `legio_target_temperature_set` | Legionellenschutz Zieltemperatur | `MODBUS_CON_LEGIO_TEMPERATURE` | 20–95 | °C |
| `low_tariff_target_temperature_set` | Niedertarif Zieltemperatur | `MODBUS_CON_TEMPERATURE_LOW_TARIFF` | 20–95 | °C |
| `heat_pump_request_on_step_set` / `heat_pump_request_off_step_set` | Wärmepumpen-Anforderung Ein-/Aus-Stufe | `MODBUS_CON_HEAT_PUMP_REQUEST_ON/OFF_STEP` | `0`–`NUMBER_OF_STEPS` (dynamisch) | — |
| `heat_pump_request_target_temperature_set` | Wärmepumpen-Anforderung Zieltemperatur | `MODBUS_CON_TEMPERATURE_HEAT_PUMP_REQUEST` | 20–95 | °C |
| `auto_heater_off_timeout_set` | Auto-Abschaltung Timeout | `MODBUS_CON_AUTO_HEATER_OFF_MINUTES` | 0–1440 | min |

Alle als `entity_category: config` eingestuft (erscheinen im UI unter
"Konfiguration", nicht in der normalen Entity-Liste).

## Time-Entities: Installer-Zeitfenster (`time.py`, schreibbar)

Uhrzeit-Installer-Einstellungen, ebenfalls über `POST /server1/` geschrieben.
Das Gerät speichert Uhrzeiten intern als getrennte Stunde/Minute-Felder — die
Entity kombiniert/zerlegt das transparent zu einem einzelnen `time`-Wert.

| Key | Name (DE) | Wizard-Schlüssel (Stunde/Minute) |
|---|---|---|
| `legio_activation_time_set` | Legionellenschutz Startzeit | `MODBUS_CON_LEGIO_ACTIV_TIME_HOUR`/`_MINUTE` |
| `low_tariff_start_time_set` / `low_tariff_end_time_set` | Niedertarif Start/Ende | `MODBUS_CON_LOW_TARIFF_START/END_TIME_HOUR`/`_MINUTE` |
| `feedin_window_start_time_set` / `feedin_window_end_time_set` | Einspeise-Zeitfenster Start/Ende | `MODBUS_CON_USE_FEEDIN_START/END_TIME_HOUR`/`_MINUTE` |
| `auto_reboot_time_set` | Auto-Reboot Zeit | `AUTO_REBOOT_HOUR`/`AUTO_REBOOT_MINUTE` |

## Switch-Entity (`switch.py`)

| Key | Name (DE) | Pfad (Anzeige) | Ein-Befehl | Aus-Befehl |
|---|---|---|---|---|
| `emergency_mode` | Notbetrieb | `STATUS_FLAGS.EMERGENCY_MODE` | `on` | `off` |

Entspricht der physischen Taste am Gerät (`on`/`off`-Endpunkte ohne
Parameter, siehe [02_api-referenz.md](02_api-referenz.md)) — **kein**
60s-Verfall, daher kein Keep-Alive nötig, anders als bei den Number-Entities
oben. Ersetzt den gleichnamigen, rein lesenden Binary-Sensor aus Phase 1
(gleicher Grund wie bei den Number-Entities: Anzeige + Steuerung in einem).

## Diagnose-/Konfigurations-Entities standardmäßig deaktiviert

Reine Stammdaten (Artikelnummer, Seriennummer, Versionsnummern, PV-Peak,
Verbindungsdiagnose) sind standardmäßig **deaktiviert**
(`entity_registry_enabled_default=False`), damit die Entity-Liste im Alltag
übersichtlich bleibt. Sie lassen sich pro Entity in den Einstellungen
jederzeit aktivieren.

**Sonderfall `temperature_sensor_1`..`4`:** hier wird der Standard nicht statisch
gesetzt, sondern bei jedem Setup live anhand des aktuellen Gerätewerts
ermittelt — ein Fühler ist "aktiv", außer er meldet `"not connected"` oder den
numerischen Sentinel `9999`. Bereits registrierte, zuvor deaktivierte Sensoren
werden automatisch reaktiviert, sobald sie live einen Wert liefern (kein
Entfernen/Neu-Einrichten nötig). Siehe `sensor.py`
(`_resolve_temp_sensor_defaults`, `_reenable_now_connected_temp_sensors`).

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
