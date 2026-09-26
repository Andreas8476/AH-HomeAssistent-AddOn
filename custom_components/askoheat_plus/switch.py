"""Switch-Plattform für die ASKOHEAT+-Integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry
from .api import AskoheatApiError, get_path, parse_active
from .const import CMD_EMERGENCY_OFF, CMD_EMERGENCY_ON, PATH_EMERGENCY_MODE
from .entity import AskoheatEntity


@dataclass(frozen=True, kw_only=True)
class AskoheatSwitchEntityDescription(SwitchEntityDescription):
    """Beschreibt einen ASKOHEAT+-Switch, gesteuert über parameterlose on/off-Befehle.

    Anders als die Number-Entities entsprechen diese dem physischen Taster am
    Gerät (z.B. Notbetrieb) — das Gerät setzt sie nicht automatisch zurück,
    daher ist hier kein Keep-Alive nötig.
    """

    on_command: str
    off_command: str
    value_path: str


SWITCH_DESCRIPTIONS: tuple[AskoheatSwitchEntityDescription, ...] = (
    AskoheatSwitchEntityDescription(
        key="emergency_mode",
        translation_key="emergency_mode",
        icon="mdi:alert-octagon-outline",
        on_command=CMD_EMERGENCY_ON,
        off_command=CMD_EMERGENCY_OFF,
        value_path=PATH_EMERGENCY_MODE,
    ),
)


class AskoheatSwitch(AskoheatEntity, SwitchEntity):
    """Ein ASKOHEAT+-Switch, gesteuert über parameterlose on/off-Inline-Commands."""

    entity_description: AskoheatSwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return parse_active(get_path(self.coordinator.data, self.entity_description.value_path))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_send(self.entity_description.on_command)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_send(self.entity_description.off_command)

    async def _async_send(self, command: str) -> None:
        try:
            await self.coordinator.client.async_send_bare_command(command)
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
    """ASKOHEAT+-Switch-Entities aus einem Config-Entry einrichten."""
    coordinator = entry.runtime_data
    async_add_entities(
        AskoheatSwitch(coordinator, description) for description in SWITCH_DESCRIPTIONS
    )
