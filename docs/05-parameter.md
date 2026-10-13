# 5. Bekannte Parameter (InfoNr)

„ebusd-Name“ ist der Name in der CSV, das MQTT-Topic lautet `ebusd/<circuit>/<Name>`.

## Kessel (Slave `08`, circuit `wtc`)

| InfoNr | hex | ebusd-Name | Bedeutung | Format | Anzeige am Kessel |
|---|---|---|---|---|---|
| 1 | 0001 | Stoerung | Fehlercode, 0 = keine Störung | UIN | |
| 2 | 0002 | Waermeanforderung | Wärmeanforderung / Kesselsollwert | SIN ÷10 °C | |
| 12 | 000C | Aussentemp | Außentemperatur | SIN ÷10 °C | i33 |
| 13 | 000D | Kesseltemp | Kesseltemperatur (Startseite WCM-COM) | SIN ÷10 °C | |
| 14 | 000E | Warmwassertemp | Warmwassertemperatur | SIN ÷10 °C | i34 |
| 81 | 0051 | Flamme | Flammensignal | 0/1 | |
| 82 | 0052 | BetriebsartHeizung | Betriebsart Heizung aktiv | 0/1 | |
| 83 | 0053 | BetriebsartWarmwasser | Betriebsart Warmwasser aktiv | 0/1 | |
| 103 | 0067 | Betriebsart | Betriebsart als Code | UIN | |
| 138 | 008A | Ladezustand | Ladezustand (bei uns n/v) | UIN | |
| 325 | 0145 | Abgastemp | Abgastemperatur | SIN ÷10 °C | |
| 373 | 0175 | Betriebsphase | Betriebsphase 0–9 (siehe unten) | UIN | i10 |
| 374 | 0176 | Betriebszustand | (bei uns n/v) | UIN | |
| 466 | 01D2 | Pumpe | Kesselpumpe | 0/1 | |
| 700 | 02BC | ZeitSeitWartung | Zeit seit letzter Wartung | UIN | |
| 1497 | 05D9 | Magnetventil1 | Brennerstufe 1 | 0/1 | |
| 1498 | 05DA | Magnetventil2 | Brennerstufe 2 | 0/1 | |
| 2572 | 0A0C | AussentempGedaempft | gedämpfte Außentemperatur | SIN ÷10 °C | |
| 3101 | 0C1D | Vorlauftemp | Vorlauftemperatur (eSTB) | SIN ÷10 °C | i30 |
| 3196 / 3197 | 0C7C / 0C7D | BrennerstartsRest / -Tausender | Brennerstarts = T × 1000 + R | UIN | |
| 3198 / 3199 | 0C7E / 0C7F | BetriebsstundenRest / -Tausender | Betriebsstunden = T × 1000 + R | UIN | |
| 3792 / 3793 | 0ED0 / 0ED1 | OelzaehlerTausender / -Rest | Ölzähler in Litern = T × 1000 + R | UIN | |
| 4176 | 1050 | Laststellung | Laststellung | UIN ÷10 kW | i11 |

**Betriebsphase (i10):** 0 Bereitschaft, 1 Ruhestandskontrolle, 2 Ölvorwärmung, 3 Vorbelüftung, 4 Sicherheitszeit, 5 Nachzündung, 6 Flammenstabilisierung, 7 Reglerfreigabe, 8 Nachbelüftung, 9 Zwangsbelüftung.

**Ölzähler:** Der Kessel berechnet ihn aus den Laufzeiten von Stufe 1 und Stufe 2 und den eingestellten Brennerleistungen (P36/P37). Er ist also nur so genau wie diese Einstellungen.

## Heizkreis 1 (WCM-FS, Lesen über Slave `35`, Schreiben über Master `30`, circuit `hk1`)

| WCM-COM | InfoNr | hex | ebusd-Name | Bedeutung | Bereich in der CSV |
|---|---|---|---|---|---|
| 112 | 5 | 0005 | Raumsoll | Normal-Raumtemperatur | 10–30 °C / 0,5 |
| 113 | 8 | 0008 | RaumsollAbsenk | Absenk-Raumtemperatur | 10–30 °C / 0,5 |
| 117 | 270 | 010E | Steilheit | Heizkurve Steilheit | 2,5–40 / 0,5 |
| 118 | 2580 | 0A14 | Raumfrosttemp | Raumfrosttemperatur | 0–15 °C / 0,5 |
| 119 | 278 | 0116 | SoWiUmschalt | Sommer/Winter-Umschalttemperatur | 5–30 °C / 0,5 |
| 132 | 19 | 0013 | WWSollNormal | Warmwasser-Soll normal | 30–65 °C / 0,5 |
| 133 | 650 | 028A | WWSollAbsenk | Warmwasser-Soll abgesenkt | 10–65 °C / 0,5 |
| – | 2 | 0002 | Vorlaufsoll | Vorlauf-Sollwert Heizkreis (nur lesen) | |
| 111? | 274 | 0112 | Betriebsart | Betriebsart HK als Code (nicht entschlüsselt, nur lesen) | |

Alle Werte sind SIN ÷ 10. Die Bereiche sind bewusst großzügig gewählt. Ob der WCM-FS selbst engere Grenzen hat, ist nicht geprüft. Nach dem Schreiben immer nachlesen, das Package macht das automatisch.

## Weitere Parameter finden

1. WCM-COM (noch) am Bus lassen, ebusd mit `--readonly --lograwdata` laufen lassen.
2. In der WCM-COM-Weboberfläche die gewünschte Seite öffnen bzw. einen Wert übernehmen und die Uhrzeit notieren.
3. Im ebusd-Protokoll nach `ff 08 50 22` / `ff 35 50 22` bzw. `ff 30 50 23` zu dieser Zeit suchen. Die Bytes 2–3 nach dem Prüfbyte sind die InfoNr.
4. Den Parameter in `tools/generate_csv.py` ergänzen und die CSV neu erzeugen.

Neue Funde bitte als Issue oder Pull Request beisteuern.
