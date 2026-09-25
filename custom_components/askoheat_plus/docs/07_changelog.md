# 07 — Changelog

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

## Offene Punkte

- **Polling-Frequenz der Sekundär-Endpunkte** (`getwizard_status.json`,
  `gettemperature_calibration.json`, `getreg.json`): aktuell nur einmalig beim
  Start, kein Refresh danach. Muss laut Andreas später genauer betrachtet
  werden (eigenes langsames Intervall? Options-Flow-Einstellung? Reconnect-
  Trigger?).
- **Relais-Zähler/Saldo** (`STATUS_FLAGS.HEATER_1_RELAY` etc.) noch nicht als
  einzelne Sensoren abgebildet — Freitext-Parsing bewusst auf später verschoben.
- **Phase 2 — Schreiben:** Heizstufe/Leistungsvorgabe/Einspeisewert setzen, über
  die in [02_api-referenz.md](02_api-referenz.md) referenzierten Inline-Commands.
  Noch nicht begonnen.
- **Phase 3 — Dashboard:** Lovelace-Dashboard mit Heizstab-Bildern je Modell.
  Noch nicht begonnen.
- `manifest.json`: `codeowners`/`documentation`/`issue_tracker` verweisen auf
  einen Platzhalter-GitHub-Namen (`stegemann-andreas/ha-askoheat-plus`) —
  anpassen, sobald das echte Repository existiert.
