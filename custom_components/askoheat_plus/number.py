"""Number platform for the ASKOHEAT+ integration (Phase 2 — Steuern)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry
from .api import AskoheatApiError, extract_number, get_path
from .const import (
    CMD_HEATER_STEP,
    CMD_LOAD_FEEDIN,
    CMD_LOAD_SETPOINT,
    FALLBACK_MAX_HEATER_STEP,
    FALLBACK_MAX_LOAD_SETPOINT,
    LOAD_FEEDIN_MAX,
    LOAD_FEEDIN_MIN,
    PATH_MAX_POWER,
    PATH_NUMBER_OF_STEPS,
)
from .entity import AskoheatEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class AskoheatNumberEntityDescription(NumberEntityDescription):
    """Describes an ASKOHEAT+ number control.

    ``command`` is the already-URL-encoded write endpoint (see const.py).
    ``value_path`` reads the current value (for display) from gethome.json.
    ``max_value_path``, if set, overrides ``native_max_value`` dynamically
    from a value already present in gethome.json (device-reported limits
    instead of a hardcoded guess).
    """

    command: str
    value_path: str
    max_value_path: str | None = None


NUMBER_DESCRIPTIONS: tuple[AskoheatNumberEntityDescription, ...] = (
    AskoheatNumberEntityDescription(
        key="heater_step_target",
        translation_key="heater_step_target",
        icon="mdi:radiator",
        native_min_value=0,
        native_max_value=FALLBACK_MAX_HEATER_STEP,
        native_step=1,
        command=CMD_HEATER_STEP,
        value_path="SET_INPUTS.SET_HEATER_STEP",
        max_value_path=PATH_NUMBER_OF_STEPS,
    ),
    AskoheatNumberEntityDescription(
        key="load_setpoint",
        translation_key="load_setpoint",
        device_class=NumberDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        native_min_value=0,
        native_max_value=FALLBACK_MAX_LOAD_SETPOINT,
        native_step=50,
        mode=NumberMode.BOX,
        command=CMD_LOAD_SETPOINT,
        value_path="SET_INPUTS.SET_LOAD_SETPOINT",
        max_value_path=PATH_MAX_POWER,
    ),
    AskoheatNumberEntityDescription(
        key="load_feedin",
        translation_key="load_feedin",
        device_class=NumberDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        native_min_value=LOAD_FEEDIN_MIN,
        native_max_value=LOAD_FEEDIN_MAX,
        native_step=10,
        mode=NumberMode.BOX,
        command=CMD_LOAD_FEEDIN,
        value_path="SET_INPUTS.SET_LOAD_FEEDIN",
    ),
)


class AskoheatNumber(AskoheatEntity, NumberEntity):
    """A settable ASKOHEAT+ value, backed by an inline-command endpoint.

    Note: the device reverts these values on its own ~60s after the last
    write if nothing resends them — see docs/02_api-referenz.md. This
    integration does not resend/keep-alive automatically.
    """

    entity_description: AskoheatNumberEntityDescription

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        return extract_number(get_path(self.coordinator.data, self.entity_description.value_path))

    @property
    def native_max_value(self) -> float:
        max_path = self.entity_description.max_value_path
        if max_path and self.coordinator.data:
            dynamic_max = extract_number(get_path(self.coordinator.data, max_path))
            if dynamic_max is not None:
                return dynamic_max
        return self.entity_description.native_max_value

    async def async_set_native_value(self, value: float) -> None:
        try:
            await self.coordinator.client.async_send_command(
                self.entity_description.command, value
            )
        except AskoheatApiError as err:
            raise HomeAssistantError(
                f"Could not set {self.entity_description.key} on ASKOHEAT+: {err}"
            ) from err
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ASKOHEAT+ number entities from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        AskoheatNumber(coordinator, description) for description in NUMBER_DESCRIPTIONS
    )
