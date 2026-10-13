#!/usr/bin/env python3
"""
Erzeugt die ebusd-Definitionsdatei fuer Weishaupt WTC-OB mit WCM-FS (Heizkreis 1).

Hintergrund (Details in docs/03-protokoll.md):
  Weishaupt verwendet die herstellerspezifischen eBUS-Dienste
    50 22  Parameter lesen   (Master -> Slave, Antwort 2 Byte little endian)
    50 23  Parameter schreiben (Master -> Master, ohne Antwort)
  Das erste Datenbyte ist ein Pruefbyte ("Kennbyte"), das von allen folgenden Bytes
  abhaengt. ebusd kann es nicht selbst berechnen, deshalb erzeugt dieses Skript
  fuer jede Abfrage und fuer jeden einstellbaren Wert ein fertiges Telegramm.

Aufruf:
  python3 tools/generate_csv.py > ebusd/weishaupt-wtc.csv

Bereiche, Schritte und Abfrage-Prioritaeten lassen sich unten anpassen.
"""

import sys


# ---------------------------------------------------------------------------
# Pruefbyte
# ---------------------------------------------------------------------------
def _crc_step(c: int) -> int:
    """Ein CRC8-Schritt (8 Bit) mit Polynom 0x5C, nicht reflektiert."""
    for _ in range(8):
        c = ((c << 1) ^ 0x5C) & 0xFF if c & 0x80 else (c << 1) & 0xFF
    return c


def weishaupt_check(data: list[int]) -> int:
    """
    Pruefbyte fuer die Nutzdaten eines 50 22 / 50 23 Telegramms.
    Alle Bytes ausser dem letzten laufen durch CRC8 (Poly 0x5C, Startwert 0),
    das letzte Byte wird nur noch per XOR verknuepft.
    """
    c = 0
    for b in data[:-1]:
        c = _crc_step(c ^ b)
    return c ^ data[-1]


def le16(v: int) -> list[int]:
    v &= 0xFFFF
    return [v & 0xFF, v >> 8]


def hexs(bs: list[int]) -> str:
    return "".join(f"{b:02x}" for b in bs)


def read_id(infonr: int) -> str:
    d = le16(infonr)
    return hexs([weishaupt_check(d)] + d)


WRITE_TAIL = [0x5D, 0x01, 0x00, 0x00]  # konstant bei allen Schreibtelegrammen des WCM-COM, Bedeutung unbekannt


def write_id(infonr: int, raw: int) -> str:
    d = le16(infonr) + le16(raw) + WRITE_TAIL
    return hexs([weishaupt_check(d)] + d)


# Selbsttest gegen aufgezeichnete Original-Telegramme des WCM-COM
assert read_id(3101) == "941d0c"        # ff 08 50 22 03 94 1d 0c  (Vorlauf)
assert read_id(81) == "945100"          # Flamme
assert read_id(5) == "700500"           # Normal-Raumtemperatur HK1
assert write_id(8, 185) == "d80800b9005d010000"   # Absenk-Raumtemp. 18,5 °C
assert write_id(8, 180) == "1c0800b4005d010000"   # Absenk-Raumtemp. 18,0 °C
assert write_id(5, 210) == "600500d2005d010000"   # Normal-Raumtemp. 21,0 °C


# ---------------------------------------------------------------------------
# Definitionen
# ---------------------------------------------------------------------------
# Kessel / Feuerungsautomat (eBUS-Slave 08)
# (Prioritaet, Name, InfoNr, Datentyp, Teiler, Einheit, Kommentar)
KESSEL = [
    (1, "Flamme", 81, "UIN", "", "", "Flammensignal 0/1"),
    (1, "Magnetventil1", 1497, "UIN", "", "", "Brennerstufe 1 0/1"),
    (1, "Magnetventil2", 1498, "UIN", "", "", "Brennerstufe 2 0/1"),
    (1, "Pumpe", 466, "UIN", "", "", "Kesselpumpe 0/1"),
    (1, "BetriebsartHeizung", 82, "UIN", "", "", "Betriebsart Heizung 0/1"),
    (1, "BetriebsartWarmwasser", 83, "UIN", "", "", "Betriebsart Warmwasser 0/1"),
    (1, "Betriebsphase", 373, "UIN", "", "", "Betriebsphase i10 (0-9)"),
    (1, "Laststellung", 4176, "UIN", "10", "kW", "Laststellung i11"),
    (1, "Vorlauftemp", 3101, "SIN", "10", "°C", "Vorlauftemperatur i30 (eSTB)"),
    (2, "Waermeanforderung", 2, "SIN", "10", "°C", "Waermeanforderung / Kesselsollwert"),
    (2, "Kesseltemp", 13, "SIN", "10", "°C", "Kesseltemperatur"),
    (2, "Warmwassertemp", 14, "SIN", "10", "°C", "Warmwassertemperatur i34"),
    (2, "Abgastemp", 325, "SIN", "10", "°C", "Abgastemperatur"),
    (2, "Stoerung", 1, "UIN", "", "", "Fehlercode (0 = keine Stoerung)"),
    (2, "Betriebszustand", 374, "UIN", "", "", "Betriebszustand (32768 = n/v)"),
    (3, "Aussentemp", 12, "SIN", "10", "°C", "Aussentemperatur i33"),
    (3, "AussentempGedaempft", 2572, "SIN", "10", "°C", "gedaempfte Aussentemperatur"),
    (5, "Betriebsart", 103, "UIN", "", "", "Betriebsart (Code)"),
    (5, "Ladezustand", 138, "UIN", "", "", "Ladezustand (32768 = n/v)"),
    (5, "ZeitSeitWartung", 700, "UIN", "", "", "Zeit seit letzter Wartung"),
    (5, "BrennerstartsRest", 3196, "UIN", "", "", "Brennerstarts Rest (< 1000)"),
    (5, "BrennerstartsTausender", 3197, "UIN", "", "", "Brennerstarts Tausender"),
    (5, "BetriebsstundenRest", 3198, "UIN", "", "", "Betriebsstunden Brenner Rest (< 1000)"),
    (5, "BetriebsstundenTausender", 3199, "UIN", "", "", "Betriebsstunden Brenner Tausender"),
    (5, "OelzaehlerTausender", 3792, "UIN", "", "", "Oelzaehler Tausender Liter"),
    (5, "OelzaehlerRest", 3793, "UIN", "", "", "Oelzaehler Rest Liter (< 1000)"),
]

# Heizkreis 1 / WCM-FS (Lesen: Slave 35, Schreiben: Master 30)
# (Name, InfoNr, WCM-COM-Nummer, Beschreibung, min, max, Schritt)  -> SIN /10 °C bzw. ohne Einheit
HK1_PARAMETER = [
    ("Raumsoll", 5, 112, "Normal-Raumtemperatur", 10.0, 30.0, 0.5, "°C"),
    ("RaumsollAbsenk", 8, 113, "Absenk-Raumtemperatur", 10.0, 30.0, 0.5, "°C"),
    ("Steilheit", 270, 117, "Heizkurve Steilheit", 2.5, 40.0, 0.5, ""),
    ("Raumfrosttemp", 2580, 118, "Raumfrosttemperatur", 0.0, 15.0, 0.5, "°C"),
    ("SoWiUmschalt", 278, 119, "Sommer/Winter-Umschalttemperatur", 5.0, 30.0, 0.5, "°C"),
    ("WWSollNormal", 19, 132, "Warmwasser-Soll normal", 30.0, 65.0, 0.5, "°C"),
    ("WWSollAbsenk", 650, 133, "Warmwasser-Soll abgesenkt", 10.0, 65.0, 0.5, "°C"),
]
HK1_NUR_LESEN = [
    ("Vorlaufsoll", 2, "SIN", "10", "°C", "Vorlauf-Sollwert Heizkreis"),
    ("Betriebsart", 274, "UIN", "", "", "Betriebsart Heizkreis (Code noch nicht entschluesselt)"),
]


def main(out=sys.stdout) -> None:
    w = out.write
    w("# ebusd-Definitionen Weishaupt WTC-OB mit WCM-FS (Heizkreis 1)\n")
    w("# Erzeugt mit tools/generate_csv.py - Aenderungen bitte dort vornehmen.\n")
    w("# Projekt: https://github.com/B-o-r-i-s-M/Weishaupt-WTC-OB-ebusd-Home-Assistant\n")
    w("# Voraussetzung fuer das Schreiben: ebusd laeuft mit --address=ff und das WCM-COM ist vom Bus getrennt.\n")
    w("# 32768 (0x8000) bedeutet 'Wert nicht verfuegbar'.\n")
    w("# type,circuit,name,comment,QQ,ZZ,PBSB,ID,field,part,datatype,divider/values,unit,comment\n")
    w("#\n# --- Kessel / Feuerungsautomat (Slave 08), Lesen mit 50 22 ---\n")
    for prio, name, nr, typ, div, unit, com in KESSEL:
        w(f"r{prio},wtc,{name},{com} (InfoNr {nr}),,08,5022,{read_id(nr)},,s,{typ},{div},{unit},\n")

    w("#\n# --- Heizkreis 1 / WCM-FS (Slave 35), Lesen mit 50 22 ---\n")
    for name, nr, wcm, desc, lo, hi, step, unit in HK1_PARAMETER:
        w(f"r5,hk1,{name},{desc} [{wcm}] (InfoNr {nr}),,35,5022,{read_id(nr)},,s,SIN,10,{unit},\n")
    for name, nr, typ, div, unit, com in HK1_NUR_LESEN:
        w(f"r5,hk1,{name},{com} (InfoNr {nr}),,35,5022,{read_id(nr)},,s,{typ},{div},{unit},\n")

    w("#\n# --- Broadcast WCM-FS (30) an Feuerungsautomat (f1): genormter Dienst 05 07 ---\n")
    w("u,regler,Betriebsdaten,Regler an Feuerungsautomat (05 07),30,f1,0507,,"
      "Zustand,,UCH,,,,Aktion,,UCH,,,,Kesselsollwert,,D2C,,°C,,Kesseldruck,,D2C,,bar,,"
      "Stellgrad,,UCH,,%,,WWSollwert,,D1C,,°C,,Brennstoff,,UCH,,,\n")

    w("#\n# --- Schreiben Heizkreis 1: Dienst 50 23 an WCM-FS-Master 30 ---\n")
    w("# Ein Telegramm je Wert, weil das Pruefbyte vom Wert abhaengt.\n")
    w("# MQTT: publish auf ebusd/hk1/Set<Name>_<Wert*10>/set (leerer Payload), z. B. ebusd/hk1/SetRaumsoll_215/set\n")
    for name, nr, wcm, desc, lo, hi, step, unit in HK1_PARAMETER:
        n = int(round((hi - lo) / step))
        for i in range(n + 1):
            v = lo + i * step
            raw = int(round(v * 10))
            w(f"w,hk1,Set{name}_{raw},{desc} [{wcm}] auf {v:.1f} setzen,,30,5023,{write_id(nr, raw)},,,,,,\n")


if __name__ == "__main__":
    main()
