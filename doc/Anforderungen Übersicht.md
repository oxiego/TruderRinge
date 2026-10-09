# Anforderungen-Übersicht TruderRinge (v3.0)

**Projekt:** Nachfolgeanwendung für die Schützengesellschaft Gemütlichkeit Trudering e.V.
**Stand:** Oktober 2026

## 1. Zweck und Quellenbasis

Diese Übersicht fasst den fachlichen Umfang der Neuentwicklung zusammen. Maßgebliche fachliche Quelle ist [ANFORDERUNGEN_NEUENTWICKLUNG.md](./ANFORDERUNGEN_NEUENTWICKLUNG.md), das beobachtete Verhalten der LibreOffice-Base-Altanwendung beschreibt.

Die Datei [Schuetzen_sqlite_migration.sql](./Schuetzen_sqlite_migration.sql) ist ein SQLite-Export des HSQLDB-Bestands der Altanwendung. Sie belegt Tabellen, Spalten und vorhandene Beispieldaten für Mitglieder, Klassen, Saisons, Schießtage, Ergebnisse und Auswertungen. Sie ist **keine WM-Shot-`.wmk`-Datei** und beschreibt nicht deren internes Schema. Das SQL-Skript schaltet Fremdschlüsselprüfungen beim Import aus; sein Schema ist daher als Migrationsquelle, nicht als ungeprüftes Produktionsschema zu behandeln.

Anforderungen aus früheren Entwürfen zu wöchentlichen Moduswechseln, Standbelegung, Best-of-N, Android, Live-Import und frei konfigurierbaren Traditionswettbewerben sind nicht durch diese Bestandsquellen als bestehende Vereinsregeln bestätigt. Sie sind Erweiterungsoptionen und müssen vor einer Umsetzung fachlich beschlossen werden.

## 2. Fachlicher Kernumfang

TruderRinge verwaltet Mitglieder, LG-/LP-Teilnahmen, Saisons, Schießtage, saisonbezogene Klasseneinteilungen, Tagesergebnisse und die daraus erzeugten Vereinswertungen. LG und LP teilen sich Stammdaten und Saisonabläufe, bleiben aber fachlich unterscheidbare Disziplinen.

### FR-01 – Mitglieder und Stammdaten

- Mitglieder mit eindeutiger achtstelliger Pass-/Mitgliedsnummer, Vor- und Nachname, Geburtsdatum, Geschlecht und Aktivstatus verwalten.
- LG- und LP-Teilnahme, Fleischberechtigung je Disziplin, Hilfsmittel und Vorjahresschnitte abbilden.
- Bei Neuanlage während einer laufenden Saison die saisonbezogene Klasseneinteilung anbieten.
- Für noch unbekannte Nummern unterstützt der Altbestand temporäre Nummern ab `99999999`; Vergabe und spätere Ersetzung müssen nachvollziehbar sein.

### FR-02 – Saison und Klasseneinteilung

- Höchstens eine Saison ist aktiv. Die Saison hat Jahresbezeichnung, Beginn, Ende und getrennte Abschlussstatus für LG und LP.
- Klassen werden administrativ konfiguriert: Disziplin, Serienzahl, Jugend-/Damenmerkmale, Hilfsmittel, Fleischberechtigung, Einlage und Aktivstatus.
- Aktive und für LG bzw. LP gemeldete Mitglieder werden je Disziplin in Saisonklassen eingeteilt. Sondergruppen werden nur separat geführt, wenn dafür aktive Klassen bestehen.
- Allgemeine Klassen berücksichtigen den Vorjahresschnitt; die Klasseneinteilung vergibt saisonbezogene Nummern (LG ab 1, LP ab 81).
- Jugendgrenze, Klassendefinitionen und Verteilungsrandfälle sind vor Umsetzung mit dem Verein zu bestätigen.

### FR-03 – Schießtag und Fleischpreise

- Ein Schießtag gehört zu einer aktiven Saison, hat eine fortlaufende Nummer, ein Datum und einen Gesamtstatus für das Fleischschießen.
- Pro Datum darf nicht versehentlich ein zweiter Schießtag derselben Saison angelegt werden.
- Die Fleischpreis-Auswahl wird zusätzlich je Klasse gespeichert. Konfigurierte Fleisch-Tage je Klasse werden bei Auswahl berücksichtigt; ein globales Ein/Aus allein reicht fachlich nicht aus.
- Beim ersten Schießtag wird der Saisonbeginn gesetzt. Der Saisonabschluss verwendet das Datum des letzten Schießtages.
- Die Altanwendung schlägt den Fleischstatus gegenüber dem vorigen Schießtag alternierend vor. Regeln und manuelle Übersteuerung sind im Zielsystem sichtbar zu machen.

### FR-04 – Tagesergebnisse und Serien

- Tagesergebnisse werden getrennt für LG und LP erfasst und einem Mitglied, einer Saison, einem Schießtag und einer Disziplin zugeordnet.
- Die saisonbezogene Schützennummer dient in der Erfassung zur Auswahl; der Name wird zur Kontrolle angezeigt.
- Zahl der Serien richtet sich nach der Klasse. Der Bestand enthält bis zu vier zusammengefasste Serien und ein Gesamtergebnis sowie Rohdaten auf Serien-/Schussebene.
- In den vorliegenden Tabellen sind LG-Einzelschüsse für zehn Schüsse je Serie und LP-Einzelschüsse für fünf Schüsse je Serie angelegt. Ungeschossene Serien wurden im Altverhalten mit null aufgefüllt.
- Für Tagesergebnisse werden zusätzlich Pokal- und zweiter Programm-/Teilerwert geführt. Teiler-Randfälle und die Abhängigkeit vom Fleischstatus sind fachlich zu prüfen.
- Eingaben müssen unvollständige Serien, Nullwerte und auffällige Teiler verständlich behandeln. Ergebnisse müssen nach dem Speichern korrigierbar sein; Änderungen und Neuberechnungen dürfen nicht still erfolgen.

### FR-05 – Tagesauswertung und Preise

- Tagesauswertungen erzeugen LG-/LP-Ranglisten, Geldpreise, Pokalteiler und Fleischpreislisten je Schießtag und Klasse.
- Serienrangfolgen vergleichen die vier Serien in absteigender Reihenfolge als Tie-Breaker; Teilerwertungen sortieren den kleineren Teiler besser.
- Geldpreise berücksichtigen Klasse, Einlage, Jugendstatus und Teilnehmerzahl. Die Altformeln einschließlich Rundung und Randfällen sind vor Übernahme fachlich abzunehmen.
- Fleischpreis-Kandidaten berücksichtigen Fleischberechtigung und Klasse. Die Bestimmung nutzt erste Serie und Gesamtergebnis; Wiederholungsvermeidung und Gleichstände müssen gegen Vereinsbeispiele verifiziert werden.
- Eine Neuberechnung ersetzt die vorherigen Tages-Auswertungsdaten nicht unbemerkt: Auslöser, Zeitpunkt, Regelversion und geänderte Resultate sind nachvollziehbar.

### FR-06 – Saisonwertungen und Abschluss

- Je Disziplin werden Vereinsmeisterschaft/Jahresschnitt, Geldpreise, Pokalteiler, Königsschießen und Schmankerlpokal ausgewertet.
- LG-spezifisch kommen Diepold- und Röhrner-Wanderpokal hinzu. Saisonberichte führen unter anderem Schnitt, Vorjahresvergleich, Platzierungen und Preisresultate zusammen.
- Eine LG-Wertung setzt vorhandene Schießtage und mindestens ein LG-Ergebnis je Schießtag voraus. Eine LP-Wertung wird ausgeführt, wenn LP-Ergebnisse vorhanden sind.
- Der Saisonabschluss schreibt die aktuellen Schnitte als Vorjahresschnitte fort und deaktiviert die Saison. Das beobachtete Altverhalten verlangt abgeschlossene LG- und LP-Auswertungen; die gewünschte Behandlung einer nicht genutzten Disziplin ist zu bestätigen.
- Saisonlöschung ist eine gesonderte, destruktive Aktion und benötigt explizite Berechtigung, Bestätigung und Aufbewahrungsregeln.

### FR-07 – Sonderwettbewerbe und Berichte

- Im Bestand belegt sind Königsschießen und Schmankerlpokal (LG/LP), Pokalteiler und Vereinsmeisterschaft (LG/LP) sowie Diepold- und Röhrner-Wanderpokal (LG).
- Königsschießen trennt Jugend und Erwachsene; niedrigerer Teiler bedeutet bessere Platzierung. Teiler werden mit einer Nachkommastelle gespeichert.
- PDF-Berichte umfassen Schützenliste, Tagesergebnisse und Ranglisten, Fleischpreise, Klasseneinteilungen, Saison-Schützenberichte, Königsschießen, Schmankerlpokal, Wanderpokale und Saisonabschluss.
- Berichtspfade und Dateinamen sind konfigurierbar. Überschreiben und erneute Ausgabe müssen nachvollziehbar sein.
- Er-und-Sie-, Oster-, Martini-, Nikolaus- und weitere frei konfigurierbare Wettbewerbe sind mögliche Erweiterungen, nicht Bestandteil der belegten Bestandsbaseline.

### FR-08 – Migration und Betrieb

- Mitglieds-, Saison-, Schießtag-, Klassen-, Ergebnis-, Preis- und Berichtsdaten aus dem HSQLDB-Bestand müssen kontrolliert migrierbar sein.
- Der bereitgestellte SQLite-Export ist als Quelle zu prüfen und stichprobenartig gegen Altberichte abzugleichen. Temporäre `Temp_...`-Tabellen sind keine dauerhafte fachliche Historie.
- Eindeutigkeit und Beziehungen sind im Zielsystem mit Constraints durchzusetzen. Fehlerhafte oder verwaiste Quelldaten werden protokolliert und zur Klärung ausgewiesen.
- Personenbezogene Daten benötigen angemessene Zugriffsrechte, sichere Backups und ein geregeltes Aufbewahrungs-/Löschkonzept.
- Backup und vollständige Wiederherstellung müssen regelmäßig in einer Testumgebung überprüft werden.

## 3. Externe Ergebniserfassung

Der Bestands-SQL-Export und der externe Wettkampfimport sind getrennte Datenwege:

1. **WM-Shot `.wmk` nach Schießtag:** bevorzugter technischer Importweg, sofern eine reale Datei der eingesetzten Version die benötigten Daten verlässlich enthält. Zu prüfen sind Identität, Datum, Disziplin, Serie/Schussnummer, Ring- und Zehntelwerte, Teiler sowie Probe-/Wertungsschuss.
2. **OpticScore XML:** möglicher alternativer Offline-Import. Verfügbarkeit und Struktur für den konkreten WM-Shot-Wettkampf sind anhand eines realen Exports zu bestätigen.
3. **JSON-Live/DB-Poller:** nicht erforderlich für die beschriebene Tagesabschlussverarbeitung; nur nach bestätigtem Vereinsbedarf neu bewerten.

Der Import muss Vorschau, Validierung unbekannter oder mehrdeutiger Schützen, Fehlerbericht, Wiederholbarkeit und Herkunftsnachweis unterstützen. Fehlende Quellfelder dürfen nicht durch scheinbar gültige Standardwerte ersetzt werden. Eine 40-Schuss-Wertung darf erst als abgenommen gelten, wenn reale Importdaten mit der Referenzauswertung verglichen wurden.

## 4. Nichtfunktionale Anforderungen

- **Datenintegrität:** eindeutige Mitgliedsnummern, konsistente Saison-/Schießtagzuordnung und referenzielle Beziehungen.
- **Nachvollziehbarkeit:** Auditspur für Stammdatenkorrekturen, Ergebnisänderungen, Importläufe und Neuberechnungen.
- **Reproduzierbarkeit:** zentrale, versionierte Wertungsregeln und aus Quelldaten erneut erzeugbare Berichte.
- **Datenschutz:** rollenbasierte Zugriffe auf Geburtsdaten, Mitgliedsnummern und Ergebnisse.
- **Konfigurierbarkeit:** Klassen, Serien, Einlagen, Altersgrenzen, Fleischquoten, Preisregeln und Berichtspfade nicht in Code oder festen Betriebspfaden verstecken.
- **Betriebsfähigkeit:** dokumentierte Installation, Migration, Backup, Wiederherstellung und Fehlerbehebung.

## 5. Vor Umsetzung zu bestätigen

- Aktuelle Klassen, Jugendgrenze, LG-/LP-Serienzahl und Umgang mit unvollständigen Serien.
- Mindestteilnahme, Vereinsmeisterschaftsformel, Gleichstände und fehlende Schießtage.
- Geldpreisformeln, Rundung, Währungsformat und kleine/ungerade Teilnehmergruppen.
- Fleischpreis-Tie-Breaker, Kontingente und Regeln gegen wiederholte Gewinner.
- Gültige Korrekturen nach Tagesabschluss und Umgang mit bereits exportierten PDFs.
- Saisonabschluss, wenn nur eine Disziplin genutzt wurde; Saisonlöschung und Aufbewahrung.
- Rollen, Mehrbenutzerbetrieb, Backup-Aufbewahrung und Wiederherstellungsziel.
- Felder, Kennungen und Probe-/Wertungsschuss-Markierung im konkreten WM-Shot-/XML-Export.
- Ob Livebetrieb, Standbelegung, Wochen-Regelsets, Best-of-N oder weitere Traditionswettbewerbe tatsächlich benötigt werden.

## 6. Abnahmetests

- Nur eine Saison kann aktiv sein; Nummerierung und Klasseneinteilung sind je Disziplin stabil und korrekt.
- Ein Datum lässt keinen unbeabsichtigten doppelten Schießtag zu; Fleischstatus und Auswahl je Klasse bleiben unterscheidbar.
- LG- und LP-Serien ergeben nachvollziehbare Einzel-, Serien- und Gesamtergebnisse; ungültige oder fehlende Werte werden angezeigt.
- Tagesranglisten und Preisberechnungen stimmen für abgenommene Referenzfälle einschließlich Gleichständen und Randgrößen.
- Korrigierte Ergebnisse lassen sich mit dokumentierter Historie erneut auswerten; Berichte entsprechen den gespeicherten Eingaben.
- Saisonwertungen, Vorjahresschnitt-Fortschreibung und Abschluss stimmen für LG und LP mit Referenzfällen überein.
- Migration der gelieferten SQLite-Quelle ist reproduzierbar; Abweichungen und nicht auflösbare Beziehungen werden ausgewiesen.
- Ein realer WMK-/XML-Testimport wird auf Schützen, Datum, Serien, Schüsse, Teiler und Schussstatus gegen WM-Shot/OpticScore geprüft.
- PDFs landen im konfigurierten Ziel; ein Backup lässt sich vollständig in einer Testumgebung wiederherstellen.
