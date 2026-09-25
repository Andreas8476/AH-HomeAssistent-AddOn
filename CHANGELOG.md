# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden hier festgehalten.

Format angelehnt an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
Versionierung nach [Semantic Versioning](https://semver.org/lang/de/) (die
Versionsnummer steht auch in `custom_components/askoheat_plus/manifest.json`).

Ausführlichere, erzählende Projekt-Historie (inkl. Begründungen/Entscheidungen):
[`custom_components/askoheat_plus/docs/07_changelog.md`](custom_components/askoheat_plus/docs/07_changelog.md).

## [Unreleased]

### Hinzugefügt

- Referenzdoku [`09_modbus-status-flags.md`](custom_components/askoheat_plus/docs/09_modbus-status-flags.md):
  Bit-für-Bit-Bedeutung der Modbus-Status-/Fehler-Register, aus der
  offiziellen Registerdoku des Herstellers.

### Verifiziert

- Phase 1 erfolgreich gegen echtes Testgerät (`192.168.20.54`) geprüft — alle
  Entities liefern plausible Werte.

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

[Unreleased]: https://gitlab.com/SyberAlf/ah-homeassistent-addon/-/compare/v0.1.0...main
[0.1.0]: https://gitlab.com/SyberAlf/ah-homeassistent-addon/-/tags/v0.1.0
