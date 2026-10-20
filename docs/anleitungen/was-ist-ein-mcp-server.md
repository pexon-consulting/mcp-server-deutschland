# Was ist ein MCP-Server? Model Context Protocol einfach erklärt

Ein MCP-Server ist ein kleines Programm, das einer KI-Anwendung wie Claude, ChatGPT, Cursor oder VS Code Werkzeuge und Daten über ein einheitliches Protokoll bereitstellt: das Model Context Protocol (MCP). Diese Anleitung erklärt Begriff, Rollen, Bausteine und Transportwege, zeigt die Änderungen der Spezifikation 2026-07-28 und nennt typische Einsätze in deutschen Unternehmen.

Stand: 19.10.2026. Spezifikation: MCP 2026-07-28. Teil der Sammlung [MCP-Server für Geschäftssysteme in Deutschland](../liste.md).

Für: Fachleute aus IT, Controlling und Geschäftsführung, die verstehen wollen, was hinter "MCP" steckt, und Entwickler, die einen schnellen Überblick suchen.

## Inhaltsverzeichnis

- [Das Wichtigste in Kürze](#das-wichtigste-in-kürze)
- [MCP-Server: Erklärung und Bedeutung](#mcp-server-erklärung-und-bedeutung)
- [Die drei Rollen: Host, Client und Server](#die-drei-rollen-host-client-und-server)
- [Bausteine: Tools, Resources und Prompts](#bausteine-tools-resources-und-prompts)
- [Transportwege: stdio und Streamable HTTP](#transportwege-stdio-und-streamable-http)
- [So sieht eine MCP-Nachricht aus](#so-sieht-eine-mcp-nachricht-aus)
- [Was sich mit der Spezifikation 2026-07-28 geändert hat](#was-sich-mit-der-spezifikation-2026-07-28-geändert-hat)
- [Typische Einsätze in deutschen Unternehmen](#typische-einsätze-in-deutschen-unternehmen)
- [Die MCP Registry](#die-mcp-registry)
- [Grenzen von MCP](#grenzen-von-mcp)
- [Häufige Fragen](#häufige-fragen)
- [Weiterlesen](#weiterlesen)

## Das Wichtigste in Kürze

- MCP ist ein offenes Protokoll auf Basis von JSON-RPC 2.0. Es legt fest, wie eine KI-Anwendung Werkzeuge findet, aufruft und Daten liest.
- Ein **MCP-Server** stellt Fähigkeiten bereit, zum Beispiel "Buchungsstapel prüfen" oder "Feiertage eines Bundeslands auflisten". Ein **MCP-Client** in der KI-Anwendung nutzt sie.
- Die drei wichtigsten Bausteine heißen **Tools** (Funktionen), **Resources** (lesbare Inhalte) und **Prompts** (vorbereitete Vorlagen).
- Es gibt zwei Standard-Transportwege: **stdio** für lokale Prozesse und **Streamable HTTP** für Server im Netz.
- Die aktuelle Spezifikation 2026-07-28 macht MCP **zustandslos**: Es gibt keinen `initialize`-Handshake und keine Sitzungen mehr, dafür die neue Methode `server/discover`. Viele bestehende Server laufen noch auf 2025-11-25.
- MCP ersetzt keine API. Lizenzen, Freigaben und Rate Limits des Zielsystems gelten weiter.

## MCP-Server: Erklärung und Bedeutung

Die Abkürzung MCP steht für **Model Context Protocol**. "Context" meint alles, was ein Sprachmodell über die eigentliche Frage hinaus braucht: Daten aus dem ERP, eine Tabelle aus der Datenbank, eine Funktion zum Anlegen eines CRM-Kontakts. Das Protokoll wurde am 25.11.2024 von Anthropic als offener Standard veröffentlicht ([Ankündigung](https://www.anthropic.com/news/model-context-protocol), abgerufen 19.10.2026). Die Spezifikation liegt heute unter [modelcontextprotocol.io/specification](https://modelcontextprotocol.io/specification/2026-07-28).

Vor MCP musste jede KI-Anwendung jede Schnittstelle selbst anbinden. Zehn Anwendungen und zehn Systeme ergaben bis zu hundert Einzelintegrationen. Mit MCP schreibt der Anbieter eines Systems einmal einen Server, und jede MCP-fähige Anwendung kann ihn nutzen. Die Spezifikation nennt das Language Server Protocol aus der Editor-Welt als Vorbild: Auch dort spricht ein Editor mit beliebigen Sprachservern über ein gemeinsames Protokoll.

Ein MCP-Server ist dabei kein großer Dienst. Oft ist es ein Python- oder Node-Programm mit wenigen hundert Zeilen, das lokal neben der KI-Anwendung startet. Er kann aber auch ein gehosteter Dienst sein, etwa der Remote-Server von HubSpot unter `https://mcp.hubspot.com`.

## Die drei Rollen: Host, Client und Server

Die Spezifikation unterscheidet drei Rollen ([Specification, Overview](https://modelcontextprotocol.io/specification/2026-07-28), abgerufen 19.10.2026):

| Rolle | Was sie ist | Beispiel |
| --- | --- | --- |
| Host | Die KI-Anwendung, mit der Sie arbeiten. Sie startet die Verbindungen und holt Ihre Zustimmung ein. | Claude Desktop, Claude Code, Cursor, VS Code mit Copilot, Codex |
| Client | Die Verbindungskomponente im Host, je eine pro Server | der MCP-Client in Cursor, der mit Ihrem Postgres-Server spricht |
| Server | Das Programm, das Fähigkeiten bereitstellt | ein EXTF-Server, der Power-BI-Server von Microsoft |

Ein Host kann mehrere Clients gleichzeitig halten, also mehrere Server parallel nutzen. Das Sprachmodell selbst ist keine Rolle im Protokoll. Es sieht nur, was der Host ihm an Tool-Beschreibungen und Ergebnissen weitergibt.

Wichtig für die Sicherheit: Der Host ist für Ihre Zustimmung zuständig. Die Spezifikation verlangt, dass Hosts vor jedem Tool-Aufruf eine ausdrückliche Zustimmung einholen und Beschreibungen von Tools als nicht vertrauenswürdig behandeln, solange der Server nicht vertrauenswürdig ist.

## Bausteine: Tools, Resources und Prompts

Ein Server kann drei Arten von Fähigkeiten anbieten. Welche er unterstützt, meldet er in seinen `capabilities`.

| Baustein | Wer steuert ihn | Wofür | Beispiel |
| --- | --- | --- | --- |
| Tools | das Modell | Funktionen mit Eingabeschema, die etwas berechnen, lesen oder ändern | `count_working_days(start, end, state)` |
| Resources | die Anwendung oder der Nutzer | lesbare Inhalte mit URI, etwa Dateien oder Tabellen | `file:///berichte/2026-09.csv` |
| Prompts | der Nutzer | vorbereitete Vorlagen und Abläufe | "Monatsabschluss prüfen" mit Parameter Monat |

**Tools** sind der meistgenutzte Baustein. Jedes Tool hat einen Namen, eine Beschreibung, ein `inputSchema` (JSON Schema, Standard ist Version 2020-12) und optional ein `outputSchema`. Ergebnisse kommen als `content` (Text, Bild, Audio, Links) und optional als `structuredContent`, also als maschinenlesbares JSON. Zusätzlich kann ein Tool **Annotations** tragen, zum Beispiel `readOnlyHint: true` für "ändert nichts". Diese Hinweise sind laut Spezifikation nur Hinweise; ein Client darf ihnen nur bei vertrauenswürdigen Servern folgen.

**Resources** eignen sich für Inhalte, die eher gelesen als ausgeführt werden. Ein Server kann sie auflisten (`resources/list`), Vorlagen anbieten (`resources/templates/list`) und Änderungen melden.

**Prompts** sind Vorlagen, die Sie in der Anwendung bewusst auswählen, zum Beispiel über einen Slash-Befehl.

Daneben gibt es eine Fähigkeit in der Gegenrichtung: Mit **Elicitation** fragt der Server über den Client bei Ihnen nach, etwa nach einer fehlenden Angabe. Passwörter, API-Schlüssel und Token darf ein Server laut Spezifikation nicht per Formular abfragen, dafür ist der URL-Modus vorgesehen. Die älteren Client-Fähigkeiten **Roots** und **Sampling** sind seit 2026-07-28 abgekündigt (dazu unten mehr).

## Transportwege: stdio und Streamable HTTP

Die Spezifikation definiert zwei Standard-Transporte ([Transports](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports), abgerufen 19.10.2026):

| Merkmal | stdio | Streamable HTTP |
| --- | --- | --- |
| Wo läuft der Server | als Unterprozess auf Ihrem Rechner | auf einem Server im Netz oder lokal |
| Wer startet ihn | der Client | der Betreiber |
| Nachrichten | eine JSON-RPC-Nachricht pro Zeile über stdin und stdout | jede Nachricht als HTTP-POST an einen Endpunkt, Antwort als JSON oder SSE-Stream |
| Anmeldung | Zugangsdaten aus Umgebungsvariablen | OAuth 2.1 nach MCP-Autorisierungsspezifikation empfohlen |
| Typischer Fall | Datenbank im Firmennetz, lokale Dateien, Entwicklung | SaaS-Dienste wie HubSpot, Business Central, Atlassian |

Bei **stdio** gilt eine Regel, die viele Einsteiger überrascht: Der Server darf auf stdout ausschließlich gültige MCP-Nachrichten schreiben. Ein einzelnes `print("Hallo")` zerstört die Verbindung. Logs gehören nach stderr. Das zeigt die Anleitung [MCP-Server erstellen](./mcp-server-erstellen.md) an einem Beispiel.

Bei **Streamable HTTP** verlangt die Spezifikation, dass Server den `Origin`-Header prüfen (Schutz gegen DNS-Rebinding) und lokal an `127.0.0.1` statt `0.0.0.0` binden. Der ältere Transport **HTTP+SSE** ist seit 2025-03-26 abgekündigt. Eigene Transporte sind erlaubt; über Byte-Streams sollen sie die stdio-Rahmung übernehmen.

## So sieht eine MCP-Nachricht aus

MCP ist JSON-RPC 2.0. Eine Anfrage hat `jsonrpc`, `id`, `method` und `params`. Seit 2026-07-28 trägt jede Anfrage in `params._meta` die Protokollversion und die Fähigkeiten des Clients. So sieht ein echter Tool-Aufruf an den Beispielserver aus [MCP-Server erstellen](./mcp-server-erstellen.md) aus, geschickt als eine Zeile an stdin:

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_holidays","arguments":{"year":2026,"state":"SN"},"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientCapabilities":{},"io.modelcontextprotocol/clientInfo":{"name":"handtest","version":"0.0.1"}}}}
```

Die Antwort des Servers (gekürzt, echte Ausgabe vom 19.10.2026):

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "resultType": "complete",
    "content": [{"type": "text", "text": "{\n  \"year\": 2026,\n  \"state\": \"SN\", ..."}],
    "structuredContent": {
      "year": 2026,
      "state": "SN",
      "state_name": "Sachsen",
      "count": 11,
      "holidays": [
        {"date": "2026-11-18", "name": "Buß- und Bettag", "weekday": "Mittwoch", "nationwide": false}
      ]
    },
    "isError": false,
    "_meta": {"io.modelcontextprotocol/serverInfo": {"name": "feiertage", "version": "0.1.0"}}
  }
}
```

Fehlt `_meta`, lehnt ein Server nach 2026-07-28 die Anfrage mit dem Fehlercode `-32602` ab. Genau das meldete der Python-Beispielserver im Test: `params._meta must be an object carrying the required 'io.modelcontextprotocol/protocolVersion' and 'io.modelcontextprotocol/clientCapabilities' envelope keys`.

## Was sich mit der Spezifikation 2026-07-28 geändert hat

Die Version 2026-07-28 ist die erste große Revision nach 2025-11-25. Versionsnummern sind Datumsangaben und markieren die letzte nicht abwärtskompatible Änderung. Die wichtigsten Punkte laut [Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) (abgerufen 19.10.2026):

**Zustandslos statt Sitzung.** Der Handshake aus `initialize` und `notifications/initialized` entfällt. Jede Anfrage bringt ihre Protokollversion und Client-Fähigkeiten selbst mit. Ein Server darf sich nicht darauf verlassen, dass frühere Anfragen auf derselben Verbindung etwas festgelegt haben. Wer Zustand über mehrere Aufrufe braucht, gibt eine explizite Kennung zurück (etwa eine Warenkorb-ID), die das Modell beim nächsten Aufruf mitschickt.

**Keine Protokoll-Sitzungen bei HTTP.** Der Header `Mcp-Session-Id` ist entfernt. Dafür sind bei Streamable HTTP die Header `Mcp-Method` und `Mcp-Name` Pflicht, damit Proxys und Firewalls Anfragen ohne Blick in den Body zuordnen können.

**Neue Pflichtmethode `server/discover`.** Damit fragt ein Client vorab, welche Protokollversionen, Fähigkeiten und Identität ein Server hat. Auf stdio dient `server/discover` auch als Probe: Antwortet der Server nicht passend, fällt der Client auf den alten `initialize`-Handshake zurück.

**Multi Round-Trip Requests (MRTR).** Früher konnte ein Server mitten in einem Aufruf selbst Anfragen an den Client stellen (`sampling/createMessage`, `elicitation/create`, `roots/list`). Jetzt antwortet er mit `resultType: "input_required"`, und der Client wiederholt die ursprüngliche Anfrage mit `inputResponses`. Jedes Ergebnis trägt deshalb das Pflichtfeld `resultType`.

**Abonnements neu.** `subscriptions/listen` ersetzt den HTTP-GET-Endpunkt und `resources/subscribe`.

**Entfernt:** `ping`, `logging/setLevel`, `notifications/roots/list_changed` und die Wiederaufnahme von SSE-Streams über `Last-Event-ID`. Tasks wanderten aus dem Kern in die offizielle Erweiterung `io.modelcontextprotocol/tasks`.

**Kleinere Änderungen:** `tools/list` soll eine stabile Reihenfolge liefern. Listen- und Leseergebnisse tragen Pflichtfelder `ttlMs` und `cacheScope` als Cache-Hinweise. Mit `x-mcp-header` kann ein Tool-Parameter als HTTP-Header gespiegelt werden. In Schemas ist JSON Schema 2020-12 vollständig erlaubt.

**Abgekündigt (deprecated)** sind laut [Deprecated-Liste](https://modelcontextprotocol.io/specification/2026-07-28/deprecated) (abgerufen 19.10.2026):

| Funktion | Empfohlener Ersatz |
| --- | --- |
| Roots | Pfade als Tool-Parameter, Resource-URI oder Serverkonfiguration übergeben |
| Sampling | den LLM-Anbieter direkt aufrufen |
| Logging über das Protokoll | nach stderr schreiben (stdio) oder OpenTelemetry nutzen |
| Dynamic Client Registration (RFC 7591) | Client ID Metadata Documents |
| HTTP+SSE-Transport | Streamable HTTP |
| `includeContext: "thisServer"` und `"allServers"` | Feld weglassen oder `"none"` |

Abgekündigte Funktionen bleiben vorerst nutzbar. Laut Richtlinie gilt ein Zeitfenster von mindestens zwölf Monaten; frühestens die erste Revision ab dem 28.07.2027 darf sie entfernen.

Für die Praxis heißt das: Viele Server und Clients sprechen noch 2025-11-25. Shopware zum Beispiel betreibt seinen eingebauten Server laut eigener Doku mit dem sitzungsbasierten Protokoll 2025-11-25 und hat den zustandslosen Modus abgeschaltet. Die offiziellen SDKs (Python `mcp` 2.x, TypeScript `@modelcontextprotocol/server` 2.x) sprechen beide Versionen: Der Python-Client probiert zuerst `server/discover` und fällt sonst auf `initialize` zurück.

## Typische Einsätze in deutschen Unternehmen

Die [Sammelliste](../liste.md) führt MCP-Server für Geschäftssysteme mit Stand, Lizenz, Auth und Lese- oder Schreibzugriff auf. Vier Beispiele zeigen, wie verschieden die Lage je System ist:

**DATEV.** Einen offiziellen MCP-Server der DATEV eG gibt es nach unserem Stand nicht. Es existieren einige kleine Community-Server, die meist mit dem Dateiformat EXTF (DATEV-Format, Buchungsstapel) arbeiten, plus kommerzielle Schichten. Die DATEV-Cloud-APIs stehen auch ohne Partnerschaft offen, setzen aber Registrierung, Abonnement und für den Produktivbetrieb eine technische Prüfung durch DATEV voraus. Ohne eigenen API-Zugang über das DATEV Developer Portal ist das Dateiformat EXTF der einfachste Weg: eine Datei, die lokal erzeugt und geprüft wird und dann per Import in DATEV landet. Details in der [Anleitung zum DATEV-Format (EXTF)](./datev-mcp-server.md).

**SAP.** SAP veröffentlicht mehrere offizielle MCP-Server, vor allem für Entwicklung (Fiori, CAP, UI5, ABAP Development Tools). Für den Zugriff auf Geschäftsdaten bietet die SAP Integration Suite ein MCP Gateway, das SAP-APIs und Integrationsflüsse als MCP-Tools über Streamable HTTP mit OAuth bereitstellt. Mehr in [SAP MCP-Server](./sap-mcp-server.md).

**Power BI.** Microsoft nennt zwei Wege: den Power BI Authoring MCP Server zum Anlegen und Ändern semantischer Modelle (lokal per stdio oder gehostet als Vorschau) und für Abfragen den Fabric IQ MCP Server bzw. den früheren Remote-Endpunkt. Siehe [Power BI MCP](./power-bi-mcp.md).

**HubSpot.** Der offizielle CRM-Server läuft nur remote unter `https://mcp.hubspot.com` mit OAuth und PKCE. Schreibende Aktionen verlangen eine Bestätigung der vorgeschlagenen Änderungen. Daneben gibt es einen lokalen Developer-Server für die App-Entwicklung, der keine CRM-Daten liest. Siehe [HubSpot MCP](./hubspot-mcp.md).

Weitere häufige Fälle sind Datenbanken ([Postgres MCP](./postgres-mcp.md); der offizielle Referenzserver ist archiviert), ERP-Systeme wie [Business Central](./business-central-mcp.md) mit offiziellem Remote-Server und Buchhaltungsprogramme ([Buchhaltung und MCP](./buchhaltung-mcp.md)).

## Die MCP Registry

Unter [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io) betreibt das MCP-Projekt eine offizielle Registry. Sie speichert nur Metadaten (Name, Version, Paket, Transport), nicht den Code. Die API ist seit 24.10.2025 als v0.1 eingefroren; eine allgemeine Verfügbarkeit (v1) ist laut README angekündigt, eine Meldung dazu haben wir nicht gefunden.

So durchsuchen Sie die Registry per API:

```bash
curl -s "https://registry.modelcontextprotocol.io/v0.1/servers?search=datev&limit=5" \
  | jq -c '.servers[] | {name: .server.name, version: .server.version}'
```

Am 16.10.2026 lieferte die Suche nach "datev" zwei Server (`engineering.seamless/datev-extf` und `io.github.igorkazazic1989/beleg2datev-mcp`), nach "hubspot" 26 Einträge, alle aus der Community. Bei unserer Kontrolle am 19.10.2026 antwortete die Registry nicht innerhalb von 40 Sekunden. Planen Sie Ausfälle ein, wenn Sie die API automatisiert nutzen.

Ein Eintrag in der Registry ist keine Prüfung. Die Registry bestätigt, dass der Namensraum (zum Beispiel `io.github.<konto>/...`) dem Veröffentlicher gehört, nicht, dass der Server sicher oder fachlich richtig ist. Wie Sie selbst veröffentlichen, steht in [MCP-Server erstellen](./mcp-server-erstellen.md#veröffentlichen-in-der-mcp-registry).

## Grenzen von MCP

MCP ist ein Protokoll, keine Lösung für alles. Diese Grenzen sollten Sie kennen:

- **Kein Ersatz für die API.** Ein MCP-Server ruft meist eine bestehende API auf. Deren Lizenz, Tarif, Partnerfreigabe und Rate Limits gelten weiter. Für DATEV-Online-APIs etwa ist ein Freigabeprozess nötig, die lexware-office-API setzt den Tarif XL voraus. Der Vergleich steht in [MCP vs. API](./mcp-vs-api.md).
- **Kontext kostet Token.** Jede Tool-Beschreibung landet im Kontext des Modells. Die `tools/list`-Antwort des kleinen Beispielservers mit zwei Tools ist bereits 3.197 Byte groß. Viele Server mit vielen Tools machen Anfragen teurer und das Modell unsicherer bei der Auswahl.
- **Untrusted Input.** Tool-Beschreibungen und Tool-Ergebnisse sind Text, den das Modell liest. Ein manipulierter Server oder ein präparierter Datensatz kann versuchen, das Modell zu unerwünschten Aufrufen zu bewegen. Die Spezifikation verlangt deshalb einen Menschen, der Aufrufe ablehnen kann. Mehr in [MCP-Sicherheit](./mcp-sicherheit.md).
- **Datenschutz.** Ergebnisse eines Tools gehen an den Anbieter des Sprachmodells. Für personenbezogene Daten brauchen Sie eine Rechtsgrundlage und meist einen Auftragsverarbeitungsvertrag. Siehe [MCP und DSGVO](./mcp-dsgvo.md).
- **Uneinheitlicher Stand.** Server und Clients sprechen verschiedene Protokollversionen und unterstützen nicht alle Bausteine. Manche Clients zeigen Prompts oder Resources nicht an.
- **Qualität schwankt.** Viele Community-Server sind kleine Projekte mit einstelliger Sternzahl. Prüfen Sie Code, Lizenz und Pflege, bevor Sie einen Server an produktive Daten lassen.

## Häufige Fragen

### Was ist ein MCP-Server einfach erklärt?

Ein MCP-Server ist ein Adapter zwischen einer KI-Anwendung und einem System wie einer Datenbank, einem CRM oder einer Buchhaltung. Er beschreibt, welche Funktionen er anbietet, und führt sie auf Anfrage aus. Die KI-Anwendung spricht mit allen Servern über dasselbe Protokoll.

### Was bedeutet MCP?

MCP steht für Model Context Protocol. Es ist ein offenes Protokoll auf Basis von JSON-RPC 2.0, das Anthropic im November 2024 veröffentlicht hat. Inzwischen unterstützen es unter anderem Claude, ChatGPT, Cursor, VS Code und Codex.

### Brauche ich zum Nutzen eines MCP-Servers Programmierkenntnisse?

Für fertige Server meist nicht. Sie tragen einen Startbefehl oder eine URL in die Konfiguration Ihrer KI-Anwendung ein. Wie das je Anwendung geht, zeigt [MCP-Clients einrichten](./mcp-clients-einrichten.md). Für eigene Server brauchen Sie Python oder TypeScript.

### Ist ein MCP-Server sicher?

Das hängt vom Server ab. Ein lokaler Server läuft mit Ihren Benutzerrechten und kann alles, was Sie können. Nutzen Sie Server aus nachvollziehbarer Quelle, geben Sie nur die nötigen Rechte und bestätigen Sie schreibende Aufrufe. Details in [MCP-Sicherheit](./mcp-sicherheit.md).

### Was ist der Unterschied zwischen MCP-Server und API?

Eine API ist die Schnittstelle eines Systems, ein MCP-Server ist eine standardisierte Hülle darum, die KI-Anwendungen zur Laufzeit verstehen. Der Server entdeckt sich selbst über `tools/list`, die API braucht eine eigene Integration je Anwendung. Ausführlich in [MCP vs. API](./mcp-vs-api.md).

### Gibt es einen offiziellen DATEV-MCP-Server?

Nach unserem Stand vom 19.10.2026 nein. Es gibt Community-Server, die meist mit EXTF-Dateien arbeiten. Eine Übersicht steht in der [Anleitung zum DATEV-Format (EXTF)](./datev-mcp-server.md) und in der [Liste](../liste.md).

## Weiterlesen

- [Übersicht: MCP-Server für deutsche Geschäftssysteme](../../README.md)
- [MCP-Server-Liste](../liste.md)
- [MCP vs. API: Unterschied und wann Sie was brauchen](./mcp-vs-api.md)
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
