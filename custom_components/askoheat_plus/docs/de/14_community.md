# 14 — Community & Verbreitung

*[English version](../en/14_community.md)*

Wo das Projekt vorgestellt wurde, welcher Text dort stand und wo es als
Verzeichnis-Eintrag geführt wird. Neue Foren/Plattformen einfach in die
Tabelle und darunter als eigenen Abschnitt eintragen.

## Übersicht

| Wo | Link | Datum | Status |
|---|---|---|---|
| Home Assistant Community Forum (englisch), Kategorie "Share your Projects → Custom Integrations" | <https://community.home-assistant.io/t/askoheat-askoma-pv-heating-element-custom-integration-local-no-cloud/1030960> | 2026-10-29 | veröffentlicht, noch keine Antworten (Stand Veröffentlichung) |
| HACS-Standard-Store (Aufnahme beantragt) | <https://github.com/hacs/default/pull/12952> | 2026-10-29 | Pull Request offen, wartet auf Review der HACS-Maintainer |

Weitere geplante Orte (noch nicht umgesetzt): deutschsprachiges
Home-Assistant-Forum, Photovoltaik-Foren (Bereich Heizstab/Eigenverbrauch),
Hinweis an Askoma mit der Bitte um Verlinkung.

## Wer antwortet, wo?

- **Fehler und Wünsche:** am liebsten als Issue auf GitHub
  (<https://github.com/Andreas8476/AH-HomeAssistent-AddOn/issues>).
- **Forum und Pull Request:** regelmäßig nach Rückfragen schauen und dort
  antworten. Die Pull Request bei `hacs/default` nicht mehr verändern,
  solange sie läuft.
- **Bei Fehlern/Verbesserungswünschen aus den Antworten:** im Repo beheben,
  neues Release veröffentlichen (siehe [13_aktualisieren.md](13_aktualisieren.md)).

## Home Assistant Community Forum (englisch)

- **Titel:** `ASKOHEAT+ (Askoma PV heating element) custom integration – local, no cloud`
- **Kategorie:** Share your Projects → Custom Integrations
- **Tags:** energy, custom-template, heater
- **Angehängte Bilder:** `HA_AH_Ausschnitt_Dashboard.png`,
  `HA_AH_Ausschnitt_Einstellungen.png` (aus `product_pics/`)
- **Hinweis zum Text:** enthält die Angabe, dass die Integration mit
  Unterstützung von Claude (KI-Assistent) entwickelt wurde — gleichlautend
  mit dem README.

Veröffentlichter Text (Stand 2026-10-29, v0.10.1):

```markdown
Hi everyone,

I built a custom integration for the **ASKOHEAT+ PV heating element by Askoma** and wanted to share it. It talks directly to the device over its local interface, so no cloud is needed.

**What it can do**
- Read all values: temperatures (sensors 0–4), heating power, heater step, status and errors
- Control: heater step, load setpoint, feed-in value, emergency mode
- Link the feed-in value or load setpoint to your meter or inverter sensor without any automation. You can pick the source right in the dashboard.
- Configure all temperature functions of the device's web UI from Home Assistant: heat pump request, minimum temperature, low tariff, feed-in value, load setpoint, heater step, legionella protection (switches, temperatures, time windows, sensor selection)
- Ready-made dashboard with images of the heating element and history graphs, generated automatically per device
- Several devices at once

**Installation:** via HACS as a custom repository (step-by-step guide in the repo, also for beginners). HACS shows updates as usual. I have also submitted it for the HACS default store.

**Tested** with two devices (a flange heater with 19 stages and a 5.2 kW variant). I would be especially happy about feedback from other models.

Repo, docs and screenshots: https://github.com/Andreas8476/AH-HomeAssistent-AddOn

The documentation is available in German and English. The integration was developed with the help of Claude (an AI assistant).

Questions, bugs and wishes are welcome here or as an issue on GitHub.
```

## Deutschsprachiger Text (für deutsche Foren, noch nicht veröffentlicht)

**Titel:** `ASKOHEAT+ (Askoma PV-Heizstab) in Home Assistant – lokal, ohne Cloud`

```markdown
Hallo zusammen,

ich habe eine Integration für den **ASKOHEAT+ PV-Heizstab von Askoma** gebaut und möchte sie hier vorstellen. Sie spricht direkt mit dem Gerät über dessen lokale Schnittstelle, es wird keine Cloud gebraucht.

**Was sie kann**
- Alle Werte lesen: Temperaturen (Sensor 0–4), Heizleistung, Heizstufe, Status und Fehler
- Steuern: Heizstufe, Leistungsvorgabe, Einspeisewert, Notbetrieb
- Den Einspeisewert oder die Leistungsvorgabe direkt mit dem Zähler- oder Wechselrichter-Sensor verknüpfen, ganz ohne Automation. Die Quelle wählst du direkt im Dashboard.
- Alle Temperatur-Funktionen der Geräte-Weboberfläche in Home Assistant einstellen: Wärmepumpenanforderung, Minimaltemperatur, Niedertarif, Einspeisewert, Leistungsvorgabe, Heizstufe, Legionellenschutz (Schalter, Temperaturen, Zeitfenster, Fühler-Auswahl)
- Fertiges Dashboard mit Bildern des Heizstabs und Verlaufsgrafen, automatisch pro Gerät erzeugt
- Mehrere Geräte gleichzeitig

**Installation:** über HACS als benutzerdefiniertes Repository (die Schritt-für-Schritt-Anleitung liegt im Repo, auch für Einsteiger). Updates meldet HACS wie gewohnt. Für den HACS-Standard-Store ist die Aufnahme beantragt.

**Getestet** mit zwei Geräten (ein Flansch-Heizstab mit 19 Stufen und eine 5,2-kW-Variante). Über Rückmeldungen mit anderen Modellen freue ich mich besonders.

Repo, Doku und Screenshots: https://github.com/Andreas8476/AH-HomeAssistent-AddOn

Die Doku gibt es auf Deutsch und Englisch. Die Integration habe ich mit Unterstützung von Claude (KI-Assistent) entwickelt.

Fragen, Fehler und Wünsche gern hier oder als Issue auf GitHub.
```

## HACS-Standard-Store

- **Pull Request:** <https://github.com/hacs/default/pull/12952> (Eintrag
  `Andreas8476/AH-HomeAssistent-AddOn` in der Datei `integration`).
- **Eingereicht:** 2026-10-29, mit Release v0.10.1 (nach den ersten grünen
  Läufen von HACS-Action und hassfest erstellt, wie es die Vorlage verlangt).
- **Danach:** Review der HACS-Maintainer, Dauer nicht planbar. Nach der
  Aufnahme erscheint ASKOHEAT+ direkt in der HACS-Suche, ohne dass man ein
  benutzerdefiniertes Repository eintragen muss — dann
  [04_installation.md](04_installation.md) entsprechend vereinfachen.

## Neuen Ort eintragen (Vorlage)

```markdown
## <Name der Plattform>

- **Link:** <URL>
- **Datum:** <JJJJ-MM-TT>
- **Kategorie/Tags:** …
- **Besonderheiten:** (Regeln der Plattform, angehängte Bilder, …)
- **Text:** (veröffentlichten Text hier einfügen)
```
