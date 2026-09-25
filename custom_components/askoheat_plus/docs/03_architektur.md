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
      number.py
      switch.py
      translations/{de,en}.json
      brand/                                          # ASKOMA-Logo (icon/logo, HA 2026.3+ Konvention)
      docs/                                          # <- diese Dokumentation
  dashboard/
    askoheat_plus_dashboard.yaml                      # YAML-Mode Lovelace-Dashboard (Phase 3)
    images/
      boiler-sensors.png                                # Andreas' Originalbilder
      boiler-meter.png

/homeassistant/custom_components/askoheat_plus       # Symlink -> ../askoheat_plus/custom_components/askoheat_plus
/homeassistant/www/askoheat_plus                     # ECHTE Kopie der Bilder (kein Symlink möglich, siehe 11_dashboard.md)
```

**Warum der Symlink:** Home Assistant lädt Custom Integrations ausschließlich aus
`/homeassistant/custom_components/<domain>/`. Damit das Projekt trotzdem als ein
einziger, eigenständiger Ordner existiert (der später 1:1 auf GitHub/GitLab
gepusht werden kann, inkl. README/LICENSE/hacs.json auf Repo-Root-Ebene), liegt
der tatsächliche Code unter `/homeassistant/askoheat_plus/custom_components/askoheat_plus/`
und wird per Symlink nach `/homeassistant/custom_components/askoheat_plus`
eingehängt. Kein Datei-Duplikat, eine Quelle der Wahrheit. Git wird nur im
Ordner `/homeassistant/askoheat_plus/` initialisiert.

**Ausnahme Dashboard-Bilder:** Für `www/askoheat_plus` funktioniert derselbe
Symlink-Trick **nicht** — Home Assistants `/local/`-Datei-Server folgt keinen
Symlinks, die aus `www/` herauszeigen (Sicherheitsmaßnahme). Die Bilder
liegen dort deshalb als echte, manuell synchronisierte Kopie. Details:
[11_dashboard.md](11_dashboard.md).

## Modul-Verantwortlichkeiten

| Datei | Verantwortung |
|---|---|
| `const.py` | Domain, Default-Werte, Endpunkt-Namen, JSON-Pfad-Konstanten |
| `api.py` | `AskoheatApiClient` — reines HTTP/JSON, kein HA-Wissen. Hilfsfunktionen `get_path`, `extract_number`, `parse_active` |
| `coordinator.py` | `AskoheatDataUpdateCoordinator` — pollt `gethome.json` regelmäßig, holt Sekundär-Endpunkte einmalig, baut `DeviceInfo` |
| `entity.py` | `AskoheatEntity` — gemeinsame Basisklasse (unique_id, device_info) |
| `config_flow.py` | UI-Setup: Host/Port/Intervall abfragen, Verbindung testen, `unique_id` = `DEVICEID` |
| `sensor.py` / `binary_sensor.py` | Deklarative Entity-Beschreibungen (`AskoheatSensorEntityDescription` mit `value_fn` + `source`) |
| `number.py` | Steuerbare Werte (Phase 2): liest `SET_INPUTS.*` zur Anzeige, schreibt über `AskoheatApiClient.async_send_command`, plus Keep-Alive |
| `switch.py` | Notbetrieb ein/aus: liest `STATUS_FLAGS.EMERGENCY_MODE`, schreibt über `AskoheatApiClient.async_send_bare_command` (kein Keep-Alive nötig) |
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

## Schreib-Datenfluss (Phase 2)

```
number.py: async_set_native_value(value)
    └─► coordinator.client.async_send_command(command, value)
            └─► GET http://<host>/<command>?value=<value>   (z.B. "heater%20step")
                    └─► bei Erfolg: coordinator.async_request_refresh()
                            └─► nächster gethome.json-Poll zeigt den neuen Ist-Zustand
```

Kein separater Schreib-Coordinator, keine Bestätigungsabfrage — der reguläre
`gethome.json`-Poll (siehe Datenfluss oben) zeigt den Effekt beim nächsten
Zyklus. Fehler beim Schreiben werden als `HomeAssistantError` an die UI
durchgereicht (z.B. Gerät nicht erreichbar).

**Keep-Alive:** solange ein gesetzter Wert `≠ 0` ist, hält jede Number-Entity
zusätzlich einen eigenen `async_track_time_interval`-Timer (alle 45s), der
denselben Befehl erneut sendet — verhindert den vom Hersteller dokumentierten
60s-Auto-Verfall. Timer lebt pro Entity-Instanz (`_unsub_keepalive`), wird bei
`0` oder `async_will_remove_from_hass` gestoppt. Details:
[02_api-referenz.md](02_api-referenz.md).

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
