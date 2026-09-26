"""Sensor platform for the ASKOHEAT+ integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
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
    """Describes an ASKOHEAT+ sensor backed by a path in one of the fetched endpoints.

    ``source`` selects which coordinator-held dict ``value_fn`` is applied to:
    "home" is the regularly-polled gethome.json (default), the others are the
    secondary endpoints fetched once at startup (see coordinator.py).
    """

    value_fn: Callable[[dict[str, Any]], Any]
    source: str = "home"


def _text(path: str) -> Callable[[dict[str, Any]], Any]:
    """Return a value_fn that reads a path as plain text."""
    return lambda data: get_path(data, path)


def _number(path: str) -> Callable[[dict[str, Any]], Any]:
    """Return a value_fn that reads a path and extracts a number from it."""
    return lambda data: extract_number(get_path(data, path))


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
    # Sensor 0 is always the one at the heating element itself; 1-4 are
    # additional probes along the tank, not present on every installation.
    # entity_registry_enabled_default=False here is only the fallback for
    # entities never seen before — async_setup_entry() below overrides it
    # per-device based on whether the sensor actually reports a value, and
    # retroactively re-enables already-registered ones the same way.
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
    # Note: SET_INPUTS.SET_HEATER_STEP / SET_LOAD_FEEDIN are no longer shown
    # as separate read-only sensors here — the Phase 2 number entities
    # (number.py) display and set the same values in one place.
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
    # --- Diagnostic/static info, all from the same gethome.json poll ---
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
    # --- From secondary endpoints, fetched once at startup (see coordinator.py) ---
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
)


class AskoheatSensor(AskoheatEntity, SensorEntity):
    """An ASKOHEAT+ sensor backed by a value_fn reading gethome.json or a secondary endpoint."""

    entity_description: AskoheatSensorEntityDescription

    @property
    def native_value(self) -> Any:
        source = self.entity_description.source
        data = (
            self.coordinator.data
            if source == "home"
            else getattr(self.coordinator.secondary, source, None)
        )
        if not data:
            return None
        return self.entity_description.value_fn(data)


# 9999 is the manufacturer's raw-register "no sensor connected" sentinel;
# "not connected" is the plain-text form already used in gethome.json today.
# Both mean the probe isn't physically wired up.
_TEMP_SENSOR_DISCONNECTED_SENTINEL = 9999

_TEMP_SENSOR_PATHS: dict[str, str] = {
    f"temperature_sensor_{i}": f"ACTUAL_VALUES.TEMP_SENSOR_{i}" for i in range(1, 5)
}


def _is_temp_sensor_connected(data: dict[str, Any], path: str) -> bool:
    """A probe counts as connected unless it reports "not connected" or 9999."""
    value = extract_number(get_path(data, path))
    return value is not None and value != _TEMP_SENSOR_DISCONNECTED_SENTINEL


def _resolve_temp_sensor_defaults(
    data: dict[str, Any],
) -> tuple[AskoheatSensorEntityDescription, ...]:
    """Give temperature_sensor_1..4 a live entity_registry_enabled_default.

    Applies only to brand-new entities never seen by the registry before —
    already-registered ones are handled separately in async_setup_entry.
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
    """Re-enable temperature_sensor_1..4 that were disabled-by-default before but now report a value.

    entity_registry_enabled_default only affects an entity the first time it's
    registered, so a probe that was unconnected during initial setup and gets
    wired up later would otherwise stay disabled forever without this.
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
    """Set up ASKOHEAT+ sensors from a config entry."""
    coordinator = entry.runtime_data
    data = coordinator.data or {}
    descriptions = _resolve_temp_sensor_defaults(data)
    async_add_entities(AskoheatSensor(coordinator, description) for description in descriptions)
    _reenable_now_connected_temp_sensors(hass, coordinator, data)
