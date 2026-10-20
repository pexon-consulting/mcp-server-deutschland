// MCP-Server "Feiertage und Arbeitstage in Deutschland" (TypeScript-SDK v2).
import { McpServer, type CallToolResult } from "@modelcontextprotocol/server";
import { serveStdio } from "@modelcontextprotocol/server/stdio";
import * as z from "zod/v4";

import { STATES, checkState, holidays, parseDate, workingDays, type Holiday } from "./holidays.js";

// Bei stdio gehört stdout dem Protokoll: Logs nur über console.error (stderr).
const log = (msg: string) => console.error(`${new Date().toISOString()} feiertage-mcp: ${msg}`);

const WEEKDAYS = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];
const withWeekday = (h: Holiday) => ({ ...h, weekday: WEEKDAYS[new Date(`${h.date}T00:00:00Z`).getUTCDay()]! });

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
      inputSchema: z.object({
        year: z.number().int().describe("Jahr, 1995 bis 2100"),
        state: stateSchema,
      }),
      outputSchema: z.object({
        year: z.number().int(),
        state: z.string(),
        state_name: z.string(),
        count: z.number().int(),
        holidays: z.array(holidayOut),
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

  server.registerTool(
    "count_working_days",
    {
      title: "Arbeitstage zählen",
      description: "Zählt die Arbeitstage zwischen zwei Daten (Mo-Fr ohne gesetzliche Feiertage des Bundeslands).",
      inputSchema: z.object({
        start: z.string().describe("Erster Tag, JJJJ-MM-TT (inklusive)"),
        end: z.string().describe("Letzter Tag, JJJJ-MM-TT (inklusive)"),
        state: stateSchema,
        saturday_is_workday: z.boolean().default(false).describe("Samstag als Arbeitstag zählen"),
      }),
      outputSchema: z.object({
        start: z.string(),
        end: z.string(),
        state: z.string(),
        working_days: z.number().int(),
        holidays_on_workdays: z.array(holidayOut),
      }),
      annotations: READ_ONLY,
    },
    async ({ start, end, state, saturday_is_workday }) => {
      log(`count_working_days ${start}..${end} state=${state}`);
      try {
        const code = checkState(state);
        const { count, skipped } = workingDays(parseDate(start, "start"), parseDate(end, "end"), code, saturday_is_workday);
        return ok({ start, end, state: code, working_days: count, holidays_on_workdays: skipped.map(withWeekday) });
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
