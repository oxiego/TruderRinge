# Projektplanung TruderRinge

**Stand:** 09.10.2026
**Grundlage:** [Anforderungen Übersicht.md](./Anforderungen%20Übersicht.md), [ANFORDERUNGEN_NEUENTWICKLUNG.md](./ANFORDERUNGEN_NEUENTWICKLUNG.md), [Schuetzen_sqlite_migration.sql](./Schuetzen_sqlite_migration.sql) und aktueller PoC-Stand.

## Ziel und Leitlinien

TruderRinge soll die bisherige LibreOffice-Base-Anwendung für die SG Gemütlichkeit Trudering ablösen. Der belastbare fachliche Kern ist der Saison- und Schießtagbetrieb mit Mitgliedern, LG-/LP-Klasseneinteilung, Ergebniserfassung, Tages- und Saisonwertungen sowie Berichten.

Die Projektplanung trennt drei Aufgaben, die nicht miteinander verwechselt werden dürfen:

1. **Altbestandsmigration:** Das bereitgestellte SQLite-SQL-Exportskript stammt aus der bisherigen HSQLDB-Anwendung und belegt deren Tabellen und vorhandene Resultate.
2. **Schießtag-Import:** WM-Shot-`.wmk` oder OpticScore-XML sind externe Quellen für künftige Wettkampfergebnisse. Ihr konkretes Schema und ihre Feldbelegung sind noch mit realen Dateien zu verifizieren.
3. **Optionale Erweiterungen:** Live-Daten, Standbelegung, wöchentliche Moduswechsel, Best-of-N, Android und weitere Traditionswettbewerbe sind keine bestätigte MVP-Basis.

Der vorhandene PoC umfasst laut Projekt-README ein FastAPI-Backend und Angular-Frontend. Bedienoberflächen oder PoC-Endpunkte gelten erst dann als fertig, wenn Daten dauerhaft gespeichert, validiert und über die API nachvollziehbar bearbeitet werden.

## Zielbild und Abnahmekriterien

Ein Vereinsverantwortlicher kann eine Saison eröffnen, Mitglieder und LG-/LP-Klasseneinteilung pflegen, Schießtage anlegen, Ergebnisse erfassen oder aus einer bestätigten Importquelle übernehmen und Tages- sowie Saisonwertungen erzeugen. Ergebnisse und Auswertungen lassen sich korrigieren und reproduzieren. Berichte können sicher exportiert werden.

Die fachlichen Abnahmekriterien umfassen:

- Kontrollierte Migration der Altbestandsdaten mit Abgleich gegen ausgewählte Altberichte.
- LG-/LP-Tages- und Saisonabläufe einschließlich Serien, Teiler, Fleischpreisen, Geldpreisen und belegten Sonderwertungen.
- Verifizierter Import einer realen WM-Shot-Datei, falls dieser Import als MVP-Zugang beschlossen wird; SQL-Exportdaten gelten nicht als Ersatz für WMK-Testdaten.
- Verständliche Fehlerbehandlung, Auditspur, Datenschutz, Backup und erfolgreich getestete Wiederherstellung.
- Vor Produktivbetrieb bestätigt die Schießleitung offene Vereinsregeln und Referenzergebnisse.

## Umsetzungsreihenfolge

### Phase 0 – Fachregeln, Datenquellen und Betrieb verifizieren

**Epic E0: Abnahmegrundlagen**

- **E0.1 – Fachregeln bestätigen:** LG-/LP-Klassen, Jugendgrenze, Serienzahlen, Preisregeln, Fleischvergabe, Saisonabschluss und Korrekturablauf mit konkreten Referenzfällen festhalten.
- **E0.2 – SQLite-Altbestand profilieren:** Tabellen, Schlüssel, Datenqualität und Verknüpfbarkeit des gelieferten Exports prüfen. Beispielmigration gegen Altberichte und erwartete Datensätze abgleichen.
- **E0.3 – WM-Shot-Import testen:** Testwettkampf mit realen Dateien der eingesetzten Version durchführen. Schützen-ID, Datum, Wertungsschüsse, Serien, Ring-/Zehntelwerte und Teiler nachweisen; Probe-/Wertungsschuss-Markierung gesondert prüfen.
- **E0.4 – XML-Eignung entscheiden:** OpticScore-XML nur dann als Adapter einplanen, wenn es für den tatsächlichen WM-Shot-Ablauf exportierbar ist und benötigte Felder enthält.
- **E0.5 – Betrieb und Datenschutz festlegen:** Einsatzort, Nutzerrollen, DB-Betriebsmodell, Berichtsablage, Aufbewahrung sowie Backup-/Restore-Ziel entscheiden.

**Gate:** Ungeklärte Wertungsregeln blockieren die fachliche Berechnung; nicht verfügbare WMK-Felder blockieren nur den WMK-Import, nicht die Altbestandsmigration oder manuelle Erfassung.

### Phase 1 – Zielmodell und Migration

**Epic E1: Datenbasis**

- **E1.1 – Domänenmodell entwerfen:** Mitglieder, Disziplinen, Klassen, Saison, Saisonklasseneinteilung, Schießtag, Ergebnisse, Serien/Einzelschüsse, Wettbewerbe, Preise und Berichte abbilden.
- **E1.2 – LG/LP-Strukturen vereinheitlichen:** Wiederholte LG-/LP-Tabellen können intern über eine Disziplin-Dimension vereinheitlicht werden; Exporte und historische Ansichten behalten die Trennung bei.
- **E1.3 – Constraints und Migrationen erstellen:** Eindeutigkeit und Beziehungen verbindlich absichern. Die Altmigration mit Fremdschlüsselprüfungen, Fehlerbericht und deterministischem Wiederholungslauf versehen.
- **E1.4 – Herkunft und Historie speichern:** Quell-ID/Datei, Importlauf, Zeitstempel, Regelversion, manuelle Korrekturen und Neuberechnungen nachvollziehbar halten.

### Phase 2 – Mitglieder, Saisons und Schießtagbetrieb

**Epic E2: Fachliche Grundabläufe**

- **E2.1 – Mitgliederverwaltung:** Stammdaten, Aktivstatus, Disziplinteilnahme, Fleischberechtigung und Hilfsmittel pflegen; temporäre Mitgliedsnummern sicher behandeln.
- **E2.2 – Saison und Klassen:** Saison eröffnen/abschließen, Klassen konfigurieren und LG-/LP-Einteilungen einschließlich saisonbezogener Schützennummern erzeugen.
- **E2.3 – Schießtag:** Datum, fortlaufende Nummer und Gesamt-/Klassen-Fleischstatus erfassen; Duplikate verhindern.
- **E2.4 – Manuelle Ergebniserfassung:** LG-/LP-Ergebnisse gemäß Klassen-Serienzahl eingeben, prüfen und mit kontrolliertem Korrekturpfad speichern.

### Phase 3 – Tagesauswertung und Fachregeln

**Epic E3: Tageswertungen**

- **E3.1 – Serien und Gesamtergebnis berechnen:** Serien-/Schussdaten und Zusammenfassungen konsistent auswerten; Nullauffüllung und Teiler-Randfälle gemäß bestätigter Regel behandeln.
- **E3.2 – Fleischpreise:** Klassenauswahl, Teilnahmeberechtigung, Rangfolge, Preise und Wiederholungsvermeidung abbilden.
- **E3.3 – Geldpreise und Pokal:** LG-/LP-Rangfolgen, Tie-Breaker, Jugend-/Hilfsmittelbehandlung und bestätigte Betragsformeln implementieren.
- **E3.4 – Rechenläufe versionieren:** Tagesauswertung reproduzierbar machen; Neuberechnung, Eingaben und Resultatänderungen protokollieren.

### Phase 4 – Saisonwertungen und Berichte

**Epic E4: Saisonabschluss und Ausgabe**

- **E4.1 – Saisonwertungen umsetzen:** Vereinsmeisterschaft/Jahresschnitt, Vorjahresvergleich, Saison-Geldpreise und Pokalteiler je Disziplin.
- **E4.2 – Bestandswettbewerbe ergänzen:** Königsschießen und Schmankerlpokal für LG/LP sowie Diepold- und Röhrner-Wanderpokal für LG nach bestätigten Regeln.
- **E4.3 – Saisonabschluss:** Teilnahme-/Auswertungsstatus prüfen, Vorjahresschnitte fortschreiben und Saisonende setzen.
- **E4.4 – PDF-Berichte:** Tages-, Fleischpreis-, Klassen-, Schützen- und Saisonabschlussberichte mit konfiguriertem Pfad und nachvollziehbaren Dateinamen ausgeben.

### Phase 5 – Externe Importe

**Epic E5: Eingangsadapter**

- **E5.1 – WMK-Reader:** Nur nach E0.3; konkrete Versionserkennung, sichere Leseverarbeitung und Mapping auf das kanonische Schussmodell.
- **E5.2 – Importvorschau und Konflikte:** Unbekannte Schützen, unvollständige Felder, Duplikate und Probe-/Wertungsschüsse vor Übernahme anzeigen.
- **E5.3 – Idempotenter Import:** Wiederholung einer Quelle erzeugt keine Duplikate und lässt sich anhand des Importlaufs diagnostizieren.
- **E5.4 – XML-Adapter:** Nur bei bestätigter Eignung aus E0.4; dieselbe kanonische Validierung und Importhistorie wie WMK.
- **E5.5 – Referenzabnahme:** Importergebnis bis zum Einzelschuss mit WM-Shot/OpticScore vergleichen und Abweichungen dokumentieren.

Der SQLite-Export aus der Altanwendung wird über die Migrationsstrecke aus E1.3 übernommen und ist ausdrücklich kein WMK-Importer-Test.

### Phase 6 – Bedienoberfläche, Einführung und Betrieb

**Epic E6: Produktivbetrieb**

- **E6.1 – Angular-Flows an die API anbinden:** Scheinpersistenz durch echte Lade-/Speicherabläufe, Validierungsfehler und Statusmeldungen ersetzen.
- **E6.2 – Bedienbarkeit prüfen:** Schießleitung auf PC/Tablet, barrierearme Formulare und sichere Bestätigungen bei destruktiven oder wertungsrelevanten Aktionen.
- **E6.3 – Rollen und Datenschutz:** Zugriff auf personenbezogene Daten sowie Protokollierung und Lösch-/Aufbewahrungsregeln umsetzen.
- **E6.4 – Backup und Wiederherstellung:** automatisierbare Sicherung und Restore-Test dokumentieren und durchführen.
- **E6.5 – Deployment und Monitoring:** Installation, Konfiguration, Updates, Logs und Fehlerbehebung für den Linux-Host festhalten.

## Abhängigkeiten und kritischer Pfad

`E0.1/E0.2 → E1 → E2 → E3 → E4 → E6`

Der externe WMK-Pfad lautet `E0.3 → E5.1–E5.5`; er benötigt das kanonische Datenmodell, blockiert aber weder manuelle Erfassung noch die Migration des Altbestands. XML hängt zusätzlich von E0.4 ab.

## MVP-Vorschlag

Das MVP umfasst:

1. Migration und Prüfung des vorhandenen SQLite-Exports.
2. Mitglieder, LG-/LP-Klassen, Saison und Schießtag.
3. Manuelle Ergebniserfassung mit Korrekturhistorie.
4. Belegte Tages- und Saisonwertungen, soweit deren Regeln fachlich abgenommen sind.
5. Die notwendigen Tages- und Saisonberichte.
6. Datenschutz, Backup und Restore.

Der WMK-Import gehört zum MVP, wenn E0.3 nachweist, dass die benötigten Quelldaten verfügbar sind und der Verein ihn für den Tagesbetrieb priorisiert. Sonst wird ein manueller Erfassungsweg als erster produktiver Pfad genutzt und der Importer separat weitergeführt. XML, Live-Poller, Android, Standbelegung und weitere nicht belegte Wettbewerbe sind nachgelagerte Entscheidungen.

## Risiken und offene Entscheidungen

| Thema | Risiko / offene Frage | Maßnahme |
| --- | --- | --- |
| SQLite-Altbestand | Export schaltet Fremdschlüssel aus; Daten oder Beziehungen können unvollständig sein | Datenprofil, Constraints beim Zielimport und Fehlerliste |
| WMK-Schema | Altbestands-SQL sagt nichts über `.wmk`-Format oder dessen Version | Reale Dateien analysieren; unterstützte Versionen festlegen |
| Wertungsregeln | Preis-, Klassen- und Saisonregeln enthalten Randfälle | Beispiele vom Verein abnehmen und automatisiert testen |
| Rohdaten | Altbestand und WMK-Export können unterschiedliche Detailgrade liefern | Kanonisches Modell und Herkunft/Fehlfelder dokumentieren |
| Wiederholte Auswertung | Neuberechnung kann gespeicherte Preise/Berichte ersetzen | Versionierte Rechenläufe und nachvollziehbare Korrektur |
| Datenschutz/Betrieb | Geburtsdaten, Mitgliedsnummern und Ergebnisse sind personenbezogen | Rollen, Aufbewahrung und Restore-Ziel festlegen |
| Früherer Featureumfang | Live-/Wochenmodus-/Stand- und Sonderwettbewerbe sind nicht quellbelegt | Nicht als MVP implementieren, vor Aufnahme beschließen |

## Abstimmung mit GitHub-Issues

Die bestehenden Epics und Stories wurden am 09.10.2026 an diese quellenbasierte Reihenfolge angepasst. Wochenmodus, automatische Schussbereichszuordnung, Best-of-N, Standbelegung und zusätzliche Wettbewerbe sind nur noch optionale, beschlussabhängige Erweiterungen. Die Datenqualitätsanalyse des SQLite-Altbestands ist in [#52](https://github.com/oxiego/TruderRinge/issues/52) ergänzt; [#53](https://github.com/oxiego/TruderRinge/issues/53) klärt Betriebsmodell, Datenschutz und Wiederherstellung. Beide Issues sind als native Sub-issues mit [Epic E0 (#1)](https://github.com/oxiego/TruderRinge/issues/1) verknüpft. Die fachlich zur Saisonwertungs-Baseline gehörende Königsschießen-Story [#36](https://github.com/oxiego/TruderRinge/issues/36) wurde aus dem optionalen Epic E6 gelöst und unter [Epic E5 (#9)](https://github.com/oxiego/TruderRinge/issues/9) eingeordnet.
