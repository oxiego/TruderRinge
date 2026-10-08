# Technische Vorprüfung: Übernahme von OpticScore- / WM-Shot-Daten in unser bestehendes Auswerteprogramm

---

## 1. Ausgangssituation

Unser Schießstand wird auf elektronische **DISAG-OpticScore-Stände** umgerüstet. Die Auswertung und Wettkampfverwaltung soll weiterhin über **WM-Shot** erfolgen. Parallel dazu möchten wir unser bestehendes eigenes Auswerteprogramm weiterverwenden.

Das eigene Programm arbeitet mit frei strukturierten Datenbanken und benötigt nach Abschluss eines Schießtages lediglich die für unsere Auswertung relevanten Ergebnisdaten. Eine Echtzeitübertragung ist nicht erforderlich.

---

## 2. Benötigte Daten

Für unsere Anwendung müssen pro Schütze folgende Informationen übernommen werden:

* **Schütze / eindeutige Schützenidentifikation**
* **Schießdatum**
* **Gesamtergebnis über 40 Schuss**
  * Ganze Ringe
  * Ergebnis mit Zehntelwertung
* **Ergebnisse der vier 10-Schuss-Serien**
  * Ganze Ringe
  * Zehntelwertung
* **Bester Teiler jeder 10-Schuss-Serie**

> **Hinweis:** Wir benötigen insbesondere keine Live-Datenübertragung und voraussichtlich auch keine vollständigen Rohdaten wie Schusszeit oder X-/Y-Koordinaten.

---

## 3. Relevante Systemarchitektur

Die geplante Umgebung sieht grundsätzlich so aus:

```text
DISAG OpticScore Messrahmen
          │
          ▼
       SIZ / OpticScore
          │
          ▼
   OpticScore Server
          │
          ▼
     WM-Shot-Modul
          │
          ▼
   WM-Shot-Datenbank (.wmk)
          │
          ├──────────► WM-Shot-Auswertung
          │
          └──────────► Eigenes Auswerteprogramm

```

DISAG dokumentiert, dass die über OpticScore erfassten Schussdaten über das WM-Shot-Modul in die WM-Shot-Datenbank übertragen werden. Die WM-Shot-Datenbank verwendet Dateien mit der Endung `.wmk`.

---

## 4. Mögliche Schnittstellen

Es gibt grundsätzlich drei relevante technische Ansätze:

### A. Auslesen der WM-Shot-Datenbank (`.wmk`)

Die `.wmk`-Datei könnte nach Abschluss des Schießtages durch unser Programm gelesen und die benötigten Daten in unsere eigene Datenbank übernommen werden. Dies wäre für unseren Anwendungsfall grundsätzlich der interessanteste Weg, sofern die benötigten Datenfelder in der WM-Shot-Datenbank vorhanden und stabil auslesbar sind.

**Zu prüfen sind insbesondere:**

* Tabellen-/Relationenstruktur der `.wmk`
* Schützenidentifikation
* Wettkampf-/Wertungszuordnung
* Schuss- bzw. Serienzuordnung
* Ringwert
* Zehntelwert
* Teiler
* Datum
* Kennzeichnung von Probeschüssen und Wertungsschüssen

*Bewertung:* Die direkte Abhängigkeit von einem nicht offiziell dokumentierten internen WM-Shot-Datenbankschema sollte hinsichtlich Wartbarkeit und Versionskompatibilität bewertet werden.

---

### B. DISAG-OpticScore-XML

OpticScore besitzt einen dokumentierten XML-Export. Dieser enthält beim entsprechenden OpticScore-Preisschießmodul sämtliche Informationen zu Schützen und Schüssen.

**Die dokumentierte XML-Struktur enthält unter anderem:**

* Schütze & Stand
* Schussnummer, Serie / Durchgang
* Ringwert, Zehntelwert, Teiler
* X-/Y-Koordinaten & Schussstatus
* Datum / Zeit

Damit wäre ein XML-Import in unsere Software grundsätzlich sehr gut geeignet.

*Bewertung:* Zu klären ist allerdings noch, ob dieser XML-Export in exakt derselben Form auch für die von uns geplanten WM-Shot-Wettkämpfe zur Verfügung steht. Die DISAG-Dokumentation beschreibt den XML-Export insbesondere für das OpticScore-Preisschießen; für die WM-Shot-Anbindung ist ein entsprechender Tagesexport bislang nicht eindeutig dokumentiert.

---

### C. JSON-Live-Schnittstelle

DISAG stellt außerdem eine offizielle JSON-Live-Schnittstelle zur Verfügung. Diese überträgt Schussereignisse in Echtzeit, unter anderem mit Ringwert, Zehntelwert, Teiler, X/Y-Koordinaten, Schussnummer, Serie und Schützeninformationen.

*Bewertung:* Diese Schnittstelle ist technisch leistungsfähig, für unseren Anwendungsfall aber nicht erforderlich, da wir die Daten erst nach Abschluss des Schießtages übernehmen möchten. Ein permanenter UDP-Listener bzw. eine laufende Live-Datenübernahme wäre daher unnötig komplex.

---

## 5. Für unsere Auswertung notwendige Datenstruktur

Für unsere Zwecke reichen grundsätzlich die Einzelschussdaten, aus denen sich die gewünschten Serien- und Gesamtergebnisse berechnen lassen.

### Beispiel-Datensatz:

* **Schütze:** Mustermann, Max
* **Datum:** 08.10.2026

| Serie | Ganze Ringe | Zehntelwertung | Bester Teiler |
| --- | --- | --- | --- |
| **Serie 1** | 98 Ringe | 102,7 | 87 |
| **Serie 2** | 96 Ringe | 101,8 | 112 |
| **Serie 3** | 99 Ringe | 104,1 | 43 |
| **Serie 4** | 97 Ringe | 102,6 | 76 |
| **Gesamt** | **390 Ringe** | **411,9** | — |

*Der beste Teiler je Serie kann aus den Teilerwerten der zehn Wertungsschüsse der jeweiligen Serie durch Ermittlung des Minimums berechnet werden.*

---

## 6. Vorläufige technische Bewertung

Für unseren konkreten Anwendungsfall erscheint folgende Priorisierung sinnvoll:

1. **Priorität 1:** Prüfen, ob die benötigten Einzelschussdaten einschließlich Teiler zuverlässig aus der WM-Shot-`.wmk`-Datenbank ausgelesen werden können.
2. **Priorität 2:** Prüfen, ob für WM-Shot-Wettkämpfe der OpticScore-XML-Export mit den benötigten Einzelschussdaten genutzt werden kann. Falls ja, wäre dies wegen des dokumentierten und strukturierten Austauschformats wahrscheinlich die bevorzugte Schnittstelle.
3. **Priorität 3:** JSON-Live-Schnittstelle nur dann einsetzen, wenn weder `.wmk` noch XML einen geeigneten Offline-Export ermöglichen. Für den derzeit vorgesehenen Tagesabschluss-Import wäre sie ansonsten unnötig.

---

## 7. Nächster technischer Test

Für eine belastbare Entscheidung sollte ein kleiner Testwettkampf durchgeführt werden:

* **Szenario:** 2–3 Testschützen mit jeweils 40 Schuss über mehrere 10er-Serien.
* **Durchführung:** Anschließend Export bzw. Sicherung der WM-Shot-`.wmk`-Datei (und ggf. zusätzlich OpticScore-XML exportieren).
* **Verifikation:** Prüfen, ob sich folgende Informationen eindeutig extrahieren lassen:
* [ ] Schütze
* [ ] Datum
* [ ] Serie 1–4
* [ ] Schussnummer
* [ ] Ringwert & Zehntelwert
* [ ] Teiler
* [ ] Unterscheidung Wertungsschuss / Probeschuss



Sind diese Informationen vorhanden, ist die Weiterverwendung unseres bestehenden Auswerteprogramms technisch problemlos vorstellbar.

---

## 8. Quellen

Als maßgebliche Quellen sollten für die weitere technische Prüfung insbesondere die Herstellerdokumentationen herangezogen werden von:

* **DISAG / OpticScore**
* **Konrad Software / WM-Shot**

Besonders relevant sind dabei die DISAG-Dokumentationen zur WM-Shot-Schnittstelle, zur OpticScore-XML-Struktur und zur JSON-Live-Schnittstelle sowie die von Konrad Software bereitgestellte Dokumentation zur DISAG-OpticScore-Schnittstelle und zum OpticScore-Import.

> **Wichtig:** Vor einer Implementierung sollte anhand einer realen Test-`.wmk` bzw. einer realen OpticScore-XML-Datei verifiziert werden, welche Felder in der konkret eingesetzten Version tatsächlich befüllt werden. Die bisherige Recherche belegt die grundsätzliche Verfügbarkeit der genannten Datenstrukturen, ersetzt aber keinen Test mit der tatsächlich eingesetzten Software-/Firmware-Version.
          