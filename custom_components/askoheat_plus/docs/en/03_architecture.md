# 03 — Architecture

*[Deutsche Version](../de/03_architektur.md) (primary, authoritative)*

## Overview: who talks to whom?

```mermaid
flowchart LR
    subgraph HA["Home Assistant"]
        UI["Dashboard, device page,<br/>automations"]
        SRC["Meter or<br/>inverter sensor"]
        subgraph CC["Custom component askoheat_plus"]
            ENT["Entities<br/>sensor, number, switch,<br/>select, time, button"]
            COORD["Coordinator<br/>polls gethome.json"]
            LINK["link.py<br/>link a source"]
        end
    end
    subgraph DEV["ASKOHEAT+ heating element with ESP32"]
        API["Local REST/JSON interface<br/>HTTP, port 80"]
        HEAT["Heating elements<br/>and relays"]
    end
    UI <--> ENT
    ENT <--> COORD
    SRC -->|"state change"| LINK
    LINK -->|"number.set_value"| ENT
    COORD <-->|"HTTP and JSON,<br/>home network only"| API
    API --- HEAT
```

> [!NOTE]
> **No Modbus on this path:** the integration talks to the heating element exclusively via **HTTP**
> (local REST/JSON interface, unauthenticated, home network only). Names like `MODBUS_CMD_…` or
> `MODBUS_CON_…` are key and register names within this HTTP interface. The heating element
> additionally offers a Modbus interface of its own (TCP/RTU) for other controllers, which this
> integration does **not** use. See [02_api-reference.md](02_api-reference.md) and
> [09_modbus-status-flags.md](09_modbus-status-flags.md).

## Folder structure

```
/homeassistant/askoheat_plus/                     # repo root (self-contained git repo)
  README.md  CHANGELOG.md  LICENSE  hacs.json  .gitignore
  .github/
    workflows/validate.yml                          # HACS action + hassfest (GitHub only)
    ISSUE_TEMPLATE/                                 # bug/feature forms (DE/EN)
  blueprints/
    askoheat_plus_feedin_from_meter.yaml            # alternative to the built-in link
  custom_components/
    askoheat_plus/                                  # <- the actual HA integration
      __init__.py  manifest.json  const.py
      api.py  coordinator.py  entity.py  config_flow.py  link.py
      sensor.py  binary_sensor.py  number.py  switch.py
      time.py  select.py  button.py
      translations/{de,en}.json
      brand/                                        # ASKOMA logo (icon/logo, HA 2026.3+ convention)
      product_pics/                                 # product/screenshot images for README/docs
      docs/
        de/                                         # <- this documentation (authoritative)
        en/                                         # English translation
  dashboard/
    generate_dashboard.py                           # generates the dashboard per device
    askoheat_plus_dashboard.yaml                    # generated, YAML-mode Lovelace dashboard
    images/boiler-sensors.png  boiler-meter.png     # Andreas' original images

/homeassistant/custom_components/askoheat_plus       # Symlink -> ../askoheat_plus/custom_components/askoheat_plus
/homeassistant/www/askoheat_plus                     # REAL copy of the images (no symlink possible, see 11_dashboard.md)
```

> [!NOTE]
> **Why the symlink:** Home Assistant only loads custom integrations from
> `/homeassistant/custom_components/<domain>/`. So the project can still exist
> as a single, self-contained folder (which can later be pushed 1:1 to
> GitHub/GitLab, including README/LICENSE/hacs.json at repo root), the actual
> code lives under
> `/homeassistant/askoheat_plus/custom_components/askoheat_plus/` and is
> mounted via a symlink at `/homeassistant/custom_components/askoheat_plus`.
> No file duplication, one source of truth. Git is only initialized inside
> `/homeassistant/askoheat_plus/`.

> [!WARNING]
> **Exception, dashboard images:** the same symlink trick does **not** work for
> `www/askoheat_plus` — Home Assistant's `/local/` file server doesn't follow
> symlinks pointing outside `www/` (a security measure). The images therefore
> live there as a real, manually synced copy. Details:
> [11_dashboard.md](11_dashboard.md).

## Module responsibilities

| File | Responsibility |
|---|---|
| `const.py` | Domain, defaults, endpoint names, JSON path constants, options-flow keys |
| `api.py` | `AskoheatApiClient` — plain HTTP/JSON, no HA knowledge: GET endpoints, inline commands, `POST /server1/` (`async_write_wizard`, with a single retry on "Server disconnected"). Helpers `get_path`, `extract_number`, `parse_active` |
| `coordinator.py` | `AskoheatDataUpdateCoordinator` — polls `gethome.json` regularly, loads secondary endpoints at startup and on demand (`async_reload_secondary`), writes bits of shared registers via read-modify-write (`async_write_wizard_flags`), builds `DeviceInfo` |
| `entity.py` | `AskoheatEntity` — common base class (unique_id, device_info) |
| `config_flow.py` | UI setup (host/port/interval, connection test, `unique_id` = `DEVICEID`), reconfigure and the options flow for the link |
| `link.py` | Links optional source entities (options) to the feed-in value/load setpoint `number` entities via state listeners and `number.set_value` |
| `sensor.py` / `binary_sensor.py` | Declarative entity descriptions (`AskoheatSensorEntityDescription` with `value_fn` + `source`) |
| `number.py` | Controllable values: `SET_INPUTS.*` via inline commands (with keep-alive) and installer settings/temperatures via `POST /server1/` |
| `time.py` | Installer time windows (hour/minute fields as a single `time` value) via `POST /server1/` |
| `switch.py` | Emergency mode (parameterless commands, no keep-alive) and the "enabled" switches of the temperature functions (single bits of a register) |
| `select.py` | Sensor selection and legionella interval (bit groups of a register) and the source selection for feed-in value/load setpoint (writes the config entry's options) |
| `button.py` | "Reload settings" |
| `__init__.py` | `async_setup_entry`/`async_unload_entry`, wires client → coordinator → `entry.runtime_data` → platforms → links, reloads on options change |

## Data flow

```mermaid
flowchart LR
    HOME["gethome.json<br/>interval, default 30 s"] --> CLIENT
    SEC["Secondary endpoints<br/>start and button"] --> CLIENT
    CLIENT["AskoheatApiClient<br/>aiohttp, shared HA session"] --> COORD
    COORD["Coordinator<br/>errors become UpdateFailed"] --> RT["entry.runtime_data"]
    RT --> ENT["Entities as CoordinatorEntity<br/>value_fn reads a path from<br/>coordinator.data and coordinator.secondary"]
```

> [!CAUTION]
> **Spare the ESP32:** the device is a small microcontroller. Don't add extra endpoints to the regular
> poll (`_async_update_data`) lightly, see [02_api-reference.md](02_api-reference.md), section
> "Polling strategy".

## Write data flow

Three write paths, depending on the kind of value:

```mermaid
flowchart TB
    subgraph W1["Path 1: inline commands with keep-alive"]
        N1["number.py<br/>heater step, load setpoint,<br/>feed-in value"] --> C1["GET command with value"]
        C1 --> R1["Refresh, the next poll<br/>shows the actual state"]
        N1 -.->|"every 45 s while value is not 0"| C1
    end
    subgraph W2["Path 2: installer settings with their own value"]
        N2["number.py and time.py"] --> P2["POST /server1/"]
        P2 --> A2["Response is the new getwizard.json dump<br/>coordinator.secondary.wizard"]
    end
    subgraph W3["Path 3: single bits of shared registers"]
        N3["switch.py and select.py"] --> F3["async_write_wizard_flags"]
        F3 --> G3["load a fresh getwizard.json"]
        G3 --> M3["change only the bits of the mask"]
        M3 --> P3["POST /server1/<br/>only if changed"]
    end
```

Sequence of path 3, using a switch as an example:

```mermaid
sequenceDiagram
    actor U as User
    participant E as Switch or select
    participant C as Coordinator
    participant D as Heating element
    U->>E: toggle the switch
    E->>C: async_write_wizard_flags with register, mask and bits
    C->>D: GET getwizard.json
    D-->>C: current register value
    Note over C: replace only the bits of the mask
    C->>D: POST /server1/ with the new value
    D-->>C: updated getwizard.json dump
    C-->>E: state is current immediately
```

No separate write coordinator, no confirmation query. Errors while writing
are passed on to the UI as `HomeAssistantError` (e.g. device unreachable).

> [!IMPORTANT]
> **Keep-alive (path 1 only):** as long as a set value is `≠ 0`, each number
> entity additionally holds its own `async_track_time_interval` timer (every
> 45s) that resends the same command — preventing the 60s auto-expiry
> documented by the manufacturer. The timer lives per entity instance
> (`_unsub_keepalive`) and is stopped at `0` or `async_will_remove_from_hass`.
> Paths 2 and 3 do not expire, so no keep-alive is needed there. Details:
> [02_api-reference.md](02_api-reference.md).

## HA conventions deliberately used

- **`entry.runtime_data`** (instead of `hass.data[DOMAIN][entry_id]`) —
  the current recommendation for HA versions from 2024.7 onward, matching
  the 2026.10.4 installed here. Typed via
  `type AskoheatConfigEntry = ConfigEntry[AskoheatDataUpdateCoordinator]`
  in `__init__.py`.
- **`async_get_clientsession(hass)`** instead of our own
  `aiohttp.ClientSession()` — uses HA's managed, shared session (no manual
  closing needed).
- **`CoordinatorEntity`** + a central `DeviceInfo` on the coordinator (not
  duplicated per entity) — a pattern already proven in `goecharger_api2`.
- **Dataclass `EntityDescription` lists** instead of one class per sensor —
  compact, easy to extend (more sensors, `number`/`select` for
  write access).

## Why no multi-coordinator setup

The secondary endpoints could have lived in their own, slower coordinators.
The decision (at Andreas' request) was deliberately simpler: one coordinator,
the secondary endpoints load at startup and on a button press ("Reload
settings" button), no automatic interval. That spares the ESP32 and is
sufficient because changes made through Home Assistant are picked up
immediately anyway. Should automatic reloading prove necessary later, a
second `DataUpdateCoordinator` with `update_interval=timedelta(minutes=30)`
would be a locally contained change in `coordinator.py`.

