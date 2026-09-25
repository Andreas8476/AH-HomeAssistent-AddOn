# 04 — Installation

Zwei Repositories, ein Stand: **[GitLab](https://gitlab.com/SyberAlf/ah-homeassistent-addon)**
ist das Haupt-Repo, **[GitHub](https://github.com/Andreas8476/AH-HomeAssistent-AddOn)**
ist ein öffentlicher Spiegel — nötig, weil **HACS ausschließlich öffentliche
GitHub-Repositories** unterstützt ("Only public repositories hosted on GitHub
will be compatible with HACS.", laut offizieller HACS-Doku). Für die
HACS-Installation unten immer die GitHub-URL verwenden.

## Variante A: Installation über HACS (empfohlen für andere Nutzer)

Diese Variante ist komplett von vorn beschrieben — auch wenn du noch nie mit
einem Terminal oder mit HACS gearbeitet hast:

- **Schritt 1:** Terminal-Zugriff einrichten (nur falls noch nicht vorhanden)
- **Schritt 2:** HACS installieren (nur falls noch nicht vorhanden)
- **Schritt 3–5:** ASKOHEAT+ über HACS installieren und einrichten

### Schritt 1 — Terminal-Zugriff einrichten (falls noch nicht vorhanden)

Voraussetzung: dein Home Assistant läuft als **Home Assistant OS** oder
**Supervised** (mit Add-on-Store). Prüfe das, indem du links in der
Seitenleiste nach **"Add-ons"** oder **"Add-on-Store"** unter
**Einstellungen** suchst — ist das nicht vorhanden (reines "Home Assistant
Container"/"Core"), überspringe diesen Schritt und nutze direkt die
terminallose Alternative weiter unten.

1. Links in der Seitenleiste auf **Einstellungen** klicken.
2. Dort auf **Add-ons** klicken.
3. Unten rechts auf den blauen Button **Add-on-Store** klicken.
4. Oben im Suchfeld **"Terminal"** eingeben.
5. Das Add-on **"Terminal & SSH"** anklicken (offizielles Home-Assistant-
   Add-on, kein Zusatz-Repository nötig). Falls es nicht auftaucht,
   funktioniert alternativ auch **"Advanced SSH & Web Terminal"** genauso —
   dafür muss ggf. erst ein zusätzliches Add-on-Repository hinzugefügt
   werden, siehe <https://github.com/hassio-addons/repository>.
6. Oben rechts auf **Installieren** klicken und warten, bis die Installation
   abgeschlossen ist (kann 1–2 Minuten dauern, ein Fortschrittsbalken zeigt
   den Stand).
7. Nach der Installation: den Schalter **"Beim Start starten"** aktivieren
   (empfohlen, damit das Terminal nach einem Neustart automatisch verfügbar
   ist), danach oben auf **Starten** klicken.
8. In der linken Seitenleiste erscheint jetzt ein neuer Menüpunkt
   (**"Terminal"** bzw. **"SSH & Web Terminal"**). Anklicken öffnet eine
   Kommandozeile direkt im Browser — dort im nächsten Schritt den
   HACS-Installationsbefehl eingeben.

### Schritt 2 — HACS installieren (falls noch nicht vorhanden)

Falls in deiner Home Assistant Instanz unter **Einstellungen → Geräte &
Dienste** noch kein "HACS" auftaucht:

1. Im Terminal aus Schritt 1 (oder per SSH, falls du das bevorzugst) folgenden
   Befehl eingeben und mit Enter bestätigen:
   ```sh
   wget -O - https://get.hacs.xyz | bash -
   ```
   Das Skript lädt HACS herunter und richtet es automatisch ein. Am Ende
   sollte eine Erfolgsmeldung erscheinen.

   **Alternative ganz ohne Terminal-Add-on:** HACS-ZIP von
   <https://github.com/hacs/integration/releases/latest> herunterladen, den
   darin enthaltenen Ordner `hacs` über das **"File editor"**-Add-on (oder per
   Samba/Netzwerkfreigabe) nach `<config>/custom_components/hacs/`
   hochladen/kopieren. Ausführliche, bebilderte Anleitung:
   <https://hacs.xyz/docs/use/download/download/>.
2. Home Assistant neu starten: **Einstellungen → System → Neu starten**
   (oder auf diesem Host per Terminal: `ha core restart`).
3. Nach dem Neustart: **Einstellungen → Geräte & Dienste → Integration
   hinzufügen** (blauer Button unten rechts) → **"HACS"** eingeben und
   auswählen.
4. Dem Einrichtungsdialog folgen — HACS verlangt eine Anmeldung über ein
   **GitHub-Konto** (falls noch keins vorhanden: kostenlos anlegbar unter
   <https://github.com/signup>). Der Dialog zeigt einen Code an; diesen auf
   <https://github.com/login/device> eingeben und den HACS-Zugriff im
   Browser bestätigen.
5. Nach Abschluss erscheint **"HACS"** als neuer Menüpunkt in der
   Seitenleiste.

Ausführliche, aktuelle Anleitung falls etwas abweicht: <https://hacs.xyz/docs/use/download/download/>.

### Schritt 3 — ASKOHEAT+ als benutzerdefiniertes Repository hinzufügen

HACS kennt dieses Projekt nicht automatisch (kein Eintrag im offiziellen
HACS-Standard-Store) — es muss einmalig als **Custom Repository** eingetragen
werden:

1. In der Seitenleiste **HACS** öffnen.
2. Oben rechts die drei Punkte (⋮) → **Benutzerdefinierte Repositories**
   ("Custom repositories").
3. **Repository-URL:** `https://github.com/Andreas8476/AH-HomeAssistent-AddOn`
4. **Kategorie:** `Integration`
5. **Hinzufügen** klicken.

### Schritt 4 — Installieren

1. In HACS nach **"ASKOHEAT+"** suchen (jetzt als Ergebnis sichtbar).
2. Öffnen → **Herunterladen/Download** → aktuellste Version wählen → installieren.
3. Home Assistant neu starten, wenn HACS danach fragt (`ha core restart`).

### Schritt 5 — Einrichten (gilt für alle Installationsvarianten)

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
4. Weiter wie oben ab "Schritt 5 — Einrichten".

## Variante C: Lokale Entwicklung auf diesem Host (aktueller Stand)

Der Code liegt bereits unter `/homeassistant/askoheat_plus/` und ist per
Symlink in `custom_components/` eingehängt (siehe [03_architektur.md](03_architektur.md)) —
für diesen Host ist nichts zu installieren, nur:

1. `ha core check` (Konfiguration validieren)
2. `ha core restart`
3. Weiter wie oben ab "Schritt 5 — Einrichten"

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
