# 1. Hardware

## Was du brauchst

| Teil | Zweck | Hinweis |
|---|---|---|
| **eBUS-Adapter** mit ebusd-Unterstützung (*enhanced protocol*) | Verbindung zum eBUS | Getestet: **eBUS Adapter Shield C5** (ESP32-C5, WLAN, ca. 34 $). Ebenso geeignet: Shield C6, Stick C6, Shield v5. Bezug z. B. über Elecrow, Doku auf adapter.ebusd.eu |
| USB-C-Netzteil 5 V, ≥ 0,5 A | Versorgung des Adapters | Der Adapter zieht **keinen** Strom aus dem eBUS (galvanisch getrennt). Ein normales Handy-Netzteil reicht. |
| 2-adrige Leitung | Verbindung zu den eBUS-Klemmen | Kleinspannung, z. B. J-Y(St)Y 2×2×0,8 oder Klingeldraht. Der Stecker liegt dem Adapter bei. |
| Home Assistant (HA OS oder Supervised) | ebusd-App, MQTT, Automationen | Für andere Installationen läuft ebusd auch als Docker-Container. |
| MQTT-Broker | Datenaustausch ebusd ↔ HA | z. B. die App *Mosquitto broker* |
| *optional:* Gehäuse, Hutschienenhalter | saubere Montage im Heizungsraum | Für den Shield v5/C6 gibt es druckbare Gehäuse (Printables). |

Ein Raspberry Pi ist **nicht** nötig. Der Adapter spricht per WLAN (oder optional Ethernet) direkt mit ebusd.

## Voraussetzungen an der Heizung

- Weishaupt **WTC-OB** (Öl-Brennwert) mit eBUS-Regelung.
- Fernbedienung bzw. Heizkreisregler **WCM-FS** am eBUS. In dieser Konfiguration ist der WCM-FS der Regler des Heizkreises (Adresse 30/35) und führt die aktive Heizkurve. Die Kessel-Parameter (z. B. P22) wirken dann nicht.
- Bisher meist ein **WCM-COM** am Bus. Das wird durch den Adapter ersetzt und am Ende abgeklemmt.

Andere WTC-Varianten (WTC-GW Gas) verwenden sehr wahrscheinlich dasselbe Protokoll, sind aber nicht getestet. Siehe [Mitmachen](../README.md#mitmachen).

## Der eBUS in Kürze

- 2-Draht-Bus, **Polarität egal** (der Adapter ist verpolungssicher).
- Gleichspannung im Kleinspannungsbereich: Ruhepegel **ca. 15–24 V** (typisch um 20 V), Datenbit 0 bei ca. 9–12 V, 2400 Baud. Mit dem Multimeter (DC) misst du an den Klemmen ca. 18–22 V.
- Die Busspannung wird von der Anlage geliefert, **nicht vom WCM-COM**: Nach dem Abklemmen des WCM-COM läuft der Bus unverändert weiter.

## Anschluss

1. **Heizung stromlos machen** (Heizungsnotschalter) und gegen Wiedereinschalten sichern.
2. Die eBUS-Klemmen suchen, an denen WCM-FS und WCM-COM angeschlossen sind. Die Lage steht in der Montageanleitung von Kessel bzw. WCM.
3. Die beiden Adern des Adapters **parallel** auf diese Klemmen legen. Während der Einrichtungsphase dürfen WCM-COM und Adapter gleichzeitig am Bus hängen.
4. Adapter mit dem USB-Netzteil versorgen und Heizung wieder einschalten.
5. Auf der Statusseite des Adapters muss jetzt **„eBUS signal: acquired“** stehen.

## WLAN-Empfang

eBUS über WLAN funktioniert gut, ist aber latenzempfindlich. Auf der Statusseite des Adapters wird der Pegel angezeigt:

| Pegel | Bewertung |
|---|---|
| besser als −65 dBm | sehr gut |
| −65 … −75 dBm | meist problemlos, gelegentlich einzelne Timeouts |
| schlechter als −75 dBm | AP näher bringen, in der Router-Software „an AP binden“ oder Ethernet-Modul verwenden |

Die Sendeleistung des Adapters steht ab Werk auf Maximum (20 dBm). Einen festen WLAN-Kanal im Adapter einzustellen bringt nichts und führt zu Abbrüchen, wenn der Router den Kanal wechselt.

**Empfehlung:** dem Adapter eine feste IP per DHCP-Reservierung geben, gern in einem eigenen IoT-Netz. ebusd baut die Verbindung zum Adapter auf, nicht umgekehrt. Home Assistant braucht also TCP-Zugriff auf Port 9999 des Adapters.
