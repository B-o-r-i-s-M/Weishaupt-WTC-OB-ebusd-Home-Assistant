# 3. Das Weishaupt-eBUS-Protokoll

Ermittelt durch Mitschnitt des Busverkehrs zwischen WCM-COM, WCM-FS und Kessel (WTC-OB 18-B, WCM-FS 327.30) und durch Vergleich mit den Werten der WCM-COM-Weboberfläche. Alle Angaben in hex.

## Teilnehmer

| Master | Slave | Gerät | Bemerkung |
|---|---|---|---|
| `f1` | `f6`* | Feuerungsautomat / Kessel | sendet Broadcast `50 0A` |
| — | `08` | Kessel (Parameter-Slave) | beantwortet `50 22` |
| `30` | `35` | **WCM-FS** (Heizkreisregler, Fernbedienung) | Regler HK1, sendet `05 07`, nimmt `50 23` an |
| `07` | `0c` | weiteres Gerät der Anlage, vermutlich Bedienteil am Kessel | sendet `09 02` an `50`/`f6`; bleibt nach Entfernen des WCM-COM aktiv |
| `ff` | `04` | **WCM-COM**, später ebusd | |

\* Slave-Adresse = Master-Adresse + 5 (eBUS-Konvention).

## Dienst `50 22`: Parameter lesen

```
QQ ZZ 50 22 03  CK NL NH                → Antwort: 02 VL VH
```

| Feld | Bedeutung |
|---|---|
| `ZZ` | `08` = Kessel, `35` = Heizkreis 1 (WCM-FS) |
| `CK` | **Prüfbyte**, siehe unten |
| `NL NH` | Parameternummer („InfoNr“), little endian |
| `VL VH` | Wert, 16 Bit little endian. Temperaturen: vorzeichenbehaftet ÷ 10. `0x8000` = nicht verfügbar |

Beispiel: Vorlauftemperatur (InfoNr 3101 = `0x0C1D`)

```
ff 08 50 22 03  94 1d 0c        → 02 f0 00   = 0x00F0 = 240 → 24,0 °C
```

Die Parameternummern sind **dieselben wie in der `parameter.json` des WCM-COM** (`[Modul, Bus, 1, InfoNr, …]`), siehe [05-parameter.md](05-parameter.md).

## Dienst `50 23`: Parameter schreiben

```
ff 30 50 23 09  CK NL NH VL VH 5D 01 00 00        (kein Antworttelegramm, nur ACK)
```

- Geschrieben wird an den **Master `30`** des WCM-FS (Master-Master-Telegramm), gelesen dagegen vom Slave `35`.
- `5D 01 00 00` war bei allen beobachteten Schreibtelegrammen gleich. Die Bedeutung ist unbekannt, möglicherweise eine Sender- oder Berechtigungskennung. Das Telegramm funktioniert mit genau diesen Bytes.
- Das WCM-COM sendet beim „Übernehmen“ **alle Werte der Seite**, nicht nur den geänderten. Einzelne Telegramme genügen aber.
- ⚠️ **Der WCM-FS übernimmt den Wert nur, wenn der Absender `ff` ist.** Von `31` (ebusd-Standard) kommt zwar ein ACK, der Wert bleibt aber unverändert. Getestet am 13.10.2026.

Beispiel: Absenk-Raumtemperatur (InfoNr 8) auf 18,5 °C (Rohwert 185 = `0x00B9`)

```
ff 30 50 23 09  d8 08 00 b9 00 5d 01 00 00
```

## Das Prüfbyte

Das erste Datenbyte `CK` hängt von **allen folgenden Datenbytes** ab. Es ist eine CRC8 mit Polynom `0x5C` (Startwert 0, nicht reflektiert), wobei das **letzte Byte nicht mehr durch die CRC-Schleife läuft, sondern nur per XOR verknüpft** wird:

```python
def check(data):            # data = alle Bytes nach CK
    c = 0
    for b in data[:-1]:
        c ^= b
        for _ in range(8):
            c = ((c << 1) ^ 0x5C) & 0xFF if c & 0x80 else (c << 1) & 0xFF
    return c ^ data[-1]
```

Für das Lesen ist `data = [NL, NH]`, für das Schreiben `data = [NL, NH, VL, VH, 0x5D, 0x01, 0x00, 0x00]`.

Geprüft gegen alle 38 aufgezeichneten Lese- und 10 Schreibtelegramme des WCM-COM sowie gegen gezielte Abfragen der InfoNr 1, 2, 4, 8, 16 … 32768 (Bit-für-Bit).

Kontrollwerte:

| Daten | CK |
|---|---|
| `1d 0c` (InfoNr 3101) | `94` |
| `51 00` (InfoNr 81) | `94` |
| `05 00` (InfoNr 5) | `70` |
| `08 00 b9 00 5d 01 00 00` | `d8` |
| `08 00 b4 00 5d 01 00 00` | `1c` |

**Folge für ebusd:** ebusd kann das Prüfbyte nicht selbst berechnen. Lesebefehle sind kein Problem, weil das Prüfbyte je Parameter fest ist und einfach in die ID der CSV kommt. Für das Schreiben enthält die CSV **ein fertiges Telegramm pro erlaubtem Wert** (`Set<Name>_<Rohwert>`), erzeugt von [`tools/generate_csv.py`](../tools/generate_csv.py).

## Broadcasts und weiterer Verkehr

| Telegramm | Takt | Inhalt |
|---|---|---|
| `30 f1 05 07` (genormt) | ca. 10 s | Betriebsdaten Regler → Feuerungsautomat: Zustand, Aktion, **Kesselsollwert** (DATA2c), Kesseldruck (n/v), Stellgrad, **Warmwasser-Soll** (DATA1c), Brennstoff. In der CSV als `regler Betriebsdaten`. |
| `30 fe 07 00` (genormt) | ca. 60 s | Datum/Uhrzeit, Außentemperatur |
| `f1 fe 50 0a` | ca. 30 s | Kesselstatus, 13 Byte. Vermutlich Byte 7 = Kesseltemperatur und Byte 9 = Warmwasser (je ÷ 2). Brennerstatus noch **nicht** entschlüsselt. |
| `30 50 50 14` | regelmäßig | WCM-FS-intern, nicht entschlüsselt |
| `07 f6 09 02`, `07 50 09 02` | regelmäßig | nicht entschlüsselt |
| `f1 fe fe 01` | selten | Kennung (ASCII „E000“ …) |

Für den Betrieb ist nichts davon nötig. Alle relevanten Werte kommen über `50 22`.

## Hintergrund: Schnittstelle des WCM-COM

Die Weboberfläche des WCM-COM fragt per `POST /parameter.json` (Content-Type `text/plain`) ab:

```json
{"prot":"coco","telegramm":[[10,0,1,3101,0,0,0,0]]}
```

Felder: `[Modultyp, Buskennung, Befehl, InfoNr, Index, Prot, Wert_lo, Wert_hi]`, mit Befehl `1` = lesen und `2` = schreiben. Bekannte Modultypen laut Skript des WCM-COM: `3` = KE/Solar, `6` = BE/FS (Heizkreis), `9` = MA/KA, `10` = WTC (HM/WG/WO). Die Antwort enthält den Wert in den letzten beiden Feldern. Das ist praktisch, um vor dem Umstieg InfoNr und Werte zu vergleichen.
