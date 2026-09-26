# 10 — Automatisierung: Einspeisewert mit Zähler/Wechselrichter verknüpfen

*[English version](../en/10_automation.md)*

## Hintergrund

Der klassische Anwendungsfall für ASKOHEAT+: PV-Überschuss automatisch
verheizen, statt ins Netz einzuspeisen. Dafür muss der **Einspeisewert**
(`number.load_feedin`) laufend den aktuellen Wert eines Netz-/
Wechselrichter-Leistungssensors widerspiegeln (negativ = Überschuss, positiv
= Bezug — siehe [02_api-referenz.md](02_api-referenz.md)).

Diese Integration bildet die eigentliche **Verknüpfung** bewusst **nicht**
als fest verdrahtete Config-Option ab, sondern über eine mitgelieferte
**Home-Assistant-Blueprint** — flexibler (eigene Bedingungen/Filter möglich)
und ohne zusätzlichen Setup-Schritt in der Integration selbst. Das eingebaute
Keep-Alive (siehe [02_api-referenz.md](02_api-referenz.md)) sorgt danach
automatisch dafür, dass der zuletzt übertragene Wert nicht wegen des
60s-Verfalls verloren geht, auch wenn der Zähler mal länger nicht aktualisiert.

## Blueprint importieren

Datei im Repo: [`blueprints/askoheat_plus_feedin_from_meter.yaml`](../../../../blueprints/askoheat_plus_feedin_from_meter.yaml).

1. In Home Assistant: **Einstellungen → Automatisierungen & Szenen →
   Blueprints → Blueprint importieren**.
2. URL der Rohdatei eintragen:
   `https://raw.githubusercontent.com/Andreas8476/AH-HomeAssistent-AddOn/main/blueprints/askoheat_plus_feedin_from_meter.yaml`
3. **Vorschau/Importieren**.
4. Unter **Automatisierungen** eine neue Automation aus der importierten
   Blueprint anlegen:
   - **Zähler-/Wechselrichter-Sensor:** dein Sensor mit der aktuellen
     Einspeise-/Bezugsleistung in Watt (z.B. aus der Solar-Manager-Pipeline).
   - **ASKOHEAT+ Einspeisewert-Entity:** die `number.load_feedin`-Entity
     deines ASKOHEAT+-Geräts.
5. Speichern.

## Was die Blueprint macht

- **Trigger:** Zustandsänderung des gewählten Zähler-/Wechselrichter-Sensors.
- **Bedingung:** Sensorwert ist nicht `unknown`/`unavailable`.
- **Aktion:** `number.set_value` auf die ASKOHEAT+-Einspeisewert-Entity mit
  dem (gerundeten) Sensorwert.

Keine eigene Wiederholungslogik in der Blueprint — das erledigt das
Keep-Alive der Integration bereits (alle 45s, solange der Wert `≠ 0` ist).

## Hinweise

- Vorzeichen prüfen: manche Zähler/Wechselrichter liefern Einspeisung als
  positiven Wert — dann vor dem Verknüpfen ggf. einen Hilfs-Sensor mit
  invertiertem Vorzeichen anlegen (Template-Sensor), da ASKOHEAT+ negativ =
  Überschuss erwartet.
- Die Blueprint setzt keine Ober-/Untergrenzen über den in
  [02_api-referenz.md](02_api-referenz.md) dokumentierten int16-Bereich
  (`-32768`–`32767`) hinaus — `number.set_value` lehnt Werte außerhalb des in
  `number.py` definierten Bereichs automatisch ab.
- Reine Kür, nicht Voraussetzung: Wer die Verknüpfung lieber selbst als
  Automation bauen möchte (z.B. mit zusätzlichen Bedingungen), kann das
  jederzeit auch ohne diese Blueprint tun — `number.load_feedin` ist eine
  ganz normale, per `number.set_value` ansteuerbare Entity.
