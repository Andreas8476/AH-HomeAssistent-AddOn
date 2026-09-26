# 10 — Automation: linking the feed-in value to a meter/inverter

*[Deutsche Version](../de/10_automatisierung.md) (primary, authoritative)*

## Background

The classic use case for ASKOHEAT+: automatically burn PV surplus instead
of feeding it into the grid. For that, the **feed-in value**
(`number.load_feedin`) needs to continuously mirror the current value of a
grid/inverter power sensor (negative = surplus, positive = draw — see
[02_api-reference.md](02_api-reference.md)).

Two ways to do this: the **built-in link** directly in the integration's
settings (recommended for the standard case), or a bundled **Home
Assistant blueprint** for anyone who needs custom conditions/filters.
Either way, the built-in keep-alive (see
[02_api-reference.md](02_api-reference.md)) automatically ensures the
last-transmitted value isn't lost to the 60s revert, even if the source
doesn't update for a while.

## Built-in link (recommended)

**Settings → Devices & Services → ASKOHEAT+** → the three dots (⋮) on the
device → **"Configure"** (the options flow, not to be confused with
"Reconfigure" for host/port). Two optional entity pickers there:

- **Feed-in value automatically from:** a meter/inverter sensor with the
  current feed-in/draw power in watts.
- **Load setpoint automatically from:** likewise for the load setpoint.

Leave both empty = no link, purely manual control as before. Once an
entity is selected, the integration keeps the target value automatically
in sync with it (technically via the same `number.set_value` service the
UI and the blueprint below also use — so the keep-alive applies
identically). Changing the selection automatically reloads the
integration, no manual restart needed.

## Alternative: your own automation (blueprint)

For anyone who needs extra conditions/filters (e.g. only linking during
certain hours), a blueprint is still available — it works independently of
the built-in link above (both call the same service, there's no special
handling for collisions: as with two automations targeting the same
entity, the last write simply wins).

## Importing the blueprint

File in the repo: [`blueprints/askoheat_plus_feedin_from_meter.yaml`](../../../../blueprints/askoheat_plus_feedin_from_meter.yaml).

1. In Home Assistant: **Settings → Automations & Scenes → Blueprints →
   Import Blueprint**.
2. Enter the raw file URL:
   `https://raw.githubusercontent.com/Andreas8476/AH-HomeAssistent-AddOn/main/blueprints/askoheat_plus_feedin_from_meter.yaml`
3. **Preview/Import**.
4. Under **Automations**, create a new automation from the imported
   blueprint:
   - **Meter/inverter sensor:** your sensor with the current feed-in/draw
     power in watts (e.g. from the Solar Manager pipeline).
   - **ASKOHEAT+ feed-in value entity:** the `number.load_feedin` entity of
     your ASKOHEAT+ device.
5. Save.

## What the blueprint does

- **Trigger:** a state change of the chosen meter/inverter sensor.
- **Condition:** the sensor value is not `unknown`/`unavailable`.
- **Action:** `number.set_value` on the ASKOHEAT+ feed-in value entity with
  the (rounded) sensor value.

No repetition logic of its own in the blueprint — the integration's
keep-alive already handles that (every 45s, as long as the value is `≠ 0`).

## Notes

- Check the sign: some meters/inverters report feed-in as a positive
  value — if so, create a helper sensor with an inverted sign before
  linking (a template sensor), since ASKOHEAT+ expects negative = surplus.
- The blueprint doesn't enforce upper/lower bounds beyond the int16 range
  documented in [02_api-reference.md](02_api-reference.md)
  (`-32768`–`32767`) — `number.set_value` automatically rejects values
  outside the range defined in `number.py`.
- Purely optional, not a requirement: anyone who'd rather build the link
  as their own automation (e.g. with extra conditions) can do that any
  time without this blueprint — `number.load_feedin` is a perfectly normal
  entity controllable via `number.set_value`.
