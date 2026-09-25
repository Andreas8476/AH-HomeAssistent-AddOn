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

## Offene Punkte

- **Polling-Frequenz der Sekundär-Endpunkte** (`getwizard_status.json`,
  `gettemperature_calibration.json`, `getreg.json`): aktuell nur einmalig beim
  Start, kein Refresh danach. Muss laut Andreas später genauer betrachtet
  werden (eigenes langsames Intervall? Options-Flow-Einstellung? Reconnect-
  Trigger?).
- **Relais-Zähler/Saldo** (`STATUS_FLAGS.HEATER_1_RELAY` etc.) noch nicht als
  einzelne Sensoren abgebildet — Freitext-Parsing bewusst auf später verschoben.
- **Phase 3 — Dashboard:** Lovelace-Dashboard mit Heizstab-Bildern je Modell.
  Noch nicht begonnen.
- **Keep-Alive für gesetzte Werte:** bewusst nicht automatisiert (siehe oben) —
  falls gewünscht, später als optionale HA-Automation dokumentieren/anbieten.
- **EW-Sperre (`128`) / direkte Heizstufen-Pfade (`0`–`19`):** nicht als eigene
  Entities abgebildet, nur die reguläre Ziel-Heizstufe.
- Verwaiste Entity-Registry-Einträge (`sensor..._soll_heizstufe`,
  `sensor..._soll_einspeisewert`, Status `unavailable`) noch manuell zu
  entfernen.
