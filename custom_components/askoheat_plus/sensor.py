"""Sensor-Plattform für die ASKOHEAT+-Integration."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry
from .api import extract_number, get_path
from .const import DOMAIN
from .coordinator import AskoheatDataUpdateCoordinator
from .entity import AskoheatEntity


@dataclass(frozen=True, kw_only=True)
class AskoheatSensorEntityDescription(SensorEntityDescription):
    """Beschreibt einen ASKOHEAT+-Sensor, der einen Pfad in einem der Endpunkte ausliest.

    ``source`` legt fest, auf welches Coordinator-Dict ``value_fn`` angewendet
    wird: "home" ist das regelmäßig gepollte gethome.json (Standard), die
    anderen sind die einmalig beim Start geladenen Sekundär-Endpunkte.
    "coordinator" ist ein Sonderfall: hier bekommt ``value_fn`` den Coordinator
    selbst statt eines Daten-Dicts (siehe last_update unten).
    """

    value_fn: Callable[[Any], Any]
    source: str = "home"


def _text(path: str) -> Callable[[dict[str, Any]], Any]:
    """Eine value_fn liefern, die einen Pfad als reinen Text liest."""
    return lambda data: get_path(data, path)


def _number(path: str) -> Callable[[dict[str, Any]], Any]:
    """Eine value_fn liefern, die einen Pfad liest und eine Zahl daraus extrahiert."""
    return lambda data: extract_number(get_path(data, path))


def _last_update(coordinator: AskoheatDataUpdateCoordinator) -> datetime | None:
    """value_fn für den last_update-Sensor: Zeitpunkt des letzten erfolgreichen Polls."""
    return coordinator.last_update_time


# Präfix von HARDWARE_VERSION (z.B. "RCe1.0", "HW 1.3", "HWe1.8") gibt die
# Gerätefamilie an: "RCe" = ASKOHEAT 2.0 mit EEPROM (das "e"), "HWe" = ASKOHEAT
# Classic mit EEPROM, "HW" = ASKOHEAT Classic ohne EEPROM. Die Zahl danach ist
# die Hardware-Generation. Quelle: Andreas (ASKOMA AG).
_HARDWARE_FAMILY_PREFIXES = {
    "RCe": "ASKOHEAT 2.0 (mit EEPROM)",
    "HWe": "ASKOHEAT Classic (mit EEPROM)",
    "HW": "ASKOHEAT Classic (ohne EEPROM)",
}


def _hardware_family(data: dict[str, Any]) -> str | None:
    """value_fn für den device_family-Sensor: Gerätefamilie aus HARDWARE_VERSION ableiten."""
    raw = get_path(data, "ASKOHEAT_PLUS_INFO.HARDWARE_VERSION")
    if not raw:
        return None
    match = re.match(r"[A-Za-z]+", str(raw))
    if not match:
        return None
    prefix = match.group()
    return _HARDWARE_FAMILY_PREFIXES.get(prefix, f"Unbekannt ({prefix})")


SENSOR_DESCRIPTIONS: tuple[AskoheatSensorEntityDescription, ...] = (
    AskoheatSensorEntityDescription(
        key="heater_step",
        translation_key="heater_step",
        icon="mdi:radiator",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_number("ACTUAL_VALUES.ACTUAL_HEATER_STEP"),
    ),
    AskoheatSensorEntityDescription(
        key="heater_load",
        translation_key="heater_load",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_number("ACTUAL_VALUES.ACTUAL_HEATER_LOAD"),
    ),
    AskoheatSensorEntityDescription(
        key="temperature_sensor_0",
        translation_key="temperature_sensor_0",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_number("ACTUAL_VALUES.TEMP_SENSOR_0"),
    ),
    # Sensor 0 sitzt immer direkt am Heizstab; 1-4 sind zusätzliche Messfühler
    # am Tank, nicht bei jeder Installation vorhanden.
    # entity_registry_enabled_default=False ist hier nur der Fallback für
    # Entities, die noch nie gesehen wurden — async_setup_entry() weiter unten
    # überschreibt das pro Gerät live, je nachdem ob der Sensor tatsächlich
    # einen Wert liefert, und aktiviert bereits registrierte Entities auf
    # demselben Weg rückwirkend.
    AskoheatSensorEntityDescription(
        key="temperature_sensor_1",
        translation_key="temperature_sensor_1",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_number("ACTUAL_VALUES.TEMP_SENSOR_1"),
    ),
    AskoheatSensorEntityDescription(
        key="temperature_sensor_2",
        translation_key="temperature_sensor_2",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_number("ACTUAL_VALUES.TEMP_SENSOR_2"),
    ),
    AskoheatSensorEntityDescription(
        key="temperature_sensor_3",
        translation_key="temperature_sensor_3",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_number("ACTUAL_VALUES.TEMP_SENSOR_3"),
    ),
    AskoheatSensorEntityDescription(
        key="temperature_sensor_4",
        translation_key="temperature_sensor_4",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_number("ACTUAL_VALUES.TEMP_SENSOR_4"),
    ),
    AskoheatSensorEntityDescription(
        key="temperature_limit_info",
        translation_key="temperature_limit_info",
        icon="mdi:thermometer-alert",
        value_fn=_text("ACTUAL_VALUES.ACTUAL_TEMPERATURE_LIMIT"),
    ),
    # Hinweis: SET_INPUTS.SET_HEATER_STEP / SET_LOAD_FEEDIN werden hier nicht
    # mehr als eigene read-only-Sensoren geführt — die Phase-2-Number-Entities
    # (number.py) zeigen und setzen dieselben Werte an einer Stelle.
    AskoheatSensorEntityDescription(
        key="error_status",
        translation_key="error_status",
        icon="mdi:alert-circle-outline",
        value_fn=_text("ASKOHEAT_PLUS_INFO.ERROR_STATUS"),
    ),
    AskoheatSensorEntityDescription(
        key="legio_info",
        translation_key="legio_info",
        icon="mdi:bacteria-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_text("ASKOHEAT_PLUS_INFO.LEGIO_INFO"),
    ),
    AskoheatSensorEntityDescription(
        key="last_update",
        translation_key="last_update",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        source="coordinator",
        value_fn=_last_update,
    ),
    # --- Diagnose-/statische Infos, alle aus demselben gethome.json-Poll ---
    AskoheatSensorEntityDescription(
        key="article_name",
        translation_key="article_name",
        icon="mdi:tag-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_text("ASKOHEAT_PLUS_INFO.ARTICLE_NAME"),
    ),
    AskoheatSensorEntityDescription(
        key="article_number",
        translation_key="article_number",
        icon="mdi:barcode",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_text("ASKOHEAT_PLUS_INFO.ARTICLE_NUMBER"),
    ),
    AskoheatSensorEntityDescription(
        key="serial_number",
        translation_key="serial_number",
        icon="mdi:identifier",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_text("ASKOHEAT_PLUS_INFO.SERIAL_NUMBER"),
    ),
    AskoheatSensorEntityDescription(
        key="software_version",
        translation_key="software_version",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_text("ASKOHEAT_PLUS_INFO.SOFTWARE_VERSION"),
    ),
    AskoheatSensorEntityDescription(
        key="hardware_version",
        translation_key="hardware_version",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_text("ASKOHEAT_PLUS_INFO.HARDWARE_VERSION"),
    ),
    AskoheatSensorEntityDescription(
        key="device_family",
        translation_key="device_family",
        icon="mdi:memory",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_hardware_family,
    ),
    AskoheatSensorEntityDescription(
        key="max_power",
        translation_key="max_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_number("ASKOHEAT_PLUS_INFO.MAX_POWER"),
    ),
    AskoheatSensorEntityDescription(
        key="number_of_heater",
        translation_key="number_of_heater",
        icon="mdi:counter",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_number("ASKOHEAT_PLUS_INFO.NUMBER_OF_HEATER"),
    ),
    AskoheatSensorEntityDescription(
        key="number_of_steps",
        translation_key="number_of_steps",
        icon="mdi:counter",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_number("ASKOHEAT_PLUS_INFO.NUMBER_OF_STEPS"),
    ),
    # --- Aus den Sekundär-Endpunkten, einmalig beim Start geladen (siehe coordinator.py) ---
    AskoheatSensorEntityDescription(
        key="temperature_precise",
        translation_key="temperature_precise",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
        source="temperature_calibration",
        value_fn=_number("TEMPERATURE_0.VALUE"),
    ),
    AskoheatSensorEntityDescription(
        key="tcp_connection",
        translation_key="tcp_connection",
        icon="mdi:lan-connect",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        source="wizard_status",
        value_fn=_text("MODBUS_INFO.TCP_CONNECTION"),
    ),
    AskoheatSensorEntityDescription(
        key="rtu_connection",
        translation_key="rtu_connection",
        icon="mdi:serial-port",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        source="wizard_status",
        value_fn=_text("MODBUS_INFO.RTU_CONNECTION"),
    ),
    AskoheatSensorEntityDescription(
        key="pv_peak",
        translation_key="pv_peak",
        icon="mdi:solar-power",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        source="registration",
        value_fn=_number("EXTRA.PV_PEAK"),
    ),
    AskoheatSensorEntityDescription(
        key="battery_size",
        translation_key="battery_size",
        icon="mdi:battery-high",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        source="registration",
        value_fn=_number("EXTRA.BATTERY"),
    ),
    # --- Installer-Einstellungen aus getwizard.json, die (noch) nicht als
    # schreibbare number/time-Entity abgebildet sind (siehe number.py/time.py)
    # verbleiben hier read-only. Kommunikations-Timeout bewusst nur als
    # Diagnose-Sensor: Andreas möchte hier explizit keinen Schreibzugriff,
    # ein falscher Wert könnte die Geräte-Kommunikation lahmlegen.
    # Einheit laut Feldname/Größenordnung vermutlich Sekunden, aber vom
    # Hersteller nicht explizit dokumentiert — deshalb bewusst ohne
    # native_unit_of_measurement, um keine falsche Einheit zu behaupten.
    AskoheatSensorEntityDescription(
        key="communication_timeout_heater_off",
        translation_key="communication_timeout_heater_off",
        icon="mdi:lan-disconnect",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        source="wizard",
        value_fn=_number("COMMUNICATION_TIMEOUT_HEATER_OFF"),
    ),
    AskoheatSensorEntityDescription(
        key="communication_timeout_reset",
        translation_key="communication_timeout_reset",
        icon="mdi:lan-disconnect",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        source="wizard",
        value_fn=_number("COMMUNICATION_TIMEOUT_RESET"),
    ),
)


class AskoheatSensor(AskoheatEntity, SensorEntity):
    """Ein ASKOHEAT+-Sensor, dessen value_fn gethome.json, einen Sekundär-Endpunkt
    oder (source="coordinator") den Coordinator selbst ausliest."""

    entity_description: AskoheatSensorEntityDescription

    @property
    def native_value(self) -> Any:
        source = self.entity_description.source
        if source == "coordinator":
            return self.entity_description.value_fn(self.coordinator)
        data = (
            self.coordinator.data
            if source == "home"
            else getattr(self.coordinator.secondary, source, None)
        )
        if not data:
            return None
        return self.entity_description.value_fn(data)


# 9999 ist der herstellerseitige Sentinel-Wert im Rohregister für "kein
# Sensor angeschlossen"; "not connected" ist die bereits in gethome.json
# verwendete Textform. Beides bedeutet: der Fühler ist nicht verkabelt.
_TEMP_SENSOR_DISCONNECTED_SENTINEL = 9999

_TEMP_SENSOR_PATHS: dict[str, str] = {
    f"temperature_sensor_{i}": f"ACTUAL_VALUES.TEMP_SENSOR_{i}" for i in range(1, 5)
}


def _is_temp_sensor_connected(data: dict[str, Any], path: str) -> bool:
    """Ein Fühler gilt als angeschlossen, außer er meldet "not connected" oder 9999."""
    value = extract_number(get_path(data, path))
    return value is not None and value != _TEMP_SENSOR_DISCONNECTED_SENTINEL


def _resolve_temp_sensor_defaults(
    data: dict[str, Any],
) -> tuple[AskoheatSensorEntityDescription, ...]:
    """temperature_sensor_1..4 einen live ermittelten entity_registry_enabled_default geben.

    Gilt nur für brandneue Entities, die der Registry noch nie bekannt waren —
    bereits registrierte werden separat in async_setup_entry behandelt.
    """
    return tuple(
        replace(
            description,
            entity_registry_enabled_default=_is_temp_sensor_connected(
                data, _TEMP_SENSOR_PATHS[description.key]
            ),
        )
        if description.key in _TEMP_SENSOR_PATHS
        else description
        for description in SENSOR_DESCRIPTIONS
    )


def _reenable_now_connected_temp_sensors(
    hass: HomeAssistant,
    coordinator: AskoheatDataUpdateCoordinator,
    data: dict[str, Any],
) -> None:
    """temperature_sensor_1..4 reaktivieren, die vorher standardmäßig deaktiviert
    waren, aber jetzt einen Wert liefern.

    entity_registry_enabled_default wirkt nur bei der erstmaligen Registrierung
    einer Entity — ein Fühler, der beim Ersteinrichten nicht angeschlossen war
    und später nachgerüstet wird, bliebe ohne diese Funktion für immer deaktiviert.
    """
    registry = er.async_get(hass)
    device_id = coordinator.device_id or coordinator.config_entry.entry_id
    for key, path in _TEMP_SENSOR_PATHS.items():
        if not _is_temp_sensor_connected(data, path):
            continue
        entity_id = registry.async_get_entity_id(
            "sensor", DOMAIN, f"{device_id}_{key}"
        )
        if not entity_id:
            continue
        entity_entry = registry.async_get(entity_id)
        if (
            entity_entry is not None
            and entity_entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION
        ):
            registry.async_update_entity(entity_id, disabled_by=None)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ASKOHEAT+-Sensoren aus einem Config-Entry einrichten."""
    coordinator = entry.runtime_data
    data = coordinator.data or {}
    descriptions = _resolve_temp_sensor_defaults(data)
    async_add_entities(AskoheatSensor(coordinator, description) for description in descriptions)
    _reenable_now_connected_temp_sensors(hass, coordinator, data)
