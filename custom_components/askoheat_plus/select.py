"""Select-Plattform für die ASKOHEAT+-Integration — Fühler-/Intervall-Auswahl aus getwizard.json."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry
from .api import AskoheatApiError, extract_number
from .const import CONF_FEEDIN_SOURCE_ENTITY_ID, CONF_SETPOINT_SOURCE_ENTITY_ID
from .entity import AskoheatEntity

# Fühler-Auswahl: ein Bit pro Fühler (Radio-Gruppe in der Geräte-
# Weboberfläche), Sensor 0 = intern, 1–4 = extern.
_SENSOR_FLAGS: dict[str, int] = {
    "sensor_0": 0x0001,
    "sensor_1": 0x0002,
    "sensor_2": 0x0004,
    "sensor_3": 0x0008,
    "sensor_4": 0x0010,
}


@dataclass(frozen=True, kw_only=True)
class AskoheatWizardFlagSelectEntityDescription(SelectEntityDescription):
    """Beschreibt eine Radio-Gruppe (genau ein gesetztes Bit) in einem getwizard.json-Bitfeld.

    ``option_flags`` ordnet jeder Option ihr Bit zu; die Maske ergibt sich
    aus allen Bits zusammen, alle übrigen Bits des Registers bleiben beim
    Schreiben erhalten (Read-Modify-Write im Coordinator).
    """

    wizard_key: str
    option_flags: dict[str, int]


SELECT_DESCRIPTIONS: tuple[AskoheatWizardFlagSelectEntityDescription, ...] = (
    # In der Geräte-Weboberfläche hat zwar jede Zeile der Temperatur-
    # Funktionen ein eigenes Fühler-Dropdown, alle sechs schreiben aber
    # dieselben Bits 0x0001–0x0010 von MODBUS_CON_TEMPERATURE_SETTING
    # (Jextended.js) — es gibt also nur EINEN gemeinsamen Fühler für alle
    # Temperatur-Funktionen außer dem Legionellenschutz. Die Bits
    # 0x0800–0x8000 desselben Registers gehören zur Pufferladepumpe und
    # werden hier nicht angefasst.
    AskoheatWizardFlagSelectEntityDescription(
        key="temperature_sensor_select",
        translation_key="temperature_sensor_select",
        icon="mdi:thermometer-probe",
        entity_category=EntityCategory.CONFIG,
        wizard_key="MODBUS_CON_TEMPERATURE_SETTING",
        option_flags=_SENSOR_FLAGS,
        options=list(_SENSOR_FLAGS),
    ),
    AskoheatWizardFlagSelectEntityDescription(
        key="legio_sensor_select",
        translation_key="legio_sensor_select",
        icon="mdi:thermometer-probe",
        entity_category=EntityCategory.CONFIG,
        wizard_key="MODBUS_CON_LEGIO_SETTING",
        option_flags=_SENSOR_FLAGS,
        options=list(_SENSOR_FLAGS),
    ),
    AskoheatWizardFlagSelectEntityDescription(
        key="legio_interval_select",
        translation_key="legio_interval_select",
        icon="mdi:calendar-refresh",
        entity_category=EntityCategory.CONFIG,
        wizard_key="MODBUS_CON_LEGIO_SETTING",
        option_flags={
            "daily": 0x0100,
            "weekly": 0x0200,
            "fortnightly": 0x0400,
            "monthly": 0x0800,
        },
        options=["daily", "weekly", "fortnightly", "monthly"],
    ),
)


class AskoheatWizardFlagSelect(AskoheatEntity, SelectEntity):
    """Eine Radio-Gruppe aus einem getwizard.json-Bitfeld, geschrieben über POST /server1/."""

    entity_description: AskoheatWizardFlagSelectEntityDescription

    @property
    def current_option(self) -> str | None:
        value = extract_number(
            self.coordinator.secondary.wizard.get(self.entity_description.wizard_key)
        )
        if value is None:
            return None
        for option, flag in self.entity_description.option_flags.items():
            if int(value) & flag:
                return option
        return None

    async def async_select_option(self, option: str) -> None:
        description = self.entity_description
        mask = 0
        for flag in description.option_flags.values():
            mask |= flag
        try:
            await self.coordinator.async_write_wizard_flags(
                description.wizard_key, mask, description.option_flags[option]
            )
        except AskoheatApiError as err:
            raise HomeAssistantError(
                f"Could not set {description.key} on ASKOHEAT+: {err}"
            ) from err


@dataclass(frozen=True, kw_only=True)
class AskoheatLinkSelectEntityDescription(SelectEntityDescription):
    """Beschreibt die Quell-Auswahl einer Einspeisewert-/Leistungsvorgabe-Verknüpfung.

    ``option_key`` ist derselbe Options-Flow-Schlüssel, den auch der Dialog
    "⋮ → Konfigurieren" setzt (siehe config_flow.py/link.py) — Dashboard und
    Options-Flow bearbeiten also dieselbe Einstellung und bleiben synchron.
    """

    option_key: str


LINK_SELECT_DESCRIPTIONS: tuple[AskoheatLinkSelectEntityDescription, ...] = (
    AskoheatLinkSelectEntityDescription(
        key="feedin_source_select",
        translation_key="feedin_source_select",
        icon="mdi:link-variant",
        entity_category=EntityCategory.CONFIG,
        option_key=CONF_FEEDIN_SOURCE_ENTITY_ID,
    ),
    AskoheatLinkSelectEntityDescription(
        key="setpoint_source_select",
        translation_key="setpoint_source_select",
        icon="mdi:link-variant",
        entity_category=EntityCategory.CONFIG,
        option_key=CONF_SETPOINT_SOURCE_ENTITY_ID,
    ),
)

# Option für "keine Verknüpfung" (rein manuelle Steuerung), übersetzt.
LINK_NONE = "none"

_LINK_SOURCE_DOMAINS = ("sensor", "number", "input_number")
_POWER_UNITS = ("W", "kW")


class AskoheatLinkSelect(AskoheatEntity, SelectEntity):
    """Wählt die Quell-Entity für Einspeisewert/Leistungsvorgabe direkt im Dashboard.

    Angeboten werden alle Leistungs-Entities (device_class power bzw. Einheit
    W/kW) aus sensor/number/input_number, ohne die eigenen Entities dieses
    Geräts (eine Verknüpfung auf sich selbst wäre eine Schleife). Die Liste
    wird bei jedem Zugriff neu aufgebaut, neue Sensoren erscheinen also ohne
    Neustart. Eine im Options-Flow gewählte Entity, die keine Leistungs-
    Entity ist, wird trotzdem angezeigt, damit die Auswahl nie "leer" wirkt.
    Speichern aktualisiert die Optionen des Config-Entry; der bestehende
    Update-Listener (__init__.py) lädt die Integration daraufhin neu und
    link.py richtet die Verknüpfung ein — derselbe Weg wie beim Options-Flow.
    """

    entity_description: AskoheatLinkSelectEntityDescription

    @property
    def current_option(self) -> str | None:
        return self.coordinator.config_entry.options.get(self.entity_description.option_key) or LINK_NONE

    @property
    def options(self) -> list[str]:
        entry_id = self.coordinator.config_entry.entry_id
        registry = er.async_get(self.hass)
        own = {
            ent.entity_id for ent in er.async_entries_for_config_entry(registry, entry_id)
        }
        candidates = {
            state.entity_id
            for state in self.hass.states.async_all(_LINK_SOURCE_DOMAINS)
            if state.entity_id not in own
            and (
                state.attributes.get("device_class") == "power"
                or state.attributes.get("unit_of_measurement") in _POWER_UNITS
            )
        }
        current = self.current_option
        if current and current != LINK_NONE:
            candidates.add(current)
        return [LINK_NONE, *sorted(candidates)]

    async def async_select_option(self, option: str) -> None:
        entry = self.coordinator.config_entry
        options = dict(entry.options)
        if option == LINK_NONE:
            options.pop(self.entity_description.option_key, None)
        else:
            options[self.entity_description.option_key] = option
        self.hass.config_entries.async_update_entry(entry, options=options)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ASKOHEAT+-Select-Entities aus einem Config-Entry einrichten."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            *(
                AskoheatWizardFlagSelect(coordinator, description)
                for description in SELECT_DESCRIPTIONS
            ),
            *(AskoheatLinkSelect(coordinator, description) for description in LINK_SELECT_DESCRIPTIONS),
        ]
    )
