# 03 — Architecture

*[Deutsche Version](../de/03_architektur.md) (primary, authoritative)*

## Folder structure

```
/homeassistant/askoheat_plus/                     # repo root (a self-contained git repo)
  README.md
  LICENSE
  hacs.json
  .gitignore
  custom_components/
    askoheat_plus/                                 # <- this is the actual HA integration
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
      brand/                                          # ASKOMA logo (icon/logo, HA 2026.3+ convention)
      docs/
        de/                                          # <- this documentation (authoritative)
        en/                                          # English translation
  dashboard/
    askoheat_plus_dashboard.yaml                      # YAML-mode Lovelace dashboard (phase 3)
    images/
      boiler-sensors.png                                # Andreas' original images
      boiler-meter.png

/homeassistant/custom_components/askoheat_plus       # symlink -> ../askoheat_plus/custom_components/askoheat_plus
/homeassistant/www/askoheat_plus                     # REAL copy of the images (symlink not possible, see 11_dashboard.md)
```

**Why the symlink:** Home Assistant only loads custom integrations from
`/homeassistant/custom_components/<domain>/`. So the project can still exist
as a single, self-contained folder (which can later be pushed 1:1 to
GitHub/GitLab, including README/LICENSE/hacs.json at repo root), the actual
code lives under
`/homeassistant/askoheat_plus/custom_components/askoheat_plus/` and is
mounted via a symlink at `/homeassistant/custom_components/askoheat_plus`.
No file duplication, one source of truth. Git is only initialized inside
`/homeassistant/askoheat_plus/`.

**Exception, dashboard images:** the same symlink trick does **not** work for
`www/askoheat_plus` — Home Assistant's `/local/` file server doesn't follow
symlinks pointing outside `www/` (a security measure). The images therefore
live there as a real, manually synced copy. Details:
[11_dashboard.md](11_dashboard.md).

## Module responsibilities

| File | Responsibility |
|---|---|
| `const.py` | domain, default values, endpoint names, JSON path constants |
| `api.py` | `AskoheatApiClient` — plain HTTP/JSON, no HA knowledge. Helper functions `get_path`, `extract_number`, `parse_active` |
| `coordinator.py` | `AskoheatDataUpdateCoordinator` — polls `gethome.json` regularly, fetches secondary endpoints once, builds `DeviceInfo` |
| `entity.py` | `AskoheatEntity` — shared base class (unique_id, device_info) |
| `config_flow.py` | UI setup: asks for host/port/interval, tests the connection, `unique_id` = `DEVICEID` |
| `sensor.py` / `binary_sensor.py` | declarative entity descriptions (`AskoheatSensorEntityDescription` with `value_fn` + `source`) |
| `number.py` | controllable values (phase 2): reads `SET_INPUTS.*` for display, writes via `AskoheatApiClient.async_send_command`, plus keep-alive |
| `switch.py` | emergency mode on/off: reads `STATUS_FLAGS.EMERGENCY_MODE`, writes via `AskoheatApiClient.async_send_bare_command` (no keep-alive needed) |
| `__init__.py` | `async_setup_entry`/`async_unload_entry`, wires client → coordinator → `entry.runtime_data` → platforms |

## Data flow

```
gethome.json ──┐
               ├─► AskoheatApiClient ──► AskoheatDataUpdateCoordinator ──► entry.runtime_data
secondary endp.┘         (aiohttp,                  (polling every 30s,           │
 (once)              async_get_clientsession)         errors → UpdateFailed)      │
                                                                                   ▼
                                                          sensor.py / binary_sensor.py
                                                          (CoordinatorEntity, value_fn reads
                                                           a path from coordinator.data /
                                                           coordinator.secondary.*)
```

## Write data flow (phase 2)

```
number.py: async_set_native_value(value)
    └─► coordinator.client.async_send_command(command, value)
            └─► GET http://<host>/<command>?value=<value>   (e.g. "heater%20step")
                    └─► on success: coordinator.async_request_refresh()
                            └─► the next gethome.json poll shows the new actual state
```

No separate write coordinator, no confirmation query — the regular
`gethome.json` poll (see data flow above) shows the effect on the next
cycle. Write errors are surfaced to the UI as `HomeAssistantError` (e.g.
device unreachable).

**Keep-alive:** as long as a set value is `≠ 0`, each number entity also
keeps its own `async_track_time_interval` timer (every 45s) that resends the
same command — preventing the manufacturer-documented 60s auto-revert. The
timer lives per entity instance (`_unsub_keepalive`), and is stopped on `0`
or `async_will_remove_from_hass`. Details:
[02_api-reference.md](02_api-reference.md).

## HA conventions deliberately used

- **`entry.runtime_data`** (instead of `hass.data[DOMAIN][entry_id]`) —
  the current recommendation for HA versions from 2024.7 onward, matching
  the 2026.9.3 installed here. Typed via
  `type AskoheatConfigEntry = ConfigEntry[AskoheatDataUpdateCoordinator]`
  in `__init__.py`.
- **`async_get_clientsession(hass)`** instead of our own
  `aiohttp.ClientSession()` — uses HA's managed, shared session (no manual
  closing needed).
- **`CoordinatorEntity`** + a central `DeviceInfo` on the coordinator (not
  duplicated per entity) — a pattern already proven in `goecharger_api2`.
- **Dataclass `EntityDescription` lists** instead of one class per sensor —
  compact, easy to extend for phase 2 (more sensors, `number`/`select` for
  write access).

## Why no multi-coordinator setup (yet)

The four secondary endpoints could have lived more cleanly in their own,
slower coordinators. For phase 1 this was deliberately simplified (one
coordinator, a "first time only" fetch) — see the open point in
[07_changelog.md](07_changelog.md). Should it turn out that this data does
change and needs refreshing, switching to e.g. a second
`DataUpdateCoordinator` with `update_interval=timedelta(minutes=30)` is a
locally contained change in `coordinator.py`.
