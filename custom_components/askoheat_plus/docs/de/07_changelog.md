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

## Offene Punkte (ToDo)

- **Dashboard-Verlaufsgrafen:** Andreas möchte zwei zusätzliche Grafen im
  Dashboard — Temperaturverlauf (Sensor 0–4) und Heizleistungsverlauf,
  Standardansicht jeweils die letzten 24h. Noch nicht umgesetzt.
- **Schreibzugriff auf Installer-Einstellungen** (siehe oben): Merge- vs.
  Replace-Semantik des `POST /server1/`-Endpunkts muss vor der Umsetzung
  sicher verifiziert werden.

- **Polling-Frequenz der Sekundär-Endpunkte** (`getwizard_status.json`,
  `gettemperature_calibration.json`, `getreg.json`): aktuell nur einmalig beim
  Start, kein Refresh danach. Muss laut Andreas später genauer betrachtet
  werden (eigenes langsames Intervall? Options-Flow-Einstellung? Reconnect-
  Trigger?).
- **Relais-Zähler/Saldo** (`STATUS_FLAGS.HEATER_1_RELAY` etc.) noch nicht als
  einzelne Sensoren abgebildet — Freitext-Parsing bewusst auf später verschoben.
- **EW-Sperre (`128`) / direkte Heizstufen-Pfade (`0`–`19`):** nicht als eigene
  Entities abgebildet, nur die reguläre Ziel-Heizstufe.
