"""Data update coordinator for the ASKOHEAT+ integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AskoheatApiClient, AskoheatApiError, get_path
from .const import DOMAIN, MANUFACTURER, PATH_DEVICE_ID

_LOGGER = logging.getLogger(__name__)


@dataclass
class AskoheatSecondaryData:
    """Data from the low-frequency secondary endpoints, fetched once at startup."""

    wizard_status: dict[str, Any] = field(default_factory=dict)
    temperature_calibration: dict[str, Any] = field(default_factory=dict)
    registration: dict[str, Any] = field(default_factory=dict)


class AskoheatDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls gethome.json on a regular interval.

    Only gethome.json is polled repeatedly, by design (see
    docs/02_api-referenz.md, "Abfrage-Strategie") to avoid overloading the
    device's ESP32 controller. The remaining, less time-critical endpoints
    are fetched a single time after the first successful update.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: AskoheatApiClient,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self.secondary = AskoheatSecondaryData()
        self._secondary_fetched = False

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self.client.async_get_home()
        except AskoheatApiError as err:
            raise UpdateFailed(f"Error communicating with ASKOHEAT+: {err}") from err

        if not self._secondary_fetched:
            # Mark done before fetching: a failure here must not turn into a
            # retry storm against the device on every subsequent poll.
            self._secondary_fetched = True
            await self._async_fetch_secondary_once()

        return data

    async def _async_fetch_secondary_once(self) -> None:
        """Fetch the low-frequency secondary endpoints a single time."""
        fetchers = (
            ("wizard_status", self.client.async_get_wizard_status),
            ("temperature_calibration", self.client.async_get_temperature_calibration),
            ("registration", self.client.async_get_registration),
        )
        for key, fetch in fetchers:
            try:
                setattr(self.secondary, key, await fetch())
            except AskoheatApiError as err:
                _LOGGER.warning("Could not fetch secondary endpoint %s: %s", key, err)

    @property
    def device_id(self) -> str | None:
        """Return the device's MAC-style DEVICEID, used as the unique_id."""
        return get_path(self.data, PATH_DEVICE_ID) if self.data else None

    @property
    def device_info(self) -> DeviceInfo:
        """Build DeviceInfo from the ASKOHEAT_PLUS_INFO block of gethome.json."""
        info = get_path(self.data, "ASKOHEAT_PLUS_INFO") or {}
        device_id = self.device_id or self.config_entry.entry_id
        article_name = info.get("ARTICLE_NAME")
        return DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            manufacturer=MANUFACTURER,
            name=article_name or "ASKOHEAT+",
            model=article_name,
            hw_version=info.get("HARDWARE_VERSION"),
            sw_version=info.get("SOFTWARE_VERSION"),
            serial_number=info.get("SERIAL_NUMBER"),
            configuration_url=f"{self.client.base_url}/",
        )
