# Fachliche Anforderungen für eine Neuentwicklung

## Zweck und Quellenbasis

Dieses Dokument beschreibt die aus den vorhandenen Dateien rekonstruierte Anwendung für die Schützengesellschaft Gemütlichkeit Trudering e.V. Es soll als fachliche Grundlage für eine Neuentwicklung dienen und nicht die vorhandene Umsetzung oder deren technische Fehler nachbilden.

Die Beschreibung basiert hauptsächlich auf den LibreOffice-Basic-Makros der jüngsten vorliegenden Fassung `Makros/2025-09-28-Gem_Trudering_Makros`, dem HSQLDB-Schema unter `database/`, den mitgelieferten Berichten und den älteren Makroständen. Die übrigen datierten Makroordner sind überwiegend historische Versionen. `Koenig_alt.xba` liegt auch im jüngsten Ordner und ist als ältere Variante zu behandeln. Die Dateien `Schuetzen.odt` und `Verwaltung.odt` enthalten nur knappe Deckblattinformationen; das mitgelieferte Base-Handbuch beschreibt LibreOffice Base allgemein, nicht die Fachlogik dieser Anwendung.

Die folgenden Regeln geben das beobachtete Altverhalten wieder. Wo Regeln nicht eindeutig oder nur über konfigurierbare Tabellen festgelegt sind, ist das ausdrücklich vermerkt.

## 1. Fachlicher Umfang

Die Anwendung verwaltet Vereinsmitglieder, Saison- und Schießtagsdaten, Luftgewehr- und Luftpistolenergebnisse, Klassen, Fleischpreise, Geldpreise, Pokale sowie die dazugehörigen Ranglisten und Berichte.

Die beiden Disziplinen Luftgewehr (LG) und Luftpistole (LP) teilen sich Stammdaten und Saisonabläufe, werden aber bei Ergebnissen, Klassen, Nummerierung und zahlreichen Auswertungen getrennt geführt. Ein Schütze kann für eine oder beide Disziplinen gemeldet sein.

## 2. Zentrale Abläufe

### 2.1 Neue Saison

1. Eine neue Saison darf erst begonnen werden, wenn keine andere Saison als aktiv markiert ist.
2. Die Saisonbezeichnung ist eine Jahreszahl. Sie wird vorbelegt mit dem aktuellen Kalenderjahr, muss eindeutig sein und wird als aktive Saison gespeichert.
3. Für Jugendklassen wird ein Jahrgangsgrenzwert auf `aktuelles Jahr - 17` gesetzt. Die Klasseneinteilung unterscheidet Jugend und Nicht-Jugend anhand des Geburtsjahres gegenüber diesem Wert.
4. Saisonbezogene Fleischpreis-Zähler und zugehörige temporäre/verteilungsbezogene Daten werden zurückgesetzt.
5. Die Saison besitzt Beginn- und Enddatum sowie Statusfelder, die anzeigen, ob LG- und LP-Saisonwertungen durchgeführt wurden.

### 2.2 Klasseneinteilung zu einer Saison

- Die Einteilung erfolgt pro Disziplin und aktiver Saison.
- Berücksichtigt werden aktive Vereinsmitglieder, die für die jeweilige Disziplin gemeldet sind.
- Klassen werden anhand administrativ gepflegter Merkmale ausgewählt: Disziplin, Aktivstatus, Jugendklasse, Damenklasse, Hilfsmittel, Einlage, Zahl der Serien und Fleischberechtigung.
- Sondergruppen (Jugend, Damen, Hilfsmittel) werden nur getrennt geführt, wenn dafür in der Disziplin aktive Klassen eingerichtet sind. Fehlt eine solche Klasse, werden betroffene Mitglieder bei der allgemeinen Einteilung berücksichtigt.
- In allgemeinen Klassen werden Mitglieder nach dem Vorjahresschnitt absteigend sortiert und möglichst gleichmäßig auf die aktiven Klassen verteilt. Eine etwaige Restgruppe wird den letzten Klassen der sortierten Klassenliste zugeordnet.
- Für die LG werden saisonbezogene Schützennummern ab 1 vergeben, für die LP ab 81. Die Nummer und Klasse werden zusammen mit Saison und Mitglied in der Disziplin-Einteilung gespeichert.
- Zu Beginn einer Neuteilung werden bisherige Zähler in den Klassen zurückgesetzt. Die Einteilung wird in saisonbezogenen LG-/LP-Klassentabellen abgelegt.

### 2.3 Schießtag eröffnen

1. Ein Schießtag kann nur in einer aktiven Saison eröffnet werden.
2. Die Nummer ist die bisher höchste Schießtagsnummer der Saison plus eins.
3. Für das aktuelle Datum darf nicht bereits ein Schießtag eröffnet worden sein.
4. Das Fleischschießen wird gegenüber dem letzten Schießtag zunächst alternierend vorgeschlagen. Anschließend kann der Bediener pro Klasse auswählen, ob sie an diesem Tag Fleischpreise schießt.
5. Die konfigurierten Fleisch-Tage pro Klasse werden bei Auswahl heruntergezählt. Gibt es keine berechtigte/ausgewählte Klasse mehr, wird der Schießtag nicht als Fleisch-Schießtag markiert.
6. Saison, Schießtagsnummer, Datum und Fleischstatus werden gespeichert. Beim ersten Schießtag wird außerdem das Saison-Beginn-Datum gesetzt.

Fleisch ist somit kein bloß globales An/Aus-Merkmal: Der Schießtag enthält einen Gesamtstatus, und zusätzlich wird die Auswahl je Klasse gespeichert.

### 2.4 Mitglieder erfassen

Die Erfassungsmaske nimmt folgende Stammdaten und Teilnahme-Merkmale auf:

- Mitglieds-/Passnummer, Vorname, Nachname, Geburtsdatum und Geschlecht (`M`/`W`)
- LG- und LP-Teilnahme
- Fleischberechtigung für LG und LP
- Verwendung von Hilfsmitteln
- Aktivstatus

Die Passnummer ist achtstellig und muss eindeutig sein. Ist sie noch unbekannt, kann die Eingabe leer bleiben; dann wird eine temporäre Nummer aus dem Bereich beginnend bei `99999999` abwärts vergeben. Vorname, Nachname, Geburtsdatum und Geschlecht sind Pflichtangaben. Neue Mitglieder sind standardmäßig aktiv.

Wird während einer laufenden Saison ein Mitglied angelegt, wird eine Klasseneinteilung angeboten. In den vorhandenen Makros ist eine Erfassungs-/Neuanlagefunktion erkennbar; ein vollständiger Änderungs- und Löschworkflow für bestehende Stammdaten ist daraus nicht sicher ableitbar.

### 2.5 Tagesergebnisse erfassen

- LG und LP werden getrennt erfasst. Die Eingabe ist nur möglich, wenn die aktive Saison einen Schießtag mit heutigem Datum hat.
- Die Bedienung wählt den Schützen über seine saisonbezogene Nummer aus; die Anwendung zeigt dazu den zugehörigen Namen.
- Zahl und Definition der Serien werden über die Schützenklasse konfiguriert. Ergebnisse werden disziplinbezogen als bis zu vier zusammengefasste Serien und als Gesamtergebnis gespeichert. Zusätzlich gibt es Rohdaten je Serie und Einzelschuss: zehn Schüsse pro LG-Serie und fünf pro LP-Serie.
- Für die Ergebniszeile werden außerdem ein Pokal-Teiler und ein zweites Programm/zweiter Teiler geführt. Die konkreten Felder variieren danach, ob an diesem Tag Fleisch geschossen wird.
- Ungeschossene Serien werden mit null aufgefüllt. Beim Speichern wird der Tagesdatensatz sofort persistiert.
- Die Erfassung prüft problematische Null-Teiler und zeigt bei einer Schnapszahl (333) einen Hinweis an.
- Es gibt eine Dialogfolge zum Erfassen, Anzeigen bzw. Korrigieren innerhalb des Erfassungsablaufs. Ein belastbarer, allgemeiner Korrekturworkflow für bereits abgeschlossene Tage ist aus den Makros nicht ersichtlich.

### 2.6 Königsschießen und Schmankerlpokal erfassen

- Beide Sonderwettbewerbe erfassen je Schütze und Saison einen Teiler sowie Disziplin, Klasse und Jugendstatus.
- Der Teiler ist numerisch mit einer Nachkommastelle; die Eingabemaske begrenzt ihn auf 0 bis 999,9. Bei 0,0 bzw. einem auffälligen Grenzwert wird eine Bestätigung eingeholt.
- Beim Königsschießen werden Erwachsene und Jugend getrennt ausgewertet. Die Platzierung erfolgt je Gruppe nach aufsteigendem Teiler (kleiner ist besser).
- Der Schmankerlpokal wird je Disziplin saisonbezogen gespeichert und in seiner Saisonwertung ebenfalls nach Teiler gerankt.

### 2.7 Tagesauswertung und Tagesberichte

Die Tagesauswertung kann für den aktuellen Schießtag ausdrücklich bestätigt werden. Wird sie für einen bereits ausgewerteten Tag erneut gestartet, löscht die Anwendung die vorherigen Tages-Preis- und Berichtsdaten des betroffenen Tages und berechnet sie neu.

Je Disziplin umfasst die Auswertung:

- Verteilung der Geldpreise anhand Klasse, Einlage, Jugendstatus, Serienergebnissen und zweitem Programm/Teiler.
- Separate Behandlung von Klassen mit Hilfsmitteln und Jugendklassen.
- Rangfolge nach den Serien: die vier zusammengefassten Serien werden der Größe nach sortiert und als Tie-Breaker nacheinander verglichen (höchste Serie zuerst).
- Gesonderte Teilerplatzierungen, bei denen der kleinere Teiler die bessere Platzierung darstellt.
- Aufbau von Ranglisten-/Berichtsdaten, die anschließend als PDF ausgegeben werden.

Die Geldpreisberechnung stammt aus einer gemeinsamen Funktion. Das beobachtete Altverhalten ist:

1. Bei ungerader Teilnehmerzahl wird die für die Berechnung verwendete Anzahl zunächst um eins erhöht.
2. Für Erwachsene gilt bei 1–2 Teilnehmern ein fixer Betrag von 1,40; bei 3–4 Teilnehmern wird `Einlage * (0,36 - 0,26 * (Platz - 1))` verwendet; bei mehr Teilnehmern `Einlage * (0,55 - 0,5 / (Anzahl / 2 - 1) * (Platz - 1))`.
3. Für Jugend gilt bei Anzahl 1 der Betrag `Einlage`; bei 2–5 Teilnehmern `Einlage * (1 - 0,5 / (Anzahl / 2 - 1) * (Platz - 1))`; sonst `Einlage * (1 - 0,69 / (Anzahl / 2 - 1) * (Platz - 1)) + 0,75 / Platz`.

Diese Formeln sollten vor einer Übernahme mit dem Verein fachlich bestätigt und mit Randfällen getestet werden. Insbesondere ist die Ein-Personen-Jugendgruppe nach der vorgeschalteten Rundung ein Randfall.

#### Fleischpreise

- Das Fleisch wird je Schießtag und Klasse konfiguriert und je Disziplin aus den angetretenen, für Fleisch berechtigten Mitgliedern der betreffenden Klasse verteilt.
- Die Kandidaten werden anhand erster Serie und Gesamtergebnis sortiert.
- Vergebene Plätze (erster bis dritter Preis) und Schütze/Serie werden pro Schießtag und Klasse protokolliert. Saisonbezogene Preisfelder verhindern insbesondere eine unmittelbar wiederholte Vergabe desselben Spitzenplatzes an denselben Schützen bei aufeinanderfolgenden Fleisch-Schießtagen.
- Tages- und Saisonübersichten der Fleischpreise sind Bestandteil der Berichte.

Die genaue Behandlung sämtlicher Gleichstände und aller Wiederholungsfälle ist im Altcode verteilt implementiert und sollte mit konkreten Vereinsbeispielen als Abnahmetest festgeschrieben werden.

#### Berichte für einen Schießtag

Die vorhandenen Ausgaben decken LG-/LP-Tagesergebnisse, LG-/LP-Ranglisten (Geldpreise) und Fleischpreise ab. Es gibt zusätzlich einen Administratorpfad für die Tagesauswertung.

Beim Programmstart wird nach einem Schießtag, dessen Datum nicht mehr heute ist, eine Plausibilitätsprüfung der Tagesauswertungs-Tabellen vorgenommen. Bei fehlenden Auswertungsdaten wird ein Fehlerhinweis ausgegeben.

### 2.8 Saisonwertungen

Die Saisonwertung läuft nur für eine aktive Saison. Vor der LG-Wertung wird geprüft, ob Schießtage und LG-Ergebnisse vorhanden sind. Für jeden erfassten Schießtag muss mindestens ein LG-Ergebnis existieren. Eine LP-Wertung wird zusätzlich gestartet, wenn in der Saison LP-Ergebnisse vorhanden sind.

Pro Disziplin sind folgende Auswertungen vorhanden:

- **Vereinsmeisterschaft:** jahresbezogener Schnitt je Schütze und Klasse; Vergleich mit Vorjahr sowie Differenz. Die Jahreswerte werden für den Saisonabschluss in den Mitgliederstammdaten als Vorjahresschnitt fortgeschrieben.
- **Geldpreise:** saisonbezogene Summen/Beträge und Zahl der gewerteten Tage je Schütze und Klasse.
- **Pokalteiler:** Platzierungen nach Teiler je Klasse (LP und LG).
- **Schmankerlpokal:** Platzierung nach Teiler, getrennt nach Disziplin sowie Jugend-/Klassenmerkmal.
- **Königsschießen:** Platzierung nach Teiler; Erwachsene und Jugend werden getrennt geführt.
- **LG Diepold-Wanderpokal:** LG-spezifische Platzierung mit Teiler, Jugend- und Klassenmerkmal.
- **LG Röhrner-Wanderpokal:** LG-spezifische Platzierung, bei der die gespeicherten Daten die Anzahl der Tage und das Geburtsdatum berücksichtigen.

Die Saisonauswertung speichert ihre Ergebnisse in separaten Tabellen, aktualisiert die jeweiligen Auswertungsstatus der Saison und erzeugt Abschlussberichte.

### 2.9 Saison abschließen und löschen

- Ein Abschluss setzt eine aktive Saison voraus und ist erst möglich, wenn die LG- und LP-Saisonwertungen als durchgeführt markiert sind.
- Nach Bestätigung werden die saisonalen Schnitte als Vorjahresschnitte in den Mitgliederstammdaten abgelegt, das Enddatum auf das Datum des letzten Schießtages gesetzt und die Saison deaktiviert.
- Eine Saison kann außerdem über eine gesonderte Funktion gelöscht werden. Die Funktion ist destruktiv; die Neuentwicklung muss Umfang, Sicherheitsabfrage und Aufbewahrung für diese Aktion explizit festlegen.

## 3. Berichte und Exporte

Die Altanwendung erzeugt und exportiert PDF-Berichte für:

- Schützenliste
- LG-/LP-Tagesergebnisse und Ranglisten
- Tages- und Saison-Fleischpreise
- LG-/LP-Klasseneinteilung
- LG-/LP-Schützenbericht je Saison
- Königsschießen
- Schmankerlpokal
- Diepold- und Röhrner-Wanderpokal
- Vereinsmeisterschaft, Geldpreise und Pokalteiler
- Saisonabschlussberichte

Berichte werden im Verzeichnis `Berichte/<Saison>/` abgelegt. Die Dateinamen enthalten typischerweise Saison, Schießtag, Disziplin/Berichtstyp und Tagesdatum. Die vorhandenen Makros verwenden feste Windows-Pfade; in der Neuentwicklung müssen Ausgabepfad, Dateinamen und Überschreiben bereits vorhandener Dateien konfigurierbar bzw. nachvollziehbar sein.

## 4. Datenmodell der Altanwendung

### Stammdaten und Konfiguration

- **Saison:** Saisonjahr, Beginn, Ende, aktiv sowie Status LG-/LP-Auswertung.
- **Schuetzen:** Passnummer, Name, Vorname, Geburtsdatum, Geschlecht, LG-/LP-Meldung, Vorjahresschnitte, Fleischberechtigung je Disziplin, Hilfsmittel und Aktivstatus.
- **Schuetzenklassen:** Klassenkennung/-bezeichnung, Disziplin, Zahl der Serien, Jahrgang/Jugendstatus, Damenstatus, Hilfsmittelstatus, Fleischstatus, Einlage, Aktivstatus und zugeordnete Schützenzahl.
- **Schuetzenliste:** Zuordnung von Mitgliedern zu LG-/LP-Nummern.

### Saison- und Schießtagdaten

- **Schiesstage:** Saison, fortlaufende Schießtagsnummer, Datum und Fleischstatus.
- **LG-/LP_Einteilung_Klassen:** Saison, Mitglied, saisonbezogene Nummer und Klasse.
- **LG-/LP_Ergebnisse_Schiesstag:** Saison, Schießtag, Mitglied, vier Serien, Gesamtergebnis, Pokal und zweites Programm/Teiler.
- **LG-/LP_Serien:** einzelne Serien samt Einzelschüssen und Serienergebnis.
- **LG-/LP_Jahresschnitt:** saisonbezogener Durchschnitt je Mitglied.

### Preise und Auswertungen

- **LG-/LP_Geldpreise** und **Geldpreise_Bericht:** Platzierung nach Serie/Teiler, Betrag, Jugendstatus sowie lesbare Berichtsdaten.
- **Fleischpreise_Anzahl**, **Fleischpreise_Schiesstag**, **Fleischpreise_Ergebnisse_Schiesstag**, **Fleischpreise_Saison:** Quoten, Tagesauswahl, Preisvergabe und saisonale Wiederholungsverfolgung.
- Wettbewerbstabellen für **Königsschießen**, **Schmankerlpokal**, **Pokalteiler**, **Vereinsmeister**, **Diepold-WP** und **Röhrner-WP** (LG und/oder LP je nach Wettbewerb).
- **Schuetzen_Bericht** (LG/LP): zusammengeführte Saisonübersicht mit Schnitt, Platzierungen, Teilern, Fleisch- und Geldpreisen.
- **Temp_...** Tabellen: technische Arbeitsbereiche zur Klassen-, Fleisch- und Preisverteilung; nicht als dauerhafte fachliche Historie behandeln.

Die LG-/LP-Tabellen wiederholen viele Strukturen. Eine Neuentwicklung kann sie intern vereinheitlichen, muss aber die Disziplin als fachliche Dimension erhalten und historische Berichte weiterhin getrennt ausgeben können.

## 5. Betrieb, Integration und Backup im Bestand

- Die Altanwendung ist eine LibreOffice-Base-Datei mit HSQLDB-Backend und StarBasic-Makros. Makros greifen über eine gemeinsame Datenbankverbindung auf Tabellen zu.
- Beim Start werden aktive Saison, letzter Schießtag, Fleischstatus, Datum, Schriftparameter und Druck-/Berichtsumgebung initialisiert.
- Beim Schließen werden Datenbankdokument und Verbindung gespeichert/geschlossen.
- `Trudering.bat` erstellt mit 7-Zip aus `backup.lst` ein datiertes ZIP, kopiert es in einen fest codierten Windows-Backupordner und verschiebt es in einen lokalen Backupordner.
- Pfade, Datenbankname, LibreOffice-Integration, PDF-Export und Backup-Ziele sind derzeit fest an Laufwerksbuchstaben/Windows-Benutzer gebunden. Für die Neuentwicklung müssen diese Betriebswerte konfigurierbar und plattform-/standortunabhängig sein.

## 6. Anforderungen an die Neuentwicklung

1. **Datenintegrität:** eindeutige Mitgliedsnummern, eindeutige Saison-/Schießtagzuordnungen und konsistente Beziehungen zwischen Mitgliedern, Klassen, Ergebnissen und Wettbewerben.
2. **Nachvollziehbarkeit:** Änderungen und Neuberechnungen an Ergebnissen/Auswertungen müssen protokolliert werden; erneute Berechnungen dürfen nicht unbemerkt Daten überschreiben.
3. **Wiederholbare Auswertungen:** Tages- und Saisonberichte müssen aus den gespeicherten Rohdaten reproduzierbar sein; fachliche Berechnungsregeln sollen zentral und versioniert definiert werden.
4. **Korrekturworkflow:** autorisierte Benutzer müssen fehlerhafte Stammdaten, Ergebnisse und Schießtags korrigieren können, mit sichtbarer Auswirkung auf abhängige Auswertungen.
5. **Konfigurierbarkeit:** Klassen, Serienzahl, Einlagen, Alters-/Jahrgangsgrenzen, Mindestteilnahme, Fleischquoten, Preisregeln, Dateipfade und Vereinsbezeichnungen dürfen nicht in Programmcode oder festen Pfaden versteckt sein.
6. **Ergebnisvalidierung:** Disziplin-/Klassenregeln, Nullwerte, ungültige Teiler, Doppelmeldungen und fehlende Ergebnisse müssen verständlich geprüft werden.
7. **Berichte:** PDF-Ausgaben müssen alle oben genannten Berichtstypen unterstützen, reproduzierbar benannt werden und an einen konfigurierten Speicherort exportiert werden.
8. **Datenschutz und Zugriff:** personenbezogene Daten (Geburtsdatum, Mitgliedsnummer, Ergebnisse) benötigen rollenbasierte Zugriffe, sichere Backups und ein geregeltes Aufbewahrungs-/Löschkonzept.
9. **Migration:** Saison-, Mitglieder-, Ergebnis-, Preis- und Berichtsdaten aus der bestehenden Base-Datenbank müssen übernommen und stichprobenartig gegen Altberichte geprüft werden.
10. **Betriebsfähigkeit:** Backup und Wiederherstellung müssen dokumentiert und regelmäßig testbar sein; ein bloßes Erzeugen von ZIP-Dateien genügt nicht als Wiederherstellungskonzept.

## 7. Vor Umsetzung fachlich zu bestätigen

Die Dateien reichen nicht aus, um folgende Punkte sicher als verbindliche Vereinsregeln festzulegen:

- Exakte LG-/LP-Serien- und Schusszahlen je Klasse sowie Umgang mit unvollständigen Serien.
- Aktuelle Definitionen der Klassen und Alters-/Jahrgangsgrenzen; die vorhandene Jugendlogik verwendet das Kalenderjahr und den Wert `Jahr - 17`.
- Genaue Mindestteilnahme und Berechnung der Vereinsmeisterschaft, einschließlich Umgang mit fehlenden Tagen und Gleichständen.
- Vollständige Geldpreisformeln und deren Rundung/Währungsformat; die Altformeln enthalten Sonderfälle, die fachlich verifiziert werden müssen.
- Fleischpreis-Tie-Breaker und alle Regeln zur Vermeidung wiederholter Gewinner.
- Zulässige Korrekturen nach Tagesabschluss und ob alte PDF-Ausgaben ersetzt, versioniert oder archiviert werden.
- Fachliche Voraussetzungen für Saisonabschluss, insbesondere das Altverhalten, dass sowohl LG- als auch LP-Auswertung als durchgeführt erwartet werden.
- Regeln und Datenumfang beim Löschen einer Saison sowie gesetzliche/vereinsinterne Aufbewahrungsfristen.
- Mehrbenutzerbetrieb, Rollen, Berechtigungen und benötigte Audit-Protokolle.
- Wiederherstellungspunkt, Backup-Aufbewahrung und Zielsysteme der künftigen Anwendung.

## 8. Vorgeschlagene Abnahmetests

- Saison darf nicht doppelt aktiv sein; Neuanlage setzt Jahrgang und Fleischkonfiguration nachvollziehbar zurück.
- Klasseneinteilung bildet aktive Mitglieder nach LG/LP, Geschlecht, Jugend und Hilfsmittel korrekt ab und erzeugt stabile saisonbezogene Nummern.
- Pro Datum kann nicht versehentlich ein zweiter Schießtag erzeugt werden; Fleischberechtigung und Quoten werden korrekt angewendet.
- LG- und LP-Rohschüsse ergeben nachvollziehbar Serien- und Gesamtergebnisse; unvollständige Ergebnisse und Teiler-Randfälle werden geprüft.
- Eine Tagesauswertung lässt sich nach dokumentierter Korrektur reproduzierbar neu erstellen; alle Tagesberichte stimmen mit den gespeicherten Ausgangsdaten überein.
- Preisberechnung deckt kleine/ungerade Teilnehmerzahlen, Jugend und mehrere Platzierungen ab; Beträge und Rangfolgen entsprechen abgenommenen Beispielen.
- Fleischpreise respektieren Klassenberechtigung, Rangfolge und bestätigte Wiederholungsregeln.
- Saisonwertungen, Vorjahresschnittfortschreibung und Saisonabschluss stimmen für LG und LP mit manuell kontrollierten Referenzfällen überein.
- Alle PDFs werden mit erwarteter Saison/Schießtag/Disziplin abgelegt; Backup kann in einer Testumgebung vollständig wiederhergestellt werden.
