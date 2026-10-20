# Business Central MCP: Dynamics 365 Business Central MCP Server einrichten

Diese Anleitung ist für Business-Central-Admins, Partner und Entwickler, die Dynamics 365 Business Central per Model Context Protocol (MCP) an Copilot Studio, VS Code, Claude Code oder andere Clients anbinden wollen. Sie erklärt den offiziellen Business Central MCP Server, die Konfiguration in Business Central, die Dataverse- und Dynamics-365-MCP-Server und deutsche Besonderheiten.

Stand: 19.10.2026

## Inhaltsverzeichnis

- [Das Wichtigste in Kürze](#das-wichtigste-in-kürze)
- [Welche Dynamics MCP Server gibt es?](#welche-dynamics-mcp-server-gibt-es)
- [Der Business Central MCP Server](#der-business-central-mcp-server)
- [Konfiguration in Business Central](#konfiguration-in-business-central)
- [Header: Mandant, Umgebung, Unternehmen](#header-mandant-umgebung-unternehmen)
- [Copilot Studio und VS Code](#copilot-studio-und-vs-code)
- [Externe Clients: Entra-App, Claude Code, Copilot CLI](#externe-clients-entra-app-claude-code-copilot-cli)
- [Dataverse MCP Server](#dataverse-mcp-server)
- [Dynamics 365 Finance und Supply Chain](#dynamics-365-finance-und-supply-chain)
- [Community-Server](#community-server)
- [Beispiele](#beispiele)
- [Deutsche Besonderheiten](#deutsche-besonderheiten)
- [Risiken und Empfehlungen](#risiken-und-empfehlungen)
- [Häufige Fragen](#häufige-fragen)
- [Weiterlesen](#weiterlesen)

## Das Wichtigste in Kürze

- Microsoft betreibt einen offiziellen Business Central MCP Server unter `https://mcp.businesscentral.dynamics.com`. Er gilt laut Microsoft Learn für **Business Central online**. Transport ist nur Streamable HTTP.
- Was der Server darf, legen Sie in Business Central auf der Seite **Model Context Protocol (MCP) Server Configurations** fest: welche API-Seiten als Tools erscheinen und ob Lesen, Anlegen, Ändern, Löschen oder Aktionen erlaubt sind.
- Copilot Studio und VS Code nutzen eine von Microsoft vorregistrierte App. Für Claude Code, GitHub Copilot CLI und andere Clients brauchen Sie eine eigene Entra-App.
- Die Data Query Tools führt Microsoft als **Preview**.
- Dataverse (Dynamics 365 Sales, Customer Service usw.) und Dynamics 365 Finance und Supply Chain haben eigene MCP Server mit eigenen Regeln und eigener Abrechnung.
- Auf der Learn-Seite zur deutschen Lokalisierung steht kein DATEV-Export. Mehr dazu unter [Deutsche Besonderheiten](#deutsche-besonderheiten).

## Welche Dynamics MCP Server gibt es?

| Server | Für | Adresse | Status laut Microsoft |
| --- | --- | --- | --- |
| Business Central MCP Server | Business Central online | `https://mcp.businesscentral.dynamics.com` | allgemein verfügbar seit 01.04.2026, Data Query Tools Preview |
| Dataverse MCP Server | Dataverse, also Dynamics 365 Sales, Customer Service, Power Apps | `https://{org}.crm.dynamics.com/api/mcp` | allgemein verfügbar, zusätzlich Preview-Endpunkt `/api/mcp_preview` |
| Dynamics 365 ERP MCP Server | Finance, Supply Chain Management und weitere F&O-Apps | über Copilot Studio und eigene Clients | siehe Abschnitt unten |

"Dynamics MCP" meint also je nach Produkt einen anderen Server. Business Central läuft nicht auf Dataverse als Hauptdatenbank und hat deshalb einen eigenen.

## Der Business Central MCP Server

Quellen: Microsoft Learn, Seiten [Business Central MCP server overview](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/ai/mcp-overview), "Configure Business Central MCP server" und "Connect non-Microsoft clients" (abgerufen 19.10.2026).

### Version und Status

Laut Release-Plan für 2026 Release Wave 1 ist der Server seit dem **01.04.2026 allgemein verfügbar**. Microsoft nennt dabei die aktuellen MCP-Spezifikationen und OAuth 2.1, Telemetrie, Purview-Protokollierung von Konfigurationsänderungen und eingebettete Ressourcen. Die Release-Plan-Seite ist seit Oktober 2026 archiviert.

### Anmeldung

Der Server nutzt OAuth 2.0 Authorization Code mit PKCE gegen Microsoft Entra ID. Am 19.10.2026 nennt die Protected Resource Metadata unter `https://mcp.businesscentral.dynamics.com/.well-known/oauth-protected-resource` als Scope `https://api.businesscentral.dynamics.com/Financials.ReadWrite.All`. Für `code_challenge_methods` stehen dort `plain` und `S256`. Nutzen Sie S256.

Alle Aufrufe laufen mit der Identität und den Berechtigungen des angemeldeten Benutzers in Business Central. Der MCP Server gibt also keine Daten heraus, die der Benutzer nicht ohnehin sehen dürfte.

### Tools

Business Central erzeugt Tools aus API-Seiten. Der Name setzt sich aus Aktion, Entität und Seiten-ID zusammen, etwa `List_Customers_PAG30009`. Daneben gibt es je nach Konfiguration:

- **API Tools**: Lesen, Anlegen, Ändern, Löschen und gebundene Aktionen auf den freigegebenen API-Seiten.
- **Dynamic Tool Mode**: statt vieler einzelner Tools nur drei, nämlich `bc_actions_search`, `bc_actions_describe` und `bc_actions_invoke`. Das hilft bei Clients mit Tool-Limit. Copilot Studio erlaubt laut Microsoft höchstens 70 Tools.
- **Data Query Tools (Preview)**: `bc_data_find_tables`, `bc_data_get_table_schema`, `bc_data_get_table_relations` und `bc_data_query` für lesende Abfragen auf Tabellen.

## Konfiguration in Business Central

### Voraussetzungen

- Business Central online.
- Für die Konfiguration den Berechtigungssatz **MCP - Admin**.
- Für Benutzer die üblichen Rechte auf die Daten, die sie per MCP lesen oder ändern sollen.

### Schritte

1. In Business Central nach **Model Context Protocol (MCP) Server Configurations** suchen.
2. Eine neue Konfiguration anlegen, Name und Beschreibung vergeben, zum Beispiel `Vertrieb-Lesen`.
3. Unter **Server Features** wählen, ob API Tools, Dynamic Tool Mode und Data Query Tools aktiv sein sollen.
4. Unter **Available APIs** API-Seiten hinzufügen. **Add All Standard APIs** fügt die Standard-APIs v2.0 hinzu.
5. Je API-Seite die Rechte setzen: **Allow Read**, **Allow Create**, **Allow Modify**, **Allow Delete**, **Allow Bound Actions**.
6. Mit **Validate** prüfen lassen, ob die Konfiguration gültig ist.
7. Die Konfiguration auf **Active** setzen.

Eine aktive Konfiguration lässt sich laut Microsoft nicht mehr bearbeiten. Für Änderungen setzen Sie sie wieder inaktiv. Konfigurationen können Sie als JSON exportieren und in andere Umgebungen importieren. Die Aktion **Connection String** liefert die Werte für die Header.

### Einschränkungen

- ListPart- und CardPart-Seiten werden nicht als Tools unterstützt.
- Die Standardkonfiguration ohne `ConfigurationName` ist laut Microsoft nur lesend und für die Suche nach Tools gedacht.
- Schreibende Tools sind gesperrt, bis Sie den Schalter **Unblock Edit Tools** setzen. Erst dann wirken Allow Create, Allow Modify und Allow Delete.

Welche Konfigurationen es gibt, liefert laut Doku `GET /$configurations` am MCP-Endpunkt. Auf der Seite für Entra-Anwendungen in Business Central sehen Sie, welche Apps zugreifen.

## Header: Mandant, Umgebung, Unternehmen

Der Client wählt Mandant, Umgebung, Unternehmen und Konfiguration über HTTP-Header:

| Header | Bedeutung | Beispiel |
| --- | --- | --- |
| `TenantId` | Entra-Mandant (GUID oder Domain) | `00000000-0000-0000-0000-000000000000` |
| `EnvironmentName` | Umgebung | `Production` oder `Sandbox` |
| `Company` | Unternehmen in Business Central | `Muster GmbH` |
| `ConfigurationName` | MCP-Konfiguration | `Vertrieb-Lesen` |

Werte mit Zeichen außerhalb von ASCII, also auch Umlaute, müssen laut Microsoft Base64-kodiert im Format `=?base64?<Wert>?=` übergeben werden. Für das Unternehmen `Muster GmbH München` (UTF-8) sieht das so aus:

```text
Company: =?base64?TXVzdGVyIEdtYkggTcO8bmNoZW4=?=
```

Den Wert haben wir mit Python erzeugt:

```bash
python3 -c "import base64;print('=?base64?'+base64.b64encode('Muster GmbH München'.encode()).decode()+'?=')"
```

Ohne Header arbeitet der Server im **Headerless-Modus**. Dann stehen Tools wie `list_environments` und `list_companies` bereit, mit denen der Agent Umgebung und Unternehmen erst ermittelt.

Bei GitHub Copilot CLI widersprechen sich zwei Learn-Seiten: Die Übersicht sagt, alle Header seien optional. Die Seite für Nicht-Microsoft-Clients nennt `EnvironmentName` als Pflicht. Setzen Sie `EnvironmentName` im Zweifel.

## Copilot Studio und VS Code

### Copilot Studio

In Copilot Studio fügen Sie den Business Central MCP Server als Tool zu einem Agenten hinzu. Microsoft nutzt dafür eine vorregistrierte App, Sie brauchen keine eigene Entra-App. Copilot Studio braucht laut Doku aktuell alle Header. Microsoft schreibt, der Headerless-Modus komme bald ("soon"). Beachten Sie das Limit von 70 Tools. Bei vielen API-Seiten hilft der Dynamic Tool Mode.

### VS Code mit GitHub Copilot

Auch VS Code nutzt eine vorregistrierte App. Laut Microsoft reicht in `.vscode/mcp.json`:

```json
{
  "servers": {
    "businesscentral": {
      "url": "https://mcp.businesscentral.dynamics.com",
      "type": "http"
    }
  }
}
```

Beim ersten Aufruf meldet VS Code Sie über Microsoft Entra an. Ohne Header läuft der Server im Headerless-Modus. Diese Konfiguration ist ungetestet, weil uns keine Business-Central-Umgebung zur Verfügung stand.

## Externe Clients: Entra-App, Claude Code, Copilot CLI

### Entra-App registrieren

Für alle anderen Clients beschreibt Microsoft eine eigene App-Registrierung:

1. Im Entra Admin Center eine neue App anlegen. Dafür brauchen Sie mindestens die Rolle **Application Developer**.
2. Kontotyp: Konten in einem beliebigen Organisationsverzeichnis (Multi-Tenant).
3. Plattform **Mobile and desktop applications** mit der Redirect-URI des Clients:
   - Claude Code: `http://localhost:<port>/callback`
   - GitHub Copilot CLI: `http://localhost:<port>`
4. API-Berechtigung: **Dynamics 365 Business Central**, delegiert, `Financials.ReadWrite.All`.
5. Admin-Consent erteilen.

Der Scope heißt `ReadWrite`. Was der Benutzer wirklich darf, regeln weiterhin seine Rechte in Business Central und die MCP-Konfiguration.

### Claude Code

Das Beispiel aus Microsoft Learn sieht so aus (Werte ersetzt):

```json
{
  "mcpServers": {
    "businesscentral": {
      "type": "http",
      "url": "https://mcp.businesscentral.dynamics.com",
      "headers": {
        "TenantId": "00000000-0000-0000-0000-000000000000",
        "EnvironmentName": "Production",
        "Company": "Muster GmbH",
        "ConfigurationName": "Vertrieb-Lesen"
      },
      "oauth": {
        "clientId": "11111111-1111-1111-1111-111111111111",
        "callbackPort": 33418
      }
    }
  }
}
```

Per Befehl mit Claude Code 2.1.303 (ausgeführt, die Anmeldung selbst ist ungetestet):

```bash
claude mcp add --scope project --transport http \
  --client-id 11111111-1111-1111-1111-111111111111 \
  --callback-port 33418 \
  businesscentral https://mcp.businesscentral.dynamics.com \
  --header "EnvironmentName: Production" \
  --header "Company: Muster GmbH"
```

Die Optionen `--header` gehören hinter Name und URL. Davor geschrieben, schluckt die Option die folgenden Argumente und der Befehl bricht mit "missing required argument 'name'" ab. Die Redirect-URI in der Entra-App ist dann `http://localhost:33418/callback`. In einer älteren Version (2.1.229) gab es einen gemeldeten Fehler, bei dem Claude Code `127.0.0.1` statt `localhost` schickte. Dann passt die Redirect-URI nicht.

### GitHub Copilot CLI

Laut Microsoft Learn (ungetestet):

```json
{
  "mcpServers": {
    "businesscentral": {
      "type": "http",
      "url": "https://mcp.businesscentral.dynamics.com",
      "headers": {
        "EnvironmentName": "Production"
      },
      "oauthClientId": "11111111-1111-1111-1111-111111111111",
      "oauthRedirectPort": 33418,
      "oauthPublicClient": true,
      "tools": ["*"]
    }
  }
}
```

Für andere Clients gilt dasselbe Muster: Streamable HTTP, OAuth mit eigener Client-ID, Header für die Auswahl. Mehr in [MCP-Clients einrichten](./mcp-clients-einrichten.md).

## Dataverse MCP Server

Für Dynamics 365 Sales, Customer Service, Field Service und Power Apps ist der Dataverse MCP Server zuständig. Quelle: Microsoft Learn, "Connect to Dataverse with Model Context Protocol" (abgerufen 19.10.2026).

- Adresse: `https://{org}.crm.dynamics.com/api/mcp`, Preview-Funktionen unter `/api/mcp_preview`.
- Tools unter anderem: `search_data`, `search`, `read_query`, `describe`, `create_record`, `update_record`, `delete_record`, `create_table`, `update_table`, `delete_table`, `upsert_skill`, `delete_skill` sowie Datei-Tools.
- Im Power Platform Admin Center pflegen Admins je Umgebung eine Liste erlaubter MCP-Clients. Copilot Studio ist standardmäßig erlaubt.

### Abrechnung

Microsoft schreibt: Seit dem **15.12.2025** fallen für Aufrufe aus Agenten außerhalb von Copilot Studio Copilot Credits an. Ausgenommen sind laut Microsoft Kunden mit Dynamics-365-Premium-Lizenzen und Benutzer mit Microsoft-365-Copilot-Lizenz. Einen Preis je Credit nennt die Seite nicht. Prüfen Sie Ihre Lizenzbedingungen.

### Lokaler Proxy

Für Clients mit stdio bietet Microsoft das npm-Paket `@microsoft/dataverse` (Version 1.0.82 am 19.10.2026, Node 18 oder neuer). Ein Admin muss vorher der App `0c412cc3-0dd6-449b-987f-05b053db9457` zustimmen. Beispiel aus der Doku (ungetestet):

```bash
claude mcp add dataverse -t stdio -- npx -y @microsoft/dataverse mcp https://yourorg.crm.dynamics.com
```

Für den direkten Remote-Zugang brauchen Sie eine eigene Entra-App mit der Dynamics-CRM-Berechtigung `mcp.tools`.

Eine Beispielanweisung in der Microsoft-Doku sagt dem Agenten, vor dem Löschen nicht nachzufragen. Für Produktivumgebungen ist das ein Risiko. Prüfen Sie, ob Ihr Client Löschaufrufe bestätigen lässt.

## Dynamics 365 Finance und Supply Chain

Für Finance, Supply Chain Management und die übrigen Finance-and-Operations-Apps gibt es den **Dynamics 365 ERP MCP Server**. Laut Microsoft Learn (abgerufen 19.10.2026):

- Mindestversion 10.0.47, alternativ 10.0.46 mit PQU-2 oder 10.0.45 mit PQU-7.
- Umgebungen ab Tier 2, nicht auf Cloud Hosted Environments (CHE).
- Data-, Form- und Action-Tools.
- Außerhalb von Copilot Studio fallen laut Microsoft 0,1 Copilot Credits je Tool-Aufruf an.
- Nur Sprache en-us.
- Den älteren statischen MCP Server für Finance and Operations hat Microsoft zum **01.10.2026** abgekündigt; die Doku formuliert das am 19.10.2026 noch als Ankündigung.

## Community-Server

Repositories auf GitHub (gh api, 19.10.2026):

| Repository | Ansatz | Lizenz | Sterne |
| --- | --- | --- | --- |
| [SShadowS/business-central-mcp](https://github.com/SShadowS/business-central-mcp) | spricht das Protokoll des Web-Clients nach | MIT | 45 |
| [Bertverbeek4PS/BusinessCentralMCPserver](https://github.com/Bertverbeek4PS/BusinessCentralMCPserver) | eigener Server auf Basis der BC-APIs | MIT | 8 |
| [demiliani/BCMCPProxyVNEXT](https://github.com/demiliani/BCMCPProxyVNEXT) | lokaler Proxy für den offiziellen Server | keine Lizenzangabe | 2 |
| [CDataSoftware/dynamics-365-business-central-mcp-server-by-cdata](https://github.com/CDataSoftware/dynamics-365-business-central-mcp-server-by-cdata) | über einen CData-Treiber, nur lesend | MIT | 2 |

Ein Server, der das interne Protokoll des Web-Clients nachbaut, ist nicht von Microsoft dokumentiert. Er kann mit einem Update brechen. Prüfen Sie außerdem, ob diese Nutzung zu Ihren Vertragsbedingungen passt. Für neue Projekte ist der offizielle Server der naheliegende Startpunkt.

## Beispiele

Die folgenden Prompts sind Beispiele. Wir konnten sie mangels Business-Central-Umgebung nicht ausführen. Die Tool-Namen folgen dem Schema aus der Microsoft-Doku.

### Kunden auflisten

Konfiguration `Vertrieb-Lesen` mit der API-Seite `customers` und nur **Allow Read**.

```text
Liste alle Kunden mit offenem Saldo über 10.000 EUR auf,
sortiert nach Saldo. Zeige Nummer, Name, Ort und Saldo.
```

Der Agent ruft `List_Customers_PAG30009` mit einem Filter auf. Die API-Seiten von Business Central verstehen OData-Optionen wie `$filter`, `$select` und `$orderby`. Ob der Agent den Filter selbst setzt oder alle Kunden lädt und dann filtert, hängt vom Modell ab. Bei großen Kundenstämmen lohnt es sich, im Prompt einen Filter vorzugeben.

### Artikel anlegen

Konfiguration `Einkauf-Schreiben` mit der API-Seite `items`, **Allow Read** und **Allow Create**, Schalter **Unblock Edit Tools** an.

```text
Lege einen neuen Artikel an: Beschreibung "Wartungsset Typ A",
Basiseinheit Stück, Einstandspreis 42,50 EUR. Zeige mir vorher die Werte.
```

Der Agent ruft das Create-Tool für Artikel auf. Ob Ihr Client vor dem Aufruf eine Bestätigung verlangt, hängt vom Client ab. VS Code und Claude Code fragen bei Tool-Aufrufen standardmäßig nach, solange Sie das nicht abschalten. Der Business Central Server selbst prüft nur Konfiguration und Benutzerrechte.

### Daten abfragen (Preview)

Mit den Data Query Tools kann ein Agent Tabellen finden und lesend abfragen:

```text
Welche Tabellen enthalten Sachposten? Zeige die Summe der Sachposten
je Sachkonto für September 2026 im Unternehmen Muster GmbH.
```

Der Agent nutzt `bc_data_find_tables`, `bc_data_get_table_schema` und dann `bc_data_query`. Die Funktion ist Preview. Ergebnisse sind kein Ersatz für die Berichte in Business Central.

## Deutsche Besonderheiten

### Lokalisierung DE

Die Learn-Seite zur deutschen Lokalisierung von Business Central (Stand der Seite 09.10.2026) nennt unter anderem:

- Umsatzsteuer-Berichte, Umsatzsteuer-Voranmeldung (UStVA) und Zusammenfassende Meldung (ZM),
- E-Rechnung mit XRechnung, ZUGFeRD und Peppol,
- Datenexport nach GoBD/GDPdU für digitale Betriebsprüfungen,
- Intrastat.

Geplant sind laut Seite euBP (elektronische Betriebsprüfung) für 2026 Release Wave 2 und ein Update des GDPdU/GoBD-Exports für 2027 Release Wave 1.

Mehr zu E-Rechnungen und MCP in [MCP für Buchhaltung](./buchhaltung-mcp.md).

### DATEV

Ein DATEV-Export steht nicht auf der Learn-Seite zur deutschen Lokalisierung. In der Praxis kommt er oft über Erweiterungen von Partnern aus AppSource. Welche es gibt und was sie können, haben wir hier nicht geprüft. Der Business Central MCP Server sieht solche Erweiterungen nur, wenn sie eigene API-Seiten mitbringen und Sie diese in der MCP-Konfiguration freigeben.

Wie DATEV selbst per MCP angebunden werden kann, beschreibt die [Anleitung zum DATEV-Format (EXTF)](./datev-mcp-server.md).

### Umlaute in Unternehmensnamen

Viele deutsche Unternehmensnamen enthalten Umlaute oder ß. Diese müssen im Header `Company` Base64-kodiert übergeben werden, siehe [Header](#header-mandant-umgebung-unternehmen). Sonst findet der Server das Unternehmen nicht.

## Risiken und Empfehlungen

- **Eine Konfiguration je Zweck.** Lieber `Vertrieb-Lesen` und `Einkauf-Schreiben` als eine Konfiguration mit allem.
- **Unblock Edit Tools nur gezielt.** Ohne diesen Schalter bleibt der Server lesend.
- **Allow Delete vermeiden.** Löschen in einem ERP hat oft Folgen für Belege und Posten.
- **Sandbox zuerst.** Testen Sie mit `EnvironmentName: Sandbox`, bevor Sie `Production` freigeben.
- **Benutzerrechte prüfen.** Der Agent arbeitet mit Ihren Rechten. Ein Benutzer mit SUPER-Rechten gibt dem Agenten alles, was die MCP-Konfiguration zulässt.
- **Datenabfluss.** Finanz- und Kundendaten gehen an den Anbieter des Sprachmodells. Klären Sie AV-Vertrag und Datenstandort, siehe [MCP und DSGVO](./mcp-dsgvo.md).
- **Protokollierung.** Microsoft protokolliert Konfigurationsänderungen in Purview und bietet Telemetrie. Prüfen Sie, ob Sie Tool-Aufrufe auswerten können.

Allgemeine Punkte stehen in [MCP-Sicherheit](./mcp-sicherheit.md).

## Häufige Fragen

### Gibt es einen offiziellen Business Central MCP Server?

Ja. Microsoft betreibt ihn unter `https://mcp.businesscentral.dynamics.com`. Laut Release-Plan ist er seit dem 01.04.2026 allgemein verfügbar. Die Data Query Tools sind Preview.

### Funktioniert der MCP Server mit Business Central on-premises?

Die Learn-Seiten gelten laut Kopfzeile für Business Central online. Eine Variante für on-premises beschreibt Microsoft dort nicht.

### Brauche ich eine eigene Entra-App?

Für Copilot Studio und VS Code nicht, die nutzen eine vorregistrierte App. Für Claude Code, GitHub Copilot CLI und andere Clients ja: Multi-Tenant, Plattform "Mobile and desktop", delegiert `Financials.ReadWrite.All`, Admin-Consent.

### Kann der Agent Daten in Business Central ändern?

Nur, wenn Sie in der MCP-Konfiguration **Unblock Edit Tools** setzen und je API-Seite Allow Create, Modify oder Delete erlauben. Außerdem braucht der angemeldete Benutzer selbst die Rechte.

### Was ist der Unterschied zwischen Business Central MCP und Dynamics 365 MCP?

Business Central hat einen eigenen Server. Dynamics 365 Sales, Customer Service und Power Apps nutzen den Dataverse MCP Server. Finance und Supply Chain nutzen den Dynamics 365 ERP MCP Server.

### Kostet der MCP Server extra?

Für Business Central nennt die Übersichtsseite keinen eigenen Preis. Für Dataverse und den ERP MCP Server von Finance and Operations nennt Microsoft eine Abrechnung über Copilot Credits außerhalb von Copilot Studio, mit Ausnahmen für bestimmte Lizenzen.

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
- [HubSpot MCP](./hubspot-mcp.md)
- [Postgres MCP](./postgres-mcp.md)
- [MCP für Buchhaltung](./buchhaltung-mcp.md)

> **Hinweis:** Technische Informationen nach Stand 19.10.2026, ohne Gewähr für Vollständigkeit
> und Richtigkeit. Keine Rechts- oder Steuerberatung; die Autoren sind keine Rechtsanwälte,
> Steuerberater oder Datenschutzbeauftragten. Produktnamen sind Marken ihrer Inhaber; es besteht
> keine Verbindung zu den genannten Herstellern.

> Die Autoren erbringen keine Hilfeleistung in Steuersachen im Sinne des Steuerberatungsgesetzes.
> Ob und wie Buchungen steuerlich richtig sind, klären Sie mit Ihrer Steuerberatung. DATEV ist
> eine Marke der DATEV eG; dieses Projekt ist kein Produkt der DATEV eG und nicht von ihr geprüft
> oder freigegeben.
