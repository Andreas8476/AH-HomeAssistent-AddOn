# 01 — Überblick

## Ziel

Eine Home-Assistant-Integration für den **ASKOHEAT+** PV-Heizstab (Hersteller
[Askoma](https://www.askoma.com)), die dessen lokale, unauthentifizierte
REST-API im Heimnetz ausliest und später auch steuert.

## Warum Custom Integration statt Add-on

ASKOHEAT+ spricht eine einfache lokale REST/JSON-API (kein MQTT, kein Cloud-
Zwang). Eine eigene, per HACS/GitHub installierbare **Custom Integration**
(`custom_components/askoheat_plus/`) ist dafür der idiomatische Weg — sie läuft
direkt im Home-Assistant-Prozess, erzeugt native Entities und braucht keinen
eigenen Docker-Container. Zwei bereits bestehende Integrationen im selben
Home-Assistant-Setup lösen strukturell dasselbe Problem (lokales Gerät, Polling,
Config Flow) und dienten als Vorbild:

- [`goecharger_api2`](https://github.com/marq24/ha-goecharger-api2) — go-eCharger Wallbox
- [`froeling_lambdatronic_modbus`](https://github.com/GyroGearl00se/ha_froeling_lambdatronic_modbus) — Pelletheizung

## Phasen

Das Projekt ist bewusst in Schritten angelegt:

1. **Phase 1 — Lesen (dieser Stand)**: Sensoren/Binary-Sensoren, die den
   aktuellen Zustand des Geräts anzeigen (Heizstufe, Leistung, Temperatur,
   Status, Fehler). Kein Schreibzugriff.
2. **Phase 2 — Schreiben** *(noch nicht umgesetzt)*: Heizstufe setzen,
   Leistungsvorgabe setzen, Einspeisewert setzen — über die vom Hersteller
   dokumentierten Inline-Commands (`number`/`select`-Entities oder Services).
3. **Phase 3 — Dashboard** *(noch nicht umgesetzt)*: Ein Lovelace-Dashboard mit
   Bildern passend zum jeweiligen Heizstab-Modell.

## Aktueller Stand

- [x] Phase 1: Integration mit Sensor- und Binary-Sensor-Entities, Config Flow
      über die UI, Polling von `gethome.json`.
- [x] Phase 2: Steuerung/Schreiben — drei `number`-Entities (Ziel-Heizstufe,
      Leistungsvorgabe, Einspeisewert), siehe [05_entities.md](05_entities.md).
- [ ] Phase 3: Dashboard.

## Testumgebung

Lokales Testgerät im Heimnetz von Andreas: `192.168.20.54` (Host ist in der
Integration frei konfigurierbar, nicht hart kodiert).

## Weiterführende Dokumente

Siehe [../docs/](.) — durchnummeriert, `02` beginnt mit der API-Referenz.
