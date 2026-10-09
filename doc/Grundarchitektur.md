# Grundarchitektur TruderRinge (v3.0)

**Projekt:** Nachfolgeanwendung für die Schützengesellschaft Gemütlichkeit Trudering e.V.
**Stand:** Oktober 2026
**Laufender PoC:** FastAPI-Backend und Angular-Frontend

## 1. Architekturziele und Quellenabgrenzung

Die Zielarchitektur bildet die belegten Abläufe der Altanwendung ab: Mitglieder- und Klassenverwaltung, Saison, Schießtag, LG-/LP-Ergebnisse, Tages-/Saisonwertungen und Berichte. Wertungsregeln sind zentral, testbar und versionierbar.

Es gibt zwei unterschiedliche Eingangswege:

- **Altbestandsmigration:** [Schuetzen_sqlite_migration.sql](./Schuetzen_sqlite_migration.sql) ist ein SQLite-Export der alten HSQLDB-Anwendung. Er dient zur Datenübernahme und Validierung der historischen Tabellen.
- **Wettkampfergebnisse:** WM-Shot-`.wmk` ist als Offline-Import vorgesehen, sein konkretes Dateischema muss jedoch gegen reale Dateien verifiziert werden. OpticScore-XML ist eine bedingte Alternative.

Der Altbestands-SQL-Export ist kein WMK-Beispiel. Er beweist daher weder Verfügbarkeit noch Bedeutung von Feldern wie Probe-/Wertungsschuss, Zeitstempel oder Zehntelwerten in einem WMK-Export. Der JSON-Live-Listener ist für den beschriebenen Tagesabschluss nicht erforderlich.

## 2. Systemkontext und Datenfluss

```text
HSQLDB / LibreOffice-Base-Altbestand
               │
               ▼
     SQLite-Export / Migrationsadapter
               │
               ├────────────────────────────────┐
                                                ▼
WM-Shot .wmk ──► WMK-Adapter (nach Verifikation) ──► Importvorschau / Validierung
OpticScore XML ► XML-Adapter (optional, bestätigt) ─► Importvorschau / Validierung
                                                │
                                                ▼
                               Kanonisches TruderRinge-Datenmodell
                                                │
                    ┌───────────────────────────┼──────────────────────────┐
                    ▼                           ▼                          ▼
            Fachliche Dienste             REST API                 Berichte / PDF
       (Saison, Tageswertungen,     (FastAPI / Pydantic)        (Tages- und Saison-
        Saisonwertungen, Preise)             │                    auswertungen)
                                             ▼
                                    Angular-Weboberfläche
```

Jeder Eingangsadapter bleibt von der Fachlogik getrennt. Vor dem Speichern werden Identität, Saison/Schießtag, Disziplin, Klasse und Ergebnisdaten validiert. Konflikte oder fehlende Felder werden angezeigt und protokolliert; ein unbekannter Quellwert wird nicht stillschweigend in ein gültiges Ergebnis umgewandelt.

## 3. Anwendungsschichten

### 3.1 Eingangsadapter und Migration

- Der **Altbestandsadapter** liest die Tabellen des SQLite-Exports, ordnet historische Schlüssel zu und berichtet verwaiste oder widersprüchliche Beziehungen. Temporäre `Temp_...`-Tabellen sind keine dauerhaften fachlichen Entitäten.
- Der **WMK-Adapter** arbeitet zunächst lesend und unterstützt nur nachgewiesene Dateiversionen. Der Import wird als eigener Lauf mit Dateiquelle, Prüfergebnis und Importstatus gespeichert.
- Der **XML-Adapter** wird nur implementiert, wenn ein realer Export für den WM-Shot-Ablauf zur Verfügung steht und mit dem kanonischen Modell abbildbar ist.
- Ein Importlauf bietet Vorschau, Dublettenprüfung, Konfliktauflösung und Wiederholung ohne Duplikate.

### 3.2 Fachlicher Kern

Der Fachkern enthält voneinander testbare Dienste für:

- Saisonstart, Einteilung, Schießtag und Saisonabschluss.
- LG-/LP-Erfassung, Serien-/Gesamtergebnisse und Korrekturen.
- Tagesranglisten, Geldpreise, Fleischpreise und Teilerwertungen.
- Vereinsmeisterschaft/Jahresschnitt, Vorjahresvergleich und Saisonpreise.
- Königsschießen, Schmankerlpokal, Pokalteiler sowie LG-Diepold- und LG-Röhrner-Wanderpokal.
- Berichtsaufbereitung.

Klassen- und Preisregeln kommen aus versionierter Konfiguration, nicht aus Importadaptern. Obsolete oder ungeklärte Regeln (z. B. Gleichstände, Rundung und fehlende Disziplin am Saisonabschluss) werden nicht durch einen technischen Standardwert entschieden.

### 3.3 API und Bedienoberfläche

FastAPI/Pydantic stellt die validierten Domänenoperationen bereit. REST-Endpunkte sollen Saison, Mitglieder, Klassen, Schießtage, Ergebnisse, Importläufe, Auswertungen und Berichte abbilden. API-Fehler sind für die Angular-Anwendung strukturiert und verständlich.

Angular ist die primäre Bedienoberfläche für Schießleitung und Vereinsverwaltung. Aktionen für Import, Korrektur, Neuberechnung und Saisonlöschung benötigen geeignete Bestätigung, Statusanzeige und Fehlerdarstellung. WebSockets oder eine Android-Hülle sind keine Voraussetzungen des fachlichen Kerns.

### 3.4 Persistenz

Die Zielpersistenz hält Stammdaten, historische Saison-/Schießtagzuordnungen, Detail- und Summenergebnisse, Auswertungsresultate, Importherkunft und Auditdaten dauerhaft. Die konkrete Datenbankwahl (SQLite oder PostgreSQL) ist anhand Betriebsort, Mehrbenutzerzugriff, Backup und Wiederherstellung festzulegen; der SQLite-Export allein entscheidet diese Architekturfrage nicht.

Die gelieferten Tabellen sind ein Migrationsformat, kein direktes Zielschema: Im Export ist `PRAGMA foreign_keys = OFF` gesetzt, LG-/LP-Tabellen wiederholen viele Strukturen und einzelne temporäre bzw. historische Tabellen dienen technischen oder berichtsbezogenen Zwecken. Zielconstraints werden daher explizit definiert und beim Import geprüft.

## 4. Kanonisches fachliches Datenmodell

Die Zielstruktur soll mindestens folgende Entitäten unterscheiden:

| Entität | Zweck und wesentliche Beziehungen |
| --- | --- |
| **Mitglied** | Eindeutige Vereins-/Passnummer, Name, Geburtsdatum, Geschlecht, Aktivstatus, Vorjahresschnitte und Teilnahme-/Berechtigungsmerkmale |
| **Disziplin** | LG oder LP; erhält fachlich getrennte Klassen, Ergebnisse und Auswertungen |
| **Klasse** | Bezeichnung, Serienzahl, Disziplin, Jahrgangs-/Jugend- und Damenmerkmale, Hilfsmittel, Fleischberechtigung, Einlage und Aktivstatus |
| **Saison** | Jahresbezeichnung, Beginn/Ende, aktiver Status und getrennte LG-/LP-Auswertungsstatus |
| **Saison-Einteilung** | Mitglied, Saison, Disziplin, saisonbezogene Schützennummer und Klasse |
| **Schießtag** | Saison, fortlaufende Nummer, Datum, Fleischstatus; Klassenwahl je Tag separat |
| **Tagesergebnis** | Mitglied, Saison, Schießtag, Disziplin, Zusammenfassungen für Serien/Gesamt und Pokal-/Zusatzteiler |
| **Serie und Einzelschuss** | Geordnete Schüsse einer Serie mit Ring-/Zehntel-/Teilerwerten und – sofern die Quelle sie liefert – Koordinaten und Schussstatus |
| **Wertungslauf und Preisresultat** | Eingaben, Regelversion, Rangfolge, Betrag/Preis, Berechnungszeit und Herkunft |
| **Sonderwettbewerb** | Saisonbezogene Teilnahme/Teiler und Rangfolge der im Bestand belegten Wettbewerbe |
| **Importlauf und Auditereignis** | Quelle, Schlüssel/Datei, Mapping, Status, Fehler, Änderungen und verantwortliche Aktion |

### Abbildung des Altbestands

Der SQLite-Export enthält unter anderem:

- **Stamm/Konfiguration:** `Schuetzen`, `Schuetzenliste`, `Schuetzenklassen`, `Saison`.
- **Betrieb:** `Schiesstage`, `LG_Einteilung_Klassen`, `LP_Einteilung_Klassen`.
- **Ergebnisse:** `LG_Ergebnisse_Schiesstag`, `LP_Ergebnisse_Schiesstag`, `LG_Serien`, `LP_Serien`, `LG_Jahresschnitt`, `LP_Jahresschnitt`.
- **Auswertungen:** Geldpreis-, Fleischpreis-, Vereinsmeister-, Königsschießen-, Schmankerlpokal-, Pokalteiler- und Wanderpokal-Tabellen sowie `LG_Schuetzen_Bericht`/`LP_Schuetzen_Bericht`.

Die Legacy-Tabellen speichern LG und LP überwiegend getrennt. `LG_Serien` enthält bis zu zehn Schüsse je Serie und `LP_Serien` fünf; Schussringe, Teiler und teilweise X-/Y-Koordinaten sind vorhanden. Das Altformat belegt nicht automatisch, dass WMK dieselben Felder, Schlüssel oder Schussstatuswerte liefert. Ein vereinheitlichtes Zielschema ist zulässig, sofern Disziplin und historische Ausgabe getrennt reproduzierbar bleiben.

## 5. Integrationsverträge für Schussergebnisse

Ein kanonischer Schussdatensatz soll, soweit die Quelle diese Angaben liefert, enthalten:

- externe Schützenkennung und aufgelöste interne Mitglieds-ID;
- Saison/Schießtag oder eine vorläufige Wettkampfzuordnung;
- Disziplin, Serie und Schussnummer;
- Ringwert und Zehntelwert als getrennte fachliche Werte;
- Teiler, falls geliefert;
- Probe-/Wertungsschuss-Kennzeichnung, falls geliefert;
- optionale Quellzeit und Koordinaten;
- Importlauf und unveränderte Quellreferenz.

Die Integrationsprüfung muss klären, wie Gesamtwerte aus Quellwerten gebildet werden und ob die Quelldaten Serien oder Einzelresultate eindeutig markieren. Zeiten, Koordinaten oder Schussstatus sind optional, bis ein realer Export sie bestätigt. Nicht vorhandene Felder dürfen nicht als Pflichtwerte ohne fachliche Begründung modelliert werden.

## 6. Wertung, Korrektur und Reproduzierbarkeit

- Rohdaten und berechnete Ranglisten/Preisresultate sind logisch unterscheidbar.
- Fachregeln erhalten eine Version; jeder Wertungslauf verweist auf die verwendete Version und Eingangsdaten.
- Eine Korrektur invalidiert oder markiert betroffene Auswertungen als veraltet und ermöglicht eine explizite Neuberechnung.
- Neuberechnungen überschreiben Ergebnisse nicht unprotokolliert. Vorher-/Nachher-Ergebnis und Auslöser bleiben nachvollziehbar.
- Tages- und Saisonberichte werden aus gespeicherten und validierten Daten erzeugt. Exportpfad und Dateinamen sind konfigurierbar.

## 7. Betrieb, Sicherheit und Netzwerkgrenzen

- Backend: Linux-Host; bestehender PoC nutzt FastAPI/Python. Frontend: Angular-Webanwendung.
- Datenbank, Berichtsablage und Backup-Ziele werden konfiguriert, nicht in Quellcode oder Benutzerpfade eingebaut.
- Der externe `.wmk`-Zugriff erfolgt im MVP als kontrollierter Offline-Dateiimport. Schreibender Zugriff auf WM-Shot oder DISAG ist nicht vorgesehen.
- Kein permanenter UDP-/WebSocket-Listener und kein Polling der DISAG-Datenbank ohne beschlossenen Echtzeitbedarf und bestätigte Schnittstelle.
- Personenbezogene Daten sind nach Rollen zu schützen. Datenexporte und Backups sind in Zugriff und Aufbewahrung einzubeziehen.
- Backup umfasst einen dokumentierten Restore-Test; Archivdateien allein gelten nicht als abgenommene Wiederherstellung.

## 8. Qualitäts- und Architekturentscheidungen

Vor Umsetzung sind zu bestätigen:

1. Datenbankprodukt und Mehrbenutzer-/Deploymentmodell.
2. Fachliche Formeln, Gleichstände, Jugend-/Klassenregeln und Saisonabschlussbedingungen.
3. Minimal erforderliche Einzelschussfelder und Umgang mit nicht gelieferten Probe-/Wertungsschussmarkierungen.
4. Verfügbarkeit und Versionen von WMK bzw. XML im realen Schießbetrieb.
5. Benutzerrollen, Aufbewahrung und Umfang des Auditprotokolls.

Abnahmekriterien sind die Datenmigration gegen Referenzberichte, reproduzierbare LG-/LP-Wertungen, explizite Importvalidierung, stabile Korrektur-/Neuberechnungshistorie und ein erfolgreich ausgeführter Restore-Test.

## 9. Nicht Bestandteil der bestätigten Baseline

Wochenweise Regelsets, automatische Kontingentumschaltung für Schuss 1–20, DISAG-Standbelegung, Best-of-N/Streichergebnisse, Live-Poller, Capacitor/Android und Er-und-Sie-/Oster-/Martini-/Nikolauswettbewerbe bleiben optionale Erweiterungen. Ihre Aufnahme erfordert eine fachliche Entscheidung und eigene Abnahmekriterien.
