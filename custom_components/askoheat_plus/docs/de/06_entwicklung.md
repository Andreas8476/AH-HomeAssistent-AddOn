# 06 — Entwicklung

*[English version](../en/06_development.md)*

> ⚠️ **VERBINDLICHE REGEL: Jeder Commit geht auf BEIDE Remotes — GitLab
> (`origin`) UND GitHub (`github`).** Kein Push nur auf eines der beiden.
> Grund: GitLab ist das Haupt-Repo, GitHub ist zwingend nötig, damit HACS
> funktioniert (HACS installiert nur aus öffentlichen GitHub-Repos). Siehe
> Abschnitt "Zwei Git-Remotes" unten für die genauen Befehle.

## Wo der Code liegt

- Repo-Root: `/homeassistant/askoheat_plus/`
- Geladene Integration: `/homeassistant/custom_components/askoheat_plus` (Symlink,
  siehe [03_architektur.md](03_architektur.md))
- Testgerät im lokalen Netz: `192.168.20.54` (frei wählbar beim Einrichten)

## Übliche Befehle

```sh
python3 -m py_compile /homeassistant/askoheat_plus/custom_components/askoheat_plus/*.py
ha core check                 # Konfiguration validieren — immer vor restart
ha core restart                # HA Core neu starten (nötig nach Code-Änderungen)
ha core logs | grep -i askoheat   # Auf Fehler/Tracebacks prüfen
```

Wichtig: `homeassistant` ist auf diesem Host zwar als Namespace-Verzeichnis im
`sys.path`, aber **nicht** als echtes, importierbares Paket vorhanden — ein
`python3 -c "import custom_components.askoheat_plus"` schlägt daher fehl, auch
wenn der Code korrekt ist. Echte Ladefehler zeigen sich ausschließlich über
`ha core restart` + `ha core logs`. Reine Syntaxfehler fängt `py_compile` ab.

## Nach jeder Code-Änderung

1. `python3 -m py_compile ...` (Syntax)
2. `ha core check`
3. `ha core restart`
4. `ha core logs | grep -i askoheat` — insbesondere nach Tracebacks/`ERROR` suchen
5. Falls schon ein Config Entry existiert: prüfen, ob die Entities in der UI noch
   Werte liefern (nicht "nicht verfügbar")

## Gegen das Testgerät verifizieren

```sh
curl -s http://192.168.20.54/gethome.json | python3 -m json.tool | head -50
```

Damit lässt sich unabhängig von Home Assistant prüfen, ob das Gerät erreichbar
ist und welche Felder es aktuell liefert — nützlich, um `value_fn`/Pfade in
`sensor.py`/`binary_sensor.py` gegen echte Daten abzugleichen, bevor man einen
HA-Neustart macht.

## Zwei Git-Remotes: GitLab (`origin`) + GitHub (`github`)

```sh
git push origin main     # Haupt-Repo (GitLab)
git push github main     # Öffentlicher Spiegel für HACS (GitHub)
git push origin <tag>
git push github <tag>
```

Beide sollen immer denselben Stand haben — nach jedem `commit` auf **beide**
Remotes pushen. Grund: HACS installiert ausschließlich aus öffentlichen
GitHub-Repos, siehe [04_installation.md](04_installation.md).

## Fallstricke

- **Symlink nicht kaputt machen:** `/homeassistant/custom_components/askoheat_plus`
  ist ein Symlink. Nicht versehentlich mit `cp`/Editoren in eine echte Kopie
  auflösen — dann laufen Repo und geladene Integration auseinander.
- **Übersetzungen zweisprachig pflegen:** neue `translation_key`s in `sensor.py`/
  `binary_sensor.py` brauchen einen passenden Eintrag in **beiden**
  `translations/de.json` und `translations/en.json`, sonst zeigt HA den rohen
  Key statt eines lesbaren Namens.
- **ESP32 schonen:** keine zusätzlichen Endpunkte leichtfertig in den regulären
  Coordinator-Zyklus (`_async_update_data`) aufnehmen — siehe
  [02_api-referenz.md](02_api-referenz.md), Abschnitt "Abfrage-Strategie".
- **Code-Kommentare/Docstrings auf Deutsch:** unabhängig von der Doku-Sprache
  (siehe [01_ueberblick.md](01_ueberblick.md)) sind Kommentare und Docstrings
  im gesamten Python-Code durchgängig auf Deutsch zu schreiben.
