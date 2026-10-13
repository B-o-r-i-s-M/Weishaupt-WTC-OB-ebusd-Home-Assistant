# Changelog

## 1.0.0 – 2026-10-13

Erste Veröffentlichung.

- Protokoll der Weishaupt-Dienste `50 22` (lesen) und `50 23` (schreiben) inklusive Prüfbyte (CRC8, Polynom 0x5C) dokumentiert
- ebusd-CSV mit 26 Kesselwerten, 9 Heizkreis-Werten, Broadcast `05 07` und 422 Schreibtelegrammen für 7 Heizkreis-Parameter
- CSV-Generator `tools/generate_csv.py` mit Selbsttest gegen Original-Telegramme
- Home-Assistant-Packages (Sensoren, Statistik, Schreiben mit Rückmeldung) und Dashboard-Ansicht
- Erkenntnis: Der WCM-FS übernimmt Schreibbefehle nur von Absender `ff` → ebusd mit `--address=ff`, WCM-COM entfernen

Getestet mit WTC-OB 18-B, WCM-FS 327.30, eBUS Adapter Shield C5, ebusd 26.1, Home Assistant 2026.10.
