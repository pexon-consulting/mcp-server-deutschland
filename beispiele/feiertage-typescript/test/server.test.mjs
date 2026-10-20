import assert from "node:assert/strict";
import { test } from "node:test";

import { Client } from "@modelcontextprotocol/client";
import { StdioClientTransport } from "@modelcontextprotocol/client/stdio";

import { easterSunday, holidays, iso } from "../dist/holidays.js";

test("Osterformel", () => {
  assert.equal(iso(easterSunday(2024)), "2024-03-31");
  assert.equal(iso(easterSunday(2026)), "2026-04-05");
});

test("Buß- und Bettag nur in Sachsen", () => {
  assert.deepEqual(holidays(2026, "SN").filter((h) => h.name === "Buß- und Bettag").map((h) => h.date), ["2026-11-18"]);
  assert.equal(holidays(2026, "BY").length, 12);
});

test("stdio: tools/list und tools/call", async () => {
  const client = new Client({ name: "feiertage-test", version: "0.0.1" });
  await client.connect(new StdioClientTransport({ command: process.execPath, args: ["dist/index.js"], stderr: "ignore" }));
  try {
    const { tools } = await client.listTools();
    assert.deepEqual(tools.map((t) => t.name), ["list_holidays", "count_working_days"]);

    const res = await client.callTool({
      name: "count_working_days",
      arguments: { start: "2026-12-01", end: "2026-12-31", state: "NW" },
    });
    assert.equal(res.isError ?? false, false);
    assert.equal(res.structuredContent.working_days, 22);

    const bad = await client.callTool({ name: "list_holidays", arguments: { year: 2026, state: "XX" } });
    assert.equal(bad.isError, true);
    assert.match(bad.content[0].text, /Unbekanntes Bundesland/);
  } finally {
    await client.close();
  }
});
