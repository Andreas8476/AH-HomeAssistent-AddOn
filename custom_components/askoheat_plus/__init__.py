"""The ASKOHEAT+ integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AskoheatApiClient
from .const import DEFAULT_PORT, DEFAULT_SCAN_INTERVAL
from .coordinator import AskoheatDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.NUMBER]

type AskoheatConfigEntry = ConfigEntry[AskoheatDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AskoheatConfigEntry) -> bool:
    """Set up ASKOHEAT+ from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    session = async_get_clientsession(hass)
    client = AskoheatApiClient(session, host, port)
    coordinator = AskoheatDataUpdateCoordinator(hass, entry, client, scan_interval)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: AskoheatConfigEntry) -> bool:
    """Unload an ASKOHEAT+ config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
