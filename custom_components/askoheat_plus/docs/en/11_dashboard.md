# 11 — Dashboard (phase 3)

*[Deutsche Version](../de/11_dashboard.md) (primary, authoritative)*

## What it is

A dedicated, YAML-versioned Lovelace dashboard "ASKOHEAT+"
(`dashboard/askoheat_plus_dashboard.yaml` in the repo) — **its own view
(tab) per configured ASKOHEAT+ device**, with two `picture-elements` cards
per view, showing Andreas' own Askoma render images as a background and
positioning live values as overlay labels directly on the image:

- **Card 1** (`dashboard/images/boiler-sensors.png`): temperature sensors
  0–4 (sensor 0 = always at the heating element) plus the current heater
  load, plus a line with the time of the last update (a "heartbeat") and
  the device's IP address.
- **Card 2** (`dashboard/images/boiler-meter.png`): target heater step at
  the tank, load setpoint and feed-in value at the meter cabinet in the
  image.
- Two **history graphs** (`history-graph`): temperature history (sensors
  0–4) and heater load history, both defaulting to `hours_to_show: 24`.
- An additional **fallback table card** with the same values as a plain
  list (in case the image overlays fail to load, or you just prefer a
  table).

**Column layout (per Andreas' sketch, 2026-09-26):** three columns side by
side instead of the default masonry arrangement (which only balances cards
by height, with no fixed column assignment). Left: the fallback table.
Middle: the heating-element image (card 1) on top, directly below it the
meter-cabinet image (card 2) — both in one `vertical-stack`. Right: the two
history graphs, also in a `vertical-stack`. Implemented via
`type: horizontal-stack` with three `cards` entries (the middle and right
columns each a nested `type: vertical-stack`) — the only Lovelace card
types that guarantee an exact column position instead of a pure
height-balancing heuristic.

**Important — the view needs `type: panel`:** the default masonry view
treats every top-level card (even a `horizontal-stack`) as *one* card and
caps it at a single masonry column width (default ~500px) — with only one
card in `cards:`, that rendered as a tiny, centered window that then also
had to squeeze the three inner columns into it (the problem in Andreas'
screenshot after the first layout version: the column widths "didn't match
at all anymore"). Each device view therefore now sets `type: panel` — panel
views give their one card the view's full width, with no column cap.

**Label positions (image 1):** the tank contains two visually distinct
parts: the large heating coil (heat-exchanger spiral) and the actual
ASKOHEAT+ heating element (the smaller orange coil beneath/behind it,
right next to the white sensor puck). Current layout (per Andreas'
sketch): T0 sits directly right of the ASKOHEAT+ heating element; T1–T4
are cleanly right-aligned with T0 (the same `left` column); the heater
load is centered below the heating element. In image 2, "Stufe" was moved
off the tank onto the open wall/floor area, so the heating element stays
visible there too.

**Heartbeat/timestamp:** the markdown card above image 1 shows
`Zuletzt aktualisiert: vor …` ("last updated: … ago") as a Jinja template,
read from the `last_update` diagnostic entity's timestamp (tracked by the
coordinator on every successful poll — so it reflects the last successful
poll cycle, not just "the integration is running"). Right below it: the
device's IP (`📡 Gerät: ...`), read from the `host` field of that device's
config entry (`.storage/core.config_entries`), not from an entity.

**History graphs:** Andreas wanted a quick look at the temperature/load
history without switching to the entity history view separately.
`history-graph` is the fitting built-in Lovelace card for that — needs no
extra recorder configuration, since Home Assistant records sensor history
by default anyway. `hours_to_show: 24` is the default range Andreas asked
for, changeable any time in the UI card editor (but like the label
positions, gets overwritten on the next script run — for a permanent change,
adjust `HISTORY_TEMPERATURE_KEYS`/`HISTORY_LOAD_KEY` or the `hours_to_show`
value directly in `generate_dashboard.py`).

**Important note about the images:** these are Andreas' own, unmodified
original Askoma render images — I have no way to generate new images. The
positioning of the overlay labels (percentage coordinates) is a sensible
starting point, not a precision measurement of real sensor positions. For
multiple devices, the **same** image pair is currently used for every view
(no photo per device model available) — but content-wise each view is
correctly separated, since each view points at that device's own entities.

## Multiple heating elements: auto-generated, not hand-maintained

**The problem:** plain Lovelace YAML can't generically express "one card
per ASKOHEAT+ device" — `picture-elements` elements need concrete entity
IDs, which depend on the device's article name (only known after setup).
Two devices can even get differently named IDs for the same field (e.g.
with/without an area prefix, depending on whether the device already had a
Home Assistant area assigned when its entities were created) — so
maintaining this by hand would be both tedious and error-prone.

**The solution:** [`dashboard/generate_dashboard.py`](../../../../dashboard/generate_dashboard.py) —
a script that **completely regenerates** `askoheat_plus_dashboard.yaml` by
looking directly at Home Assistant's own registry
(`.storage/core.config_entries` + `.storage/core.entity_registry`) to see
which ASKOHEAT+ devices are currently configured, and automatically builds
a dedicated view with the correct entity IDs for each.

```sh
python3 /homeassistant/askoheat_plus/dashboard/generate_dashboard.py
ha core check && ha core restart
```

**When to run it:** after adding, removing or renaming any ASKOHEAT+
device. The script overwrites the file completely from the current
registry state every time — no manual editing needed, but also no manual
adjustments (e.g. moved label positions) survive a re-run. Anyone who
wants different positions permanently should edit the coordinate constants
(`SENSOR_ELEMENTS`, `METER_ELEMENTS`) directly in the script, not in the
generated YAML file.

**Why a script instead of a generic Lovelace card/custom card:** a
"for-every-device" logic directly in Lovelace would require its own
JavaScript custom card (considerably more effort/maintenance than a
150-line Python script you run once when needed).

## Why a dedicated YAML dashboard (instead of a UI dashboard)

All previously existing dashboards in this HA setup (`stegi-home`,
`solar-manager-v2`, `home-uebersicht`) are UI-managed
(`.storage/lovelace.*`). ASKOHEAT+ instead gets its own, **separate
YAML-mode dashboard**, registered via a new `lovelace:` block in
`configuration.yaml`:

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

Advantage: fully versioned in the project repo (fits the "everything in
one place" principle), doesn't touch the existing UI dashboards.

## Images must additionally be copied to `www/`

**Important limitation that ruled out the original symlink idea (as used
for `custom_components/`):** Home Assistant's static file server (`/local/`
→ `<config>/www/`) does not, for security reasons, **follow symlinks that
point outside `www/`** — an attempt to mount the images purely via a
symlink from `dashboard/images/` to `www/askoheat_plus/` consistently
produced `404`.

So: the images additionally live as a **real copy** under
`/homeassistant/www/askoheat_plus/` (not part of the git repo, since it's
outside `/homeassistant/askoheat_plus/`). The master copies in the repo
stay under `dashboard/images/`. **When the images change, copy them again
to `www/askoheat_plus/`:**

```sh
cp /homeassistant/askoheat_plus/dashboard/images/*.png /homeassistant/www/askoheat_plus/
```

## Adjusting positions

In the Lovelace UI (not in the YAML editor, see above — it gets
overwritten on the next script run): open the "ASKOHEAT+" dashboard → the
desired device view/tab → the pencil icon → the affected
`picture-elements` card → select an element → drag & drop to move it. For
permanent changes: edit the coordinates in
`dashboard/generate_dashboard.py` (`SENSOR_ELEMENTS`/`METER_ELEMENTS`).

## For other users (HACS installation)

`generate_dashboard.py` needs read access to
`/homeassistant/.storage/core.config_entries` and `core.entity_registry` —
so it runs directly on the HA host (via a terminal add-on, see
[04_installation.md](04_installation.md)). Before running it: copy your
own images (or Andreas' originals, `dashboard/images/`) to
`www/askoheat_plus/` — this doesn't happen automatically via HACS.
