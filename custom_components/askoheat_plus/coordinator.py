"""Update-Coordinator für die ASKOHEAT+-Integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import AskoheatApiClient, AskoheatApiError, get_path
from .const import DOMAIN, MANUFACTURER, PATH_DEVICE_ID

_LOGGER = logging.getLogger(__name__)


@dataclass
class AskoheatSecondaryData:
    """Daten der selten abgefragten Sekundär-Endpunkte, einmalig beim Start geladen."""

    wizard_status: dict[str, Any] = field(default_factory=dict)
    temperature_calibration: dict[str, Any] = field(default_factory=dict)
    registration: dict[str, Any] = field(default_factory=dict)
    wizard: dict[str, Any] = field(default_factory=dict)


class AskoheatDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator, der gethome.json in regelmäßigem Intervall abfragt.

    Nur gethome.json wird wiederholt abgefragt, bewusst so entworfen (siehe
    docs/de/02_api-referenz.md, "Abfrage-Strategie"), um den ESP32-Controller
    des Geräts nicht zu überlasten. Die übrigen, weniger zeitkritischen
    Endpunkte werden nur einmalig nach dem ersten erfolgreichen Update geladen.
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
        # Zeitpunkt des letzten erfolgreichen Polls, für die "Herzschlag"-
        # Anzeige im Dashboard. last_updated von normalen Sensoren eignet sich
        # dafür nicht: Home Assistant aktualisiert last_updated nur, wenn sich
        # der Wert selbst ändert, nicht bei jedem Poll (z.B. bei konstanter
        # Heizleistung stand hier sonst ein veralteter Zeitstempel).
        self.last_update_time: datetime | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self.client.async_get_home()
        except AskoheatApiError as err:
            raise UpdateFailed(f"Error communicating with ASKOHEAT+: {err}") from err

        self.last_update_time = dt_util.utcnow()

        if not self._secondary_fetched:
            # Vor dem Abruf schon als erledigt markieren: ein Fehlschlag hier
            # darf bei jedem weiteren Poll keinen Retry-Sturm gegen das Gerät auslösen.
            self._secondary_fetched = True
            await self._async_fetch_secondary_once()

        return data

    async def _async_fetch_secondary_once(self) -> None:
        """Die selten abgefragten Sekundär-Endpunkte einmalig laden."""
        fetchers = (
            ("wizard_status", self.client.async_get_wizard_status),
            ("temperature_calibration", self.client.async_get_temperature_calibration),
            ("registration", self.client.async_get_registration),
            # Installer-Einstellungen (Legionellenschutz, Niedertarif,
            # Einspeise-Zeitfenster, Wärmepumpen-Anforderung, Timeouts, ...),
            # aktuell nur lesend als Diagnose-Sensoren abgebildet (siehe
            # sensor.py). Wie die anderen Sekundär-Endpunkte nur einmalig
            # beim Start geladen, spiegelt also den Stand bei Integrations-
            # Start wider, nicht live.
            ("wizard", self.client.async_get_wizard),
        )
        for key, fetch in fetchers:
            try:
                setattr(self.secondary, key, await fetch())
            except AskoheatApiError as err:
                _LOGGER.warning("Could not fetch secondary endpoint %s: %s", key, err)

    @property
    def device_id(self) -> str | None:
        """Die MAC-artige DEVICEID des Geräts liefern, verwendet als unique_id."""
        return get_path(self.data, PATH_DEVICE_ID) if self.data else None

    @property
    def device_info(self) -> DeviceInfo:
        """DeviceInfo aus dem ASKOHEAT_PLUS_INFO-Block von gethome.json aufbauen."""
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
