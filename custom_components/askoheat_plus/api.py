"""Lightweight REST client for the ASKOHEAT+ local JSON API.

The device exposes a set of unauthenticated ``GET`` endpoints under
``http://<host>/<endpoint>`` that return JSON. See ``docs/02_api-referenz.md``
for the full endpoint reference this integration was built against.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

_NUMBER_RE = re.compile(r"-?\d+(?:[.,]\d+)?")

# Text values that mean "off"/"inactive" across the various boolean-ish
# string fields returned by the device (e.g. "not active", "off", "disabled").
_INACTIVE_VALUES = {"not active", "off", "disabled", "false", "no", "0"}


class AskoheatApiError(Exception):
    """Raised when the ASKOHEAT+ device cannot be reached or replies unexpectedly."""


class AskoheatApiClient:
    """Minimal async client for the ASKOHEAT+ local REST API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int = 80,
    ) -> None:
        self._session = session
        self._host = host
        self._port = port

    @property
    def base_url(self) -> str:
        """Return the base URL of the device, e.g. http://192.168.20.54:80."""
        return f"http://{self._host}:{self._port}"

    async def async_get_endpoint(self, endpoint: str) -> dict[str, Any]:
        """Fetch a single JSON endpoint from the device.

        Raises AskoheatApiError on any connection, timeout or parsing problem
        so callers only need to handle one exception type.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            async with self._session.get(url) as response:
                response.raise_for_status()
                # The device does not always send a proper JSON content-type
                # header, so parse the body manually instead of relying on it.
                text = await response.text()
        except aiohttp.ClientError as err:
            raise AskoheatApiError(f"Error requesting {url}: {err}") from err
        except TimeoutError as err:
            raise AskoheatApiError(f"Timeout requesting {url}") from err

        try:
            data = json.loads(text)
        except ValueError as err:
            raise AskoheatApiError(f"Invalid JSON from {url}: {err}") from err

        if not isinstance(data, dict):
            raise AskoheatApiError(f"Unexpected JSON shape from {url}: {data!r}")

        return data

    async def async_get_home(self) -> dict[str, Any]:
        """Fetch gethome.json — the single endpoint polled regularly."""
        return await self.async_get_endpoint("gethome.json")

    async def async_get_wizard(self) -> dict[str, Any]:
        """Fetch getwizard.json — full config dump, fetched rarely/on demand."""
        return await self.async_get_endpoint("getwizard.json")

    async def async_get_wizard_status(self) -> dict[str, Any]:
        """Fetch getwizard_status.json — connection diagnostics, fetched once at startup."""
        return await self.async_get_endpoint("getwizard_status.json")

    async def async_get_temperature_calibration(self) -> dict[str, Any]:
        """Fetch gettemperature_calibration.json, fetched once at startup."""
        return await self.async_get_endpoint("gettemperature_calibration.json")

    async def async_get_registration(self) -> dict[str, Any]:
        """Fetch getreg.json — installation metadata, fetched once at startup."""
        return await self.async_get_endpoint("getreg.json")


def get_path(data: dict[str, Any], path: str) -> Any | None:
    """Look up a dotted path (e.g. "ACTUAL_VALUES.ACTUAL_HEATER_STEP") in a nested dict."""
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def extract_number(value: Any) -> float | None:
    """Extract a float from values like "0 watts", "24 °C" or plain numbers.

    Returns None if no number can be found (e.g. empty string, "not connected").
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = _NUMBER_RE.search(str(value).replace(",", "."))
    if not match:
        return None
    try:
        return float(match.group().replace(",", "."))
    except ValueError:
        return None


def parse_active(value: Any) -> bool | None:
    """Parse device "active"/"not active"-style strings into a bool.

    Returns None if the value is empty/unknown rather than guessing.
    """
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    return text not in _INACTIVE_VALUES
