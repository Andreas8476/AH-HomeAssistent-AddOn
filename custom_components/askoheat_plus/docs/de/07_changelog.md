# 07 — Changelog

*[English version](../en/07_changelog.md)*

Änderungsprotokoll dieses Projekts. Separat vom globalen
`/homeassistant/docs/changelog.md` des Gesamt-HA-Setups (der dort verweist nur
kurz auf dieses Projekt).

## 2026-09-25 — Phase 1: Lesen (Erststellung)

- Projekt angelegt: `custom_components/askoheat_plus/` als eigenständiges,
  HACS-fähiges Repo unter `/homeassistant/askoheat_plus/`, per Symlink in
  `custom_components/` eingehängt.
- Architektur: `DataUpdateCoordinator` pollt ausschließlich `gethome.json`
  (ein Request pro Zyklus, Default 30s), vier weitere Endpunkte
  (`getwizard_status.json`, `gettemperature_calibration.json`, `getreg.json`,
  perspektivisch `getwizard.json`) werden einmalig beim Start geladen.
  Endpunkt-Auswahl und "ESP32 nicht überfordern"-Vorgabe kamen von Andreas.
- Config Flow mit Verbindungstest, `unique_id` = Geräte-`DEVICEID`.
- 13 Sensoren + 5 Binary-Sensoren, alle read-only. Details:
  [05_entities.md](05_entities.md).
- Bewusste Auslassungen: freitextige Relais-Zähler, personenbezogene Felder aus
  `getreg.json` (`USER_CONTACT`/`INSTALLER_CONTACT`).

## 2026-09-25 — Verifikation + Modbus-Flag-Referenz

- Phase 1 gegen das echte Testgerät (`192.168.20.54`, Modell "AHF280-TI-plus-15.8")
  verifiziert: alle Sensoren/Binary-Sensoren liefern plausible Werte, inkl. der
  einmalig geladenen `gettemperature_calibration.json`-Sensoren. Gerätekonfiguration
  wurde korrekt dynamisch erkannt (anderes Modell als im ursprünglichen Beispiel-Dump).
- Neue Referenzdoku [09_modbus-status-flags.md](09_modbus-status-flags.md):
  Bit-für-Bit-Bedeutung der Status-/Fehler-Register (`MODBUS_VAL_STATUS`,
  `MODBUS_VAL_STATUS_EXTENDED`, `MODBUS_VAL_ERROR_STATUS`, u.a.), aus der
  offiziellen Modbus-Registerdoku des Herstellers. Dient aktuell nur als
  Cross-Check/Grundlage für spätere Erweiterungen, keine neuen Entities.
- Repo zu GitLab gepusht: `git@gitlab.com:SyberAlf/ah-homeassistent-addon.git`,
  Tag `v0.1.0`. Zusätzliches Root-`CHANGELOG.md` (Keep a Changelog/SemVer)
  ergänzt dieses Dokument für eine saubere Release-Historie auf GitLab.

## 2026-09-25 — Phase 2: Steuern

- Drei `number`-Entities (`number.py`): Ziel-Heizstufe, Leistungsvorgabe,
  Einspeisewert. Schreiben über die dokumentierten Inline-Command-Endpunkte
  (`heater%20step`, `load%20setpoint`, `load%20feedin`), Bereiche dynamisch
  aus `ASKOHEAT_PLUS_INFO.NUMBER_OF_STEPS`/`MAX_POWER` bzw. statisch
  (int16-Bereich) für den Einspeisewert.
- `api.py`: neue Methode `async_send_command`, nutzt denselben Client wie das
  Lesen, kein zusätzlicher Coordinator/Polling.
- **Aufräumen:** die Phase-1-Diagnose-Sensoren `set_heater_step` und
  `set_load_feedin` entfernt (redundant zu den neuen Number-Entities, die
  denselben Wert anzeigen und zusätzlich setzen können). Die zugehörigen
  Entity-Registry-Einträge werden von Home Assistant nicht automatisch
  gelöscht, sondern zeigen `unavailable` — manuell in den Einstellungen
  entfernbar.
- Bewusst **kein** automatischer Keep-Alive gegen den 60s-Verfall gesetzter
  Werte (Herstellerdoku) implementiert — würde dem ESP32-Schonungsprinzip aus
  Phase 1 widersprechen. Wer dauerhafte Steuerung will, muss selbst periodisch
  erneut setzen (z.B. per HA-Automation).

## 2026-09-25 — Keep-Alive, GitHub-Spiegel, Attribution, Automatisierungs-Blueprint

- **Korrektur zur Keep-Alive-Entscheidung oben:** Andreas hat nach dem Live-
  Test klargestellt, dass regelmäßiges Neusenden für den ESP32 unproblematisch
  und vom Hersteller sogar erwartet ist ("kontinuierlich steuerndes Gerät").
  Jede Number-Entity implementiert jetzt ein eingebautes Keep-Alive: alle
  `NUMBER_KEEPALIVE_INTERVAL` (45s) wird der zuletzt gesetzte Wert erneut
  gesendet, solange er `≠ 0` ist; stoppt bei `0` oder Entity-Entfernung.
  `native_value` zeigt bevorzugt den intern gehaltenen Wert (sofortiges
  UI-Feedback). Details: [02_api-referenz.md](02_api-referenz.md).
- Neue Automation-Blueprint [`blueprints/askoheat_plus_feedin_from_meter.yaml`](../../../../blueprints/askoheat_plus_feedin_from_meter.yaml)
  verknüpft einen beliebigen Zähler-/Wechselrichter-Leistungssensor mit dem
  Einspeisewert (`number.load_feedin`) — Import-Anleitung in neuer
  [10_automatisierung.md](10_automatisierung.md). Bewusst als Blueprint statt
  fest verdrahteter Config-Option (flexibler, kein Extra-Setup-Schritt).
- **GitHub-Spiegel eingerichtet:** `github.com/Andreas8476/AH-HomeAssistent-AddOn`,
  da HACS ausschließlich öffentliche GitHub-Repos unterstützt (GitLab bleibt
  Haupt-Repo). **Ab jetzt verbindlich: jeder Commit geht auf beide Remotes**
  (`origin` + `github`), siehe [06_entwicklung.md](06_entwicklung.md).
  `manifest.json` `documentation`/`issue_tracker`/`codeowners` zeigen jetzt auf
  das echte GitHub-Repo.
- Vollständige HACS-Installationsanleitung inkl. HACS-Ersteinrichtung in
  [04_installation.md](04_installation.md).
- Attribution ergänzt (README, `01_ueberblick.md`, `LICENSE`): Andreas
  Stegemann + Claude (Sonnet 5), Hinweis auf Andreas' Mitarbeit bei der
  ASKOMA AG (privates Projekt, keine offizielle ASKOMA-Software).

## 2026-09-25 — Notbetrieb-Schalter

- Neue `switch`-Entity `emergency_mode` (`switch.py`): steuert den Notbetrieb
  über die parameterlosen `on`/`off`-Endpunkte (physische Taste am Gerät,
  kein 60s-Verfall, daher kein Keep-Alive nötig). Ersetzt den gleichnamigen
  read-only Binary-Sensor aus Phase 1.
- `api.py`: neue Methode `async_send_bare_command` für parameterlose Befehle.
- Live bestätigt: der neue Schalter hat einen echten Zustandswechsel des
  Testgeräts korrekt erfasst (`off → on → off` während eines Neustarts).
- Aufräumen: verwaiste Entity-Registry-Einträge (`sensor..._soll_heizstufe`,
  `sensor..._soll_einspeisewert` aus Phase 2, sowie der abgelöste
  `binary_sensor..._notbetrieb`) direkt in `.storage/core.entity_registry`
  entfernt (Backup vorher angelegt), da kein Long-Lived-Access-Token für die
  UI-seitige Löschung zur Verfügung stand.
- Klargestellt: manuelles Setzen der Number-Entities (Ziel-Heizstufe,
  Leistungsvorgabe, Einspeisewert) funktioniert bereits ohne weiteres Zutun,
  unabhängig von einer zusätzlichen Automation-Verknüpfung.

## 2026-09-25 — Phase 3: Dashboard

- `sensor.py`: `temperature_sensor_1`..`4` ergänzt (bisher nur Sensor 0) —
  Voraussetzung für die im Dashboard gewünschten 4 Temperaturanzeigen.
  Standardmäßig deaktiviert, falls am Gerät nicht angeschlossen.
- Neues, eigenes YAML-Mode-Lovelace-Dashboard "ASKOHEAT+"
  (`dashboard/askoheat_plus_dashboard.yaml`), registriert über einen neuen
  `lovelace:`-Block in `configuration.yaml` (bisher gab es in diesem Setup
  nur UI-verwaltete Dashboards). Zwei `picture-elements`-Karten mit Andreas'
  eigenen Askoma-Renderbildern (`dashboard/images/`) als Hintergrund und
  Live-Werten als Overlay-Labels (Temperatursensoren 0–4 + Heizleistung am
  Tank; Ziel-Heizstufe, Leistungsvorgabe, Einspeisewert am Zählerschrank).
  Details inkl. Anpassungshinweise für andere Nutzer: [11_dashboard.md](11_dashboard.md).
- **Wichtige technische Erkenntnis:** der bisherige Symlink-Trick
  (`custom_components/`) funktioniert **nicht** für Dashboard-Bilder — Home
  Assistants `/local/`-Server folgt keinen aus `www/` herauszeigenden
  Symlinks (404). Bilder liegen daher zusätzlich als echte Kopie in
  `www/askoheat_plus/`, synchron zu `dashboard/images/` zu halten.
- YAML-Stolperstein: Home Assistants eigener YAML-Loader (`annotatedyaml`)
  behandelt `<<: *anchor` + zusätzliche Keys in derselben Mapping als
  Duplicate-Key-Warnung statt sauber zu mergen (anders als reines PyYAML) —
  Dashboard-YAML daher bewusst ohne Anker/Merge-Keys geschrieben.
- Live verifiziert: beide Bilder unter `/local/askoheat_plus/*.png` liefern
  HTTP 200, `ha core check`/Neustart fehlerfrei, keine Duplicate-Key-Warnungen
  mehr im Log.

## 2026-09-25 — Dashboard-Feinschliff, Installationsdoku-Ergänzung

- Nach Screenshot-Feedback von Andreas: Label-Abstände im Dashboard
  vergrößert (Vorgabe/Einspeisewert lagen mit nur ~12 Prozentpunkten
  Abstand fast übereinander), Temperatursensor-Labels breiter über die
  Heizwendel verteilt statt eng gestapelt.
- "Alle Werte"-Fallback-Karte: explizite kurze `name:`-Overrides für jede
  Entity, da die vollen Standardnamen (inkl. Gerätename) in der
  Entities-Karte abgeschnitten wurden.
- `docs/de/04_installation.md`: Terminal/SSH-Add-on als Voraussetzung für die
  HACS-Erstinstallation jetzt explizit unter "Voraussetzungen" genannt
  (vorher nur implizit in Schritt 1), inkl. terminalloser Alternative
  (File editor/Samba).
- **Nachgelegt auf Wunsch von Andreas:** bloßes Erwähnen des Terminal-Add-ons
  reichte nicht — Ziel ist eine Anleitung, der auch ein technisch unerfahrener
  Anwender von Grund auf folgen kann. Schritt 1 der HACS-Variante jetzt eine
  vollständige Klick-für-Klick-Anleitung zur Installation eines Terminal-
  Add-ons (Add-on-Store öffnen, "Terminal & SSH" suchen/installieren/starten),
  Schritt 2 entsprechend für HACS selbst ausgebaut (inkl. GitHub-Konto
  anlegen, Device-Code-Flow erklärt). Schritte neu durchnummeriert (1–5).

## 2026-09-25 — ASKOMA-Logo, nachträgliche Rekonfiguration

- **ASKOMA-Logo eingebaut** (`custom_components/askoheat_plus/brand/`):
  `icon.png`/`icon@2x.png` (quadratischer Ausschnitt des Berg+Kreuz-Symbols
  aus Andreas' Originallogo, HA 2026.3+ liest Custom-Integration-Icons direkt
  aus dem Komponentenordner, kein Zentral-Repo-Eintrag nötig — Muster wie bei
  `froeling_lambdatronic_modbus/brand/icon.png`), `logo.png`
  (Hellmodus-Wortmarke), `dark_logo.png`/`dark_logo@2x.png` (Dunkelmodus-
  Variante). Bildzuschnitt lokal mit Pillow in einer isolierten venv erstellt
  (System-Python bewusst nicht verändert).
- **Neu: nachträgliche Rekonfiguration.** `config_flow.py` implementiert jetzt
  `async_step_reconfigure` — Host/Port/Abfrageintervall sind über "Geräte &
  Dienste → ASKOHEAT+ → ⋮ → Neu konfigurieren" jederzeit änderbar, nicht mehr
  nur beim Ersteinrichten. Verbindungstest wie beim Ersteinrichten, plus
  Schutz gegen versehentliches Umbiegen auf ein anderes physisches Gerät
  (`_abort_if_unique_id_mismatch`). API-Methoden verifiziert durch direktes
  Nachschlagen im tatsächlich installierten `homeassistant`-Quellcode via
  `docker exec homeassistant` (Container-Zugriff diese Session neu entdeckt) —
  zuverlässiger als die vorherige reine `py_compile`-Prüfung.

## 2026-09-25 — Mehrgeräte-Test: Dashboard-Generator, robustere Fehlerbehandlung

- Andreas hat ein zweites Gerät ("SONNENBOOSTER 5,2 kW") probeweise
  eingerichtet. Dabei aufgefallen: Temperatursensoren 1–4 fehlten scheinbar
  — tatsächlich nur wie designed standardmäßig deaktiviert (kein Bug),
  gegengeprüft direkt in der Entity-Registry des zweiten Geräts.
- **Geklärt (kein Code nötig):** Home Assistant entfernt beim Löschen eines
  Config-Entry automatisch Gerät + alle zugehörigen Entities aus der
  Registry (`async_clear_config_entry`, Kernverhalten, im tatsächlichen
  HA-Quellcode via `docker exec` verifiziert). Recorder-Verlaufsdaten bleiben
  bewusst erhalten (HA-Design), keine Sonderbehandlung für uns nötig.
- **Neu: `dashboard/generate_dashboard.py`.** Erzeugt
  `askoheat_plus_dashboard.yaml` automatisch aus der aktuellen
  Geräte-/Entity-Registry — eine Ansicht pro eingerichtetem ASKOHEAT+-Gerät,
  beliebig viele. Löst das Problem, dass Lovelace-YAML keine generische
  "pro Gerät eine Karte"-Logik kennt und Entity-IDs sich je Gerät
  unterscheiden (teils mit, teils ohne Bereichs-Präfix). Details:
  [11_dashboard.md](11_dashboard.md).
- `api.py`: Ausnahmebehandlung um `RuntimeError` erweitert (fing zuvor nur
  `aiohttp.ClientError`/`TimeoutError` ab) — beim zweiten Testgerät
  aufgefallen, dass aiohttps "Session is closed" beim Neustart mitten in
  einem laufenden Request als unbehandelter Fehler im Log landete (kosmetisch,
  kein Funktionsfehler, trat nur während des Herunterfahrens auf).
- Am zweiten Testgerät fehlen `gettemperature_calibration.json` und
  `getreg.json` (HTTP 404, vermutlich andere Firmware-Version) — vom
  bestehenden Try/Except pro Sekundär-Endpunkt bereits korrekt als Warnung
  statt Fehler behandelt, keine Änderung nötig.

## 2026-09-25 — Automatisches Aktivieren der Temperatursensoren 1–4, Dashboard-Label-Position korrigiert

- **Temperatursensoren 1–4 automatisch aktiv statt manuell freizuschalten:**
  Andreas' Feedback (Screenshot zeigte Warnsymbole für die deaktivierten
  Sensoren): eine Entity soll aktiviert werden, sobald das Gerät einen
  echten Wert liefert, statt dass man sie manuell in den Entity-Einstellungen
  freischalten muss. `sensor.py` ermittelt jetzt bei jedem Setup live pro
  Gerät, ob `TEMP_SENSOR_1`..`_4` verbunden sind (weder Text `"not connected"`
  noch der numerische Sentinel `9999`) und setzt
  `entity_registry_enabled_default` entsprechend — und reaktiviert dabei
  auch bereits vorhandene, zuvor deaktivierte Entities automatisch, sobald
  sie live einen Wert liefern (kein Entfernen/Neu-Einrichten nötig). Direkt
  gegen beide Testgeräte geprüft: Gerät 1 (AHF280) hat echte Werte für
  Sensor 1–4 → wird jetzt automatisch aktiv; Gerät 2 (SONNENBOOSTER) hat nur
  Sensor 1–3 verbunden (Sensor 4 meldet `"not connected"`) → nur 1–3 werden
  aktiv, 4 bleibt deaktiviert.
- **Dashboard, Bild 1 (Heizstab-Nahaufnahme):** Andreas' Feedback nach
  Screenshot — die Wertfelder (v.a. T1–T3) saßen direkt auf der
  Heizwendel und verdeckten sie. Alle sechs Labels (T0–T4, Heizleistung)
  sitzen jetzt in einer gemeinsamen Spalte rechts neben der Heizwendel
  (`left: 63%`), deren Position pixelgenau anhand von
  `dashboard/images/boiler-sensors.png` verifiziert wurde (die Heizwendel
  reicht in diesem Bildausschnitt nie über `left: 58%` hinaus). Damit bleibt
  die Heizwendel vollständig sichtbar. `dashboard/generate_dashboard.py`
  neu ausführen + `ha core restart`, um die Änderung auf beide
  Geräte-Ansichten anzuwenden.

## 2026-09-26 — Dashboard: ASKOHEAT+-Heizelement freigelegt, Herzschlag-Anzeige

- Andreas' Feedback nach Live-Test: das eigentliche ASKOHEAT+-Heizelement
  (die kleine orangene Wendel neben dem Sensor-Puck, zu unterscheiden von
  der größeren Wärmetauscher-Heizwendel) war in Bild 1 weiterhin von den
  T0-/Heizleistungs-Labels verdeckt, in Bild 2 vom "Stufe"-Label. Beide
  jetzt so verschoben, dass das Element frei sichtbar ist: T0/Heizleistung
  ganz nach links, T1–T4 weiter nach rechts (Bild 1); "Stufe" auf die freie
  Wandfläche neben den Tank (Bild 2). Positionen wieder pixelgenau gegen
  beide Bilder verifiziert.
- Neu: Herzschlag-/Zeitstempel-Zeile ("Zuletzt aktualisiert: vor …") über
  Bild 1, per Jinja-Template aus dem `last_updated` der Heizleistungs-Entity.
- Die bisherige Beschreibungszeile ("Sensor 0 sitzt direkt am Heizstab...")
  über Bild 1 auf Wunsch entfernt, für nicht mehr nötig befunden.

## 2026-09-26 — Dashboard-Feinlayout nach Skizze: T0 neben Element, T1-T4 rechtsbündig, Watt zentriert

- Andreas hat eine mit Pfeilen annotierte Skizze geschickt: T0 soll rechts
  neben das ASKOHEAT+-Heizelement, T1–T4 sauber rechtsbündig mit T0
  ausgerichtet werden, die Heizleistung mittig darunter. Umgesetzt und
  pixelgenau gegen `boiler-sensors.png` verifiziert: T0/T1–T4 jetzt alle bei
  `left: 76%` (T0 bei `top: 65%`, direkt rechts vom Element, das dort bei
  ~49-73% eine Schattenzone bis ~74% hat), Heizleistung bei
  `left: 54%, top: 88%` (mittig unter dem Element, unterhalb jeder
  Schattenzone, durchgehend freie Fläche).

## 2026-09-26 — Gerätefamilie erkennen (ASKOHEAT 2.0 / Classic, mit/ohne EEPROM)

- Neuer Diagnose-Sensor `device_family`: leitet aus dem Präfix von
  `HARDWARE_VERSION` ab, um welche Gerätefamilie es sich handelt (Angaben
  von Andreas/ASKOMA AG) — `RCe` → "ASKOHEAT 2.0 (mit EEPROM)", `HWe` →
  "ASKOHEAT Classic (mit EEPROM)", `HW` → "ASKOHEAT Classic (ohne EEPROM)".
  Gegen beide Testgeräte verifiziert: Gerät 1 meldet `RCe1.0` → "ASKOHEAT
  2.0 (mit EEPROM)", Gerät 2 meldet `HW 1.3` (mit Leerzeichen!) → "ASKOHEAT
  Classic (ohne EEPROM)" — der Präfix-Regex funktioniert unabhängig vom
  Leerzeichen. Standardmäßig deaktiviert, wie die anderen Stammdaten-Sensoren.

## 2026-09-26 — Eingebaute Verknüpfung für Einspeisewert & Leistungsvorgabe

- Andreas' Wunsch: statt nur über die Blueprint soll sich der Einspeisewert
  (und die Leistungsvorgabe) auch direkt in der Integration mit einer
  beliebigen anderen Entity verknüpfen lassen, per Auswahl statt Automation.
- Neuer Options-Flow (`config_flow.py`, `AskoheatOptionsFlow`, erreichbar
  über "⋮ → Konfigurieren"): zwei optionale Entity-Picker
  (`feedin_source_entity_id`, `setpoint_source_entity_id`), Domains
  `sensor`/`number`/`input_number`. Leer lassen = keine Verknüpfung.
- Neues Modul `link.py`: registriert bei gesetzter Verknüpfung einen
  State-Listener (`async_track_state_change_event`) auf die Quell-Entity
  und ruft bei jeder Änderung denselben `number.set_value`-Service auf, den
  auch die manuelle UI-Bedienung nutzt — der bestehende Keep-Alive in
  `number.py` greift dadurch automatisch, ohne eigene Wiederhol-/
  Schreiblogik in `link.py`. Zusätzlich einmalige Synchronisierung direkt
  beim Setup, statt erst auf die nächste Zustandsänderung der Quelle zu
  warten.
- `__init__.py`: `entry.add_update_listener` lädt die Integration automatisch
  neu, sobald sich die Verknüpfung im Options-Flow ändert — kein manueller
  Neustart nötig.
- Bestehende Blueprint (`docs/de/10_automatisierung.md`) bleibt zusätzlich
  bestehen, für Nutzer die eigene Bedingungen/Filter brauchen — jetzt als
  "Alternative", die eingebaute Verknüpfung als empfohlener Standardweg.
- **Architektur/Vorbild:** Pattern 1:1 aus dem bereits im selben
  Home-Assistant-Setup laufenden `froeling_lambdatronic_modbus` übernommen
  (`FroelingOptionsFlowHandler`) statt neu zu erfinden — inkl.
  `add_suggested_values_to_schema` für leerbare Felder statt fester
  `default=`-Werte.
- **Verifikation:** `py_compile` + echter Import-Test (`docker exec`) aller
  betroffenen Dateien, `ha core check` + Neustart ohne Fehler. Ein direkter
  Live-Test über einen manuellen `.storage/core.config_entries`-Eintrag
  wurde versucht, aber verworfen: Home Assistant persistiert Config-Entry-
  Options offenbar ähnlich verzögert/debounced wie die Entity-Registry
  (siehe bekannter Punkt oben) — der manuelle Datei-Edit wurde beim
  nächsten internen Save wieder überschrieben. Der echte End-to-End-Test
  über den Options-Flow-Dialog in der UI steht daher noch aus (durch
  Andreas).

## 2026-09-26 — Installer-Einstellungen als Diagnose-Sensoren (Legionellenschutz, Niedertarif, Wärmepumpe, Timeouts)

- Auf Andreas' Wunsch (Auswahl aus dem `extended.html`-Vorschlag, siehe
  unten) 13 neue read-only Diagnose-Sensoren aus `getwizard.json`:
  Legionellenschutz-Zieltemperatur + Startzeit, Niedertarif-Zeitfenster +
  Zieltemperatur, Einspeise-Zeitfenster, Wärmepumpen-Anforderung Ein-/
  Aus-Stufe + Zieltemperatur, Auto-Abschaltung-Timeout, Auto-Reboot-Zeit,
  Kommunikations-Timeout (Heizstab aus/Reset). `getwizard.json` dafür neu
  als vierter Sekundär-Endpunkt eingebunden (`coordinator.py`,
  `AskoheatSecondaryData.wizard`) — wie die anderen drei nur einmalig beim
  Start geladen, keine zusätzliche Poll-Last. Alle standardmäßig
  deaktiviert wie die übrigen Stammdaten-Sensoren. Werte gegen den echten
  Gerätedump verifiziert (`docker exec` mit dem tatsächlichen
  `getwizard.json`-Inhalt), alle 13 Werte stimmen exakt.
- **Vorerst bewusst nur lesend, kein Schreibzugriff:** beim Untersuchen von
  `extended.html`/`Jxfunc.js` gefunden, dass Schreiben über
  `POST http://<host>/server1/` mit JSON-Body passiert (nicht der Geräte-
  Root, wie zunächst vermutet — steht in `Jbootloader.js`, `xBASEURL`).
  Das Server-Log deutet auf ein reines Delta/Merge hin ("Sende nur
  Batch-Änderungen"), aber das ist **noch nicht sicher verifiziert** — ein
  geplanter No-Op-Testschreibvorgang gegen das echte Testgerät wurde vom
  Sandbox-Sicherheitssystem zurecht blockiert (echter Schreibzugriff auf
  reale Hardware ohne Andreas' direkte Freigabe). Schreibbare `number`/
  `time`-Entities für diese Einstellungen sind der nächste Schritt, sobald
  die Merge-vs-Replace-Frage sicher geklärt ist (am besten: Andreas ändert
  testweise selbst einen unkritischen Wert über `extended.html` und wir
  vergleichen `getwizard.json` davor/danach).

## 2026-09-26 — Schreibzugriff auf Installer-Einstellungen + Dashboard-Grafen/IP

- **Schreibzugriff-Frage geklärt:** Andreas hat für sein Testgerät (`.54`)
  ausdrücklich die Freigabe erteilt, direkt live zu testen ("hier kann
  nichts passieren"). Live-Verifikation von `POST /server1/`:
  - No-Op-Schreiben (`AUTO_REBOOT_HOUR` unverändert zurückgesendet) +
    vollständiger Vorher/Nachher-Diff aller Felder → nur der ohnehin
    tickende `SOFTWARE_UPDATE`-Countdown-Text änderte sich. Bestätigt:
    **reines Merge**, kein Ersetzen des restlichen Konfigurationsstands.
  - Wert geändert (`AUTO_REBOOT_HOUR` 2→3), 65s gewartet, erneut
    abgefragt: Wert blieb bei 3. Bestätigt: **kein 60s-Verfall** wie bei
    den Inline-Commands (heater step/load setpoint/load feedin) — kein
    Keep-Alive nötig. Danach auf den Originalwert zurückgesetzt.
  - Details/Beispiel-Request: [02_api-referenz.md](02_api-referenz.md),
    Abschnitt "Installer-Einstellungen schreiben".
- Die 12 zuvor read-only Diagnose-Sensoren aus dem letzten Eintrag (außer
  Kommunikations-Timeout, siehe unten) sind jetzt **schreibbare Entities**:
  6 neue `number`-Entities (`number.py`, `AskoheatWizardNumber`) und 6 neue
  `time`-Entities (neue Datei `time.py`, `AskoheatWizardTime`) für
  Legionellenschutz-Zieltemperatur/-Startzeit, Niedertarif-Zeitfenster +
  Zieltemperatur, Einspeise-Zeitfenster, Wärmepumpen-Anforderung Ein-/
  Aus-Stufe + Zieltemperatur, Auto-Abschaltung-Timeout, Auto-Reboot-Zeit.
  `api.py` bekam dafür `async_write_wizard()`. Nach jedem Schreiben wird
  `coordinator.secondary.wizard` sofort mit der vollständigen Geräte-
  Antwort aktualisiert (kein Warten auf den nächsten Poll).
- **Kommunikations-Timeout bleibt bewusst read-only** — ausdrücklicher
  Wunsch von Andreas, da ein Fehlwert hier die Geräte-Kommunikation
  lahmlegen könnte.
- Neue Plattform `Platform.TIME` in `__init__.py` registriert.
- Live gegen beide bei Andreas eingerichteten Geräte geprüft (Entity-
  Registry-Eintrag nach Neustart kontrolliert, keine Fehler in `ha core
  logs`).
- Dashboard: zwei neue `history-graph`-Karten pro Geräte-Ansicht
  (Temperaturverlauf Sensor 0–4, Heizleistungsverlauf), Standard
  `hours_to_show: 24` — Andreas' Wunsch von der letzten Runde, jetzt
  umgesetzt (siehe [11_dashboard.md](11_dashboard.md)).
- Dashboard: Geräte-IP-Adresse als zusätzliche Zeile in der Markdown-Karte
  über Bild 1 (`generate_dashboard.py`, aus dem `host`-Feld des jeweiligen
  Config-Entry, nicht aus einer Entity).

## 2026-09-26 — Dashboard: 3-Spalten-Layout

- Nach Andreas' Skizze (Pfeile auf Screenshot): Dashboard von der Standard-
  Masonry-Anordnung auf ein explizites 3-Spalten-Layout umgestellt.
  Fallback-Tabelle ganz links, Zählerschrank-Bild + Heizstab-Bild
  übereinander in der Mitte, die beiden Verlaufs-Grafen rechts. Umgesetzt
  über `type: horizontal-stack` mit zwei verschachtelten
  `type: vertical-stack` (mittlere/rechte Spalte) in
  `generate_dashboard.py` — siehe [11_dashboard.md](11_dashboard.md) für
  Details, warum diese Kartentypen statt der Standard-Masonry-Ansicht.
- **Nachbesserung (Feedback nach Live-Screenshot):** die Spaltenbreiten
  waren winzig — Ursache war, dass die Standard-Masonry-Ansicht die einzige
  Top-Level-Karte (den `horizontal-stack`) auf eine einzelne
  Masonry-Spaltenbreite (~500px) begrenzt hat, in der sich die drei inneren
  Spalten drängen mussten. Behoben durch `type: panel` auf der
  Geräte-Ansicht (gibt der einzigen Karte die volle Breite). Zusätzlich auf
  Wunsch die Reihenfolge in der Mittelspalte getauscht: Heizstab-Bild
  ("Temperaturen & Leistung") jetzt oben, Zählerschrank-Bild darunter.

## 2026-09-26 — Bilder in product_pics/, Bedienungsanleitung, README-Links geprüft

- Andreas hat die 4 HA-Screenshots + 5 Produktbilder diesmal per Datei-
  Kopie ins Container-Dateisystem bereitgestellt (`/home/andreas/`, nicht
  mehr eingefügt/pasted) — alle 9 nach
  `custom_components/askoheat_plus/product_pics/` kopiert.
- Neue Doku [12_bedienung.md](12_bedienung.md) (+ EN:
  [12_usage.md](../en/12_usage.md)): kurzer Rundgang mit den 4 HA-
  Screenshots durch Dashboard, automatisch generierte Geräteseite,
  Neu-Konfigurieren-Dialog und den Verknüpfungen-Options-Flow. Aus dem
  README verlinkt.
- `RC_Einschrauber.png` (Einschraub-Heizkörper-Produktbild) zur
  Wiedererkennung oben ins README eingebunden.
- **README-Links geprüft:** alle Doku-Links im README live gegen die
  GitHub-Seite verifiziert (Ziel-Datei existiert, Seite rendert Inhalt statt
  404) — nichts kaputt gefunden. GitLab konnte ich nicht automatisiert
  gegenprüfen (der Datei-Browser dort ist eine JavaScript-Anwendung, mein
  Fetch-Werkzeug bekommt nur den Lade-Platzhalter zu sehen, unabhängig vom
  tatsächlichen Link-Ziel) — falls dort weiterhin ein konkreter Link nicht
  funktioniert, brauche ich den genauen Link/die Seite von Andreas, um es
  gezielt zu beheben.

## 2026-10-29 — Temperatur-Funktionen + Button "Einstellungen neu laden"

- Auf Andreas' Wunsch (Screenshot der Kachel "Temperatur Funktionen" aus der
  Geräte-Weboberfläche): alle Temperatur-Programme jetzt les- und schreibbar.
  Bitbelegung aus `Jextended.js` der Geräte-Weboberfläche rekonstruiert:
  - "Aktiviert"-Häkchen = Bits in `MODBUS_CON_INPUT_SETTING`
    (`0x0080` WP-Anforderung/Notbetrieb, `0x0200` Minimaltemperatur, `0x0100`
    Niedertarif, `0x0004` Einspeisewert, `0x0008` Leistungsvorgabe, `0x0010`
    Heizstufe), Legionellenschutz = `0x8000` in `MODBUS_CON_LEGIO_SETTING`.
  - Fühler = Bits `0x0001`–`0x0010` in `MODBUS_CON_TEMPERATURE_SETTING`
    (bzw. `MODBUS_CON_LEGIO_SETTING` für Legionellen), Legionellen-Intervall =
    Bits `0x0100`–`0x0800` in `MODBUS_CON_LEGIO_SETTING`.
  - Gegen die Häkchen beider Geräte (Testgerät `192.168.20.54`,
    SONNENBOOSTER `192.168.1.201`) abgeglichen: passt exakt zum Screenshot.
- **Zwei Geräte-Eigenheiten** (keine Einschränkung der Integration, sondern
  so in der Geräte-Firmware): "Temperatur bei Einspeisewert" und "Temperatur
  bei Leistungsvorgabe" teilen sich ein Register
  (`MODBUS_CON_TEMPERATURE_LOAD_SETPOINT`), und alle sechs Fühler-Dropdowns
  schreiben dieselben Bits — es gibt also nur einen gemeinsamen Fühler.
  Daher jeweils nur eine Entity statt zwei bzw. sechs.
- Neu: 7 Schalter (`switch.py`), 3 Auswahl-Entities (neue Plattform
  `select.py`), 4 Number-Entities (Minimaltemperatur, Temperatur bei
  Einspeisewert/Leistungsvorgabe, Temperatur bei Heizstufe,
  Legionellenschutz-Zeitbegrenzung). Details:
  [05_entities.md](05_entities.md), "Temperatur-Funktionen".
- Bitfeld-Schreiben per Read-Modify-Write im Coordinator
  (`async_write_wizard_flags`): vorher `getwizard.json` frisch laden, nur die
  betroffenen Bits ändern, damit in der Geräte-Weboberfläche zwischenzeitlich
  geänderte Bits nicht überschrieben werden.
- **Offener Punkt "Polling der Sekundär-Endpunkte" erledigt:** statt eines
  automatischen Intervalls (Andreas' Wunsch) neuer Button
  `reload_settings` ("Einstellungen neu laden", neue Plattform `button.py`),
  der alle Sekundär-Endpunkte auf Anforderung neu lädt.
- Neue Doku [13_aktualisieren.md](13_aktualisieren.md) (+ EN:
  [13_updating.md](../en/13_updating.md)): wie Nutzer das AddOn bei einer
  neuen GitHub-Version aktualisieren (HACS, manuell, Entwicklungs-Setup),
  plus Release-Ablauf für uns. Entscheidung: kein eigener Update-Mechanismus
  in der Integration — HACS bringt das bereits mit (Update-Entity unter
  "Einstellungen"), Voraussetzung ist ein echtes GitHub-Release pro Version
  (Tag allein reicht nicht).
- **Live-Schreibtest** am Testgerät `192.168.20.54` (mit Andreas'
  ausdrücklicher Freigabe, SONNENBOOSTER nicht angefasst), über die echten
  HA-Services: Schalter Minimaltemperatur ein/aus (`INPUT_SETTING`
  `0x20dc` → `0x22dc` → `0x20dc`), Fühler Sensor 1/0 (`0x0801` → `0x0802` →
  `0x0801`), Legionellen-Intervall wöchentlich/zweiwöchentlich (`0x0401` →
  `0x0201` → `0x0401`), Minimaltemperatur 21/20 °C, Reload-Button. Jeweils
  nur das erwartete Bit geändert, am Ende vollständiger `getwizard.json`-
  Vergleich vorher/nachher: keine Unterschiede.
- **Fix dabei gefunden:** Der erste Versuch scheiterte mit "Server
  disconnected" (nichts geschrieben) — der POST direkt nach dem frischen
  GET erwischte eine vom ESP32 bereits geschlossene Keep-Alive-Verbindung.
  `api.py`: `async_write_wizard` wiederholt den POST bei
  `ServerDisconnectedError` einmal (unbedenklich, absolute Werte =
  idempotent). Danach liefen alle Schritte fehlerfrei.

## 2026-10-29 — Dashboard: Temperatur-Funktionen + Quellen-Auswahl

- Dashboard (`generate_dashboard.py`): neue Karte "Temperatur-Funktionen" in
  der linken Spalte (aufgebaut wie die Kachel der Geräte-Weboberfläche, alles
  direkt bedienbar) und je ein Auswahlfeld "↳ Quelle" unter
  Leistungsvorgabe/Einspeisewert.
- Neue `select`-Entities `feedin_source_select`/`setpoint_source_select`
  (`select.py`): Quell-Entity für Einspeisewert/Leistungsvorgabe direkt im
  Dashboard wählen statt über "⋮ → Konfigurieren". Schreiben die
  Options-Flow-Optionen des Config-Entry (gleiche Einstellung, beide Wege
  synchron); der bestehende Update-Listener lädt die Integration neu und
  `link.py` richtet die Verknüpfung ein. Angeboten werden Leistungs-Entities
  (device_class power bzw. W/kW), ohne die eigenen Entities des Geräts.
- Live am Testgerät `192.168.20.54` getestet (Freigabe Andreas): Quelle
  `sensor.solar_grid_power` gewählt → Einspeisewert folgt dem Sensor, Option
  im Config-Entry gesetzt; "Keine" → Option entfernt, Einspeisewert danach
  auf den Ausgangswert 0 zurückgesetzt.

## 2026-10-29 — Community: Forenbeitrag + HACS-Store-Antrag

- Projekt im Home Assistant Community Forum vorgestellt (Kategorie "Share
  your Projects → Custom Integrations", englisch, mit zwei Screenshots):
  https://community.home-assistant.io/t/askoheat-askoma-pv-heating-element-custom-integration-local-no-cloud/1030960
- Neue Doku [14_community.md](14_community.md) (+ EN:
  [14_community.md](../en/14_community.md)): Übersicht aller Orte mit Link,
  Datum und Status, die veröffentlichten Texte (englisch und deutsch), Stand
  des HACS-Store-Antrags und eine Vorlage zum Eintragen weiterer Foren.
  Aus dem README verlinkt.

## 2026-10-29 — README überarbeitet, Issue-Vorlagen

- README als Startseite neu aufgebaut (Funktionsübersicht, Screenshots, HACS-
  Schnellstart mit "My Home Assistant"-Knopf, getestete Geräte, Hilfe,
  Dokumentations-Tabelle, englische Kurzfassung).
- GitHub-Issue-Formulare (`.github/ISSUE_TEMPLATE/`): "Fehler melden" fragt
  Gerätemodell, Geräte-Firmware, Version der Integration, Home-Assistant-
  Version, Installationsart und Protokoll ab; "Wunsch" für neue Funktionen
  oder Modelle. Zweisprachig beschriftet (DE/EN). Leere Issues sind
  abgeschaltet, stattdessen Verweise auf Forum und Doku. Läuft nur auf GitHub.

## 2026-10-29 — Doku-Durchsicht (Stand v0.10.1)

- Komplette Doku (DE + EN) gegen den Code geprüft: alle 64 Entity-Schlüssel
  sind in `05_entities.md` dokumentiert, keine kaputten Links/Anker, DE und
  EN haben identische Struktur.
- Veraltetes korrigiert: `01_ueberblick` (Phasen 1–5, aktueller Stand),
  `02_api-referenz` (Sekundär-Endpunkte: Start + Button statt "einmalig",
  Offener-Punkt-Absatz erledigt), `03_architektur` (Ordnerstruktur, alle
  Module inkl. `link.py`/`time.py`/`select.py`/`button.py`, drei
  Schreibwege, Datenfluss, Coordinator-Entscheidung), `05_entities`
  (Einleitung, "nicht abgebildet"), `04_installation`, `06_entwicklung`
  (Release-Hinweis, Neustart nach Versionsänderung), `12_bedienung`
  (Karte "Konfiguration"). `08_neuerstellungs-prompt` bleibt bewusst auf dem
  Stand Phase 1, mit Hinweis auf die aktuellen Dokumente.

## Offene Punkte (ToDo)

- **Aufnahme in den offiziellen HACS-Standard-Store:** in Vorbereitung
  (Andreas hat sich 2026-10-29 dafür entschieden). Erledigt: Validierungs-
  Workflow `.github/workflows/validate.yml` (`hacs/action` + `hassfest`),
  GitHub-Beschreibung/Topics, Releases, Marken-Bilder im Ordner `brand/`
  (eine separate PR bei `home-assistant/brands` ist dafür nicht mehr nötig).
  **PR eingereicht (2026-10-29):** https://github.com/hacs/default/pull/12952
  (Eintrag in der Datei `integration`, alphabetisch einsortiert, Vorab-Checks
  Sorted/JSON-Schema/Preflight grün). Offen: Review der HACS-Maintainer
  (Dauer nicht planbar), auf Rückfragen dort antworten, die PR bis dahin
  nicht mehr ändern. Release v0.10.1 wurde eigens nach dem ersten grünen
  Workflow-Lauf erstellt (Checklisten-Punkt der PR-Vorlage).
- **Relais-Zähler/Saldo** (`STATUS_FLAGS.HEATER_1_RELAY` etc.) noch nicht als
  einzelne Sensoren abgebildet — Freitext-Parsing bewusst auf später verschoben.
- **EW-Sperre (`128`) / direkte Heizstufen-Pfade (`0`–`19`):** nicht als eigene
  Entities abgebildet, nur die reguläre Ziel-Heizstufe.
