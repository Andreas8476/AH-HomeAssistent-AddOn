#!/usr/bin/env python3
"""Erzeugt askoheat_plus_dashboard.yaml aus den aktuell in Home Assistant
eingerichteten ASKOHEAT+-Geräten.

Warum es das gibt: die picture-elements-Karten des Dashboards brauchen
konkrete Entity-IDs, die vom Artikelnamen des jeweiligen Geräts abhängen und
erst nach dem Einrichten bekannt sind — generisch in reinem Lovelace-YAML
lässt sich das nicht templaten. Statt das Dashboard bei jedem Hinzufügen,
Entfernen oder Umbenennen eines Geräts von Hand zu pflegen, leitet dieses
Skript eine Dashboard-Ansicht pro eingerichtetem ASKOHEAT+-Gerät direkt aus
Home Assistants eigener Entity-Registry ab.

Verwendung (auf dem HA-Host):
    python3 /homeassistant/askoheat_plus/dashboard/generate_dashboard.py

Danach: `ha core check` && `ha core restart`, um das Ergebnis zu sehen.
Gefahrlos jederzeit erneut ausführbar, wenn ein ASKOHEAT+-Gerät hinzugefügt,
entfernt oder umbenannt wird — es erzeugt die Datei jedes Mal komplett neu
aus dem aktuellen Registry-Stand, nichts wird von Hand zusammengeführt.
"""

from __future__ import annotations

import json
import re
import textwrap
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

# (unique_id-Suffix, Label-Präfix, top%, left%, Hintergrundfarbe) für das
# Heizstab-/Wendel-Bild. Layout nach Andreas' Skizze (Pfeile auf Screenshot):
# T0 sitzt rechts neben dem eigentlichen ASKOHEAT+-Heizelement (die kleine
# orangene Wendel bei ~49-73% links / 63-70% oben, unterhalb der großen
# Wärmetauscher-Wendel, neben dem Sensor-Puck); T1-T4 sind sauber
# rechtsbündig mit T0 ausgerichtet (dieselbe left%-Spalte); die
# Heizleistung sitzt mittig unter dem Heizelement. Alle Positionen
# pixelgenau gegen dashboard/images/boiler-sensors.png (398x502) verifiziert.
SENSOR_ELEMENTS = [
    ("temperature_sensor_4", "T4: ", 10, 76, "rgba(0, 0, 0, 0.65)"),
    ("temperature_sensor_3", "T3: ", 24, 76, "rgba(0, 0, 0, 0.65)"),
    ("temperature_sensor_2", "T2: ", 38, 76, "rgba(0, 0, 0, 0.65)"),
    ("temperature_sensor_1", "T1: ", 52, 76, "rgba(0, 0, 0, 0.65)"),
    ("temperature_sensor_0", "T0: ", 65, 76, "rgba(0, 0, 0, 0.65)"),
    ("heater_load", "⚡ ", 88, 54, "rgba(120, 20, 20, 0.75)"),
]

# (unique_id-Suffix, Label-Präfix, top%, left%) für das Zählerschrank-Bild.
# "Stufe" ist an heater_step (Ist-Wert) gebunden statt an heater_step_target
# (Soll-Wert): Bei aktivem Notbetrieb steuert das Gerät die Heizstufe selbst,
# ohne die Ziel-Heizstufen-Entity zu ändern — mit heater_step_target blieb
# die Anzeige dabei fälschlich stehen (Feedback von Andreas nach Live-Test
# mit Notbetrieb). Position rechts neben dem Tank auf der freien Wand-/
# Bodenfläche, weg vom ASKOHEAT+-Heizelement bei ~21-23% links / 68-71% oben
# in dashboard/images/boiler-meter.png.
METER_ELEMENTS = [
    ("heater_step", "Stufe: ", 76, 42),
    ("load_setpoint", "Vorgabe: ", 18, 70),
    ("load_feedin", "Einspeisung: ", 60, 68),
]

# Entities für die beiden Verlaufs-Grafen am Ende jeder Ansicht (Wunsch von
# Andreas: Temperaturverlauf Sensor 0-4 + Heizleistungsverlauf, Standard 24h).
HISTORY_TEMPERATURE_KEYS = [f"temperature_sensor_{i}" for i in range(5)]
HISTORY_LOAD_KEY = "heater_load"

# (unique_id-Suffix, Kurzname) für die Fallback-Entities-Karte
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
    """Ein Dict pro ASKOHEAT+-Config-Entry liefern: {entry_id, title, entities}."""
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
            # unique_id = f"{device_id}_{key}", device_id selbst kann
            # Doppelpunkte enthalten (MAC-artig), aber nie Unterstriche —
            # daher einmalig von links am ersten "_" nach der MAC-artigen ID trennen.
            suffix = unique_id.split("_", 1)[1] if "_" in unique_id else None
            if suffix:
                entities_by_suffix[suffix] = ent["entity_id"]
        devices.append(
            {
                "entry_id": entry["entry_id"],
                "title": entry.get("title") or "ASKOHEAT+",
                "entities": entities_by_suffix,
                "host": entry.get("data", {}).get("host"),
            }
        )
    return devices


def render_label(entity_id: str | None, prefix: str, top: float, left: float, bg: str) -> str:
    if entity_id is None:
        return ""  # Entity auf diesem Gerät nicht vorhanden, still überspringen
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

    # Herzschlag: Zeitpunkt des letzten erfolgreichen Polls, aus der
    # last_update-Diagnose-Entity (siehe coordinator.py/sensor.py) statt aus
    # last_updated eines gewöhnlichen Sensors — Home Assistant aktualisiert
    # last_updated nämlich nur bei einer echten Wertänderung, nicht bei jedem
    # Poll (bei konstanter Heizleistung stand hier sonst ein veralteter
    # Zeitstempel, obwohl brav alle scan_interval-Sekunden gepollt wurde).
    heartbeat_entity = ents.get("last_update")
    heartbeat_line = (
        "\n\n          🔄 Zuletzt aktualisiert: vor "
        "{{ relative_time(as_datetime(states('" + heartbeat_entity + "'))) }}"
        if heartbeat_entity
        else ""
    )

    host = device.get("host")
    ip_line = f"\n\n          📡 Gerät: `{host}`" if host else ""

    temperature_history_entities = [
        ents[key] for key in HISTORY_TEMPERATURE_KEYS if key in ents
    ]
    load_history_entities = [ents[HISTORY_LOAD_KEY]] if HISTORY_LOAD_KEY in ents else []

    history_cards = ""
    if temperature_history_entities:
        entity_rows = "".join(f"          - {e}\n" for e in temperature_history_entities)
        history_cards += f"""      - type: history-graph
        title: Temperaturverlauf (Sensor 0-4)
        hours_to_show: 24
        entities:
{entity_rows}"""
    if load_history_entities:
        entity_rows = "".join(f"          - {e}\n" for e in load_history_entities)
        history_cards += f"""      - type: history-graph
        title: Heizleistungsverlauf
        hours_to_show: 24
        entities:
{entity_rows}"""

    # Layout nach Andreas' Skizze (Pfeile auf Screenshot, 2026-09-26): drei
    # Spalten nebeneinander statt der Standard-Masonry-Ansicht (die Karten
    # nur nach Höhe balanciert, keine feste Spalten-Zuordnung erlaubt).
    # Links: Fallback-Tabelle. Mitte: Zählerschrank-Bild, darunter das
    # Heizstab-Bild (beide in einem vertical-stack). Rechts: die beiden
    # Verlaufs-Grafen (ebenfalls vertical-stack). horizontal-stack/
    # vertical-stack sind die einzigen Lovelace-Kartentypen, die eine exakte
    # Spalten-Position statt einer Höhen-Heuristik garantieren.
    fallback_card = f"""      - type: entities
        title: Alle Werte (Fallback / Details)
        entities:
{fallback_rows}"""

    meter_and_sensor_cards = f"""      - type: markdown
        content: >
          ## Einspeisewert & Leistungsvorgabe am Zählerschrank

      - type: picture-elements
        image: /local/askoheat_plus/boiler-meter.png
        elements:
{meter_labels}
      - type: markdown
        content: >
          ## {device["title"]} — Temperaturen & Leistung{heartbeat_line}{ip_line}

      - type: picture-elements
        image: /local/askoheat_plus/boiler-sensors.png
        elements:
{sensor_labels}"""

    history_column = (
        f"""          - type: vertical-stack
            cards:
{textwrap.indent(history_cards, "        ")}"""
        if history_cards
        else ""
    )

    return f"""  - title: {device["title"]}
    path: {path}
    icon: mdi:radiator
    cards:
      - type: horizontal-stack
        cards:
{textwrap.indent(fallback_card, "    ")}
          - type: vertical-stack
            cards:
{textwrap.indent(meter_and_sensor_cards, "        ")}
{history_column}"""


def main() -> None:
    devices = load_devices()
    if not devices:
        raise SystemExit(
            "Keine ASKOHEAT+-Config-Entries in core.config_entries gefunden - "
            "zuerst mindestens ein Gerät einrichten."
        )

    header = """# ASKOHEAT+ Dashboard — automatisch generiert, nicht von Hand bearbeiten
#
# Erzeugt von dashboard/generate_dashboard.py aus den aktuell in dieser
# Home-Assistant-Instanz eingerichteten ASKOHEAT+-Geräten. Nach dem
# Hinzufügen/Entfernen/Umbenennen eines Geräts erneut ausführen, dann
# `ha core restart`.
#
# Positionen (top/left in %) sind ein Startpunkt, keine Präzisionsmessung -
# per Drag & Drop im Lovelace-UI-Editor anpassbar.
# Details: custom_components/askoheat_plus/docs/de/11_dashboard.md
#
# Hinweis: bewusst OHNE YAML-Anker/Merge-Keys (&/*/<<) geschrieben - Home
# Assistants eigener YAML-Loader (annotatedyaml) protokolliert bei
# "<<: *anchor" plus Geschwister-Keys in derselben Zuordnung "duplicate key"-
# Warnungen statt sauber zu mergen, daher ist jeder style-Block vollständig
# ausgeschrieben.

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
