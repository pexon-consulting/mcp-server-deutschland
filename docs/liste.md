# MCP-Server-Liste für deutsche Geschäftssysteme

Diese Liste sammelt MCP-Server für Geschäftssysteme, die in Deutschland verbreitet sind: ERP, Buchhaltung, E-Rechnung, CRM, BI, Datenbanken, HR, E-Commerce, Zusammenarbeit, Versand, Zahlungen, Dokumentenmanagement und offene Daten von Behörden. Je Kategorie stehen zuerst die Server der Hersteller, danach Community- und kommerzielle Server.

Grundlagen: [Was ist ein MCP-Server?](anleitungen/was-ist-ein-mcp-server.md). Vor dem Einsatz: [MCP Sicherheit](anleitungen/mcp-sicherheit.md) und [MCP und DSGVO](anleitungen/mcp-dsgvo.md). Übersicht aller Anleitungen in der [README](../README.md#anleitungen).

**Stand:** 19.10.2026. 138 Einträge, davon 48 offiziell, 88 Community und 2 kommerziell. Die Liste wird aus `daten/server.yaml` erzeugt; Änderungen bitte dort vornehmen.

> **Hinweis:** Technisches Hilfswerk, keine Beratung. Technische Informationen nach Stand 19.10.2026, ohne Gewähr für Vollständigkeit und Richtigkeit. Keine Rechts-, Steuer- oder Datenschutzberatung; die Autoren sind keine Rechtsanwälte, Steuerberater oder Datenschutzbeauftragten. Was ein KI-Assistent mit diesen Servern erzeugt, stammt vom Sprachmodell und nicht von uns; für den Output von KI-Systemen übernehmen wir keine Haftung. Prüfen Sie jede Ausgabe, bevor Sie sie verwenden. Produktnamen sind Marken ihrer Inhaber; es besteht keine Verbindung zu den genannten Herstellern.

## Legende

- **Typ:** *offiziell* = vom Hersteller des Systems veröffentlicht. *Community* = von Dritten, meist Open Source. *kommerziell* = Angebot eines Drittanbieters, das Kosten verursachen kann.
- **Transport:** *stdio* = lokaler Prozess. *HTTP* = Streamable HTTP, Sie betreiben den Server selbst. *stdio und HTTP* = beides möglich. *gehostet* = der Anbieter betreibt den Server.
- **Zugriff:** *lesen* = nur lesende Tools, mindestens in der Standardeinstellung. *lesen und schreiben* = der Server kann Daten ändern, oft abschaltbar.
- **Lizenz:** SPDX-Kennung des Repositorys. *proprietär* = Dienst oder Software des Herstellers. *keine* = keine Lizenzdatei im Repository. *unklar* = GitHub erkennt die Lizenz nicht. SSPL, Elastic, BUSL, FSL oder CC-BY-NC sind keine Open-Source-Lizenzen und können den Einsatz im Unternehmen einschränken.
- **Reihenfolge:** offizielle Server zuerst, danach nach GitHub-Sternen. Sterne zeigen Bekanntheit, nicht Qualität oder Sicherheit.
- **Hinweis:** Archivierte Repositorys und Repositorys ohne Änderung seit mehr als zwölf Monaten sind dort vermerkt.

## Inhalt

- [ERP](#erp) (27)
- [Buchhaltung und Steuern](#buchhaltung-und-steuern) (18)
- [E-Rechnung](#e-rechnung) (6)
- [CRM und Vertrieb](#crm-und-vertrieb) (13)
- [BI und Analytics](#bi-und-analytics) (10)
- [Datenbanken](#datenbanken) (16)
- [Personal (HR)](#personal-hr) (6)
- [E-Commerce](#e-commerce) (8)
- [Zusammenarbeit](#zusammenarbeit) (14)
- [Logistik und Versand](#logistik-und-versand) (2)
- [Banking und Zahlungen](#banking-und-zahlungen) (4)
- [Dokumente und DMS](#dokumente-und-dms) (4)
- [Behörden und Open Data](#behörden-und-open-data) (10)
- [So prüfen Sie einen MCP-Server vor dem Einsatz](#so-prüfen-sie-einen-mcp-server-vor-dem-einsatz)
- [Eintrag vorschlagen](#eintrag-vorschlagen)

## ERP

SAP veröffentlicht vor allem Entwicklungswerkzeuge (ABAP, CAP, Fiori, UI5). Für den Zugriff auf Geschäftsdaten aus S/4HANA ist der offizielle Weg die Integration Suite. Eine ausführlichere SAP-Übersicht pflegt marianfoo/sap-ai-mcp-servers.

Für weclapp und Xentral haben wir keinen Server des Herstellers gefunden. JTL bietet bisher nur einen Dokumentations-Server an.

Anleitung: [SAP MCP Server](anleitungen/sap-mcp-server.md), [Business Central MCP](anleitungen/business-central-mcp.md)

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [SAP Fiori MCP Server](https://github.com/SAP/open-ux-tools/tree/main/packages/fiori-mcp-server)<br>SAP Fiori | offiziell | stdio | keine | lesen und schreiben | Apache-2.0 | Entwicklungswerkzeug. Erzeugt und ändert Fiori-Elements-Anwendungen im lokalen Projekt. Sterne und Aktivität beziehen sich auf das Monorepo open-ux-tools. |
| [SAP CAP MCP Server](https://github.com/cap-js/mcp-server)<br>SAP Cloud Application Programming Model | offiziell | stdio | keine | lesen | Apache-2.0 | Entwicklungswerkzeug. Durchsucht das CDS-Modell des lokalen Projekts und die CAP-Dokumentation. |
| [UI5 MCP Server](https://github.com/UI5/mcp-server)<br>SAPUI5 / OpenUI5 | offiziell | stdio | keine | lesen und schreiben | Apache-2.0 | Entwicklungswerkzeug. Legt UI5-Anwendungen und Integration Cards an und liefert API-Referenz und Linter-Ergebnisse. |
| [Business Central MCP Server](https://mcp.businesscentral.dynamics.com)<br>Microsoft Dynamics 365 Business Central | offiziell | gehostet | OAuth (Microsoft Entra ID) | lesen und schreiben | proprietär | Allgemein verfügbar seit 01.04.2026, Data Query Tools in Vorschau. Welche APIs freigegeben sind und ob geschrieben werden darf, legt eine Konfiguration in Business Central fest. Firmennamen mit Umlauten werden im Header Base64-kodiert. |
| [Dynamics 365 ERP MCP Server](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/copilot/copilot-mcp)<br>Microsoft Dynamics 365 Finance und Supply Chain Management | offiziell | gehostet | OAuth (Microsoft Entra ID), Client muss unter "Allowed MCP clients" freigegeben sein | lesen und schreiben | proprietär | Ab Version 10.0.47 (oder 10.0.46 PQU-2, 10.0.45 PQU-7), Umgebungen ab Tier 2. Data-, Form- und Action-Tools. Den älteren statischen Server hat Microsoft zum 01.10.2026 abgekündigt; die Doku formulierte das am 19.10.2026 noch als Ankündigung. |
| [JTL Developer MCP](https://developer.jtl-software.com/mcp)<br>JTL-Wawi / JTL-Plattform | offiziell | gehostet | keine | lesen | proprietär | Nur Entwicklerdokumentation, kein Zugriff auf ERP-Daten. Einen MCP-Zugang zum JTL-ERP kündigt JTL als offene Beta ab November 2026 an, Voraussetzung ERP 2.2 oder neuer. Ankündigung: https://www.jtl-software.com/en/ai/juno |
| [Odoo MCP Server (AI-App)](https://www.odoo.com/documentation/20.0/applications/productivity/ai/mcp_server.html)<br>Odoo | offiziell | HTTP | OAuth (CIMD oder DCR, empfohlen) oder API-Schlüssel mit MCP-Scope | lesen und schreiben | proprietär | Teil der AI-App von Odoo Enterprise ab Version 20.0 bzw. Odoo Online saas-19.4, nicht in 19.0. Endpunkt unter /mcp der eigenen Datenbank. 'Readonly Tool' ist nur ein Hinweis an den Client; die Rechte bestimmt der Odoo-Benutzer. |
| [SAP ADT MCP Server](https://help.sap.com/docs/abap-cloud/abap-development-tools-for-visual-studio-code/enabling-adt-mcp-server?locale=en-US)<br>SAP ABAP (ABAP Development Tools) | offiziell | HTTP | Token aus den ADT-Einstellungen | lesen und schreiben | proprietär | Entwicklungswerkzeug. In Eclipse ab ADT 3.60 lokal unter localhost, Standardport 2234; Variante für VS Code laut SAP-Hilfe. Die ADT-Tools in VS Code setzen eine Joule-Lizenz voraus. |
| [SAP Integration Suite MCP Gateway](https://www.sap.com/products/technology-platform/integration-suite/agentic-ai.html)<br>SAP S/4HANA und SAP-APIs | offiziell | gehostet | OAuth 2.0 / OIDC | lesen und schreiben | proprietär | Macht SAP-APIs, iFlows und OpenAPI-Spezifikationen als MCP-Tools verfügbar. On-Premise-Systeme über den Cloud Connector. Teil der SAP Integration Suite. Protokoll 2025-11-25, 2026-07-28. |
| [vibing-steampunk](https://github.com/oisee/vibing-steampunk)<br>SAP ABAP (ADT) | Community | stdio und HTTP | SAP-Benutzer (Basic) oder Zertifikat | lesen und schreiben | MIT | ABAP-Entwicklung über die ADT-REST-API, inklusive Debugging und Tests. Einzelne Binärdatei in Go. |
| [mcp-odoo](https://github.com/erpipe-org/mcp-odoo)<br>Odoo | Community | stdio und HTTP | Odoo-Benutzer oder API-Schlüssel | lesen und schreiben | MIT | Über XML-RPC für ältere Odoo-Versionen nutzbar. Schreibzugriffe lassen sich absichern. Früher unter tuanle96/mcp-odoo. |
| [MCP SAP Docs](https://github.com/marianfoo/mcp-sap-docs)<br>SAP-Dokumentation | Community | stdio und HTTP | keine | lesen | Apache-2.0 | Suche in SAP-Hilfe, Community und Beispielen; zusätzlich als öffentlicher Server ohne Anmeldung betrieben. Der Autor pflegt auch die Übersicht marianfoo/sap-ai-mcp-servers. |
| [ARC-1](https://github.com/arc-mcp/arc-1)<br>SAP ABAP (ADT) | Community | stdio und HTTP | SAP-Benutzer oder BTP-OAuth | lesen und schreiben | MIT | Standardmäßig nur lesend; Schreibrechte werden einzeln über SAP_ALLOW-Schalter und Paketgrenzen freigegeben. |
| [mcp-abap-adt](https://github.com/mario-andreschak/mcp-abap-adt)<br>SAP ABAP (ADT) | Community | stdio | SAP-Benutzer (Basic) | lesen | MIT | Liest ABAP-Quelltext, Tabellenstrukturen und Pakete über ADT. Sechzehn Tools, alle lesend. |
| [OData MCP Bridge (Go)](https://github.com/oisee/odata_mcp_go)<br>SAP OData-Dienste | Community | stdio und HTTP | Basic, Cookie oder durchgereichte Header | lesen und schreiben | MIT | Erzeugt Tools aus beliebigen OData-v2/v4-Diensten. Schalter --read-only verfügbar. |
| [mcp-sap-gui](https://github.com/mario-andreschak/mcp-sap-gui)<br>SAP GUI für Windows | Community | stdio | SAP-GUI-Anmeldung | lesen und schreiben | MIT | Steuert SAP GUI per Scripting; nur Windows, SAP-GUI-Scripting muss serverseitig erlaubt sein. |
| [BTP SAP OData to MCP Server](https://github.com/lemaiwo/btp-sap-odata-to-mcp-server)<br>SAP S/4HANA über SAP BTP | Community | HTTP | XSUAA / BTP-Destinations | lesen und schreiben | MIT | Läuft auf SAP BTP Cloud Foundry und erkennt OData-Dienste über BTP-Destinations. |
| [odoo-mcp-pro](https://github.com/pantalytics/odoo-mcp-pro)<br>Odoo | Community | stdio und HTTP | API-Schlüssel oder OAuth | lesen und schreiben | Elastic-2.0 | Elastic License 2.0, keine OSI-Lizenz; Betrieb als Dienst für Dritte untersagt. Der Anbieter bietet zusätzlich eine gehostete Variante an. |
| [Business Central MCP (WebUI)](https://github.com/SShadowS/business-central-mcp)<br>Microsoft Dynamics 365 Business Central | Community | stdio und HTTP | BC-Benutzer (On-Premise) oder Entra ID | lesen und schreiben | MIT | Arbeitet über das Protokoll des BC-Webclients statt über die Standard-API; Massenabfragen über OData API v2.0. |
| [SAP Business One MCP Server by CData](https://github.com/CDataSoftware/sap-business-one-mcp-server-by-cdata)<br>SAP Business One | kommerziell | stdio | Zugangsdaten im CData-JDBC-Treiber | lesen | MIT | Letzte Änderung im Repository am 18.10.2025. Der Server selbst ist MIT-lizenziert und nur lesend, benötigt aber den kostenpflichtigen CData-JDBC-Treiber. |
| [sapgui.mcp](https://github.com/Hochfrequenz/sapgui.mcp)<br>SAP GUI für Windows | Community | stdio und HTTP | SAP-GUI-Anmeldung | lesen und schreiben | MIT | SAP-GUI-Automatisierung über Scripting; nur Windows. |
| [odoo-mcp-19](https://github.com/AlanOgic/odoo-mcp-19)<br>Odoo 19 | Community | stdio und HTTP | API-Schlüssel | lesen und schreiben | MIT | Nutzt die JSON-2-API von Odoo 19. Schreibende Aufrufe laufen über eine Freigabe; eine reine Leserolle ist einstellbar. |
| [weclapp MCP](https://github.com/codelev/weclapp-mcp)<br>weclapp | Community | stdio | weclapp-API-Token | lesen und schreiben | SSPL-1.0 | SSPL, keine OSI-Lizenz. Verwaltet Firmen und Personen (Parteien) in weclapp. |
| [xentral-mcp (mjmirza)](https://github.com/mjmirza/xentral-mcp)<br>Xentral | Community | stdio und HTTP | Xentral-API-Token | lesen und schreiben | LicenseRef-OpenRoots-Agent-2.3 | Archiviert. Eigene Lizenz, vor dem Einsatz prüfen. Standardmäßig nur lesend, Schreibzugriffe einzeln freischaltbar. |
| [weclapp MCP Server (kochfreiburg)](https://github.com/kochfreiburg/weclapp-mcp-server)<br>weclapp | Community | HTTP | weclapp-API-Token | lesen und schreiben | AGPL-3.0 | Betrieb als Container vorgesehen. |
| [Xentral MCP Server (kochfreiburg)](https://github.com/kochfreiburg/xentral-mcp-server)<br>Xentral | Community | HTTP | Xentral-API-Token | lesen und schreiben | AGPL-3.0 | Betrieb als Container vorgesehen. |
| [xentral-mcp (matthiashuebner)](https://github.com/matthiashuebner/xentral-mcp)<br>Xentral | Community | stdio | Xentral-API-Token | lesen und schreiben | keine | Zugriff über die Xentral-API. |

## Buchhaltung und Steuern

Für DATEV, Lexware Office, sevdesk und BuchhaltungsButler haben wir keinen Server des Herstellers gefunden; alle Einträge dazu sind Community-Projekte.

**ELSTER:** Die Finanzverwaltung bietet keinen MCP-Server an. Die offizielle Schnittstelle für Übermittlungen ist die Bibliothek ERiC, für die sich Hersteller registrieren müssen. Die beiden gelisteten ELSTER-Server arbeiten stattdessen mit dem Webportal. Ob das mit den Nutzungsbedingungen von ELSTER vereinbar ist, klären Sie vor dem Einsatz.

Anleitung: [MCP Buchhaltung](anleitungen/buchhaltung-mcp.md), [MCP-Server für das DATEV-Format (EXTF)](anleitungen/datev-mcp-server.md)

> Die Autoren erbringen keine Hilfeleistung in Steuersachen im Sinne des Steuerberatungsgesetzes. Ob und wie Buchungen steuerlich richtig sind, klären Sie mit Ihrer Steuerberatung. DATEV ist eine Marke der DATEV eG; dieses Projekt ist kein Produkt der DATEV eG und nicht von ihr geprüft oder freigegeben.

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [Candis Developer MCP](https://developer.candis.io/mcp)<br>Candis | offiziell | gehostet | keine | lesen | proprietär | Nur API-Dokumentation für Entwickler, kein Zugriff auf Belegdaten. |
| [GetMyInvoices MCP](https://api.getmyinvoices.com/accounts/mcp-v1/public/index.php)<br>GetMyInvoices | offiziell | gehostet | GetMyInvoices-Konto | lesen | proprietär | Zugriff auf Belege und Rechnungen im GetMyInvoices-Konto, nur lesend. |
| [mcp-lexware-office](https://github.com/JannikWempe/mcp-lexware-office)<br>Lexware Office (ehemals lexoffice) | Community | stdio | Lexware-API-Schlüssel | lesen und schreiben | MIT | Standardmäßig nur lesend; Schreiben erst nach Freigabe per Umgebungsvariable. Zwei Tools (search, execute) statt eines Tools je Endpunkt. |
| [Lexware MCP Server (marselsel)](https://github.com/marselsel/Lexware-MCP-Server)<br>Lexware Office (ehemals lexoffice) | Community | stdio und HTTP | Lexware-API-Schlüssel, für HTTP zusätzlich OAuth 2.1 | lesen und schreiben | MIT | Belege werden als Entwurf angelegt; LEXWARE_READ_ONLY=true erzwingt reinen Lesezugriff. |
| [mcp-sevdesk](https://github.com/nikolausm/mcp-sevdesk)<br>sevdesk | Community | stdio | sevdesk-API-Token | lesen und schreiben | keine | Legt unter anderem Kontakte, Artikel und Transaktionen an. |
| [elster-mcp-server (lukasschwarz)](https://github.com/lukasschwarz/elster-mcp-server)<br>ELSTER | Community | stdio | ELSTER-Zertifikat | lesen und schreiben | MIT | Kein Angebot der Finanzverwaltung. Steuert das ELSTER-Webportal per Puppeteer statt über ERiC; das README weist darauf hin, dass die Nutzungsbedingungen automatisierte Zugriffe einschränken können. Abruf- und Postfach-Tools sind lesend. |
| [Buchhaltungsbutler-MCP (ohneben)](https://github.com/ohneben/Buchhaltungsbutler-MCP)<br>BuchhaltungsButler | Community | stdio und HTTP | BuchhaltungsButler-API-Schlüssel | lesen und schreiben | MIT | Tools sind nach lesend, schreibend und destruktiv gekennzeichnet (MCP-Annotationen). Dokumentation auf Deutsch. |
| [lexware-mcp-server (lazyants)](https://github.com/lazyants/lexware-mcp-server)<br>Lexware Office (ehemals lexoffice) | Community | stdio | Lexware-API-Schlüssel | lesen und schreiben | FSL-1.1-MIT | Functional Source License, erst nach zwei Jahren MIT. Zugriff über die Lexware-Office-API. |
| [sevdesk-mcp (codestra)](https://github.com/codestra/sevdesk-mcp)<br>sevdesk | Community | stdio | sevdesk-API-Token | lesen und schreiben | keine | Zugriff über die sevdesk-API. |
| [sevdesk-mcp (joosthel)](https://github.com/joosthel/sevdesk-mcp)<br>sevdesk | Community | stdio und HTTP | sevdesk-API-Token | lesen und schreiben | MIT | Kennzeichnet lesende und schreibende Tools getrennt. |
| [datev-mcp-server](https://github.com/ppronobis/datev-mcp-server)<br>DATEV | Community | stdio | keine | lesen | MIT | Kein Produkt der DATEV eG. Wertet lokale Buchungsdaten im DATEV-Format (EXTF) aus, zum Beispiel Salden und offene Posten; keine Verbindung zu DATEV. |
| [datev-mcp](https://github.com/BadRix90/datev-mcp)<br>DATEV | Community | stdio und HTTP | DATEV-OAuth | lesen und schreiben | MIT | Kein Produkt der DATEV eG. Für die DATEV-APIs ist eine Registrierung im DATEV-Entwicklerportal nötig. |
| [elster-mcp-server (Infraviored)](https://github.com/Infraviored/elster-mcp-server)<br>ELSTER | Community | stdio | ELSTER-Zertifikat | lesen und schreiben | MIT | Kein Angebot der Finanzverwaltung. Füllt Formulare im ELSTER-Webportal aus und führt die Portal-Prüfungen aus; das Absenden bleibt beim Menschen im Browser. |
| [buchhaltungsbutler-mcp (mrvnklm)](https://github.com/mrvnklm/buchhaltungsbutler-mcp)<br>BuchhaltungsButler | Community | stdio | BuchhaltungsButler-API-Schlüssel | lesen und schreiben | MIT | Legt auch Bankkonten und Transaktionen an. |
| [belege.ai MCP](https://belege.ai/mcp-buchhaltung)<br>belege.ai | kommerziell | gehostet | belege.ai-Konto | lesen | proprietär | Gehosteter Dienst rund um Belege und Buchhaltungsdaten, nur lesend. |
| [buchhaltungsbutler-mcp (dennismenken)](https://github.com/dennismenken/buchhaltungsbutler-mcp)<br>BuchhaltungsButler | Community | stdio und HTTP | BuchhaltungsButler-API-Schlüssel | lesen und schreiben | MIT | Lese- und Schreibmodus getrennt einstellbar. |
| [datev-extf-mcp](https://github.com/seamless-engineering/datev-extf-mcp)<br>DATEV-Format (EXTF) | Community | stdio | keine | lesen und schreiben | MIT | Arbeitet nur mit Dateien. Validiert und schreibt Buchungsstapel im DATEV-Format (EXTF), ohne Verbindung zu DATEV. |
| [lexware-mcp-community](https://github.com/lepatrick/lexware-mcp-community)<br>Lexware Office (ehemals lexoffice) | Community | stdio | Lexware-API-Schlüssel | lesen und schreiben | AGPL-3.0 | Läuft nur lokal über stdio, ohne HTTP-Port und ohne OAuth. Dokumentation auf Deutsch. |

## E-Rechnung

Einen Server von KoSIT oder FeRD haben wir nicht gefunden. Achten Sie darauf, ob ein Server lokal validiert oder die Rechnung an einen externen Dienst schickt: Rechnungen enthalten personenbezogene Daten und Geschäftsdaten.

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [einvoice-mcp (makririch)](https://github.com/makririch/einvoice-mcp)<br>XRechnung | Community | stdio | keine | lesen und schreiben | keine | Erzeugt XRechnung im UBL-Format aus strukturierten Daten. |
| [einvoice-mcp (Mavengence)](https://github.com/Mavengence/einvoice-mcp)<br>XRechnung und ZUGFeRD | Community | stdio und HTTP | keine | lesen und schreiben | MIT | Erzeugt und validiert E-Rechnungen; Betrieb auch als Container. |
| [xrechnung-mcp](https://github.com/Ozycore/xrechnung-mcp)<br>XRechnung | Community | stdio | keine | lesen und schreiben | MIT | Das Repository spiegelt den Quelltext des npm-Pakets. |
| [e-rechnung (erechnung-mcp)](https://github.com/pexon-consulting/e-rechnung)<br>XRechnung und ZUGFeRD | Community | stdio | keine | lesen und schreiben | MIT | Projekt der Maintainer dieser Liste. Python-Bibliothek mit MCP-Server als Extra (erechnung-mcp). Liest und validiert XRechnung und ZUGFeRD mit den KoSIT-Regeln ohne Java und erzeugt Rechnungsdateien lokal. |
| [einvoicechecker-mcp](https://github.com/vpukhalskyi/einvoicechecker-mcp)<br>XRechnung und ZUGFeRD | Community | stdio und HTTP | API-Schlüssel für den gehosteten Dienst | lesen | MIT | Validierung von E-Rechnungen. Zusätzlich als gehosteter Endpunkt einvoicechecker.com/v1/mcp; Rechnungsdaten gehen dann an einen externen Dienst. |
| [eleata-einvoice-mcp](https://github.com/eleata/eleata-einvoice-mcp)<br>E-Rechnung (EN 16931) | Community | stdio | API-Schlüssel für den gehosteten Dienst | lesen | keine | Validiert über die gehostete eleata-API, Rechnungsdaten gehen an diesen Dienst; Fehlercode-Referenz offline. Früher unter hernaninverso/eleata-einvoice-mcp. |

## CRM und Vertrieb

HubSpot, Salesforce, Pipedrive und Microsoft betreiben eigene, gehostete Server. Community-Server sind vor allem für lokale Setups und abweichende Rechtekonzepte verbreitet.

Anleitung: [HubSpot MCP Server](anleitungen/hubspot-mcp.md)

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [Salesforce DX MCP Server](https://github.com/salesforcecli/mcp)<br>Salesforce (Entwicklung) | offiziell | stdio | Salesforce-CLI-Anmeldung | lesen und schreiben | Apache-2.0 | Entwicklungswerkzeug. Laut Salesforce Supportende am 02.11.2026. |
| [Dataverse MCP Server](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-mcp)<br>Microsoft Dataverse / Dynamics 365 | offiziell | stdio und HTTP | OAuth (Microsoft Entra ID) | lesen und schreiben | proprietär | Endpunkt /api/mcp der eigenen Umgebung, lokal über den Proxy @microsoft/dataverse. Außerhalb von Copilot Studio werden seit 15.12.2025 Copilot Credits berechnet. |
| [Dynamics 365 Sales MCP Server](https://learn.microsoft.com/en-us/dynamics365/sales/connect-agents-to-model-context-protocol)<br>Microsoft Dynamics 365 Sales | offiziell | gehostet | OAuth (Microsoft Entra ID) | lesen und schreiben | proprietär | Läuft über Agent 365; Endpunkt je Umgebung. |
| [HubSpot Developer MCP Server](https://developers.hubspot.com/mcp)<br>HubSpot Developer Platform | offiziell | stdio | HubSpot-CLI-Anmeldung | lesen und schreiben | proprietär | Entwicklungswerkzeug über die HubSpot-CLI (hs mcp setup), nicht für CRM-Daten. Das ältere npm-Paket @hubspot/mcp-server endet bei Version 0.4.0. |
| [HubSpot MCP Server (remote)](https://mcp.hubspot.com)<br>HubSpot | offiziell | gehostet | OAuth mit PKCE über einen MCP Connector im HubSpot-Account (Client-ID und Secret), ohne DCR | lesen und schreiben | proprietär | Kein Löschen von Datensätzen. Mit aktivierter Einstellung für sensible Daten sind Aktivitäten und Konversationen gesperrt. |
| [Pipedrive MCP Server](https://mcp.pipedrive.ai/mcp)<br>Pipedrive | offiziell | gehostet | OAuth | lesen und schreiben | proprietär | Seit 30.06.2026 in allen Tarifen verfügbar. |
| [Salesforce Hosted MCP Servers](https://api.salesforce.com/platform/mcp/v1/)<br>Salesforce | offiziell | gehostet | OAuth mit PKCE über External Client App | lesen und schreiben | proprietär | Allgemein verfügbar seit 29.04.2026, ab Enterprise Edition. |
| [mcp-server-salesforce](https://github.com/tsmztech/mcp-server-salesforce)<br>Salesforce | Community | stdio | Benutzer/Token oder OAuth | lesen und schreiben | MIT | Abfragen, Datensätze und Metadaten bis hin zu Apex. |
| [pipedrive-mcp-server (WillDent)](https://github.com/WillDent/pipedrive-mcp-server)<br>Pipedrive | Community | stdio und HTTP | Pipedrive-API-Token | lesen | MIT | Standardmäßig nur lesend; zwei eng begrenzte Schreib-Tools optional. |
| [salesforce-mcp-server (advancedcommunities)](https://github.com/advancedcommunities/salesforce-mcp-server)<br>Salesforce | Community | stdio | Salesforce-CLI-Anmeldung | lesen und schreiben | MIT | Nur-Lese-Modus je Org einstellbar. |
| [hubspot-mcp (shinzo-labs)](https://github.com/shinzo-labs/hubspot-mcp)<br>HubSpot | Community | stdio und HTTP | Private-App-Token | lesen und schreiben | MIT | Deckt CRM-Objekte, Zuordnungen und Batch-Operationen ab. |
| [pipedrive-mcp-server (ckalima)](https://github.com/ckalima/pipedrive-mcp-server)<br>Pipedrive | Community | stdio und HTTP | Pipedrive-API-Token | lesen und schreiben | MIT | Umfangreiche Schreib-Tools; Nur-Lese-Modus verfügbar. |
| [hubspot-mcp (promptmetrics)](https://github.com/promptmetrics/hubspot-mcp)<br>HubSpot | Community | stdio | OAuth oder Private-App-Token | lesen und schreiben | MIT | Ordner skills/ unter Apache-2.0. Jeder Schreibzugriff braucht eine Freigabe und wird mit Rücksprungpunkt protokolliert. |

## BI und Analytics

Bei Power BI und Fabric gibt es mehrere offizielle Server mit unterschiedlichem Zweck: Modellierung, Abfragen und Verwaltung.

Anleitung: [Power BI MCP Server](anleitungen/power-bi-mcp.md)

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [Fabric MCP Server (lokal)](https://github.com/microsoft/mcp/tree/main/servers/Fabric.Mcp.Server)<br>Microsoft Fabric | offiziell | stdio | Microsoft Entra ID | lesen und schreiben | MIT | Öffentliche Vorschau für Entwickler. Sterne und Aktivität beziehen sich auf das Monorepo microsoft/mcp. |
| [Power BI Modeling MCP Server](https://github.com/microsoft/powerbi-modeling-mcp)<br>Microsoft Power BI | offiziell | stdio | Microsoft Entra ID | lesen und schreiben | MIT | Bearbeitet semantische Modelle; Schalter --readonly verfügbar. Lizenzfeld MIT, das README verlangt zusätzlich die Annahme einer EULA. Nicht für macOS. Microsoft nennt ihn inzwischen Power BI Authoring MCP Server (lokal); das Paket heißt weiter powerbi-modeling-mcp. |
| [Tableau MCP](https://github.com/tableau/tableau-mcp)<br>Tableau | offiziell | stdio und HTTP | Personal Access Token oder OAuth | lesen | Apache-2.0 | Abfragen auf veröffentlichte Datenquellen und Inhalte von Tableau Cloud und Server. |
| [Fabric Core MCP](https://api.fabric.microsoft.com/v1/mcp/core)<br>Microsoft Fabric | offiziell | gehostet | OAuth (Microsoft Entra ID) | lesen und schreiben | proprietär | Verwaltung von Arbeitsbereichen und Elementen über die Fabric-REST-API. |
| [Fabric IQ MCP](https://fabriciq.svc.cloud.microsoft/v1/mcp/FabricIQ)<br>Microsoft Fabric / Power BI | offiziell | gehostet | OAuth (Microsoft Entra ID) | lesen | proprietär | Abfragen auf Power-BI-Modelle, nur lesend. Die Abfragegenerierung braucht eine Copilot-Lizenz. |
| [Power BI Authoring MCP (gehostet)](https://api.fabric.microsoft.com/v1/mcp/powerbi/authoring)<br>Microsoft Power BI | offiziell | gehostet | OAuth (Microsoft Entra ID) | lesen und schreiben | proprietär | Vorschau. |
| [Qlik MCP Server](https://help.qlik.com/en-us/cloud-services/Subsystems/Hub/Content/Sense_Hub/QlikMCP/Connecting-Qlik-MCP-server.htm)<br>Qlik Cloud | offiziell | gehostet | OAuth (CIMD, DCR oder manuell) | lesen und schreiben | proprietär | Allgemein verfügbar seit 10.02.2026. Endpunkt /api/ai/mcp des eigenen Tenants; muss von der Administration aktiviert werden. |
| [horizun-pbi-mcp](https://github.com/HorizunGroup/horizun-pbi-mcp)<br>Microsoft Power BI | Community | stdio | Microsoft Entra ID | lesen und schreiben | Apache-2.0 | DAX-Abfragen und Modelländerungen; Schreibzugriffe auf das aktive Projektverzeichnis begrenzt. |
| [qlik-mcp-server (arthurfantaci)](https://github.com/arthurfantaci/qlik-mcp-server)<br>Qlik Sense Enterprise | Community | stdio | Zertifikat (WebSocket zur Engine) | lesen | MIT | Letzte Änderung im Repository am 28.09.2025. Liest App-Metadaten, Kennzahlen und Skripte. |
| [SAP Datasphere MCP](https://github.com/rahulsethi/SAPDatasphereMCP)<br>SAP Datasphere | Community | stdio und HTTP | OAuth (Datasphere) | lesen | BUSL-1.1 | Business Source License, keine OSI-Lizenz. Katalog, Abfragen und analytische Modelle; in Version 1.x ausdrücklich ohne Schreib-Tools. |

## Datenbanken

Viele Datenbank-Server führen beliebiges SQL aus. Verbinden Sie sie mit einem eigenen Datenbankbenutzer mit minimalen Rechten, nicht mit einem Administrator.

Anleitung: [Postgres MCP Server](anleitungen/postgres-mcp.md)

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [MCP Toolbox for Databases](https://github.com/googleapis/mcp-toolbox)<br>Google-Cloud-Datenbanken, PostgreSQL, MySQL, SQL Server und weitere | offiziell | stdio und HTTP | Datenbank-Zugangsdaten, optional OAuth | lesen und schreiben | Apache-2.0 | Tools werden in einer YAML-Datei als feste SQL-Abfragen definiert. Früher unter googleapis/genai-toolbox. |
| [SQL MCP Server (Data API builder)](https://github.com/Azure/data-api-builder)<br>Microsoft SQL Server / Azure SQL | offiziell | HTTP | Datenbank-Zugangsdaten, optional Entra ID | lesen und schreiben | MIT | Teil des Data API builder; Tabellen und Aktionen werden in der Konfiguration freigegeben. |
| [MySQL MCP Server (Oracle)](https://github.com/oracle/mcp/tree/main/src/mysql-mcp-server)<br>MySQL / HeatWave | offiziell | stdio und HTTP | Datenbank-Zugangsdaten | lesen und schreiben | UPL-1.0 | Teil der Sammlung oracle/mcp; Sterne und Aktivität beziehen sich auf die Sammlung. |
| [MariaDB MCP Server](https://github.com/MariaDB/mcp)<br>MariaDB | offiziell | stdio und HTTP | Datenbank-Zugangsdaten | lesen und schreiben | MIT | MCP_READ_ONLY erzwingt reine SELECT/SHOW/DESCRIBE-Abfragen. Optional Vektorsuche. |
| [Azure Database for PostgreSQL MCP](https://github.com/microsoft/postgres-mcp)<br>PostgreSQL (Azure) | offiziell | stdio | Entra ID oder Passwort | lesen und schreiben | MIT | Verbindungsprofile erlauben Schreib-Tools, solange access_mode nicht auf ro steht. |
| [SQLcl MCP Server](https://docs.oracle.com/en/database/oracle/sql-developer-command-line/26.1/sqcug/sqlcl-mcp-server.html)<br>Oracle Database | offiziell | stdio | gespeicherte SQLcl-Verbindungen | lesen und schreiben | proprietär | In SQLcl ab Version 25.2 enthalten, Start mit sql -mcp. |
| [Postgres MCP Pro](https://github.com/crystaldba/postgres-mcp)<br>PostgreSQL | Community | stdio und HTTP | Verbindungs-URL | lesen und schreiben | MIT | Eingeschränkter Modus nur lesend; zusätzlich Index- und Abfrageanalyse. |
| [mcp-server-mysql (benborla)](https://github.com/benborla/mcp-server-mysql)<br>MySQL | Community | stdio und HTTP | Datenbank-Zugangsdaten, HTTP mit Bearer-Token | lesen | MIT | Standardmäßig nur lesend, Schreibrechte je Schema per Umgebungsvariable. |
| [mysql_mcp_server (designcomputer)](https://github.com/designcomputer/mysql_mcp_server)<br>MySQL | Community | stdio und HTTP | Datenbank-Zugangsdaten | lesen und schreiben | MIT | Führt SQL mit den Rechten des konfigurierten Benutzers aus. |
| [mssql_mcp_server](https://github.com/RichardHan/mssql_mcp_server)<br>Microsoft SQL Server | Community | stdio | SQL- oder Windows-Anmeldung | lesen und schreiben | MIT | Führt beliebiges SQL aus; Rechte über den Datenbankbenutzer begrenzen. |
| [PostgreSQL-Referenzserver (archiviert)](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/postgres)<br>PostgreSQL | Community | stdio | Verbindungs-URL | lesen | MIT | Archiviert. Letzte Änderung im Repository am 28.05.2025. Früherer Referenzserver des MCP-Projekts; npm-Paket als veraltet markiert. Nur zur Einordnung gelistet. |
| [pgEdge Postgres MCP](https://github.com/pgEdge/pgedge-postgres-mcp)<br>PostgreSQL | Community | stdio und HTTP | Benutzer- und Token-Anmeldung | lesen | PostgreSQL | Abfragen laufen in Nur-Lese-Transaktionen, je Datenbank einstellbar. |
| [mssql-mcp (Aaronontheweb)](https://github.com/Aaronontheweb/mssql-mcp)<br>Microsoft SQL Server | Community | stdio | Verbindungszeichenfolge | lesen und schreiben | Apache-2.0 | In .NET, Betrieb als Container. Das README beschreibt eine Nur-Lese-Rolle. |
| [oracle-mcp-server (danielmeppiel)](https://github.com/danielmeppiel/oracle-mcp-server)<br>Oracle Database | Community | stdio | Verbindungszeichenfolge | lesen | MIT | Letzte Änderung im Repository am 22.08.2025. Schema-Kontext und lesende Abfragen für große Oracle-Schemata. |
| [hana-mcp-server](https://github.com/HatriGt/hana-mcp-server)<br>SAP HANA | Community | stdio und HTTP | HANA-Benutzer | lesen und schreiben | MIT | Schema-Erkundung und SQL-Abfragen auf SAP HANA und HANA Cloud. |
| [mssqlclient-mcp-server](https://github.com/aadversteeg/mssqlclient-mcp-server)<br>Microsoft SQL Server | Community | stdio | Verbindungszeichenfolge | lesen | MIT | Standardmäßig nur lesende Tools; Ausführen von SQL lässt sich zusätzlich freigeben. |

## Personal (HR)

HR-Systeme enthalten besonders schutzbedürftige Daten. Klären Sie den Einsatz mit Ihrer Datenschutzbeauftragten oder Ihrem Datenschutzbeauftragten und, wo vorhanden, mit dem Betriebsrat. Für SAP SuccessFactors haben wir keinen Server von SAP gefunden.

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [Factorial MCP Server](https://mcp.factorialhr.com)<br>Factorial | offiziell | gehostet | OAuth 2.0 mit DCR | lesen und schreiben | proprietär | Unter anderem Zeiterfassung, Abwesenheiten und Aufgaben. |
| [Personio MCP Server](https://support.personio.de/hc/en-us/articles/38314656674333-Personio-MCP-server-Beta-access-overview)<br>Personio | offiziell | gehostet | OAuth (Client-ID aus den persönlichen Personio-Einstellungen, ohne Client-Secret) | lesen und schreiben | proprietär | Beta, noch nicht für alle Konten. Endpunkt /mcp der eigenen Personio-Instanz. Liest Profile, Abwesenheiten, Vergütung und Performance; begrenzte Schreibaktionen wie Urlaubsanträge sind standardmäßig aus und separat einschaltbar. Admins können einzelne Tools und Personenattribute sperren. |
| [sf-mcp](https://github.com/aiadiguru2025/sf-mcp)<br>SAP SuccessFactors | Community | stdio und HTTP | SuccessFactors-API-Zugangsdaten | lesen | MIT | Abfragen über die OData-API von SuccessFactors. |
| [mcp-factorial](https://github.com/t4dhg/mcp-factorial)<br>Factorial | Community | stdio | API-Schlüssel oder OAuth | lesen und schreiben | MIT | Lohndaten nur lesend; Schreibzugriffe werden protokolliert. |
| [personio-mcp-server (NikolaiGoMedicus)](https://github.com/NikolaiGoMedicus/personio-mcp-server)<br>Personio | Community | stdio | Personio-API-Zugangsdaten | lesen und schreiben | MIT | Verarbeitet personenbezogene Daten; das README weist auf destruktive Tools für Anwesenheiten hin. |
| [personio-mcp (gyopiazza)](https://github.com/gyopiazza/personio-mcp)<br>Personio | Community | stdio | Personio-API-Zugangsdaten | lesen und schreiben | keine | Zugriff über die Personio-API. |

## E-Commerce

Shopware hat den MCP-Server in den Kern übernommen. JTL steht unter ERP.

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [Shopify Dev MCP](https://shopify.dev/docs/apps/build/ai-toolkit)<br>Shopify (Entwicklung) | offiziell | stdio | keine | lesen | ISC | npm-Paket @shopify/dev-mcp; nur Dokumentation und API-Schemata, keine Shopdaten. Telemetrie standardmäßig aktiv. |
| [Shopify Storefront MCP](https://shopify.dev/docs/apps/build/storefront-mcp)<br>Shopify-Shops | offiziell | gehostet | keine | lesen | proprietär | Katalog- und Warenkorb-Tools unter /api/mcp wurden entfernt, Shopify verweist dafür auf das Universal Commerce Protocol. Erhalten ist die Suche in Shop-Richtlinien und FAQ. |
| [Shopware MCP Server](https://developer.shopware.com/docs/products/tools/mcp-server/intro.html)<br>Shopware 6 | offiziell | HTTP | Admin-API-Integration bzw. Store-API-Zugriffsschlüssel | lesen und schreiben | MIT | Im Shopware-Kern enthalten, Endpunkte /api/_mcp (Admin) und /store-api/_mcp (Storefront). Protokoll 2025-11-25. |
| [shopify-mcp (GeLi2001)](https://github.com/GeLi2001/shopify-mcp)<br>Shopify | Community | stdio | Admin-API-Zugriffstoken | lesen und schreiben | MIT | Produkte, Kunden und Bestellungen über die Admin-GraphQL-API. |
| [shopware-mcp (bnymnDev)](https://github.com/bnymnDev/shopware-mcp)<br>Shopware 6 | Community | stdio und HTTP | Admin-API-Integration | lesen und schreiben | MIT | Nur lesend, solange nicht mit --allow-write gestartet; Schreibzugriffe laufen zuerst als Probelauf. |
| [billbee-mcp-server (kochfreiburg)](https://github.com/kochfreiburg/billbee-mcp-server)<br>Billbee | Community | HTTP | Billbee-API-Schlüssel und Benutzer | lesen und schreiben | AGPL-3.0 | Betrieb als Container vorgesehen. |
| [BillbeeMcpServer](https://github.com/biegomar/BillbeeMcpServer)<br>Billbee | Community | stdio | Billbee-API-Schlüssel und Benutzer | lesen und schreiben | MIT | In C#/.NET. |
| [shopware-mcp-server (kochfreiburg)](https://github.com/kochfreiburg/shopware-mcp-server)<br>Shopware 6 | Community | HTTP | Admin-API-Integration | lesen und schreiben | AGPL-3.0 | Betrieb als Container vorgesehen. |

## Zusammenarbeit

Microsoft betreibt die Server für Outlook, Teams und SharePoint als Teil von Agent 365 je Tenant. Nextcloud ist für selbst betriebene Installationen aufgeführt.

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [notion-mcp-server (lokal)](https://github.com/makenotion/notion-mcp-server)<br>Notion | offiziell | stdio und HTTP | Integration-Token | lesen und schreiben | MIT | Laut Notion-Dokumentation nicht mehr aktiv gepflegt. Ein Token nur mit Leserecht ist möglich. |
| [Atlassian Rovo MCP Server](https://mcp.atlassian.com/v2/mcp)<br>Jira und Confluence (Cloud) | offiziell | gehostet | OAuth 2.1 oder API-Token | lesen und schreiben | proprietär | Nur Atlassian Cloud. Die Administration gibt Tool-Gruppen (lesen, schreiben, löschen) frei. Das Repository unter Apache-2.0 enthält Konfiguration und Doku. |
| [Microsoft MCP Server for Enterprise](https://mcp.svc.cloud.microsoft/enterprise)<br>Microsoft Entra ID / Microsoft Graph | offiziell | gehostet | OAuth (Microsoft Entra ID) | lesen | proprietär | Öffentliche Vorschau, nur lesende Graph-Abfragen für IT-Administration. Das Repository enthält nur Dokumentation (CC-BY-4.0). |
| [Microsoft 365 Server (Agent 365)](https://github.com/microsoft/mcp)<br>Outlook, Kalender, Teams, Word, OneDrive und SharePoint | offiziell | gehostet | OAuth (Microsoft Entra ID) | lesen und schreiben | proprietär | Mehrere gehostete Server je Tenant unter agent365.svc.cloud.microsoft, unter anderem für Mail, Kalender, Teams, Word, OneDrive/SharePoint und SharePoint-Listen; im Katalog microsoft/mcp aufgeführt. |
| [Notion MCP (gehostet)](https://mcp.notion.com/mcp)<br>Notion | offiziell | gehostet | OAuth mit PKCE | lesen und schreiben | proprietär | Von Notion empfohlener Weg; der lokale Open-Source-Server wird laut Notion nicht mehr aktiv gepflegt. |
| [Slack MCP Server](https://mcp.slack.com/mcp)<br>Slack | offiziell | gehostet | OAuth über registrierte Slack-App, ohne DCR | lesen und schreiben | proprietär | Allgemein verfügbar seit 17.02.2026. |
| [mcp-atlassian](https://github.com/sooperset/mcp-atlassian)<br>Jira und Confluence (Cloud, Server, Data Center) | Community | stdio und HTTP | API-Token, Personal Access Token oder OAuth | lesen und schreiben | MIT | Unterstützt auch Server- und Data-Center-Installationen. Schalter READ_ONLY_MODE verfügbar. |
| [slack-mcp-server (korotovsky)](https://github.com/korotovsky/slack-mcp-server)<br>Slack | Community | stdio und HTTP | OAuth- oder Browser-Token | lesen und schreiben | MIT | Nachrichten senden ist standardmäßig deaktiviert. Die Anmeldung mit Browser-Token ist im Workspace vorher abzustimmen. |
| [ms-365-mcp-server](https://github.com/Softeria/ms-365-mcp-server)<br>Microsoft 365 (Graph) | Community | stdio und HTTP | OAuth (Microsoft Entra ID) | lesen und schreiben | MIT | Mail, Kalender, Dateien, Teams und mehr; Schalter --read-only und Tool-Presets. |
| [nextcloud-mcp-server](https://github.com/cbcoutinho/nextcloud-mcp-server)<br>Nextcloud | Community | stdio und HTTP | App-Passwort oder OAuth | lesen und schreiben | AGPL-3.0 | Dateien, Kalender, Kontakte, Notizen und Deck; mehrere Benutzer über Login Flow v2. |
| [Lokka](https://github.com/merill/lokka)<br>Microsoft Graph und Azure | Community | stdio | Entra-App, Zertifikat oder interaktiv | lesen und schreiben | MIT | Für Tenant-Administration; Rechte ergeben sich aus den Graph-Berechtigungen der App. |
| [notion-mcp-server (awkoy)](https://github.com/awkoy/notion-mcp-server)<br>Notion | Community | stdio und HTTP | Integration-Token | lesen und schreiben | MIT | Gebündelte Schreibvorgänge mit Rücknahme bei Fehlern. |
| [teams-mcp (floriscornel)](https://github.com/floriscornel/teams-mcp)<br>Microsoft Teams | Community | stdio | OAuth (Microsoft Entra ID) | lesen und schreiben | MIT | Nur-Lese-Modus verfügbar. |
| [sharepoint-mcp](https://github.com/DEmodoriGatsuO/sharepoint-mcp)<br>Microsoft SharePoint | Community | stdio und HTTP | Entra-App (Client Secret) | lesen und schreiben | MIT | Dokumente und Listen in SharePoint über Microsoft Graph. |

## Logistik und Versand

Die Kategorie hat zwei Einträge: die Server von DHL (nur Sandbox) und Sendcloud. Gepflegte Community-Server für Versanddienstleister haben wir nicht gefunden.

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [DHL API Assistant MCP Server](https://developer.dhl.com/dhl-api-assistant-manual-mcp-integration-guide?language_content_entity=en)<br>DHL-APIs (Versand, Retouren, Sendungsverfolgung) | offiziell | gehostet | API-Schlüssel im Header dhl-api-key | lesen und schreiben | proprietär | Nur Sandbox, kein Zugriff auf Produktivumgebungen. Schlüssel aus dem DHL Developer Portal. |
| [Sendcloud MCP Server](https://mcp.sendcloud.com/mcp)<br>Sendcloud | offiziell | gehostet | OAuth 2.0 mit CIMD | lesen und schreiben | proprietär | Setzt CIMD voraus; Clients ohne CIMD-Unterstützung können sich nicht verbinden. |

## Banking und Zahlungen

**FinTS und EBICS:** Einen MCP-Server für FinTS (HBCI) oder EBICS haben wir nicht gefunden, ebenso keinen eigenen Server von Sparkassen, Volksbanken oder Direktbanken. Wer Kontoumsätze deutscher Banken anbinden will, braucht eine eigene Anbindung, zum Beispiel auf Basis der Bibliothek python-fints (LGPL-3.0). EBICS setzt einen Vertrag mit der Bank voraus.

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [Stripe MCP](https://mcp.stripe.com)<br>Stripe | offiziell | stdio und HTTP | OAuth oder eingeschränkter API-Schlüssel | lesen und schreiben | MIT | Gehostet unter mcp.stripe.com, lokal über @stripe/mcp. Laut Stripe werden vollständige Secret Keys ab Dezember 2026 nicht mehr angenommen. Früher unter stripe/agent-toolkit. |
| [PayPal MCP Server](https://mcp.paypal.com)<br>PayPal | offiziell | stdio und HTTP | OAuth bzw. PayPal-Zugangsdaten | lesen und schreiben | Apache-2.0 | Gehostet mit Sandbox mcp.sandbox.paypal.com, lokal über das Agent Toolkit. Rechnungen, Bestellungen, Abos und Streitfälle. |
| [Mollie MCP Server](https://mcp.mollie.com/mcp)<br>Mollie | offiziell | gehostet | OAuth mit CIMD | lesen und schreiben | proprietär | Anmeldung mit statischem Token ist abgekündigt. |
| [Qonto MCP Server](https://mcp.qonto.com/mcp)<br>Qonto | offiziell | gehostet | OAuth | lesen und schreiben | proprietär | Keine SEPA-Überweisungen über MCP. Zusätzlich ein nur lesender Endpunkt für mehrere Organisationen. |

## Dokumente und DMS

Für DocuWare, d.velop und ELO haben wir keinen Server des Herstellers gefunden. DocuWare verweist auf die Aura-API, d.velop kündigt ein Agent Center für das vierte Quartal 2026 an.

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [AnythingMCP](https://github.com/HelpCode-ai/anythingmcp)<br>d.velop, ELO, SAP und weitere über Konnektoren | Community | HTTP | je Konnektor, OAuth für Clients | lesen und schreiben | AGPL-3.0 | Gateway, das REST-, SOAP- und Datenbank-Schnittstellen als MCP-Tools bereitstellt; Konnektoren für d.velop und ELO. Zusätzlich als gehosteter Dienst angeboten. |
| [elo-mcp-server (LOUPZ-DE)](https://github.com/LOUPZ-DE/elo-mcp-server)<br>ELO ECM | Community | stdio und HTTP | ELO-Benutzer oder OAuth | lesen | CC-BY-NC-4.0 | CC BY-NC 4.0, nur nicht-kommerzielle Nutzung. Vier Schreiboperationen sind standardmäßig aus und nur mit persönlicher ELO-Anmeldung nutzbar. |
| [docuware-mcp](https://github.com/sniner/docuware-mcp)<br>DocuWare | Community | stdio und HTTP | DocuWare-Benutzer oder OAuth | lesen | BSD-3-Clause | Suche und Abruf in DocuWare-Archiven, auf PyPI als docuware-mcp. Protokoll 2026-07-28, 2025-11-25. |
| [elo-mcp (Herzog)](https://github.com/Herzog-GmbH/elo-mcp)<br>ELO ECM | Community | stdio | ELO-Benutzer | lesen und schreiben | MIT | Für ELO 25 unter Windows. Jeder Schreibvorgang braucht Vorschau und Einmal-Token. Dokumentation auf Deutsch. |

## Behörden und Open Data

Eigene MCP-Server von Behörden haben wir nicht gefunden. Viele Server bauen auf den Schnittstellen auf, die bund.dev dokumentiert. Das Python-Paket bundesAPI/deutschland ist kein MCP-Server, eignet sich aber als Baustein.

| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |
| --- | --- | --- | --- | --- | --- | --- |
| [deutsche-gesetze-mcp](https://github.com/floleuerer/deutsche-gesetze-mcp)<br>Bundesgesetze (gesetze-im-internet.de) | Community | stdio | keine | lesen | MIT | Suche und Abruf von Gesetzestexten. Ersetzt keine Rechtsberatung. |
| [DejureMcp](https://github.com/halllo/DejureMcp)<br>dejure.org | Community | stdio | keine | lesen | MIT | Rechtsgebiete, Gesetze und Paragrafen, bei Bedarf von dejure.org geladen; in C#/.NET. |
| [germany-mcp-server](https://github.com/AiAgentKarl/germany-mcp-server)<br>Autobahn-API, DWD, NINA | Community | stdio | keine | lesen | MIT | 16 Tools zu offenen Bundes-APIs, unter anderem Verkehrslage, Wetter und Warnmeldungen, ohne API-Schlüssel nutzbar. |
| [handelsregister-mcp (lexdoudkin)](https://github.com/lexdoudkin/handelsregister-mcp)<br>Handelsregister | Community | stdio | keine | lesen | Apache-2.0 | Firmensuche, Registerauszüge und Dokumentenlisten aus handelsregister.de; dessen Nutzungsbedingungen gelten auch für automatisierte Abrufe. |
| [bundestag-mcp](https://github.com/oguzhan/bundestag-mcp)<br>DIP-API des Deutschen Bundestags, abgeordnetenwatch | Community | stdio | keine | lesen | MIT | Drucksachen, Vorgänge und Plenarprotokolle; das README kennzeichnet das Projekt als in Arbeit. |
| [destatis-mcp](https://github.com/inooLabs/destatis-mcp)<br>Statistisches Bundesamt (GENESIS-Online) | Community | HTTP | GENESIS-API-Token (kostenlose Registrierung) | lesen | keine | Tabellen und Zeitreihen aus GENESIS-Online. |
| [dwd-mcp (difu)](https://github.com/difu/dwd-mcp)<br>Deutscher Wetterdienst | Community | stdio | keine | lesen | MIT | Letzte Änderung im Repository am 14.09.2025. Wetterdaten aus dem Open-Data-Angebot des DWD. |
| [dwd-mcp-server (jimimatt)](https://github.com/jimimatt/dwd-mcp-server)<br>Deutscher Wetterdienst (über Bright Sky) | Community | stdio | keine | lesen | MIT | Wetterdaten des DWD über die Bright-Sky-API. |
| [handelsregister-mcp (mirrorops-io)](https://github.com/mirrorops-io/handelsregister-mcp)<br>Handelsregister | Community | stdio | keine | lesen | MIT | Firmensuche im Handelsregister, in TypeScript. |
| [openclaw-bahn-mcp](https://github.com/biacz/openclaw-bahn-mcp)<br>Bahn- und ÖPNV-Auskunft (Transitous) | Community | stdio | keine | lesen | MIT | Verbindungen und Abfahrten mit Echtzeit aus den offenen DELFI-Daten über Transitous, nicht über eine API der Deutschen Bahn. |

## So prüfen Sie einen MCP-Server vor dem Einsatz

- [ ] **Herkunft:** Stammt der Server vom Hersteller des Systems oder aus der Community? Stimmen Repository, Paketname und Herausgeber überein?
- [ ] **Wartung:** Wann gab es die letzte Änderung? Werden Issues beantwortet? Ist das Repository archiviert?
- [ ] **Lizenz:** Ohne Lizenzdatei räumt der Autor keine Nutzungsrechte ein. AGPL-3.0 gilt auch, wenn Sie den Server Dritten über das Netz bereitstellen.
- [ ] **Rechte:** Gibt es einen Nur-Lese-Modus? Nutzen Sie einen eigenen technischen Benutzer mit minimalen Rechten und starten Sie mit einem Testsystem.
- [ ] **Anmeldung:** OAuth mit kurzlebigen Tokens ist API-Schlüsseln mit Vollzugriff vorzuziehen. Schlüssel gehören nicht in Konfigurationsdateien im Repository.
- [ ] **Datenfluss:** Läuft der Server lokal, bei Ihnen oder beim Anbieter? Bei gehosteten Diensten klären Sie Auftragsverarbeitung, Speicherort und Protokollierung.
- [ ] **Transport:** stdio-Server laufen als lokaler Prozess. HTTP-Server binden Sie nicht ungeschützt an öffentliche Adressen.
- [ ] **Tool-Beschreibungen:** Lesen Sie, welche Tools der Server anbietet und was sie auslösen. Inhalte aus E-Mails, Tickets oder Dokumenten können Anweisungen an das Modell enthalten.
- [ ] **Versionen:** Pinnen Sie Paketversionen statt immer die neueste Version zu laden, und lesen Sie Änderungen vor einem Update.
- [ ] **Protokollversion:** Die aktuelle MCP-Spezifikation ist 2026-07-28. Viele Server und Clients sprechen noch 2025-11-25; der Transport SSE ist veraltet.

## Eintrag vorschlagen

Ein Server fehlt oder eine Angabe ist veraltet? Öffnen Sie ein Issue oder einen Pull Request mit einer Änderung an `daten/server.yaml`.

- Der Server ist öffentlich zugänglich, funktioniert und betrifft ein System, das in Deutschland verbreitet ist.
- Keine leeren Repositorys und keine Forks ohne eigene Änderungen.
- Für offizielle Server nennen Sie eine Quelle beim Hersteller.
- Der Hinweis ist kurz und sachlich, ohne Werbung und ohne Wertung über Personen oder andere Projekte.
- Danach `python3 scripts/liste_bauen.py` ausführen; das Skript validiert die Daten und erzeugt diese Datei neu.

> **Hinweis:** Technisches Hilfswerk, keine Beratung. Technische Informationen nach Stand 19.10.2026, ohne Gewähr für Vollständigkeit und Richtigkeit. Keine Rechts-, Steuer- oder Datenschutzberatung; die Autoren sind keine Rechtsanwälte, Steuerberater oder Datenschutzbeauftragten. Was ein KI-Assistent mit diesen Servern erzeugt, stammt vom Sprachmodell und nicht von uns; für den Output von KI-Systemen übernehmen wir keine Haftung. Prüfen Sie jede Ausgabe, bevor Sie sie verwenden. Produktnamen sind Marken ihrer Inhaber; es besteht keine Verbindung zu den genannten Herstellern.
