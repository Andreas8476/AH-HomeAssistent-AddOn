"""Schlanker REST-Client für die lokale JSON-API des ASKOHEAT+.

Das Gerät stellt eine Reihe unauthentifizierter ``GET``-Endpunkte unter
``http://<host>/<endpoint>`` bereit, die JSON liefern. Die vollständige
Endpunkt-Referenz, gegen die diese Integration gebaut wurde, steht in
``docs/de/02_api-referenz.md``.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

_NUMBER_RE = re.compile(r"-?\d+(?:[.,]\d+)?")

# Textwerte, die in den verschiedenen bool-artigen String-Feldern des Geräts
# "aus"/"inaktiv" bedeuten (z.B. "not active", "off", "disabled").
_INACTIVE_VALUES = {"not active", "off", "disabled", "false", "no", "0"}


class AskoheatApiError(Exception):
    """Wird ausgelöst, wenn das ASKOHEAT+-Gerät nicht erreichbar ist oder unerwartet antwortet."""


class AskoheatApiClient:
    """Minimaler asynchroner Client für die lokale REST-API des ASKOHEAT+."""

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
        """Die Basis-URL des Geräts liefern, z.B. http://192.168.20.54:80."""
        return f"http://{self._host}:{self._port}"

    async def async_get_endpoint(self, endpoint: str) -> dict[str, Any]:
        """Einen einzelnen JSON-Endpunkt vom Gerät abrufen.

        Löst bei jedem Verbindungs-, Timeout- oder Parsing-Problem einen
        AskoheatApiError aus, damit Aufrufer nur einen Exception-Typ
        behandeln müssen.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            async with self._session.get(url) as response:
                response.raise_for_status()
                # Das Gerät sendet nicht immer einen korrekten
                # JSON-Content-Type-Header, daher den Body von Hand parsen
                # statt sich darauf zu verlassen.
                text = await response.text()
        except TimeoutError as err:
            raise AskoheatApiError(f"Timeout requesting {url}") from err
        except (aiohttp.ClientError, RuntimeError) as err:
            # RuntimeError deckt "Session is closed" ab, das aiohttp auslöst
            # (kein ClientError), wenn während des Herunterfahrens/Neustarts
            # ein Request noch läuft, während HAs gemeinsame Session
            # geschlossen wird.
            raise AskoheatApiError(f"Error requesting {url}: {err}") from err

        try:
            data = json.loads(text)
        except ValueError as err:
            raise AskoheatApiError(f"Invalid JSON from {url}: {err}") from err

        if not isinstance(data, dict):
            raise AskoheatApiError(f"Unexpected JSON shape from {url}: {data!r}")

        return data

    async def async_get_home(self) -> dict[str, Any]:
        """gethome.json abrufen — der einzige regelmäßig gepollte Endpunkt."""
        return await self.async_get_endpoint("gethome.json")

    async def async_get_wizard(self) -> dict[str, Any]:
        """getwizard.json abrufen — vollständiger Konfigurations-Dump, selten/on demand."""
        return await self.async_get_endpoint("getwizard.json")

    async def async_get_wizard_status(self) -> dict[str, Any]:
        """getwizard_status.json abrufen — Verbindungsdiagnose, einmalig beim Start."""
        return await self.async_get_endpoint("getwizard_status.json")

    async def async_get_temperature_calibration(self) -> dict[str, Any]:
        """gettemperature_calibration.json abrufen, einmalig beim Start."""
        return await self.async_get_endpoint("gettemperature_calibration.json")

    async def async_get_registration(self) -> dict[str, Any]:
        """getreg.json abrufen — Installationsmetadaten, einmalig beim Start."""
        return await self.async_get_endpoint("getreg.json")

    async def async_send_command(self, command: str, value: float | int) -> None:
        """Einen Schreib-Request ("Inline Command") senden, z.B. command="heater%20step".

        ``command`` muss bereits URL-kodiert sein (Leerzeichen als %20),
        passend zu den in docs/de/02_api-referenz.md dokumentierten Endpunkten.
        """
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        url = f"{self.base_url}/{command}?value={value}"
        try:
            async with self._session.get(url) as response:
                response.raise_for_status()
        except TimeoutError as err:
            raise AskoheatApiError(f"Timeout sending command to {url}") from err
        except (aiohttp.ClientError, RuntimeError) as err:
            raise AskoheatApiError(f"Error sending command to {url}: {err}") from err

    async def async_send_bare_command(self, path: str) -> None:
        """Einen parameterlosen Befehl senden, z.B. path="on" für den Notbetrieb.

        Anders als async_send_command nehmen diese Endpunkte kein ``?value=``
        entgegen und wirken wie ein physischer Tastendruck am Gerät (kein
        60s-Auto-Verfall).
        """
        url = f"{self.base_url}/{path}"
        try:
            async with self._session.get(url) as response:
                response.raise_for_status()
        except TimeoutError as err:
            raise AskoheatApiError(f"Timeout sending command to {url}") from err
        except (aiohttp.ClientError, RuntimeError) as err:
            raise AskoheatApiError(f"Error sending command to {url}: {err}") from err


def get_path(data: dict[str, Any], path: str) -> Any | None:
    """Einen gepunkteten Pfad (z.B. "ACTUAL_VALUES.ACTUAL_HEATER_STEP") in einem verschachtelten Dict nachschlagen."""
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def extract_number(value: Any) -> float | None:
    """Eine Fließkommazahl aus Werten wie "0 watts", "24 °C" oder reinen Zahlen extrahieren.

    Liefert None, wenn keine Zahl gefunden werden kann (z.B. leerer String,
    "not connected").
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
    """Geräteseitige "active"/"not active"-artige Strings in einen bool umwandeln.

    Liefert None, wenn der Wert leer/unbekannt ist, statt zu raten.
    """
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    return text not in _INACTIVE_VALUES
