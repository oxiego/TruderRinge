Hier ist das vollständig überarbeitete und erweiterte **Software-Architekturdokument (`Grundarchitektur.md`)**.

Es enthält nun die flexiblen Ingestion-Strategien für den **Offline-/Tagesabschluss-Import** (WM-Shot `.wmk`, OpticScore XML) als primäre Wege sowie die **JSON-Live-Schnittstelle** als Fallback, die **dynamische wöchentliche Klassen- & Kontingent-Steuerung** (Fleischpreis vs. Pokal per Klasse) sowie das erweiterte **Schießspiele-Modul** (Er-und-Sie, Ostern, Martini, Nikolaus).

---

# Software-Architekturdokument: TruderRinge (v2.0)

**Projekt:** TruderRinge – Nachfolger für Schuetzenliste

**Kontext:** Schützengesellschaft Gemütlichkeit Trudering e.V.

**Plattform:** Linux Host (Backend) / Web & Android (Frontend)

**Datum:** Oktober 2026

---

## 1. Übersicht & Zielsetzung

Die Software **TruderRinge** dient der digitalen Auswertung, Konfiguration und Ergebnisaggregation für Schießstände der Marke **DISAG OpticScore** (optional betrieben mit **WM-Shot**). Sie löst die bisherige Office-basierte Lösung (*Schuetzenliste*) ab.

### Hauptziele

* **Flexible Schnittstellen & Entkopplung:** Die Erfassung unterstützt primär den lesenden **Offline-/Tagesabschluss-Import** aus WM-Shot-Datenbanken (`.wmk`) oder DISAG-OpticScore-XML-Dateien sowie optional die direkte Ingestion aus dem DISAG OpticScore Server.
* **Dynamische Regel-Engine:** Wöchentlich wechselnde und klassenspezifische Auswertung (z. B. *Schuss 1–20 = Fleischpreis (Teiler)*, bis das Kontingent pro Schützenklasse aufgebraucht ist; danach automatischer Wechsel auf *Pokal (Ringe)*).
* **Erweitertes Schießspiele-Modul:** Native Unterstützung für Traditionsschießen (Er-und-Sie, Osterschießen mit Limit-Scheiben, Martinischießen, Nikolausschießen).
* **Multi-Plattform:** Primäre Bedienung als Web-Anwendung für Schießleiter (PC/Tablet im Schützenheim) sowie als Android-App für Schützen via Capacitor.
* **Linux-Native:** Das Backend läuft vollständig auf Linux (FastAPI / Python).

---

## 2. Systemarchitektur & Datenfluss

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ELEKTRONISCHE SCHIESSSTAND-INFRASTRUKTUR              │
│      DISAG OpticScore Messrahmen ──► SIZ ──► OpticScore Server (Windows)     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
 ┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
 │ OpticScore XML       │   │ WM-Shot DB (.wmk)    │   │ DISAG JSON-Live / DB │
 │ (Dokumentierter      │   │ (Tagesabschluss-     │   │ (Echtzeit / Direct   │
 │  Offline-Export)     │   │  Import nach Event)  │   │  DB Access Fallback) │
 └──────────┬───────────┘   └──────────┬───────────┘   └──────────┬───────────┘
            │                          │                          │
            └──────────────────────────┼──────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                  TRUDERRINGE BACKEND (Linux Host)                           │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ 1. Ingestion Layer (Multi-Adapter / Parser)                           │  │
│  │    - WM-Shot .wmk File Parser / Reader                                │  │
│  │    - OpticScore XML Importer                                          │  │
│  │    - Optional: Async Poller / JSON Live Listener                      │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ 2. Core Business & Rule Engine                                        │  │
│  │    - Wöchentliche Klassen- & Kontingent-Steuerung                     │  │
│  │    - Dynamic Sequence Splitter (Schuss 1-20 Fleischpreis ↔ Pokal)     │  │
│  │    - Trad. Schießspiele (Er-und-Sie, Ostern, Martini, Nikolaus)       │  │
│  │    - Aggregation für Saisontabellen (Best-of-N, Streichergebnisse)    │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ 3. Vereins-Datenbank (PostgreSQL / SQLite)                            │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ 4. REST API & WebSocket Server (FastAPI / Pydantic)                   │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 │ HTTP REST / WebSockets (OpenAPI Schema)   │
                 ▼                                           ▼
┌─────────────────────────────────┐         ┌─────────────────────────────────┐
│     ANGULAR WEB FRONTEND        │         │   ANGULAR + CAPACITOR (ANDROID) │
│ (Schießleiter PC / PWA / Tablet)│         │ (Ergebnis-App für Schützen)     │
└─────────────────────────────────┘         └─────────────────────────────────┘

```

---

## 3. Tech-Stack

| Schicht | Technologie | Beschreibung |
| --- | --- | --- |
| **Backend Framework** | **Python 3.11+ / FastAPI** | High-Performance API, native Datenauswertung, asynchrone Tasks für File-Parsing und Ingestion. |
| **ORM & DB-Access** | **SQLAlchemy 2.0 & sqlite3 / pyodbc** | DB-Zugriff auf die Vereins-DB sowie Parser/Reader für externe MS SQL / SQLite `.wmk`-Dateien. |
| **Vereins-Datenbank** | **PostgreSQL** (oder SQLite) | Speicherung von Mitgliederdaten, Wochen-Klassenkontingenten, Regelsätzen und aggregierten Ergebnissen. |
| **Frontend Framework** | **Angular 17+** | Single-Page-Application mit TypeScript für Schießleiter-Dashboard, Standbelegung und Siegerlisten. |
| **Mobile Deployment** | **Capacitor** (`@capacitor/core`) | Native Hülle um das Angular-Frontend für die Android-App der Schützen. |

---

## 4. Kernkomponenten & Modulbeschreibung

### 4.1. Flexible Ingestion Layer

Das Ingestion-Modul verarbeitet Schuss- und Seriendaten flexibel über drei Prioritätsstufen:

* **Priorität 1 (WM-Shot-Datenbank `.wmk`):** Liest nach Abschluss des Schießtages die `.wmk`-Datei aus und extrahiert Schützen, Serien 1–4 (Ringe und Zehntel), Einzel-Teiler sowie Probe-/Wertungsschuss-Markierungen.
* **Priorität 2 (OpticScore XML-Export):** Importiert strukturierte XML-Dateien mit vollständigen Einzelschussdaten (Ringe, Zehntel, Teiler, Schussnummer, Status).
* **Priorität 3 (JSON-Live / Direct Poller):** Optionaler Fallback für Live-Echtzeitübertragungen während des Schießbetriebs.

### 4.2. Core Business Engine (Dynamische Regel- & Sequenzsteuerung)

* **Klassen- & Kontingent-Steuerung:** Schießabende werden nach Schützenklassen (z. B. *Pistole*, *Gewehr Herren*, *Damen*, *Jugend*) getrennt verwaltet.
* **Dynamic Sequence Splitter (Schuss 1–20):**
* **Status A (Fleischpreis aktiv):** Schuss 1–20 werden als Teiler-Wertung für die Fleischpreis-Tagesliste ausgewertet.
* **Status B (Fleischpreise aufgebraucht ODER Pokal-Woche):** Schuss 1–20 werden direkt der Pokal- / Jahresmeisterschaft (Ringe / Zehntel) gutgeschrieben. Sobald z. B. die Pistolen-Schützen ihr Fleischpreis-Kontingent verschossen haben, schaltet das System für diese Klasse automatisch auf Pokal um, während Gewehr-Klassen weiter auf Fleischpreise schießen können.


* **Saison-Aggregator:** Berechnet Jahresmeister über $N$ beste Schießabende (inkl. Streichergebnissen).

### 4.3. Sonder- & Traditionsschießspiele-Modul

* **Er-und-Sie-Schießen:** Verwaltung von Zweier-Teams (Dame + Herr oder Zulosung) mit automatischer Aufsummierung der Einzelergebnisse zu einer Team-Rangliste.
* **Osterschießen:** Beschränkung auf feste Maximal-Schusszahlen $X$ (z. B. strikt 3 oder 5 Spezial-Schüsse auf Osterei-/Motivscheiben).
* **Martinischießen:** Kombinierte Auswertung aus bestem Teiler + bester Deckserie für die Martinsgans-Auswertung.
* **Nikolausschießen & Königsschießen:** Direkt-Ausgabe von Siegerlisten bzw. verdeckte Auswertung bester Tiefschüsse (Teiler).

---

## 5. Relationales Datenmodell (Vereins-DB Schema)

```sql
-- Mitgliederstamm
CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    disag_start_number INT UNIQUE,
    category_class VARCHAR(50) NOT NULL, -- z.B. 'PISTOLE', 'GEWEHR_HERREN', 'DAMEN'
    active BOOLEAN DEFAULT TRUE
);

-- Wettbewerbe / Schießabende
CREATE TABLE competitions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    season VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    competition_type VARCHAR(50) DEFAULT 'STANDARD', -- 'STANDARD', 'ER_UND_SIE', 'OSTERN', 'MARTINI', 'NIKOLAUS'
    active BOOLEAN DEFAULT TRUE
);

-- Wöchentlicher Klassen-Status (Fleischpreis vs. Pokal)
CREATE TABLE class_night_status (
    id SERIAL PRIMARY KEY,
    competition_id INT REFERENCES competitions(id),
    category_class VARCHAR(50) NOT NULL,
    fleischpreis_active BOOLEAN DEFAULT TRUE, -- TRUE = Schuss 1-20 Fleischpreis, FALSE = Schuss 1-20 Pokal
    fleischpreis_remaining_prizes INT DEFAULT 0
);

-- Verarbeitete Schussergebnisse (Aggregiert & Einzelschuss)
CREATE TABLE processed_shots (
    id SERIAL PRIMARY KEY,
    member_id INT REFERENCES members(id),
    competition_id INT REFERENCES competitions(id),
    series_number INT NOT NULL,         -- Serie 1, 2, 3, 4
    shot_number INT NOT NULL,           -- Schuss 1 bis 40
    ring_value INT NOT NULL,            -- Ganze Ringe
    tenth_value NUMERIC(4,1) NOT NULL,  -- Zehntelwertung (z.B. 102.7)
    teiler NUMERIC(6,1) NOT NULL,       -- Teiler / Tiefschuss
    target_category VARCHAR(50) NOT NULL, -- 'FLEISCHPREIS', 'POKAL', 'GAUDI', 'SONDER'
    is_practice BOOLEAN DEFAULT FALSE,  -- Probe- vs. Wertungsschuss
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Zweier-Teams für Er-und-Sie-Schießen
CREATE TABLE couples_competition (
    id SERIAL PRIMARY KEY,
    competition_id INT REFERENCES competitions(id),
    member_male_id INT REFERENCES members(id),
    member_female_id INT REFERENCES members(id),
    total_score NUMERIC(6,1),
    combined_teiler NUMERIC(6,1)
);

```

---

## 6. Meilensteine & Roadmap

1. **Phase 1: Vorbereitung & Import-Verifikation**
* Analyse realer WM-Shot `.wmk`-Dateien sowie OpticScore XML-Exporte im Test-Wettkampf.
* Aufbau der Entwicklungs-Pipeline (Python / FastAPI / Angular).


2. **Phase 2: Ingestion & Business Logic**
* Implementierung der File-Parser (`.wmk` / XML).
* Entwicklung der dynamischen Klassen- & Kontingent-Steuerung für Schuss 1–20.
* Entwicklung des Sonder-Schießspiele-Moduls (Er-und-Sie, Ostern, Martini, Nikolaus).


3. **Phase 3: Angular Frontend**
* Dashboard für Schießleiter (Standbelegung, Kontingent-Schalter pro Klasse, Siegerlisten).
* Live-Anzeige und Aushang-Export (PDF/Druck).


4. **Phase 4: Mobile App Target (Android)**
* Integration von Capacitor in Angular.
* Bereitstellung und Test des Android-APKs für Schützen.