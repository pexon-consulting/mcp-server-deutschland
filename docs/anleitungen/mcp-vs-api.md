# MCP vs. API: der Unterschied einfach erklärt

MCP vs. API, oder genauer: MCP oder REST-API? Diese Anleitung vergleicht das Model Context Protocol mit einer klassischen Programmierschnittstelle, zeigt dieselbe Abfrage einmal als REST-Aufruf und einmal als MCP-Tool-Aufruf und grenzt MCP von Function Calling, RAG und MCP-Gateways ab.

Stand: 19.10.2026. Spezifikation: MCP 2026-07-28. Teil der Sammlung [MCP-Server für Geschäftssysteme in Deutschland](../liste.md).

Für: Entwickler, Architekten und IT-Verantwortliche, die entscheiden, ob sie ein System per API, per MCP oder mit beidem anbinden.

## Inhaltsverzeichnis

- [Das Wichtigste in Kürze](#das-wichtigste-in-kürze)
- [Was ist eine API, was ist MCP?](#was-ist-eine-api-was-ist-mcp)
- [MCP vs. API: Unterschiede in der Tabelle](#mcp-vs-api-unterschiede-in-der-tabelle)
- [Beispiel: dieselbe Abfrage als REST und als MCP](#beispiel-dieselbe-abfrage-als-rest-und-als-mcp)
- [MCP ersetzt keine API](#mcp-ersetzt-keine-api)
- [Kosten, Latenz und Token](#kosten-latenz-und-token)
- [Sicherheit im Vergleich](#sicherheit-im-vergleich)
- [Wann MCP, wann API?](#wann-mcp-wann-api)
- [MCP vs. Function Calling](#mcp-vs-function-calling)
- [MCP vs. RAG](#mcp-vs-rag)
- [Was ist ein MCP-Gateway?](#was-ist-ein-mcp-gateway)
- [Häufige Fragen](#häufige-fragen)
- [Weiterlesen](#weiterlesen)

## Das Wichtigste in Kürze

- Eine **API** ist die Schnittstelle eines Systems für Programme. Ein **MCP-Server** ist eine standardisierte Schicht, über die KI-Anwendungen Funktionen zur Laufzeit finden und aufrufen.
- Der Kernunterschied ist die **Entdeckung zur Laufzeit**: Ein MCP-Client fragt `tools/list` und bekommt Namen, Beschreibungen und JSON-Schemas. Bei einer REST-API schreibt ein Mensch Code nach der Dokumentation.
- MCP **ersetzt keine API**. Meist ruft der MCP-Server intern genau die API auf, die es schon gibt. Lizenzen, Tarife, Freigaben und Rate Limits bleiben.
- Für feste Abläufe zwischen Programmen (Batch, Synchronisation, Webhooks) bleibt die API die direkte Wahl. MCP lohnt sich, wenn ein Sprachmodell entscheiden soll, welche Funktion es mit welchen Parametern aufruft.
- MCP verursacht zusätzliche Kosten in Form von **Token**: Jede Tool-Beschreibung landet im Kontext des Modells.

## Was ist eine API, was ist MCP?

Eine **API** (Application Programming Interface) beschreibt, wie ein Programm mit einem anderen spricht. Bei Web-APIs sind das meist REST-Endpunkte wie `GET /v1/invoices` mit JSON als Antwort, beschrieben in einer OpenAPI-Datei. Wer die API nutzt, liest die Dokumentation, holt sich einen Schlüssel und schreibt Code für genau diese API.

**MCP** (Model Context Protocol) ist ein Protokoll auf Basis von JSON-RPC 2.0, das festlegt, wie KI-Anwendungen mit Servern sprechen. Ein MCP-Server meldet selbst, welche Tools, Resources und Prompts er anbietet. Jede MCP-fähige Anwendung, etwa Claude, Cursor, VS Code oder Codex, kann ihn ohne eigenen Integrationscode nutzen. Die Grundlagen stehen in [Was ist ein MCP-Server?](./was-ist-ein-mcp-server.md).

Ein Bild hilft: Die API ist die Steckdose eines Geräts, MCP ist eine genormte Steckerleiste davor, an die jedes MCP-fähige Gerät passt. Ohne Steckdose nützt die Leiste nichts.

## MCP vs. API: Unterschiede in der Tabelle

| Merkmal | REST-API | MCP |
| --- | --- | --- |
| Zielgruppe | Programme, geschrieben von Entwicklern | KI-Anwendungen, gesteuert von einem Sprachmodell |
| Entdeckung | außerhalb des Protokolls (Doku, OpenAPI) | zur Laufzeit über `tools/list`, `resources/list`, `prompts/list` und `server/discover` |
| Nachrichtenformat | frei: Pfade, HTTP-Verben, Query, Body | JSON-RPC 2.0 mit festen Methoden wie `tools/call` |
| Transport | HTTP | stdio (lokaler Prozess) oder Streamable HTTP |
| Schema | OpenAPI optional | JSON Schema für Eingabe Pflicht, Ausgabe optional (`outputSchema`) |
| Ergebnisse | beliebiges JSON, Binärdaten | `content` (Text, Bild, Audio, Links) plus optional `structuredContent` |
| Anmeldung | je API verschieden (Key, Bearer, OAuth) | HTTP: OAuth 2.1 mit Protected Resource Metadata (RFC 9728); stdio: Umgebungsvariablen |
| Zustand | je API | seit 2026-07-28 zustandslos, Zustand über explizite Kennungen |
| Fehler | HTTP-Statuscodes | JSON-RPC-Fehler plus Tool-Fehler mit `isError: true` für das Modell |
| Verhaltenshinweise | keine | Annotations wie `readOnlyHint`, `destructiveHint` (nur Hinweise) |
| Wiederverwendung | eine Integration je Anwendung | ein Server für viele Anwendungen |
| Reife | jahrzehntelang erprobt | jung, Spezifikation ändert sich noch |

Quellen: [Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools), [server/discover](https://modelcontextprotocol.io/specification/2026-07-28/server/discover), [Authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization), alle abgerufen 19.10.2026.

## Beispiel: dieselbe Abfrage als REST und als MCP

Aufgabe: Welche gesetzlichen Feiertage gibt es 2026 in Sachsen?

### Variante 1: REST-Aufruf

Die öffentliche, kostenlose API [Nager.Date](https://date.nager.at) braucht keinen Schlüssel. Ein Aufruf liefert alle deutschen Feiertage, den Filter auf Sachsen erledigt `jq`:

```bash
curl -s "https://date.nager.at/api/v3/PublicHolidays/2026/DE" \
  | jq -c '[.[] | select(.global or (.counties | index("DE-SN"))) | {date, localName}]'
```

Echte Ausgabe vom 19.10.2026:

```json
[{"date":"2026-01-01","localName":"Neujahr"},{"date":"2026-04-03","localName":"Karfreitag"},{"date":"2026-04-06","localName":"Ostermontag"},{"date":"2026-05-01","localName":"Tag der Arbeit"},{"date":"2026-05-14","localName":"Christi Himmelfahrt"},{"date":"2026-05-25","localName":"Pfingstmontag"},{"date":"2026-10-03","localName":"Tag der Deutschen Einheit"},{"date":"2026-10-31","localName":"Reformationstag"},{"date":"2026-11-18","localName":"Buß- und Bettag"},{"date":"2026-12-25","localName":"Erster Weihnachtstag"},{"date":"2026-12-26","localName":"Zweiter Weihnachtstag"}]
```

Was Sie dafür wissen mussten: die URL-Struktur, dass Länder als `DE-SN` in `counties` stehen, dass `global` bundesweit bedeutet. Das steht in der Doku, nicht in der Antwort.

### Variante 2: MCP-Tool-Aufruf über stdio

Derselbe Inhalt kommt vom Beispielserver aus [MCP-Server erstellen](./mcp-server-erstellen.md), der die Feiertage selbst berechnet. Ein Client schickt zuerst optional `server/discover` und `tools/list`, dann `tools/call`. Nach Spezifikation 2026-07-28 trägt jede Anfrage in `params._meta` Protokollversion und Client-Fähigkeiten. Diese drei Zeilen gehen an stdin des Serverprozesses, jede Nachricht steht in genau einer Zeile:

```text
{"jsonrpc":"2.0","id":1,"method":"server/discover","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientCapabilities":{}}}}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientCapabilities":{}}}}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_holidays","arguments":{"year":2026,"state":"SN"},"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientCapabilities":{}}}}
```

Die Antwort auf `tools/list` beschreibt das Tool vollständig, inklusive Schema und Verhaltenshinweisen (gekürzt):

```json
{
  "name": "list_holidays",
  "title": "Feiertage eines Bundeslands",
  "description": "Listet die gesetzlichen Feiertage eines Jahres für ein Bundesland.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "year": {"type": "integer", "description": "Jahr, 1995 bis 2100"},
      "state": {"type": "string", "minLength": 2, "maxLength": 2,
                "description": "Kürzel des Bundeslands, z. B. BY, NW, BE"}
    },
    "required": ["year", "state"]
  },
  "annotations": {"readOnlyHint": true, "idempotentHint": true, "openWorldHint": false}
}
```

Die Antwort auf `tools/call` (gekürzt, echte Ausgabe vom 19.10.2026):

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "resultType": "complete",
    "content": [{"type": "text", "text": "{\n  \"year\": 2026, ..."}],
    "structuredContent": {
      "year": 2026, "state": "SN", "state_name": "Sachsen", "count": 11,
      "holidays": [
        {"date": "2026-01-01", "name": "Neujahr", "weekday": "Donnerstag", "nationwide": true},
        {"date": "2026-11-18", "name": "Buß- und Bettag", "weekday": "Mittwoch", "nationwide": false}
      ]
    },
    "isError": false,
    "_meta": {"io.modelcontextprotocol/serverInfo": {"name": "feiertage", "version": "0.1.0"}}
  }
}
```

Beide Wege liefern dieselben elf Tage. Der Unterschied: Beim MCP-Aufruf musste niemand vorher eine Doku lesen. Das Modell hat aus `tools/list` gelernt, dass es `year` und `state` braucht und welche Werte erlaubt sind.

### Variante 3: MCP über Streamable HTTP

Läuft derselbe Server als HTTP-Dienst, ist der Aufruf wieder ein `curl`, aber mit festem Format. Die Header `MCP-Protocol-Version`, `Mcp-Method` und `Mcp-Name` sind nach 2026-07-28 Pflicht ([Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http), abgerufen 19.10.2026). Getestet am 19.10.2026 gegen den Python-Beispielserver auf `127.0.0.1:8765`:

```bash
curl -s http://127.0.0.1:8765/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2026-07-28" \
  -H "Mcp-Method: tools/call" \
  -H "Mcp-Name: count_working_days" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"count_working_days","arguments":{"start":"2026-12-24","end":"2026-12-31","state":"BY"},"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientCapabilities":{}}}}'
```

Antwort (gekürzt): `HTTP/1.1 200 OK`, im Body `"structuredContent":{"start":"2026-12-24","end":"2026-12-31","state":"BY","working_days":5,...}`. Ohne die MCP-Header behandelte das Python-SDK 2.3.0 die Anfrage als Altversion mit Sitzung und antwortete `400 Bad Request` mit `Missing session ID`.

## MCP ersetzt keine API

MCP ist eine Schicht über bestehenden Schnittstellen. Fast jeder Geschäfts-MCP-Server ruft intern eine API auf, liest eine Datenbank oder schreibt eine Datei. Daraus folgt:

- **Lizenz und Tarif bleiben.** Die Public API von lexware office setzt laut Hersteller den Tarif XL voraus. Ein MCP-Server, der diese API nutzt, braucht denselben Tarif.
- **Freigaben bleiben.** Die DATEV-Online-APIs stehen auch ohne Partnerschaft offen, setzen aber eine Registrierung im Developer Portal, ein Abonnement und für den Produktivbetrieb eine technische Prüfung durch DATEV voraus. Ein MCP-Server umgeht das nicht. Darum arbeiten Community-Server für DATEV meist mit dem Dateiformat EXTF, siehe die [Anleitung zum DATEV-Format (EXTF)](./datev-mcp-server.md).
- **Rate Limits bleiben.** Die lexware-office-API erlaubt laut Doku 2 Anfragen pro Sekunde. Ein Modell, das in einer Schleife Tools aufruft, erreicht solche Grenzen schneller als ein Mensch.
- **Nutzungsbedingungen bleiben.** Manche Anbieter verbieten Polling oder die Weitergabe von Zugängen an Dritte. Das gilt auch, wenn der Zugriff über einen MCP-Server läuft.

Umgekehrt braucht nicht jede API einen MCP-Server. Ein nächtlicher Abgleich zwischen Shop und Warenwirtschaft läuft besser direkt per API, ohne Sprachmodell dazwischen.

## Kosten, Latenz und Token

**Token.** Damit ein Modell ein Tool wählen kann, muss die Tool-Liste in seinem Kontext stehen. Die `tools/list`-Antwort des Beispielservers mit zwei Tools ist 3.197 Byte groß, die vollständige REST-Antwort von Nager.Date für ganz Deutschland 3.588 Byte. Als grobe Faustregel entsprechen vier Zeichen etwa einem Token; das genaue Verhältnis hängt vom Modell ab. Zehn Server mit je zwanzig Tools kosten bei jeder Anfrage spürbar Kontext. Viele Clients erlauben deshalb, einzelne Tools oder Server abzuschalten, etwa Codex mit `enabled_tools` und `disabled_tools`.

**Latenz.** Gemessen am 19.10.2026 auf einem Mac mit Apple M4 Max, Python-Beispielserver über stdio:

| Vorgang | Dauer |
| --- | --- |
| REST-Aufruf an Nager.Date (Internet) | 0,08-0,10 s |
| Serverprozess starten und verbinden (stdio, Python) | 0,25 s, einmal pro Sitzung |
| einzelner `tools/call` im laufenden Prozess (Median aus 20) | 1,0 ms |

Die Protokollschicht selbst kostet kaum Zeit. Teuer ist der Umweg über das Sprachmodell: Jeder Tool-Aufruf bedeutet mindestens eine weitere Modellantwort, die Sekunden dauern kann.

**Geld.** MCP selbst ist kostenlos. Kosten entstehen durch Token beim Modellanbieter, durch Hosting bei Remote-Servern und durch die zugrunde liegende API.

## Sicherheit im Vergleich

| Thema | REST-API | MCP |
| --- | --- | --- |
| Wer entscheidet über den Aufruf | Ihr Code | das Modell, bestätigt durch einen Menschen |
| Zugangsdaten | im Client-Code oder Secret Store | stdio: Umgebungsvariablen des Serverprozesses; HTTP: OAuth 2.1 |
| Typische Risiken | Schlüssel im Code, zu weite Rechte | zusätzlich manipulierte Tool-Beschreibungen und präparierte Daten, die das Modell beeinflussen |
| Prüfung | Code-Review | Code-Review plus Freigaben im Client |

Die Spezifikation verlangt von Servern, alle Eingaben zu prüfen, Zugriffe zu kontrollieren, Aufrufe zu begrenzen und Ausgaben zu bereinigen. Clients sollen sensible Aufrufe bestätigen lassen, Eingaben vor dem Aufruf anzeigen und Tool-Annotations nur bei vertrauenswürdigen Servern glauben. Ein Server darf laut [Security Best Practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices) (abgerufen 19.10.2026) keine Token annehmen, die nicht für ihn ausgestellt wurden ("Token Passthrough" ist ausdrücklich ein Anti-Pattern).

Der größte Unterschied: Bei einer API ruft Ihr Code genau das auf, was Sie programmiert haben. Bei MCP entscheidet ein Modell anhand von Text, und dieser Text kann aus fremden Quellen stammen. Geben Sie einem MCP-Server deshalb nur die Rechte, die er braucht, und starten Sie mit lesenden Tools. Mehr in [MCP-Sicherheit](./mcp-sicherheit.md).

## Wann MCP, wann API?

| Situation | Empfehlung |
| --- | --- |
| Feste, wiederkehrende Abläufe ohne Entscheidung (Export, Sync, Webhook) | API direkt |
| Massendaten, Reporting-Pipelines | API oder Datenbank direkt |
| Ein Assistent soll Fragen beantworten und dafür Daten nachschlagen | MCP |
| Entwickler wollen in Claude Code, Cursor oder VS Code auf Systeme zugreifen | MCP |
| Dieselbe Integration soll in mehreren KI-Anwendungen laufen | MCP |
| Strenge Nachvollziehbarkeit jedes Schritts, keine Modellentscheidung erlaubt | API, ggf. mit festem Workflow |
| System hat keine API, nur Dateien (z. B. DATEV-Import per EXTF) | MCP-Server, der Dateien erzeugt und prüft |

Oft ist die Antwort "beides": Die API bleibt die Grundlage, ein schlanker MCP-Server stellt ausgewählte, gut beschriebene Funktionen für KI-Anwendungen bereit.

## MCP vs. Function Calling

**Function Calling** (auch Tool Use) ist eine Fähigkeit des Sprachmodells: Sie schicken dem Modell eine Liste von Funktionen mit JSON-Schema, und es antwortet mit "rufe Funktion X mit diesen Argumenten auf". Ausführen müssen Sie die Funktion selbst, in Ihrer Anwendung.

**MCP** setzt eine Ebene darüber an. Es legt fest, woher die Funktionsliste kommt (vom MCP-Server über `tools/list`) und wie der Aufruf ausgeführt wird (`tools/call` an den Server). Der Host übersetzt die MCP-Tools intern in das Function-Calling-Format seines Modells.

| | Function Calling | MCP |
| --- | --- | --- |
| Ebene | Modell-API eines Anbieters | Protokoll zwischen Anwendung und Server |
| Wo stehen die Funktionen | in Ihrem Anwendungscode | in einem separaten Server |
| Wiederverwendbar über Anwendungen | nein | ja |
| Format | je Anbieter leicht verschieden | einheitlich |

Kurz: Function Calling ist das "Wie entscheidet das Modell", MCP ist das "Woher kommen die Werkzeuge und wer führt sie aus".

## MCP vs. RAG

**RAG** (Retrieval-Augmented Generation) heißt: Vor der Antwort sucht ein System passende Textstellen, meist aus einer Vektordatenbank, und gibt sie dem Modell mit. RAG ist ein Muster, kein Protokoll.

MCP und RAG schließen sich nicht aus. Ein MCP-Server kann eine Suche als Tool anbieten (`search_documents(query)`) oder Dokumente als Resources bereitstellen. Der Unterschied liegt im Zeitpunkt: Klassisches RAG holt Kontext vor der Modellanfrage automatisch, bei MCP entscheidet das Modell während des Gesprächs, ob und was es nachschlägt. Für Live-Daten aus ERP oder CRM passt MCP, für große Bestände an Handbüchern und Richtlinien bleibt RAG mit Index oft die effizientere Lösung.

## Was ist ein MCP-Gateway?

Ein **MCP-Gateway** steht zwischen KI-Anwendungen und vielen MCP-Servern oder APIs. Typische Aufgaben:

- mehrere Server unter einem Endpunkt bündeln und Namenskonflikte auflösen (die Spezifikation empfiehlt dafür Präfixe),
- zentrale Anmeldung, zum Beispiel über OpenID Connect,
- Rate Limiting, Protokollierung und Freigabelisten für Tools,
- bestehende APIs oder OpenAPI-Beschreibungen in MCP-Tools übersetzen.

Ein Beispiel aus dem SAP-Umfeld ist das MCP Gateway der SAP Integration Suite: Es stellt SAP-APIs, Integrationsflüsse und OpenAPI-Spezifikationen als MCP-Tools über Streamable HTTP bereit, mit OIDC/OAuth, Rate Limiting und Monitoring (Stand laut SAP, abgerufen 16.10.2026). Ähnliche Funktionen bieten API-Management-Produkte anderer Hersteller und Open-Source-Projekte. Einen Teil davon erledigen auch Clients selbst, etwa Cursor mit einer Allowlist für Teams.

Ein Gateway lohnt sich, sobald mehrere Teams viele Server nutzen. Für einen einzelnen lokalen Server ist es meist Overhead.

## Häufige Fragen

### Was ist der Unterschied zwischen MCP und API?

Eine API ist die Schnittstelle eines Systems, die Entwickler nach Doku ansprechen. MCP ist ein Protokoll, über das KI-Anwendungen Funktionen zur Laufzeit entdecken und aufrufen. Ein MCP-Server nutzt intern meist eine API.

### Ersetzt MCP REST-APIs?

Nein. MCP setzt auf bestehende Schnittstellen auf. Für feste Abläufe zwischen Programmen bleibt die API die direkte Lösung. MCP ergänzt sie dort, wo ein Sprachmodell entscheiden soll, was es aufruft.

### MCP oder REST-API: was soll ich bauen?

Wenn Ihr System schon eine API hat und Sie KI-Anwendungen anbinden wollen, bauen Sie einen schlanken MCP-Server mit wenigen, gut beschriebenen Tools vor dieser API. Wenn es noch keine Schnittstelle gibt, brauchen Sie zuerst eine API oder einen Dateiweg. Wie ein Server entsteht, zeigt [MCP-Server erstellen](./mcp-server-erstellen.md).

### Ist MCP langsamer als ein direkter API-Aufruf?

Die Protokollschicht kostet kaum Zeit, im Test etwa 1 ms pro Aufruf im laufenden Prozess. Langsamer wird es durch das Sprachmodell, das vor und nach jedem Tool-Aufruf eine Antwort erzeugt.

### Was ist der Unterschied zwischen MCP und Function Calling?

Function Calling ist eine Fähigkeit des Modells, Funktionsaufrufe vorzuschlagen. MCP ist ein Protokoll, das festlegt, woher diese Funktionen kommen und wer sie ausführt. Hosts übersetzen MCP-Tools in das Function-Calling-Format ihres Modells.

## Weiterlesen

- [Übersicht: MCP-Server für deutsche Geschäftssysteme](../../README.md)
- [MCP-Server-Liste](../liste.md)
- [Was ist ein MCP-Server?](./was-ist-ein-mcp-server.md)
- [MCP-Server erstellen mit Python und TypeScript](./mcp-server-erstellen.md)
- [MCP-Clients einrichten: Claude, Cursor, VS Code, Codex](./mcp-clients-einrichten.md)
- [MCP-Sicherheit](./mcp-sicherheit.md)
- [MCP und DSGVO](./mcp-dsgvo.md)
- [Anleitung zum DATEV-Format (EXTF)](./datev-mcp-server.md)
- [SAP MCP-Server](./sap-mcp-server.md)
- [Power BI MCP](./power-bi-mcp.md)
- [HubSpot MCP](./hubspot-mcp.md)
- [Postgres MCP](./postgres-mcp.md)
- [Buchhaltung und MCP](./buchhaltung-mcp.md)
- [Business Central MCP](./business-central-mcp.md)

> **Hinweis:** Technische Informationen nach Stand 19.10.2026, ohne Gewähr für Vollständigkeit
> und Richtigkeit. Keine Rechts- oder Steuerberatung; die Autoren sind keine Rechtsanwälte,
> Steuerberater oder Datenschutzbeauftragten. Produktnamen sind Marken ihrer Inhaber; es besteht
> keine Verbindung zu den genannten Herstellern.
>
> Die Autoren erbringen keine Hilfeleistung in Steuersachen im Sinne des Steuerberatungsgesetzes.
> Ob und wie Buchungen steuerlich richtig sind, klären Sie mit Ihrer Steuerberatung. DATEV ist
> eine Marke der DATEV eG; dieses Projekt ist kein Produkt der DATEV eG und nicht von ihr geprüft
> oder freigegeben.
