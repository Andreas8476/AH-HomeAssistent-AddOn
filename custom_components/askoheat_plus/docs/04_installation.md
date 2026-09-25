# 04 — Installation

## Variante A: Lokale Entwicklung auf diesem Host (aktueller Stand)

Der Code liegt bereits unter `/homeassistant/askoheat_plus/` und ist per Symlink
in `custom_components/` eingehängt (siehe [03_architektur.md](03_architektur.md)).
Für diesen Host ist nichts weiter zu installieren — nur:

1. `ha core check` (Konfiguration validieren)
2. `ha core restart`
3. In der HA-Oberfläche: **Einstellungen → Geräte & Dienste → Integration
   hinzufügen → "ASKOHEAT+"** suchen und die Setup-Maske ausfüllen
   (Host/IP, optional Port und Abfrageintervall).

## Variante B: Installation via HACS (sobald auf GitHub veröffentlicht)

Sobald `/homeassistant/askoheat_plus/` als eigenes Repository z.B. unter
`github.com/<user>/ha-askoheat-plus` liegt:

1. HACS → Integrationen → Menü (⋮) → **Benutzerdefinierte Repositories**
2. Repository-URL eintragen, Kategorie **Integration**
3. "ASKOHEAT+" installieren, Home Assistant neu starten
4. Wie oben: Integration über die UI einrichten

## Variante C: Manuelle Installation (ohne HACS)

1. Repository herunterladen/klonen
2. Den Ordner `custom_components/askoheat_plus/` aus dem Repo nach
   `<HA-Konfigurationsordner>/custom_components/askoheat_plus/` kopieren
3. Home Assistant neu starten
4. Wie oben: Integration über die UI einrichten

## Voraussetzungen

- ASKOHEAT+ Gerät im selben lokalen Netz wie Home Assistant, per HTTP erreichbar
  (Standardport 80), keine Authentifizierung notwendig.
- Keine zusätzlichen Python-Pakete (`requirements: []` im Manifest) — es wird
  nur die von Home Assistant bereits mitgebrachte `aiohttp`-Bibliothek genutzt.

## Setup-Formular

| Feld | Pflicht | Default | Bemerkung |
|---|---|---|---|
| Host / IP-Adresse | ja | — | z.B. `192.168.20.54` |
| Port | nein | `80` | |
| Abfrageintervall (Sekunden) | nein | `30` | 10–300s, siehe [02_api-referenz.md](02_api-referenz.md) |

Beim Absenden wird eine Testabfrage (`gethome.json`) durchgeführt. Schlägt sie
fehl, erscheint ein Fehlerhinweis im Formular statt eines fehlgeschlagenen
Config-Entry.
