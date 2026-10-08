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
│    ├── STATUS A (Fleischpreis aktiv):  Schuss 1–20 ➔ Fleischpreis (Teiler)  │
│    └── STATUS B (Fleischpreise aus):   Schuss 1–20 ➔ Pokal (Ring/Zehntel)   │
│                                                                             │
│ 3. Folge-Schüsse (Schuss 21–30+):                                           │
│    └── Schuss 21+ ➔ Pokal, Serie, Vortag oder Schießspiele / Gaudischuss    │
└─────────────────────────────────────────────────────────────────────────────┘

```

---

## 2. Detaillierte Feature-Anforderungen

### Feature 2.1: Klassen- & Kontingent-Steuerung (`Button: Schießabend-Setup`)

* **FR-101 (Klassenspezifischer Status):** Der Schießmodus (Fleischpreis vs. Pokal) lässt sich pro Schützenklasse (z. B. *Pistole*, *Gewehr Herren*, *Damen*, *Jugend*) unabhängig steuern.
* **FR-102 (Kontingent-Verwaltung / Fleischpreis-Stop):**
* Wenn das Kontingent für Fleischpreise einer Klasse aufgebraucht ist (alle Preise verschossen), schaltet das System für diese Klasse automatisch oder manuell auf **Status B (Standard = Pokal)** um.
* *Beispiel:* Da Pistolen-Schützen oft früher fertig sind oder weniger Beteiligte stellen, kann deren Fleischpreis-Phase früher beendet werden, während die Gewehr-Klasse noch auf Fleischpreise schießt.


* **FR-103 (Wochen-Turnus / Wechsel-Logik):** Die Schießleitung definiert vor Beginn des Schießabends das Wochen-Set (z. B. *Ungerade Woche = Fokus Fleischpreis*, *Gerade Woche = Fokus Pokal*).

---

### Feature 2.2: Dynamischer Ingestion-Splitter (`Button: DISAG Import & Rule Engine`)

* **FR-201 (Dynamische Regelanwendung Schuss 1–20):**
* **Fall 1 (Fleischpreis-Woche & Kontingent offen):** Schuss 1–20 wird als **Fleischpreis / Tiefschuss (Teiler)** gewertet.
* **Fall 2 (Pokal-Woche ODER Fleischpreise verschossen):** Schuss 1–20 wird direkt der **Pokal- / Jahrestabelle (Ringe / Zehntel)** gutgeschrieben.


* **FR-202 (Folgeserien / Schuss 21+):**
* Schuss 21–30 wird je nach Konfiguration für den Pokal-Nachtrag, Vortagsserien oder Preisschießen gewertet.
* Schuss 31+ wird für Schießspiele, Glücksscheiben oder Gaudischießen eingeordnet.


* **FR-203 (Klassen-Disziplinen):** Berücksichtigung unterschiedlicher Scheiben- und Wertungsarten (Luftgewehr Ringe/Teiler vs. Luftpistole mit eigenem Teiler-Faktor).

---

### Feature 2.3: Schützen- & Stammdatenverwaltung (`Button: Mitglieder`)

* **FR-301 (Mitglieder-Profil):** Erfassung aller Stammdaten (Name, Vorname, Geburtsdatum, Klasse, Status).
* **FR-302 (DISAG-Zuordnung):** Verknüpfung der internen Vereins-ID mit der DISAG-Startnummer / Chipkarte.
* **FR-303 (Klassen-Zuordnung):** Zuordnung zu Disziplinen (z. B. *Luftpistole*, *Luftgewehr*, *Auflage*), um die automatische Schuss-Regel anzuwenden.

---

### Feature 2.4: Standbelegung & Anmeldung (`Button: Standbelegung`)

* **FR-401 (Schnell-Anmeldung):** Der Schießleiter weist einem Schützen beim Betreten des Standes einen freien DISAG-Stand zu.
* **FR-402 (Automatische Regel-Anzeige):** Das System zeigt beim Anmelden sofort an, welcher Modus für die Klasse des Schützen heute aktiv ist (z. B. *"Pistole: Pokal (Fleischpreise beendet)"* vs. *"Gewehr: Fleischpreis"*).

---

### Feature 2.5: Tages- & Saisonauswertung (`Button: Saisontabellen & Ergebnisse`)

* **FR-501 (Flexibles Saisonkonto):** Das System aggregiert alle Wochentage über die Saison und berücksichtigt nur die gültigen Pokal-Schüsse (egal ob in der 1. oder 2. Serie geschossen).
* **FR-502 (Best-of-N Wertung):** Berechnung der Jahresmeister über die $N$ besten Schießabende einer Saison pro Klasse (unter Berücksichtigung von Streichergebnissen).
* **FR-503 (Fleischpreis-Siegerliste):** Erstellung tagesaktueller Gewinnlisten sortiert nach Best-Teilern zur Preisverteilung am Ende des Schießabends.

---

### Feature 2.6: Sonder- & Schießspiele Modul (`Button: Schießspiele / Traditionsschießen`)

* **FR-601 (Königsschießen):** Verdeckte Auswertung bester Tiefschüsse (Teiler) ohne Live-Anzeige für die Schützen.
* **FR-602 (Gaudischießen / Vorgabe):** Modul für Vorgabe-Teiler, Teiler-Differenzen oder Glücksscheiben.
* **FR-603 (Er-und-Sie-Schießen):**
* Paar-Bildung aus zwei Schützen (z. B. Dame + Herr oder zugeloste Paare).
* Kombinierte Auswertung: Aufsummierung der Einzelergebnisse (Ringe oder Teiler-Summe) des Paares zu einer gemeinsamen Team-Rangliste.


* **FR-604 (Osterschießen):**
* Unterstützung von Spezial- / Motivscheiben (z. B. Osterei-/Glücksscheiben mit reduzierter / begrenzter Schussanzahl $X$).
* Erfassung fester Maximal-Schusszahlen pro Schütze (z. B. strikt nur 3 oder 5 Spezial-Schuss erlaubt).


* **FR-605 (Martinischießen):**
* Saisonal geführter Wettbewerb (z. B. Martinsgans-Schießen).
* Auswertung nach kombiniertem Schlüssel (z. B. bester Teiler + beste Deckserie).


* **FR-606 (Nikolausschießen):**
* Jahresabschluss-/Jubiläumsschießen mit spezifischem Preisschlüssel und Direkt-Ausgabe der Platzierungen.



---

## 3. Tech-Stack & Architektur-Verankerung

* **Backend:** Python (FastAPI) mit dynamischer `RuleEngine`-Klasse, die pro Schuss, Schützenklasse und Tages-Status die korrekte Zielkategorie ermittelt.
* **Frontend:** Angular Web-App für die Schießleitung (PC/Tablet) + Capacitor-App für Schützen.
* **Datenbank:** PostgreSQL / SQLite mit getrennten Tabellen für `Woche_Status`, `Klassen_Kontingent`, `ProcessedShots` und `SeasonAggregations`.

```

```