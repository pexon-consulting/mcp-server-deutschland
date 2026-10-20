# SAP MCP Server: offizielle Angebote, GitHub-Projekte und Architektur

Diese Anleitung ist für SAP-Entwickler, Basis-Teams und Architekten, die KI-Assistenten wie Claude, Copilot oder Cursor über das Model Context Protocol (MCP) an SAP anbinden wollen. Sie zeigt, welche SAP MCP Server es offiziell gibt, welche Community-Server auf GitHub verbreitet sind und welche Berechtigungs- und Lizenzfragen Sie vorher klären sollten.

Stand: 19.10.2026

## Inhaltsverzeichnis

- [Das Wichtigste in Kürze](#das-wichtigste-in-kürze)
- [Offizielle SAP-Angebote im Überblick](#offizielle-sap-angebote-im-überblick)
- [SAP MCP Gateway in der Integration Suite](#sap-mcp-gateway-in-der-integration-suite)
- [ABAP MCP: der ADT MCP Server](#abap-mcp-der-adt-mcp-server)
- [SAP-Entwickler-MCP-Server: CAP, UI5, Fiori, MDK](#sap-entwickler-mcp-server-cap-ui5-fiori-mdk)
- [Joule Studio und SAP-verwaltete MCP Server](#joule-studio-und-sap-verwaltete-mcp-server)
- [SAP MCP Server auf GitHub: Community-Projekte](#sap-mcp-server-auf-github-community-projekte)
- [Architektur-Optionen: OData, RFC oder ADT](#architektur-optionen-odata-rfc-oder-adt)
- [Berechtigungen](#berechtigungen)
- [Lizenzfragen als Prüfpunkte](#lizenzfragen-als-prüfpunkte)
- [Beispiel: Community-Server mcp-abap-adt konfigurieren](#beispiel-community-server-mcp-abap-adt-konfigurieren)
- [Häufige Fragen](#häufige-fragen)
- [Weiterlesen](#weiterlesen)

## Das Wichtigste in Kürze

- SAP bietet keinen einzelnen "SAP MCP Server", sondern mehrere Bausteine: das MCP Gateway in der SAP Integration Suite für Geschäftsdaten, den ADT MCP Server für ABAP-Entwicklung sowie Open-Source-Server für CAP, UI5, Fiori und MDK.
- Das MCP Gateway erzeugt MCP Server aus API-Artefakten, OpenAPI-Beschreibungen, RFC-Funktionen oder fremden MCP Servern. Es unterstützt laut SAP-Hilfe die Protokollversionen 2025-11-25 und 2026-07-28.
- Für Werkzeuge des ADT MCP Servers in ADT für VS Code setzt SAP eine gültige Lizenz "SAP Joule for Developers, ABAP AI capabilities" voraus.
- Die SAP API Policy (v.4.2026a) verbietet in Abschnitt 2.2.2 die API-Nutzung durch KI-Systeme, die Aufrufketten selbst planen, außer über von SAP anerkannte Architekturen. Das betrifft auch selbst betriebene MCP Server.
- Die bekannteste Sammelliste ist [marianfoo/sap-ai-mcp-servers](https://github.com/marianfoo/sap-ai-mcp-servers) mit 527 Sternen (gh api, 19.10.2026).

## Offizielle SAP-Angebote im Überblick

| Angebot | Zweck | Betrieb | Quelle (abgerufen 19.10.2026) |
| --- | --- | --- | --- |
| MCP Gateway (MCP Server in SAP Integration Suite) | Geschäfts-APIs, iFlows, RFC als MCP-Tools | SAP-verwaltet, Integration Cell | [SAP Help: MCP Server](https://help.sap.com/docs/SAP_INTEGRATION_SUITE/9519789d5664487f8b9cd89eba514477/9eb9239c1b4c458198ca5234d191f8bd.html) |
| ADT MCP Server | ABAP-Entwicklung aus KI-Assistenten | lokal in ADT für Eclipse bzw. ADT für VS Code | [SAP Help: Enabling ADT MCP Server](https://help.sap.com/docs/ABAP_AI/c7f5ef43ab274d078baf22f995fd2161/6f6e72852b9746ffbe083d5a818fbbec.html) |
| CAP MCP Server | CDS-Modelle und CAP-Doku durchsuchen | lokal, npm `@cap-js/mcp-server` | [cap-js/mcp-server](https://github.com/cap-js/mcp-server) |
| UI5 MCP Server | UI5-Projekte anlegen, UI5-Wissen | lokal, npm `@ui5/mcp-server` | [UI5/mcp-server](https://github.com/UI5/mcp-server) |
| SAP Fiori MCP Server | Fiori-Apps erzeugen und ändern | lokal, npm `@sap-ux/fiori-mcp-server` | [SAP/open-ux-tools](https://github.com/SAP/open-ux-tools/tree/main/packages/fiori-mcp-server) |
| SAP MDK MCP Server | Mobile Development Kit | lokal | [SAP/mdk-mcp-server](https://github.com/SAP/mdk-mcp-server) |
| MCP Server for SAP BTP Administration | BTP-Konten, Sicherheit, Services | laut SAP-Hilfe | [SAP Help](https://help.sap.com/docs/btp/sap-business-technology-platform/account-administration-using-mcp-servers) |
| SAP LeanIX MCP Server | Unternehmensarchitektur-Daten | gehostet | [SAP Help](https://help.sap.com/docs/leanix/ea/mcp-server) |
| Joule Studio | erzeugt SAP-verwaltete MCP Server für Fachbereichs-Funktionen | SAP-verwaltet | [SAP Architecture Center](https://architecture.learning.sap.com/docs/ref-arch/137800) |

Die Seiten zu BTP Administration und LeanIX wurden für diese Anleitung nicht im Detail gelesen. Funktionsumfang und Status dieser beiden Server sind deshalb hier ungeprüft.

## SAP MCP Gateway in der Integration Suite

Das "SAP MCP Gateway" ist laut SAP-Hilfe die Laufzeitschicht, über die die Integration Suite ihre Funktion "MCP Server" bereitstellt. Sie legen in einem Integrationspaket ein Artefakt vom Typ MCP Server an. Das Gateway übernimmt Authentifizierung (OIDC/OAuth 2.0), Ratenbegrenzung, Monitoring und den Lebenszyklus der Tools. Die Architekturseite von Microsoft Learn zum Gateway nennt Streamable HTTP als Transport.

Die SAP-Hilfe (Stand der Seite 19.10.2026) nennt vier Wege, einen MCP Server zu erzeugen:

| Quelle | Was daraus wird |
| --- | --- |
| API-Artefakt | ein auf der Integration Cell bereitgestelltes API-Artefakt wird zu Tools |
| HTTP-Endpunkt | beliebiger REST-Dienst, beschrieben durch eine OpenAPI-Spezifikation |
| RFC-Backend | ausgewählte RFC-Funktionsbausteine aus SAP ECC oder S/4HANA |
| Remote-MCP-Server | ein fremder MCP Server, den das Gateway als verwalteter Proxy absichert |

Wichtige Einschränkungen und Voraussetzungen aus der SAP-Hilfe:

- Die Verfügbarkeit hängt vom Service-Plan der Integration Suite ab (SAP-Hinweis 2903776).
- Für die RFC-Variante brauchen Sie die API-Management-Funktion, die Integration-Cell-Laufzeit, die Rollensammlung `PI_Integration_Developer`, eine RFC-Destination und den Cloud Connector.
- Im Cloud Connector müssen für die RFC-Erkennung unter anderem `RFC_FUNCTION_SEARCH`, `RFC_METADATA_GET`, `BAPI_TRANSACTION_COMMIT` und `BAPI_TRANSACTION_ROLLBACK` freigegeben sein.
- Ein RFC-basierter MCP Server darf höchstens 50 Tools enthalten.
- MCP über RFC unterstützt SAP ECC 6.0 (NetWeaver 7.0 bis 7.5), ECC 5.0 und S/4HANA.

Für On-Premise- und Private-Cloud-Systeme läuft der Weg über den Cloud Connector mit Principal Propagation. Damit kommt der angemeldete Benutzer als echter ABAP-Benutzer im Backend an (Quelle: [Microsoft Learn, SAP MCP Gateway](https://learn.microsoft.com/en-us/azure/sap/microsoft-ai/copilot-studio/architecture-mcp-gateway-integration-suite), abgerufen 19.10.2026). Für S/4HANA Cloud Public Edition beschreibt ein [SAP-Community-Beitrag zu Principal Propagation](https://community.sap.com/t5/technology-blog-posts-by-sap/principal-propagation-for-mcp-servers-sap-integration-suite-to-sap-s-4hana/ba-p/14488140) den Weg über OAuth2SAMLBearerAssertion (abgerufen 16.10.2026).

Das Gateway unterstützt beide aktuellen Protokollversionen. Die SAP-Hilfe formuliert es so: "SAP Integration Suite supports both MCP specification version 2025-11-25 and version 2026-07-28". Ihr Client verbindet sich mit der Version, auf der er gebaut ist.

## ABAP MCP: der ADT MCP Server

Wer nach "abap mcp" sucht, landet meist bei zwei Dingen: dem offiziellen ADT MCP Server von SAP und Community-Servern, die die ADT-REST-Schnittstelle nutzen. Der offizielle Server ist Teil der ABAP Development Tools.

### In ADT für Eclipse

Laut SAP-Hilfe "Enabling ADT MCP Server" (Seite vom 01.10.2026):

1. In Eclipse **Window > Preferences > ABAP Development > MCP Server** öffnen.
2. **Enable ADT MCP Server** wählen. Das startet einen lokalen HTTP-Server unter `http://localhost:<port>/mcp`.
3. Der Standard-Port ist **2234**. Beim Aktivieren erzeugt ADT ein **Server Token**, das der Client als Bearer-Token schickt.
4. Unter **Access Restrictions** legen Sie fest, auf welche ABAP-Projekte zugegriffen werden darf und in welchen Paketen Objekte geändert werden dürfen. Lesen ist laut Doku aus allen Paketen erlaubt.

Die Konfigurationsseite zeigt ein Beispiel für VS Code. Angepasst an das aktuelle VS-Code-Format (Schlüssel `servers`, Header direkt unter `headers`) sieht das so aus. Ungetestet, weil kein SAP-System verfügbar war:

```json
{
  "servers": {
    "com.sap.adt/mcp": {
      "type": "http",
      "url": "http://localhost:2234/mcp",
      "headers": {
        "Authorization": "Bearer ${input:adt-token}"
      }
    }
  },
  "inputs": [
    {
      "id": "adt-token",
      "type": "promptString",
      "description": "ADT MCP Server Token aus den Eclipse-Einstellungen",
      "password": true
    }
  ]
}
```

Das SAP-Beispiel selbst nutzt `requestInit.headers`. Welche Form Ihr Client erwartet, prüfen Sie in dessen Doku (siehe [MCP-Clients einrichten](./mcp-clients-einrichten.md)).

### In ADT für VS Code

Die SAP-Hilfe "Model Context Protocol Tools" (Seite vom 16.10.2026) listet die Werkzeuge in ADT für VS Code. Eine Auswahl:

| Werkzeuggruppe | Beispiele | Joule-Token nötig |
| --- | --- | --- |
| Objektsuche und Dateien | `abap_repository_search_object`, `abap_read_file`, `abap_edit_file` | nein |
| Anlegen und Aktivieren | `abap_object_create`, `abap_activate_objects` | nein |
| Transporte | `abap_transport_create_request`, `abap_transport_get_unified_diff` | nein |
| Tests und ATC | `abap_run_unit_tests`, `abap_run_atc`, `abap_atc_apply_ai_fix` | ATC-KI-Fix ja |
| Erklärung und Doku | `abap_explain_object`, `abap_docs_dcp` | ja |
| Fehleranalyse | `abap_feed_query` (Kurzdumps ST22, Gateway-Fehlerprotokoll) | nein |

Zwei Hinweise aus derselben Seite sollten Sie kennen:

- "Support for the MCP tools is only provided if the customer possesses a valid SAP Joule for Developers, ABAP AI capabilities license."
- Zu `abap_feed_query` warnt SAP, dass über das Gateway-Fehlerprotokoll echte Geschäftsdaten, auch personenbezogene, an den KI-Anbieter gelangen können.

Die Sicherheitsseite zum ADT MCP Server nennt ausdrücklich Prompt Injection als Risiko und legt die Verantwortung für weitere installierte MCP Server beim Benutzer.

## SAP-Entwickler-MCP-Server: CAP, UI5, Fiori, MDK

Diese Server sprechen nicht mit Ihrem SAP-System, sondern helfen beim Entwickeln. Sie laufen lokal über stdio und werden per `npx` gestartet.

| Server | npm-Paket, Version (npm, 19.10.2026) | Lizenz | Sterne |
| --- | --- | --- | --- |
| CAP MCP Server | `@cap-js/mcp-server` 0.0.8 | Apache-2.0 | 116 |
| UI5 MCP Server | `@ui5/mcp-server` 0.3.2 | Apache-2.0 | 103 |
| SAP Fiori MCP Server | `@sap-ux/fiori-mcp-server` 1.15.13 | Apache-2.0 | 159 (Monorepo open-ux-tools) |

Den CAP-Server haben wir lokal gestartet. Er meldet sich als `cds-mcp`, spricht Protokoll 2025-11-25 und bietet zwei Tools: `search_model` und `search_docs`. Eintragen in Claude Code laut README:

```bash
claude mcp add --scope project cds-mcp -- npx -y @cap-js/mcp-server
```

Das Fiori-README empfiehlt, eine feste Version zu verwenden statt `@latest`:

```bash
claude mcp add fiori-mcp -- npx --yes @sap-ux/fiori-mcp-server@1.15.13 fiori-mcp
```

Der Fiori-Befehl ist aus dem README übernommen und hier nicht ausgeführt.

## Joule Studio und SAP-verwaltete MCP Server

Joule ist der KI-Assistent von SAP. Laut SAP Architecture Center (Seite "Third-Party MCP Server Access to SAP Solutions on BTP", zuletzt geändert 08.06.2026) kann SAP beim Bau von Joule-Agenten in Joule Studio MCP Server für Fachbereichs-Funktionen erzeugen. SAP verwaltet dann Lebenszyklus, Protokoll-Upgrades und Sicherheit. Für Agent-zu-Agent-Szenarien empfiehlt SAP A2A über das Agent Gateway.

Wie Joule selbst als MCP-Client fremde Server einbindet, wurde für diese Anleitung nicht geprüft.

## SAP MCP Server auf GitHub: Community-Projekte

Die Sammelliste [marianfoo/sap-ai-mcp-servers](https://github.com/marianfoo/sap-ai-mcp-servers) (MIT, "Last generated: 2026-10-19") ordnet offizielle und Community-Projekte nach Bereichen und hat einen interaktiven Katalog. Die folgende Auswahl stammt aus `gh api` am 19.10.2026:

| Repository | Bereich | Lizenz | Sterne | Letzter Push |
| --- | --- | --- | --- | --- |
| [oisee/vibing-steampunk](https://github.com/oisee/vibing-steampunk) | ADT-Brücke für ABAP und AMDP | MIT | 505 | 09.10.2026 |
| [marianfoo/mcp-sap-docs](https://github.com/marianfoo/mcp-sap-docs) | SAP-Dokumentation durchsuchen | Apache-2.0 | 243 | 19.10.2026 |
| [arc-mcp/arc-1](https://github.com/arc-mcp/arc-1) | ADT, BTP OAuth | MIT | 229 | 19.10.2026 |
| [mario-andreschak/mcp-abap-abap-adt-api](https://github.com/mario-andreschak/mcp-abap-abap-adt-api) | ADT über abap-adt-api | MIT | 204 | 16.09.2026 |
| [mario-andreschak/mcp-abap-adt](https://github.com/mario-andreschak/mcp-abap-adt) | ADT, nur lesend | MIT | 200 | 16.09.2026 |
| [oisee/odata_mcp_go](https://github.com/oisee/odata_mcp_go) | OData v2/v4 als Tools | MIT | 145 | 19.02.2026 |
| [mario-andreschak/mcp-sap-gui](https://github.com/mario-andreschak/mcp-sap-gui) | SAP-GUI-Steuerung | MIT | 141 | 24.09.2026 |
| [lemaiwo/btp-sap-odata-to-mcp-server](https://github.com/lemaiwo/btp-sap-odata-to-mcp-server) | OData über BTP | MIT | 137 | 22.05.2026 |
| [HatriGt/hana-mcp-server](https://github.com/HatriGt/hana-mcp-server) | SAP HANA | MIT | 71 | 07.10.2026 |

Sterne sind ein Hinweis auf Verbreitung, kein Qualitätsurteil. Prüfen Sie vor dem Einsatz Lizenz, letzte Aktivität, Protokollversion und ob der Server schreiben kann.

## Architektur-Optionen: OData, RFC oder ADT

Es gibt drei technische Wege, über die ein MCP Server mit einem SAP-System spricht. Welcher passt, hängt davon ab, ob Sie Geschäftsdaten oder Entwicklungsobjekte brauchen.

| Weg | Typische Nutzung | Beispiele | Zu beachten |
| --- | --- | --- | --- |
| OData über BTP Destination | Geschäftsdaten lesen und schreiben | MCP Gateway (API-Artefakt), lemaiwo/btp-sap-odata-to-mcp-server, odata_mcp_go | nur veröffentlichte APIs (API Policy 1.1), Principal Propagation statt Sammelbenutzer |
| RFC/BAPI | Altsysteme ohne passende OData-Dienste | MCP Gateway (RFC-Quelle), romankorim/sap-mcp-server | Cloud Connector, RFC-Berechtigungen, Commit/Rollback |
| ABAP ADT (REST) | Quellcode, Tabellen, Transporte | offizieller ADT MCP Server, mcp-abap-adt, arc-1, vibing-steampunk | Entwicklerrechte, kein Produktivsystem |
| SAP GUI Scripting | Abläufe ohne API | mcp-sap-gui | nur Windows, fragil, schwer prüfbar |

### Variante OData über BTP Destination

Der MCP Server läuft auf SAP BTP (Cloud Foundry oder Kyma) und erreicht das Backend über eine Destination. Bei On-Premise-Systemen hängt der Cloud Connector dazwischen. Vorteile: Die Zugangsdaten liegen im Destination Service, nicht im MCP Server, und Principal Propagation ist möglich.

SAP nennt das im Architecture Center "Pattern 2: Custom MCP Server on SAP BTP". Die gesamte Betriebs- und Sicherheitsverantwortung liegt dann beim Kunden. SAP verlangt dort unter anderem:

- Token-Austausch (RFC 8693) statt Weiterreichen des Benutzer-Tokens.
- Eingaben jedes Tool-Aufrufs validieren.
- Ratenbegrenzung unterhalb der Limits der SAP-APIs.
- Protokollierung jedes Aufrufs mit Aufrufer, Ziel-API und Status.

### Variante RFC

Für ältere ECC-Systeme gibt es oft keine passenden OData-Dienste. Die Integration Suite kann RFC-Funktionen direkt als Tools anbieten (siehe oben). Community-Server mit eigener RFC-Anbindung brauchen die SAP NetWeaver RFC SDK oder eine Brücke. Prüfen Sie hier besonders, ob ein BAPI schreibt und wer `BAPI_TRANSACTION_COMMIT` auslöst.

### Variante ADT

ADT ist die REST-Schnittstelle der ABAP-Entwicklungswerkzeuge. Sie liefert Quellcode, Dictionary-Objekte und Transporte. Community-Server wie `mcp-abap-adt` melden sich mit Benutzer und Passwort am System an. Das ist für Entwicklungssysteme gedacht. Ein Tool wie `GetTableContents` kann aber auch Tabelleninhalte lesen, also im Zweifel personenbezogene Daten.

## Berechtigungen

MCP ändert nichts an den SAP-Berechtigungen. Der Server kann genau das, was der verwendete Benutzer darf. Daraus folgen ein paar Regeln:

- **Kein Sammelbenutzer mit SAP_ALL.** Ein technischer Benutzer mit breiten Rechten macht jeden Tool-Aufruf zu einem Aufruf mit diesen Rechten.
- **Principal Propagation bevorzugen.** Dann arbeitet der Agent als der angemeldete Mensch, und das Änderungsprotokoll zeigt, wer es war.
- **Typische Berechtigungsobjekte prüfen.** Für ADT ist das in klassischen Systemen meist `S_DEVELOP`, für RFC `S_RFC`, für OData-Dienste `S_SERVICE` plus die fachlichen Objekte. Welche Rollen bei Ihnen gelten, klärt Ihr Berechtigungsteam.
- **Schreibende Tools getrennt freigeben.** Beim offiziellen ADT MCP Server über die Paketliste, bei Community-Servern über Lese-Modi, beim Gateway über die Auswahl der Operationen.
- **Kein Produktivsystem für Experimente.** ADT-Server gehören an Entwicklungs- oder Sandbox-Systeme.

Mehr zu Rechten, Tokens und Prompt Injection steht in [MCP-Sicherheit](./mcp-sicherheit.md).

## Lizenzfragen als Prüfpunkte

Dieser Abschnitt ist keine Rechtsberatung. Er nennt Punkte, die Sie mit Ihrem SAP-Vertrag, Ihrem Lizenzmanagement oder SAP selbst klären sollten.

### SAP API Policy

Die [SAP API Policy v.4.2026a](https://help.sap.com/doc/sap-api-policy/latest/en-US/API_Policy_latest.pdf) (PDF, abgerufen 19.10.2026) gehört laut eigenem Text zur Dokumentation der SAP-Lösungen. Zwei Stellen sind für MCP relevant:

- Abschnitt 1.2: Nicht veröffentlichte APIs dürfen von Kunden- und Drittanwendungen nicht genutzt werden, außer die Dokumentation erlaubt es. Kundeneigene ABAP-Schnittstellen in Private Cloud und On-Premise sind als Beispiel ausgenommen.
- Abschnitt 2.2.2: Außerhalb von "SAP-endorsed architectures" ist API-Nutzung für "(semi-) autonomous or generative AI systems that plan, select, or execute sequences of API calls" untersagt, ebenso großflächiges Extrahieren von Daten.

Das SAP Architecture Center nennt als anerkannte Wege das MCP Gateway, von Joule Studio erzeugte MCP Server und A2A über das Agent Gateway. Fremde MCP Server sind dort erlaubt, wenn die API Policy vollständig eingehalten wird. Ob Ihr konkreter Aufbau darunter fällt, ist eine Vertrags- und Auslegungsfrage. SAP hat dazu ein [FAQ zur API Policy](https://www.sap.com/documents/2026/04/e2a0665e-4c7f-0010-bca6-c68f7e60039b.html) veröffentlicht, das für diese Anleitung nicht im Detail gelesen wurde.

### Indirekte Nutzung und Digital Access

SAP lizenziert den Zugriff von Drittsoftware, Bots und automatisierten Systemen auf das ERP-Kernsystem gesondert. Laut SAP-Übersicht "SAP ERP Pricing for the Digital Age" ([PDF](https://news.sap.com/wp-content/blogs.dir/1/files/Pricing_for_Digital_Age_Overview-3.pdf)) zählt im Modell Digital Access das Anlegen von Belegen aus neun Belegarten. Lesen, Ändern und Löschen zählen dort nicht.

Ein MCP Server, über den ein Agent Aufträge oder Bestellungen anlegt, kann also lizenzrelevant sein. Ob und wie, hängt von Ihrem Vertragsmodell ab (klassische Lizenz, Digital Access, RISE). Preise nennen wir nicht, weil sie vertragsabhängig sind.

### Lizenz der Werkzeuge selbst

- ADT MCP Tools in VS Code: Lizenz "SAP Joule for Developers, ABAP AI capabilities" (siehe oben).
- MCP Gateway: abhängig vom Service-Plan der Integration Suite (SAP-Hinweis 2903776).
- Community-Server: meist MIT oder Apache-2.0. Das regelt nur den Code, nicht Ihr Nutzungsrecht am SAP-System.

## Beispiel: Community-Server mcp-abap-adt konfigurieren

[mario-andreschak/mcp-abap-adt](https://github.com/mario-andreschak/mcp-abap-adt) ist auf npm als `mcp-abap-adt` (Version 1.2.0) und in der offiziellen MCP Registry als `io.github.mario-andreschak/mcp-abap-adt` gelistet. Laut README sind alle 16 Tools nur lesend. Der Server läuft über stdio.

**Was getestet ist:** Wir haben das Paket in einem temporären Ordner installiert und ohne SAP-System gestartet. `initialize` und `tools/list` funktionieren. **Was nicht getestet ist:** jede Verbindung zu einem echten SAP-System, weil keins zur Verfügung stand.

### Schritt 1: Start und Tool-Liste prüfen

Damit sehen Sie ohne Client, ob der Server läuft. Die SAP-Werte sind Platzhalter.

```bash
mkdir -p /tmp/abaptest && cd /tmp/abaptest
npm init -y >/dev/null && npm i mcp-abap-adt@1.2.0
(printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'; sleep 3) \
| SAP_URL=https://sap.example:44300 SAP_USERNAME=DEMO SAP_PASSWORD=demo SAP_CLIENT=100 \
  ./node_modules/.bin/mcp-abap-adt
```

Ergebnis am 19.10.2026 (gekürzt):

```text
serverInfo: mcp-abap-adt 0.1.0, protocolVersion 2025-11-25
tools: GetProgram, GetClass, GetFunctionGroup, GetFunction, GetStructure,
       GetTable, GetTableContents, GetPackage, GetTypeInfo, GetInclude,
       SearchObject, GetTransaction, GetCDSView, GetInterface,
       GetBehaviorDefinition, GetServiceDefinition
```

### Schritt 2: in Claude Code eintragen

Der folgende Befehl wurde ausgeführt und schreibt eine `.mcp.json` im Projektordner. Das Passwort steht bewusst nicht im Befehl:

```bash
claude mcp add --scope project abap-adt \
  -e SAP_URL=https://sap.example:44300 -e SAP_CLIENT=100 \
  -- npx -y mcp-abap-adt
```

Erzeugte Datei mit Claude Code 2.1.303:

```json
{
  "mcpServers": {
    "abap-adt": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-abap-adt"],
      "env": {
        "SAP_URL": "https://sap.example:44300",
        "SAP_CLIENT": "100"
      }
    }
  }
}
```

`SAP_USERNAME` und `SAP_PASSWORD` gehören nicht in eine Datei, die ins Git wandert. Setzen Sie sie in der Shell oder über eine nicht eingecheckte `.env`. Laut README sind außerdem `SAP_LANGUAGE` und `SAP_CA_FILE` (eigene CA als PEM) möglich. Die Zertifikatsprüfung ist standardmäßig an.

### Schritt 3: erste Abfrage (ungetestet)

Mit einem erreichbaren Entwicklungssystem wäre ein typischer Prompt:

```text
Suche im SAP-System alle Klassen, die mit ZCL_FI_ beginnen,
und zeige mir den Quelltext der Methode CALCULATE in ZCL_FI_MAHNUNG.
```

Der Agent würde `SearchObject` und danach `GetClass` aufrufen. Dieser Schritt ist ungetestet.

## Häufige Fragen

### Gibt es einen offiziellen SAP MCP Server?

Ja, mehrere. Für Geschäftsdaten ist es das MCP Gateway in der SAP Integration Suite, für ABAP-Entwicklung der ADT MCP Server in ADT für Eclipse und VS Code. Dazu kommen Open-Source-Server von SAP für CAP, UI5, Fiori und MDK.

### Was ist das SAP MCP Gateway?

Das MCP Gateway ist die Laufzeit hinter der Funktion "MCP Server" in der SAP Integration Suite. Es macht aus API-Artefakten, OpenAPI-Beschreibungen, RFC-Funktionen oder fremden MCP Servern verwaltete MCP-Endpunkte mit OAuth, Ratenbegrenzung und Monitoring.

### Wo finde ich SAP MCP Server auf GitHub?

Die Sammelliste [marianfoo/sap-ai-mcp-servers](https://github.com/marianfoo/sap-ai-mcp-servers) ordnet offizielle und Community-Projekte. Offizielle Server liegen in den Organisationen `SAP`, `cap-js` und `UI5`.

### Darf ich einen eigenen MCP Server an S/4HANA hängen?

Technisch ja. Vertraglich müssen Sie die SAP API Policy einhalten, besonders Abschnitt 2.2.2 zu KI-Systemen, und gegebenenfalls Digital Access berücksichtigen. Klären Sie das mit Ihrem SAP-Vertrag und Lizenzmanagement, bevor Sie produktiv gehen.

### Was ist der Unterschied zwischen ABAP MCP und SAP MCP Gateway?

ABAP MCP (ADT MCP Server) arbeitet mit Entwicklungsobjekten wie Klassen, Tabellendefinitionen und Transporten. Das Gateway stellt Geschäftsprozesse und Daten bereit, zum Beispiel Kundenaufträge über OData oder BAPIs.

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
- [Power BI MCP](./power-bi-mcp.md)
- [HubSpot MCP](./hubspot-mcp.md)
- [Postgres MCP](./postgres-mcp.md)
- [MCP für Buchhaltung](./buchhaltung-mcp.md)
- [Business Central MCP](./business-central-mcp.md)

> **Hinweis:** Technische Informationen nach Stand 19.10.2026, ohne Gewähr für Vollständigkeit
> und Richtigkeit. Keine Rechts- oder Steuerberatung; die Autoren sind keine Rechtsanwälte,
> Steuerberater oder Datenschutzbeauftragten. Produktnamen sind Marken ihrer Inhaber; es besteht
> keine Verbindung zu den genannten Herstellern.
