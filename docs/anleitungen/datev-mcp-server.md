# MCP-Server für das DATEV-Format: Buchungsstapel (EXTF) mit Claude erstellen und prüfen

Diese Anleitung zeigt, was es für "DATEV MCP" heute gibt, warum der Weg über eine EXTF-Datei ohne eigenen API-Zugang funktioniert und wie Sie mit dem Server aus diesem Repository und Claude einen Buchungsstapel erzeugen, prüfen und an Ihre Steuerberatung übergeben.

Stand: 19.10.2026

## Inhaltsverzeichnis

- [Das Wichtigste in Kürze](#das-wichtigste-in-kürze)
- [Was es gibt: DATEV, MCP und die Alternativen](#was-es-gibt-datev-mcp-und-die-alternativen)
- [Warum der Weg über die EXTF-Datei ohne API-Zugang funktioniert](#warum-der-weg-über-die-extf-datei-ohne-api-zugang-funktioniert)
- [Schritt für Schritt: eigener Server mit Claude](#schritt-für-schritt-eigener-server-mit-claude)
- [Die erzeugte Datei](#die-erzeugte-datei)
- [Befunde verstehen und beheben](#befunde-verstehen-und-beheben)
- [Import in DATEV](#import-in-datev)
- [Grenzen](#grenzen)
- [Datenschutz](#datenschutz)
- [Häufige Fragen](#häufige-fragen)
- [Weiterlesen](#weiterlesen)

## Das Wichtigste in Kürze

- DATEV bietet am 19.10.2026 keinen eigenen MCP-Server an. Es gibt Cloud-APIs mit Sandbox und Freigabeprozess, das lokale DATEVconnect und einige Community-Projekte.
- Das DATEV-Format (EXTF) ist eine dokumentierte CSV-Datei. Sie lässt sich ohne API-Zugang und ohne Partnerschaft erzeugen und wird in DATEV importiert.
- Der Server in [`server/extf-buchungsstapel`](../../server/extf-buchungsstapel/README.md) schreibt, liest und prüft Buchungsstapel lokal. Er sendet nichts an DATEV und hat keinen Netzwerkzugriff.
- Die Buchungsdaten gehen aber an das Sprachmodell Ihres KI-Clients. Das ist der wichtigste Punkt beim Datenschutz.
- Ob Konten und BU-Schlüssel stimmen, prüft kein Formatprüfer. Das klären Sie mit Ihrer Steuerberatung.

## Was es gibt: DATEV, MCP und die Alternativen

Wer nach "datev mcp server", "datev claude mcp" oder "datev unternehmen online mcp" sucht, möchte meist eines von zwei Dingen: Buchhaltungsdaten aus DATEV mit einem KI-Assistenten auswerten oder Buchungen aus einem anderen System per Assistent nach DATEV bringen. Für beides lohnt ein Blick darauf, welche Zugänge es überhaupt gibt.

### Offiziell: kein MCP-Server von DATEV

Das [DATEV Developer Portal](https://developer.datev.de/de/) beschreibt API-Produkte mit OAuth 2.0 und OpenID Connect, aber keinen MCP-Endpunkt. Auch "DATEV Unternehmen online" hat am 19.10.2026 keine MCP-Schnittstelle. Jede Lösung, die heute "DATEV MCP" heißt, stammt also von Dritten und nutzt einen der folgenden Zugänge.

### DATEV-Cloud-APIs mit Sandbox und Freigabe

Im Developer Portal registrieren Sie sich, legen eine Organisation und eine App an und abonnieren API-Produkte. Danach haben Sie Zugriff auf eine Sandbox. Für den Produktivbetrieb buchen Sie eine technische Abnahme; Cloud-Integrationen von Drittanbietern durchlaufen einen Freigabeprozess ([Schnittstellenanforderungen](https://developer.datev.de/de/guides/interface-requirements)).

Die DATEV-Cloud-APIs stehen auch ohne Partnerschaft offen, setzen aber Registrierung, Abonnement und für den Produktivbetrieb eine technische Prüfung durch DATEV voraus. Ohne eigenen API-Zugang über das DATEV Developer Portal ist das Dateiformat EXTF der einfachste Weg.

Für Buchungen ist das API-Produkt accounting:extf-files interessant. Es nimmt genau die EXTF-Dateien entgegen, um die es in dieser Anleitung geht, und leitet sie an das DATEV-Rechenzentrum weiter. Laut der Produktdokumentation verlangt es mindestens Header-Version 700 und Buchungsstapel-Format 12, und es prüft beim Upload nur grundlegend; die vollständige Prüfung passiert später in der DATEV-Anwendung ([accounting:extf-files, Erste Schritte](https://developer.datev.de/de/product-detail/accounting-extf-files/2.0/documentation/erste-schritte)).

### DATEVconnect im eigenen Netz

DATEVconnect ist ein lokaler REST-Dienst, der eine installierte DATEV-Umgebung voraussetzt. Ein MCP-Server könnte darauf aufsetzen. Ohne DATEV-Installation lässt sich das nicht testen, und die Details kennen wir nur aus Sekundärquellen. Diese Anleitung behandelt DATEVconnect deshalb nicht weiter.

### Community-Projekte und kommerzielle Angebote

Auf GitHub gibt es kleine MCP-Projekte mit DATEV-Bezug, zum Beispiel (Stand 19.10.2026, Angaben laut GitHub):

| Projekt | Lizenz | Sterne | Letzte Änderung | Ansatz laut Beschreibung |
|---|---|---|---|---|
| `ppronobis/datev-mcp-server` | MIT | 5 | 28.03.2026 | Zugriff von KI-Assistenten auf DATEV-Daten |
| `BadRix90/datev-mcp` | MIT | 2 | 27.07.2026 | Buchhaltungs-Workflows mit DATEV |
| `seamless-engineering/datev-extf-mcp` | MIT | 0 | 26.09.2026 | EXTF-Dateien lokal prüfen und schreiben |

Daneben bieten kommerzielle Dienste eigene MCP-Zugänge, die Daten in Richtung DATEV aufbereiten. Welche Lösung passt, hängt von Ihrem Fall ab: Wie viel Code wollen Sie selbst lesen, wer betreibt den Server, wohin fließen die Daten? Die Kriterien dafür stehen in [MCP-Sicherheit](./mcp-sicherheit.md), eine gepflegte Übersicht in der [Sammelliste](../liste.md).

## Warum der Weg über die EXTF-Datei ohne API-Zugang funktioniert

Das DATEV-Format ist ein Dateiformat, keine Schnittstelle. DATEV beschreibt es öffentlich im Developer Portal: eine CSV-Datei mit dem Präfix `EXTF_`, in Zeile 1 ein Header mit 31 Feldern, in Zeile 2 die Spaltenüberschriften, ab Zeile 3 die Buchungen ([DATEV-Format, Einstieg](https://developer.datev.de/de/file-formats/details/datev-format/getting-started)).

Für eine Datei brauchen Sie weder einen API-Schlüssel noch eine Freigabe. Sie erzeugen sie lokal, prüfen sie lokal und geben sie an die Stelle weiter, die in DATEV bucht, meist Ihre Steuerberatung. Das hat drei Vorteile:

- **Kontrolle**: Zwischen KI-Assistent und Buchhaltung liegt eine Datei, die ein Mensch ansehen kann, bevor etwas gebucht wird.
- **Testbarkeit**: Alles läuft offline. Ein Fehler kostet keine Buchung, sondern einen Befund.
- **Keine Zugangsdaten**: Der MCP-Server kennt keine DATEV-Zugänge und kann deshalb auch keine missbrauchen.

Der Preis: Der Assistent bucht nicht direkt in DATEV. Der Import bleibt ein eigener Schritt, und Daten aus DATEV zurück bekommen Sie nur über einen Export, den jemand in DATEV anstößt.

### Für wen das passt

Der Dateiweg passt gut, wenn Buchungen außerhalb von DATEV entstehen und regelmäßig an die Steuerberatung gehen: Rechnungen aus einem Shop, einer Branchensoftware oder einer Tabelle, Belege aus einem Spesenprozess, Umbuchungen aus einer Auswertung. Der Assistent übernimmt dann das mühsame Übertragen in das starre Format, und die Formatprüfung fängt typische Tippfehler ab.

Weniger geeignet ist er, wenn Sie Auswertungen direkt aus dem DATEV-Bestand brauchen, etwa offene Posten oder eine BWA. Dafür muss jemand in DATEV exportieren, oder Sie brauchen einen Zugang über die DATEV-APIs. Auch für große Mengen ist ein Skript ohne Sprachmodell oft die bessere Wahl; die Kommandozeile `extf-buchungsstapel` im selben Paket erzeugt Dateien direkt aus JSON oder CSV.

### Was der Header festlegt

Der Header bestimmt, in welchen Bestand die Datei gehört und wie DATEV die Buchungen deutet. Ein Beispiel aus diesem Repository:

```text
"EXTF";700;21;"Buchungsstapel";13;20261019211932861;;"";"";"";1001;1;20260101;4;20260901;20260930;"Belege 09/2026";"";1;0;0;"EUR";;"";;;"03";;;"";""
```

Wichtig sind vor allem diese Felder:

| Feld | Wert im Beispiel | Bedeutung |
|---|---|---|
| 2, 3, 5 | `700`, `21`, `13` | Header-Version, Kategorie Buchungsstapel, Formatversion 13 mit 125 Spalten |
| 11, 12 | `1001`, `1` | Beraternummer und Mandantennummer des Bestands |
| 13 | `20260101` | Beginn des Wirtschaftsjahres; daraus ergibt sich das Jahr jedes Belegdatums |
| 14 | `4` | Sachkontenlänge, muss zur Einstellung des Mandanten passen |
| 15, 16 | `20260901`, `20260930` | Zeitraum des Stapels; jedes Belegdatum muss darin liegen |
| 21 | `0` | Festschreibung; leer würde laut DATEV "festschreiben" bedeuten |

## Schritt für Schritt: eigener Server mit Claude

Die folgenden Schritte nutzen Claude Desktop und Claude Code. Für Cursor, VS Code und Codex stehen die Konfigurationen im [README des Servers](../../server/extf-buchungsstapel/README.md#einrichtung-in-mcp-clients) und in [MCP-Clients einrichten](./mcp-clients-einrichten.md).

### 1. Voraussetzungen

- Python 3.11 oder neuer und [uv](https://docs.astral.sh/uv/) (für `uvx`).
- Ein leerer Arbeitsordner, in dieser Anleitung `~/extf-export`. Nur dort liest und schreibt der Server. Er legt den Ordner nicht selbst an; fehlt er, schlagen alle Tools mit einer Fehlermeldung fehl. Legen Sie ihn deshalb vorher an:

  ```bash
  mkdir -p ~/extf-export
  ```

- Die Stammdaten Ihres DATEV-Bestands von Ihrer Steuerberatung: Beraternummer, Mandantennummer, Beginn des Wirtschaftsjahres, Sachkontenlänge und Kontenrahmen.

### 2. Server testen

Prüfen Sie zuerst, ob der Server startet. Mit einem lokalen Klon des Repositorys:

```bash
uvx --from ./server/extf-buchungsstapel extf-buchungsstapel-mcp --version
```

```text
extf-buchungsstapel-mcp 0.1.0
```

Sobald das Repository auf GitHub veröffentlicht ist, geht dasselbe ohne Klon mit `--from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel"`.

### 3. In Claude einbinden

Für Claude Desktop tragen Sie den Server in `claude_desktop_config.json` ein (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`), siehe [Connect to local MCP servers](https://modelcontextprotocol.io/docs/develop/connect-local-servers):

```json
{
  "mcpServers": {
    "extf-buchungsstapel": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel",
        "extf-buchungsstapel-mcp"
      ],
      "env": {
        "EXTF_ORDNER": "/Users/name/extf-export"
      }
    }
  }
}
```

Ersetzen Sie `/Users/name` durch Ihr Home-Verzeichnis (`echo $HOME`). Claude Desktop erwartet einen absoluten Pfad, `~` wird dort nicht aufgelöst.

Für Claude Code reicht ein Befehl ([Claude Code, MCP](https://code.claude.com/docs/en/mcp)):

```bash
mkdir -p ~/extf-export
claude mcp add extf-buchungsstapel -e EXTF_ORDNER="$HOME/extf-export" -- \
  uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel" extf-buchungsstapel-mcp
```

Ohne `-s` gilt der Scope `local`: Der Eintrag steht in `~/.claude.json` und gilt nur für Sie in diesem Projekt. Mit `-s project` landet er stattdessen in der Datei `.mcp.json` im Projektordner, die meist ins Repository kommt. Tragen Sie dort statt Ihres persönlichen Pfads eine Variable ein, wie in [MCP-Clients einrichten](./mcp-clients-einrichten.md#claude-code) gezeigt.

Nach einem Neustart des Clients sehen Sie vier Tools: `buchungsstapel_erstellen`, `extf_pruefen`, `extf_lesen` und `felder_erklaeren`. Nur das erste schreibt, und zwar ausschließlich neue Dateien im Arbeitsordner.

### 4. Ein Beispieldialog

Der folgende Dialog ist ein gekürztes Beispiel. Die Formulierungen des Assistenten hängen vom Modell ab; die Tool-Antworten weiter unten sind echte Ausgaben des Servers.

```text
Sie:      Lege einen Buchungsstapel für September 2026 an. Bestand: Beraternummer 1001,
          Mandant 1, Wirtschaftsjahr ab 01.01.2026, Sachkontenlänge 4, SKR03.
          1) 02.09.2026, Ausgangsrechnung RE2026-0815 an Muster GmbH, 1190,00 brutto,
             Debitor 10000 an 8400.
          2) 15.09.2026, Bürobedarf, Beleg ER-4711, 59,50, 4930 an 1200, Kostenstelle 100.
          3) 30.09.2026, Lieferschein LS/2026/09-1, Nordlicht Beispiel GmbH, 2380,00,
             Kreditor 70000 im Haben gegen 3400.
          Dateiname EXTF_Belege_2026-09.csv.

Claude:   [ruft buchungsstapel_erstellen auf]
          Die Datei EXTF_Belege_2026-09.csv mit 3 Buchungen liegt im Arbeitsordner.
          Die Formatprüfung meldet keine Fehler. Bitte lassen Sie Konten und
          BU-Schlüssel vor dem Import von Ihrer Steuerberatung bestätigen.
```

Die Konten im Beispiel sind nur Platzhalter für die Technik. Welche Konten und Schlüssel für Ihre Vorgänge richtig sind, legt Ihre Steuerberatung fest.

Die Antwort des Tools (`structuredContent`):

```json
{
  "geschrieben": true,
  "datei": "EXTF_Belege_2026-09.csv",
  "buchungen": 3,
  "bytes": 3832,
  "sha256": "42d7d67313cf1b39c55f8a040d1c5938b9273bfbcf1422b9d77525d8780d7142",
  "fehler": 0,
  "warnungen": 0,
  "befunde": [],
  "hinweis": "Datei geschrieben. Prüfen Sie Konten und BU-Schlüssel mit Ihrer Steuerberatung, bevor Sie importieren."
}
```

### 5. Ergebnis kontrollieren

Bitten Sie den Assistenten, die Datei mit `extf_lesen` anzuzeigen, oder nutzen Sie die Kommandozeile `extf-buchungsstapel`, die mit dem Paket kommt. `uvx` installiert sie nicht dauerhaft; ohne Installation rufen Sie sie so auf:

```bash
uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel" \
  extf-buchungsstapel lesen ~/extf-export/EXTF_Belege_2026-09.csv
```

Wer `extf-buchungsstapel` öfter braucht, installiert das Paket aus derselben Quelle mit `uv tool install` oder in einer virtuellen Umgebung (siehe [README des Servers, Abschnitt Installation](../../server/extf-buchungsstapel/README.md#installation)). Dann genügt `extf-buchungsstapel lesen ~/extf-export/EXTF_Belege_2026-09.csv`.

```text
    3 2026-09-02        1190,00 S     10000      8400      RE2026-0815          Muster GmbH Beratung September
    4 2026-09-15          59,50 S      4930      1200      ER-4711              Bürobedarf Größe A4
    5 2026-09-30        2380,00 H     70000      3400      LS/2026/09-1         Nordlicht Beispiel GmbH Wartung
```

Die erste Zahl ist die Zeile in der Datei. Buchungen beginnen in Zeile 3, weil Zeile 1 der Header und Zeile 2 die Spaltenüberschriften sind.

## Die erzeugte Datei

Die Datei ist eine CSV-Datei in Windows-1252 mit CR/LF am Ende jeder Zeile. Das ist der Standardzeichensatz des DATEV-Formats; Unicode akzeptiert DATEV nur mit Byte Order Mark und nicht auf jedem Importweg (DATEV-Format, Navigation "Zeichensatz"). Der Server schreibt deshalb immer Windows-1252. Das Euro-Zeichen wird dabei zum Byte `0x80`, Umlaute zu je einem Byte.

Eine Buchungszeile hat 125 Felder. Der Server füllt die Felder, die für einen einfachen Stapel nötig sind, und lässt die übrigen leer:

```text
1190,00;"S";"";;;"";10000;8400;"";0209;"RE2026-0815";"";;"Muster GmbH Beratung September";;"";;;;"";"";...
```

Was hier passiert:

- `1190,00`: Umsatz mit Komma und genau zwei Nachkommastellen, ohne Vorzeichen. Die Richtung steht im nächsten Feld.
- `"S"`: Soll, bezogen auf das Konto in Feld 7.
- `10000` und `8400`: Konto und Gegenkonto. Mit Sachkontenlänge 4 ist ein fünfstelliges Personenkonto erlaubt.
- `0209`: Belegdatum als TTMM. Das Jahr 2026 ergibt sich aus dem Wirtschaftsjahr im Header.
- Textfelder stehen in Anführungszeichen, auch leere. Ein Anführungszeichen im Text wird verdoppelt.

Feld 114 (Festschreibung) schreibt der Server in jeder Zeile ausdrücklich als `0` oder `1`. Ein leeres Feld bedeutet laut Formatbeschreibung "nicht definiert; wird automatisch festgeschrieben", und eine einzige `1` schreibt den ganzen Stapel fest ([Formatbeschreibung Buchungsstapel](https://developer.datev.de/de/file-formats/details/datev-format/format-description/booking-batch)).

## Befunde verstehen und beheben

Bevor der Server schreibt, prüft er jede Buchung. Bei einem Fehler entsteht keine Datei; stattdessen kommen die Befunde zurück. Ein Beispiel mit zwei typischen Fehlern, einer Belegnummer mit Leerzeichen und Punkt und einem Belegdatum außerhalb des Zeitraums:

```json
{
  "geschrieben": false,
  "fehler": 2,
  "befunde": [
    {
      "code": "BELEGFELD1_ZEICHEN",
      "schwere": "fehler",
      "zeile": 3,
      "feld": "11 Belegfeld 1",
      "wert": "RE 2026.1",
      "meldung": "Unerlaubte Zeichen: ' ', '.'. Erlaubt sind A-Z, a-z, 0-9, _ und $ & % * + - /."
    },
    {
      "code": "BELEGDATUM_AUSSERHALB_ZEITRAUM",
      "schwere": "fehler",
      "zeile": 5,
      "feld": "10 Belegdatum",
      "wert": "0110",
      "meldung": "Belegdatum 01.10.2026 liegt außerhalb des Zeitraums 01.09.2026-30.09.2026."
    }
  ],
  "hinweis": "Die Buchungen enthalten Fehler; es wurde keine Datei geschrieben."
}
```

Der Assistent kann solche Befunde meist selbst beheben, etwa die Belegnummer zu `RE2026-1` umschreiben oder die Oktober-Buchung in einen eigenen Stapel legen. Fragen Sie im Zweifel nach, was er geändert hat.

Häufige Befunde:

| Prüfcode | Ursache | Lösung |
|---|---|---|
| `BELEGFELD1_ZEICHEN` | Leerzeichen, Punkt, Komma oder Umlaut in der Belegnummer | Nur A-Z, a-z, 0-9 und `_ $ & % * + - /` verwenden |
| `BELEGDATUM_AUSSERHALB_ZEITRAUM` | Beleg gehört nicht in den Zeitraum des Stapels | Eigenen Stapel je Monat anlegen oder Zeitraum anpassen |
| `KONTO_ZU_LANG` | Mehr Stellen als Sachkontenlänge + 1 | Sachkontenlänge mit der Steuerberatung klären |
| `BUCHUNGSTEXT_ZU_LANG` | Mehr als 60 Zeichen | Text kürzen |
| `UTF8_OHNE_BOM` | Fremde Datei in UTF-8 ohne Byte Order Mark | Als Windows-1252 oder mit BOM speichern |

Mit `felder_erklaeren` erklärt der Server jeden Code und jedes Feld, zum Beispiel `felder_erklaeren("Belegfeld 1")` oder `felder_erklaeren("Header 14")`. Dateien aus anderen Programmen prüfen Sie mit `extf_pruefen`, wenn sie im Arbeitsordner liegen. Die vollständige Liste der Prüfcodes und ihre Quellen stehen im [README](../../server/extf-buchungsstapel/README.md#prüfcodes) und in der [Spezifikation](../../server/extf-buchungsstapel/SPEZIFIKATION.md).

## Import in DATEV

Den Import macht der Server nicht. DATEV dokumentiert im Developer Portal drei Wege (DATEV-Format, Navigation "Import/Export"):

- **Manuell in DATEV Rechnungswesen** über die Stapelverarbeitung. Das ist der übliche Weg, wenn Sie die Datei Ihrer Steuerberatung schicken.
- **Automatisiert** über das Programm `KrStaPv.exe` der Stapelverarbeitung. Achtung: Dieser Weg unterstützt laut DATEV kein Unicode, eine Datei in Windows-1252 passt.
- **Online** über das API-Produkt accounting:extf-files in das DATEV-Rechenzentrum. Dafür brauchen Sie den Zugang über das Developer Portal mit Freigabe, siehe oben.

DATEV stellt außerdem ein Prüfprogramm für das DATEV-Format zum Download bereit (Navigation "Tools"). Es ist sinnvoll, eine erzeugte Datei vor dem ersten echten Import auch damit zu prüfen. Wir haben das Prüfprogramm und einen echten Import in DATEV Rechnungswesen für diese Anleitung nicht ausprobiert.

Diese Punkte können die Zusammenarbeit mit Ihrer Steuerberatung erleichtern:

1. Eine Datei je Monat und je Art von Vorgang, so wie DATEV es für den Online-Import empfiehlt.
2. Vorher klären: Beraternummer, Mandantennummer, Sachkontenlänge, Kontenrahmen, ob Personenkonten verwendet werden.
3. Die erste Datei als Test schicken und mit der Steuerberatung im Stapel ansehen, bevor regelmäßig importiert wird.
4. Festschreibung im Header auf `0` lassen, damit die Steuerberatung den Stapel vor dem Festschreiben prüfen kann.

## Grenzen

- **Keine steuerliche Prüfung.** Der Server prüft das Format: Längen, Zeichen, Datumsangaben, Zeitraum, Zeichensatz. Ob 8400 das richtige Erlöskonto ist oder ein BU-Schlüssel passt, weiß er nicht.
- **Keine Kontenrahmen.** Er enthält keine SKR03- oder SKR04-Listen und erkennt deshalb keine Automatikkonten.
- **Nur Buchungsstapel.** Debitoren/Kreditoren, Kontenbeschriftungen oder andere Formatkategorien schreibt er nicht.
- **Nur die wichtigsten Felder.** Er füllt Umsatz, Soll/Haben, Währung, Konto, Gegenkonto, BU-Schlüssel, Belegdatum, Belegfelder, Buchungstext, Kostenstellen und Festschreibung. Für Fremdwährung mit Kurs, EU-Angaben, Skonto oder SEPA-Felder bräuchte es Erweiterungen.
- **Nicht jede Regel ist primär belegt.** Die Grenzen von 50 MB und 99.999 Buchungen je Datei stammen aus Sekundärquellen und führen nur zu Warnungen. Welche Regel woher kommt, steht in der [Spezifikation](../../server/extf-buchungsstapel/SPEZIFIKATION.md).
- **Ein Sprachmodell kann sich irren.** Es kann Beträge vertauschen oder Soll und Haben verwechseln, ohne dass ein Formatfehler entsteht. Lesen Sie die Datei vor der Weitergabe.

## Datenschutz

Der Server selbst ist lokal: Er öffnet keine Netzwerkverbindung und speichert nur im Arbeitsordner. Das gilt aber nicht für den Rest der Kette. Alles, was Sie dem Assistenten schreiben, und alles, was die Tools zurückgeben, verarbeitet das Sprachmodell Ihres Clients, in der Regel auf den Servern des Anbieters.

Buchungsdaten enthalten oft personenbezogene Daten: Namen von Kunden und Lieferanten im Buchungstext, Rechnungsnummern, manchmal Hinweise auf Gesundheit oder Gehalt. Klären Sie deshalb vor dem Einsatz mit echten Daten:

- Gibt es mit dem Anbieter des Sprachmodells einen Vertrag zur Auftragsverarbeitung, und wo werden die Daten verarbeitet?
- Werden Eingaben zum Training verwendet? Das regeln die Bedingungen und Einstellungen Ihres Tarifs.
- Welche Daten braucht der Assistent wirklich? Oft reichen Rechnungsnummer und Betrag, Namen sind nicht nötig.

Für Tests nehmen Sie erfundene Daten, etwa die Beispieldateien im Ordner `tests/fixtures` des Servers. Mehr zur rechtlichen Seite steht in [MCP und DSGVO](./mcp-dsgvo.md).

Ein zweites Risiko ist Prompt Injection: Ein Buchungstext in einer fremden Datei kann wie eine Anweisung an den Assistenten formuliert sein. Der Server behandelt solche Texte als Daten und kann ohnehin nur neue Dateien im Arbeitsordner anlegen. Andere Tools in Ihrem Client können mehr; geben Sie Tool-Aufrufe deshalb nur nach Durchsicht frei ([MCP-Sicherheit](./mcp-sicherheit.md)).

## Häufige Fragen

### Gibt es einen offiziellen DATEV MCP Server?

Nein, am 19.10.2026 nicht. DATEV bietet Cloud-APIs über das Developer Portal und das lokale DATEVconnect an. MCP-Server mit DATEV-Bezug stammen von Dritten.

### Kann Claude direkt in DATEV Unternehmen online buchen?

Nicht mit diesem Server. Er erzeugt eine Datei, die Sie oder Ihre Steuerberatung importieren. Ein direkter Upload wäre über das API-Produkt accounting:extf-files möglich, setzt aber den Zugang über das Developer Portal und den Freigabeprozess von DATEV voraus.

### Brauche ich eine DATEV-Lizenz für den Server?

Für das Erzeugen und Prüfen der Datei nicht. Für den Import braucht die Stelle, die bucht, DATEV Rechnungswesen oder einen anderen von DATEV vorgesehenen Importweg.

### Warum schreibt der Server Windows-1252 und nicht UTF-8?

Weil Windows-1252 der Standardzeichensatz des DATEV-Formats ist und auf allen Importwegen funktioniert. UTF-8 versteht DATEV nur mit Byte Order Mark und nicht über die automatisierte Stapelverarbeitung.

### Prüft der Server, ob meine Buchungen steuerlich stimmen?

Nein. Er prüft nur das Dateiformat. Konten, BU-Schlüssel und Steuersätze klären Sie mit Ihrer Steuerberatung.

### Funktioniert das auch mit Cursor, VS Code oder Codex?

Ja, jeder MCP-Client mit stdio-Unterstützung kann den Server starten. Die Konfigurationen stehen im [README des Servers](../../server/extf-buchungsstapel/README.md#einrichtung-in-mcp-clients).

## Weiterlesen

- [Übersicht: MCP-Server für deutsche Geschäftssysteme](../../README.md)
- [MCP-Server-Liste](../liste.md)
- [Was ist ein MCP-Server?](./was-ist-ein-mcp-server.md)
- [Einen eigenen MCP-Server erstellen](./mcp-server-erstellen.md)
- [MCP-Sicherheit](./mcp-sicherheit.md)
- [MCP für die Buchhaltung](./buchhaltung-mcp.md)
- [MCP-Clients einrichten](./mcp-clients-einrichten.md)
- [README des EXTF-Servers](../../server/extf-buchungsstapel/README.md)

> **Hinweis:** Technische Informationen nach Stand 19.10.2026, ohne Gewähr für Vollständigkeit und Richtigkeit. Keine Rechts- oder Steuerberatung; die Autoren sind keine Rechtsanwälte, Steuerberater oder Datenschutzbeauftragten. Produktnamen sind Marken ihrer Inhaber; es besteht keine Verbindung zu den genannten Herstellern.

> Die Autoren erbringen keine Hilfeleistung in Steuersachen im Sinne des Steuerberatungsgesetzes. Ob und wie Buchungen steuerlich richtig sind, klären Sie mit Ihrer Steuerberatung. DATEV ist eine Marke der DATEV eG; dieses Projekt ist kein Produkt der DATEV eG und nicht von ihr geprüft oder freigegeben.
