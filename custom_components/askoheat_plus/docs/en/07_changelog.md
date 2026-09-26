# 07 — Changelog

*[Deutsche Version](../de/07_changelog.md) (primary, authoritative)*

Change log for this project. Separate from the overall HA setup's global
`/homeassistant/docs/changelog.md` (which only briefly points to this
project).

## 2026-09-25 — Phase 1: reading (initial build)

- Project created: `custom_components/askoheat_plus/` as a self-contained,
  HACS-capable repo under `/homeassistant/askoheat_plus/`, mounted into
  `custom_components/` via a symlink.
- Architecture: `DataUpdateCoordinator` polls only `gethome.json` (one
  request per cycle, default 30s), four further endpoints
  (`getwizard_status.json`, `gettemperature_calibration.json`, `getreg.json`,
  `getwizard.json` reserved for later) are loaded once at startup.
  Endpoint selection and the "don't overload the ESP32" requirement came
  from Andreas.
- Config flow with a connection test, `unique_id` = the device's `DEVICEID`.
- 13 sensors + 5 binary sensors, all read-only. Details:
  [05_entities.md](05_entities.md).
- Deliberate omissions: free-text relay counters, personal-data fields from
  `getreg.json` (`USER_CONTACT`/`INSTALLER_CONTACT`).

## 2026-09-25 — Verification + Modbus flag reference

- Phase 1 verified against the real test device (`192.168.20.54`, model
  "AHF280-TI-plus-15.8"): all sensors/binary sensors deliver plausible
  values, including the once-loaded `gettemperature_calibration.json`
  sensors. Device configuration was correctly detected dynamically
  (a different model than in the original sample dump).
- New reference doc [09_modbus-status-flags.md](09_modbus-status-flags.md):
  bit-by-bit meaning of the status/error registers (`MODBUS_VAL_STATUS`,
  `MODBUS_VAL_STATUS_EXTENDED`, `MODBUS_VAL_ERROR_STATUS`, among others),
  from the manufacturer's official Modbus register documentation. Currently
  only serves as a cross-check/basis for later extensions, no new entities.
- Repo pushed to GitLab: `git@gitlab.com:SyberAlf/ah-homeassistent-addon.git`,
  tag `v0.1.0`. An additional root `CHANGELOG.md` (Keep a Changelog/SemVer)
  complements this document for a clean release history on GitLab.

## 2026-09-25 — Phase 2: control

- Three `number` entities (`number.py`): target heater step, load setpoint,
  feed-in value. Written via the documented inline-command endpoints
  (`heater%20step`, `load%20setpoint`, `load%20feedin`), ranges dynamic from
  `ASKOHEAT_PLUS_INFO.NUMBER_OF_STEPS`/`MAX_POWER` or static (int16 range)
  for the feed-in value.
- `api.py`: new method `async_send_command`, uses the same client as
  reading, no extra coordinator/polling.
- **Cleanup:** removed the phase-1 diagnostic sensors `set_heater_step` and
  `set_load_feedin` (redundant with the new number entities, which display
  the same value and can also set it). The corresponding entity registry
  entries aren't automatically deleted by Home Assistant, but show
  `unavailable` — removable manually in the settings.
- Deliberately **did not** implement an automatic keep-alive against the
  60s revert of set values (per the manufacturer docs) — would have
  contradicted the "protect the ESP32" principle from phase 1. Anyone
  wanting continuous control has to periodically re-set the value
  themselves (e.g. via an HA automation).

## 2026-09-25 — Keep-alive, GitHub mirror, attribution, automation blueprint

- **Correction to the keep-alive decision above:** after a live test,
  Andreas clarified that resending regularly is unproblematic for the ESP32
  and is in fact expected by the manufacturer ("continuously controlling
  device"). Every number entity now implements a built-in keep-alive: every
  `NUMBER_KEEPALIVE_INTERVAL` (45s) the last-set value is resent, as long as
  it is `≠ 0`; stops at `0` or when the entity is removed. `native_value`
  prefers the internally held value (instant UI feedback). Details:
  [02_api-reference.md](02_api-reference.md).
- New automation blueprint [`blueprints/askoheat_plus_feedin_from_meter.yaml`](../../../../blueprints/askoheat_plus_feedin_from_meter.yaml)
  links any meter/inverter power sensor to the feed-in value
  (`number.load_feedin`) — import instructions in the new
  [10_automation.md](10_automation.md). Deliberately a blueprint instead of
  a hardwired config option (more flexible, no extra setup step).
- **GitHub mirror set up:** `github.com/Andreas8476/AH-HomeAssistent-AddOn`,
  since HACS only supports public GitHub repos (GitLab stays the main repo).
  **From now on, mandatory: every commit goes to both remotes** (`origin` +
  `github`), see [06_development.md](06_development.md). `manifest.json`
  `documentation`/`issue_tracker`/`codeowners` now point at the real GitHub
  repo.
- Full HACS installation guide including initial HACS setup in
  [04_installation.md](04_installation.md).
- Attribution added (README, `01_overview.md`, `LICENSE`): Andreas
  Stegemann + Claude (Sonnet 5), noting Andreas' employment at ASKOMA AG
  (a private project, not official ASKOMA software).

## 2026-09-25 — Emergency mode switch

- New `switch` entity `emergency_mode` (`switch.py`): controls emergency
  mode via the parameter-less `on`/`off` endpoints (the physical button on
  the device, no 60s revert, so no keep-alive needed). Replaces the
  same-named read-only binary sensor from phase 1.
- `api.py`: new method `async_send_bare_command` for parameter-less
  commands.
- Confirmed live: the new switch correctly captured a real state change on
  the test device (`off → on → off` during a restart).
- Cleanup: removed orphaned entity registry entries
  (`sensor..._soll_heizstufe`, `sensor..._soll_einspeisewert` from phase 2,
  plus the superseded `binary_sensor..._notbetrieb`) directly in
  `.storage/core.entity_registry` (backup taken first), since no long-lived
  access token was available for UI-side deletion.
- Clarified: setting the number entities manually (target heater step,
  load setpoint, feed-in value) already works without further action,
  independent of any additional automation link.

## 2026-09-25 — Phase 3: dashboard

- `sensor.py`: added `temperature_sensor_1`..`4` (previously only sensor
  0) — a prerequisite for the 4 temperature displays wanted on the
  dashboard. Disabled by default if not connected on the device.
- New, dedicated YAML-mode Lovelace dashboard "ASKOHEAT+"
  (`dashboard/askoheat_plus_dashboard.yaml`), registered via a new
  `lovelace:` block in `configuration.yaml` (previously this setup only had
  UI-managed dashboards). Two `picture-elements` cards using Andreas' own
  Askoma render images (`dashboard/images/`) as a background with live
  values as overlay labels (temperature sensors 0–4 + heater load at the
  tank; target heater step, load setpoint, feed-in value at the meter
  cabinet). Details including customization notes for other users:
  [11_dashboard.md](11_dashboard.md).
- **Important technical finding:** the existing symlink trick
  (`custom_components/`) does **not** work for dashboard images — Home
  Assistant's `/local/` server doesn't follow symlinks pointing outside
  `www/` (404). The images therefore additionally live as a real copy in
  `www/askoheat_plus/`, to be kept in sync with `dashboard/images/`.
- YAML gotcha: Home Assistant's own YAML loader (`annotatedyaml`) treats
  `<<: *anchor` plus extra keys in the same mapping as a duplicate-key
  warning instead of merging cleanly (unlike plain PyYAML) — the dashboard
  YAML was therefore deliberately written without anchors/merge keys.
- Verified live: both images under `/local/askoheat_plus/*.png` return
  HTTP 200, `ha core check`/restart clean, no more duplicate-key warnings
  in the log.

## 2026-09-25 — Dashboard fine-tuning, installation-doc additions

- After screenshot feedback from Andreas: widened label spacing on the
  dashboard (setpoint/feed-in value were almost on top of each other with
  only ~12 percentage points of spacing), spread the temperature-sensor
  labels more widely across the coil instead of stacking them tightly.
- "All values" fallback card: explicit short `name:` overrides for every
  entity, since the full default names (including the device name) were
  truncated in the entities card.
- `docs/de/04_installation.md`: the terminal/SSH add-on as a prerequisite
  for the initial HACS install is now explicitly named under
  "Prerequisites" (previously only implicit in step 1), including the
  terminal-less alternative (file editor/Samba).
- **Followed up at Andreas' request:** merely mentioning the terminal
  add-on wasn't enough — the goal is a guide a technically inexperienced
  user can follow from scratch. Step 1 of the HACS option is now a
  complete click-by-click guide to installing a terminal add-on (open the
  add-on store, search/install/start "Terminal & SSH"), step 2 similarly
  expanded for HACS itself (including creating a GitHub account, the
  device-code flow explained). Steps renumbered (1–5).

## 2026-09-25 — ASKOMA logo, reconfigure after setup

- **ASKOMA logo added** (`custom_components/askoheat_plus/brand/`):
  `icon.png`/`icon@2x.png` (a square crop of the mountain+cross glyph from
  Andreas' original logo; HA 2026.3+ reads custom-integration icons
  directly from the component folder, no central-repo entry needed —
  same pattern as `froeling_lambdatronic_modbus/brand/icon.png`),
  `logo.png` (light-mode wordmark), `dark_logo.png`/`dark_logo@2x.png`
  (dark-mode variant). Image cropping done locally with Pillow in an
  isolated venv (system Python deliberately left untouched).
- **New: reconfigure after setup.** `config_flow.py` now implements
  `async_step_reconfigure` — host/port/polling interval can be changed any
  time via "Devices & Services → ASKOHEAT+ → ⋮ → Reconfigure", not just at
  initial setup. Same connection test as initial setup, plus protection
  against accidentally repointing an entry at a different physical device
  (`_abort_if_unique_id_mismatch`). API methods verified by looking
  directly at the actually installed `homeassistant` source via
  `docker exec homeassistant` (container access newly discovered this
  session) — more reliable than the previous plain `py_compile` check.

## 2026-09-25 — Multi-device test: dashboard generator, more robust error handling

- Andreas set up a second device ("SONNENBOOSTER 5,2 kW") as a test. This
  revealed: temperature sensors 1–4 appeared to be missing — actually just
  disabled by default as designed (not a bug), confirmed directly in the
  second device's entity registry.
- **Clarified (no code needed):** Home Assistant already auto-removes the
  device and all its entities from the registry when a config entry is
  deleted (`async_clear_config_entry`, core behavior, verified in the
  actual HA source via `docker exec`). Recorder history data is
  deliberately kept (HA design), no special handling needed on our side.
- **New: `dashboard/generate_dashboard.py`.** Generates
  `askoheat_plus_dashboard.yaml` automatically from the current
  device/entity registry — one view per configured ASKOHEAT+ device, any
  number of them. Solves the problem that plain Lovelace YAML has no
  generic "one card per device" logic, and entity IDs differ per device
  (some with, some without an area prefix). Details:
  [11_dashboard.md](11_dashboard.md).
- `api.py`: broadened exception handling to include `RuntimeError`
  (previously only caught `aiohttp.ClientError`/`TimeoutError`) — noticed
  on the second test device that aiohttp's "Session is closed" during a
  restart, mid-request, ended up as an unhandled error in the log
  (cosmetic, not a functional bug, only occurred during shutdown).
- The second test device is missing `gettemperature_calibration.json` and
  `getreg.json` (HTTP 404, presumably a different firmware version) —
  already correctly handled as a warning rather than an error by the
  existing per-secondary-endpoint try/except, no change needed.

## 2026-09-25 — Auto-enabling temperature sensors 1–4, dashboard label position fixed

- **Temperature sensors 1–4 now enable automatically instead of requiring
  manual activation:** Andreas' feedback (a screenshot showed warning icons
  for the disabled sensors) — an entity should be enabled as soon as the
  device reports a real value, instead of having to enable it manually in
  the entity settings. `sensor.py` now determines live at every setup, per
  device, whether `TEMP_SENSOR_1`..`_4` are connected (neither the text
  `"not connected"` nor the numeric sentinel `9999`) and sets
  `entity_registry_enabled_default` accordingly — and also automatically
  re-enables already-existing, previously disabled entities as soon as
  they report a value live (no removing/re-adding needed). Checked
  directly against both test devices: device 1 (AHF280) has real values
  for sensors 1–4 → now enabled automatically; device 2 (SONNENBOOSTER)
  only has sensors 1–3 connected (sensor 4 reports `"not connected"`) →
  only 1–3 become enabled, 4 stays disabled.
- **Dashboard, image 1 (heating-element close-up):** Andreas' feedback
  after a screenshot — the value labels (especially T1–T3) sat directly on
  the heating coil and covered it. All six labels (T0–T4, heater load) now
  sit in a shared column right of the coil (`left: 63%`), whose position
  was verified pixel by pixel against `dashboard/images/boiler-sensors.png`
  (the coil never extends past `left: 58%` in this crop). This keeps the
  coil fully visible. Re-run `dashboard/generate_dashboard.py` + `ha core
  restart` to apply the change to both device views.

## 2026-09-26 — Dashboard: ASKOHEAT+ heating element revealed, heartbeat display

- Andreas' feedback after a live test: the actual ASKOHEAT+ heating element
  (the small orange coil next to the sensor puck, distinct from the larger
  heat-exchanger coil) was still covered in image 1 by the T0/heater-load
  labels, and in image 2 by the "Stufe" label. Both moved so the element
  stays fully visible: T0/heater load all the way to the left, T1–T4
  further right (image 1); "Stufe" onto the open wall area next to the tank
  (image 2). Positions re-verified pixel by pixel against both images.
- New: a heartbeat/timestamp line ("Zuletzt aktualisiert: vor …") above
  image 1, via a Jinja template reading `last_updated` of the heater-load
  entity.
- Removed the previous description line ("Sensor 0 sitzt direkt am
  Heizstab...") above image 1 at Andreas' request, deemed no longer
  necessary.

## 2026-09-26 — Dashboard fine layout per sketch: T0 next to the element, T1-T4 right-aligned, watt centered

- Andreas sent a sketch annotated with arrows: T0 should sit right next to
  the ASKOHEAT+ heating element, T1–T4 should be cleanly right-aligned with
  T0, and the heater load centered below it. Implemented and re-verified
  pixel by pixel against `boiler-sensors.png`: T0/T1–T4 are now all at
  `left: 76%` (T0 at `top: 65%`, directly right of the element, whose
  shadow zone there extends to about ~74%), heater load at
  `left: 54%, top: 88%` (centered below the element, below any shadow zone,
  consistently open area).

## 2026-09-26 — Detect device family (ASKOHEAT 2.0 / Classic, with/without EEPROM)

- New diagnostic sensor `device_family`: derives which device family it is
  from the `HARDWARE_VERSION` prefix (per Andreas/ASKOMA AG) — `RCe` →
  "ASKOHEAT 2.0 (mit EEPROM)", `HWe` → "ASKOHEAT Classic (mit EEPROM)",
  `HW` → "ASKOHEAT Classic (ohne EEPROM)". Verified against both test
  devices: device 1 reports `RCe1.0` → "ASKOHEAT 2.0 (mit EEPROM)", device
  2 reports `HW 1.3` (with a space!) → "ASKOHEAT Classic (ohne EEPROM)" —
  the prefix regex works regardless of the space. Disabled by default, like
  the other master-data sensors.

## 2026-09-26 — Built-in link for feed-in value & load setpoint

- Andreas' request: instead of only via the blueprint, the feed-in value
  (and the load setpoint) should also be linkable directly in the
  integration to any other entity, by selection rather than an automation.
- New options flow (`config_flow.py`, `AskoheatOptionsFlow`, reachable via
  "⋮ → Configure"): two optional entity pickers
  (`feedin_source_entity_id`, `setpoint_source_entity_id`), domains
  `sensor`/`number`/`input_number`. Leave empty = no link.
- New module `link.py`: when a link is set, registers a state listener
  (`async_track_state_change_event`) on the source entity and, on every
  change, calls the same `number.set_value` service that manual UI control
  also uses — the existing keep-alive in `number.py` thus applies
  automatically, with no separate resend/write logic in `link.py`. Also
  does a one-time sync right at setup, instead of waiting for the source's
  next state change.
- `__init__.py`: `entry.add_update_listener` automatically reloads the
  integration as soon as the link changes in the options flow — no manual
  restart needed.
- The existing blueprint (`docs/de/10_automatisierung.md`) stays available
  for anyone who needs custom conditions/filters — now presented as the
  "alternative", with the built-in link as the recommended default path.
- **Architecture/model:** pattern adopted 1:1 from
  `froeling_lambdatronic_modbus`, already running in the same Home
  Assistant setup (`FroelingOptionsFlowHandler`), instead of reinventing it
  — including `add_suggested_values_to_schema` for clearable fields
  instead of fixed `default=` values.
- **Verification:** `py_compile` + a real import test (`docker exec`) of
  every affected file, `ha core check` + restart with no errors. A direct
  live test via a manual `.storage/core.config_entries` edit was attempted
  but abandoned: Home Assistant apparently persists config-entry options
  with a similar delayed/debounced save as the entity registry (see the
  known point above) — the manual file edit got overwritten by the next
  internal save. The real end-to-end test via the options-flow dialog in
  the UI is therefore still pending (by Andreas).

## Open points

- **Polling frequency of the secondary endpoints** (`getwizard_status.json`,
  `gettemperature_calibration.json`, `getreg.json`): currently loaded only
  once at startup, no refresh afterward. Needs a closer look later per
  Andreas (its own slow interval? an options-flow setting? a reconnect
  trigger?).
- **Relay counters/balance** (`STATUS_FLAGS.HEATER_1_RELAY` etc.) not yet
  mapped as individual sensors — free-text parsing deliberately deferred.
- **Grid-lock (`128`) / direct heater-step paths (`0`–`19`):** not mapped
  as separate entities, only the regular target heater step.
