# 10 — Automatisierung: Einspeisewert mit Zähler/Wechselrichter verknüpfen

*[English version](../en/10_automation.md)*

## Hintergrund

Der klassische Anwendungsfall für ASKOHEAT+: PV-Überschuss automatisch
verheizen, statt ins Netz einzuspeisen. Dafür muss der **Einspeisewert**
(`number.load_feedin`) laufend den aktuellen Wert eines Netz-/
Wechselrichter-Leistungssensors widerspiegeln (negativ = Überschuss, positiv
= Bezug — siehe [02_api-referenz.md](02_api-referenz.md)).

Zwei Wege dafür: die **eingebaute Verknüpfung** direkt in den Integrations-
Einstellungen (empfohlen für den Standardfall), oder eine mitgelieferte
**Home-Assistant-Blueprint** für alle, die eigene Bedingungen/Filter
brauchen. Das eingebaute Keep-Alive (siehe
[02_api-referenz.md](02_api-referenz.md)) sorgt in beiden Fällen automatisch
dafür, dass der zuletzt übertragene Wert nicht wegen des 60s-Verfalls
verloren geht, auch wenn die Quelle mal länger nicht aktualisiert.

## Eingebaute Verknüpfung (empfohlen)

**Einstellungen → Geräte & Dienste → ASKOHEAT+** → beim jeweiligen Gerät
die drei Punkte (⋮) → **"Konfigurieren"** (Options-Flow, nicht zu
verwechseln mit "Neu konfigurieren" für Host/Port). Dort zwei optionale
Entity-Picker:

- **Einspeisewert automatisch aus:** Zähler-/Wechselrichter-Sensor mit der
  aktuellen Einspeise-/Bezugsleistung in Watt.
- **Leistungsvorgabe automatisch aus:** entsprechend für die Leistungsvorgabe.

Beide Felder leer lassen = keine Verknüpfung, weiterhin rein manuelle
Steuerung wie bisher. Sobald eine Entity ausgewählt ist, hält die
Integration den Zielwert automatisch synchron dazu (technisch über
denselben `number.set_value`-Service, den auch die UI und die Blueprint
unten nutzen — der Keep-Alive greift also identisch). Eine Änderung der
Auswahl lädt die Integration automatisch neu, kein manueller Neustart nötig.

## Alternative: eigene Automation (Blueprint)

Für alle, die zusätzliche Bedingungen/Filter brauchen (z.B. nur zwischen
bestimmten Uhrzeiten verknüpfen), steht weiterhin eine Blueprint zur
Verfügung — funktioniert unabhängig von der eingebauten Verknüpfung oben
(beide rufen denselben Service auf, es gibt keinen Sonderfall für
Kollisionen: wie bei zwei Automationen auf dieselbe Entity gewinnt schlicht
der letzte Schreibvorgang).

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
