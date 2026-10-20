# MCP-Server erstellen: Tutorial mit Python und TypeScript

In diesem Tutorial erstellen Sie einen eigenen MCP-Server "Feiertage und Arbeitstage in Deutschland", einmal in Python mit dem offiziellen SDK `mcp` 2.3 und einmal in TypeScript mit `@modelcontextprotocol/server` 2.3. Der Server berechnet Feiertage je Bundesland selbst, braucht also weder Netz noch API-Schlüssel, und ist damit ein gutes Übungsobjekt.

Stand: 19.10.2026. Spezifikation: MCP 2026-07-28. Getestet mit Python 3.13.1, `mcp` 2.3.0, Node.js 22.23.1, `@modelcontextprotocol/server` 2.3.1 und MCP Inspector 2.11.0. Teil der Sammlung [MCP-Server für Geschäftssysteme in Deutschland](../liste.md).

Für: Entwickler mit Grundkenntnissen in Python oder TypeScript. Der vollständige Code liegt lauffähig unter [`beispiele/feiertage-python`](../../beispiele/feiertage-python/) und [`beispiele/feiertage-typescript`](../../beispiele/feiertage-typescript/).

## Inhaltsverzeichnis

- [Das Wichtigste in Kürze](#das-wichtigste-in-kürze)
- [Was der Server können soll](#was-der-server-können-soll)
- [Achtung: FastMCP heißt jetzt MCPServer](#achtung-fastmcp-heißt-jetzt-mcpserver)
- [Die Fachlogik: Feiertage selbst berechnen](#die-fachlogik-feiertage-selbst-berechnen)
- [MCP-Server in Python](#mcp-server-in-python)
- [MCP-Server in TypeScript](#mcp-server-in-typescript)
- [Eingabeschema, structuredContent und Annotations](#eingabeschema-structuredcontent-und-annotations)
- [Fehlerbehandlung](#fehlerbehandlung)
- [Logging nach stderr, nie nach stdout](#logging-nach-stderr-nie-nach-stdout)
- [Testen: Client, Inspector und pytest](#testen-client-inspector-und-pytest)
- [Paketieren und starten mit uvx und npx](#paketieren-und-starten-mit-uvx-und-npx)
- [Veröffentlichen in der MCP Registry](#veröffentlichen-in-der-mcp-registry)
- [Häufige Fragen](#häufige-fragen)
- [Weiterlesen](#weiterlesen)

## Das Wichtigste in Kürze

- Ein MCP-Server besteht aus Fachlogik plus einer dünnen Schicht, die Funktionen als **Tools** anmeldet. Das SDK erzeugt daraus Eingabeschema, Ausgabeschema und die JSON-RPC-Kommunikation.
- In Python heißt die bequeme Server-Klasse seit `mcp` 2.0 **`MCPServer`**. Der alte Import `from mcp.server.fastmcp import FastMCP` funktioniert nur mit `mcp<2`.
- In TypeScript nutzen Sie `McpServer` aus `@modelcontextprotocol/server`, Schemas mit zod und `serveStdio` für den Start.
- Bei stdio gehört **stdout dem Protokoll**. Logs gehen nach stderr.
- Getestet wird mit dem offiziellen Client des SDK oder dem MCP Inspector im CLI-Modus, ohne globale Installation.
- Verteilt wird über PyPI und `uvx` oder npm und `npx`. In der MCP Registry veröffentlichen Sie nur Metadaten (`server.json`).

## Was der Server können soll

Der Server bietet zwei Tools an:

| Tool | Eingabe | Ergebnis |
| --- | --- | --- |
| `list_holidays` | `year` (1995-2100), `state` (z. B. `BY`) | Liste der gesetzlichen Feiertage mit Datum, Name, Wochentag, bundesweit ja/nein |
| `count_working_days` | `start`, `end` (JJJJ-MM-TT), `state`, optional `saturday_is_workday` | Anzahl Arbeitstage und Feiertage, die auf Werktage fielen |

Die Tool-Namen und Feldnamen sind englisch, Beschreibungen und Fehlermeldungen deutsch. So bleiben Bezeichner für jedes Modell gut lesbar, und Nutzer bekommen verständliche Meldungen.

Eine fachliche Grenze vorab: Der Server kennt landesweit geltende Feiertage. Feiertage, die nur in einzelnen Gemeinden gelten (Fronleichnam in Teilen von Sachsen und Thüringen, Mariä Himmelfahrt in Teilen Bayerns, das Augsburger Friedensfest), sind nicht enthalten. Für 2025 bis 2027 haben wir die Ergebnisse aller 16 Länder gegen die öffentliche API Nager.Date abgeglichen; sie stimmten vollständig überein.

## Achtung: FastMCP heißt jetzt MCPServer

Viele Tutorials im Netz beginnen mit `from mcp.server.fastmcp import FastMCP`. Mit der aktuellen Version 2.3.0 des Python-SDK schlägt das fehl. Getestet am 19.10.2026:

```bash
uv venv -p 3.13 .venv
uv pip install -p .venv "mcp>=2.3,<2.4"
.venv/bin/python -c "import mcp.server.fastmcp"
```

```text
ModuleNotFoundError: No module named 'mcp.server.fastmcp'. This is mcp 2.x, where FastMCP was renamed to MCPServer (from mcp.server.mcpserver import MCPServer) and other APIs changed; see the migration guide at https://py.sdk.modelcontextprotocol.io/v2/migration/#fastmcp-renamed-to-mcpserver or pin 'mcp<2' to keep running v1 code.
```

Hintergrund: Mit Version 2 hat das offizielle SDK die High-Level-Klasse umbenannt und weitere APIs geändert. Sie haben zwei Möglichkeiten:

- **Neuer Code:** `from mcp.server import MCPServer` verwenden, wie in diesem Tutorial.
- **Alter Code:** `mcp<2` festschreiben. Die 1.x-Linie wird laut Release-Seite weiter gepflegt (v1.30.0 vom 07.09.2026).

Nicht verwechseln: Das eigenständige Paket `fastmcp` (Version 4.1.0 am 16.10.2026) ist ein separates Projekt und nicht das offizielle SDK.

## Die Fachlogik: Feiertage selbst berechnen

Fast alle beweglichen Feiertage hängen am Ostersonntag. Die Berechnung nach der Gaußschen Osterformel (anonymer gregorianischer Algorithmus) passt in wenige Zeilen:

```python
from datetime import date

def easter_sunday(year: int) -> date:
    """Ostersonntag im gregorianischen Kalender."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)
```

Daraus folgen Karfreitag (Ostern minus 2 Tage), Ostermontag (plus 1), Christi Himmelfahrt (plus 39), Pfingstmontag (plus 50) und Fronleichnam (plus 60). Der Buß- und Bettag in Sachsen ist der Mittwoch vor dem 23. November. Dazu kommen landesspezifische Regeln mit Startjahr, zum Beispiel:

```python
if st in {"BW", "BY", "ST"}:
    result.append(reg(date(year, 1, 6), "Heilige Drei Könige"))
if (st == "BE" and year >= 2019) or (st == "MV" and year >= 2023):
    result.append(reg(date(year, 3, 8), "Internationaler Frauentag"))
if st in {"BW", "BY", "HE", "NW", "RP", "SL"}:
    result.append(reg(easter + timedelta(days=60), "Fronleichnam"))
```

Die vollständige Datei steht in [`holidays.py`](../../beispiele/feiertage-python/src/feiertage_mcp/holidays.py). Sie kennt kein MCP und lässt sich deshalb getrennt testen. Diese Trennung lohnt sich bei jedem Server: Die Fachlogik bleibt unabhängig, die MCP-Schicht bleibt dünn.

## MCP-Server in Python

### Projekt anlegen

```bash
mkdir feiertage-python && cd feiertage-python
uv init --package --name feiertage-mcp
uv add "mcp>=2.3,<3"
uv add --optional test pytest anyio
```

`uv init --package` legt bereits einen Startbefehl `feiertage-mcp = "feiertage_mcp:main"` an. Ändern Sie ihn so, dass er auf das Servermodul zeigt; die fertige [`pyproject.toml`](../../beispiele/feiertage-python/pyproject.toml) des Beispiels nutzt Hatchling als Build-Backend:

```toml
[project.scripts]
feiertage-mcp = "feiertage_mcp.server:main"
```

Kopieren Sie dann [`holidays.py`](../../beispiele/feiertage-python/src/feiertage_mcp/holidays.py) und [`server.py`](../../beispiele/feiertage-python/src/feiertage_mcp/server.py) aus dem Beispiel nach `src/feiertage_mcp/`. Der Auszug im nächsten Abschnitt ist gekürzt und allein nicht lauffähig. Mit einem lokalen Klon des Repositorys unter `$KLON`:

```bash
cp "$KLON/beispiele/feiertage-python/src/feiertage_mcp/holidays.py" \
   "$KLON/beispiele/feiertage-python/src/feiertage_mcp/server.py" src/feiertage_mcp/
```

### Der Server

Die MCP-Schicht in [`server.py`](../../beispiele/feiertage-python/src/feiertage_mcp/server.py), gekürzt um das zweite Tool und die Hilfsfunktion `_out`, die einen Feiertag in `HolidayOut` umwandelt:

```python
import logging
import sys
from typing import Annotated

from pydantic import BaseModel, Field

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from .holidays import STATES, check_state, holidays

# Bei stdio gehört stdout dem Protokoll. Logs gehen deshalb nach stderr.
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("feiertage-mcp")

mcp = MCPServer(
    "feiertage",
    version="0.1.0",
    instructions="Gesetzliche Feiertage und Arbeitstage je Bundesland in Deutschland, offline berechnet.",
)

READ_ONLY = ToolAnnotations(read_only_hint=True, idempotent_hint=True, open_world_hint=False)
StateCode = Annotated[str, Field(description="Kürzel des Bundeslands, z. B. BY, NW, BE", min_length=2, max_length=2)]


class HolidayOut(BaseModel):
    date: str = Field(description="Datum im Format JJJJ-MM-TT")
    name: str
    weekday: str
    nationwide: bool = Field(description="true, wenn der Feiertag in ganz Deutschland gilt")


class HolidayList(BaseModel):
    year: int
    state: str
    state_name: str
    count: int
    holidays: list[HolidayOut]


@mcp.tool(title="Feiertage eines Bundeslands", annotations=READ_ONLY)
def list_holidays(
    year: Annotated[int, Field(description="Jahr, 1995 bis 2100")],
    state: StateCode,
) -> HolidayList:
    """Listet die gesetzlichen Feiertage eines Jahres für ein Bundesland."""
    log.info("list_holidays year=%s state=%s", year, state)
    try:
        code = check_state(state)
        items = holidays(year, code)
    except ValueError as exc:
        raise ToolError(str(exc))
    return HolidayList(year=year, state=code, state_name=STATES[code], count=len(items),
                       holidays=[_out(h) for h in items])


def main() -> None:
    log.info("feiertage-mcp startet (stdio)")
    mcp.run()
```

Was hier passiert:

- `MCPServer(...)` erzeugt den Server. `instructions` landet in der Antwort auf `server/discover` und hilft dem Modell, den Server einzuordnen.
- `@mcp.tool(...)` meldet die Funktion als Tool an. Name ist der Funktionsname, Beschreibung der Docstring.
- Die Typen der Parameter werden zum `inputSchema`. `Field(description=...)` gibt dem Modell Hinweise, `min_length` und `max_length` werden zu JSON-Schema-Regeln.
- Der Rückgabetyp `HolidayList` (ein Pydantic-Modell) erzeugt automatisch ein `outputSchema`, und das SDK liefert das Ergebnis als `structuredContent` plus Text.
- `mcp.run()` startet standardmäßig den stdio-Transport. Mit `mcp.run("streamable-http", host="127.0.0.1", port=8765)` läuft derselbe Server als HTTP-Dienst.

### Starten

```bash
uv run feiertage-mcp
```

Der Prozess wartet dann still auf JSON-RPC-Zeilen. Das ist richtig so: Ein stdio-Server ist kein interaktives Programm, sondern wird vom Client gestartet.

## MCP-Server in TypeScript

### Projekt anlegen

```bash
mkdir feiertage-typescript && cd feiertage-typescript
npm init -y
npm install @modelcontextprotocol/server@^2.3.1 zod@^4.2.0
npm install -D typescript@^5.9.0 @types/node@^22 @modelcontextprotocol/client@^2.3.1
```

Das TypeScript-SDK ist seit v2 in Pakete aufgeteilt: `@modelcontextprotocol/server` für Server, `@modelcontextprotocol/client` für Clients. Das alte Sammelpaket `@modelcontextprotocol/sdk` ist die 1.x-Wartungslinie (1.32.1). Das Server-Paket verlangt Node.js 20 oder neuer.

In der [`package.json`](../../beispiele/feiertage-typescript/package.json) sind `"type": "module"` und ein `bin`-Eintrag wichtig:

```json
{
  "name": "feiertage-mcp",
  "type": "module",
  "bin": { "feiertage-mcp": "dist/index.js" },
  "scripts": { "build": "tsc", "prepare": "tsc", "test": "tsc && node --test test/server.test.mjs" }
}
```

In der Datei, die `npm init -y` angelegt hat, ergänzen Sie diese Einträge von Hand oder per Befehl:

```bash
npm pkg set type=module bin.feiertage-mcp=dist/index.js scripts.build=tsc scripts.prepare=tsc
```

Dazu kommt eine `tsconfig.json` im Projektordner. Ohne sie gibt `tsc` nur seine Hilfe aus, und `npm run build` erzeugt kein `dist/`. Sie übersetzt `src/` nach `dist/` und erzeugt ES-Module für Node ([`tsconfig.json`](../../beispiele/feiertage-typescript/tsconfig.json) des Beispiels):

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "skipLibCheck": true,
    "types": ["node"]
  },
  "include": ["src"]
}
```

Kopieren Sie schließlich [`src/holidays.ts`](../../beispiele/feiertage-typescript/src/holidays.ts), [`src/server.ts`](../../beispiele/feiertage-typescript/src/server.ts) und [`src/index.ts`](../../beispiele/feiertage-typescript/src/index.ts) aus dem Beispiel nach `src/`. Der Auszug im nächsten Abschnitt ist gekürzt und allein nicht lauffähig:

```bash
mkdir -p src
cp "$KLON"/beispiele/feiertage-typescript/src/*.ts src/
```

### Der Server

Aus [`src/server.ts`](../../beispiele/feiertage-typescript/src/server.ts), gekürzt um das zweite Tool und die Hilfsfunktion `withWeekday`, die den Wochentag ergänzt:

```typescript
import { McpServer, type CallToolResult } from "@modelcontextprotocol/server";
import { serveStdio } from "@modelcontextprotocol/server/stdio";
import * as z from "zod/v4";

import { STATES, checkState, holidays, type Holiday } from "./holidays.js";

// Bei stdio gehört stdout dem Protokoll: Logs nur über console.error (stderr).
const log = (msg: string) => console.error(`${new Date().toISOString()} feiertage-mcp: ${msg}`);

const READ_ONLY = { readOnlyHint: true, idempotentHint: true, openWorldHint: false };
const stateSchema = z.string().length(2).describe("Kürzel des Bundeslands, z. B. BY, NW, BE");
const holidayOut = z.object({
  date: z.string().describe("Datum im Format JJJJ-MM-TT"),
  name: z.string(),
  weekday: z.string(),
  nationwide: z.boolean().describe("true, wenn der Feiertag in ganz Deutschland gilt"),
});

function ok<T extends Record<string, unknown>>(data: T): CallToolResult {
  return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }], structuredContent: data };
}

function toolError(err: unknown): CallToolResult {
  const text = err instanceof Error ? err.message : String(err);
  log(`Tool-Fehler: ${text}`);
  return { content: [{ type: "text", text }], isError: true };
}

export function createServer(): McpServer {
  const server = new McpServer(
    { name: "feiertage", version: "0.1.0" },
    { instructions: "Gesetzliche Feiertage und Arbeitstage je Bundesland in Deutschland, offline berechnet." },
  );

  server.registerTool(
    "list_holidays",
    {
      title: "Feiertage eines Bundeslands",
      description: "Listet die gesetzlichen Feiertage eines Jahres für ein Bundesland.",
      inputSchema: z.object({ year: z.number().int().describe("Jahr, 1995 bis 2100"), state: stateSchema }),
      outputSchema: z.object({
        year: z.number().int(), state: z.string(), state_name: z.string(),
        count: z.number().int(), holidays: z.array(holidayOut),
      }),
      annotations: READ_ONLY,
    },
    async ({ year, state }) => {
      log(`list_holidays year=${year} state=${state}`);
      try {
        const code = checkState(state);
        const items = holidays(year, code).map(withWeekday);
        return ok({ year, state: code, state_name: STATES[code], count: items.length, holidays: items });
      } catch (err) {
        return toolError(err);
      }
    },
  );

  return server;
}

export function main(): void {
  log("feiertage-mcp startet (stdio)");
  serveStdio(createServer);
}
```

Die Einstiegsdatei [`src/index.ts`](../../beispiele/feiertage-typescript/src/index.ts) ruft nur `main()` auf und beginnt mit `#!/usr/bin/env node`, damit `npx` sie direkt ausführen kann.

`serveStdio` bekommt eine **Fabrikfunktion**, keinen fertigen Server. Laut SDK-Doku entscheidet die erste Nachricht der Verbindung, ob ein Client nach 2026-07-28 oder nach dem alten `initialize`-Verfahren spricht; die Fabrik liefert für beide Fälle dieselbe Konfiguration. Bauen und testen:

```bash
npm run build
node dist/index.js
```

Im Unterschied zu Python bauen Sie Ergebnisse in TypeScript selbst: `content` als Text für ältere Clients und `structuredContent` passend zum `outputSchema`. Die Spezifikation empfiehlt genau diese Doppelung.

## Eingabeschema, structuredContent und Annotations

Aus dem Code oben erzeugen beide SDKs eine Tool-Beschreibung. So meldet der Python-Server sein Tool per `tools/list` (echte Ausgabe, gekürzt):

```json
{
  "name": "list_holidays",
  "title": "Feiertage eines Bundeslands",
  "description": "Listet die gesetzlichen Feiertage eines Jahres für ein Bundesland.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "year": {"description": "Jahr, 1995 bis 2100", "title": "Year", "type": "integer"},
      "state": {"description": "Kürzel des Bundeslands, z. B. BY, NW, BE",
                "maxLength": 2, "minLength": 2, "title": "State", "type": "string"}
    },
    "required": ["year", "state"]
  },
  "outputSchema": {"title": "HolidayList", "type": "object", "properties": {"...": "..."}},
  "annotations": {"idempotentHint": true, "openWorldHint": false, "readOnlyHint": true}
}
```

Drei Punkte zum Mitnehmen:

- **Beschreibungen sind Prompt.** Das Modell wählt Tools nur anhand von Name, Beschreibung und Schema. Schreiben Sie, was das Tool tut, welche Formate erwartet werden und welche Grenzen gelten.
- **`structuredContent`** ist maschinenlesbares JSON, das zum `outputSchema` passen muss. Clients können es validieren und weiterverarbeiten, statt Text zu parsen.
- **Annotations** beschreiben Verhalten: `readOnlyHint` (ändert nichts), `destructiveHint` (kann löschen oder überschreiben), `idempotentHint` (wiederholbar ohne Nebenwirkung), `openWorldHint` (spricht mit externen Systemen). Clients nutzen sie für Freigaben; Codex etwa fragt im Modus `writes` nur bei Tools nach, die nicht als nur lesend markiert sind. Die Spezifikation stellt klar: Annotations sind Hinweise und nur bei vertrauenswürdigen Servern verlässlich.

## Fehlerbehandlung

MCP kennt zwei Fehlerarten ([Tools, Error Handling](https://modelcontextprotocol.io/specification/2026-07-28/server/tools#error-handling), abgerufen 19.10.2026):

1. **Protokollfehler** als JSON-RPC-`error`, etwa bei kaputten Anfragen. Das Modell kann damit wenig anfangen.
2. **Tool-Ausführungsfehler** als normales Ergebnis mit `isError: true` und einer verständlichen Meldung. Das Modell liest sie und kann es mit anderen Parametern erneut versuchen.

Fachliche Fehler gehören in die zweite Gruppe. In Python lösen Sie dafür `ToolError` aus, in TypeScript geben Sie `isError: true` zurück. Echte Antworten beider Server vom 19.10.2026:

```text
Python, falsches Bundesland:
{"isError": true, "content": [{"type": "text", "text": "Error executing tool list_holidays: Unbekanntes Bundesland 'XX'. Erlaubt sind: BW, BY, BE, BB, HB, HH, HE, MV, NI, NW, RP, SL, SN, ST, SH, TH."}]}

TypeScript, Jahr als Text statt Zahl (Prüfung durch das zod-Schema):
{"isError": true, "content": [{"type": "text", "text": "Input validation error: Invalid arguments for tool list_holidays: year: Invalid input: expected number, received string"}]}
```

Ein Unterschied der SDKs fiel im Test auf: Bei einem unbekannten Tool-Namen antwortete der TypeScript-Server mit dem Protokollfehler `-32602` (`Tool gibtsnicht not found`), wie im Beispiel der Spezifikation. Das Python-SDK 2.3.0 lieferte stattdessen ein Ergebnis mit `isError: true` und `Unknown tool: gibtsnicht`. Clients sollten beides verarbeiten.

Für unerwartete Ausnahmen gilt in Python: Alles, was kein `ToolError` ist, meldet das SDK dem Modell nur als `Error executing tool <name>` und schreibt den Stacktrace ins Log. So gelangen keine internen Details wie Pfade oder Zugangsdaten zum Modell. Bauen Sie Ihre Meldungen deshalb bewusst: Was soll das Modell wissen, um es besser zu machen?

## Logging nach stderr, nie nach stdout

Beim stdio-Transport liest der Client jede Zeile auf stdout als JSON-RPC-Nachricht. Die Spezifikation sagt: Der Server darf auf stdout nichts schreiben, was keine gültige MCP-Nachricht ist, und darf stderr für Logs nutzen ([stdio](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio), abgerufen 19.10.2026).

Typische Fehlerquellen:

- `print()` in Python oder `console.log()` in Node. Nutzen Sie `logging` mit `stream=sys.stderr` bzw. `console.error()`.
- Bibliotheken, die beim Import Banner oder Warnungen auf stdout schreiben.
- Startskripte, die vor dem Server etwas ausgeben, etwa `npm` mit Hinweisen. Starten Sie in der Client-Konfiguration besser `node dist/index.js` oder `npx -y paket` als `npm start`.

Das Protokoll-Logging (`notifications/message`) ist seit 2026-07-28 abgekündigt. Die Spezifikation empfiehlt stderr oder OpenTelemetry. Clients zeigen stderr meist in ihren Logs an, Claude Desktop zum Beispiel in `mcp-server-<NAME>.log`. Wo die Logs je Client liegen, steht in [MCP-Clients einrichten](./mcp-clients-einrichten.md#fehlersuche).

## Testen: Client, Inspector und pytest

### Mit dem Python-Client des SDK

```python
import asyncio
from mcp import Client
from mcp.client.stdio import StdioServerParameters

async def main():
    params = StdioServerParameters(command="uv", args=["run", "--directory", "feiertage-python", "feiertage-mcp"])
    async with Client(params) as client:
        print("Protokoll:", client.protocol_version)
        for tool in (await client.list_tools()).tools:
            print("-", tool.name)
        result = await client.call_tool("count_working_days",
                                        {"start": "2026-12-01", "end": "2026-12-31", "state": "NW"})
        print(result.structured_content)

asyncio.run(main())
```

Echte Ausgabe vom 19.10.2026 (Struktur zur Lesbarkeit gekürzt):

```text
Protokoll: 2026-07-28
- list_holidays
- count_working_days
{'start': '2026-12-01', 'end': '2026-12-31', 'state': 'NW', 'working_days': 22,
 'holidays_on_workdays': [{'date': '2026-12-25', 'name': '1. Weihnachtstag', 'weekday': 'Freitag', 'nationwide': True}]}
```

Der Client handelt die Version selbst aus: Er probiert `server/discover` und fällt bei älteren Servern auf `initialize` zurück.

### Mit dem MCP Inspector im CLI-Modus

Der offizielle Inspector läuft per `npx` ohne globale Installation. Mit `--cli` gibt er JSON aus, statt eine Weboberfläche zu öffnen:

```bash
npx -y @modelcontextprotocol/inspector@2.11.0 --cli node dist/index.js \
  --method tools/call --tool-name count_working_days \
  --tool-arg start=2026-12-01 --tool-arg end=2026-12-31 --tool-arg state=NW
```

Echte Ausgabe gegen den TypeScript-Server (gekürzt):

```json
{
  "content": [{"type": "text", "text": "{\n  \"start\": \"2026-12-01\", ..."}],
  "structuredContent": {
    "start": "2026-12-01", "end": "2026-12-31", "state": "NW", "working_days": 22,
    "holidays_on_workdays": [{"date": "2026-12-25", "name": "1. Weihnachtstag", "nationwide": true, "weekday": "Freitag"}]
  }
}
```

Für den Python-Server ersetzen Sie `node dist/index.js` durch `.venv/bin/python -m feiertage_mcp.server`. Mit `--method tools/list` sehen Sie die Tool-Beschreibungen. Die Version 0.21 des Inspectors funktioniert ebenfalls, meldet aber, dass v1 nur noch Sicherheitsupdates bekommt.

### Automatische Tests

Das Python-Beispiel enthält [`tests/test_server.py`](../../beispiele/feiertage-python/tests/test_server.py) mit sechs Tests: Osterformel, landesspezifische Feiertage, Arbeitstage Dezember 2026, Tool-Aufruf im selben Prozess, Fehlerfall und ein echter stdio-Durchlauf. Für schnelle Tests verbindet sich der Client direkt mit dem Serverobjekt, ganz ohne Unterprozess:

```python
async def test_tool_error_for_unknown_state():
    async with Client(mcp) as client:
        result = await client.call_tool("list_holidays", {"year": 2026, "state": "XX"})
        assert result.is_error
        assert "Unbekanntes Bundesland" in result.content[0].text
```

```bash
uv run --extra test pytest -q
```

```text
......                                                                   [100%]
6 passed in 1.52s
```

Das TypeScript-Beispiel testet mit dem Node-Testrunner und `@modelcontextprotocol/client` über stdio:

```bash
npm ci && npm test
```

```text
# tests 3
# pass 3
# fail 0
```

## Paketieren und starten mit uvx und npx

MCP-Clients starten stdio-Server mit einem Befehl. Am bequemsten für Nutzer sind `uvx` (Python) und `npx` (Node), weil sie das Paket bei Bedarf in einen Cache laden und ohne manuelle Installation starten.

**Python.** Mit dem `[project.scripts]`-Eintrag startet der Server direkt aus einem Git-Repository oder einem lokalen Ordner:

```bash
uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=beispiele/feiertage-python" feiertage-mcp
uvx --from ./feiertage-python feiertage-mcp
```

Den lokalen Aufruf haben wir getestet; der Git-Aufruf setzt voraus, dass der Ordner im öffentlichen Repository liegt. Nach einer Veröffentlichung auf PyPI (`uv build`, dann `uv publish`) genügt `uvx feiertage-mcp`.

**TypeScript.** `npm pack` erzeugt ein Paket mit `dist/`, `package.json` und `README.md` (im Test am 20.10.2026 5 Dateien, 4,5 kB). Lokal getestet:

```bash
npm pack
npx -y --package ./feiertage-mcp-0.1.0.tgz feiertage-mcp
```

Nach `npm publish` starten Nutzer den Server mit `npx -y <paketname>`. Der Eintrag `"prepare": "tsc"` sorgt dafür, dass auch eine Installation direkt aus Git den Code übersetzt; diesen Weg haben wir nicht getestet.

## Veröffentlichen in der MCP Registry

Die [MCP Registry](https://registry.modelcontextprotocol.io) speichert nur Metadaten. Das Paket selbst liegt weiter auf PyPI oder npm ([Quickstart](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/quickstart.mdx), abgerufen 19.10.2026). Der Ablauf, hier nur beschrieben:

1. Paket auf npm oder PyPI veröffentlichen.
2. Besitz nachweisen: bei npm über `"mcpName": "io.github.<konto>/feiertage"` in der `package.json`, bei PyPI über eine Zeile `mcp-name: io.github.<konto>/feiertage` in der README (darf in einem HTML-Kommentar stehen).
3. Das Werkzeug `mcp-publisher` installieren und mit `mcp-publisher init` eine `server.json` erzeugen.
4. Mit `mcp-publisher login github` anmelden (Namensraum `io.github.<konto>/`) und mit `mcp-publisher publish` veröffentlichen.

Eine `server.json` für den Feiertage-Server mit beiden Paketen könnte so aussehen. Sie ist gegen das offizielle Schema `2025-12-11` validiert (mit `jsonschema`, am 19.10.2026), aber nicht veröffentlicht:

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.muster-gmbh/feiertage",
  "title": "Feiertage Deutschland",
  "description": "Gesetzliche Feiertage und Arbeitstage je Bundesland, offline berechnet.",
  "repository": { "url": "https://github.com/muster-gmbh/feiertage-mcp", "source": "github" },
  "version": "0.1.0",
  "packages": [
    { "registryType": "pypi", "identifier": "feiertage-mcp", "version": "0.1.0",
      "runtimeHint": "uvx", "transport": { "type": "stdio" } },
    { "registryType": "npm", "identifier": "@muster-gmbh/feiertage-mcp", "version": "0.1.0",
      "runtimeHint": "npx", "transport": { "type": "stdio" } }
  ]
}
```

Braucht Ihr Server Zugangsdaten, beschreiben Sie diese unter `environmentVariables` mit `isSecret: true`. Den Wert selbst tragen Nutzer in ihrem Client ein, nie in die `server.json`.

## Häufige Fragen

### Wie erstelle ich einen MCP-Server mit Python?

Installieren Sie `mcp` 2.x, erzeugen Sie mit `MCPServer("name")` einen Server und melden Sie Funktionen mit `@mcp.tool()` an. `mcp.run()` startet ihn über stdio. Das vollständige Beispiel steht in [`beispiele/feiertage-python`](../../beispiele/feiertage-python/).

### Warum funktioniert `from mcp.server.fastmcp import FastMCP` nicht mehr?

Seit `mcp` 2.0 heißt die Klasse `MCPServer` und liegt unter `mcp.server`. Für alten Code können Sie `mcp<2` festschreiben. Das separate Paket `fastmcp` ist ein anderes Projekt.

### Wie erstelle ich einen MCP-Server mit TypeScript?

Installieren Sie `@modelcontextprotocol/server` und `zod`, legen Sie `new McpServer(...)` an, registrieren Sie Tools mit `registerTool` und starten Sie mit `serveStdio(createServer)`. Siehe [`beispiele/feiertage-typescript`](../../beispiele/feiertage-typescript/).

### Warum zeigt mein Client "Unexpected token" oder trennt die Verbindung?

Meist schreibt der Server etwas auf stdout, das kein JSON-RPC ist, etwa ein `print()` oder eine Startmeldung. Leiten Sie alle Ausgaben nach stderr um.

### Wie teste ich einen MCP-Server ohne Claude oder Cursor?

Mit dem MCP Inspector im CLI-Modus (`npx -y @modelcontextprotocol/inspector@2.11.0 --cli ...`) oder mit dem Client aus dem SDK. Für automatische Tests verbindet sich der Python-Client direkt mit dem Serverobjekt.

## Weiterlesen

- [Übersicht: MCP-Server für deutsche Geschäftssysteme](../../README.md)
- [MCP-Server-Liste](../liste.md)
- [Was ist ein MCP-Server?](./was-ist-ein-mcp-server.md)
- [MCP vs. API: Unterschied und wann Sie was brauchen](./mcp-vs-api.md)
- [MCP-Clients einrichten: Claude, Cursor, VS Code, Codex](./mcp-clients-einrichten.md)
- [MCP-Sicherheit](./mcp-sicherheit.md)
- [MCP und DSGVO](./mcp-dsgvo.md)
- [Anleitung zum DATEV-Format (EXTF)](./datev-mcp-server.md)
- [SAP MCP-Server](./sap-mcp-server.md)
- [Power BI MCP](./power-bi-mcp.md)
- [HubSpot MCP](./hubspot-mcp.md)
- [Postgres MCP](./postgres-mcp.md)
- [Buchhaltung und MCP](./buchhaltung-mcp.md)
- [Business Central MCP](./business-central-mcp.md)

> **Hinweis:** Technische Informationen nach Stand 19.10.2026, ohne Gewähr für Vollständigkeit
> und Richtigkeit. Keine Rechts- oder Steuerberatung; die Autoren sind keine Rechtsanwälte,
> Steuerberater oder Datenschutzbeauftragten. Produktnamen sind Marken ihrer Inhaber; es besteht
> keine Verbindung zu den genannten Herstellern.
