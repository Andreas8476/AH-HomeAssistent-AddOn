# 12 — Using the add-on

*[Deutsche Version](../de/12_bedienung.md) (primary, authoritative)*

A short guided tour with screenshots through the four places you'll deal
with day to day: the dashboard, the device page, reconfiguration, and the
built-in feed-in/load-setpoint linking.

## Dashboard

![Dashboard](../../product_pics/HA_AH_Ausschnitt_Dashboard.png)

The automatically generated dashboard view (see
[11_dashboard.md](11_dashboard.md)) — one view per device, reached via the
heating-element icon in the sidebar. Left: the fallback table with all
values. Middle: the heating-element and meter-cabinet images with live
values as overlays. Right: the two history graphs (temperature, heater
load).

## Device page (controls & sensors)

![Device page](../../product_pics/HA_AH_Ausschnitt_Einstellungen.png)

The device page Home Assistant generates automatically — reached via
**Settings → Devices & services → ASKOHEAT+**, then click the device name
(e.g. "SONNENBOOSTER 5,2 kW"). Home Assistant groups the entities by domain
on its own: the "Steuerung" (controls) card shows the writable `number`
entities (feed-in value, load setpoint, target heater step) and the
emergency-mode switch; the "Sensoren" card shows the read-only values
(device status, heater load, heater step, pump, ...). No custom UI from
this integration — plain stock Home Assistant behavior.

## Reconfigure (change host/port/polling interval)

![Reconfigure](../../product_pics/HA_AH_Neu-Konfiguration.png)

Via **Settings → Devices & services → ASKOHEAT+** → the **⋮** menu on the
relevant device → **Reconfigure**. Host/IP address, port and polling
interval can be changed here any time without re-adding the device (see
also [04_installation.md](04_installation.md)).

## Links (auto-fill feed-in value/load setpoint)

![Links](../../product_pics/HA_AH_Verbindungen.png)

Via **Settings → Devices & services → ASKOHEAT+** → the **⚙** icon
("Configure") on the relevant device. Here the feed-in value and/or load
setpoint can be linked directly to any other entity (e.g. a meter/inverter
sensor) — pick the entity, confirm with OK, done. Leave empty for purely
manual control. Details/how it works: [10_automation.md](10_automation.md).
