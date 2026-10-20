# extf-buchungsstapel-mcp: MCP-Server für Buchungsstapel im DATEV-Format (EXTF)

Ein lokaler MCP-Server und ein Kommandozeilenwerkzeug, die Buchungsstapel im DATEV-Format (EXTF) schreiben, lesen und auf Formatfehler prüfen. Alles läuft auf Ihrem Rechner, ohne Netzwerkzugriff und ohne Verbindung zu DATEV. Dieses Projekt ist kein Produkt der DATEV eG. Es ist auch nicht mit Projekten Dritter zum selben Thema verbunden, etwa `seamless-engineering/datev-extf-mcp`.

Stand: 20.10.2026

## Inhalt

- [Was der Server kann und was nicht](#was-der-server-kann-und-was-nicht)
- [Werkzeuge](#werkzeuge)
- [Installation](#installation)
- [Arbeitsordner](#arbeitsordner)
- [Einrichtung in MCP-Clients](#einrichtung-in-mcp-clients)
- [Beispiele](#beispiele)
- [Eingabeformat](#eingabeformat)
- [Kommandozeile](#kommandozeile)
- [Prüfcodes](#prüfcodes)
- [Sicherheit](#sicherheit)
- [Tests](#tests)
- [Haftung und Lizenz](#haftung-und-lizenz)

## Was der Server kann und was nicht

Der Server kann:

- eine neue Datei `EXTF_...csv` im Format Buchungsstapel (Header-Version 700, Formatkategorie 21, Formatversion 13, 125 Spalten) erzeugen, in Windows-1252 mit CR/LF,
- vorhandene Buchungsstapel-Dateien lesen (Windows-1252, UTF-8 mit oder ohne BOM, UTF-16 mit BOM) und seitenweise als strukturierte Buchungen zurückgeben,
- Header, Spaltenzeile und Buchungszeilen gegen die Formatbeschreibung prüfen und jeden Befund mit Prüfcode, Zeile, Feld und deutscher Meldung melden,
- jedes der 125 Felder, die 31 Header-Felder und alle Prüfcodes erklären.

Der Server kann nicht und soll nicht:

- **nichts hochladen**: Er sendet keine Daten an DATEV, an DATEV Unternehmen online oder an andere Dienste. Er hat keinen Netzwerkzugriff.
- **keine steuerliche Prüfung**: Ob Konto, Gegenkonto, BU-Schlüssel und Steuersatz richtig sind, prüft er nicht. Er enthält keine Kontenrahmen (SKR03, SKR04).
- **kein Import**: Den Import in DATEV Rechnungswesen oder über eine DATEV-Schnittstelle machen Sie oder Ihre Steuerberatung selbst.
- **keine anderen Formate**: Debitoren/Kreditoren, Sachkontenbeschriftungen oder andere Formatkategorien sind nicht enthalten.

Welche Regeln umgesetzt sind und welche Quelle dahinter steht (primär bei DATEV belegt, abgeleitet, sekundär oder ungeprüft), steht in [SPEZIFIKATION.md](SPEZIFIKATION.md).

## Werkzeuge

| Tool | Zweck | Schreibt? | Annotations |
|---|---|---|---|
| `buchungsstapel_erstellen` | Kopfdaten und Buchungen prüfen und als neue Datei in den Arbeitsordner schreiben. Bei Fehlern wird nichts geschrieben, die Befunde kommen zurück. | ja, nur neue Dateien | `readOnlyHint: false`, `destructiveHint: false`, `idempotentHint: false`, `openWorldHint: false` |
| `extf_pruefen` | Eine Datei im Arbeitsordner prüfen | nein | `readOnlyHint: true`, `idempotentHint: true`, `openWorldHint: false` |
| `extf_lesen` | Buchungen einer Datei lesen, mit `limit` (1-1000, Vorgabe 100) und `offset` | nein | `readOnlyHint: true`, `idempotentHint: true`, `openWorldHint: false` |
| `felder_erklaeren` | Feldnummer (z. B. `11`), Feldname (z. B. `Belegfeld 1`), `Header 14` oder Prüfcode erklären | nein | `readOnlyHint: true`, `idempotentHint: true`, `openWorldHint: false` |

Alle Tools haben ein `inputSchema` und ein `outputSchema` und liefern `structuredContent`. Ressourcen und Prompts bietet der Server nicht an; die vier Tools decken die Aufgaben ab.

## Installation

Voraussetzung ist Python 3.11 oder neuer. Am einfachsten starten Sie den Server mit [uv](https://docs.astral.sh/uv/), dann ist keine eigene Installation nötig:

```bash
uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel" extf-buchungsstapel-mcp --version
```

Dieser Aufruf funktioniert, sobald das Repository auf GitHub veröffentlicht ist; am 20.10.2026 war es das noch nicht. Getestet ist derselbe Aufruf mit einem lokalen Klon. Die folgenden Befehle gelten aus der Wurzel des Klons (dem Ordner `mcp-server-deutschland`):

```bash
uvx --from ./server/extf-buchungsstapel extf-buchungsstapel-mcp --version
```

```text
extf-buchungsstapel-mcp 0.1.0
```

Das Paket bringt zwei Befehle mit: `extf-buchungsstapel-mcp` (MCP-Server über stdio, wird vom Client gestartet) und `extf-buchungsstapel` (Kommandozeile). Einzige Abhängigkeit ist das offizielle MCP-SDK für Python (`mcp>=2.3,<3`).

`uvx` installiert nichts dauerhaft. Die Kommandozeile rufen Sie darum ebenfalls über `uvx` auf, mit dem Befehlsnamen `extf-buchungsstapel` statt `extf-buchungsstapel-mcp`:

```bash
uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel" \
  extf-buchungsstapel prüfen ~/extf-export/EXTF_Belege_2026-09.csv
```

Wer die Kommandozeile öfter braucht, installiert das Paket in einer virtuellen Umgebung (aus der Wurzel des Klons). Danach liegen beide Befehle in `.venv/bin/`:

```bash
python3 -m venv .venv
.venv/bin/pip install ./server/extf-buchungsstapel
.venv/bin/extf-buchungsstapel-mcp --version
.venv/bin/extf-buchungsstapel --version
```

Mit `. .venv/bin/activate` stehen sie in dieser Shell ohne Pfad zur Verfügung. Installieren Sie das Paket nicht global mit `pip install` außerhalb einer virtuellen Umgebung.

## Arbeitsordner

Der Server liest und schreibt nur in einem Ordner, den Sie über die Umgebungsvariable `EXTF_ORDNER` festlegen. Der Ordner muss existieren, der Server legt ihn nicht an, und der Pfad muss absolut sein. In dieser Anleitung heißt er überall `~/extf-export`:

```bash
mkdir -p ~/extf-export
```

- Dateinamen sind nur einfache Namen wie `EXTF_Buchungsstapel_2026-09.csv`: Buchstaben, Ziffern, `_` und `-`, Endung `.csv`, keine Ordner, kein `..`.
- Bestehende Dateien werden nie überschrieben. Ist der Name belegt, meldet das Tool einen Fehler.
- Symbolische Links, Dateien mit mehreren harten Links und andere Dateiarten als normale Dateien werden nicht gelesen.
- Unter Windows reservierte Gerätenamen wie `CON.csv` oder `NUL.csv` werden abgelehnt.
- Neue Dateien erhalten die Rechte `0600` (nur Ihr Benutzer).

Ist die Variable nicht gesetzt, startet der Server trotzdem, meldet aber bei jedem Datei-Tool einen Fehler mit Hinweis auf `EXTF_ORDNER`. `felder_erklaeren` funktioniert auch ohne Ordner.

## Einrichtung in MCP-Clients

In allen Beispielen steht `/Users/name/extf-export` für Ihren Arbeitsordner `~/extf-export`; tragen Sie den vollen Pfad ein. Der Server löst zwar ein führendes `~` selbst auf, der volle Pfad ist aber eindeutiger. Unter Windows schreiben Sie den Pfad z. B. als `C:\\Users\\name\\extf-export` (in JSON mit doppeltem Backslash). Findet der Client `uvx` nicht, tragen Sie den vollen Pfad ein (Ausgabe von `which uvx` bzw. `where uvx`).

### Claude Desktop

Datei `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`), Schlüssel `mcpServers`. Quelle: [modelcontextprotocol.io, Connect to local MCP servers](https://modelcontextprotocol.io/docs/develop/connect-local-servers).

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

Danach Claude Desktop neu starten.

### Claude Code

Quelle: [Claude Code, MCP](https://code.claude.com/docs/en/mcp) und `claude mcp add --help`. Der folgende Befehl wurde mit einem lokalen Pfad statt der GitHub-Adresse ausprobiert:

```bash
mkdir -p "$HOME/extf-export"
claude mcp add extf-buchungsstapel -e EXTF_ORDNER="$HOME/extf-export" -- \
  uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel" extf-buchungsstapel-mcp
```

Ohne `-s` gilt der Scope `local`: Der Eintrag steht in `~/.claude.json` und gilt nur für Sie in diesem Projekt. Soll er in der Datei `.mcp.json` des Projekts landen, geben Sie `-s project` an (`claude mcp add -s project extf-buchungsstapel ...`). Weil `.mcp.json` meist eingecheckt wird, gehört Ihr persönlicher Pfad dann nicht hinein; schreiben Sie stattdessen `-e 'EXTF_ORDNER=${EXTF_ORDNER}'` und setzen Sie die Variable in Ihrer Shell. Mit `-s user` gilt der Eintrag für alle Ihre Projekte.

### Cursor

Datei `.cursor/mcp.json` im Projekt oder `~/.cursor/mcp.json` global, Schlüssel `mcpServers`. Quelle: [Cursor, Model Context Protocol](https://cursor.com/docs/context/mcp).

```json
{
  "mcpServers": {
    "extf-buchungsstapel": {
      "type": "stdio",
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

### VS Code (GitHub Copilot)

Datei `.vscode/mcp.json` im Projekt oder `mcp.json` im Benutzerprofil. Achtung: Der Schlüssel heißt hier `servers`. Quelle: [VS Code, MCP configuration reference](https://code.visualstudio.com/docs/copilot/reference/mcp-configuration).

```json
{
  "servers": {
    "extf-buchungsstapel": {
      "type": "stdio",
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

### Codex

Datei `~/.codex/config.toml` (oder `.codex/config.toml` in vertrauenswürdigen Projekten). Quelle: [OpenAI Codex, MCP](https://developers.openai.com/codex/mcp). Der Befehl

```bash
codex mcp add extf-buchungsstapel --env EXTF_ORDNER=/Users/name/extf-export -- \
  uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel" extf-buchungsstapel-mcp
```

erzeugt diesen Eintrag (ausprobiert mit einem separaten `CODEX_HOME`):

```toml
[mcp_servers.extf-buchungsstapel]
command = "uvx"
args = ["--from", "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel", "extf-buchungsstapel-mcp"]

[mcp_servers.extf-buchungsstapel.env]
EXTF_ORDNER = "/Users/name/extf-export"
```

## Beispiele

Die Ausgaben unten stammen aus echten Aufrufen mit dem offiziellen MCP-Client für Python (Testdaten aus `tests/fixtures/eingabe_beispiel.json`, Beraternummer 1001, Mandant 1).

Konten, Gegenkonten und BU-Schlüssel in allen Beispielen sind frei gewählte Platzhalter für die Technik und keine Empfehlung für eine Kontierung. Welche Konten und Schlüssel für Ihre Vorgänge richtig sind, legt Ihre Steuerberatung fest.

### Buchungsstapel erstellen

Aufruf von `buchungsstapel_erstellen` (gekürzt, die dritte Buchung ist weggelassen):

```json
{
  "kopf": {
    "beraternummer": 1001,
    "mandantennummer": 1,
    "wj_beginn": "2026-01-01",
    "sachkontenlaenge": 4,
    "datum_von": "2026-09-01",
    "datum_bis": "2026-09-30",
    "bezeichnung": "Belege 09/2026",
    "sachkontenrahmen": "03"
  },
  "buchungen": [
    {"belegdatum": "2026-09-02", "umsatz": "1190,00", "soll_haben": "S", "konto": "10000",
     "gegenkonto": "8400", "belegfeld1": "RE2026-0815", "buchungstext": "Muster GmbH Beratung September"},
    {"belegdatum": "2026-09-15", "umsatz": 59.5, "soll_haben": "S", "konto": 4930,
     "gegenkonto": 1200, "belegfeld1": "ER-4711", "buchungstext": "Bürobedarf Größe A4", "kost1": "100"}
  ],
  "dateiname": "EXTF_Belege_2026-09.csv"
}
```

Antwort (`structuredContent`):

```json
{
  "geschrieben": true,
  "datei": "EXTF_Belege_2026-09.csv",
  "buchungen": 3,
  "bytes": 3832,
  "sha256": "42d7d67313cf1b39c55f8a040d1c5938b9273bfbcf1422b9d77525d8780d7142",
  "kopfzeile": "\"EXTF\";700;21;\"Buchungsstapel\";13;20261019211932861;;\"\";\"\";\"\";1001;1;20260101;4;20260901;20260930;\"Belege 09/2026\";\"\";1;0;0;\"EUR\";;\"\";;;\"03\";;;\"\";\"\"",
  "fehler": 0,
  "warnungen": 0,
  "befunde": [],
  "hinweis": "Datei geschrieben. Prüfen Sie Konten und BU-Schlüssel mit Ihrer Steuerberatung, bevor Sie importieren."
}
```

Die erste Buchungszeile der Datei (gekürzt, insgesamt 125 Felder):

```text
1190,00;"S";"";;;"";10000;8400;"";0209;"RE2026-0815";"";;"Muster GmbH Beratung September";;"";;;;"";"";...
```

Das Belegdatum steht als `0209` (TTMM) in der Datei; das Jahr ergibt sich aus dem Beginn des Wirtschaftsjahres im Header. Der Header setzt die Festschreibung (Feld 21) ausdrücklich auf `0`, weil ein leeres Feld bei DATEV "festschreiben" bedeutet.

### Fehlerhafte Eingabe

Mit `"belegfeld1": "RE 2026.1"` in der ersten und `"belegdatum": "2026-10-01"` in der dritten Buchung schreibt der Server nichts und antwortet:

```json
{
  "geschrieben": false,
  "datei": null,
  "buchungen": 3,
  "bytes": null,
  "sha256": null,
  "kopfzeile": null,
  "fehler": 2,
  "warnungen": 0,
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

`zeile` zählt wie in der Datei: Zeile 1 ist der Header, Zeile 2 die Spaltenüberschriften, die erste Buchung steht in Zeile 3.

### Datei lesen

`extf_lesen` mit `{"datei": "EXTF_Belege_2026-09.csv", "limit": 1}` liefert (Kopf gekürzt):

```json
{
  "datei": "EXTF_Belege_2026-09.csv",
  "kopf": {"kennzeichen": "EXTF", "formatversion": 13, "beraternummer": 1001, "mandantennummer": 1,
           "wj_beginn": "2026-01-01", "sachkontenlaenge": 4, "datum_von": "2026-09-01", "datum_bis": "2026-09-30"},
  "spalten": 125,
  "buchungen_gesamt": 3,
  "offset": 0,
  "buchungen": [
    {"zeile": 3, "umsatz": "1190,00", "soll_haben": "S", "wkz": "", "konto": "10000", "gegenkonto": "8400",
     "bu_schluessel": "", "belegdatum": "0209", "belegdatum_iso": "2026-09-02", "belegfeld1": "RE2026-0815",
     "belegfeld2": "", "buchungstext": "Muster GmbH Beratung September", "kost1": "", "kost2": "",
     "festschreibung": "0"}
  ],
  "weitere": true,
  "fehler": 0
}
```

### Unerlaubter Pfad

`extf_pruefen` mit `{"datei": "../geheim.csv"}` endet mit `isError: true` und dem Text:

```text
Error executing tool extf_pruefen: Nur ein Dateiname ohne Ordner ist erlaubt (keine / oder \).
```

## Eingabeformat

`buchungsstapel_erstellen` und `extf-buchungsstapel erstellen` erwarten dieselben Schlüssel.

Kopf (`kopf`):

| Schlüssel | Pflicht | Beispiel | Hinweis |
|---|---|---|---|
| `beraternummer` | ja | `1001` | 1001-9999999 |
| `mandantennummer` | ja | `1` | 1-99999 |
| `wj_beginn` | ja | `"2026-01-01"` | Beginn des Wirtschaftsjahres |
| `sachkontenlaenge` | ja | `4` | 4-8, wie beim Mandanten in DATEV eingestellt |
| `datum_von`, `datum_bis` | ja | `"2026-09-01"` | Zeitraum des Stapels, innerhalb eines Wirtschaftsjahres |
| `bezeichnung` | nein | `"Belege 09/2026"` | höchstens 30 Zeichen |
| `diktatkuerzel` | nein | `"MM"` | 2 oder 4 Großbuchstaben |
| `festschreibung` | nein | `false` | Vorgabe `false` |
| `wkz` | nein | `"EUR"` | Vorgabe `EUR` |
| `sachkontenrahmen` | nein | `"03"` | nur Kennzeichen, keine Prüfung der Konten |

Buchungen (`buchungen`, Liste):

| Schlüssel | Pflicht | Beispiel | Hinweis |
|---|---|---|---|
| `belegdatum` | ja | `"2026-09-02"` | auch `02.09.2026` oder `20260902` |
| `umsatz` | ja | `"1190,00"` oder `1190.00` | positiv, höchstens 2 Nachkommastellen, kein Tausenderpunkt: `"1.190"` oder `"10.000"` werden als mehrdeutig abgelehnt |
| `soll_haben` | ja | `"S"` | `S` oder `H`, bezogen auf `konto` |
| `konto`, `gegenkonto` | ja | `"10000"`, `"8400"` | nur Ziffern; Sachkontenlänge, Personenkonten eine Stelle mehr |
| `bu_schluessel` | nein | weglassen oder 4 Ziffern | 4 Ziffern laut DATEV-Ausdruck; 1-3 Ziffern werden unverändert geschrieben, mit Warnung `BU_SCHLUESSEL_KURZ` |
| `belegfeld1` | nein | `"RE2026-0815"` | höchstens 36 Zeichen: A-Z, a-z, 0-9, `_ $ & % * + - /` |
| `belegfeld2` | nein | `"30092026"` | höchstens 12 Zeichen, gleiche Zeichen wie `belegfeld1` |
| `buchungstext` | nein | `"Muster GmbH"` | höchstens 60 Zeichen, nicht mit `=` oder `@` am Anfang |
| `kost1`, `kost2` | nein | `"100"` | höchstens 36 Zeichen: Buchstaben (auch Umlaute), Ziffern, `_` und Leerzeichen |
| `festschreibung` | nein | weglassen | leer = Wert aus dem Kopf. `true` bei einer einzigen Buchung würde laut DATEV den ganzen Stapel festschreiben; steht im Kopf `false`, lehnt der Server das als Fehler `FESTSCHREIBUNG_EINZELN` ab |
| `wkz` | nein | `"EUR"` | Währung des Umsatzes |

Für die Kommandozeile gibt es zusätzlich ein CSV-Format (UTF-8, Trennzeichen `;`, `,` oder Tab, erste Zeile mit den Schlüsseln). Die Kopfdaten kommen dann aus einer eigenen JSON-Datei, die nur die Schlüssel aus der Tabelle "Kopf" enthält, ohne umschließendes `kopf`. Beispiele liegen in `tests/fixtures`: `eingabe_beispiel.json` (Kopf und Buchungen), `eingabe_beispiel.csv` (nur Buchungen) und `kopf_beispiel.json` (nur Kopf).

## Kommandozeile

Die Befehle in diesem Abschnitt gelten aus dem Ordner `server/extf-buchungsstapel` eines lokalen Klons, weil dort die Beispieldateien liegen, und setzen voraus, dass `extf-buchungsstapel` aufrufbar ist (siehe [Installation](#installation); ohne Installation schreiben Sie `uvx --from . extf-buchungsstapel` statt `extf-buchungsstapel`). Erzeugte Dateien `EXTF_*.csv` in diesem Ordner sind per `.gitignore` von Git ausgenommen.

```bash
extf-buchungsstapel erstellen tests/fixtures/eingabe_beispiel.json -o EXTF_Belege_2026-09.csv
extf-buchungsstapel prüfen EXTF_Belege_2026-09.csv
extf-buchungsstapel lesen EXTF_Belege_2026-09.csv
```

```text
EXTF_Belege_2026-09.csv: 3 Buchungen, 3832 Bytes geschrieben (Windows-1252, CR/LF).
EXTF_Belege_2026-09.csv: 3 Buchungen, 0 Fehler, 0 Warnungen, 0 Hinweise, Zeichensatz windows-1252
    3 2026-09-02        1190,00 S     10000      8400      RE2026-0815          Muster GmbH Beratung September
    4 2026-09-15          59,50 S      4930      1200      ER-4711              Bürobedarf Größe A4
    5 2026-09-30        2380,00 H     70000      3400      LS/2026/09-1         Nordlicht Beispiel GmbH Wartung
```

Eine Datei mit Fehlern (Exit-Code 1):

```text
WARNUNG  ZEILE_ZU_WENIGE_FELDER             Zeile 3: 17 statt 125 Felder.
FEHLER   BELEGFELD1_ZEICHEN                 Zeile 3, 11 Belegfeld 1: Unerlaubte Zeichen: ' ', '.'. Erlaubt sind A-Z, a-z, 0-9, _ und $ & % * + - /.
HINWEIS  FESTSCHREIBUNG_LEER                Zeile 3: Feld 114 (Festschreibung) ist in 1 Buchung(en) leer, zuerst in Zeile 3. Laut DATEV bedeutet leer 'nicht definiert; wird automatisch festgeschrieben'.
EXTF_fehler.csv: 1 Buchungen, 1 Fehler, 1 Warnungen, 1 Hinweise, Zeichensatz windows-1252
```

CSV-Eingabe mit eigener Kopfdatei:

```bash
extf-buchungsstapel erstellen tests/fixtures/eingabe_beispiel.csv --kopf tests/fixtures/kopf_beispiel.json -o EXTF_Belege_2026-09_csv.csv
```

```text
EXTF_Belege_2026-09_csv.csv: 3 Buchungen, 3829 Bytes geschrieben (Windows-1252, CR/LF).
```

Die Datei ist 3 Bytes kürzer als die aus dem JSON-Beispiel, weil die CSV-Eingabe keine Kostenstelle `100` enthält.

Weitere Befehle: `extf-buchungsstapel erklären "Belegfeld 1"`, `extf-buchungsstapel prüfen DATEI --json`, `extf-buchungsstapel lesen DATEI --limit 10 --offset 20`. `erstellen` überschreibt nie (Exit-Code 2, wenn die Zieldatei existiert). Die Kommandozeile ist nicht auf den Arbeitsordner beschränkt; sie schreibt dorthin, wo Sie es angeben.

## Prüfcodes

Schwere `fehler` heißt: Die Datei entspricht an dieser Stelle nicht der Formatbeschreibung, der Server schreibt so eine Datei nicht. `warnung` heißt: wahrscheinlich ein Problem, aber nicht sicher belegt oder von DATEV toleriert. `hinweis` dient der Information. Einige Codes gelten nur beim Schreiben (`FORMELZEICHEN_BEIM_SCHREIBEN`, `FESTSCHREIBUNG_EINZELN`, `BELEGDATUM_AUSSERHALB_WJ`, `ZEICHEN_NICHT_CP1252`, `EINGABE_UNGUELTIG`); dort ist der Server bewusst strenger als beim Prüfen fremder Dateien. Die Spalte "Beleg" verweist auf die Einstufung in [SPEZIFIKATION.md](SPEZIFIKATION.md).

Der Server kennt 83 Prüfcodes:

| Prüfcode | Schwere | Bedeutung | Beleg |
|---|---|---|---|
| `DATEI_LEER` | fehler | Die Datei ist leer. | primär |
| `DATEI_ZU_GROSS` | warnung | Die Datei ist größer als 50 MB. Für den Upload über den Buchungsdatenservice wird eine Grenze von 50 MB genannt. | sekundär |
| `DATEINAME_PRAEFIX` | warnung | Der Dateiname beginnt nicht mit EXTF_ und endet nicht auf .csv. DATEV nennt ein festes Präfix EXTF_. | primär |
| `ZEICHENSATZ_UNGUELTIG` | fehler | Die Datei lässt sich weder als Windows-1252 noch als Unicode mit BOM lesen. | primär |
| `UTF8_OHNE_BOM` | warnung | Die Datei ist UTF-8 ohne Byte Order Mark. DATEV liest Unicode nur mit BOM, sonst als Windows-1252; Umlaute werden dann falsch dargestellt. | primär |
| `UNICODE_MIT_BOM` | hinweis | Die Datei ist Unicode mit BOM. Das geht laut DATEV beim manuellen Import und über die API accounting:extf-files, nicht mit dem Programm KrStaPv. | primär |
| `ZEILENENDE_KEIN_CRLF` | fehler | Eine Zeile endet nicht mit CR/LF. DATEV verlangt CR/LF am Ende jeder Zeile. | primär |
| `LETZTE_ZEILE_OHNE_CRLF` | warnung | Die letzte Zeile endet nicht mit CR/LF. | primär |
| `ANFUEHRUNGSZEICHEN_OFFEN` | fehler | Ein Textfeld ist nicht korrekt in Anführungszeichen eingeschlossen. Anführungszeichen im Text müssen verdoppelt werden. | primär |
| `STEUERZEICHEN` | fehler | Ein Feld enthält ein Steuerzeichen (z. B. Tabulator oder Zeilenumbruch). Das ist in Textfeldern nicht zulässig. | primär |
| `KEINE_BUCHUNGEN` | warnung | Die Datei enthält keine Buchungszeilen. | abgeleitet |
| `ZU_VIELE_BUCHUNGEN` | warnung | Mehr als 99.999 Buchungen in einer Datei. Für den Buchungsdatenservice wird diese Grenze genannt. Die Buchungszeilen werden dann nicht gelesen und nicht geprüft. | sekundär |
| `BEFUNDE_GEKUERZT` | hinweis | Ab 10.000 Befunden werden weitere Befunde nur noch gezählt, nicht einzeln aufgeführt. Die Zahlen für Fehler, Warnungen und Hinweise enthalten sie trotzdem. | abgeleitet |
| `HEADER_FELDANZAHL` | fehler | Der Header hat nicht genau 31 Felder. | primär |
| `HEADER_KENNZEICHEN` | fehler | Feld 1 des Headers ist nicht "EXTF" (Fremdsoftware) oder "DTVF" (DATEV-Programm). | primär |
| `HEADER_KENNZEICHEN_DTVF` | warnung | Kennzeichen DTVF steht für Exporte aus DATEV-Programmen. Dateien aus Fremdsoftware tragen EXTF. | primär |
| `HEADER_VERSION` | fehler | Die Header-Version (Feld 2) ist nicht 700. | primär |
| `HEADER_FORMATKATEGORIE` | fehler | Die Formatkategorie (Feld 3) ist nicht 21 (Buchungsstapel). Andere Kategorien prüft dieses Werkzeug nicht. | primär |
| `HEADER_FORMATNAME` | fehler | Der Formatname (Feld 4) ist nicht "Buchungsstapel". | primär |
| `HEADER_FORMATVERSION` | fehler | Die Formatversion (Feld 5) ist nicht 13 (oder 12). | primär |
| `HEADER_FORMATVERSION_ALT` | warnung | Formatversion 12 ist älter; aktuell ist 13. Für den Buchungsdatenservice nennt DATEV mindestens 12. | primär |
| `HEADER_ZEITSTEMPEL` | fehler | Der Zeitstempel (Feld 6) hat nicht das Format JJJJMMTTHHMMSSmmm. | primär |
| `HEADER_BERATERNUMMER` | fehler | Die Beraternummer (Feld 11) liegt nicht zwischen 1001 und 9999999. | primär |
| `HEADER_MANDANTENNUMMER` | fehler | Die Mandantennummer (Feld 12) liegt nicht zwischen 1 und 99999. | primär |
| `HEADER_WJ_BEGINN` | fehler | WJ-Beginn (Feld 13) ist kein gültiges Datum JJJJMMTT. | primär |
| `HEADER_SACHKONTENLAENGE` | fehler | Die Sachkontenlänge (Feld 14) liegt nicht zwischen 4 und 8. | primär |
| `HEADER_DATUM_VON` | fehler | Datum von (Feld 15) ist kein gültiges Datum JJJJMMTT. | primär |
| `HEADER_DATUM_BIS` | fehler | Datum bis (Feld 16) ist kein gültiges Datum JJJJMMTT. | primär |
| `HEADER_ZEITRAUM` | fehler | Datum von liegt nach Datum bis. | abgeleitet |
| `HEADER_ZEITRAUM_AUSSERHALB_WJ` | fehler | Der Zeitraum des Stapels liegt nicht vollständig im Wirtschaftsjahr ab WJ-Beginn. Weil das Belegdatum kein Jahr enthält, muss der Stapel in einem Wirtschaftsjahr liegen. | abgeleitet |
| `HEADER_BEZEICHNUNG` | warnung | Die Bezeichnung (Feld 17) ist länger als 30 Zeichen oder enthält andere Zeichen als Buchstaben, Ziffern, _, Punkt, Schrägstrich und Leerzeichen. | primär |
| `HEADER_DIKTATKUERZEL` | warnung | Das Diktatkürzel (Feld 18) ist nicht leer, 2 oder 4 Großbuchstaben. | primär |
| `HEADER_BUCHUNGSTYP` | fehler | Der Buchungstyp (Feld 19) ist nicht 1 oder 2. | primär |
| `HEADER_RECHNUNGSLEGUNGSZWECK` | fehler | Der Rechnungslegungszweck (Feld 20) ist nicht 0, 30, 40, 50 oder 64. | primär |
| `HEADER_FESTSCHREIBUNG` | fehler | Die Festschreibung (Feld 21) ist nicht 0 oder 1. | primär |
| `HEADER_FESTSCHREIBUNG_LEER` | hinweis | Feld 21 (Festschreibung) ist leer; DATEV verwendet dann die Vorgabe 1 = Festschreibung. | primär |
| `HEADER_WKZ` | fehler | Die Währung (Feld 22) besteht nicht aus 3 Großbuchstaben. | primär |
| `HEADER_SACHKONTENRAHMEN` | warnung | Der Sachkontenrahmen (Feld 27) ist nicht leer, 2 oder 4 Ziffern. | primär |
| `HEADER_FELD` | warnung | Ein weiteres Header-Feld entspricht nicht dem regulären Ausdruck der Formatbeschreibung (Länge oder Leerfeld). | primär |
| `SPALTENZEILE_FEHLT` | fehler | Zeile 2 mit den Spaltenüberschriften fehlt. | primär |
| `SPALTENANZAHL` | fehler | Die Spaltenzeile hat nicht 125 Spalten (Formatversion 13) bzw. 124 (Formatversion 12). | primär |
| `VERSION_GEMISCHT` | fehler | Header und Spaltenzeile gehören zu unterschiedlichen Formatversionen (z. B. Header 12, aber 125 Spalten). | abgeleitet |
| `SPALTENNAME_ABWEICHEND` | warnung | Eine Spaltenüberschrift weicht von der DATEV-Schreibweise ab. | primär |
| `SPALTENNAME_SCHREIBWEISE` | hinweis | Eine Spaltenüberschrift weicht nur in Bindestrich oder Leerzeichen von der DATEV-Schreibweise ab. | primär |
| `ZEILE_ZU_VIELE_FELDER` | fehler | Eine Buchungszeile hat mehr Felder als die Spaltenzeile. | abgeleitet |
| `ZEILE_ZU_WENIGE_FELDER` | warnung | Eine Buchungszeile hat weniger Felder als die Spaltenzeile; fehlende Felder werden hier als leer gelesen. Wie DATEV das behandelt, ist ungeprüft. | abgeleitet |
| `UMSATZ_FEHLT` | fehler | Der Umsatz (Feld 1) ist leer. | primär |
| `UMSATZ_FORMAT` | fehler | Der Umsatz hat nicht das Format 1234,56 (Komma als Dezimaltrenner, höchstens 10 Vor- und 2 Nachkommastellen, kein Tausenderpunkt). | primär |
| `UMSATZ_OHNE_NACHKOMMA` | warnung | Der Umsatz hat keine zwei Nachkommastellen (z. B. 100 statt 100,00). Die Formatbeschreibung verlangt sie; die DATEV-Musterdatei enthält trotzdem solche Werte. | primär |
| `UMSATZ_NICHT_POSITIV` | fehler | Der Umsatz ist 0 oder negativ. Er muss positiv sein; die Richtung steht im Soll/Haben-Kennzeichen. | primär |
| `SOLL_HABEN_UNGUELTIG` | fehler | Das Soll/Haben-Kennzeichen (Feld 2) ist nicht "S" oder "H". | primär |
| `KONTO_FEHLT` | fehler | Konto (Feld 7) ist leer. | primär |
| `KONTO_FORMAT` | fehler | Konto enthält andere Zeichen als Ziffern oder besteht nur aus Nullen. | primär |
| `KONTO_ZU_LANG` | fehler | Konto ist länger als Sachkontenlänge + 1 (Personenkonten dürfen nur eine Stelle länger sein als Sachkonten). | primär |
| `GEGENKONTO_FEHLT` | fehler | Gegenkonto (Feld 8) ist leer. | primär |
| `GEGENKONTO_FORMAT` | fehler | Gegenkonto enthält andere Zeichen als Ziffern oder besteht nur aus Nullen. | primär |
| `GEGENKONTO_ZU_LANG` | fehler | Gegenkonto ist länger als Sachkontenlänge + 1. | primär |
| `KONTO_GLEICH_GEGENKONTO` | warnung | Konto und Gegenkonto sind gleich. | abgeleitet |
| `BU_SCHLUESSEL_FORMAT` | fehler | Der BU-Schlüssel (Feld 9) enthält andere Zeichen als Ziffern oder mehr als 4 Ziffern. | primär |
| `BU_SCHLUESSEL_KURZ` | warnung | Der BU-Schlüssel hat weniger als 4 Ziffern. Der reguläre Ausdruck der Formatbeschreibung verlangt genau 4; ob DATEV kürzere Schlüssel gleich behandelt, ist ungeprüft. Der Server füllt nicht mit Nullen auf. Mit der Steuerberatung klären. | primär |
| `BELEGDATUM_FEHLT` | fehler | Das Belegdatum (Feld 10) ist leer. | primär |
| `BELEGDATUM_FORMAT` | fehler | Das Belegdatum ist kein gültiges Datum im Format TTMM (oder existiert im ermittelten Jahr nicht, z. B. 2902). | primär |
| `BELEGDATUM_AUSSERHALB_ZEITRAUM` | fehler | Das Belegdatum liegt außerhalb von Datum von/bis des Headers. | abgeleitet |
| `BELEGDATUM_AUSSERHALB_WJ` | fehler | Das Belegdatum liegt außerhalb des Wirtschaftsjahres ab WJ-Beginn und lässt sich als TTMM nicht eindeutig darstellen. | abgeleitet |
| `BELEGFELD1_ZU_LANG` | fehler | Belegfeld 1 ist länger als 36 Zeichen. | primär |
| `BELEGFELD1_ZEICHEN` | fehler | Belegfeld 1 enthält unerlaubte Zeichen. Erlaubt sind A-Z, a-z, 0-9, _ und $ & % * + - /; nicht erlaubt sind z. B. Leerzeichen, Umlaute, Punkt, Komma, Semikolon, Doppelpunkt. | primär |
| `BELEGFELD2_ZU_LANG` | fehler | Belegfeld 2 ist zu lang: beim Prüfen länger als 36 Zeichen, beim Schreiben länger als 12 Zeichen. | primär |
| `BELEGFELD2_UEBER_12` | warnung | Belegfeld 2 ist länger als 12 Zeichen. Die deutsche DATEV-Formatbeschreibung erlaubt 36, die englische 12; sicher ist höchstens 12. | primär |
| `BELEGFELD2_ZEICHEN` | fehler | Belegfeld 2 enthält unerlaubte Zeichen (wie Belegfeld 1). | primär |
| `BUCHUNGSTEXT_ZU_LANG` | fehler | Der Buchungstext (Feld 14) ist länger als 60 Zeichen. | primär |
| `KOST_FORMAT` | fehler | KOST1 oder KOST2 ist länger als 36 Zeichen oder enthält andere Zeichen als Buchstaben (auch Umlaute), Ziffern, _ und Leerzeichen. | primär |
| `FORMELZEICHEN_AM_ANFANG` | warnung | Ein Textfeld beginnt mit =, +, -, @, Tabulator oder Wagenrücklauf. Tabellenprogramme wie Excel werten so einen Wert beim Öffnen der CSV als Formel aus. DATEV wertet keine Formeln aus. | sekundär |
| `FORMELZEICHEN_BEIM_SCHREIBEN` | fehler | Beim Schreiben lehnt dieser Server Buchungstext, Belegfeld 1, Belegfeld 2, KOST1 und KOST2 ab, die mit = oder @ beginnen, damit Tabellenprogramme den Wert nicht als Formel ausführen. | sekundär |
| `WKZ_UNGUELTIG` | fehler | WKZ Umsatz (Feld 3) besteht nicht aus 3 Großbuchstaben. | primär |
| `FESTSCHREIBUNG_UNGUELTIG` | fehler | Festschreibung (Feld 114) ist nicht leer, 0 oder 1. | primär |
| `FESTSCHREIBUNG_LEER` | hinweis | Festschreibung (Feld 114) ist leer; laut DATEV bedeutet das 'nicht definiert; wird automatisch festgeschrieben'. | primär |
| `FESTSCHREIBUNG_WIDERSPRUCH` | warnung | Der Header sagt 'keine Festschreibung', aber mindestens eine Buchung hat Festschreibung 1. Laut DATEV wird dann der ganze Stapel festgeschrieben. | primär |
| `FESTSCHREIBUNG_EINZELN` | fehler | Beim Schreiben: Der Kopf sagt 'keine Festschreibung', aber mindestens eine Buchung verlangt Festschreibung. Laut DATEV würde dann der ganze Stapel nach dem Import festgeschrieben; der Server schreibt so eine Datei nicht. Setzen Sie die Festschreibung im Kopf oder lassen Sie sie bei der Buchung weg. | primär |
| `LEISTUNGSDATUM_OHNE_STEUERPERIODE` | warnung | Feld 115 (Leistungsdatum) ist gefüllt, Feld 116 (Datum Zuord. Steuerperiode) aber leer. Laut Formatbeschreibung gehören dann beide dazu; die DATEV-Musterdatei enthält trotzdem eine solche Zeile, daher nur Warnung. | primär |
| `TEXT_OHNE_ANFUEHRUNGSZEICHEN` | warnung | Ein Textfeld steht nicht in Anführungszeichen. DATEV verlangt Anführungszeichen für alle Textfelder. | primär |
| `ZAHL_IN_ANFUEHRUNGSZEICHEN` | hinweis | Ein Zahlenfeld steht in Anführungszeichen. | primär |
| `EINGABE_UNGUELTIG` | fehler | Ein Wert in der Eingabe (JSON, CSV oder Tool-Aufruf) lässt sich nicht lesen, z. B. ein Datum oder Betrag in unbekanntem Format. | abgeleitet |
| `ZEICHEN_NICHT_CP1252` | fehler | Ein Text enthält Zeichen, die es in Windows-1252 nicht gibt (z. B. Emoji). Die Datei wird in Windows-1252 geschrieben. | primär |

## Sicherheit

Kurzfassung, Details in [SECURITY.md](SECURITY.md):

- Kein Netzwerk: Der Server spricht nur stdio und öffnet keine Verbindungen. Der eigene Code importiert keine Netzwerkbibliotheken (Test `test_package_has_no_network_imports`); das MCP-SDK bringt HTTP-Komponenten mit, die dieser Server nicht startet. Er sendet nichts an DATEV.
- Arbeitsordner: Lesen und Schreiben nur direkt in `EXTF_ORDNER`, nie überschreiben, keine Pfade, keine symbolischen oder harten Links, Lesegrenze 50 MB.
- Tabellenprogramme: Werte, die mit `=`, `+`, `-`, `@`, Tabulator oder Wagenrücklauf beginnen, meldet der Server als Warnung `FORMELZEICHEN_AM_ANFANG`; beim Schreiben lehnt er `=` und `@` am Anfang von Buchungstext, Belegfeldern und Kostenstellen ab. Öffnen Sie EXTF-Dateien trotzdem nicht per Doppelklick in Excel (siehe [SECURITY.md](SECURITY.md)).
- Prompt Injection: Buchungstexte aus gelesenen Dateien sind Daten. Ein Text wie "Ignoriere alle Anweisungen" kann den Server zu nichts bringen, weil er keine Befehle ausführt und nur neue Dateien im Arbeitsordner anlegen kann. Ihr KI-Client kann sich davon aber beeinflussen lassen; prüfen Sie Tool-Aufrufe, bevor Sie sie freigeben.
- Datenschutz: Was Sie dem KI-Assistenten geben und was die Tools zurückliefern (Buchungen, Beträge, Namen in Buchungstexten), geht an den Anbieter des Sprachmodells, das Ihr Client nutzt. Der Server selbst speichert nichts außerhalb des Arbeitsordners.

## Tests

Der erste Befehl gilt aus der Wurzel des Klons, der zweite wechselt in den Paketordner:

```bash
python3 -m venv /tmp/extf-test && /tmp/extf-test/bin/pip install "./server/extf-buchungsstapel[test]"
cd server/extf-buchungsstapel && /tmp/extf-test/bin/python -m pytest -q
```

Zum Server gehören über 280 automatische Tests: Einheitstests für jeden Prüfcode, Roundtrip-Tests (schreiben, lesen, vergleichen), byte-genaue Tests (Windows-1252 für ä ö ü ß €, CR/LF, verdoppelte Anführungszeichen), Golden-Files in `tests/fixtures`, Sicherheitstests (Pfade, symbolische und harte Links, FIFO, Gerätenamen, Überschreiben, Formelzeichen) und ein End-to-End-Test, der den Server über stdio startet und mit dem offiziellen MCP-Client alle vier Tools aufruft. Tests zeigen nur das geprüfte Verhalten; sie ersetzen weder das Prüfprogramm von DATEV noch eine steuerliche Prüfung.

Zwei optionale Abgleiche laufen nur, wenn Sie die Referenzen selbst bereitstellen:

- `EXTF_MUSTERDATEI=/pfad/EXTF_Buchungsstapel.csv`: Musterdatei aus den DATEV-Musterdaten (Developer Portal, DATEV-Format, Musterdaten). Sie wird aus urheberrechtlichen Gründen nicht mitgeliefert.
- `EXTF_TS_PROJEKT=/pfad/zum/node-projekt`: Ordner, in dem `npm install @seamless-engineering/datev-extf` ausgeführt wurde (unabhängige Implementierung, MIT). Die Golden-Files müssen dort ohne Fehler durchlaufen, die Spaltenliste muss gleich sein.

## Haftung und Lizenz

MIT, siehe [LICENSE](LICENSE).

- **Haftung.** Die Software und die Texte werden unentgeltlich und ohne Zusicherung bestimmter Eigenschaften bereitgestellt. Soweit gesetzlich zulässig, ist die Haftung ausgeschlossen. Unberührt bleibt die Haftung für Vorsatz und grobe Fahrlässigkeit, für Schäden aus der Verletzung des Lebens, des Körpers oder der Gesundheit, für arglistig verschwiegene Mängel und nach dem Produkthaftungsgesetz. Prüfen Sie jede erzeugte Datei, bevor Sie sie weitergeben oder importieren.

> **Hinweis:** Technische Informationen nach Stand 20.10.2026, ohne Gewähr für Vollständigkeit und Richtigkeit. Keine Rechts- oder Steuerberatung; die Autoren sind keine Rechtsanwälte, Steuerberater oder Datenschutzbeauftragten. Produktnamen sind Marken ihrer Inhaber; es besteht keine Verbindung zu den genannten Herstellern.

> Die Autoren erbringen keine Hilfeleistung in Steuersachen im Sinne des Steuerberatungsgesetzes. Ob und wie Buchungen steuerlich richtig sind, klären Sie mit Ihrer Steuerberatung. DATEV ist eine Marke der DATEV eG; dieses Projekt ist kein Produkt der DATEV eG und nicht von ihr geprüft oder freigegeben.
