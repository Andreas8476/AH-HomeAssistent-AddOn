"""Konstanten für die ASKOHEAT+-Integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "askoheat_plus"
MANUFACTURER = "Askoma"

DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 30  # Sekunden; die Geräte-Web-UI selbst pollt alle 2s.
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 300

CONF_SCAN_INTERVAL_DEFAULT = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

# Primärer Polling-Endpunkt: ein einzelner Request pro Zyklus, bewusst auf nur
# diesen einen Endpunkt beschränkt, um den ESP32-Controller des Geräts nicht
# zu überlasten. Enthält bereits Geräteinfo, Live-Werte, gesetzte Eingaben
# und Status-Flags.
ENDPOINT_HOME = "gethome.json"

# Sekundär-Endpunkte: nur einmalig beim Start geladen (nicht im regulären
# Polling-Zyklus). Abfrage-/Refresh-Strategie dafür ist noch offen, siehe
# docs/de/07_changelog.md.
ENDPOINT_WIZARD = "getwizard.json"
ENDPOINT_WIZARD_STATUS = "getwizard_status.json"
ENDPOINT_TEMPERATURE_CALIBRATION = "gettemperature_calibration.json"
ENDPOINT_REGISTRATION = "getreg.json"

# Pfad (innerhalb von gethome.json), der als unique_id des Config-Entry dient.
PATH_DEVICE_ID = "ASKOHEAT_PLUS_INFO.DEVICEID"

# Schreib-Endpunkte ("Inline Commands"), siehe docs/de/02_api-referenz.md.
# Über diese gesetzte Werte verfallen am Gerät nach ~60s, wenn sie nicht von
# einem Controller erneut gesendet werden — diese Integration implementiert
# dafür einen eingebauten Keep-Alive, siehe NUMBER_KEEPALIVE_INTERVAL unten.
CMD_HEATER_STEP = "heater%20step"
CMD_LOAD_SETPOINT = "load%20setpoint"
CMD_LOAD_FEEDIN = "load%20feedin"

# Parameterlose Befehle (kein ?value=), wirken wie der physische Taster am
# Gerät — kein 60s-Auto-Verfall, daher hier kein Keep-Alive nötig.
CMD_EMERGENCY_ON = "on"
CMD_EMERGENCY_OFF = "off"
PATH_EMERGENCY_MODE = "STATUS_FLAGS.EMERGENCY_MODE"

PATH_NUMBER_OF_STEPS = "ASKOHEAT_PLUS_INFO.NUMBER_OF_STEPS"
PATH_MAX_POWER = "ASKOHEAT_PLUS_INFO.MAX_POWER"

# Fallback-Grenzwerte, nur verwendet wenn der dynamische Pfad oben nicht verfügbar ist.
FALLBACK_MAX_HEATER_STEP = 19  # dokumentiertes Maximum für Booster-Modelle
FALLBACK_MAX_LOAD_SETPOINT = 20000

# SET_LOAD_FEEDIN_INT16 im geräteeigenen JSON deutet auf int16-Speicherung hin.
LOAD_FEEDIN_MIN = -32768
LOAD_FEEDIN_MAX = 32767

# Das Gerät setzt einen geschriebenen Wert ~60s nach dem letzten Schreiben
# automatisch zurück, wenn ihn niemand erneut sendet. Number-Entities senden
# den letzten Wert in diesem Intervall (sicher unter 60s) erneut, solange er
# ungleich null ist. Deckt sich mit dem herstellerseitig dokumentierten
# Verhalten, dass ein steuerndes Gerät genau das tun soll — anders als bei
# der Lese-Abfrage sind regelmäßige erneute Sendungen hier unbedenklich.
NUMBER_KEEPALIVE_INTERVAL = 45
