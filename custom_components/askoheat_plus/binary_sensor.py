"""Binary sensor platform for the ASKOHEAT+ integration."""

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
    """Describes an ASKOHEAT+ binary sensor backed by a path in gethome.json."""

    value_fn: Callable[[dict[str, Any]], bool | None]


def _active(path: str) -> Callable[[dict[str, Any]], bool | None]:
    """Return a value_fn that reads an "active"/"not active"-style path."""
    return lambda data: parse_active(get_path(data, path))


BINARY_SENSOR_DESCRIPTIONS: tuple[AskoheatBinarySensorEntityDescription, ...] = (
    AskoheatBinarySensorEntityDescription(
        key="pump_output",
        translation_key="pump_output",
        icon="mdi:pump",
        value_fn=_active("ACTUAL_VALUES.PUMP_OUTPUT"),
    ),
    AskoheatBinarySensorEntityDescription(
        key="emergency_mode",
        translation_key="emergency_mode",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=_active("STATUS_FLAGS.EMERGENCY_MODE"),
    ),
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
    """An ASKOHEAT+ binary sensor backed by a value_fn reading gethome.json."""

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
    """Set up ASKOHEAT+ binary sensors from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        AskoheatBinarySensor(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )
