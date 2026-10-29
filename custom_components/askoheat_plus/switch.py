"""Switch-Plattform für die ASKOHEAT+-Integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry
from .api import AskoheatApiError, extract_number, get_path, parse_active
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


@dataclass(frozen=True, kw_only=True)
class AskoheatWizardFlagSwitchEntityDescription(SwitchEntityDescription):
    """Beschreibt ein einzelnes Bit eines Bitfeld-Registers aus getwizard.json.

    Die "Aktiviert"-Checkboxen der Temperatur-Funktionen liegen alle als
    einzelne Bits in MODBUS_CON_INPUT_SETTING (Legionellenschutz in
    MODBUS_CON_LEGIO_SETTING). Bitbelegung aus Jextended.js der Geräte-
    Weboberfläche (extended.html, Kachel "Temperatur Funktionen")
    rekonstruiert und gegen die Checkbox-Zustände beider Geräte abgeglichen.
    """

    wizard_key: str
    flag: int


WIZARD_FLAG_SWITCH_DESCRIPTIONS: tuple[AskoheatWizardFlagSwitchEntityDescription, ...] = (
    AskoheatWizardFlagSwitchEntityDescription(
        key="heat_pump_request_enabled",
        translation_key="heat_pump_request_enabled",
        icon="mdi:heat-pump",
        entity_category=EntityCategory.CONFIG,
        wizard_key="MODBUS_CON_INPUT_SETTING",
        flag=0x0080,
    ),
    AskoheatWizardFlagSwitchEntityDescription(
        key="minimum_temperature_enabled",
        translation_key="minimum_temperature_enabled",
        icon="mdi:thermometer-low",
        entity_category=EntityCategory.CONFIG,
        wizard_key="MODBUS_CON_INPUT_SETTING",
        flag=0x0200,
    ),
    AskoheatWizardFlagSwitchEntityDescription(
        key="low_tariff_enabled",
        translation_key="low_tariff_enabled",
        icon="mdi:cash-clock",
        entity_category=EntityCategory.CONFIG,
        wizard_key="MODBUS_CON_INPUT_SETTING",
        flag=0x0100,
    ),
    AskoheatWizardFlagSwitchEntityDescription(
        key="feedin_temperature_enabled",
        translation_key="feedin_temperature_enabled",
        icon="mdi:transmission-tower-import",
        entity_category=EntityCategory.CONFIG,
        wizard_key="MODBUS_CON_INPUT_SETTING",
        flag=0x0004,
    ),
    AskoheatWizardFlagSwitchEntityDescription(
        key="setpoint_temperature_enabled",
        translation_key="setpoint_temperature_enabled",
        icon="mdi:solar-power-variant",
        entity_category=EntityCategory.CONFIG,
        wizard_key="MODBUS_CON_INPUT_SETTING",
        flag=0x0008,
    ),
    AskoheatWizardFlagSwitchEntityDescription(
        key="heater_step_temperature_enabled",
        translation_key="heater_step_temperature_enabled",
        icon="mdi:radiator",
        entity_category=EntityCategory.CONFIG,
        wizard_key="MODBUS_CON_INPUT_SETTING",
        flag=0x0010,
    ),
    AskoheatWizardFlagSwitchEntityDescription(
        key="legio_enabled",
        translation_key="legio_enabled",
        icon="mdi:bacteria-outline",
        entity_category=EntityCategory.CONFIG,
        wizard_key="MODBUS_CON_LEGIO_SETTING",
        flag=0x8000,
    ),
)


class AskoheatWizardFlagSwitch(AskoheatEntity, SwitchEntity):
    """Ein Bit eines getwizard.json-Bitfelds, geschrieben über POST /server1/.

    Kein Keep-Alive nötig (Installer-Einstellung, kein 60s-Verfall). Schreiben
    per Read-Modify-Write im Coordinator, damit die übrigen Bits des
    gemeinsam genutzten Registers unverändert bleiben.
    """

    entity_description: AskoheatWizardFlagSwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        value = extract_number(
            self.coordinator.secondary.wizard.get(self.entity_description.wizard_key)
        )
        if value is None:
            return None
        return bool(int(value) & self.entity_description.flag)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_write(self.entity_description.flag)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_write(0)

    async def _async_write(self, bits: int) -> None:
        description = self.entity_description
        try:
            await self.coordinator.async_write_wizard_flags(
                description.wizard_key, description.flag, bits
            )
        except AskoheatApiError as err:
            raise HomeAssistantError(
                f"Could not set {description.key} on ASKOHEAT+: {err}"
            ) from err


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ASKOHEAT+-Switch-Entities aus einem Config-Entry einrichten."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            *(AskoheatSwitch(coordinator, description) for description in SWITCH_DESCRIPTIONS),
            *(
                AskoheatWizardFlagSwitch(coordinator, description)
                for description in WIZARD_FLAG_SWITCH_DESCRIPTIONS
            ),
        ]
    )
