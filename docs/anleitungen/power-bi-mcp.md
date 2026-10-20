# Power BI MCP Server: Authoring, Fabric IQ und Einrichtung in Claude und Copilot

Diese Anleitung ist für BI-Entwickler, Power-BI-Admins und Datenteams, die Power BI per Model Context Protocol (MCP) mit Claude, GitHub Copilot oder anderen KI-Clients verbinden wollen. Sie erklärt die offiziellen Power BI MCP Server von Microsoft, den Unterschied zwischen lokal und remote, die Voraussetzungen und die Risiken.

Stand: 19.10.2026

## Inhaltsverzeichnis

- [Das Wichtigste in Kürze](#das-wichtigste-in-kürze)
- [Welche Power BI MCP Server gibt es?](#welche-power-bi-mcp-server-gibt-es)
- [Lokal oder remote: der Unterschied](#lokal-oder-remote-der-unterschied)
- [Voraussetzungen: Rechte, Lizenzen, Tenant, Entra](#voraussetzungen-rechte-lizenzen-tenant-entra)
- [Einrichtung in VS Code mit GitHub Copilot](#einrichtung-in-vs-code-mit-github-copilot)
- [Einrichtung in GitHub Copilot CLI](#einrichtung-in-github-copilot-cli)
- [Power BI MCP Server in Claude Code und Claude Desktop](#power-bi-mcp-server-in-claude-code-und-claude-desktop)
- [Beispiel 1: DAX-Measure anlegen](#beispiel-1-dax-measure-anlegen)
- [Beispiel 2: Daten abfragen](#beispiel-2-daten-abfragen)
- [Risiken und wie Sie sie begrenzen](#risiken-und-wie-sie-sie-begrenzen)
- [Community-Server](#community-server)
- [Häufige Fragen](#häufige-fragen)
- [Weiterlesen](#weiterlesen)

## Das Wichtigste in Kürze

- Microsoft führt zwei Power BI MCP Server: den **Power BI Authoring MCP Server** zum Bauen und Ändern semantischer Modelle und **Fabric IQ** zum Abfragen. Daneben gibt es noch den älteren **Power BI Consumption MCP Server** (Vorschau).
- Den Authoring-Server gibt es **gehostet (Preview)** unter `https://api.fabric.microsoft.com/v1/mcp/powerbi/authoring` und **lokal (allgemein verfügbar)** als npm-Paket `@microsoft/powerbi-modeling-mcp`.
- Fabric IQ ist laut Microsoft **allgemein verfügbar**, nur lesend und erreichbar unter `https://fabriciq.svc.cloud.microsoft/v1/mcp/fabriciq`.
- Der lokale Server läuft laut Microsoft Learn **nicht auf macOS**. Am Mac nutzen Sie den gehosteten Server.
- Microsoft Entra ID unterstützt keine Dynamic Client Registration. Clients, die darauf angewiesen sind, brauchen eine eigene App-Registrierung.

## Welche Power BI MCP Server gibt es?

Die Übersicht auf [Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/developer/mcp/mcp-servers-overview) (abgerufen 19.10.2026) teilt nach Aufgabe ein:

| Sie wollen | Server | Status |
| --- | --- | --- |
| Tabellen, Spalten, Measures, Beziehungen, Rollen anlegen oder ändern | Power BI Authoring MCP Server | gehostet: Preview, lokal: GA |
| Best Practices prüfen, DAX umbauen, Modell dokumentieren | Power BI Authoring MCP Server | wie oben |
| mit Power BI Desktop oder TMDL-Dateien im Git arbeiten | Power BI Authoring MCP Server, lokal | GA |
| Fachfragen auf Power-BI-Daten beantworten | Fabric IQ | GA |
| eigene Agenten, Copilot Studio oder Microsoft 365 Copilot mit Power-BI-Daten versorgen | Fabric IQ | GA |
| bestehende Integrationen mit dem alten Abfrage-Endpunkt | Power BI Consumption MCP Server | Preview |

Microsoft schreibt ausdrücklich: Den Authoring-Server nicht für Endnutzer-Abfragen verwenden. Er kann DAX ausführen, aber nur zum Prüfen des Modells.

### Power BI Authoring MCP Server

Früher hieß er "Power BI Modeling MCP Server". Das GitHub-Repository heißt weiterhin [microsoft/powerbi-modeling-mcp](https://github.com/microsoft/powerbi-modeling-mcp) (1.233 Sterne, letzter Push 29.09.2026, gh api 19.10.2026). Das npm-Paket `@microsoft/powerbi-modeling-mcp` steht auf Version 1.0.0.

Zur Lizenz: GitHub zeigt für das Repository MIT. Das README sagt aber: "Use of this software is subject to the Power BI Authoring MCP Server EULA". Vor der ersten Nutzung über npm müssen Sie die EULA annehmen, entweder interaktiv über das Tool `accept_eula`, mit dem Argument `--accepteula` oder mit der Umgebungsvariable `PBI_MODELING_MCP_ACCEPT_EULA=true`.

Das README listet Tool-Gruppen wie `connection_operations`, `measure_operations`, `relationship_operations`, `dax_query_operations`, `transaction_operations`, `security_role_operations` und `object_translation_operations`.

### Fabric IQ

Fabric IQ ist laut [Microsoft Learn](https://learn.microsoft.com/en-us/fabric/iq/connectors/fabric-iq-mcp) ein Remote-Server mit nur lesenden Tools:

| Tool | Zweck |
| --- | --- |
| `DiscoverArtifacts` | Berichte und semantische Modelle nach Namen suchen |
| `ResolveFabricItem` | eine Fabric-URL aus dem Browser auflösen |
| `GetReportMetadata` | Metadaten eines Berichts |
| `GetSemanticModelSchema` | Schema eines Modells |
| `ValueSearch` | gespeicherte Werte in einem Modell finden |
| `ExecuteQuery` | eine DAX-Abfrage ausführen |

Fabric IQ hat kein Tool, das selbst in natürlicher Sprache antwortet. Ihr KI-Client baut die DAX-Abfrage und erklärt das Ergebnis. Ohne `maxRows` liefert `ExecuteQuery` höchstens 250 Zeilen.

Die Übersichtsseite schreibt den Pfad `/v1/mcp/FabricIQ`, die Einrichtungsseite `/v1/mcp/fabriciq`. Wir verwenden die Schreibweise der Einrichtungsseite. Unter dieser Adresse liefert der Server am 19.10.2026 eine gültige Protected Resource Metadata.

### Power BI Consumption MCP Server (älter)

Der Endpunkt `https://api.fabric.microsoft.com/v1/mcp/powerbi` ist laut [Microsoft Learn](https://learn.microsoft.com/en-us/power-bi/developer/mcp/remote-mcp-server-get-started) in Preview. Er bietet die Tools Execute Query, Get Semantic Model Schema, Get Report Metadata und Generate Query. Für neue Projekte empfiehlt Microsoft Fabric IQ.

## Lokal oder remote: der Unterschied

Die Vergleichstabelle von Microsoft Learn für den Authoring-Server, ergänzt um Fabric IQ:

| Merkmal | Authoring lokal | Authoring gehostet | Fabric IQ |
| --- | --- | --- | --- |
| Transport | stdio | Streamable HTTP | Streamable HTTP |
| Installation | VS Code Extension, npm oder EXE | keine | keine |
| Lesen und Schreiben | ja, mit Bestätigung | ja | nur lesen |
| Power BI Desktop | ja | nein | nein |
| PBIP- und TMDL-Dateien auf der Platte | ja | nein | nein |
| Modelle im Fabric-Workspace | ja (über XMLA) | ja | ja |
| Service Principal | ja | nein | nein |
| Transaktionen und Traces | ja | nein | nein |
| macOS | nein | ja | ja |

Zwei Punkte, die in der Praxis wichtig sind:

- **Nicht beide Authoring-Varianten gleichzeitig registrieren.** Microsoft warnt, dass der Agent dann doppelte Tools sieht und Tokens verbraucht.
- **Der gehostete Authoring-Server ist zustandsbehaftet.** Ihr Client muss den Header `mcp-Session-Id` aus der Initialisierung bei jeder Anfrage mitschicken. Das entspricht der Protokollversion 2025-11-25. In Version 2026-07-28 gibt es diesen Header nicht mehr (siehe [Was ist ein MCP Server?](./was-ist-ein-mcp-server.md)).

Der lokale Server hat zwei Modi: `--readwrite` (Standard, mit Bestätigung vor der ersten Änderung je Datenbank) und `--readonly`.

## Voraussetzungen: Rechte, Lizenzen, Tenant, Entra

### Rechte am Modell

- **Write** auf dem semantischen Modell, um Objekte anzulegen oder zu ändern.
- **Build** reicht nur zum Ausführen von DAX-Abfragen (Authoring, Consumption).
- Fabric IQ braucht laut Microsoft weder Workspace-Rolle noch Build-Recht. Es gelten die vorhandenen Fabric-Rechte, dazu Row-Level und Object-Level Security.

### XMLA-Endpunkt und Kapazität

Der lokale Server greift auf Modelle im Fabric-Workspace über den XMLA-Endpunkt zu. Dieser muss auf der Kapazität auf **Read Write** stehen. Laut [Microsoft Learn zum XMLA-Endpunkt](https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-connect-tools) gibt es ihn für Workspaces auf Power BI Premium, Premium Per User (PPU), Power BI Embedded und Fabric-Kapazität.

Für Power BI Desktop und lokale PBIP-Dateien brauchen Sie keine Kapazität. Lizenzpreise nennen wir nicht. Prüfen Sie Ihren Vertrag oder die aktuelle Preisliste von Microsoft.

### Tenant-Einstellungen

- Gehosteter Authoring-Server und Consumption-Server: Ein Fabric-Admin muss "Users can use the Power BI Model Context Protocol server endpoint" einschalten.
- Für den lokalen Server gibt es laut Microsoft **keine eigene Tenant-Einstellung**. Wer ihn sperren will, muss den XMLA-Endpunkt abschalten. Das trifft dann alle XMLA-Werkzeuge.
- Fabric IQ ist nur verfügbar, wenn die Heimatregion des Tenants alle Fabric-Workloads unterstützt. Nicht in reinen Power-BI-Regionen und nicht in Sovereign Clouds.
- Das Tool Generate Query im Consumption-Server nutzt Copilot in Power BI und setzt eine Copilot-Lizenz voraus. Wenn Sie keine Copilot-Kapazität verbrauchen wollen, schalten Sie das Tool im Client ab.

### Microsoft Entra ID

Alle Remote-Server melden sich über Entra ID als angemeldeter Benutzer an. Am 19.10.2026 liefern die Endpunkte Protected Resource Metadata nach RFC 9728 mit dem Scope `https://api.fabric.microsoft.com/.default`.

Fabric IQ verlangt die delegierten Berechtigungen `Item.Read.All`, `Item.Execute.All` und `Dataset.Read.All` der Power BI Service API. Service Principals und App-only-Anmeldung gehen bei Fabric IQ nicht. Diese Berechtigungen brauchen laut Microsoft standardmäßig keine Admin-Zustimmung, sofern Ihr Tenant Benutzerzustimmung erlaubt.

Für den gehosteten Authoring-Server verweist Microsoft auf eine Seite "Register the hosted Power BI MCP servers with external MCP clients". Diese Seite konnten wir am 19.10.2026 nicht finden. Welche Berechtigungen dort genau verlangt werden, ist deshalb ungeprüft.

## Einrichtung in VS Code mit GitHub Copilot

VS Code ist der von Microsoft dokumentierte Weg. Die Konfiguration steht in `.vscode/mcp.json` (Workspace) oder in der Benutzer-`mcp.json`, Schlüssel `servers`.

Gehosteter Authoring-Server, laut Microsoft Learn:

```json
{
  "servers": {
    "powerbi-authoring-remote": {
      "type": "http",
      "url": "https://api.fabric.microsoft.com/v1/mcp/powerbi/authoring"
    }
  }
}
```

Lokaler Authoring-Server über npm (nur Windows):

```json
{
  "servers": {
    "powerbi-authoring-local": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@microsoft/powerbi-modeling-mcp@1.0.0", "--start"]
    }
  }
}
```

Beide Ausschnitte sind aus der Microsoft-Doku übernommen und hier nicht ausgeführt. Die Doku nennt `@latest`; hier ist stattdessen die feste Version `1.0.0` eingetragen (aktuelle Version auf npm am 20.10.2026), damit nicht bei jedem Start ungeprüft eine neue Fassung lädt. Eine neuere Version übernehmen Sie bewusst, nachdem Sie die Änderungen gelesen haben.

Wenn der Server in Copilot nicht erscheint: In Enterprise-Konten ist die Option "MCP servers in Copilot" auf GitHub.com standardmäßig aus. Ein Administrator muss sie einschalten.

## Einrichtung in GitHub Copilot CLI

Für Fabric IQ beschreibt Microsoft die Copilot CLI. Datei `~/.copilot/mcp-config.json` (Windows: `%USERPROFILE%\.copilot\mcp-config.json`):

```json
{
  "mcpServers": {
    "FabricIQ": {
      "type": "http",
      "url": "https://fabriciq.svc.cloud.microsoft/v1/mcp/fabriciq",
      "tools": ["*"]
    }
  }
}
```

Danach in der CLI `/mcp show FabricIQ` aufrufen und im Browser anmelden. Die Copilot CLI nutzt laut Microsoft eine vorregistrierte Entra-App. Tragen Sie keinen eigenen `Authorization`-Header ein, sonst überschreibt er die interaktive Anmeldung.

Um eine bestimmte Version des Tool-Vertrags festzuhalten, schickt der Client den Header `X-Variants: Fabric.Routing.FabricIQ.V1`. Ungetestet, weil kein Fabric-Tenant zur Verfügung stand.

## Power BI MCP Server in Claude Code und Claude Desktop

Für Claude dokumentiert Microsoft keine eigenen Schritte. Die folgenden Konfigurationen folgen der [Claude-Code-Doku](https://code.claude.com/docs/en/mcp) und den Microsoft-Angaben zu Transport und Anmeldung. Sie sind ungetestet.

### Claude Code: lokaler Authoring-Server (Windows)

```bash
claude mcp add --scope project powerbi-authoring-local -- \
  npx -y @microsoft/powerbi-modeling-mcp@1.0.0 --start
```

Unter Windows kann es nötig sein, `npx` über `cmd /c` zu starten. Das hängt von Ihrer Node-Installation ab.

### Claude Code: Fabric IQ oder gehosteter Authoring-Server

Weil Entra ID keine Dynamic Client Registration kann, braucht Claude Code eine eigene App-Registrierung. Microsoft beschreibt das für Fabric IQ:

1. Im Entra Admin Center eine **Single-Tenant**-App anlegen.
2. Als Redirect-URI die Adresse des Clients eintragen. Claude Code nutzt laut eigener Doku `http://localhost:PORT/callback`.
3. Unter **API permissions > Power BI Service > Delegated** die Rechte `Item.Read.All`, `Item.Execute.All` und `Dataset.Read.All` hinzufügen.
4. Client-ID notieren.

Dann in Claude Code (Client-ID ist ein Platzhalter):

```bash
claude mcp add --transport http \
  --client-id 00000000-0000-0000-0000-000000000000 \
  --callback-port 8080 \
  fabriciq https://fabriciq.svc.cloud.microsoft/v1/mcp/fabriciq
```

Ob die App als öffentlicher Client ohne Secret reicht, hängt von Ihren Entra-Einstellungen ab. Laut Claude-Code-Doku lassen Sie `--client-secret` bei öffentlichen Clients weg.

### Claude Desktop

Lokale stdio-Server tragen Sie in `claude_desktop_config.json` ein (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`). Da der lokale Power-BI-Server nicht auf macOS läuft, funktioniert das nur unter Windows:

```json
{
  "mcpServers": {
    "powerbi-authoring-local": {
      "command": "npx",
      "args": ["-y", "@microsoft/powerbi-modeling-mcp@1.0.0", "--start", "--readonly"]
    }
  }
}
```

Remote-Server bindet Claude Desktop über die Connector-Einstellungen ein. Wie das mit einer eigenen Entra-App zusammenspielt, ist aus einer Primärquelle von Anthropic nicht geprüft. Mehr zu Clients steht in [MCP-Clients einrichten](./mcp-clients-einrichten.md).

## Beispiel 1: DAX-Measure anlegen

Ziel: ein Measure für den Umsatz im Vorjahr in einem Modell mit Faktentabelle `Umsatz` und Datumstabelle `Datum`. Server: Authoring, lokal oder gehostet.

1. Verbinden. Prompt aus der Microsoft-Doku, angepasst:

   ```text
   Connect to semantic model 'Vertrieb DACH' in Fabric workspace 'Controlling Muster GmbH'
   ```

2. Erst lesend prüfen:

   ```text
   Liste alle Tabellen und Measures in diesem Modell auf.
   ```

3. Dann die Änderung:

   ```text
   Lege in der Tabelle 'Umsatz' ein Measure 'Umsatz VJ' an, das den Umsatz
   des gleichen Zeitraums im Vorjahr zeigt. Nutze die Datumstabelle 'Datum'.
   Format: Währung EUR, Ordner 'Zeitvergleich'. Füge eine deutsche Beschreibung hinzu.
   ```

Der Agent ruft dazu `measure_operations` auf. Eine plausible DAX-Formel wäre:

```dax
Umsatz VJ =
CALCULATE (
    [Umsatz],
    SAMEPERIODLASTYEAR ( 'Datum'[Datum] )
)
```

Diese Formel ist ein Beispiel und wurde nicht gegen ein Modell ausgeführt. Prüfen Sie die Ausgabe des Agenten, bevor Sie sie übernehmen. Im lokalen Modus fragt der Server vor der ersten Änderung je Datenbank nach.

Wenn Sie mit PBIP-Dateien im Git arbeiten, sehen Sie die Änderung danach als Diff in der TMDL-Datei der Tabelle. Microsoft empfiehlt genau diesen Weg, weil Sie dann vor dem Commit prüfen und zurückrollen können.

## Beispiel 2: Daten abfragen

Ziel: Umsatz nach Region im letzten Quartal. Server: Fabric IQ.

```text
Nutze den Bericht 'Vertrieb DACH' und zeige den Gesamtumsatz
nach Region für das letzte abgeschlossene Quartal.
```

Laut Microsoft ruft der Client typischerweise nacheinander `DiscoverArtifacts`, `GetReportMetadata`, `GetSemanticModelSchema`, gegebenenfalls `ValueSearch` und dann `ExecuteQuery` auf. Die DAX-Abfrage könnte so aussehen:

```dax
EVALUATE
SUMMARIZECOLUMNS (
    'Region'[Region],
    TREATAS ( { "2026-Q3" }, 'Datum'[Quartal] ),
    "Umsatz", [Umsatz]
)
ORDER BY [Umsatz] DESC
```

Auch diese Abfrage ist ein ungetestetes Beispiel. Spalten- und Measure-Namen hängen von Ihrem Modell ab. Für Antworten aus mehreren Modellen braucht der Agent mehrere `ExecuteQuery`-Aufrufe, weil jeder Aufruf genau ein Modell abfragt.

## Risiken und wie Sie sie begrenzen

### Schreibzugriff auf Modelle

Microsoft schreibt, Änderungen des Agenten können "irreversible" sein. Gegenmaßnahmen laut Doku und README:

- Vor dem Start ein Backup des Modells anlegen.
- Mit PBIP-Dateien unter Git arbeiten, damit jede Änderung als Diff sichtbar ist.
- Für reine Analysen den lokalen Server mit `--readonly` starten oder gleich Fabric IQ nutzen.
- Rollen nach dem Prinzip der minimalen Rechte vergeben. Ein falsch konfigurierter Client handelt mit den vollen Fabric-Rechten des Benutzers.
- Bei Service Principals beachten: Power BI erzwingt dann keine Row-Level Security. Der Principal sieht alle Daten, auf die er Zugriff hat.

### Datenabfluss an das Sprachmodell

Der wichtigste Satz aus der Microsoft-Doku: "An MCP server doesn't expand data access, but it does move data." Metadaten, Schemas und Abfrageergebnisse gehen an den MCP-Client und von dort an den Anbieter des Sprachmodells.

Für Unternehmen in Deutschland heißt das:

- Prüfen Sie, wo der Modellanbieter Ihres Clients die Daten verarbeitet und ob ein AV-Vertrag besteht.
- Personenbezogene Daten (zum Beispiel Umsatz je Vertriebsmitarbeiter) sind besonders heikel.
- Nutzen Sie aggregierte Abfragen statt Zeilenexporte. Das Authoring-Tool hat eine harte Grenze von 100.000 Zeilen, Fabric IQ liefert ohne Angabe 250 Zeilen.
- Teilen Sie Chatverläufe mit Modelldaten nicht unbedacht. Das README warnt ausdrücklich davor.

Mehr dazu in [MCP und DSGVO](./mcp-dsgvo.md) und [MCP-Sicherheit](./mcp-sicherheit.md).

### Weitere Hosts

Der lokale Server darf sich nur mit Power-BI-Endpunkten verbinden. Für Azure Analysis Services oder SQL Server Analysis Services müssen Sie Hosts in `PBI_MODELING_MCP_ALLOWED_CONNECTION_HOSTS` freigeben. Laut README werden an diese Hosts Zugriffstokens gesendet. Tragen Sie also nur Server ein, deren Betreiber Sie kennen.

## Community-Server

Neben den Microsoft-Servern gibt es Community-Projekte (gh api, 19.10.2026):

| Repository | Beschreibung laut README | Lizenz | Sterne | Letzter Push |
| --- | --- | --- | --- | --- |
| [HorizunGroup/horizun-pbi-mcp](https://github.com/HorizunGroup/horizun-pbi-mcp) | Desktop-Modelle und PBIP-Berichte bauen, prüfen, reparieren | Apache-2.0 | 30 | 17.10.2026 |
| [ArieDavista/PowerBI-MCP-Privacy-Proxy](https://github.com/ArieDavista/PowerBI-MCP-Privacy-Proxy) | Windows-Proxy zwischen Claude Desktop und Power BI | eigene Lizenz | 12 | 20.12.2025 |

Diese Server wurden nicht getestet. Für die meisten Aufgaben decken die Microsoft-Server den Bedarf, die Community-Projekte setzen eigene Schwerpunkte, etwa bei Berichtsdateien (PBIR) oder beim Datenschutz.

## Häufige Fragen

### Gibt es einen offiziellen Power BI MCP Server?

Ja. Microsoft bietet den Power BI Authoring MCP Server (lokal GA, gehostet Preview) zum Bearbeiten semantischer Modelle und Fabric IQ (GA) zum Abfragen. Der ältere Consumption-Server ist weiter in Preview.

### Kann ich den Power BI MCP Server mit Claude nutzen?

Ja. Den lokalen Authoring-Server binden Sie unter Windows als stdio-Server in Claude Desktop oder Claude Code ein. Für Fabric IQ und den gehosteten Server brauchen Sie eine eigene Entra-App, weil Entra keine Dynamic Client Registration unterstützt.

### Funktioniert der Power BI MCP Server mit Copilot?

Ja. Microsoft dokumentiert GitHub Copilot in VS Code und die GitHub Copilot CLI. Fabric IQ ist laut Microsoft außerdem der vorgesehene Weg für Microsoft 365 Copilot, Copilot Studio und Microsoft Foundry.

### Brauche ich Power BI Premium für MCP?

Für Power BI Desktop und PBIP-Dateien mit dem lokalen Server nicht. Für Modelle im Fabric-Workspace braucht der lokale Server den XMLA-Endpunkt mit Read Write, den es auf Premium, PPU, Embedded und Fabric-Kapazität gibt. Fabric IQ braucht laut Microsoft keine Fabric- oder Premium-Kapazität für die Inhalte.

### Läuft der Power BI MCP Server auf dem Mac?

Der lokale Server nicht. Microsoft schreibt: "The local server doesn't support macOS." Am Mac nutzen Sie den gehosteten Authoring-Server oder Fabric IQ.

## Weiterlesen

- [Übersicht: MCP-Server für deutsche Geschäftssysteme](../../README.md)
- [MCP-Server-Liste](../liste.md)
- [Was ist ein MCP Server?](./was-ist-ein-mcp-server.md)
- [MCP vs. API: der Unterschied](./mcp-vs-api.md)
- [MCP Server erstellen](./mcp-server-erstellen.md)
- [MCP-Clients einrichten](./mcp-clients-einrichten.md)
- [MCP-Sicherheit](./mcp-sicherheit.md)
- [MCP und DSGVO](./mcp-dsgvo.md)
- [Anleitung zum DATEV-Format (EXTF)](./datev-mcp-server.md)
- [SAP MCP Server](./sap-mcp-server.md)
- [HubSpot MCP](./hubspot-mcp.md)
- [Postgres MCP](./postgres-mcp.md)
- [MCP für Buchhaltung](./buchhaltung-mcp.md)
- [Business Central MCP](./business-central-mcp.md)

> **Hinweis:** Technische Informationen nach Stand 19.10.2026, ohne Gewähr für Vollständigkeit
> und Richtigkeit. Keine Rechts- oder Steuerberatung; die Autoren sind keine Rechtsanwälte,
> Steuerberater oder Datenschutzbeauftragten. Produktnamen sind Marken ihrer Inhaber; es besteht
> keine Verbindung zu den genannten Herstellern.
