"""Number-Plattform für die ASKOHEAT+-Integration (Phase 2 — Steuern)."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
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
from homeassistant.helpers.event import async_track_time_interval

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
    NUMBER_KEEPALIVE_INTERVAL,
    PATH_MAX_POWER,
    PATH_NUMBER_OF_STEPS,
)
from .coordinator import AskoheatDataUpdateCoordinator
from .entity import AskoheatEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class AskoheatNumberEntityDescription(NumberEntityDescription):
    """Beschreibt ein ASKOHEAT+-Number-Steuerelement.

    ``command`` ist der bereits URL-kodierte Schreib-Endpunkt (siehe const.py).
    ``value_path`` liest den aktuellen Wert (zur Anzeige) aus gethome.json.
    ``max_value_path`` überschreibt, falls gesetzt, ``native_max_value``
    dynamisch mit einem bereits in gethome.json vorhandenen Wert
    (geräteseitig gemeldete Grenzwerte statt eines fest codierten Schätzwerts).
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
    """Ein setzbarer ASKOHEAT+-Wert, geschrieben über einen Inline-Command-Endpunkt.

    Das Gerät setzt diese Werte von sich aus ~60s nach dem letzten Schreiben
    zurück, wenn sie niemand erneut sendet (herstellerseitig dokumentiertes
    Verhalten — ein steuerndes Gerät soll kontinuierlich weitersenden). Diese
    Entity sendet den zuletzt gesetzten Wert alle NUMBER_KEEPALIVE_INTERVAL
    Sekunden erneut, solange er ungleich null ist, und stoppt, sobald er auf 0
    gesetzt wird (oder die Entity entfernt wird). Siehe docs/de/02_api-referenz.md.
    """

    entity_description: AskoheatNumberEntityDescription

    def __init__(
        self,
        coordinator: AskoheatDataUpdateCoordinator,
        description: AskoheatNumberEntityDescription,
    ) -> None:
        super().__init__(coordinator, description)
        self._last_set_value: float | None = None
        self._unsub_keepalive: Callable[[], None] | None = None

    @property
    def native_value(self) -> Any:
        # Den Wert, den wir gerade aktiv am Leben halten, gegenüber dem
        # nächsten SET_INPUTS.*-Snapshot bevorzugen — sofortiges UI-Feedback,
        # und korrekt solange ein Keep-Alive läuft, da wir selbst den Wert dort halten.
        if self._last_set_value is not None:
            return self._last_set_value
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
        await self._async_send(value)
        self._last_set_value = value
        self.async_write_ha_state()
        if value:
            self._start_keepalive()
        else:
            self._stop_keepalive()
        await self.coordinator.async_request_refresh()

    async def _async_send(self, value: float) -> None:
        try:
            await self.coordinator.client.async_send_command(
                self.entity_description.command, value
            )
        except AskoheatApiError as err:
            raise HomeAssistantError(
                f"Could not set {self.entity_description.key} on ASKOHEAT+: {err}"
            ) from err

    def _start_keepalive(self) -> None:
        self._stop_keepalive()
        self._unsub_keepalive = async_track_time_interval(
            self.hass, self._async_keepalive_tick, timedelta(seconds=NUMBER_KEEPALIVE_INTERVAL)
        )

    def _stop_keepalive(self) -> None:
        if self._unsub_keepalive is not None:
            self._unsub_keepalive()
            self._unsub_keepalive = None

    async def _async_keepalive_tick(self, _now: datetime) -> None:
        if not self._last_set_value:
            self._stop_keepalive()
            return
        try:
            await self.coordinator.client.async_send_command(
                self.entity_description.command, self._last_set_value
            )
        except AskoheatApiError as err:
            _LOGGER.warning(
                "Keep-alive resend failed for %s: %s", self.entity_description.key, err
            )

    async def async_will_remove_from_hass(self) -> None:
        self._stop_keepalive()
        await super().async_will_remove_from_hass()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ASKOHEAT+-Number-Entities aus einem Config-Entry einrichten."""
    coordinator = entry.runtime_data
    async_add_entities(
        AskoheatNumber(coordinator, description) for description in NUMBER_DESCRIPTIONS
    )
