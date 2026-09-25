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

# Write ("inline command") endpoints, see docs/02_api-referenz.md. Values set
# through these revert on the device after ~60s if not resent by a
# controller — this integration does not implement a keep-alive for that,
# see docs/02_api-referenz.md.
CMD_HEATER_STEP = "heater%20step"
CMD_LOAD_SETPOINT = "load%20setpoint"
CMD_LOAD_FEEDIN = "load%20feedin"

# Bare commands (no ?value=), act like the physical button on the device —
# no 60s auto-revert, so no keep-alive needed for these.
CMD_EMERGENCY_ON = "on"
CMD_EMERGENCY_OFF = "off"
PATH_EMERGENCY_MODE = "STATUS_FLAGS.EMERGENCY_MODE"

PATH_NUMBER_OF_STEPS = "ASKOHEAT_PLUS_INFO.NUMBER_OF_STEPS"
PATH_MAX_POWER = "ASKOHEAT_PLUS_INFO.MAX_POWER"

# Fallback bounds used only if the dynamic path above is unavailable.
FALLBACK_MAX_HEATER_STEP = 19  # documented max for booster models
FALLBACK_MAX_LOAD_SETPOINT = 20000

# SET_LOAD_FEEDIN_INT16 in the device's own JSON implies int16 storage.
LOAD_FEEDIN_MIN = -32768
LOAD_FEEDIN_MAX = 32767

# The device auto-reverts a written value ~60s after the last write if
# nothing resends it. Number entities resend the last value on this interval
# (safely under 60s) for as long as it's non-zero. Confirmed with the
# manufacturer-documented behavior that a controlling device is expected to
# do this — unlike the read-polling caution, periodic resends here are fine.
NUMBER_KEEPALIVE_INTERVAL = 45
