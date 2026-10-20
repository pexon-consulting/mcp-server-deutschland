# HubSpot MCP Server: Remote-MCP, Developer-MCP und Einrichtung in Claude

Diese Anleitung ist für Marketing- und Vertriebsteams, CRM-Admins und Entwickler, die HubSpot per Model Context Protocol (MCP) an Claude, Cursor, VS Code oder eigene Agenten anbinden wollen. Sie erklärt die zwei offiziellen HubSpot MCP Server, die Einrichtung je Client und was Sie beim Datenschutz beachten sollten.

Stand: 19.10.2026

## Inhaltsverzeichnis

- [Das Wichtigste in Kürze](#das-wichtigste-in-kürze)
- [Zwei offizielle Server: Remote und Developer](#zwei-offizielle-server-remote-und-developer)
- [Der Remote-MCP-Server: Daten, Tools, Schreibrechte](#der-remote-mcp-server-daten-tools-schreibrechte)
- [MCP Connector in HubSpot anlegen](#mcp-connector-in-hubspot-anlegen)
- [OAuth mit PKCE: was der Client können muss](#oauth-mit-pkce-was-der-client-können-muss)
- [HubSpot MCP in Claude einrichten](#hubspot-mcp-in-claude-einrichten)
- [Cursor, VS Code und MCP Inspector](#cursor-vs-code-und-mcp-inspector)
- [Der Developer-MCP-Server (CLI)](#der-developer-mcp-server-cli)
- [HubSpot MCP Server auf GitHub](#hubspot-mcp-server-auf-github)
- [Datenschutz und Rechte](#datenschutz-und-rechte)
- [Beispiele](#beispiele)
- [Häufige Fragen](#häufige-fragen)
- [Weiterlesen](#weiterlesen)

## Das Wichtigste in Kürze

- HubSpot betreibt zwei MCP Server: den **Remote-MCP-Server** unter `https://mcp.hubspot.com` für CRM-Daten und den lokalen **Developer-MCP-Server** über die HubSpot CLI für App- und CMS-Entwicklung.
- Offizieller Zugriff auf CRM-Daten geht **nur remote**. Eine lokale Variante für CRM-Daten bietet HubSpot nicht an.
- Der Remote-Server braucht OAuth mit **PKCE (S256)**. Dynamic Client Registration bietet er nicht an. Sie legen deshalb in HubSpot einen **MCP Connector** an und tragen Client-ID und Client-Secret im Client ein.
- Der Server kann lesen und schreiben. Schreibende Tools zeigen laut HubSpot vorher eine Zusammenfassung der geplanten Änderungen und verlangen eine ausdrückliche Bestätigung.
- CRM-Daten sind fast immer personenbezogen. Prüfen Sie AV-Vertrag, Rechte der Benutzer und den Anbieter des Sprachmodells.

## Zwei offizielle Server: Remote und Developer

Laut [developers.hubspot.com/mcp](https://developers.hubspot.com/mcp) (abgerufen 19.10.2026) gibt es zwei getrennte Server:

| | Remote-MCP-Server | Developer-MCP-Server |
| --- | --- | --- |
| Zweck | CRM-Daten lesen und schreiben | Apps und CMS-Inhalte auf der Developer Platform bauen |
| Betrieb | gehostet von HubSpot | lokal über die HubSpot CLI |
| Adresse | `https://mcp.hubspot.com` | stdio, Servername `HubSpotDev` |
| Anmeldung | OAuth mit PKCE über einen MCP Connector | Anmeldung der CLI (`hs auth`, Personal Access Key) |
| Einrichtung | Client-Konfiguration | `hs mcp setup` |

Beide setzen laut HubSpot die aktuelle Version der Developer Platform voraus. Die Landingpage enthält noch einen älteren Absatz ("supports OAuth 2.0. Later in 2025, we will align with ... OAuth 2.1") und beschreibt eine "user-level app". Die technische Doku spricht inzwischen vom MCP Connector und verlangt PKCE. Wir folgen hier der technischen Doku.

In Suchanfragen taucht auch der Begriff "HubSpot MCP auth apps" auf. In der aktuellen Doku heißt das Objekt "MCP connector". Ob "MCP Auth App" eine frühere Bezeichnung war, ist hier ungeprüft.

## Der Remote-MCP-Server: Daten, Tools, Schreibrechte

Die Angaben stammen aus der Doku [Integrate AI tools with the HubSpot MCP server](https://developers.hubspot.com/docs/apps/developer-platform/build-apps/integrate-with-the-remote-hubspot-mcp-server) (abgerufen 19.10.2026).

### Lesezugriff

- CRM-Objekte: Kontakte, Unternehmen, Deals, Tickets, Leads, Benutzer, Termine, Kurse, Listings, Projekte, Services, Custom Objects und Segmente. Umsatzobjekte wie Angebote, Rechnungen und Bestellungen sind als BETA gekennzeichnet.
- Aktivitäten: Anrufe, E-Mails, Meetings, Notizen, Aufgaben.
- Inhalte: Blogposts, Landingpages, Website-Seiten, Kampagnen, Marketing-Events, dazu Content-Analysen.
- Konversationen aus Live-Chat, Team-E-Mail, WhatsApp, SMS und weiteren Kanälen.
- Marketing-E-Mails mit Versandstatistik und Daten je Kontakt.
- AEO-Kennzahlen, nur mit Marketing Hub Professional oder Enterprise.

### Schreibzugriff

- CRM-Datensätze anlegen und ändern, Aktivitäten anlegen.
- Landingpages, Website-Seiten und Blogposts anlegen, bearbeiten und veröffentlichen.
- Kampagnen, E-Mail-Entwürfe, Pipelines, eigene Eigenschaften und statische Segmente.
- Angebote (BETA), nur mit Revenue Hub Professional oder Enterprise und dem optionalen Scope `manage revenue objects`.

Löschen steht in der Liste der Schreibrechte nicht.

### Wichtige Tools

| Tool | Zweck |
| --- | --- |
| `get_user_details` | eigener Benutzer, Konto, Lese- und Schreibrechte je Objekt |
| `search_crm_objects` | CRM-Suche mit bis zu fünf Filtergruppen à sechs Filter, max. 200 Treffer je Seite |
| `get_crm_objects` | bis zu 100 Objekte per ID |
| `manage_crm_objects` | anlegen oder ändern, mit Änderungsvorschau und Bestätigung |
| `query_crm_data` | SQL-artige Abfragen mit Aggregation, ohne Joins und Unterabfragen |
| `search_properties`, `get_properties` | Eigenschaften finden und beschreiben |
| `search_owners` | Besitzer per Name oder E-Mail |
| `manage_custom_pipelines` | Pipelines anlegen und ändern |
| `tool_guidance` | Hinweise zur Nutzung anderer Tools |

HubSpot empfiehlt, nach dem Verbinden zuerst `get_user_details` aufzurufen. Welche Tools Sie sehen, hängt von Abo, Benutzerrechten und Kontoeinstellungen ab.

### Sensitive Data

Ist in Ihrem Konto "Sensitive Data" eingeschaltet, sperrt der MCP Server Aktivitäten (Anrufe, E-Mails, Meetings, Notizen, Aufgaben) und Konversationen. Diese Sperre gilt laut HubSpot nur für den MCP Server, nicht für die normalen CRM-APIs.

## MCP Connector in HubSpot anlegen

1. In der Hauptnavigation von HubSpot **Development** öffnen.
2. Links **MCP Connectors** wählen.
3. Oben rechts **Create MCP connector** klicken.
4. Name, optional Beschreibung, **Redirect URL** und Symbol eintragen.
5. **Create** klicken. Auf der Detailseite stehen danach Client-ID, Client-Secret und Redirect-URLs.

Bei mehreren Redirect-URLs nimmt HubSpot die erste als Standard. Für den MCP Inspector nennt HubSpot `http://localhost:6274/oauth/callback/debug`.

Scopes legen Sie im Connector nicht selbst fest. Sie ergeben sich aus den Tools des Servers zum Zeitpunkt der Installation und aus dem, was der Benutzer bei der Anmeldung freigibt. Ändert HubSpot die Tools, müssen Benutzer den Connector neu installieren, um neue Scopes zu erteilen.

Laut Landingpage muss sich der Admin des HubSpot-Kontos zuerst verbinden, bevor andere Benutzer den Connector nutzen können.

## OAuth mit PKCE: was der Client können muss

Am 19.10.2026 liefert `https://mcp.hubspot.com/.well-known/oauth-protected-resource` diese Protected Resource Metadata:

```json
{
  "resource": "https://mcp.hubspot.com",
  "authorization_servers": ["https://mcp.hubspot.com"],
  "scopes_supported": [],
  "resource_documentation": "https://developers.hubspot.com/mcp"
}
```

Die Metadaten des Autorisierungsservers (`/.well-known/oauth-authorization-server`) nennen `code_challenge_methods_supported: ["S256"]` und `token_endpoint_auth_methods_supported: ["client_secret_post"]`. Einen `registration_endpoint` gibt es dort nicht. Clients, die sich automatisch per Dynamic Client Registration anmelden wollen, scheitern deshalb. Sie brauchen Client-ID und Client-Secret aus dem Connector.

Wer einen eigenen Client baut, muss laut HubSpot:

- einen zufälligen `code_verifier` mit 43-128 Zeichen erzeugen,
- daraus die `code_challenge` mit S256 ableiten,
- `code_challenge` und `code_challenge_method=S256` in der Autorisierungsanfrage senden,
- den `code_verifier` beim Token-Tausch mitschicken,
- das `refresh_token` nutzen, wenn das Access Token abläuft.

## HubSpot MCP in Claude einrichten

### Claude, ChatGPT, Copilot, Gemini: fertige Connectoren

HubSpot schreibt in der Doku [Using the HubSpot MCP server](https://developers.hubspot.com/docs/build-with-ai/remote-mcp-server): Für Claude, ChatGPT, Microsoft Copilot und Gemini gibt es eigene AI-Connectoren von HubSpot, die auf diesem Remote-Server laufen. Wenn Sie nur mit Ihren Daten arbeiten wollen, ist das der einfachste Weg. Der eigene MCP Connector ist für Teams gedacht, die HubSpot in einen selbst gebauten Agenten oder einen anderen Client einbinden.

Laut HubSpot können Admins von Claude Enterprise den Connector auf firmeneigene Konten beschränken (verified domain restrictions).

### Claude Code mit eigenem Connector

1. Im Connector als Redirect-URL `http://localhost:3118/callback` eintragen. Der Port ist frei wählbar, muss aber zum nächsten Schritt passen.
2. Server hinzufügen. Client-ID ist ein Platzhalter. `--client-secret` fragt das Secret verdeckt ab:

```bash
claude mcp add --scope project --transport http \
  --client-id 00000000-0000-0000-0000-000000000000 \
  --client-secret --callback-port 3118 \
  hubspot https://mcp.hubspot.com
```

3. In Claude Code `/mcp` aufrufen und im Browser bei HubSpot anmelden.

Ohne `--client-secret` haben wir den Befehl mit Claude Code 2.1.303 ausgeführt. Er erzeugt diese `.mcp.json`:

```json
{
  "mcpServers": {
    "hubspot": {
      "type": "http",
      "url": "https://mcp.hubspot.com",
      "oauth": {
        "clientId": "00000000-0000-0000-0000-000000000000",
        "callbackPort": 3118
      }
    }
  }
}
```

Das Secret landet laut Claude-Code-Doku im Schlüsselbund (macOS) oder einer Credentials-Datei, nicht in der `.mcp.json`. Die Anmeldung bei HubSpot selbst ist ungetestet, weil kein HubSpot-Konto für Tests zur Verfügung stand.

HubSpot bietet zusätzlich [HubSpot/hubspot-mcp-plugins](https://github.com/HubSpot/hubspot-mcp-plugins) an (Apache-2.0, letzter Push 12.10.2026). Das sind Claude-Code-Plugins ("HubSpot Sales", "HubSpot Partner"), die laut README auf dem Remote-Server aufbauen. Installation laut README:

```text
/install-plugin https://github.com/HubSpot/hubspot-mcp-plugins
```

### Claude Desktop

Für Claude Desktop nutzen Sie den HubSpot-Connector aus den Connector-Einstellungen von Claude. Eine eigene Konfiguration mit Client-ID und Secret in `claude_desktop_config.json` ist in der Doku von Anthropic nur für lokale stdio-Server beschrieben. Den Weg über einen eigenen Connector in Claude Desktop haben wir nicht geprüft.

## Cursor, VS Code und MCP Inspector

Die folgenden Konfigurationen folgen der Doku der jeweiligen Clients und sind ungetestet. Mehr Details in [MCP-Clients einrichten](./mcp-clients-einrichten.md).

### Cursor

Datei `.cursor/mcp.json` im Projekt oder `~/.cursor/mcp.json`. Cursor kennt laut eigener Doku einen `auth`-Block mit Client-ID, Secret und Scopes. Das Secret ziehen Sie aus einer Umgebungsvariable:

```json
{
  "mcpServers": {
    "hubspot": {
      "url": "https://mcp.hubspot.com",
      "auth": {
        "CLIENT_ID": "00000000-0000-0000-0000-000000000000",
        "CLIENT_SECRET": "${env:HUBSPOT_MCP_CLIENT_SECRET}"
      }
    }
  }
}
```

Welche Redirect-URL Cursor verwendet, steht in der Cursor-Doku. Tragen Sie genau diese im HubSpot-Connector ein.

### VS Code mit GitHub Copilot

Datei `.vscode/mcp.json`, Schlüssel `servers`. VS Code kennt einen `oauth`-Block mit `clientId`:

```json
{
  "servers": {
    "hubspot": {
      "type": "http",
      "url": "https://mcp.hubspot.com",
      "oauth": {
        "clientId": "00000000-0000-0000-0000-000000000000"
      }
    }
  }
}
```

Wie VS Code das Client-Secret abfragt, das HubSpot verlangt (`client_secret_post`), ist hier ungeprüft.

### MCP Inspector

HubSpot nennt den MCP Inspector als schnellsten Test: Transport Streamable HTTP, URL `https://mcp.hubspot.com/`, Client-ID und Secret eintragen, OAuth-Ablauf starten, dann `get_user_details` ausführen. Der Inspector ist ein Community-Werkzeug. Seine Oberfläche ändert sich laut HubSpot gelegentlich.

## Der Developer-MCP-Server (CLI)

Der Developer-MCP-Server hilft beim Bauen von HubSpot-Apps und CMS-Inhalten. Er greift nicht auf CRM-Daten zu. Laut [Setup-Doku](https://developers.hubspot.com/docs/developer-tooling/local-development/developer-mcp/setup) (abgerufen 19.10.2026):

- HubSpot CLI ab Version 8.2.0. Aktuell auf npm: `@hubspot/cli` 8.16.0 (19.10.2026).
- Unterstützte Clients: Claude Code, Codex CLI, Cursor, Gemini CLI, VS Code, Windsurf.

Einrichtung (ungetestet, weil dafür ein HubSpot-Konto nötig ist):

```bash
hs --version
hs mcp setup
```

Der Befehl fragt, für welche Clients der Server eingetragen werden soll, und ob Sie den **Standalone-Modus** wollen. Dann nutzt der Server `npx @hubspot/cli` statt einer global installierten CLI. Das ist laut HubSpot für Firmenrechner gedacht, auf denen globale npm-Installationen gesperrt sind. Optional können Sie eine CLI-Version festlegen.

Danach erscheint der Server als `HubSpotDev`. Die Tools reichen von `search-docs` und `fetch-doc` (Entwicklerdoku) über Projekt-Werkzeuge (Projekt anlegen, Features hinzufügen, Build-Status) bis zu CMS-Werkzeugen wie Modulen, Templates und Serverless Functions.

Das ältere npm-Paket `@hubspot/mcp-server` ("MCP Server for developers building HubSpot Apps") hat als letzte Version 0.4.0 vom 18.06.2025. Für neue Einrichtungen beschreibt HubSpot den Weg über `hs mcp setup`.

## HubSpot MCP Server auf GitHub

Offizielle und Community-Repositories (gh api, 19.10.2026):

| Repository | Art | Lizenz | Sterne | Letzter Push |
| --- | --- | --- | --- | --- |
| [HubSpot/hubspot-mcp-plugins](https://github.com/HubSpot/hubspot-mcp-plugins) | offiziell, Claude-Code-Plugins | Apache-2.0 | 4 | 12.10.2026 |
| [HubSpot/mcp-server](https://github.com/HubSpot/mcp-server) | offiziell, ohne Lizenzangabe | keine | 6 | 25.04.2025 |
| [shinzo-labs/hubspot-mcp](https://github.com/shinzo-labs/hubspot-mcp) | Community, lokal, Access Token | MIT | 35 | 25.11.2025 |
| [lkm1developer/hubspot-mcp-server](https://github.com/lkm1developer/hubspot-mcp-server) | Community | MIT | 13 | 01.04.2025 |
| [promptmetrics/hubspot-mcp](https://github.com/promptmetrics/hubspot-mcp) | Community, 76 Tools, Freigabe vor Schreibzugriffen, Undo | MIT (Ordner `skills/` unter Apache-2.0) | 3 | 03.10.2026 |

Community-Server laufen meist lokal und nutzen ein Access Token einer Private App oder einer eigenen OAuth-App. Beispiel aus dem README von shinzo-labs (ungetestet):

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "npx",
      "args": ["@shinzolabs/hubspot-mcp"],
      "env": {
        "HUBSPOT_ACCESS_TOKEN": "${HUBSPOT_ACCESS_TOKEN}"
      }
    }
  }
}
```

Ob Ihr Client `${...}` in `env` auflöst, hängt vom Client ab. Ein Token mit breiten Scopes in einer Konfigurationsdatei ist ein Risiko. Der offizielle Remote-Server arbeitet stattdessen mit den Rechten des angemeldeten Benutzers.

## Datenschutz und Rechte

CRM-Daten sind fast immer personenbezogen: Namen, E-Mail-Adressen, Telefonnummern, Gesprächsnotizen. Wer HubSpot an einen KI-Assistenten hängt, gibt diese Daten an den Anbieter des Sprachmodells weiter. Diese Punkte sollten Sie klären, bevor Sie loslegen:

- **AV-Vertrag mit HubSpot.** HubSpot veröffentlicht ein [Data Processing Agreement](https://legal.hubspot.com/de/dpa). Prüfen Sie, ob es für Ihr Konto gilt.
- **AV-Vertrag mit dem KI-Anbieter.** Der MCP Server schickt die Daten an Ihren Client, der Client an das Modell. Für diesen zweiten Weg brauchen Sie eine eigene Rechtsgrundlage und einen eigenen Vertrag.
- **Rolle mit minimalen Rechten.** Alle Aktionen laufen laut HubSpot mit den Rechten des angemeldeten Benutzers. Ein Benutzer mit Super-Admin-Rechten gibt dem Agenten also alles. Nutzen Sie für Agenten eine eingeschränkte Rolle, zum Beispiel nur Lesen auf Kontakten und Deals.
- **Schreibrechte begrenzen.** Bei der Anmeldung können Sie Berechtigungen abwählen. Bestätigen Sie Änderungsvorschläge nur, wenn Sie sie gelesen haben.
- **Sensitive Data nutzen.** Wenn Sie Gesprächsnotizen und Konversationen gar nicht freigeben wollen, sperrt die Einstellung "Sensitive Data" sie für den MCP Server.
- **Löschkonzept beachten.** Was einmal im Chatverlauf steht, liegt beim KI-Anbieter. Klären Sie Aufbewahrungsfristen.

Mehr dazu in [MCP und DSGVO](./mcp-dsgvo.md) und [MCP-Sicherheit](./mcp-sicherheit.md).

## Beispiele

Die folgenden Prompts sind Beispiele. Wir konnten sie mangels HubSpot-Testkonto nicht ausführen. Die Tool-Namen stammen aus der HubSpot-Doku.

### Kontakte suchen

```text
Finde alle Kontakte der Muster GmbH mit Lifecycle-Phase "Opportunity",
deren letzte Aktivität älter als 30 Tage ist. Zeige Name, E-Mail und Besitzer.
```

Ein Agent würde typischerweise so vorgehen:

1. `get_user_details`: Darf ich Kontakte lesen?
2. `search_properties`: Wie heißen die Eigenschaften für Lifecycle-Phase und letzte Aktivität?
3. `search_crm_objects` mit einer Filtergruppe (Unternehmen, Phase, Datum).
4. `search_owners`, um Besitzer-IDs in Namen zu übersetzen.

Ein Tool-Aufruf könnte etwa so aussehen. Die Struktur folgt der CRM-Search-API, auf der der Server laut HubSpot aufbaut. Das genaue Eingabeschema liefert `tools/list`:

```json
{
  "objectType": "contacts",
  "filterGroups": [
    {
      "filters": [
        { "propertyName": "company", "operator": "EQ", "value": "Muster GmbH" },
        { "propertyName": "lifecyclestage", "operator": "EQ", "value": "opportunity" },
        { "propertyName": "notes_last_updated", "operator": "LT", "value": "2026-09-19" }
      ]
    }
  ],
  "properties": ["firstname", "lastname", "email", "hubspot_owner_id"],
  "limit": 50
}
```

### Deal-Pipeline zusammenfassen

```text
Fasse meine Deal-Pipeline "Neukunden" zusammen: Anzahl und Summe je Phase,
die fünf größten offenen Deals und alle Deals ohne Aktivität seit 14 Tagen.
```

Hier passt `query_crm_data`, weil es Aggregation kann. HubSpot rät, vorher `tool_guidance` aufzurufen und Eigenschaftsnamen mit `search_properties` zu prüfen. Eine Abfrage könnte sinngemäß so aussehen:

```sql
SELECT dealstage, COUNT(*), SUM(amount)
FROM deals
WHERE pipeline = 'neukunden'
GROUP BY dealstage
```

Ob diese Syntax genau so funktioniert, ist ungetestet. Laut Doku unterstützt das Tool keine Joins, keine Spalten-Aliase, keine Unterabfragen und keine Währungsumrechnung. Deshalb steht oben kein `AS`.

### Notizen aus einem Meeting übernehmen

```text
Ich hatte heute ein Gespräch mit Erika Mustermann (Muster GmbH).
Lege eine Notiz an: Budget für Q1 2027 freigegeben, Angebot bis 30.10. schicken.
Setze den Deal "Muster GmbH Rollout" auf die Phase "Angebot".
```

`manage_crm_objects` zeigt vor dem Schreiben eine Vorschau. Erst nach Ihrer Bestätigung legt der Server Notiz und Phasenwechsel an. Bei Pipelines mit Pflichtfeldern je Phase prüft der Server laut HubSpot die Regeln der Pipeline.

## Häufige Fragen

### Gibt es einen offiziellen HubSpot MCP Server?

Ja, zwei. Der Remote-MCP-Server unter `https://mcp.hubspot.com` greift auf CRM-Daten zu. Der Developer-MCP-Server läuft lokal über die HubSpot CLI und hilft beim Bauen von Apps und CMS-Inhalten.

### Wie verbinde ich HubSpot MCP mit Claude?

Am einfachsten über den HubSpot-Connector in Claude. Für Claude Code oder eigene Agenten legen Sie in HubSpot unter Development > MCP Connectors einen Connector an und tragen Client-ID, Secret und Callback-Port mit `claude mcp add` ein.

### Wie lautet die HubSpot MCP Server URL?

`https://mcp.hubspot.com`. Der Transport ist Streamable HTTP. Für die Anmeldung braucht der Client OAuth mit PKCE.

### Gibt es den HubSpot MCP Server auf GitHub?

HubSpot hat das Repository `HubSpot/mcp-server` (letzter Push April 2025, ohne Lizenz) und `HubSpot/hubspot-mcp-plugins` mit Claude-Code-Plugins. Der Remote-Server selbst ist nicht als Quellcode veröffentlicht. Dazu kommen Community-Server wie `shinzo-labs/hubspot-mcp`.

### Kann der HubSpot MCP Server Daten löschen?

In der Liste der Schreibrechte nennt HubSpot Anlegen und Ändern, aber kein Löschen von CRM-Datensätzen. Jede Änderung braucht eine Bestätigung des Benutzers.

### Was kostet der HubSpot MCP Server?

In der Doku nennt HubSpot keinen eigenen Preis. Einige Funktionen setzen bestimmte Abos voraus, etwa AEO (Marketing Hub Professional oder Enterprise) und Angebote (Revenue Hub Professional oder Enterprise).

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
- [Power BI MCP](./power-bi-mcp.md)
- [Postgres MCP](./postgres-mcp.md)
- [MCP für Buchhaltung](./buchhaltung-mcp.md)
- [Business Central MCP](./business-central-mcp.md)

> **Hinweis:** Technische Informationen nach Stand 19.10.2026, ohne Gewähr für Vollständigkeit
> und Richtigkeit. Keine Rechts- oder Steuerberatung; die Autoren sind keine Rechtsanwälte,
> Steuerberater oder Datenschutzbeauftragten. Produktnamen sind Marken ihrer Inhaber; es besteht
> keine Verbindung zu den genannten Herstellern.
