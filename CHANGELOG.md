# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden hier festgehalten.

Format angelehnt an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
Versionierung nach [Semantic Versioning](https://semver.org/lang/de/) (die
Versionsnummer steht auch in `custom_components/askoheat_plus/manifest.json`).

Ausführlichere, erzählende Projekt-Historie (inkl. Begründungen/Entscheidungen):
[`custom_components/askoheat_plus/docs/07_changelog.md`](custom_components/askoheat_plus/docs/07_changelog.md).

## [Unreleased]

## [0.7.0] - 2026-09-25

### Hinzugefügt

- `dashboard/generate_dashboard.py`: erzeugt das Dashboard automatisch aus
  der aktuellen Geräte-Registry — eine Ansicht pro eingerichtetem
  ASKOHEAT+-Gerät, unterstützt beliebig viele Geräte.

### Geändert

- `api.py`: robustere Fehlerbehandlung (`RuntimeError` bei geschlossener
  Session während Neustart wird jetzt sauber als `AskoheatApiError`
  behandelt statt ungefangen durchzuschlagen).

### Bekannt

- Home Assistant entfernt Geräte/Entities beim Löschen eines Config-Entry
  bereits automatisch (Kernverhalten) — keine Änderung an dieser Integration
  nötig. Recorder-Verlaufsdaten bleiben bewusst erhalten.

## [0.6.0] - 2026-09-25

### Hinzugefügt

- ASKOMA-Markenbilder (`custom_components/askoheat_plus/brand/`): `icon.png`,
  `icon@2x.png`, `logo.png`, `dark_logo.png`, `dark_logo@2x.png`.
- Nachträgliche Rekonfiguration: Host/Port/Abfrageintervall über "Geräte &
  Dienste → ASKOHEAT+ → Neu konfigurieren" jederzeit änderbar, nicht mehr nur
  beim Ersteinrichten.

### Geändert

- `docs/04_installation.md`: Schritt-für-Schritt-Anleitung zur Installation
  eines Terminal-Add-ons ergänzt (vorher nur erwähnt, nicht erklärt) sowie
  Hinweis zur nachträglichen Rekonfiguration.
- Dashboard-Label-Abstände korrigiert (Feedback nach Screenshot-Review).

## [0.5.0] - 2026-09-25

### Hinzugefügt

- Phase 3 (Dashboard): eigenes YAML-Mode-Lovelace-Dashboard "ASKOHEAT+" mit
  zwei Bild-Karten (Temperatursensoren 0–4 + Heizleistung am Tank;
  Ziel-Heizstufe/Leistungsvorgabe/Einspeisewert am Zählerschrank), auf Basis
  der vom Nutzer bereitgestellten Askoma-Renderbilder.
- `temperature_sensor_1`..`4`-Sensoren (bisher nur Sensor 0).

### Bekannt

- Dashboard-Bilder müssen manuell nach `www/askoheat_plus/` kopiert werden
  (kein Symlink möglich, siehe `docs/11_dashboard.md`).
- Label-Positionen sind ein Startpunkt, nicht final feinjustiert.

## [0.4.0] - 2026-09-25

### Hinzugefügt

- Neue `switch.emergency_mode`-Entity: steuert den Notbetrieb über die
  parameterlosen `on`/`off`-Endpunkte (physische Taste am Gerät, kein
  60s-Verfall). Live bestätigt gegen das Testgerät.

### Entfernt

- Der read-only Binary-Sensor `emergency_mode` — ersetzt durch die neue
  Switch-Entity (Anzeige + Steuerung in einem).
- Verwaiste Entity-Registry-Einträge aus vorherigen Aufräumarbeiten manuell
  entfernt (Backup der Registry vorher angelegt).

## [0.3.0] - 2026-09-25

### Hinzugefügt

- **Keep-Alive für Number-Entities:** gesetzte Werte werden alle 45s
  automatisch erneut gesendet, solange sie `≠ 0` sind — verhindert den
  geräteseitigen 60s-Auto-Verfall, ohne dass man selbst nachsetzen muss.
  Korrigiert die ursprüngliche 0.2.0-Design-Entscheidung nach Rückmeldung von
  Andreas (Hersteller erwartet ein kontinuierlich steuerndes Gerät).
- Automation-Blueprint `blueprints/askoheat_plus_feedin_from_meter.yaml`, um
  den Einspeisewert automatisch aus einem Zähler-/Wechselrichter-Sensor zu
  befüllen. Anleitung: `docs/10_automatisierung.md`.
- GitHub-Spiegel (`github.com/Andreas8476/AH-HomeAssistent-AddOn`) für die
  HACS-Installation (HACS unterstützt nur GitHub). Ab jetzt wird jeder Commit
  auf beide Remotes gepusht.
- Vollständige HACS-Installationsanleitung inkl. HACS-Ersteinrichtung.
- Attribution: Andreas Stegemann + Claude (Sonnet 5) als Autoren, Hinweis auf
  ASKOMA-AG-Zugehörigkeit (privates Projekt).

## [0.2.0] - 2026-09-25

### Hinzugefügt

- Phase 2 (Steuern): drei `number`-Entities — Ziel-Heizstufe, Leistungsvorgabe,
  Einspeisewert. Schreiben über die dokumentierten Inline-Command-Endpunkte
  (`heater%20step`, `load%20setpoint`, `load%20feedin`), Wertebereiche
  dynamisch vom Gerät (Anzahl Heizstufen/max. Leistung) bzw. int16-Bereich für
  den Einspeisewert.
- Referenzdoku [`09_modbus-status-flags.md`](custom_components/askoheat_plus/docs/09_modbus-status-flags.md):
  Bit-für-Bit-Bedeutung der Modbus-Status-/Fehler-Register, aus der
  offiziellen Registerdoku des Herstellers.

### Entfernt

- Die read-only Diagnose-Sensoren `set_heater_step`/`set_load_feedin` aus
  Phase 1 — ersetzt durch die neuen, gleichnamigen Number-Entities (Anzeige
  + Steuerung in einem).

### Verifiziert

- Phase 1 erfolgreich gegen echtes Testgerät (`192.168.20.54`) geprüft — alle
  Entities liefern plausible Werte.

### Bekannt

- Vom Gerät gesetzte Werte verfallen nach ~60s ohne erneutes Senden
  (Herstellerverhalten) — kein automatischer Keep-Alive implementiert, siehe
  `docs/02_api-referenz.md`.

## [0.1.0] - 2026-09-25

### Hinzugefügt

- Phase 1 (Lesen): Custom Integration mit Config Flow, `DataUpdateCoordinator`
  (pollt `gethome.json`), 13 Sensoren, 5 Binary-Sensoren.
- Vier Sekundär-Endpunkte (`getwizard_status.json`, `gettemperature_calibration.json`,
  `getreg.json`, `getwizard.json` reserviert) werden einmalig beim Start geladen.
- Durchnummerierte Projekt-Doku (`01`–`08`) inkl. Neuerstellungs-Prompt.

### Noch nicht enthalten

- Phase 2: Steuerung/Schreiben (Heizstufe, Leistungsvorgabe, Einspeisewert).
- Phase 3: Lovelace-Dashboard mit Heizstab-Bildern.

[Unreleased]: https://gitlab.com/SyberAlf/ah-homeassistent-addon/-/compare/v0.7.0...main
[0.7.0]: https://gitlab.com/SyberAlf/ah-homeassistent-addon/-/compare/v0.6.0...v0.7.0
[0.6.0]: https://gitlab.com/SyberAlf/ah-homeassistent-addon/-/compare/v0.5.0...v0.6.0
[0.5.0]: https://gitlab.com/SyberAlf/ah-homeassistent-addon/-/compare/v0.4.0...v0.5.0
[0.4.0]: https://gitlab.com/SyberAlf/ah-homeassistent-addon/-/compare/v0.3.0...v0.4.0
[0.3.0]: https://gitlab.com/SyberAlf/ah-homeassistent-addon/-/compare/v0.2.0...v0.3.0
[0.2.0]: https://gitlab.com/SyberAlf/ah-homeassistent-addon/-/compare/v0.1.0...v0.2.0
[0.1.0]: https://gitlab.com/SyberAlf/ah-homeassistent-addon/-/tags/v0.1.0
