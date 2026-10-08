Hier ist das aktualisierte Anforderungsdokument (Software Requirements Specification - SRS v2.2), das die technischen Ergebnisse der Vorprüfung (WM-Shot `.wmk`, OpticScore XML, JSON-Live), die flexible Multi-Channel Ingestion, die dynamische Klassen-/Kontingent-Steuerung sowie das erweiterte Sonder-Schießspiele-Modul vollständig als Anforderungen formuliert.

---

```markdown
# Anforderungsdokument: TruderRinge (v2.2)
**Projekt:** Nachfolge-Vereinssoftware für die SG Gemütlichkeit Trudering e.V.  
**Ziel:** Ablösung der Alt-Software *Schuetzenliste* durch ein dynamisches, regelbasiertes System mit flexibler Anbindung an DISAG-OpticScore und WM-Shot.

---

## 1. Systemübersicht & Ingestion-Architektur

Das System verarbeitet Schuss- und Seriendaten flexibel über drei Prioritätsstufen für die Datenerfassung:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DATENERFASSUNG & INGESTION-ROUTING                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ PRIO 1: Offline / Tagesabschluss ➔ WM-Shot DB (.wmk Reader/Parser)          │
│ PRIO 2: Offline / Export         ➔ DISAG OpticScore XML Importer            │
│ PRIO 3: Online / Live-Fallback    ➔ DISAG JSON-Live / Direct DB Poller      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      WÖCHENTLICHER SCHIESSABEND-ABLAUF                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Schützen-Anmeldung & Modus-Wahl per Klasse (Gewehr, Pistole, Damen...)   │
│                                                                             │
│ 2. Dynamische Schuss-Zuordnung (Schuss 1–20) je nach Klassen-Status:        │
│    ├── STATUS A (Fleischpreis aktiv):  Schuss 1–20 ➔ Fleischpreis (Teiler) │
│    └── STATUS B (Fleischpreise aus):   Schuss 1–20 ➔ Pokal (Ring/Zehntel)  │
│                                                                             │
│ 3. Folge-Schüsse (Schuss 21–30+):                                           │
│    └── Schuss 21+ ➔ Pokal, Serie, Vortag oder Sonder-Schießspiele            │
└─────────────────────────────────────────────────────────────────────────────┘

```

---

## 2. Detaillierte Feature-Anforderungen

### Feature 2.1: Multi-Channel Ingestion Layer (`Button: Daten-Import / Synchronisation`)

* **FR-101 (WM-Shot .wmk Import - Prio 1):** Auslesen und Parsen von WM-Shot-Datenbankdateien (`.wmk`) nach Schießende zur automatischen Übernahme von Schützen, Serienergebnissen (1–4), Ringen, Zehntelwerten, Einzel-Teilern sowie der Kennzeichnung von Probe- vs. Wertungsschüssen.
* **FR-102 (DISAG OpticScore XML Import - Prio 2):** Import von strukturierten OpticScore-XML-Exporten mit vollständigen Einzelschussdaten (Ringe, Zehntel, Teiler, Schussnummer, Status, Zeitstempel).
* **FR-103 (JSON-Live / Direct Poller - Prio 3):** Optionaler Echtzeit-Worker / Listener zum direkten Abgriff von Live-Schussdaten via UDP/WebSocket oder direkte DB-Abfrage als Fallback-Lösung.

---

### Feature 2.2: Klassen- & Kontingent-Steuerung (`Button: Schießabend-Setup`)

* **FR-201 (Klassenspezifischer Status):** Der Schießmodus (Fleischpreis vs. Pokal) lässt sich pro Schützenklasse (z. B. *Pistole*, *Gewehr Herren*, *Damen*, *Jugend*) unabhängig steuern.
* **FR-202 (Kontingent-Verwaltung / Fleischpreis-Stop):**
* Wenn das Kontingent für Fleischpreise einer Klasse aufgebraucht ist (alle Preise verschossen), schaltet das System für diese Klasse automatisch oder manuell auf **Status B (Pokal)** um.
* *Beispiel:* Da Pistolen-Schützen oft früher fertig sind oder weniger Beteiligte stellen, kann deren Fleischpreis-Phase früher beendet werden, während die Gewehr-Klasse noch auf Fleischpreise schießt.


* **FR-203 (Wochen-Turnus / Wechsel-Logik):** Konfiguration der Wochen-Regelsets durch die Schießleitung (z. B. *Ungerade Woche = Fokus Fleischpreis*, *Gerade Woche = Fokus Pokal*).

---

### Feature 2.3: Dynamischer Ingestion-Splitter (`Button: Rule Engine`)

* **FR-301 (Dynamische Regelanwendung Schuss 1–20):**
* **Fall A (Fleischpreis-Woche & Kontingent offen):** Schuss 1–20 wird als **Fleischpreis / Tiefschuss (Teiler)** gewertet.
* **Fall B (Pokal-Woche ODER Fleischpreise verschossen):** Schuss 1–20 wird direkt der **Pokal- / Jahrestabelle (Ringe / Zehntel)** gutgeschrieben.


* **FR-302 (Folgeserien / Schuss 21+):**
* Schuss 21–30 wird je nach Konfiguration für den Pokal-Nachtrag, Vortagsserien oder Preisschießen gewertet.
* Schuss 31+ wird für Schießspiele, Glücksscheiben oder Gaudischießen eingeordnet.


* **FR-303 (Disziplinen & Faktoren):** Berücksichtigung unterschiedlicher Scheiben- und Wertungsarten (Luftgewehr vs. Luftpistole mit eigenem Teiler-Faktor).

---

### Feature 2.4: Schützen- & Stammdatenverwaltung (`Button: Mitglieder`)

* **FR-401 (Mitglieder-Profil):** Erfassung aller Stammdaten (Name, Vorname, Geburtsdatum, Standard-Klasse, Status).
* **FR-402 (DISAG- & WM-Shot Mapping):** Verknüpfung der internen Vereins-ID mit der DISAG-Startnummer, Chipkarte oder WM-Shot-Schützen-ID.
* **FR-403 (Klassen-Zuordnung):** Zuordnung zu Disziplinen (z. B. *Luftpistole*, *Luftgewehr*, *Auflage*), um die automatische Schuss-Regel anzuwenden.

---

### Feature 2.5: Standbelegung & Anmeldung (`Button: Standbelegung`)

* **FR-501 (Schnell-Anmeldung):** Der Schießleiter weist einem Schützen beim Betreten des Standes einen freien DISAG-Stand zu.
* **FR-502 (Automatische Regel-Anzeige):** Das System zeigt beim Anmelden sofort an, welcher Modus für die Klasse des Schützen heute aktiv ist (z. B. *"Pistole: Pokal (Fleischpreise beendet)"* vs. *"Gewehr: Fleischpreis"*).

---

### Feature 2.6: Tages- & Saisonauswertung (`Button: Saisontabellen & Ergebnisse`)

* **FR-601 (Flexibles Saisonkonto):** Aggregation aller Wochentage über die Saison unter Berücksichtigung der Pokal-Schüsse.
* **FR-602 (Best-of-N Wertung):** Berechnung der Jahresmeister über die $N$ besten Schießabende einer Saison pro Klasse (inkl. automatischer Streichergebnisse).
* **FR-603 (Fleischpreis-Siegerliste):** Erstellung tagesaktueller Gewinnlisten sortiert nach Best-Teilern zur Preisverteilung am Ende des Schießabends.

---

### Feature 2.7: Sonder- & Traditionsschießspiele Modul (`Button: Schießspiele / Traditionsschießen`)

* **FR-701 (Königsschießen):** Verdeckte Auswertung bester Tiefschüsse (Teiler) ohne Live-Anzeige für die Schützen.
* **FR-702 (Gaudischießen / Vorgabe):** Modul für Vorgabe-Teiler, Teiler-Differenzen oder Glücksscheiben.
* **FR-703 (Er-und-Sie-Schießen):**
* Paar-Bildung aus zwei Schützen (z. B. Dame + Herr oder Zulosung).
* Kombinierte Auswertung: Aufsummierung der Einzelergebnisse (Ringe oder Teiler-Summe) des Paares zu einer gemeinsamen Team-Rangliste.


* **FR-704 (Osterschießen):**
* Unterstützung von Spezial- / Motivscheiben mit reduzierter / begrenzter Schussanzahl $X$.
* Erfassung fester Maximal-Schusszahlen pro Schütze (z. B. strikt nur 3 oder 5 Spezial-Schuss auf Ostereierscheiben erlaubt).


* **FR-705 (Martinischießen):**
* Saisonal geführter Wettbewerb (Martinsgans-Schießen).
* Auswertung nach kombiniertem Schlüssel (z. B. bester Teiler + beste Deckserie).


* **FR-706 (Nikolausschießen):**
* Jahresabschluss-/Jubiläumsschießen mit spezifischem Preisschlüssel und Direkt-Ausgabe der Platzierungen.



---

## 3. Tech-Stack & Systemumgebung

* **Backend:** Python 3.11+ (FastAPI) mit asynchronem Ingestion-Modul (`.wmk`-Parser, XML-Reader) und dynamischer `RuleEngine`-Klasse.
* **Frontend:** Angular 17+ Web-App für die Schießleitung (PC/Tablet) + Capacitor Android-App für Schützen.
* **Datenbank:** PostgreSQL / SQLite mit getrennten Relationen für Mitglieder, Wochen-Klassenkontingente, verarbeitete Schüsse, Saisontabellen und Zweier-Teams.

```

```