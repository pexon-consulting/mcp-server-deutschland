# MCP-Server in Claude, Cursor, VS Code und Codex einrichten

Diese Anleitung zeigt, wie Sie einen MCP-Server in Claude Desktop, Claude Code, Cursor, VS Code und Codex eintragen: welche Datei, welcher Pfad, welches Format. Als Beispiele dienen der Feiertage-Server aus diesem Repository und der Server `extf-buchungsstapel-mcp`.

Stand: 19.10.2026

## Inhaltsverzeichnis

- [Überblick: eine Idee, fünf Dateiformate](#überblick-eine-idee-fünf-dateiformate)
- [Die beiden Beispielserver](#die-beiden-beispielserver)
- [Claude Desktop](#claude-desktop)
- [Claude Code](#claude-code)
- [Cursor](#cursor)
- [VS Code](#vs-code)
- [Codex](#codex)
- [Lokal (stdio) oder entfernt (Remote mit OAuth)](#lokal-stdio-oder-entfernt-remote-mit-oauth)
- [Zugangsdaten und Umgebungsvariablen](#zugangsdaten-und-umgebungsvariablen)
- [Projekt- oder Benutzerebene](#projekt--oder-benutzerebene)
- [Freigaben für Tool-Aufrufe](#freigaben-für-tool-aufrufe)
- [Fehlersuche](#fehlersuche)
- [Was getestet wurde](#was-getestet-wurde)
- [Häufige Fragen](#häufige-fragen)
- [Weiterlesen](#weiterlesen)

## Überblick: eine Idee, fünf Dateiformate

Alle fünf Clients brauchen dieselben Angaben: einen Namen für den Server, den Startbefehl mit Argumenten und gegebenenfalls Umgebungsvariablen. Bei entfernten Servern kommen URL und Anmeldung hinzu. Unterschiedlich sind Dateiname, Ablageort und der Schlüssel auf oberster Ebene.

| Client | Datei | Schlüssel | Ebenen |
| --- | --- | --- | --- |
| Claude Desktop | `claude_desktop_config.json` | `mcpServers` | nur Benutzer |
| Claude Code | `.mcp.json` und `~/.claude.json` | `mcpServers` | lokal, Projekt, Benutzer |
| Cursor | `.cursor/mcp.json` und `~/.cursor/mcp.json` | `mcpServers` | Projekt, global |
| VS Code | `.vscode/mcp.json` und Benutzerprofil `mcp.json` | `servers` | Arbeitsbereich, Benutzer |
| Codex | `.codex/config.toml` und `~/.codex/config.toml` | `[mcp_servers.<name>]` | Projekt, Benutzer |

Die Angaben stammen aus der Dokumentation der Hersteller, jeweils abgerufen am 19.10.2026. Die Quellen stehen in den einzelnen Abschnitten. Clients ändern sich schnell; gleichen Sie Pfade bei Abweichungen mit der verlinkten Seite ab.

## Die beiden Beispielserver

**Feiertage-Server.** Er berechnet gesetzliche Feiertage und Arbeitstage je Bundesland und braucht keine Zugangsdaten. Wie er entsteht, beschreibt [MCP-Server erstellen](mcp-server-erstellen.md). Start direkt aus dem Git-Repository:

```bash
uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=beispiele/feiertage-python" feiertage-mcp
```

Aus einem lokalen Klon geht es auch, das ist die getestete Variante:

```bash
uvx --from /Users/muster/mcp-server-deutschland/beispiele/feiertage-python feiertage-mcp
```

**`extf-buchungsstapel-mcp`.** Dieser Server erzeugt, liest und erklärt Buchungsstapel im DATEV-Format EXTF. Er arbeitet ohne Netzwerkzugriff und liest und schreibt nur in dem Ordner, den die Umgebungsvariable `EXTF_ORDNER` angibt. Start aus dem Repository:

```bash
uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel" extf-buchungsstapel-mcp
```

Legen Sie für `EXTF_ORDNER` einen eigenen, leeren Ordner an, in den Beispielen `~/extf-export` (ausgeschrieben `/Users/muster/extf-export`). Der Server legt ihn nicht selbst an; fehlt er, schlagen alle Tools fehl:

```bash
mkdir -p ~/extf-export
```

Geben Sie dem Server nicht Ihr ganzes Dokumentenverzeichnis. Was der Server mit Mandant und Beraternummer macht, beschreibt die [Anleitung zum DATEV-Format (EXTF)](datev-mcp-server.md).

Beide Server laufen über stdio: Der Client startet sie als Unterprozess. Voraussetzung ist [uv](https://docs.astral.sh/uv/) auf dem Rechner, denn `uvx` kommt mit uv.

## Claude Desktop

**Datei und Pfad.** Claude Desktop öffnet die Datei über Einstellungen > Entwickler > Konfiguration bearbeiten (englisch: Settings > Developer > Edit Config). Ablageorte:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `$XDG_CONFIG_HOME/Claude/claude_desktop_config.json`, ohne gesetztes `XDG_CONFIG_HOME` unter `~/.config/Claude/claude_desktop_config.json`

Quellen: [Connect to local MCP servers](https://modelcontextprotocol.io/docs/develop/connect-local-servers) für macOS und Windows, für Linux die [VS-Code-Referenz zur Erkennung von Claude-Desktop-Konfigurationen](https://code.visualstudio.com/docs/copilot/reference/mcp-configuration), beide abgerufen am 19.10.2026. Die MCP-Dokumentation selbst nennt nur macOS und Windows.

**Beispiel mit beiden Servern:**

```json
{
  "mcpServers": {
    "feiertage": {
      "command": "/Users/muster/.local/bin/uvx",
      "args": [
        "--from",
        "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=beispiele/feiertage-python",
        "feiertage-mcp"
      ]
    },
    "extf-buchungsstapel": {
      "command": "/Users/muster/.local/bin/uvx",
      "args": [
        "--from",
        "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel",
        "extf-buchungsstapel-mcp"
      ],
      "env": {
        "EXTF_ORDNER": "/Users/muster/extf-export"
      }
    }
  }
}
```

Die MCP-Dokumentation verlangt absolute Pfade in der Konfiguration. Wir tragen auch den Befehl absolut ein, weil Desktop-Programme nicht unbedingt denselben Suchpfad wie Ihr Terminal sehen. Den Pfad zu `uvx` liefert `which uvx` (macOS, Linux) oder `where uvx` (Windows). Unter Windows schreiben Sie Pfade mit doppelten Backslashes, etwa `"C:\\Users\\muster\\extf-export"`.

Nach dem Speichern starten Sie Claude Desktop vollständig neu. Die Tools erscheinen dann im Eingabefeld unter dem Werkzeug-Symbol.

**Entfernte Server.** Remote-Server tragen Sie nicht in diese Datei ein, sondern als „Custom Connector“ unter Einstellungen > Connectors bzw. Customize > Connectors. Laut Anthropic-Hilfe ist das in den Tarifen Free, Pro, Max, Team und Enterprise möglich; Free ist auf einen eigenen Connector begrenzt. In Team und Enterprise fügen nur Owner Connectors hinzu. Quelle: [support.claude.com](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp), abgerufen am 19.10.2026.

## Claude Code

Claude Code kennt drei Ebenen, im Englischen „scopes“ (Quelle: [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp), abgerufen am 19.10.2026):

- **local** (Standard): nur für Sie, nur in diesem Projekt. Gespeichert in `~/.claude.json` unter dem Projektpfad.
- **project**: für alle im Team, in `.mcp.json` im Projektordner. Diese Datei gehört ins Repository.
- **user**: für Sie in allen Projekten, ebenfalls in `~/.claude.json`.

Unter Windows liegt `~/.claude.json` im Benutzerprofil. Gibt es denselben Namen mehrfach, gewinnt local vor project vor user.

**Per Befehl eintragen.** Am einfachsten fügen Sie Server mit `claude mcp add` hinzu. Alles nach `--` ist der Startbefehl:

```bash
claude mcp add --scope project --transport stdio feiertage -- \
  uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=beispiele/feiertage-python" feiertage-mcp

claude mcp add --scope project --env 'EXTF_ORDNER=${EXTF_ORDNER}' --transport stdio extf-buchungsstapel -- \
  uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel" extf-buchungsstapel-mcp
```

Beide Befehle schreiben wegen `--scope project` in die Datei `.mcp.json` im Projektordner. Ohne `--scope` (kurz `-s`) gilt der Scope `local`: Der Eintrag steht dann in `~/.claude.json` und gilt nur für Sie in diesem Projekt. Für den persönlichen Gebrauch genügt das, und der Pfad darf direkt im Befehl stehen:

```bash
mkdir -p ~/extf-export
claude mcp add --env EXTF_ORDNER="$HOME/extf-export" --transport stdio extf-buchungsstapel -- \
  uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel" extf-buchungsstapel-mcp
```

Bei der Variante mit `.mcp.json` setzen Sie die Variable `EXTF_ORDNER` in Ihrer Shell, bevor Sie `claude` starten, zum Beispiel mit `export EXTF_ORDNER="$HOME/extf-export"`.

Ein Stolperstein, den die Doku erwähnt und den wir nachgestellt haben: Steht der Servername direkt hinter `--env`, hält Claude Code ihn für eine weitere Variable und bricht mit „Invalid environment variable format“ ab. Setzen Sie eine andere Option wie `--transport` dazwischen.

**Ergebnis in `.mcp.json`** (gekürzt auf den EXTF-Eintrag):

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
        "EXTF_ORDNER": "${EXTF_ORDNER}"
      }
    }
  }
}
```

`${VAR}` und `${VAR:-standardwert}` werden in `command`, `args`, `env`, `url` und `headers` aufgelöst. So steht der persönliche Ordnerpfad nicht im Repository. Fehlt die Variable, warnt `claude mcp list` mit „Missing environment variables: EXTF_ORDNER“.

**Entfernte Server** fügen Sie mit `claude mcp add --transport http <name> <url>` hinzu. Die Anmeldung per OAuth starten Sie in einer Sitzung mit `/mcp`.

**Weitere Befehle:** `claude mcp list`, `claude mcp get <name>`, `claude mcp remove <name> -s <scope>` und `claude mcp add-from-claude-desktop` (übernimmt Einträge aus Claude Desktop, laut Doku unter macOS und WSL). Startet ein Server langsam, verlängern Sie die Wartezeit mit der Umgebungsvariable `MCP_TIMEOUT` in Millisekunden.

## Cursor

**Datei und Pfad** (Quelle: [cursor.com/docs/mcp](https://cursor.com/docs/mcp), abgerufen am 19.10.2026):

- Projekt: `.cursor/mcp.json` im Projektordner
- Global: `~/.cursor/mcp.json` im Home-Verzeichnis, unter Windows also im Benutzerprofil

Der Schlüssel heißt wie bei Claude `mcpServers`. Cursor unterstützt bei stdio-Servern zusätzlich `envFile`, also eine Datei mit Umgebungsvariablen:

```json
{
  "mcpServers": {
    "feiertage": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=beispiele/feiertage-python",
        "feiertage-mcp"
      ]
    },
    "extf-buchungsstapel": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel",
        "extf-buchungsstapel-mcp"
      ],
      "env": {
        "EXTF_ORDNER": "${env:EXTF_ORDNER}"
      }
    }
  }
}
```

In Werten löst Cursor `${env:NAME}`, `${userHome}`, `${workspaceFolder}` und `${workspaceFolderBasename}` auf. Statt einer Umgebungsvariable ginge also auch `"${workspaceFolder}/extf-export"`, dann liegt der Arbeitsordner im Projekt. Nehmen Sie ihn in diesem Fall in die `.gitignore` auf.

**Entfernte Server** bekommen `url` und optional `headers`. Für Server ohne dynamische Client-Registrierung gibt es ein `auth`-Objekt mit `CLIENT_ID`, `CLIENT_SECRET` und `scopes`; Werte dort ebenfalls per `${env:...}` setzen. `envFile` gilt laut Doku nur für stdio-Server.

## VS Code

**Datei und Pfad** (Quelle: [code.visualstudio.com/docs/copilot/reference/mcp-configuration](https://code.visualstudio.com/docs/copilot/reference/mcp-configuration), Stand der Seite 16.10.2026, abgerufen am 19.10.2026):

- Arbeitsbereich: `.vscode/mcp.json`
- Benutzer: `mcp.json` im Benutzerprofil. Öffnen Sie die Datei über die Befehlspalette mit „MCP: Open User Configuration“, dann müssen Sie den Pfad nicht kennen.

Achtung, VS Code nutzt als Schlüssel `servers`, nicht `mcpServers`. Dafür gibt es `inputs`: VS Code fragt den Wert beim ersten Start ab und speichert ihn geschützt.

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "extf-ordner",
      "description": "Arbeitsordner für EXTF-Dateien"
    }
  ],
  "servers": {
    "feiertage": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=beispiele/feiertage-python",
        "feiertage-mcp"
      ]
    },
    "extfBuchungsstapel": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel",
        "extf-buchungsstapel-mcp"
      ],
      "env": {
        "EXTF_ORDNER": "${input:extf-ordner}"
      }
    }
  }
}
```

Für Passwörter und Schlüssel setzen Sie bei `promptString` zusätzlich `"password": true`. VS Code empfiehlt Servernamen in camelCase, daher `extfBuchungsstapel`.

**Sandbox.** Unter macOS und Linux kann VS Code stdio-Server mit `"sandboxEnabled": true` einschränken und im Objekt `sandbox` erlaubte Schreibpfade und Domains festlegen. Für `extf-buchungsstapel-mcp` bietet sich an, Schreibzugriff nur auf den Arbeitsordner zu erlauben.

**Entfernte Server** bekommen `"type": "http"`, `url`, optional `headers` und für OAuth `"oauth": {"clientId": "..."}`. Beim ersten Verbinden öffnet VS Code ein Browserfenster.

**Copilot-Format.** Daneben gibt es das portable Format von GitHub Copilot: `.mcp.json` im Arbeitsbereich oder `~/.copilot/mcp-config.json`, mit `mcpServers`. Es kennt weder `inputs` noch `envFile`. Kopieren Sie Einträge nicht ungeprüft zwischen den Formaten.

## Codex

**Datei und Pfad** (Quelle: [developers.openai.com/codex/mcp](https://developers.openai.com/codex/mcp), abgerufen am 19.10.2026):

- Benutzer: `~/.codex/config.toml`. Ist `CODEX_HOME` gesetzt, liegt die Datei dort.
- Projekt: `.codex/config.toml` im Projektordner, wird nur in vertrauenswürdigen Projekten gelesen.

Codex nutzt TOML statt JSON. Jeder Server ist eine eigene Tabelle:

```toml
[mcp_servers.feiertage]
command = "uvx"
args = ["--from", "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=beispiele/feiertage-python", "feiertage-mcp"]

[mcp_servers.extf-buchungsstapel]
command = "uvx"
args = ["--from", "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel", "extf-buchungsstapel-mcp"]
default_tools_approval_mode = "prompt"

[mcp_servers.extf-buchungsstapel.env]
EXTF_ORDNER = "/Users/muster/extf-export"
```

Per Befehl geht es ebenso, `--env` lässt sich hier direkt vor den Namen setzen:

```bash
mkdir -p ~/extf-export
codex mcp add extf-buchungsstapel --env EXTF_ORDNER="$HOME/extf-export" -- \
  uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel" extf-buchungsstapel-mcp
codex mcp list
```

`codex mcp list` zeigt Werte von Umgebungsvariablen maskiert an. Statt den Wert fest einzutragen, können Sie mit `env_vars = ["EXTF_ORDNER"]` eine vorhandene Variable an den Server durchreichen.

**Nützliche Schlüssel:** `startup_timeout_sec` (Standard 10), `tool_timeout_sec` (Standard 60), `enabled_tools` und `disabled_tools` für Erlaubnis- und Sperrlisten sowie `default_tools_approval_mode` mit `auto`, `prompt`, `writes` oder `approve`.

**Entfernte Server** bekommen `url`, Token per `bearer_token_env_var` oder Kopfzeilen per `http_headers` bzw. `env_http_headers`. Für OAuth melden Sie sich mit `codex mcp login <name>` an.

## Lokal (stdio) oder entfernt (Remote mit OAuth)

Ein **stdio-Server** läuft auf Ihrem Rechner, mit Ihren Rechten. Er sieht Ihre Dateien und Ihr Netzwerk, soweit Betriebssystem oder Sandbox das nicht verhindern. Dafür bleiben die Daten lokal, solange der Server sie nicht selbst versendet. Beide Beispielserver gehören in diese Gruppe.

Ein **Remote-Server** läuft bei einem Anbieter und wird per Streamable HTTP angesprochen. Die Anmeldung läuft in der Regel über OAuth: Der Client öffnet ein Browserfenster, Sie melden sich beim Anbieter an und erteilen Rechte. Prüfen Sie dabei die angeforderten Berechtigungen. Danach verwaltet der Client das Token.

Was davon datenschutzrechtlich zu beachten ist, etwa ein Auftragsverarbeitungsvertrag mit dem Betreiber, behandelt [MCP und DSGVO](mcp-dsgvo.md).

## Zugangsdaten und Umgebungsvariablen

Die Grundregel: Zugangsdaten stehen nie in einer Datei, die ins Repository kommt. Das betrifft `.mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json` und `.codex/config.toml`. Die Clients bieten dafür unterschiedliche Wege:

| Client | Weg für Geheimnisse |
| --- | --- |
| Claude Code | `${VAR}` in `.mcp.json`, Wert in Ihrer Shell |
| Cursor | `${env:NAME}` oder `envFile` (nur stdio) |
| VS Code | `inputs` mit `password: true` oder `envFile` |
| Codex | `env_vars`, `bearer_token_env_var`, `env_http_headers` |
| Claude Desktop | Wert in `env` der Benutzerdatei, die nicht im Repository liegt |

Dateien wie `.env` gehören in die `.gitignore`. Auch persönliche Pfade wie der EXTF-Arbeitsordner sind besser als Variable aufgehoben: Sie verraten Benutzernamen und Ordnerstruktur.

Ein Detail für eigene Tests: Der stdio-Client des TypeScript-SDK gibt einem Server standardmäßig nur einige unkritische Variablen wie `PATH` und `HOME` mit, nicht Ihre ganze Umgebung. Was der Server braucht, muss in `env` stehen.

## Projekt- oder Benutzerebene

**Projektebene** passt, wenn alle im Team denselben Server brauchen, etwa einen Datenbank-Server für die Entwicklungsdatenbank. Die Datei wird mit eingecheckt, Geheimnisse kommen per Variable.

**Benutzerebene** passt für persönliche Werkzeuge und alles mit eigenen Zugangsdaten. Der EXTF-Server gehört eher hierher: Er arbeitet mit Mandantendaten auf Ihrem Rechner.

Aus Sicherheitsgründen starten Projekt-Server nicht ungefragt:

- Claude Code fragt beim ersten Start in einem Projekt nach. Bis dahin zeigt `claude mcp list` den Status „Pending approval“. Zurücksetzen mit `claude mcp reset-project-choices`.
- VS Code koppelt Server aus `.vscode/mcp.json` an das Vertrauen in den Arbeitsbereich (Workspace Trust).
- Codex liest `.codex/config.toml` nur in vertrauenswürdigen Projekten.

Prüfen Sie eine fremde Projektkonfiguration, bevor Sie zustimmen. Ein Eintrag in `.mcp.json` kann jeden beliebigen Befehl starten.

## Freigaben für Tool-Aufrufe

Starten heißt noch nicht ausführen. Alle hier beschriebenen Clients fragen in der Grundeinstellung vor Tool-Aufrufen nach. Die Feinheiten unterscheiden sich:

- **Cursor** fragt laut Doku standardmäßig vor jedem Tool-Aufruf und bietet zusätzlich automatische Ausführungsmodi.
- **VS Code** trennt drei Dinge: den Server starten (Vertrauen), sich anmelden (Authentifizierung) und einzelne Tools ausführen (Freigabe).
- **Codex** steuert das je Server mit `default_tools_approval_mode`. Bei `writes` fragt Codex nur bei Tools nach, die nicht als rein lesend markiert sind.
- **Claude Code und Claude Desktop** fragen vor Tool-Aufrufen; erteilte Freigaben lassen sich in den Einstellungen bzw. Berechtigungen verwalten.

Die Markierung „rein lesend“ setzt der Server selbst über Annotations wie `readOnlyHint`. Das ist ein Hinweis, keine Garantie. Mehr dazu in [MCP-Sicherheit](mcp-sicherheit.md).

## Fehlersuche

**Wo stehen die Logs?**

| Client | Logs |
| --- | --- |
| Claude Desktop | macOS `~/Library/Logs/Claude`, Windows `%APPDATA%\Claude\logs`; `mcp.log` und `mcp-server-NAME.log` |
| Claude Code | `claude --debug-file /tmp/claude-debug.log`, Status mit `/mcp` |
| Cursor | Ausgabe-Panel (Cmd+Shift+U bzw. Strg+Shift+U), Eintrag „MCP Logs“ |
| VS Code | „MCP: List Servers“, Server wählen, „Show Output“ |
| Codex | Logs unter `$CODEX_HOME/log`, Konfiguration mit `codex mcp list` |

Unter macOS verfolgen Sie Claude-Desktop-Logs live mit:

```bash
tail -n 20 -F ~/Library/Logs/Claude/mcp*.log
```

Die Datei `mcp-server-NAME.log` enthält alles, was der Server auf stderr schreibt. Ein gut gebauter stdio-Server protokolliert genau dorthin.

**Typische Fehler:**

- **Befehl nicht gefunden.** `uvx` oder `npx` liegt nicht im Suchpfad des Programms. Lösung: absoluter Pfad als `command`.
- **Server startet, Tools fehlen.** Oft schreibt der Server Text auf stdout, das bricht das Protokoll. Starten Sie den Befehl im Terminal: Erscheint vor jeder Eingabe schon Text, liegt hier der Fehler.
- **Erster Start dauert lange.** `uvx` aus einem Git-Repository lädt und baut beim ersten Mal. Erhöhen Sie das Startzeitlimit (`MCP_TIMEOUT`, `startup_timeout_sec`) oder starten Sie den Befehl einmal vorab im Terminal.
- **Variable fehlt.** `extf-buchungsstapel-mcp` braucht `EXTF_ORDNER`, und der Ordner muss existieren. Desktop-Programme kennen Variablen aus `.zshrc` oder `.bashrc` meist nicht.
- **Windows-Pfade.** Laut MCP-Doku kann ein nicht aufgelöstes `${APPDATA}` zu `ENOENT`-Fehlern führen. Tragen Sie den Pfad dann ausgeschrieben in `env` ein.
- **Falscher Schlüssel.** `servers` in Cursor oder `mcpServers` in `.vscode/mcp.json` wird schlicht ignoriert.

Den Server ohne Client prüfen Sie mit dem MCP Inspector, siehe [MCP-Server erstellen](mcp-server-erstellen.md#testen-client-inspector-und-pytest).

## Was getestet wurde

Am 19.10.2026 auf einem Mac mit Claude Code 2.1.303 und codex-cli 0.147.0, jeweils in einem Wegwerf-Ordner bzw. mit eigenem `CODEX_HOME`:

- `claude mcp add` im Scope project erzeugte die gezeigte `.mcp.json`. Der beschriebene `--env`-Fehler trat wie erwartet auf. `claude mcp list` zeigte „Pending approval“ und die Warnung zur fehlenden Variable.
- Im Scope local meldete `claude mcp get` für beide Server „Connected“, gestartet per `uvx --from <lokaler Pfad>`.
- Am 20.10.2026 schrieb `claude mcp add` ohne `--scope` den Eintrag in `~/.claude.json` (Scope local) und legte keine `.mcp.json` an.
- `codex mcp add` erzeugte die gezeigte `config.toml`, `codex mcp list` zeigte beide Server.
- `extf-buchungsstapel-mcp` startete per `uvx` aus dem lokalen Ordner und meldete vier Tools.

Nicht getestet: der Start direkt aus dem Git-Repository (`uvx --from git+...`), Claude Desktop, Cursor, VS Code, Tool-Aufrufe in Codex sowie alle Remote- und OAuth-Wege. Die JSON- und TOML-Beispiele wurden auf gültige Syntax geprüft.

## Häufige Fragen

**Kann ich eine Konfiguration für alle Clients verwenden?**
Teilweise. Claude Desktop, Claude Code und Cursor teilen den Schlüssel `mcpServers`, unterscheiden sich aber bei Variablen. VS Code nutzt `servers`, Codex TOML. VS Code kann über `chat.mcp.discovery.enabled` Einträge aus Claude Desktop und Cursor mitlesen.

**Warum zeigt Claude Code meinen Server als „Pending approval“?**
Server aus `.mcp.json` brauchen Ihre Zustimmung. Starten Sie `claude` im Projektordner und bestätigen Sie die Abfrage.

**Muss ich nach einer Änderung neu starten?**
Bei Claude Desktop ja, vollständig. Andere Clients laden Konfigurationen teils automatisch nach; im Zweifel den Server in der MCP-Übersicht neu starten.

**Darf `.mcp.json` ins Repository?**
Ja, dafür ist sie gedacht, aber ohne Zugangsdaten und persönliche Pfade. Verwenden Sie Variablen.

**Brauche ich für den EXTF-Server ein DATEV-Konto?**
Nein. Der Server erzeugt und liest EXTF-Dateien lokal. Den Import in DATEV übernimmt, wer dort Zugang hat, meist Ihre Steuerberatung.

## Weiterlesen

- [Übersicht: MCP-Server für deutsche Geschäftssysteme](../../README.md)
- [MCP-Server-Liste](../liste.md)
- [Was ist ein MCP-Server?](was-ist-ein-mcp-server.md)
- [MCP oder API?](mcp-vs-api.md)
- [MCP-Server erstellen](mcp-server-erstellen.md)
- [MCP-Sicherheit](mcp-sicherheit.md)
- [MCP und DSGVO](mcp-dsgvo.md)
- [Anleitung zum DATEV-Format (EXTF)](datev-mcp-server.md)
- [SAP-MCP-Server](sap-mcp-server.md)
- [Power-BI-MCP](power-bi-mcp.md)
- [HubSpot-MCP](hubspot-mcp.md)
- [Postgres-MCP](postgres-mcp.md)
- [Buchhaltung mit MCP](buchhaltung-mcp.md)
- [Business-Central-MCP](business-central-mcp.md)

> **Hinweis:** Technische Informationen nach Stand 19.10.2026, ohne Gewähr für Vollständigkeit
> und Richtigkeit. Keine Rechts- oder Steuerberatung; die Autoren sind keine Rechtsanwälte,
> Steuerberater oder Datenschutzbeauftragten. Produktnamen sind Marken ihrer Inhaber; es besteht
> keine Verbindung zu den genannten Herstellern.
>
> Die Autoren erbringen keine Hilfeleistung in Steuersachen im Sinne des Steuerberatungsgesetzes.
> Ob und wie Buchungen steuerlich richtig sind, klären Sie mit Ihrer Steuerberatung. DATEV ist
> eine Marke der DATEV eG; dieses Projekt ist kein Produkt der DATEV eG und nicht von ihr geprüft
> oder freigegeben.
