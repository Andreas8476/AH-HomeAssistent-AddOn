"""Verknüpft optionale Quell-Entities mit ASKOHEAT+-Number-Entities.

Ersetzt für den Standardfall die separate Blueprint-Automation
(`blueprints/askoheat_plus_feedin_from_meter.yaml`, siehe
docs/de/10_automatisierung.md): statt eine eigene Automation zu importieren,
wählt man die Quell-Entity direkt im Options-Flow der Integration aus. Die
Blueprint bleibt für Nutzer bestehen, die eigene Bedingungen/Filter wollen.

Technisch ruft dieses Modul denselben `number.set_value`-Service auf, den
auch die manuelle UI-Bedienung nutzt — der Keep-Alive in `number.py`
(`AskoheatNumber.async_set_native_value`) greift dadurch automatisch, ohne
dass hier eigene Schreib-/Wiederhol-Logik nötig ist.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, State
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_state_change_event

from .api import extract_number
from .const import (
    CONF_FEEDIN_SOURCE_ENTITY_ID,
    CONF_SETPOINT_SOURCE_ENTITY_ID,
    DOMAIN,
)
from .coordinator import AskoheatDataUpdateCoordinator

# Kein Import von "AskoheatConfigEntry" aus __init__.py hier: link.py wird von
# __init__.py selbst direkt importiert (nicht wie die Plattform-Module erst
# später von Home Assistant nachgeladen), ein Rückimport würde also einen
# Zirkelbezug riskieren. ConfigEntry[AskoheatDataUpdateCoordinator] ist
# ohnehin funktional identisch zu AskoheatConfigEntry.

_LOGGER = logging.getLogger(__name__)

# Options-Flow-Schlüssel -> unique_id-Suffix der zu steuernden Number-Entity.
_LINKABLE_TARGETS: dict[str, str] = {
    CONF_FEEDIN_SOURCE_ENTITY_ID: "load_feedin",
    CONF_SETPOINT_SOURCE_ENTITY_ID: "load_setpoint",
}


async def async_setup_links(
    hass: HomeAssistant,
    entry: ConfigEntry[AskoheatDataUpdateCoordinator],
    coordinator: AskoheatDataUpdateCoordinator,
) -> None:
    """Für jede im Options-Flow gesetzte Quell-Entity einen State-Listener einrichten."""
    registry = er.async_get(hass)
    device_id = coordinator.device_id or entry.entry_id

    for option_key, target_key in _LINKABLE_TARGETS.items():
        source_entity_id = entry.options.get(option_key)
        if not source_entity_id:
            continue

        target_entity_id = registry.async_get_entity_id(
            "number", DOMAIN, f"{device_id}_{target_key}"
        )
        if not target_entity_id:
            _LOGGER.warning(
                "Verknüpfung für %s übersprungen: Ziel-Entity %s nicht in der Registry gefunden",
                option_key,
                target_key,
            )
            continue

        forward = _make_forwarder(hass, target_entity_id)

        entry.async_on_unload(
            async_track_state_change_event(hass, [source_entity_id], forward)
        )

        # Sofort beim Setup einmal synchronisieren, statt erst auf die
        # nächste Zustandsänderung der Quelle zu warten.
        if (current_state := hass.states.get(source_entity_id)) is not None:
            await _async_forward_state(hass, target_entity_id, current_state)


def _make_forwarder(
    hass: HomeAssistant, target_entity_id: str
) -> Callable[[Event[EventStateChangedData]], Any]:
    """Einen Event-Handler bauen, der den neuen Zustand an target_entity_id weiterreicht."""

    async def _handle_state_change(event: Event[EventStateChangedData]) -> None:
        new_state = event.data["new_state"]
        await _async_forward_state(hass, target_entity_id, new_state)

    return _handle_state_change


async def _async_forward_state(
    hass: HomeAssistant, target_entity_id: str, source_state: State | None
) -> None:
    """Den numerischen Wert von source_state per number.set_value an target_entity_id senden."""
    if source_state is None or source_state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
        return
    value = extract_number(source_state.state)
    if value is None:
        return
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": target_entity_id, "value": value},
        blocking=True,
    )
