# 11 — Dashboard (Phase 3)

## Was es ist

Ein eigenes, per YAML versioniertes Lovelace-Dashboard "ASKOHEAT+"
(`dashboard/askoheat_plus_dashboard.yaml` im Repo), das zwei
`picture-elements`-Karten mit Andreas' eigenen Askoma-Renderbildern als
Hintergrund zeigt und Live-Werte als Overlay-Labels direkt auf dem Bild
positioniert:

- **Karte 1** (`dashboard/images/boiler-sensors.png`): Temperatursensoren
  0–4 (Sensor 0 = immer am Heizstab) sowie die aktuelle Heizleistung, verteilt
  entlang der Heizwendel im Bild.
- **Karte 2** (`dashboard/images/boiler-meter.png`): Ziel-Heizstufe am Tank,
  Leistungsvorgabe und Einspeisewert am Zählerschrank im Bild.
- Zusätzliche **Fallback-Tabellenkarte** mit denselben Werten als normale
  Liste (falls die Bild-Overlays mal nicht laden oder man es lieber tabellarisch mag).

**Wichtiger Hinweis zu den Bildern:** Es sind Andreas' eigene, unveränderte
Original-Renderbilder von Askoma — ich habe keine Möglichkeit, neue Bilder zu
erzeugen oder vorhandene bildbearbeiterisch zu verändern. Die Positionierung
der Overlay-Labels (Prozent-Koordinaten) ist ein sinnvoller Startpunkt, keine
Präzisionsmessung realer Sensorpositionen.

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

Im Lovelace-UI (nicht im YAML-Editor): Dashboard "ASKOHEAT+" öffnen →
Stift-Symbol → betroffene `picture-elements`-Karte → Element auswählen →
per Drag&Drop verschieben, oder direkt `top`/`left` in der YAML-Karten-
Konfiguration ändern (Werte in Prozent der Bildgröße).

## Für andere Nutzer (HACS-Installation)

Die Entity-IDs in `askoheat_plus_dashboard.yaml` sind Andreas' echte IDs
für sein Gerätemodell (AHF280-TI-plus-15.8) und hängen vom eigenen Artikel-
namen ab. Vor Nutzung anpassen: **Einstellungen → Geräte & Dienste →
ASKOHEAT+ → Entitäten**, eigene IDs eintragen. Ebenso müssen eigene Bilder
(oder Andreas' Originale, `dashboard/images/`) nach `www/askoheat_plus/`
kopiert werden — das passiert nicht automatisch durch HACS.
