# 02 — API-Referenz

Quelle: Herstellerdoku "ASKOHEAT+ JSON" und "Askoheat+ Steuerung via REST API"
(Askoma Confluence-Export, dem Projekt als Anhang übergeben) sowie ein realer
Beispiel-Dump aller Endpunkte eines Andreas' eigenen Geräts
(`b4:8a:0a:49:5b:9c`, IP `.53` im Dump; Testgerät für diese Integration ist
`192.168.20.54`).

Für die Bedeutung der einzelnen Bits in den Status-/Fehler-Feldern
(`MODBUS_VAL_STATUS`, `MODBUS_VAL_STATUS_EXTENDED`, `MODBUS_VAL_ERROR_STATUS`,
...) siehe die eigene Referenz [09_modbus-status-flags.md](09_modbus-status-flags.md)
(Quelle: offizielle Modbus-Registerdoku).

Grundsätzliches: alle Endpunkte sind einfache, **unauthentifizierte** `GET`-
Requests auf `http://<host>/<endpunkt>`, Antwort ist JSON. Es gibt Dutzende
Endpunkte (`getall.json`, `_values.json`, `getcon.json`, `getsenec.json`, ...) —
diese Integration nutzt bewusst nur eine Teilmenge, siehe unten.

## Abfrage-Strategie (ESP32 schonen)

Der ASKOHEAT+ läuft auf einem ESP32. Die geräteeigene Weboberfläche fragt ihre
eigene "home"-Seite laut Herstellerdoku alle 2 Sekunden ab — das ist also die
Referenz für "unbedenklich". Diese Integration ist bewusst deutlich
zurückhaltender:

| Endpunkt | Verwendung | Intervall |
|---|---|---|
| `gethome.json` | Haupt-Polling: Gerätestammdaten + Live-Werte + Soll-Werte + Status/Relais in einer Antwort | Coordinator-Intervall, Default **30s**, einstellbar 10–300s |
| `getwizard_status.json` | Verbindungsdiagnose (TCP/RTU/SENEC/SMA) | einmalig beim Setup |
| `gettemperature_calibration.json` | präzise Temperaturwerte (2 Nachkommastellen) + Kalibrier-Offsets | einmalig beim Setup |
| `getreg.json` | Installationsdaten (`EXTRA.*`: PV-Peak, Batteriegröße, Pufferspeicher) | einmalig beim Setup |
| `getwizard.json` | voller Konfigurations-Dump (groß) — Referenz/Diagnose | nicht automatisch abgerufen in Phase 1 |

**Offener Punkt:** die vier Sekundär-Endpunkte werden aktuell nur ein einziges
Mal beim Start der Integration geladen, nicht wiederholt. Ob/wie oft sie erneut
abgefragt werden sollten (z.B. bei Reconnect, oder ein eigenes langsames
Intervall von z.B. 15–30 Minuten), ist bewusst noch nicht entschieden — siehe
[07_changelog.md](07_changelog.md).

## Warum ausgerechnet diese 5 Endpunkte

Auf Wunsch von Andreas eingegrenzt, weil `gethome.json` (die Datenquelle der
Geräte-eigenen "Home"-Seite) bereits fast alles enthält, was man für einen
Überblick braucht — und die vier übrigen gezielt Zusatzinfos liefern, die
`gethome.json` nicht hat (Kalibrierung, Verbindungsdiagnose, Installations-
Metadaten, vollständige Rohkonfiguration).

## `gethome.json` — Struktur (Auszug, relevante Felder)

```
TYPE
ASKOHEAT_PLUS_INFO.
    DEVICEID                  # MAC-artige ID, genutzt als unique_id
    ARTICLE_NAME / ARTICLE_NUMBER / SERIAL_NUMBER
    HARDWARE_VERSION / SOFTWARE_VERSION
    HEATER_1_POWER..HEATER_6_POWER, NUMBER_OF_STEPS, NUMBER_OF_HEATER, MAX_POWER
    ERROR_STATUS               # "fine" oder Fehlertext
    LEGIO_INFO                 # "disabled" oder Statustext
ACTUAL_VALUES.
    ACTUAL_HEATER_STEP         # aktuelle Heizstufe (Zahl)
    ACTUAL_HEATER_LOAD         # aktuelle Leistung in Watt (reine Zahl)
    ACTUAL_HEATER_LOAD_WATTS   # dieselbe Info als Text ("0 watts")
    ACTUAL_TEMPERATURE_LIMIT   # Text, z.B. "none (current 25 °C)"
    TEMP_SENSOR_0..4           # Text mit Einheit, z.B. "25 °C" / "not connected"
    PUMP_OUTPUT                # "active" / "not active"
SET_INPUTS.
    SET_HEATER_STEP, SET_LOAD_SETPOINT, SET_LOAD_FEEDIN   # Sollwerte (Phase 2 relevant)
STATUS_FLAGS.
    ERROR, EMERGENCY_MODE, HEATER_DISABLED, RELAYBOARD_CONNECTED, CURRENT_FLOW, ...
    HEATER_1_RELAY..HEATER_6_RELAY   # Freitext "off (1x on today) (saldo +135393 used 0)"
```

Felder wie `"0 watts"`, `"25 °C"` sind **Text mit angehängter Einheit** — die
Integration liest sie über einen generischen Zahlen-Extraktor
(`api.extract_number`, Regex `-?\d+(?:[.,]\d+)?`), nicht über String-Split.

## Setzen von Werten (Inline-Commands, Referenz für Phase 2)

Ab Firmware 4.6.2 lassen sich Werte per GET auf eine URL-kodierte JSON-Struktur
setzen, z.B.:

```
curl 'http://askoheat.local/%7B%22MODBUS_CMD_SET_HEATER_STEP%22:%223%22%7D'
```

entspricht dem Klartext-JSON `{"MODBUS_CMD_SET_HEATER_STEP":"3"}`. Es gibt außerdem
sprechendere Pfade wie `heater%20step?value=x` oder `load%20setpoint?value=nnn`
(siehe Herstellerdoku "Askoheat+ Steuerung via REST API", Abschnitt "Hilfsmittel
zur Installation"). Wird in Phase 2 aufgegriffen — **nicht Teil dieser Version.**

## Datenschutz-Hinweis zu `getreg.json`

`getreg.json` enthält neben `EXTRA.*` (Installationsdaten) auch `USER_CONTACT.*`
und `INSTALLER_CONTACT.*` mit echten Namen, Telefonnummer und E-Mail-Adresse.
Diese Integration liest diesen Endpunkt zwar ab, bildet aber **bewusst nur
`EXTRA.*`** als Entities ab — die Kontaktfelder landen nicht in der
Recorder-Historie.
