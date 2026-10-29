"""Button-Plattform für die ASKOHEAT+-Integration — Einstellungen auf Anforderung neu laden."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry
from .entity import AskoheatEntity

RELOAD_SETTINGS_DESCRIPTION = ButtonEntityDescription(
    key="reload_settings",
    translation_key="reload_settings",
    icon="mdi:refresh",
    entity_category=EntityCategory.CONFIG,
)


class AskoheatReloadSettingsButton(AskoheatEntity, ButtonEntity):
    """Lädt getwizard.json & Co. neu (statt automatischem Polling dieser Endpunkte).

    Fehler einzelner Endpunkte werden im Coordinator nur geloggt (wie beim
    Start), die übrigen Endpunkte werden trotzdem aktualisiert.
    """

    async def async_press(self) -> None:
        await self.coordinator.async_reload_secondary()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ASKOHEAT+-Button-Entities aus einem Config-Entry einrichten."""
    coordinator = entry.runtime_data
    async_add_entities([AskoheatReloadSettingsButton(coordinator, RELOAD_SETTINGS_DESCRIPTION)])
