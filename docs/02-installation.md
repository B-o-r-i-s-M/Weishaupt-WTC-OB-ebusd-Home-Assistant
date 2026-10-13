# 2. Installation Schritt für Schritt

Die Reihenfolge ist bewusst so gewählt: erst **parallel zum WCM-COM nur mitlesen**, dann aktiv lesen, und erst ganz am Ende das WCM-COM entfernen und das Schreiben freischalten. So kannst du jederzeit zurück.

## 1. Adapter ins WLAN bringen

1. Adapter per USB-C mit Strom versorgen. Er öffnet ein offenes WLAN **`EBUS`**.
2. Damit verbinden und **http://192.168.4.1** öffnen. Am Handy dafür die mobilen Daten ausschalten, sonst lädt die Seite oft nicht.
3. Unter *Configuration → WiFi station/client* dein WLAN eintragen (2,4 GHz genügt) und speichern.
4. Im Router eine **feste IP** für den Adapter reservieren und den Adapter neu starten.
5. Die Weboberfläche des Adapters jetzt unter seiner neuen IP öffnen und die **Firmware aktualisieren** (*Update Firmware → Update to latest*).
6. Auf der Statusseite steht der **ebusd device string**, z. B. `ens:192.168.x.y:9999`. Den brauchst du gleich.

## 2. Adapter an den Bus

Siehe [01-hardware.md → Anschluss](01-hardware.md#anschluss). Danach muss auf der Statusseite **„eBUS signal: acquired“** stehen.

## 3. ebusd in Home Assistant installieren

Voraussetzung: Die App **Mosquitto broker** und die **MQTT-Integration** sind eingerichtet.

1. *Einstellungen → Apps → App-Store → ⋮ → Repositories* → `https://github.com/LukasGrebe/ha-addons` hinzufügen.
2. App **eBUSd** installieren, aber **noch nicht starten**.
3. Unter *Konfiguration* (YAML-Modus über ⋮) eintragen:

   ```yaml
   seed_mqtt_cfg: true
   commandline_options:
     - --mqttjson
     - --device=ens:192.168.x.y:9999     # deine Adapter-IP
     - --readonly                        # Phase 1: nur mitlesen
     - --lograwdata
     - --configpath=/config
   ```

   `--configpath=/config` sorgt dafür, dass ebusd **nur unsere lokale CSV** lädt und keine Online-Konfiguration sucht (für Weishaupt gibt es dort keine). Im Container ist `/config` der Ordner `addon_configs/<id>_ebusd` deines HA.

4. [`ebusd/weishaupt-wtc.csv`](../ebusd/weishaupt-wtc.csv) in den Ordner **`addon_configs/<id>_ebusd/`** kopieren, z. B. über die Samba-App (Freigabe `addon_configs`) oder den File Editor. Neben der CSV liegt dort nach dem ersten Start auch `mqtt-hassio.cfg`.
5. App starten. Im Protokoll sollte stehen:

   ```
   bus started with own address 31/36
   found messages: 458 (0 conditional on 0 conditions, 35 poll, 1 update)
   received update-read regler Betriebsdaten: ...
   ```

   Mit `--readonly` erscheinen bei den Abfragen Meldungen wie `push poll message: ERR`. Das ist in dieser Phase normal.

## 4. Aktiv lesen

1. In der Konfiguration `--readonly` entfernen und zusätzlich **`--pollinterval=1`** eintragen. Damit fragt ebusd jede Sekunde einen Wert ab, und die Flamme wird etwa alle 8 s aktualisiert. Das ist immer noch weniger Busverkehr als beim WCM-COM.
2. App neu starten. Jetzt erscheinen Zeilen wie

   ```
   sent poll-read wtc Vorlauftemp QQ=31: 23.0
   sent poll-read hk1 Steilheit QQ=31: 8.0
   ```

3. Vergleiche die Werte mit dem WCM-COM bzw. dem Display. Einzelne `read timeout` sind bei WLAN normal, der nächste Zyklus holt den Wert nach.

## 5. WCM-COM entfernen und Schreiben freischalten

Der WCM-FS übernimmt Parameteränderungen **nur vom Absender `ff`**, also der Adresse, die auch das WCM-COM benutzt. Zwei Teilnehmer mit derselben Adresse stören sich. Deshalb:

1. **WCM-COM vom Bus abklemmen** (Strom aus).
2. Auf der Statusseite des Adapters prüfen, ob „eBUS signal“ weiter **acquired** ist. Im ebusd-Protokoll sollten die Teilnehmer `30`, `f1` und `07` weiter senden.
3. In der ebusd-Konfiguration **`--address=ff`** ergänzen und neu starten. Im Protokoll steht dann `bus started with own address ff/04`.
4. Schreibtest über MQTT (z. B. *Entwicklerwerkzeuge → Aktionen → `mqtt.publish`*), mit einem Parameter, der nichts bewirkt, etwa der Absenk-Raumtemperatur, wenn du keinen Absenkbetrieb nutzt:

   ```yaml
   action: mqtt.publish
   data:
     topic: ebusd/hk1/SetRaumsollAbsenk_185/set
     payload: ""
   ```

   Danach `ebusd/hk1/RaumsollAbsenk/get` publizieren. Im Protokoll muss `sent poll-read hk1 RaumsollAbsenk QQ=ff: 18.5` erscheinen. Anschließend mit `SetRaumsollAbsenk_<dein alter Wert × 10>` zurückstellen.

> ⚠️ Ab jetzt gilt: `--address=ff` bleibt gesetzt, und das WCM-COM darf **nicht wieder** an den Bus.

Fertige Konfiguration der App:

```yaml
seed_mqtt_cfg: true
commandline_options:
  - --mqttjson
  - --device=ens:192.168.x.y:9999
  - --lograwdata          # optional, für Fehlersuche
  - --configpath=/config
  - --pollinterval=1
  - --address=ff
```

## 6. Home Assistant

Weiter mit [04-home-assistant.md](04-home-assistant.md).

## Anpassen

Andere Wertebereiche, weitere Parameter oder Prioritäten änderst du in [`tools/generate_csv.py`](../tools/generate_csv.py). Danach

```bash
python3 tools/generate_csv.py > ebusd/weishaupt-wtc.csv
```

ausführen, die CSV neu kopieren und ebusd neu starten.
