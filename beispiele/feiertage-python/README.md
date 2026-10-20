# Feiertage-MCP-Server (Python)

Beispiel aus der Anleitung [MCP-Server erstellen](../../docs/anleitungen/mcp-server-erstellen.md): ein kleiner MCP-Server mit dem offiziellen Python-SDK `mcp` 2.3, der gesetzliche Feiertage und Arbeitstage je Bundesland berechnet. Er braucht kein Netz und keine API.

Werkzeuge (Tools):

- `list_holidays(year, state)`: gesetzliche Feiertage eines Jahres für ein Bundesland (`BY`, `NW`, `BE` ...).
- `count_working_days(start, end, state, saturday_is_workday=false)`: Arbeitstage zwischen zwei Daten.

Nicht enthalten sind Feiertage, die nur in einzelnen Gemeinden gelten (Fronleichnam in Teilen von Sachsen und Thüringen, Mariä Himmelfahrt in Teilen Bayerns, Augsburger Friedensfest).

## Starten

```bash
uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=beispiele/feiertage-python" feiertage-mcp
```

Lokal aus diesem Ordner:

```bash
uv run feiertage-mcp
```

Der Server spricht stdio. Er wartet still auf JSON-RPC-Nachrichten; Logs erscheinen auf stderr.

## Testen

```bash
uv run --extra test pytest -q
```

Der Test prüft die Osterformel, landesspezifische Feiertage, die Arbeitstage im Dezember 2026 und einen echten stdio-Aufruf mit dem SDK-Client.

## Lizenz

MIT, wie das übrige Repository. Ohne Gewähr; für verbindliche Fristen prüfen Sie die Feiertagsgesetze Ihres Bundeslands.
