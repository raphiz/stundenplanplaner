# Stundenplanplaner

## Work in progres...

**Wenn du dieses Projekt nutzt und/oder unsterstüzenswert findest, dann hilf doch bitte mit!**
Das kannst du indem du...

- ... manuell testes (und für gefundene Fehler [ein Ticket aufmachst](https://github.com/raphiz/hsr_timetable/issues))
- ... deine Ideen miteinbringst (Als [Ticket](https://github.com/raphiz/hsr_timetable/issues))
- ... Dokumentation schreibst
- ... Tests schreibst
- ... mithilfst zu coden (bessere Algorithmen, Code verschönern usw.)
- ... ein Grafischer Client etwickelst
- ...

Wenn dir Informationen fehlen um mitzuhelfen, dann schreib mir ungehemmt [eine E-Mail](https://www.raphael.li/contact/), frag mich persönlich an der HSR oder mach [ein neues Ticket auf](https://github.com/raphiz/hsr_timetable/issues)!


## Projekt einrichten

1. Docker und Make installieren
2. Projekt klonen
3. Datei auth.cfg im Projektverzeichnis erstellen:

```
[authentication]
username=<hsr-username>
password=<hsr-passwort>
```

Die Demo kann nun mittels `sudo make demo_timetables` ausgeführt werden.

Das Resultat sollte etwa so aussehen:

```
[...]
Calculation took 43.428021 seconds
Found 4 solutions!
Time      Mon      Tue       Wed       Thu       Fri       Sat    Sun
--------  -------  --------  --------  --------  --------  -----  -----
08:10:00  WED2-v1  AD2-v1    BuPl-v6   PrFm-v1   PrFm-u11
09:05:00  WED2-v1  AD2-v1    BuPl-u61  PrFm-v1   PrFm-u11
10:10:00  MGE-v1   SE1-v1    CPl-v1    WED2-u13  MGE-u11
11:05:00  MGE-v1   SE1-v1    CPl-v1    WED2-u13  MGE-u11
12:10:00                     MsTe-v1
13:10:00           AD2-u14
14:05:00           AD2-u14   MsTe-v1
15:10:00           SE1-u14   CPl-u12
16:05:00           SE1-u14   CPl-u12
17:00:00           ReIng-v1  MsTe-u11
17:55:00           ReIng-v1  MsTe-u11

[...]
```
