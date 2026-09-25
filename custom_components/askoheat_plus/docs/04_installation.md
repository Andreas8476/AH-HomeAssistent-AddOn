# 04 — Installation

Zwei Repositories, ein Stand: **[GitLab](https://gitlab.com/SyberAlf/ah-homeassistent-addon)**
ist das Haupt-Repo, **[GitHub](https://github.com/Andreas8476/AH-HomeAssistent-AddOn)**
ist ein öffentlicher Spiegel — nötig, weil **HACS ausschließlich öffentliche
GitHub-Repositories** unterstützt ("Only public repositories hosted on GitHub
will be compatible with HACS.", laut offizieller HACS-Doku). Für die
HACS-Installation unten immer die GitHub-URL verwenden.

## Variante A: Installation über HACS (empfohlen für andere Nutzer)

### Schritt 1 — HACS installieren (falls noch nicht vorhanden)

Falls in deiner Home Assistant Instanz unter **Einstellungen → Geräte &
Dienste** noch kein "HACS" auftaucht:

1. Terminal-Zugriff auf den HA-Host nötig, z.B. über ein Terminal-Add-on
   ("Advanced SSH & Web Terminal" oder "Terminal & SSH" aus dem offiziellen
   Add-on-Store — falls noch nicht installiert: **Einstellungen → Add-ons →
   Add-on-Store**, dort suchen und installieren). Dort dann:
   ```sh
   wget -O - https://get.hacs.xyz | bash -
   ```
   (Alternative **ganz ohne Terminal-Add-on**: HACS-Ordner manuell über den
   "File editor" oder Samba nach `<config>/custom_components/hacs/`
   entpacken, siehe <https://hacs.xyz/docs/use/download/download/>.)
2. Home Assistant neu starten (`ha core restart`).
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen** → "HACS" suchen.
4. Dem Einrichtungsdialog folgen — HACS verlangt eine Anmeldung über ein
   **GitHub-Konto** (Device-Code-Flow: Code wird angezeigt, auf
   <https://github.com/login/device> eingeben und den HACS-Zugriff bestätigen).
5. Nach Abschluss erscheint "HACS" in der Seitenleiste.

Ausführliche, aktuelle Anleitung falls etwas abweicht: <https://hacs.xyz/docs/use/download/download/>.

### Schritt 2 — ASKOHEAT+ als benutzerdefiniertes Repository hinzufügen

HACS kennt dieses Projekt nicht automatisch (kein Eintrag im offiziellen
HACS-Standard-Store) — es muss einmalig als **Custom Repository** eingetragen
werden:

1. In der Seitenleiste **HACS** öffnen.
2. Oben rechts die drei Punkte (⋮) → **Benutzerdefinierte Repositories**
   ("Custom repositories").
3. **Repository-URL:** `https://github.com/Andreas8476/AH-HomeAssistent-AddOn`
4. **Kategorie:** `Integration`
5. **Hinzufügen** klicken.

### Schritt 3 — Installieren

1. In HACS nach **"ASKOHEAT+"** suchen (jetzt als Ergebnis sichtbar).
2. Öffnen → **Herunterladen/Download** → aktuellste Version wählen → installieren.
3. Home Assistant neu starten, wenn HACS danach fragt (`ha core restart`).

### Schritt 4 — Einrichten (gilt für alle Installationsvarianten)

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
2. **"ASKOHEAT+"** suchen und auswählen.
3. Formular ausfüllen:

   | Feld | Pflicht | Default | Beispiel |
   |---|---|---|---|
   | Host / IP-Adresse | ja | — | `192.168.20.54` |
   | Port | nein | `80` | |
   | Abfrageintervall (Sekunden) | nein | `30` | 10–300s |

4. Absenden — die Integration testet die Verbindung (`gethome.json`) sofort.
   Bei Erfolg wird das Gerät mit Modellname als Titel angelegt, inkl. aller
   Sensoren/Binary-Sensoren/Number-Entities (siehe [05_entities.md](05_entities.md)).

## Variante B: Manuelle Installation (ohne HACS)

1. Repository herunterladen (GitHub- oder GitLab-Link, z.B. "Download ZIP"
   bzw. `git clone`).
2. Den Ordner `custom_components/askoheat_plus/` aus dem Repo nach
   `<HA-Konfigurationsordner>/custom_components/askoheat_plus/` kopieren.
3. Home Assistant neu starten.
4. Weiter wie oben ab "Schritt 4 — Einrichten".

## Variante C: Lokale Entwicklung auf diesem Host (aktueller Stand)

Der Code liegt bereits unter `/homeassistant/askoheat_plus/` und ist per
Symlink in `custom_components/` eingehängt (siehe [03_architektur.md](03_architektur.md)) —
für diesen Host ist nichts zu installieren, nur:

1. `ha core check` (Konfiguration validieren)
2. `ha core restart`
3. Weiter wie oben ab "Schritt 4 — Einrichten"

## Voraussetzungen

- ASKOHEAT+ Gerät im selben lokalen Netz wie Home Assistant, per HTTP erreichbar
  (Standardport 80), keine Authentifizierung notwendig.
- Keine zusätzlichen Python-Pakete (`requirements: []` im Manifest) — es wird
  nur die von Home Assistant bereits mitgebrachte `aiohttp`-Bibliothek genutzt.
- Für Variante A (HACS), falls HACS noch nicht installiert ist: ein
  Terminal-Add-on ("Advanced SSH & Web Terminal" o.ä., aus dem Add-on-Store)
  **oder** Zugriff auf den "File editor"/Samba für die terminallose
  Alternative — plus ein GitHub-Konto zur HACS-Anmeldung (unabhängig vom
  eigenen ASKOHEAT+-Repo). Ist HACS schon installiert, entfällt das.
