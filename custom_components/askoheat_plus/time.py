"""Time-Plattform für die ASKOHEAT+-Integration — schreibbare Uhrzeit-Installer-Einstellungen."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time

from homeassistant.components.time import TimeEntity, TimeEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry
from .api import AskoheatApiError, extract_number
from .entity import AskoheatEntity


@dataclass(frozen=True, kw_only=True)
class AskoheatWizardTimeEntityDescription(TimeEntityDescription):
    """Beschreibt eine schreibbare Uhrzeit-Installer-Einstellung aus getwizard.json.

    Das Gerät speichert Uhrzeiten als zwei getrennte Stunde/Minute-Felder
    (z.B. ``MODBUS_CON_LEGIO_ACTIV_TIME_HOUR``/``_MINUTE``) statt eines
    einzelnen Zeit-Strings — ``hour_key``/``minute_key`` bilden das ab.
    """

    hour_key: str
    minute_key: str


TIME_DESCRIPTIONS: tuple[AskoheatWizardTimeEntityDescription, ...] = (
    AskoheatWizardTimeEntityDescription(
        key="legio_activation_time_set",
        translation_key="legio_activation_time_set",
        icon="mdi:clock-start",
        entity_category=EntityCategory.CONFIG,
        hour_key="MODBUS_CON_LEGIO_ACTIV_TIME_HOUR",
        minute_key="MODBUS_CON_LEGIO_ACTIV_TIME_MINUTE",
    ),
    AskoheatWizardTimeEntityDescription(
        key="low_tariff_start_time_set",
        translation_key="low_tariff_start_time_set",
        icon="mdi:clock-start",
        entity_category=EntityCategory.CONFIG,
        hour_key="MODBUS_CON_LOW_TARIFF_START_TIME_HOUR",
        minute_key="MODBUS_CON_LOW_TARIFF_START_TIME_MINUTE",
    ),
    AskoheatWizardTimeEntityDescription(
        key="low_tariff_end_time_set",
        translation_key="low_tariff_end_time_set",
        icon="mdi:clock-end",
        entity_category=EntityCategory.CONFIG,
        hour_key="MODBUS_CON_LOW_TARIFF_END_TIME_HOUR",
        minute_key="MODBUS_CON_LOW_TARIFF_END_TIME_MINUTE",
    ),
    AskoheatWizardTimeEntityDescription(
        key="feedin_window_start_time_set",
        translation_key="feedin_window_start_time_set",
        icon="mdi:clock-start",
        entity_category=EntityCategory.CONFIG,
        hour_key="MODBUS_CON_USE_FEEDIN_START_TIME_HOUR",
        minute_key="MODBUS_CON_USE_FEEDIN_START_TIME_MINUTE",
    ),
    AskoheatWizardTimeEntityDescription(
        key="feedin_window_end_time_set",
        translation_key="feedin_window_end_time_set",
        icon="mdi:clock-end",
        entity_category=EntityCategory.CONFIG,
        hour_key="MODBUS_CON_USE_FEEDIN_END_TIME_HOUR",
        minute_key="MODBUS_CON_USE_FEEDIN_END_TIME_MINUTE",
    ),
    AskoheatWizardTimeEntityDescription(
        key="auto_reboot_time_set",
        translation_key="auto_reboot_time_set",
        icon="mdi:restart",
        entity_category=EntityCategory.CONFIG,
        hour_key="AUTO_REBOOT_HOUR",
        minute_key="AUTO_REBOOT_MINUTE",
    ),
)


class AskoheatWizardTime(AskoheatEntity, TimeEntity):
    """Eine schreibbare Uhrzeit-Installer-Einstellung aus getwizard.json.

    Wie AskoheatWizardNumber: liest/schreibt coordinator.secondary.wizard
    direkt über den POST-Endpunkt server1/ (api.py, async_write_wizard),
    kein Keep-Alive nötig (live verifiziert, kein 60s-Verfall).
    """

    entity_description: AskoheatWizardTimeEntityDescription

    @property
    def native_value(self) -> time | None:
        wizard = self.coordinator.secondary.wizard
        hour = extract_number(wizard.get(self.entity_description.hour_key))
        minute = extract_number(wizard.get(self.entity_description.minute_key))
        if hour is None or minute is None:
            return None
        return time(hour=int(hour), minute=int(minute))

    async def async_set_value(self, value: time) -> None:
        description = self.entity_description
        try:
            updated = await self.coordinator.client.async_write_wizard(
                {
                    description.hour_key: str(value.hour),
                    description.minute_key: str(value.minute),
                }
            )
        except AskoheatApiError as err:
            raise HomeAssistantError(
                f"Could not set {description.key} on ASKOHEAT+: {err}"
            ) from err
        self.coordinator.secondary.wizard = updated
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ASKOHEAT+-Time-Entities aus einem Config-Entry einrichten."""
    coordinator = entry.runtime_data
    async_add_entities(
        AskoheatWizardTime(coordinator, description) for description in TIME_DESCRIPTIONS
    )
