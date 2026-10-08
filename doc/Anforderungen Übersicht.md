# Anforderungsdokument: TruderRinge (v2.1)
**Projekt:** Nachfolge-Vereinssoftware für die SG Gemütlichkeit Trudering e.V.  
**Ziel:** Ablösung der Alt-Software *Schuetzenliste* durch ein dynamisches, regelbasiertes System mit DISAG-OpticScore-Anbindung.

---

## 1. Dynamischer Wöchentlicher Schießbetrieb (Kernlogik)

Das System unterstützt den flexiblen, wöchentlichen Schießrhythmus mit dynamischer Schuss-Sequenzierung:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      WÖCHENTLICHER SCHIESSABEND-ABLAUF                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Schützen-Anmeldung & Modus-Wahl per Klasse (Gewehr, Pistole, Damen...)   │
│                                                                             │
│ 2. Dynamische Schuss-Zuordnung (Schuss 1–20) je nach Wochen-Status:         │
│    ├── STATUS A (Fleischpreis aktiv):  Schuss 1–20 ➔ Fleischpreis (Teiler) │
│    └── STATUS B (Fleischpreise aus):   Schuss 1–20 ➔ Pokal (Ring/Zehntel)  │
│                                                                             │
│ 3. Folge-Schüsse (Schuss 21–30+):                                           │
│    └── Schuss 21+ ➔ Pokal, Serie, Vortag oder Schießspiele / Gaudischuss     │
└─────────────────────────────────────────────────────────────────────────────┘