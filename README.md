# MCP-Server für deutsche Geschäftssysteme: Liste, DATEV-Server und Anleitungen

Welche MCP-Server gibt es für SAP, DATEV, lexware office, sevdesk, HubSpot, Power BI, Business Central, Personio, Shopware und Postgres, wer bietet sie an, und was dürfen sie? Dieses Repository sammelt die Antworten auf Deutsch: eine gepflegte Liste mit über 130 MCP-Servern, einen eigenen, getesteten MCP-Server für das DATEV-Format und 13 Anleitungen.

> Stand: 19.10.2026. MIT-Lizenz. Technisches Hilfswerk, keine Beratung. Wir haften nicht für Ausgaben von KI-Systemen. Kein offizielles Projekt der genannten Hersteller.

## Inhalt

- [Was ist ein MCP-Server?](#was-ist-ein-mcp-server)
- [Die Liste auf einen Blick](#die-liste-auf-einen-blick)
- [MCP-Server für das DATEV-Format (EXTF)](#mcp-server-für-das-datev-format-extf)
- [Anleitungen](#anleitungen)
- [Beispiel: eigener MCP-Server in Python und TypeScript](#beispiel-eigener-mcp-server-in-python-und-typescript)
- [Was dieses Repository nicht ist](#was-dieses-repository-nicht-ist)
- [Häufige Fragen](#häufige-fragen)
- [Mitmachen](#mitmachen)
- [Hinweise und Lizenz](#hinweise-und-lizenz)

## Was ist ein MCP-Server?

Das Model Context Protocol (MCP) ist ein offener Standard, über den KI-Anwendungen wie Claude, ChatGPT, Cursor, VS Code oder Codex auf Werkzeuge und Daten zugreifen. Ein MCP-Server stellt solche Werkzeuge bereit, zum Beispiel "Kunden suchen", "Rechnung lesen" oder "Buchungsstapel prüfen". Der KI-Client entdeckt die Werkzeuge zur Laufzeit und ruft sie auf, wenn der Nutzer es verlangt.

Für Unternehmen heißt das: Ein MCP-Server ersetzt keine API, er macht eine vorhandene API oder Datei für KI-Assistenten nutzbar. Rechte, Lizenzen und Ratenlimits des Systems gelten weiter. Mehr dazu in [Was ist ein MCP-Server?](docs/anleitungen/was-ist-ein-mcp-server.md) und [MCP vs. API](docs/anleitungen/mcp-vs-api.md).

## Die Liste auf einen Blick

Die vollständige Liste mit Transport, Authentifizierung, Lese- oder Schreibzugriff, Lizenz und Quelle je Eintrag steht in [docs/liste.md](docs/liste.md). Sie wird aus [daten/server.yaml](daten/server.yaml) erzeugt. Offizielle Server der Hersteller stehen zuerst, danach Community-Projekte. Sterne bestimmen nur die Reihenfolge und sagen nichts über Qualität oder Sicherheit.

<!-- liste:start -->

Stand 19.10.2026: 138 Server in 13 Kategorien. Je Kategorie die offiziellen Server und bis zu drei Community-Server (nach GitHub-Sternen). Vollständige Liste mit Transport, Auth und Lizenz: [docs/liste.md](docs/liste.md).

- **ERP** - offiziell: [SAP Fiori MCP Server](https://github.com/SAP/open-ux-tools/tree/main/packages/fiori-mcp-server), [SAP CAP MCP Server](https://github.com/cap-js/mcp-server), [UI5 MCP Server](https://github.com/UI5/mcp-server), [Business Central MCP Server](https://mcp.businesscentral.dynamics.com), [Dynamics 365 ERP MCP Server](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/copilot/copilot-mcp), [JTL Developer MCP](https://developer.jtl-software.com/mcp), [Odoo MCP Server (AI-App)](https://www.odoo.com/documentation/20.0/applications/productivity/ai/mcp_server.html), [SAP ADT MCP Server](https://help.sap.com/docs/abap-cloud/abap-development-tools-for-visual-studio-code/enabling-adt-mcp-server?locale=en-US), [SAP Integration Suite MCP Gateway](https://www.sap.com/products/technology-platform/integration-suite/agentic-ai.html); weitere: [vibing-steampunk](https://github.com/oisee/vibing-steampunk), [mcp-odoo](https://github.com/erpipe-org/mcp-odoo), [MCP SAP Docs](https://github.com/marianfoo/mcp-sap-docs)
- **Buchhaltung und Steuern** - offiziell: [Candis Developer MCP](https://developer.candis.io/mcp), [GetMyInvoices MCP](https://api.getmyinvoices.com/accounts/mcp-v1/public/index.php); weitere: [mcp-lexware-office](https://github.com/JannikWempe/mcp-lexware-office), [Lexware MCP Server (marselsel)](https://github.com/marselsel/Lexware-MCP-Server), [mcp-sevdesk](https://github.com/nikolausm/mcp-sevdesk)
- **E-Rechnung** - weitere: [einvoice-mcp (makririch)](https://github.com/makririch/einvoice-mcp), [einvoice-mcp (Mavengence)](https://github.com/Mavengence/einvoice-mcp), [xrechnung-mcp](https://github.com/Ozycore/xrechnung-mcp)
- **CRM und Vertrieb** - offiziell: [Salesforce DX MCP Server](https://github.com/salesforcecli/mcp), [Dataverse MCP Server](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-mcp), [Dynamics 365 Sales MCP Server](https://learn.microsoft.com/en-us/dynamics365/sales/connect-agents-to-model-context-protocol), [HubSpot Developer MCP Server](https://developers.hubspot.com/mcp), [HubSpot MCP Server (remote)](https://mcp.hubspot.com), [Pipedrive MCP Server](https://mcp.pipedrive.ai/mcp), [Salesforce Hosted MCP Servers](https://api.salesforce.com/platform/mcp/v1/); weitere: [mcp-server-salesforce](https://github.com/tsmztech/mcp-server-salesforce), [pipedrive-mcp-server (WillDent)](https://github.com/WillDent/pipedrive-mcp-server), [salesforce-mcp-server (advancedcommunities)](https://github.com/advancedcommunities/salesforce-mcp-server)
- **BI und Analytics** - offiziell: [Fabric MCP Server (lokal)](https://github.com/microsoft/mcp/tree/main/servers/Fabric.Mcp.Server), [Power BI Modeling MCP Server](https://github.com/microsoft/powerbi-modeling-mcp), [Tableau MCP](https://github.com/tableau/tableau-mcp), [Fabric Core MCP](https://api.fabric.microsoft.com/v1/mcp/core), [Fabric IQ MCP](https://fabriciq.svc.cloud.microsoft/v1/mcp/FabricIQ), [Power BI Authoring MCP (gehostet)](https://api.fabric.microsoft.com/v1/mcp/powerbi/authoring), [Qlik MCP Server](https://help.qlik.com/en-us/cloud-services/Subsystems/Hub/Content/Sense_Hub/QlikMCP/Connecting-Qlik-MCP-server.htm); weitere: [horizun-pbi-mcp](https://github.com/HorizunGroup/horizun-pbi-mcp), [qlik-mcp-server (arthurfantaci)](https://github.com/arthurfantaci/qlik-mcp-server), [SAP Datasphere MCP](https://github.com/rahulsethi/SAPDatasphereMCP)
- **Datenbanken** - offiziell: [MCP Toolbox for Databases](https://github.com/googleapis/mcp-toolbox), [SQL MCP Server (Data API builder)](https://github.com/Azure/data-api-builder), [MySQL MCP Server (Oracle)](https://github.com/oracle/mcp/tree/main/src/mysql-mcp-server), [MariaDB MCP Server](https://github.com/MariaDB/mcp), [Azure Database for PostgreSQL MCP](https://github.com/microsoft/postgres-mcp), [SQLcl MCP Server](https://docs.oracle.com/en/database/oracle/sql-developer-command-line/26.1/sqcug/sqlcl-mcp-server.html); weitere: [Postgres MCP Pro](https://github.com/crystaldba/postgres-mcp), [mcp-server-mysql (benborla)](https://github.com/benborla/mcp-server-mysql), [mysql_mcp_server (designcomputer)](https://github.com/designcomputer/mysql_mcp_server)
- **Personal (HR)** - offiziell: [Factorial MCP Server](https://mcp.factorialhr.com), [Personio MCP Server](https://support.personio.de/hc/en-us/articles/38314656674333-Personio-MCP-server-Beta-access-overview); weitere: [sf-mcp](https://github.com/aiadiguru2025/sf-mcp), [mcp-factorial](https://github.com/t4dhg/mcp-factorial), [personio-mcp-server (NikolaiGoMedicus)](https://github.com/NikolaiGoMedicus/personio-mcp-server)
- **E-Commerce** - offiziell: [Shopify Dev MCP](https://shopify.dev/docs/apps/build/ai-toolkit), [Shopify Storefront MCP](https://shopify.dev/docs/apps/build/storefront-mcp), [Shopware MCP Server](https://developer.shopware.com/docs/products/tools/mcp-server/intro.html); weitere: [shopify-mcp (GeLi2001)](https://github.com/GeLi2001/shopify-mcp), [shopware-mcp (bnymnDev)](https://github.com/bnymnDev/shopware-mcp), [billbee-mcp-server (kochfreiburg)](https://github.com/kochfreiburg/billbee-mcp-server)
- **Zusammenarbeit** - offiziell: [notion-mcp-server (lokal)](https://github.com/makenotion/notion-mcp-server), [Atlassian Rovo MCP Server](https://mcp.atlassian.com/v2/mcp), [Microsoft MCP Server for Enterprise](https://mcp.svc.cloud.microsoft/enterprise), [Microsoft 365 Server (Agent 365)](https://github.com/microsoft/mcp), [Notion MCP (gehostet)](https://mcp.notion.com/mcp), [Slack MCP Server](https://mcp.slack.com/mcp); weitere: [mcp-atlassian](https://github.com/sooperset/mcp-atlassian), [slack-mcp-server (korotovsky)](https://github.com/korotovsky/slack-mcp-server), [ms-365-mcp-server](https://github.com/Softeria/ms-365-mcp-server)
- **Logistik und Versand** - offiziell: [DHL API Assistant MCP Server](https://developer.dhl.com/dhl-api-assistant-manual-mcp-integration-guide?language_content_entity=en), [Sendcloud MCP Server](https://mcp.sendcloud.com/mcp)
- **Banking und Zahlungen** - offiziell: [Stripe MCP](https://mcp.stripe.com), [PayPal MCP Server](https://mcp.paypal.com), [Mollie MCP Server](https://mcp.mollie.com/mcp), [Qonto MCP Server](https://mcp.qonto.com/mcp)
- **Dokumente und DMS** - weitere: [AnythingMCP](https://github.com/HelpCode-ai/anythingmcp), [elo-mcp-server (LOUPZ-DE)](https://github.com/LOUPZ-DE/elo-mcp-server), [docuware-mcp](https://github.com/sniner/docuware-mcp)
- **Behörden und Open Data** - weitere: [deutsche-gesetze-mcp](https://github.com/floleuerer/deutsche-gesetze-mcp), [DejureMcp](https://github.com/halllo/DejureMcp), [germany-mcp-server](https://github.com/AiAgentKarl/germany-mcp-server)

<!-- liste:end -->

## MCP-Server für das DATEV-Format (EXTF)

Einen offiziellen MCP-Server von DATEV gibt es nicht (Stand 19.10.2026). Die DATEV-Cloud-APIs stehen auch ohne Partnerschaft offen, setzen aber Registrierung, Abonnement und für den Produktivbetrieb eine technische Prüfung durch DATEV voraus. Ohne diesen Aufwand bleibt der Dateiweg: Buchungsstapel im DATEV-Format (EXTF), die Ihre Steuerberatung oder Ihre Buchhaltung importiert. Dafür enthält dieses Repository den MCP-Server `extf-buchungsstapel-mcp` in [server/extf-buchungsstapel](server/extf-buchungsstapel/README.md):

- schreibt neue Buchungsstapel (Header-Version 700, Formatversion 13, 125 Spalten, Windows-1252, CR/LF),
- liest und prüft vorhandene EXTF-Dateien mit 83 Prüfcodes und deutschen Meldungen,
- erklärt jedes Feld und jeden Prüfcode,
- arbeitet nur in einem Arbeitsordner, überschreibt nichts und hat keinen Netzwerkzugriff.

Start mit [uv](https://docs.astral.sh/uv/):

```bash
uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel" extf-buchungsstapel-mcp --version
```

Einrichtung in Claude Code (der Arbeitsordner muss vorher existieren):

```bash
mkdir -p ~/extf-export
claude mcp add extf-buchungsstapel --env EXTF_ORDNER="$HOME/extf-export" -- \
  uvx --from "git+https://github.com/pexon-consulting/mcp-server-deutschland#subdirectory=server/extf-buchungsstapel" extf-buchungsstapel-mcp
```

Zum Server gehören über 280 automatische Tests, darunter ein Ende-zu-Ende-Test mit dem offiziellen MCP-Client, Byte-Vergleiche gegen den Beispiel-Header aus der DATEV-Formatbeschreibung und Sicherheitstests für den Arbeitsordner. Er ersetzt weder das Prüfprogramm von DATEV noch eine steuerliche Prüfung. Details: [Anleitung zum DATEV-Format (EXTF)](docs/anleitungen/datev-mcp-server.md), [Spezifikation mit Quellen](server/extf-buchungsstapel/SPEZIFIKATION.md).

## Anleitungen

Grundlagen:

- [Was ist ein MCP-Server? Model Context Protocol einfach erklärt](docs/anleitungen/was-ist-ein-mcp-server.md)
- [MCP vs. API: der Unterschied einfach erklärt](docs/anleitungen/mcp-vs-api.md)
- [MCP-Server erstellen: Tutorial mit Python und TypeScript](docs/anleitungen/mcp-server-erstellen.md)
- [MCP-Server in Claude, Cursor, VS Code und Codex einrichten](docs/anleitungen/mcp-clients-einrichten.md)

Systeme:

- [MCP-Server für das DATEV-Format: Buchungsstapel (EXTF) erstellen und prüfen](docs/anleitungen/datev-mcp-server.md)
- [MCP Buchhaltung: lexoffice, sevdesk, DATEV und weitere Server](docs/anleitungen/buchhaltung-mcp.md)
- [SAP MCP Server: offizielle Angebote, GitHub-Projekte und Architektur](docs/anleitungen/sap-mcp-server.md)
- [Business Central MCP: Dynamics 365 Business Central MCP Server einrichten](docs/anleitungen/business-central-mcp.md)
- [Power BI MCP Server: Authoring, Fabric IQ und Einrichtung](docs/anleitungen/power-bi-mcp.md)
- [HubSpot MCP Server: Remote-MCP, Developer-MCP und Einrichtung](docs/anleitungen/hubspot-mcp.md)
- [Postgres MCP Server: Postgres MCP Pro, Docker und sichere Leserolle](docs/anleitungen/postgres-mcp.md)

Sicherheit und Datenschutz:

- [MCP Sicherheit: Risiken, Prompt Injection, Tool Poisoning und Checkliste](docs/anleitungen/mcp-sicherheit.md)
- [MCP und DSGVO: Datenschutz bei MCP-Servern im Unternehmen](docs/anleitungen/mcp-dsgvo.md)

## Beispiel: eigener MCP-Server in Python und TypeScript

Unter [beispiele/](beispiele/) liegt derselbe kleine Server zweimal: "Feiertage und Arbeitstage in Deutschland", einmal mit dem Python-SDK (`mcp` 2.3) und einmal mit dem TypeScript-SDK (`@modelcontextprotocol/server` 2.3). Beide sind getestet und dienen als Vorlage für eigene Server. Die Schritte erklärt [MCP-Server erstellen](docs/anleitungen/mcp-server-erstellen.md).

## Was dieses Repository nicht ist

- **Keine Empfehlung einzelner Server.** Ein Eintrag in der Liste heißt nicht, dass wir den Server getestet oder geprüft haben. Prüfen Sie Herkunft, Rechte und Code vor dem Einsatz, siehe [Checkliste](docs/liste.md#so-prüfen-sie-einen-mcp-server-vor-dem-einsatz).
- **Kein Hersteller-Projekt.** DATEV, SAP, Microsoft, HubSpot, Lexware, sevdesk und die anderen Hersteller haben dieses Repository weder geprüft noch freigegeben.
- **Keine Rechts- oder Steuerberatung.** Siehe [Hinweise](#hinweise-und-lizenz).

## Häufige Fragen

**Gibt es einen offiziellen DATEV MCP Server?**
Nein, Stand 19.10.2026 nicht. Es gibt DATEV-Schnittstellen (Cloud-APIs mit Freigabeprozess, DATEVconnect lokal) und einige Community-Server. Der Server in diesem Repository arbeitet mit Dateien im DATEV-Format, ohne Verbindung zu DATEV.

**Welche MCP-Server sind offiziell?**
In der [Liste](docs/liste.md) ist jeder Eintrag als *offiziell*, *Community* oder *kommerziell* markiert. Offiziell heißt: vom Hersteller des Systems veröffentlicht, belegt mit einer Quelle beim Hersteller.

**Gehen meine Daten an das Sprachmodell?**
Ja. Was ein MCP-Server zurückgibt, landet im Kontext des KI-Clients und damit beim Anbieter des Sprachmodells, es sei denn, das Modell läuft bei Ihnen. Das gilt auch für lokale Server. Details in [MCP und DSGVO](docs/anleitungen/mcp-dsgvo.md).

**Was ist der Unterschied zwischen MCP und einer REST-API?**
Eine REST-API ist für Programme gebaut, MCP für KI-Clients, die Werkzeuge zur Laufzeit entdecken. Unter dem MCP-Server arbeitet meist dieselbe API. Siehe [MCP vs. API](docs/anleitungen/mcp-vs-api.md).

**Welche Protokollversion gilt?**
Die aktuelle Spezifikation ist 2026-07-28. Viele Server sprechen noch 2025-11-25 oder älter; die Clients handeln die Version aus. Mehr in [Was ist ein MCP-Server?](docs/anleitungen/was-ist-ein-mcp-server.md).

## Mitmachen

Fehlt ein Server, ist ein Eintrag veraltet oder falsch? Schlagen Sie die Änderung in [daten/server.yaml](daten/server.yaml) per Pull Request vor und führen Sie `python3 scripts/liste_bauen.py` aus. Details stehen in [CONTRIBUTING.md](CONTRIBUTING.md). Sicherheitsprobleme bitte nicht öffentlich melden, sondern wie in [SECURITY.md](SECURITY.md) beschrieben.

## Hinweise und Lizenz

- **Technisches Hilfswerk, keine Beratung.** Dieses Repository stellt Software und technische Informationen bereit, nach Stand 19.10.2026 und ohne Gewähr für Vollständigkeit und Richtigkeit. Es ersetzt keine fachliche Prüfung und keine Rechts-, Steuer- oder Datenschutzberatung. Die Autoren sind keine Rechtsanwälte, Steuerberater oder Datenschutzbeauftragten. Sie bleiben für den Einsatz der Server in Ihrem Unternehmen verantwortlich, auch datenschutzrechtlich.
- **Keine Haftung für KI-Ausgaben.** Was ein KI-Assistent mit diesen Werkzeugen erzeugt, vorschlägt oder erklärt, stammt vom Sprachmodell und nicht von uns. Solche Ausgaben können falsch, unvollständig oder erfunden sein. Prüfen Sie sie, bevor Sie sie verwenden, versenden oder importieren. Für den Output von KI-Systemen übernehmen wir keine Haftung.
- **Keine Hilfeleistung in Steuersachen.** Die Autoren erbringen keine Hilfeleistung in Steuersachen im Sinne des Steuerberatungsgesetzes. Ob und wie Buchungen steuerlich richtig sind, klären Sie mit Ihrer Steuerberatung.
- **Marken.** DATEV ist eine Marke der DATEV eG; dieses Projekt ist kein Produkt der DATEV eG und nicht von ihr geprüft oder freigegeben. Alle anderen Produkt- und Firmennamen sind Marken ihrer Inhaber. Es besteht keine Verbindung zu den genannten Herstellern und keine Empfehlung durch sie.
- **Haftung.** Die Software und die Texte werden unentgeltlich und ohne Zusicherung bestimmter Eigenschaften bereitgestellt. Soweit gesetzlich zulässig, ist die Haftung ausgeschlossen. Unberührt bleibt die Haftung für Vorsatz und grobe Fahrlässigkeit, für Schäden aus der Verletzung des Lebens, des Körpers oder der Gesundheit, für arglistig verschwiegene Mängel und nach dem Produkthaftungsgesetz. Prüfen Sie jede erzeugte Datei, bevor Sie sie weitergeben oder importieren.
- **Lizenz.** MIT, siehe [LICENSE](LICENSE). Lizenzen der verlinkten Server gelten jeweils für sich, siehe [NOTICE](NOTICE).

Verwandte Repositories: [e-rechnung](https://github.com/pexon-consulting/e-rechnung) (XRechnung und ZUGFeRD prüfen und erstellen, mit eigenem MCP-Server), [litellm-open-webui](https://github.com/pexon-consulting/litellm-open-webui) (selbst gehostetes LLM-Gateway), [claude-code-best-practices](https://github.com/pexon-consulting/claude-code-best-practices).

Gepflegt von der Pexon Consulting GmbH. Wenn Sie MCP-Server in Ihrem Unternehmen anbinden möchten, finden Sie unser Angebot unter [Model Context Protocol (MCP) Integration](https://pexon-consulting.de/ki-beratung/ki-integration/model-context-protocol-mcp/).

Anbieterkennzeichnung: [Impressum](https://pexon-consulting.de/impressum/) · [Datenschutz](https://pexon-consulting.de/datenschutz/)
