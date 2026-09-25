# 03 — Architektur

## Ordnerstruktur

```
/homeassistant/askoheat_plus/                     # Repo-Root (künftig eigenständiges Git-Repo)
  README.md
  LICENSE
  hacs.json
  .gitignore
  custom_components/
    askoheat_plus/                                 # <- das ist die eigentliche HA-Integration
      __init__.py
      manifest.json
      const.py
      api.py
      coordinator.py
      entity.py
      config_flow.py
      sensor.py
      binary_sensor.py
      translations/{de,en}.json
      docs/                                          # <- diese Dokumentation

/homeassistant/custom_components/askoheat_plus       # Symlink -> ../askoheat_plus/custom_components/askoheat_plus
```

**Warum der Symlink:** Home Assistant lädt Custom Integrations ausschließlich aus
`/homeassistant/custom_components/<domain>/`. Damit das Projekt trotzdem als ein
einziger, eigenständiger Ordner existiert (der später 1:1 auf GitHub/GitLab
gepusht werden kann, inkl. README/LICENSE/hacs.json auf Repo-Root-Ebene), liegt
der tatsächliche Code unter `/homeassistant/askoheat_plus/custom_components/askoheat_plus/`
und wird per Symlink nach `/homeassistant/custom_components/askoheat_plus`
eingehängt. Kein Datei-Duplikat, eine Quelle der Wahrheit. Git wird nur im
Ordner `/homeassistant/askoheat_plus/` initialisiert.

## Modul-Verantwortlichkeiten

| Datei | Verantwortung |
|---|---|
| `const.py` | Domain, Default-Werte, Endpunkt-Namen, JSON-Pfad-Konstanten |
| `api.py` | `AskoheatApiClient` — reines HTTP/JSON, kein HA-Wissen. Hilfsfunktionen `get_path`, `extract_number`, `parse_active` |
| `coordinator.py` | `AskoheatDataUpdateCoordinator` — pollt `gethome.json` regelmäßig, holt Sekundär-Endpunkte einmalig, baut `DeviceInfo` |
| `entity.py` | `AskoheatEntity` — gemeinsame Basisklasse (unique_id, device_info) |
| `config_flow.py` | UI-Setup: Host/Port/Intervall abfragen, Verbindung testen, `unique_id` = `DEVICEID` |
| `sensor.py` / `binary_sensor.py` | Deklarative Entity-Beschreibungen (`AskoheatSensorEntityDescription` mit `value_fn` + `source`) |
| `__init__.py` | `async_setup_entry`/`async_unload_entry`, verdrahtet Client → Coordinator → `entry.runtime_data` → Plattformen |

## Datenfluss

```
gethome.json ──┐
               ├─► AskoheatApiClient ──► AskoheatDataUpdateCoordinator ──► entry.runtime_data
Sekundär-Endp. ┘         (aiohttp,                  (Polling alle 30s,           │
 (einmalig)          async_get_clientsession)         Fehler → UpdateFailed)     │
                                                                                   ▼
                                                          sensor.py / binary_sensor.py
                                                          (CoordinatorEntity, value_fn liest
                                                           per Pfad aus coordinator.data /
                                                           coordinator.secondary.*)
```

## HA-Konventionen, die bewusst verwendet werden

- **`entry.runtime_data`** (statt `hass.data[DOMAIN][entry_id]`) — aktuelle
  Empfehlung für HA-Versionen ab 2024.7, entspricht dem hier installierten
  2026.9.3. Typisiert über `type AskoheatConfigEntry = ConfigEntry[AskoheatDataUpdateCoordinator]`
  in `__init__.py`.
- **`async_get_clientsession(hass)`** statt eigenem `aiohttp.ClientSession()` —
  nutzt die von HA verwaltete, geteilte Session (kein manuelles Schließen nötig).
- **`CoordinatorEntity`** + zentrale `DeviceInfo` auf dem Coordinator (nicht pro
  Entity dupliziert) — ein Muster, das sich bereits bei `goecharger_api2` bewährt.
- **Dataclass-`EntityDescription`-Listen** statt einer Klasse pro Sensor — kompakt,
  leicht erweiterbar für Phase 2 (weitere Sensoren, `number`/`select` für Schreibzugriff).

## Warum kein Multi-Coordinator-Setup (noch)

Die vier Sekundär-Endpunkte hätten sauberer in eigenen, langsameren Coordinators
leben können. Für Phase 1 wurde das bewusst vereinfacht (ein Coordinator, ein
"nur beim ersten Mal"-Fetch) — siehe offener Punkt in
[07_changelog.md](07_changelog.md). Sollte sich zeigen, dass diese Daten sich
doch ändern und aktualisiert werden müssen, ist die Umstellung auf z.B. einen
zweiten `DataUpdateCoordinator` mit `update_interval=timedelta(minutes=30)`
ein lokal begrenzter Umbau in `coordinator.py`.
