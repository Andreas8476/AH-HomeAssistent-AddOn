"""Config-Flow für die ASKOHEAT+-Integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .api import AskoheatApiClient, AskoheatApiError, get_path
from .const import (
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    PATH_DEVICE_ID,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): NumberSelector(
            NumberSelectorConfig(
                min=MIN_SCAN_INTERVAL,
                max=MAX_SCAN_INTERVAL,
                step=1,
                unit_of_measurement="s",
                mode=NumberSelectorMode.BOX,
            )
        ),
    }
)


class AskoheatConfigFlow(ConfigFlow, domain=DOMAIN):
    """Behandelt einen Config-Flow für ASKOHEAT+."""

    VERSION = 1

    async def _async_validate(
        self, user_input: dict[str, Any]
    ) -> tuple[dict[str, Any] | None, str | None]:
        """Die Verbindung testen. Liefert (gethome.json-Daten, Fehlercode)."""
        session = async_get_clientsession(self.hass)
        client = AskoheatApiClient(
            session, user_input[CONF_HOST], user_input.get(CONF_PORT, DEFAULT_PORT)
        )
        try:
            data = await client.async_get_home()
        except AskoheatApiError as err:
            _LOGGER.debug("Connection test to %s failed: %s", user_input[CONF_HOST], err)
            return None, "cannot_connect"

        if not get_path(data, PATH_DEVICE_ID):
            return None, "cannot_connect"
        return data, None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Den ersten Schritt behandeln: Host/Port abfragen und die Verbindung testen."""
        errors: dict[str, str] = {}

        if user_input is not None:
            data, error = await self._async_validate(user_input)
            if error:
                errors["base"] = error
            else:
                device_id = get_path(data, PATH_DEVICE_ID)
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()

                article_name = get_path(data, "ASKOHEAT_PLUS_INFO.ARTICLE_NAME")
                title = article_name or f"ASKOHEAT+ ({user_input[CONF_HOST]})"
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Änderung von Host/Port/Abfrageintervall nach der Ersteinrichtung erlauben.

        Erreichbar über das "..."-Menü des Config-Entry -> "Neu konfigurieren".
        Nutzt denselben Verbindungstest wie die Ersteinrichtung; das gefundene
        Gerät muss dasselbe physische Gerät (gleiche DEVICEID) sein, für das
        der Entry ursprünglich eingerichtet wurde, damit ein Entry nicht
        stillschweigend auf ein anderes Gerät umgebogen wird.
        """
        reconfigure_entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            data, error = await self._async_validate(user_input)
            if error:
                errors["base"] = error
            else:
                device_id = get_path(data, PATH_DEVICE_ID)
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_mismatch(reason="wrong_device")
                return self.async_update_reload_and_abort(
                    reconfigure_entry, data=user_input
                )

        current = reconfigure_entry.data
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current.get(CONF_HOST)): str,
                vol.Optional(
                    CONF_PORT, default=current.get(CONF_PORT, DEFAULT_PORT)
                ): int,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=MAX_SCAN_INTERVAL,
                        step=1,
                        unit_of_measurement="s",
                        mode=NumberSelectorMode.BOX,
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="reconfigure", data_schema=schema, errors=errors
        )
