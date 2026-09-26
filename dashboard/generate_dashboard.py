#!/usr/bin/env python3
"""Generate askoheat_plus_dashboard.yaml from the currently configured
ASKOHEAT+ devices in Home Assistant.

Why this exists: the dashboard's picture-elements cards need concrete
entity_ids, which depend on the device's article name and are only known
after setup — they can't be templated generically in plain Lovelace YAML.
Instead of hand-editing the dashboard every time a device is added, removed
or renamed, this script re-derives one dashboard view per configured
ASKOHEAT+ device directly from Home Assistant's own entity registry.

Usage (on the HA host):
    python3 /homeassistant/askoheat_plus/dashboard/generate_dashboard.py

Then: `ha core check` && `ha core restart` to see the result. Safe to run
any time you add/remove/rename an ASKOHEAT+ device — it always regenerates
the whole file from the current registry state, nothing is hand-merged.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

CONFIG_ENTRIES_PATH = Path("/homeassistant/.storage/core.config_entries")
ENTITY_REGISTRY_PATH = Path("/homeassistant/.storage/core.entity_registry")
OUTPUT_PATH = Path(__file__).parent / "askoheat_plus_dashboard.yaml"

DOMAIN = "askoheat_plus"

LABEL_STYLE = """              color: white
              background-color: {bg}
              padding: 2px 6px
              border-radius: 6px
              font-weight: bold
              font-size: 12px"""

# (unique_id suffix, label prefix, top%, left%, bg color) for the boiler/coil image.
# All labels sit in a clear column to the right of the coil cutaway (verified
# pixel-by-pixel against dashboard/images/boiler-sensors.png: the coil never
# reaches past ~58% left in this crop) so the heating element stays fully
# visible instead of being covered by the value pills.
SENSOR_ELEMENTS = [
    ("temperature_sensor_4", "T4: ", 10, 63, "rgba(0, 0, 0, 0.65)"),
    ("temperature_sensor_3", "T3: ", 24, 63, "rgba(0, 0, 0, 0.65)"),
    ("temperature_sensor_2", "T2: ", 38, 63, "rgba(0, 0, 0, 0.65)"),
    ("temperature_sensor_1", "T1: ", 52, 63, "rgba(0, 0, 0, 0.65)"),
    ("temperature_sensor_0", "T0: ", 76, 63, "rgba(0, 0, 0, 0.65)"),
    ("heater_load", "⚡ ", 88, 63, "rgba(120, 20, 20, 0.75)"),
]

# (unique_id suffix, label prefix, top%, left%) for the meter-cabinet image
METER_ELEMENTS = [
    ("heater_step_target", "Stufe: ", 76, 25),
    ("load_setpoint", "Vorgabe: ", 18, 70),
    ("load_feedin", "Einspeisung: ", 60, 68),
]

# (unique_id suffix, short display name) for the fallback entities card
FALLBACK_ENTITIES = [
    ("error_status", "Gerätestatus"),
    ("heater_step", "Heizstufe (Ist)"),
    ("heater_load", "Heizleistung"),
    ("temperature_sensor_0", "Temperatur"),
    ("heater_step_target", "Ziel-Heizstufe"),
    ("load_setpoint", "Leistungsvorgabe"),
    ("load_feedin", "Einspeisewert"),
    ("emergency_mode", "Notbetrieb"),
]


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "device"


def load_devices() -> list[dict]:
    """Return one dict per ASKOHEAT+ config entry: {entry_id, title, entities}."""
    config_entries = json.loads(CONFIG_ENTRIES_PATH.read_text())
    entity_registry = json.loads(ENTITY_REGISTRY_PATH.read_text())

    askoheat_entries = [
        e for e in config_entries["data"]["entries"] if e.get("domain") == DOMAIN
    ]

    devices = []
    for entry in askoheat_entries:
        entities_by_suffix: dict[str, str] = {}
        for ent in entity_registry["data"]["entities"]:
            if ent.get("config_entry_id") != entry["entry_id"]:
                continue
            unique_id = ent.get("unique_id") or ""
            if "_" not in unique_id:
                continue
            # unique_id = f"{device_id}_{key}", device_id itself may contain
            # colons (MAC-style) but never underscores, so split once from
            # the left on the first "_" after the MAC-style id.
            suffix = unique_id.split("_", 1)[1] if "_" in unique_id else None
            if suffix:
                entities_by_suffix[suffix] = ent["entity_id"]
        devices.append(
            {
                "entry_id": entry["entry_id"],
                "title": entry.get("title") or "ASKOHEAT+",
                "entities": entities_by_suffix,
            }
        )
    return devices


def render_label(entity_id: str | None, prefix: str, top: float, left: float, bg: str) -> str:
    if entity_id is None:
        return ""  # entity not found on this device, skip silently
    style = LABEL_STYLE.format(bg=bg)
    return (
        f"          - type: state-label\n"
        f"            entity: {entity_id}\n"
        f'            prefix: "{prefix}"\n'
        f"            style:\n"
        f"              top: {top}%\n"
        f"              left: {left}%\n"
        f"{style}\n"
    )


def render_view(device: dict) -> str:
    ents = device["entities"]
    path = slugify(device["title"])

    sensor_labels = "".join(
        render_label(ents.get(suffix), prefix, top, left, bg)
        for suffix, prefix, top, left, bg in SENSOR_ELEMENTS
    )
    meter_labels = "".join(
        render_label(ents.get(suffix), prefix, top, left, "rgba(0, 0, 0, 0.65)")
        for suffix, prefix, top, left in METER_ELEMENTS
    )

    fallback_rows = "".join(
        f"          - entity: {ents[suffix]}\n            name: {name}\n"
        for suffix, name in FALLBACK_ENTITIES
        if suffix in ents
    )

    return f"""  - title: {device["title"]}
    path: {path}
    icon: mdi:radiator
    cards:
      - type: markdown
        content: >
          ## {device["title"]} — Temperaturen & Leistung

          Sensor 0 sitzt direkt am Heizstab, Sensor 1–4 sind zusätzliche
          Messpunkte am Tank (falls am Gerät nicht angeschlossen: "nicht
          verfügbar" — siehe `docs/11_dashboard.md` im Repo für Details).

      - type: picture-elements
        image: /local/askoheat_plus/boiler-sensors.png
        elements:
{sensor_labels}
      - type: markdown
        content: >
          ## Einspeisewert & Leistungsvorgabe am Zählerschrank

      - type: picture-elements
        image: /local/askoheat_plus/boiler-meter.png
        elements:
{meter_labels}
      - type: entities
        title: Alle Werte (Fallback / Details)
        entities:
{fallback_rows}"""


def main() -> None:
    devices = load_devices()
    if not devices:
        raise SystemExit(
            "No ASKOHEAT+ config entries found in core.config_entries - "
            "set up at least one device first."
        )

    header = """# ASKOHEAT+ Dashboard — auto-generated, do not hand-edit
#
# Generated by dashboard/generate_dashboard.py from the ASKOHEAT+ devices
# currently configured in this Home Assistant instance. Re-run that script
# after adding/removing/renaming a device, then `ha core restart`.
#
# Positions (top/left in %) are a starting point, not a precision
# measurement - adjustable via drag & drop in the Lovelace UI editor.
# Details: custom_components/askoheat_plus/docs/11_dashboard.md
#
# Note: deliberately written WITHOUT YAML anchors/merge keys (&/*/<<) - Home
# Assistant's own YAML loader (annotatedyaml) logs "duplicate key" warnings
# for "<<: *anchor" plus sibling keys in the same mapping instead of merging
# them cleanly, so every style block is fully spelled out.

title: ASKOHEAT+
views:
"""

    views = "\n".join(render_view(d) for d in devices)
    OUTPUT_PATH.write_text(header + views + "\n")
    print(f"Wrote {OUTPUT_PATH} with {len(devices)} device view(s):")
    for d in devices:
        print(f"  - {d['title']} ({len(d['entities'])} entities found)")


if __name__ == "__main__":
    main()
