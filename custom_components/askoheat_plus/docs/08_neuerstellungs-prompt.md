# 08 — Neuerstellungs-Prompt

Dieser Prompt fasst Kontext, Entscheidungen und Architektur so zusammen, dass
sich diese Integration (Phase 1 — Lesen) auch ohne den ursprünglichen Chat-
Verlauf von Grund auf nachbauen lässt. Einfach als Ganzes an einen KI-Coding-
Assistenten (z.B. Claude Code) übergeben.

---

## Prompt (zum Kopieren)

> Ich betreibe Home Assistant OS auf einem Raspberry Pi 5. Ich möchte eine
> Custom Integration für meinen **ASKOHEAT+** PV-Heizstab bauen (Hersteller
> Askoma). Das Gerät hat eine lokale, unauthentifizierte REST-API (JSON über
> HTTP, kein Cloud-Zwang).
>
> **Ziel dieser ersten Phase:** nur Daten auslesen (Sensoren). Steuerung
> (Schreiben) und ein Dashboard mit Heizstab-Bildern sind spätere, separate
> Phasen — jetzt **nicht** umsetzen.
>
> **Architektur:** eine Custom Integration unter
> `custom_components/askoheat_plus/`, HACS-kompatibel, damit sie später auf
> GitHub veröffentlicht und von jedem installiert werden kann. Kein Supervisor-
> Add-on. Orientiere dich, falls im selben Home-Assistant-Setup vorhanden, an
> bestehenden Integrationen für andere lokale Geräte mit Polling + Config Flow
> (z.B. eine go-eCharger- oder Modbus-Heizungs-Integration) für Code-Stil und
> HA-Konventionen (`DataUpdateCoordinator`, `ConfigFlow`, `CoordinatorEntity`).
>
> **Ordnerstruktur:** alles — Code UND eine durchnummerierte Projekt-Doku
> (`01_*.md`, `02_*.md`, ...) — in einem einzigen, in sich geschlossenen Ordner,
> der später 1:1 als Git-Repo dienen kann. Da Home Assistant Custom Integrations
> zwingend unter `<config>/custom_components/<domain>/` erwartet, lege das Repo
> z.B. unter `<config>/askoheat_plus/` an (mit `custom_components/askoheat_plus/`
> als Unterordner, README/LICENSE/hacs.json auf Repo-Root-Ebene) und hänge es per
> **Symlink** nach `<config>/custom_components/askoheat_plus` ein, damit Home
> Assistant es sofort lädt, ohne Code zu duplizieren. Die Doku liegt direkt im
> Integrationsordner (`custom_components/askoheat_plus/docs/`).
>
> **API-Endpunkte:** Nutze für den regelmäßigen Poll **ausschließlich**
> `GET /gethome.json` (ein Request pro Zyklus, Default-Intervall 30 Sekunden,
> konfigurierbar 10–300s). Dieser Endpunkt liefert bereits Gerätestammdaten
> (`ASKOHEAT_PLUS_INFO.*`: Artikel, Seriennummer, Versionen, `DEVICEID`),
> Live-Werte (`ACTUAL_VALUES.*`), Soll-Werte (`SET_INPUTS.*`) und Status/Relais
> (`STATUS_FLAGS.*`). **Wichtig: den ESP32-Controller im Gerät nicht mit zu
> vielen/zu häufigen Anfragen überfordern** — deshalb bewusst nur dieser eine
> Endpunkt im Regel-Poll. Vier weitere Endpunkte (`getwizard.json`,
> `getwizard_status.json`, `gettemperature_calibration.json`, `getreg.json`)
> nur **einmalig beim Start** abrufen, nicht wiederholt (Feintuning der
> Polling-Frequenz dafür bewusst offen lassen, siehe Changelog).
>
> Felder sind teils Text mit angehängter Einheit (z.B. `"0 watts"`,
> `"25 °C"`) — über einen generischen Regex-Zahlenextraktor lesen, nicht über
> String-Split. `getreg.json` enthält unter `USER_CONTACT`/`INSTALLER_CONTACT`
> personenbezogene Daten (Name, Telefon, E-Mail) — **nicht** als Entity/
> Recorder-Historie abbilden, nur `EXTRA.*` (PV-Peak, Batteriegröße, Puffer)
> verwenden.
>
> **Technische Patterns:**
> - `manifest.json`: `config_flow: true`, `integration_type: "device"`,
>   `iot_class: "local_polling"`, `requirements: []` (nur HA-eigenes `aiohttp`).
> - Eigener API-Client (`api.py`), der `async_get_clientsession(hass)` nutzt
>   (keine eigene Session erstellen/schließen).
> - `AskoheatDataUpdateCoordinator(DataUpdateCoordinator[dict])`, Fehler auf
>   `UpdateFailed` mappen.
> - `entry.runtime_data` für den Coordinator (moderne HA-Konvention, kein
>   `hass.data[DOMAIN][entry_id]`).
> - Config Flow: Host (Pflicht), Port (Default 80), Abfrageintervall (Default
>   30s) abfragen; beim Absenden `gethome.json` testweise abrufen, `DEVICEID`
>   als `unique_id` setzen (`async_set_unique_id` + `_abort_if_unique_id_configured`).
> - Entities als deklarative `EntityDescription`-Dataclass-Listen mit einer
>   `value_fn`, die einen JSON-Pfad ausliest, statt einer Python-Klasse pro
>   Sensor.
> - Zentrale `DeviceInfo` auf dem Coordinator (nicht pro Entity dupliziert).
>
> **Entity-Umfang (Phase 1):** Heizstufe, Heizleistung (W), Temperatur (°C),
> Temperaturlimit-Info, Soll-Heizstufe, Soll-Einspeisewert, Gerätestatus,
> Legionellenschutz-Info, Artikel-/Seriennummer/Versionen (diagnostisch,
> standardmäßig deaktiviert), präzise Temperatur mit Kalibrierung, TCP/RTU-
> Verbindungsstatus, PV-Peak, Batteriegröße — als Sensoren. Pumpe aktiv,
> Notbetrieb, Heizstab gesperrt, Relayboard verbunden, Stromfluss — als Binary-
> Sensoren. Freitextige Relais-Zähler (`"off (1x on today) (saldo ...)"`)
> bewusst NICHT einzeln parsen (zu fragil für v1).
>
> **Doku (durchnummeriert, im Integrationsordner):** Überblick, API-Referenz
> (inkl. Abfrage-Strategie/ESP-Schonung), Architektur, Installation (HACS +
> manuell + lokaler Dev-Symlink), Entity-Referenztabelle, Entwicklungs-
> Workflow, Changelog, und dieser Neuerstellungs-Prompt als letztes Dokument.
>
> Bevor du Code schreibst: prüfe, ob es im Ziel-Home-Assistant-Setup bereits
> ähnliche Custom Integrations gibt (lokales Gerät + Polling + Config Flow) und
> übernimm deren Code-Stil/-Konventionen wo sinnvoll. Frage nach, falls unklar:
> ob eine Custom Integration oder ein echtes Supervisor-Add-on gewünscht ist,
> wo die durchnummerierte Doku liegen soll, ob verfügbare Beispieldaten vom
> echten Gerät stammen oder nur generisches Referenzmaterial sind, und welche
> lokale IP-Adresse zum Testen verwendet werden kann.

---

## Kontext, der beim Nachbau hilfreich ist (aber nicht zwingend Teil des Prompts)

- Quelle der API-Struktur: Herstellerdoku "ASKOHEAT+ JSON" und "Askoheat+
  Steuerung via REST API" (Askoma), plus ein realer Beispiel-Dump aller
  Endpunkte eines eigenen Geräts.
- Entscheidungen kamen aus drei Rückfragen zu Beginn: (1) Custom Integration
  vs. Supervisor-Add-on, (2) Ablageort der Doku, (3) Echtdaten vs. Referenz.
- Der Endpunkt-Fokus auf `gethome.json` + 4 Sekundär-Endpunkte sowie der
  Hinweis auf ESP32-Schonung kamen als Nachtrag vom Nutzer, nachdem der
  ursprüngliche Plan noch `_values.json` + `getpar.json` vorsah.
