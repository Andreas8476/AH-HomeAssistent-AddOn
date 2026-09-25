"""Config flow for the ASKOHEAT+ integration."""

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
    """Handle a config flow for ASKOHEAT+."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step: ask for host/port and test the connection."""
        errors: dict[str, str] = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = AskoheatApiClient(
                session, user_input[CONF_HOST], user_input.get(CONF_PORT, DEFAULT_PORT)
            )
            try:
                data = await client.async_get_home()
            except AskoheatApiError as err:
                _LOGGER.debug("Connection test to %s failed: %s", user_input[CONF_HOST], err)
                errors["base"] = "cannot_connect"
            else:
                device_id = get_path(data, PATH_DEVICE_ID)
                if not device_id:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(device_id)
                    self._abort_if_unique_id_configured()

                    article_name = get_path(data, "ASKOHEAT_PLUS_INFO.ARTICLE_NAME")
                    title = article_name or f"ASKOHEAT+ ({user_input[CONF_HOST]})"
                    return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
