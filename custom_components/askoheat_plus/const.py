"""Constants for the ASKOHEAT+ integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "askoheat_plus"
MANUFACTURER = "Askoma"

DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 30  # seconds; device web UI itself polls every 2s.
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 300

CONF_SCAN_INTERVAL_DEFAULT = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

# Primary polling endpoint: single request per cycle, deliberately kept to just
# this one endpoint to avoid overloading the device's ESP32 controller. It
# already contains device info, live values, set inputs and status flags.
ENDPOINT_HOME = "gethome.json"

# Secondary endpoints: fetched once at startup only (not on the regular
# polling cycle). Cadence/refresh strategy for these is an open point, see
# docs/07_changelog.md.
ENDPOINT_WIZARD = "getwizard.json"
ENDPOINT_WIZARD_STATUS = "getwizard_status.json"
ENDPOINT_TEMPERATURE_CALIBRATION = "gettemperature_calibration.json"
ENDPOINT_REGISTRATION = "getreg.json"

# Path (within gethome.json) used as the unique_id for the config entry.
PATH_DEVICE_ID = "ASKOHEAT_PLUS_INFO.DEVICEID"
