# 6. Fehlersuche

| Symptom | Ursache / Lösung |
|---|---|
| Adapter-Statusseite: **eBUS signal: no signal** | Adern nicht richtig auf den eBUS-Klemmen, oder Anlage aus. Mit dem Multimeter ca. 18–22 V DC an den Klemmen messen. |
| ebusd-Protokoll: `invalid configpath without scanconfig` | `--configpath=/config` fehlt. |
| `found messages: 0` | CSV liegt nicht im Ordner `addon_configs/<id>_ebusd/`, oder die Datei ist kaputt, z. B. durch Kommas in Kommentaren, die das Spaltenformat verschieben. |
| `push poll message: ERR: generic device error` | ebusd läuft noch mit `--readonly`. |
| Einzelne `read timeout` | Normal bei WLAN, der nächste Zyklus holt den Wert. Häufen sie sich, Empfang verbessern (siehe Hardware). |
| Werte kommen nur sehr langsam | `--pollinterval=1` fehlt. Standard sind 5 s pro Abfrage. |
| Schreiben: ebusd meldet `sent write …`, ACK `00`, aber der Wert bleibt alt | ebusd sendet nicht als `ff`. `--address=ff` setzen. Das WCM-COM muss vom Bus. |
| Nach dem Setzen von `--address=ff`: viele Fehler und Kollisionen | Das WCM-COM hängt noch am Bus (zweiter Teilnehmer mit `ff`). |
| Regler springt nach dem Verstellen zurück | Wert wurde nicht übernommen (siehe oben) oder liegt außerhalb dessen, was der WCM-FS akzeptiert. Im ebusd-Protokoll nachsehen. |
| Sensoren heißen `…_2` | Alte Entitäten mit derselben ID existierten noch, siehe [Umstieg](04-home-assistant.md#umstieg-von-einer-rest-abfrage-des-wcm-com). |
| Betriebsart HK1 zeigt nur eine Zahl | InfoNr 274 ist noch nicht entschlüsselt. |
| Laufzeiten ungenau | Die Flamme wird zyklisch gelesen. Mit `--pollinterval=1` liegt die Auflösung bei etwa 8 s, sehr kurze Stufe-2-Phasen beim Start (ca. 20 s) werden dabei grob erfasst. |

## Nützliche Befehle

MQTT mitlesen (z. B. mit *MQTT Explorer* oder in HA unter *Einstellungen → Geräte & Dienste → MQTT → Konfigurieren → Topic abonnieren*): `ebusd/#`

Einen Wert sofort lesen: Topic `ebusd/wtc/Vorlauftemp/get` mit leerem Payload publizieren.

Rohverkehr ansehen: Mit `--lograwdata` erscheinen im Protokoll der App Zeilen wie

```
[bus notice] >ff08502203941d0c3c<0002f000xx>00
```

`>` steht für gesendete, `<` für empfangene Bytes. Die Struktur ist in [03-protokoll.md](03-protokoll.md) beschrieben.
