"""Binary-Sensor-Plattform für die ASKOHEAT+-Integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry
from .api import get_path, parse_active
from .entity import AskoheatEntity


@dataclass(frozen=True, kw_only=True)
class AskoheatBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Beschreibt einen ASKOHEAT+-Binary-Sensor, der einen Pfad in gethome.json ausliest."""

    value_fn: Callable[[dict[str, Any]], bool | None]


def _active(path: str) -> Callable[[dict[str, Any]], bool | None]:
    """Eine value_fn liefern, die einen "active"/"not active"-artigen Pfad liest."""
    return lambda data: parse_active(get_path(data, path))


BINARY_SENSOR_DESCRIPTIONS: tuple[AskoheatBinarySensorEntityDescription, ...] = (
    AskoheatBinarySensorEntityDescription(
        key="pump_output",
        translation_key="pump_output",
        icon="mdi:pump",
        value_fn=_active("ACTUAL_VALUES.PUMP_OUTPUT"),
    ),
    # Hinweis: emergency_mode ist kein binary_sensor mehr — siehe switch.py,
    # das ihn sowohl anzeigt als auch steuert (das Gerät stellt dafür einen
    # echten on/off-Befehl bereit, anders als die übrigen STATUS_FLAGS.*-Felder hier).
    AskoheatBinarySensorEntityDescription(
        key="heater_disabled",
        translation_key="heater_disabled",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=_active("STATUS_FLAGS.HEATER_DISABLED"),
    ),
    AskoheatBinarySensorEntityDescription(
        key="relayboard_connected",
        translation_key="relayboard_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_active("STATUS_FLAGS.RELAYBOARD_CONNECTED"),
    ),
    AskoheatBinarySensorEntityDescription(
        key="current_flow",
        translation_key="current_flow",
        icon="mdi:current-ac",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_active("STATUS_FLAGS.CURRENT_FLOW"),
    ),
)


class AskoheatBinarySensor(AskoheatEntity, BinarySensorEntity):
    """Ein ASKOHEAT+-Binary-Sensor, dessen value_fn gethome.json ausliest."""

    entity_description: AskoheatBinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ASKOHEAT+-Binary-Sensoren aus einem Config-Entry einrichten."""
    coordinator = entry.runtime_data
    async_add_entities(
        AskoheatBinarySensor(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )
