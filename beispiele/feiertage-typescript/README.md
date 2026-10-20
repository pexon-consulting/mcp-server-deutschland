# Feiertage-MCP-Server (TypeScript)

Beispiel aus der Anleitung [MCP-Server erstellen](../../docs/anleitungen/mcp-server-erstellen.md): derselbe Server wie in [`../feiertage-python`](../feiertage-python/), gebaut mit dem offiziellen TypeScript-SDK `@modelcontextprotocol/server` 2.3. Er berechnet gesetzliche Feiertage und Arbeitstage je Bundesland ohne Netz und ohne externe API.

Werkzeuge (Tools):

- `list_holidays(year, state)`: gesetzliche Feiertage eines Jahres für ein Bundesland (`BY`, `NW`, `BE` ...).
- `count_working_days(start, end, state, saturday_is_workday=false)`: Arbeitstage zwischen zwei Daten.

Voraussetzung: Node.js 20 oder neuer.

## Bauen und testen

```bash
npm ci
npm test
```

`npm test` übersetzt den Code nach `dist/` und startet den Server einmal über stdio mit dem offiziellen Client `@modelcontextprotocol/client`.

## Starten

```bash
node dist/index.js
```

Mit dem MCP Inspector (ohne globale Installation):

```bash
npx -y @modelcontextprotocol/inspector@2.11.0 --cli node dist/index.js --method tools/list
```

Der Server spricht stdio. Logs erscheinen auf stderr, stdout gehört dem Protokoll.

## Lizenz

MIT, wie das übrige Repository. Ohne Gewähr; für verbindliche Fristen prüfen Sie die Feiertagsgesetze Ihres Bundeslands.
