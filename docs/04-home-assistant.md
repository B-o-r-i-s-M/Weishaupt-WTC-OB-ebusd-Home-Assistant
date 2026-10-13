# 4. Home Assistant

## Packages einbinden

In `configuration.yaml` (falls noch nicht vorhanden):

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Dann beide Dateien nach `<config>/packages/` kopieren:

| Datei | Inhalt |
|---|---|
| [`weishaupt.yaml`](../homeassistant/packages/weishaupt.yaml) | MQTT-Sensoren für alle Werte, Zähler aus Tausender + Rest, Verbrauchszähler Öl/Starts (Tag/Monat/Jahr), Laufzeiten Brenner/Heizung/Warmwasser/Stufe 1/Stufe 2, Laufzeit pro Start, Dauer des letzten Brennerlaufs, Klartext-Betriebsart und -phase, Anzeige-Sensoren „X h YY min“ |
| [`weishaupt_parameter.yaml`](../homeassistant/packages/weishaupt_parameter.yaml) | Schieberegler (`input_number.weishaupt_set_*`) für die Heizkreis-Parameter und zwei Automationen: *Schreiben* (Regler → eBUS → nachlesen) und *Synchronisieren* (Wert am WCM-FS geändert → Regler folgt) |

Danach *Entwicklerwerkzeuge → YAML → Konfiguration prüfen* und neu starten (oder MQTT, Template, Input Number und Automationen neu laden).

Benötigt **Home Assistant 2025.10 oder neuer**, wegen `default_entity_id` und der neuen Trigger-Syntax.

## Wichtige Entitäten

| Entität | Bedeutung |
|---|---|
| `binary_sensor.weishaupt_flamme` | Flamme an/aus, Grundlage aller Laufzeiten |
| `binary_sensor.weishaupt_magnetventil_2` | Stufe 2 aktiv |
| `binary_sensor.weishaupt_heizung` / `_warmwasser` | aktive Betriebsart (Dreiwegeventil) |
| `sensor.weishaupt_betriebsart` | Klartext, z. B. „Heizung, Stufe 1“ oder „Brenner aus“ |
| `sensor.weishaupt_betriebsphase_text` | Klartext der Betriebsphase i10 |
| `sensor.weishaupt_vorlauftemperatur`, `_warmwassertemperatur`, `_aussentemperatur`, `_warmeanforderung` | Temperaturen |
| `sensor.weishaupt_olzahler`, `_betriebsstunden_brenner`, `_brennerstarts` | Gerätezähler (`total_increasing`) |
| `sensor.weishaupt_oel_tag` / `_monat` / `_jahr` | Ölverbrauch über Utility Meter |
| `sensor.weishaupt_laufzeit_brenner_heute` usw. | Laufzeiten über History Stats |
| `sensor.weishaupt_hk1_*` | gelesene Heizkreis-Parameter |
| `input_number.weishaupt_set_*` | Regler zum Ändern |

## Wie das Schreiben funktioniert

1. Du verstellst z. B. `input_number.weishaupt_set_raumsoll` auf 21,5.
2. Die Automation *Weishaupt HK1 Parameter schreiben* publiziert `ebusd/hk1/SetRaumsoll_215/set`.
3. ebusd sendet das fertige Telegramm aus der CSV an den WCM-FS.
4. Nach 3 s wird `ebusd/hk1/Raumsoll/get` angefordert, nach weiteren 5 s wird der Regler auf den **gelesenen** Wert gesetzt. Springt er zurück, wurde die Änderung nicht übernommen. Häufigste Ursache: ebusd läuft nicht mit `--address=ff`.

Die Automation reagiert nur auf Änderungen durch einen Benutzer (`context.user_id`), nicht auf ihre eigene Rück-Synchronisierung.

## Zähler und Übertrag

Ölzähler, Betriebsstunden und Brennerstarts liefert der Kessel in zwei Teilen (Tausender und Rest), die ebusd nacheinander liest. Beim Übertrag (z. B. 19 999 → 20 000) kann kurz ein Teil alt und der andere neu sein. Die Template-Sensoren korrigieren Sprünge über 500 deshalb um ±1000, damit Utility Meter und Statistik keinen falschen Reset sehen.

## Dashboard

[`homeassistant/dashboard/ebus-view.yaml`](../homeassistant/dashboard/ebus-view.yaml) ist eine Ansicht, die die Weboberfläche des WCM-COM ersetzt: Prozesswerte des Brenners, Temperaturen, Zähler und die Heizkreis-Parameter zum Ändern. Sie nutzt nur Standardkarten.

Einfügen: *Dashboard bearbeiten → Ansicht hinzufügen → ⋮ → In YAML bearbeiten* → Inhalt der Datei einfügen.

Die Entitäten `binary_sensor.heating_ebusd_global_signal` und `…_running` legt ebusd selbst per MQTT-Discovery an. Je nach Einstellungen in `mqtt-hassio.cfg` können sie bei dir anders heißen.

## Umstieg von einer REST-Abfrage des WCM-COM

Wer, wie ich vorher, das WCM-COM per REST-Sensor abgefragt hat und dieselben Entitäts-IDs behalten möchte, damit Verlauf, Langzeitstatistik und Dashboards weiterlaufen:

1. Die REST-Sensoren, den Abfrage-Schalter und die Abfrage-Automation aus dem alten Package entfernen und neu laden.
2. Die nun verwaisten Entitäten unter *Einstellungen → Entitäten* löschen. Der Verlauf in der Datenbank bleibt erhalten.
3. Dann die neuen Packages einspielen. Über `default_entity_id` übernehmen die MQTT-Sensoren die alten IDs.

Wird Schritt 2 ausgelassen, bekommen die neuen Sensoren IDs mit der Endung `_2`.
