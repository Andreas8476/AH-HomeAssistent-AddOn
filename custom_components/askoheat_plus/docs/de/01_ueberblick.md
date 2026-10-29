# 01 — Überblick

*[English version](../en/01_overview.md)*

## Ziel

Eine Home-Assistant-Integration für den **ASKOHEAT+** PV-Heizstab (Hersteller
[Askoma](https://www.askoma.com)), die dessen lokale, unauthentifizierte
REST-API im Heimnetz ausliest und steuert — inklusive der Einstellungen
der Geräte-Weboberfläche.

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

Das Projekt wurde bewusst in Schritten aufgebaut, alle sind umgesetzt:

1. **Phase 1 — Lesen:** Sensoren/Binary-Sensoren für den aktuellen Zustand
   des Geräts (Heizstufe, Leistung, Temperatur, Status, Fehler).
2. **Phase 2 — Schreiben:** Heizstufe, Leistungsvorgabe und Einspeisewert
   setzen — über die vom Hersteller dokumentierten Inline-Commands, als
   `number`-Entities (mit Keep-Alive), dazu der Notbetrieb-Schalter.
3. **Phase 3 — Dashboard:** eigenes Lovelace-Dashboard mit Andreas'
   Askoma-Renderbildern als Hintergrund und Live-Werten als Overlay.
4. **Phase 4 — Installer-Einstellungen:** schreibbare `number`-/`time`-
   Entities für Legionellenschutz, Niedertarif, Einspeise-Zeitfenster,
   Wärmepumpen-Anforderung usw. über `POST /server1/`.
5. **Phase 5 — Temperatur-Funktionen & Komfort:** alle Temperatur-Funktionen
   der Geräte-Weboberfläche (Schalter, Temperaturen, Fühler,
   Legionellen-Intervall), Quellen-Auswahl für Einspeisewert/Leistungsvorgabe
   direkt im Dashboard und der Button "Einstellungen neu laden".

## Aktueller Stand

Aktuelle Version: **0.10.1** (siehe [CHANGELOG.md](../../../../CHANGELOG.md)).

- [x] Lesen: Sensor-/Binary-Sensor-Entities, Config Flow über die UI, Polling
      von `gethome.json`, Sekundär-Endpunkte beim Start und per Button.
- [x] Steuern: `number`-Entities (Ziel-Heizstufe, Leistungsvorgabe,
      Einspeisewert) mit Keep-Alive gegen den 60s-Verfall, Notbetrieb-Schalter,
      Verknüpfung mit einem Zähler/Wechselrichter über Options-Flow,
      Dashboard-Auswahl oder Blueprint, siehe [05_entities.md](05_entities.md)
      und [10_automatisierung.md](10_automatisierung.md).
- [x] Installer-Einstellungen und Temperatur-Funktionen: schreibbare
      `number`-/`time`-/`switch`-/`select`-Entities, siehe
      [05_entities.md](05_entities.md).
- [x] Dashboard: YAML-Lovelace-Dashboard pro Gerät mit Bild-Karten,
      Verlaufsgrafen und der Karte "Temperatur-Funktionen", siehe
      [11_dashboard.md](11_dashboard.md).
- [x] Aktualisieren und Community: [13_aktualisieren.md](13_aktualisieren.md),
      [14_community.md](14_community.md).

## Testumgebung

Lokales Testgerät im Heimnetz von Andreas: `192.168.20.54` (Host ist in der
Integration frei konfigurierbar, nicht hart kodiert).

## Weiterführende Dokumente

Siehe [docs/de/](.) — durchnummeriert, `02` beginnt mit der API-Referenz.
Englische Übersetzung parallel unter [docs/en/](../en/).

## Autor

Andreas Stegemann, in Zusammenarbeit mit Claude (Anthropic, Sonnet 5) als
Coding-Assistent entwickelt. Privates Projekt, keine offizielle Software der
ASKOMA AG — Details siehe [README.md](../../../../README.md#autor).
