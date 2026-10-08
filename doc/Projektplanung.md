# Projektplanung TruderRinge

**Stand:** 08.10.2026  
**Grundlage:** `Anforderungen Übersicht.md` v2.2, `Anforderungen-Verein.md`, `Grundarchitektur.md` v2.0 und aktueller PoC-Stand.

## Ziel und Leitlinien

TruderRinge soll die bisherige Auswertung für die SG Gemütlichkeit Trudering ablösen. Der für den Verein beschriebene Kernablauf ist der Offline-Tagesabschluss: WM-Shot-Daten einlesen, Ergebnisse pro Schütze und Serie zuverlässig bilden, nach Vereinsregeln zuordnen und für Schießleitung und Saisonwertung bereitstellen.

Die Spezifikationen unterscheiden einen zwingenden fachlichen Bedarf von möglichen technischen Erweiterungen. Daher gilt folgende Priorität:

1. **WM-Shot `.wmk` nach dem Schießabend** als primärer Importweg.
2. **DISAG OpticScore XML** als alternativer Offline-Import, sobald das Dateiformat für den konkreten WM-Shot-Ablauf anhand eines realen Exports bestätigt ist.
3. **JSON-Live / Poller** ist optional und nachrangig. Die Vereinsspezifikation benötigt keine Echtzeitübertragung.

Der Browser-Prototyp enthält derzeit Bedienoberflächen für die Fachbereiche. Außer den bestehenden PoC-Endpunkten für WMK-Import und Ergebnislisten sind die dort angezeigten Daten und Aktionen noch nicht vollständig persistent oder serverseitig implementiert. Die Planung behandelt sie daher als UI-Prototyp, nicht als abgeschlossene Features.

## Zielbild und Abnahmekriterien

Ein Schießabend kann mit Mitgliedern, Klassen, Disziplinen und Standbelegung vorbereitet werden. Nach Abschluss kann eine reale WMK-Datei importiert werden; Schützen, Datum, Serien 1–4, Einzel-/Gesamtringe, Zehntel, Teiler und Probe-/Wertungsschüsse werden validiert, reproduzierbar gespeichert und gemäß Regelwerk zugeordnet. Wiederholte Importe erzeugen keine Duplikate. Die Schießleitung kann Klassenkontingente steuern, Ergebnisse nachvollziehen und Tages- sowie Saisonlisten exportieren. Sonderwettbewerbe sind regelbasiert konfigurierbar und auswertbar.

Vor Produktivbetrieb müssen mindestens zwei Testschützen mit 40 Schüssen gegen WM-Shot-Auswertung verifiziert werden. Abweichungen müssen bis zum Einzelschuss erklärbar sein. Backup/Wiederherstellung, Benutzerberechtigungen und Datenschutz für Mitgliederstammdaten sind geklärt.

## Umsetzungsreihenfolge

### Phase 0 – Anforderungen und Import verifizieren

**Epic E0: Fachliche und technische Verifikation**

- **Story E0.1 – Reale WMK-Testdatei analysieren:** Testwettkampf mit 2–3 Schützen und je 40 Schüssen durchführen; Schema, IDs, Datum, Serien-/Schussnummer, Ringe, Zehntel, Teiler sowie Probe-/Wertungsschuss dokumentieren. Abnahme: reproduzierbares Mapping und dokumentierte Grenzen für die tatsächlich eingesetzte WM-Shot-Version.
- **Story E0.2 – XML-Exportentscheidung treffen:** passenden OpticScore-Export erzeugen und mit WMK-Feldern vergleichen. Abnahme: XML wird als unterstützter Import priorisiert oder nachvollziehbar zurückgestellt.
- **Story E0.3 – Wertungsregeln verbindlich klären:** Klassen, Wochenwechsel, Kontingentverbrauch, Definition „Preis verschossen“, 40-Schuss-Serien, Sonderwertungen und Best-of-N fachlich bestätigen. Abnahme: versionierter Regelkatalog mit Beispielen und erwarteten Ergebnissen.

**Abhängigkeit:** E0.1 ist Voraussetzung für belastbare Import- und Datenmodellentscheidungen. Der Live-Import wird nicht begonnen, bevor ein realer Bedarf bestätigt ist.

### Phase 1 – Datenbasis und Backend-Grundlagen

**Epic E1: Wettbewerbe, Datenmodell und API-Grundlage**

- **Story E1.1 – Datenmodell auf Zielbild erweitern:** Wettbewerbe/Saisons, Mitgliederstatus und externe IDs, Klassenstatus/Kontingent, Roh-/verarbeitete Schüsse, Probe-Markierung und Zweierteams modellieren. Abnahme: Migrationen, Constraints und Beziehungen sind getestet.
- **Story E1.2 – Migrationen und Testdaten etablieren:** Schemaänderungen reproduzierbar ausrollen; Fixture-Daten verwenden. Abnahme: leere Datenbank kann vollständig erstellt und mit Tests befüllt werden.
- **Story E1.3 – API-Verträge definieren:** Ressourcen, Validierungen, Fehlerantworten, Paging/Filter und OpenAPI für Mitglieder, Wettbewerbe, Regeln, Standbelegung und Ergebnisse festlegen. Abnahme: Angular-Usecases sind ohne lokale Scheinpersistenz an die API anschließbar.
- **Story E1.4 – Konfiguration und Betrieb absichern:** DB-URL, Importpfade und CORS aus Konfiguration laden; strukturierte Logs, Healthcheck und sichere Standardkonfiguration ergänzen.

### Phase 2 – Import und fachliche Wertung

**Epic E2: Verlässlicher WM-Shot-Tagesabschlussimport**

- **Story E2.1 – WMK-Reader gegen reale Dateien stabilisieren:** Dateiversion/Tabellen erkennen und erforderliche Felder extrahieren. Abnahme: Testdateien und ungültige/unterstützte Versionen sind automatisiert getestet.
- **Story E2.2 – Importvorschau und Validierung bereitstellen:** Datei und Schießdatum prüfen; unbekannte Schützen, fehlende Felder, Probe- und Wertungsschüsse vor Commit nachvollziehbar anzeigen. Abnahme: Fehlerhafte Datensätze werden nicht stillschweigend verschluckt.
- **Story E2.3 – Idempotenten Import implementieren:** Importlauf und Quelle protokollieren; Wiederholung derselben Datei verändert Ergebnisse nicht doppelt. Abnahme: Import kann sicher wiederholt und bei Fehlern diagnostiziert werden.
- **Story E2.4 – Serien- und Gesamtergebnisse berechnen:** vier 10er-Serien und Gesamtwerte mit ganzen Ringen, Zehnteln und bestem Teiler je Serie berechnen. Abnahme: Werte stimmen mit WM-Shot-Referenzauswertung überein.
- **Story E2.5 – XML-Offlineimport ergänzen (bedingt):** Adapter erst nach E0.2 erstellen; gemeinsames kanonisches Schussformat mit WMK nutzen. Abnahme: dieselben fachlichen Validierungen und Importberichte wie WMK.

**Nicht Teil des MVP:** JSON-Live/UDP/WebSocket-Poller; die Vereinsspezifikation fordert keine Live-Daten.

**Epic E3: Regel-Engine, Klassenstatus und Kontingente**

- **Story E3.1 – Regelmodell und Wochenwechsel implementieren:** Regelset nach Saison, Schießdatum/Woche, Klasse und Disziplin auflösen. Abnahme: ungerade/gerade Woche sowie manuelle Overrides sind deterministisch.
- **Story E3.2 – Schuss 1–20 zuordnen:** aktives Fleischpreiskontingent führt zur Teilerwertung, andernfalls Pokal zu Ringen/Zehnteln. Abnahme: Grenzfälle und Klassenunabhängigkeit sind getestet.
- **Story E3.3 – Kontingentverbrauch und Moduswechsel abbilden:** Verbrauch manuell oder regelbasiert verwalten, Stop bestätigen und Auditspur führen. Abnahme: eine Klasse kann wechseln, ohne den Modus anderer Klassen zu ändern.
- **Story E3.4 – Folge- und Sonderbereiche zuordnen:** Schuss 21–30 konfigurierbar für Pokal/Vortag/Preis; Schuss 31+ für Schießspiele/Glücksscheibe. Teilerfaktoren je Disziplin berücksichtigen.

### Phase 3 – Stammdaten und Schießabendbetrieb

**Epic E4: Mitglieder, Klassen und Standbelegung**

- **Story E4.1 – Mitgliederverwaltung bereitstellen:** Name, Geburtsdatum, Status, Standardklasse und Disziplin pflegen; suchen/filtern. Abnahme: Validierung und Deaktivierung statt destruktivem Löschen.
- **Story E4.2 – Externe IDs zuordnen:** interne Vereins-ID mit DISAG-Startnummer/Chip und WM-Shot-ID verbinden; Dubletten verhindern und Konflikte anzeigen.
- **Story E4.3 – Klassen und Disziplinen verwalten:** Klassen-/Disziplinstammdaten versioniert und referenziell konsistent halten.
- **Story E4.4 – Schießabend anlegen und vorbereiten:** Datum, Saison und Regelset festlegen; Klassenstatus/Kontingent initialisieren.
- **Story E4.5 – Standbelegung verwalten:** Schütze auf freien DISAG-Stand setzen, umsetzen und freigeben; aktuellen Klassenmodus vor Anmeldung anzeigen.

### Phase 4 – Auswertung und Traditionsschießen

**Epic E5: Tages- und Saisonauswertung**

- **Story E5.1 – Fleischpreis-Tagesliste erstellen:** beste Teiler sortiert und nachvollziehbar je Klasse/Schießabend anzeigen.
- **Story E5.2 – Pokal- und Serienauswertung erstellen:** Serien 1–4 und Gesamtwerte je Schütze und Abend darstellen.
- **Story E5.3 – Saisonkonto und Best-of-N berechnen:** Schießabende je Klasse aggregieren, N beste Ergebnisse zählen und Streichergebnisse transparent markieren.
- **Story E5.4 – Listen exportieren und drucken:** CSV mindestens für Weiterverarbeitung; druckbarer Aushang/PDF für Tages- und Saisonlisten.

**Epic E6: Sonder- und Traditionsschießen**

- **Story E6.1 – Wettbewerbe konfigurieren:** Typ, Datum, Schusslimit, Scheibe und Wertungsschlüssel für König, Gaudi, Er-und-Sie, Ostern, Martini und Nikolaus verwalten.
- **Story E6.2 – Königsschießen verdeckt auswerten:** beste Teiler geheim halten bis zur Freigabe; Rollen-/Anzeigekonzept beachten.
- **Story E6.3 – Gaudi- und Vorgabewertung umsetzen:** Vorgabeteiler, Differenzen und Glücksscheiben-Regeln abbilden.
- **Story E6.4 – Er-und-Sie-Paare bilden und werten:** manuelle/Zufallspaarung und kombinierte Ringe-/Teilerwertung mit Teamrangliste.
- **Story E6.5 – Osterschießen limitieren:** Spezialschüsse pro Teilnehmer strikt begrenzen und Motiv-/Scheibenzuordnung speichern.
- **Story E6.6 – Martinischießen werten:** bester Teiler und beste Deckserie gemäß bestätigter Regel kombinieren.
- **Story E6.7 – Nikolausschießen abschließen:** Preisschlüssel konfigurieren und Platzierungen direkt ausgeben.

### Phase 5 – Bedienoberfläche, Qualität und Einführung

**Epic E7: Angular-Frontend produktionsreif anbinden**

- **Story E7.1 – Prototyp an echte API anbinden:** lokale Entwurfszustände durch Laden/Speichern, Ladezustände, Fehler und Berechtigungen ersetzen.
- **Story E7.2 – Importworkflow für Leitung fertigstellen:** Dateiupload, Vorschau, Validierung, Bestätigung und Importbericht integrieren.
- **Story E7.3 – Navigation und Formulare barrierefrei/responsiv prüfen:** PC/Tablet und schmale Displays, Tastatur, Labels und verständliche Statusmeldungen testen.
- **Story E7.4 – Dashboard und Aushang optimieren:** Tagesstatus, Klassenkontingente, Standbelegung und exportierbare Ergebnislisten.

**Epic E8: Test, Betrieb und optionale Plattformen**

- **Story E8.1 – Fachliche Testmatrix automatisieren:** Import, Regelgrenzen, Serien, Kontingente, Saisonwertung und Sonderwettbewerbe mit Referenzfällen testen.
- **Story E8.2 – Abnahme mit Testwettkampf durchführen:** 2–3 Testschützen × 40 Schuss, Soll-/Istvergleich mit WM-Shot, dokumentierte Freigabe.
- **Story E8.3 – Backup, Wiederherstellung und Datenschutz abnehmen:** Aufbewahrung, Zugriff, Rollen und Wiederherstellungsprobe dokumentieren.
- **Story E8.4 – Linux-Deployment und Monitoring dokumentieren:** Installation, Updates, Migration, Logs und Fehlerbehebung reproduzierbar beschreiben.
- **Story E8.5 – Capacitor/Android bewerten (optional):** erst nach stabiler Web/API-Basis entscheiden, ob eine native Schützen-App benötigt wird.
- **Story E8.6 – Live-Fallback bewerten (optional):** nur bei nachgewiesenem Bedarf und nach Prüfung der offiziellen DISAG-Schnittstelle planen.

## Abhängigkeiten und kritischer Pfad

`E0.1 → E1 → E2.1–E2.4 → E3 → E4.4/E4.5 → E5 → E7 → E8.2/E8.3`.

XML hängt von E0.2 ab und ist keine Voraussetzung für den ersten nutzbaren Offlinebetrieb. Sonderwettbewerbe können parallel zu E5 entwickelt werden, sobald Datenmodell und Regelbasis aus E1/E3 stehen. Android und Live-Poller sind explizite spätere Optionen, keine MVP-Blocker.

## MVP-Vorschlag

Der erste abnahmefähige Vereinsbetrieb umfasst E0, E1, WMK-Import E2.1–E2.4, Kernregeln E3.1–E3.3, Mitglieder/Zuordnung/Standbelegung E4.1–E4.5, Tages- und Pokalauswertung E5.1–E5.2 sowie die nötigen API-angebundenen Angular-Flows aus E7.1–E7.3. Saison-Best-of-N, Traditionswettbewerbe, PDF, XML und Android können danach priorisiert werden; die Reihenfolge innerhalb dieser Nachfolgepakete wird mit der Schießleitung bestätigt.

## Risiken und offene Entscheidungen

| Thema | Risiko / offene Frage | Maßnahme |
| --- | --- | --- |
| WMK-Schema | Internes, versionsabhängiges Format | Reale Dateien mehrerer Versionen analysieren; unterstützte Versionen festlegen |
| XML für WM-Shot-Wettkämpfe | Verfügbarkeit im konkreten Ablauf unklar | Testexport und Hersteller-/Vereinsverifikation vor Implementierung |
| Kontingentverbrauch | „Preis verschossen“ nicht technisch eindeutig definiert | Vereinsregel und manuelle Override-Semantik festlegen |
| Wertungsmodell | Ringwert/Zehntel können Serien-/Schusswerte unterschiedlich repräsentieren | Kanonisches Datenmodell anhand Referenzauswertung spezifizieren |
| Stammdaten | Personenbezogene Daten inkl. Geburtsdatum | Zugriffe, Minimaldaten, Backups und Aufbewahrung klären |
| Live-Funktion | Höhere Betriebs- und Schnittstellenkomplexität, derzeit kein Vereinsbedarf | Aus dem MVP ausschließen, später nur bei Bedarf neu bewerten |

## Issue-Aufteilung für GitHub

Die Epics und Stories wurden als Issues im Repository [oxiego/TruderRinge](https://github.com/oxiego/TruderRinge/issues) angelegt. GitHubs native Sub-issue-Beziehungen bilden die Hierarchie ab.

| Epic | GitHub-Issue | Zugeordnete Story-Issues |
| --- | --- | --- |
| E0 – Fachliche und technische Verifikation | [#1](https://github.com/oxiego/TruderRinge/issues/1) | #2–#4 |
| E1 – Datenmodell und Backend-Grundlagen | [#5](https://github.com/oxiego/TruderRinge/issues/5) | #13–#16 |
| E2 – WM-Shot-Tagesabschlussimport | [#6](https://github.com/oxiego/TruderRinge/issues/6) | #17–#21 |
| E3 – Rule Engine, Klassenstatus und Kontingente | [#7](https://github.com/oxiego/TruderRinge/issues/7) | #22–#25 |
| E4 – Mitglieder, Klassen und Standbelegung | [#8](https://github.com/oxiego/TruderRinge/issues/8) | #26–#30 |
| E5 – Tages- und Saisonauswertung | [#9](https://github.com/oxiego/TruderRinge/issues/9) | #31–#34 |
| E6 – Sonder- und Traditionsschießen | [#10](https://github.com/oxiego/TruderRinge/issues/10) | #35–#41 |
| E7 – Angular-Frontend produktionsreif anbinden | [#11](https://github.com/oxiego/TruderRinge/issues/11) | #42–#45 |
| E8 – Test, Betrieb und optionale Plattformen | [#12](https://github.com/oxiego/TruderRinge/issues/12) | #46–#51 |

Insgesamt wurden 9 Epics und 42 Stories (51 Issues) angelegt. Die Story-Issues enthalten eigene Ziele und Abnahmekriterien; die Epic-Issues fassen Ziel, Abnahme und Storyumfang zusammen.
