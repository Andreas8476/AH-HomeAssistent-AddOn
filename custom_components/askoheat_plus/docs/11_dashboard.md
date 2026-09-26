# 11 — Dashboard (Phase 3)

## Was es ist

Ein eigenes, per YAML versioniertes Lovelace-Dashboard "ASKOHEAT+"
(`dashboard/askoheat_plus_dashboard.yaml` im Repo) — **eine eigene Ansicht
(View/Tab) pro eingerichtetem ASKOHEAT+-Gerät**, mit zwei `picture-elements`-
Karten je Ansicht, die Andreas' eigene Askoma-Renderbilder als Hintergrund
zeigen und Live-Werte als Overlay-Labels direkt auf dem Bild positionieren:

- **Karte 1** (`dashboard/images/boiler-sensors.png`): Temperatursensoren
  0–4 (Sensor 0 = immer am Heizstab) sowie die aktuelle Heizleistung, plus
  eine Zeile mit dem Zeitpunkt der letzten Aktualisierung ("Herzschlag").
- **Karte 2** (`dashboard/images/boiler-meter.png`): Ziel-Heizstufe am Tank,
  Leistungsvorgabe und Einspeisewert am Zählerschrank im Bild.
- Zusätzliche **Fallback-Tabellenkarte** mit denselben Werten als normale
  Liste (falls die Bild-Overlays mal nicht laden oder man es lieber tabellarisch mag).

**Label-Positionen (Bild 1):** Der Tank enthält zwei optisch unterscheidbare
Teile: die große Heizwendel (Wärmetauscher-Spirale) und das eigentliche
ASKOHEAT+-Heizelement (die kleinere orangene Wendel darunter/dahinter, direkt
neben dem weißen Sensor-Puck). T1–T4 sitzen rechts neben der großen Wendel;
T0 und die Heizleistung sitzen bewusst weit links, weil ihre alte Position
in der Mitte genau das ASKOHEAT+-Heizelement verdeckt hat (Feedback nach
Screenshot-Review). Auf Bild 2 wurde "Stufe" aus demselben Grund vom Tank
weg auf die freie Wand-/Bodenfläche verschoben.

**Herzschlag/Zeitstempel:** Die Markdown-Karte über Bild 1 zeigt
`Zuletzt aktualisiert: vor …` als Jinja-Template, ausgelesen aus dem
`last_updated`-Zeitstempel der Heizleistungs-Entity (Teil des regulär
gepollten `gethome.json` — spiegelt also den letzten erfolgreichen
Poll-Zyklus wider, nicht nur "Integration läuft").

**Wichtiger Hinweis zu den Bildern:** Es sind Andreas' eigene, unveränderte
Original-Renderbilder von Askoma — ich habe keine Möglichkeit, neue Bilder zu
erzeugen. Die Positionierung der Overlay-Labels (Prozent-Koordinaten) ist ein
sinnvoller Startpunkt, keine Präzisionsmessung realer Sensorpositionen. Für
mehrere Geräte wird aktuell für jede Ansicht **dasselbe** Bildpaar verwendet
(kein Foto pro Gerätemodell verfügbar) — inhaltlich aber korrekt getrennt,
da jede Ansicht auf die Entities des jeweiligen Geräts zeigt.

## Mehrere Heizstäbe: automatisch generiert, nicht von Hand gepflegt

**Das Problem:** Lovelace-YAML kann nicht "für jedes ASKOHEAT+-Gerät eine
Karte" generisch ausdrücken — `picture-elements`-Elemente brauchen konkrete
Entity-IDs, und die hängen vom Artikelnamen des jeweiligen Geräts ab (der
erst nach dem Einrichten bekannt ist). Zwei Geräte können dabei sogar
unterschiedlich benannte IDs für dasselbe Feld bekommen (z.B. mit/ohne
Bereichs-Präfix, je nachdem ob dem Gerät beim Erstellen der Entities schon
ein Home-Assistant-Bereich zugewiesen war) — von Hand pflegen ist also
sowohl mühsam als auch fehleranfällig.

**Die Lösung:** [`dashboard/generate_dashboard.py`](../../../dashboard/generate_dashboard.py) —
ein Skript, das `askoheat_plus_dashboard.yaml` **komplett neu erzeugt**,
indem es direkt in Home Assistants eigener Registry
(`.storage/core.config_entries` + `.storage/core.entity_registry`) nachschaut,
welche ASKOHEAT+-Geräte aktuell eingerichtet sind, und für jedes automatisch
eine eigene Ansicht mit den korrekten Entity-IDs baut.

```sh
python3 /homeassistant/askoheat_plus/dashboard/generate_dashboard.py
ha core check && ha core restart
```

**Wann ausführen:** nach jedem Hinzufügen, Entfernen oder Umbenennen eines
ASKOHEAT+-Geräts. Das Skript überschreibt die Datei jedes Mal komplett neu
aus dem aktuellen Registry-Stand — keine Handbearbeitung nötig, aber auch
keine von Hand vorgenommenen Anpassungen (z.B. verschobene Label-Positionen)
bleiben über einen Neu-Lauf hinweg erhalten. Wer Positionen dauerhaft anders
haben möchte, passt die Koordinaten-Konstanten (`SENSOR_ELEMENTS`,
`METER_ELEMENTS`) direkt im Skript an, nicht in der generierten YAML-Datei.

**Warum ein Skript statt einer generischen Lovelace-Karte/Custom-Card:** Eine
"für-jedes-Gerät"-Logik direkt in Lovelace würde eine eigene JavaScript-
Custom-Card erfordern (deutlich mehr Aufwand/Wartung als ein 150-Zeilen-
Python-Skript, das man bei Bedarf einmal laufen lässt).

## Warum ein eigenes YAML-Dashboard (statt UI-Dashboard)

Alle bisherigen Dashboards in diesem HA-Setup (`stegi-home`,
`solar-manager-v2`, `home-uebersicht`) sind UI-verwaltet
(`.storage/lovelace.*`). Für ASKOHEAT+ gibt es stattdessen ein **eigenes,
separates YAML-Mode-Dashboard**, registriert über einen neuen `lovelace:`-
Block in `configuration.yaml`:

```yaml
lovelace:
  dashboards:
    askoheat-plus:
      mode: yaml
      filename: askoheat_plus/dashboard/askoheat_plus_dashboard.yaml
      title: ASKOHEAT+
      icon: mdi:radiator
      show_in_sidebar: true
```

Vorteil: komplett versioniert im Projekt-Repo (passt zum "alles an einem
Ort"-Prinzip), rührt die bestehenden UI-Dashboards nicht an.

## Bilder müssen zusätzlich nach `www/` kopiert werden

**Wichtige Einschränkung, die die ursprüngliche Symlink-Idee (wie bei
`custom_components/`) verhindert hat:** Home Assistants statischer
Datei-Server (`/local/` → `<config>/www/`) folgt aus Sicherheitsgründen
**keinen Symlinks, die aus `www/` herauszeigen** — ein Versuch, die Bilder
nur per Symlink aus `dashboard/images/` nach `www/askoheat_plus/`
einzuhängen, ergab durchgehend `404`.

Deshalb: die Bilder liegen **zusätzlich als echte Kopie** unter
`/homeassistant/www/askoheat_plus/` (nicht Teil des Git-Repos, da außerhalb
von `/homeassistant/askoheat_plus/`). Die Master-Kopien im Repo bleiben unter
`dashboard/images/`. **Bei Änderung der Bilder: erneut nach
`www/askoheat_plus/` kopieren:**

```sh
cp /homeassistant/askoheat_plus/dashboard/images/*.png /homeassistant/www/askoheat_plus/
```

## Positionen anpassen

Im Lovelace-UI (nicht im YAML-Editor, siehe oben — wird beim nächsten
Skript-Lauf überschrieben): Dashboard "ASKOHEAT+" öffnen → gewünschte
Geräte-Ansicht/Tab → Stift-Symbol → betroffene `picture-elements`-Karte →
Element auswählen → per Drag&Drop verschieben. Für dauerhafte Änderungen:
Koordinaten in `dashboard/generate_dashboard.py` (`SENSOR_ELEMENTS`/
`METER_ELEMENTS`) anpassen.

## Für andere Nutzer (HACS-Installation)

`generate_dashboard.py` braucht Lese-Zugriff auf
`/homeassistant/.storage/core.config_entries` und `core.entity_registry` —
läuft also direkt auf dem HA-Host (per Terminal-Add-on, siehe
[04_installation.md](04_installation.md)). Vor der Ausführung: eigene Bilder
(oder Andreas' Originale, `dashboard/images/`) nach `www/askoheat_plus/`
kopieren — das passiert nicht automatisch durch HACS.
