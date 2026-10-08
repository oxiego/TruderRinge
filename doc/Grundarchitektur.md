# Software-Architekturdokument: TruderRinge

**Projekt:** TruderRinge – Nachfolger für Schuetzenliste  
**Kontext:** Schützengesellschaft Gemütlichkeit Trudering e.V.  
**Plattform:** Linux Host (Backend) / Web & Android (Frontend)  
**Datum:** Oktober 2026  

---

## 1. Übersicht & Zielsetzung

Die Software **TruderRinge** dient der digitalen Auswertung, Konfiguration und Ergebnisaggregation für Schießstände der Marke **DISAG OpticScore**. Sie löst die bisherige Office-basierte Lösung (*Schuetzenliste*) ab.

### Hauptziele
* **System-Entkopplung:** Die DISAG-Trefferdatenbank wird rein lesend abgefragt. Die vereinsspezifischen Regeln und Ergebnisse liegen in einer separaten Vereins-Datenbank.
* **Flexible Regel-Engine:** Dynamische Auswertung von Schussreihenfolgen (z. B. *Schuss 1–20 = Pokal X*, *Schuss 21–30 = Fleischpreis*).
* **Multi-Plattform:** Primäre Bedienung als Web-Anwendung für Schießleiter (PC/Tablet im Schützenheim) sowie als Android-App für Schützen.
* **Linux-Native:** Die Entwicklungs- und Laufzeitumgebung des Backends basiert vollständig auf Linux.

---

## 2. Systemarchitektur & Datenfluss

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DISAG OPTICSCORE SYSTEM (Windows)                     │
│               [ MS SQL Server / LocalDB / SQLite / Network ]                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                      Lesezugriff via Network / ODBC
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                  TRUDERRINGE BACKEND (Linux Host)                           │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ 1. DISAG Ingestion Service (Async Poller / Worker)                    │  │
│  │    - Intervallbasiertes Auslesen neuer Schüsse                       │  │
│  │    - Mapping: DISAG Startnummer ↔ Vereins-Mitglieds-ID                │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ 2. Core Business & Rule Engine                                        │  │
│  │    - Zuordnung der Schuss-Sequenzen (1-20 Pokal, 21-30 Fleischpreis)   │  │
│  │    - Berechnung: Ringe, Zehntel, Teiler, Handicap                     │  │
│  │    - Aggregation für Saisontabellen & Schießspiele                    │  │
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
| :--- | :--- | :--- |
| **Backend Framework** | **Python 3.11+ / FastAPI** | Hohe Performance, native `asyncio`-Unterstützung für den Poller, automatische OpenAPI-Dokumentation. |
| **ORM & DB-Access** | **SQLAlchemy 2.0 & pyodbc** | Universeller Lesezugriff auf die DISAG-Datenbank (MS SQL / LocalDB) sowie ORM für die eigene DB. |
| **Vereins-Datenbank** | **PostgreSQL** (oder SQLite) | Speicherung von Mitgliederdaten, Wettbewerben, Regelsätzen und aggregierten Ergebnissen. |
| **Frontend Framework** | **Angular 17+** | Single-Page-Application mit TypeScript für Schießleiter-Dashboard und Tabellen. |
| **Mobile Deployment** | **Capacitor** (`@capacitor/core`) | Hülle um das Angular-Frontend zur Bereitstellung als native Android-App (APK). |

---

## 4. Kernkomponenten & Modulbeschreibung

### 4.1. DISAG Ingestion Service (Worker)
* **Aufgabe:** Ein asynchroner Hintergrundprozess prüft alle $N$ Sekunden (z. B. 3s) die DISAG-Datenbank auf neue Schuss-Einträge.
* **Strategie:** Über einen variablen `last_processed_id`-Cursor werden nur neu hinzugekommene Schüsse eingelesen, um die Systemlast gering zu halten.

### 4.2. Core Business Engine (Regel- & Sequenzierungsauswertung)
* **Sequenzierer:** Unterteilt einlaufende Schusserien eines Schützen anhand vordefinierter Regeln.
  * Schuss 1–20 ➔ Zuweisung zur Kategorie **Pokal**
  * Schuss 21–30 ➔ Zuweisung zur Kategorie **Fleischpreis**
  * Schuss 31+ ➔ Zuweisung zu **Schießspielen / Glücksscheibe**
* **Aggregator:** Berechnet Best-of-$N$-Wertungen, Teiler-Differenzen sowie Saisontabellen über mehrere Schießabende.

### 4.3. REST & WebSocket API
* Bereitstellung aller Auswertungen, Standbelegungen und Mitgliedsdaten via REST-Endpunkte.
* WebSockets werden genutzt, um neue Schüsse live an die Bedienoberflächen (Web und App) zu streamen.

---

## 5. Relationales Datenmodell (Vereins-DB Schema)

```sql
-- Mitgliederstamm
CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    disag_start_number INT UNIQUE,
    active BOOLEAN DEFAULT TRUE
);

-- Wettbewerbe / Schießabende
CREATE TABLE competitions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    season VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    active BOOLEAN DEFAULT TRUE
);

-- Auswertungs-Regeln (Sequenzen)
CREATE TABLE evaluation_rules (
    id SERIAL PRIMARY KEY,
    competition_id INT REFERENCES competitions(id),
    shot_from INT NOT NULL,  -- z.B. 1
    shot_to INT NOT NULL,    -- z.B. 20
    target_category VARCHAR(50) NOT NULL -- z.B. 'POKAL', 'FLEISCHPREIS'
);

-- Verarbeitete Schussergebnisse
CREATE TABLE processed_shots (
    id SERIAL PRIMARY KEY,
    member_id INT REFERENCES members(id),
    competition_id INT REFERENCES competitions(id),
    shot_number INT NOT NULL,
    ring_value NUMERIC(4,1) NOT NULL,
    teiler NUMERIC(6,1) NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. Meilensteine & Roadmap

1. **Phase 1: Vorbereitung & DISAG-Analyse**
   * Analyse der Tabellenstruktur der lokalen DISAG-OpticScore-Datenbank.
   * Einrichtung der Linux-Entwicklungsumgebung mit Docker (PostgreSQL, Python, Node/Angular).
2. **Phase 2: Backend Core**
   * Implementierung der SQLAlchemy-Modelle und FastAPI-Endpunkte.
   * Entwicklung des asynchronen DISAG-Ingestion-Workers.
   * Umsetzung der Sequenz- und Regel-Engine.
3. **Phase 3: Angular Frontend**
   * Erstellung des Dashboards für Schießleiter (Standbelegung, Preisauswertung).
   * Einbindung von WebSockets für Live-Updates.
4. **Phase 4: Mobile App Target (Android)**
   * Integration von Capacitor in das Angular-Projekt.
   * Erstellung und Test des Android-APKs.