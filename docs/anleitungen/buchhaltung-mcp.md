# MCP Buchhaltung: lexoffice, sevdesk, DATEV und weitere Server

Diese Übersicht richtet sich an Selbstständige, Buchhaltung und IT in kleinen und mittleren Unternehmen, die einen KI-Assistenten über MCP an ihre Buchhaltungssoftware anbinden wollen. Sie zeigt, welche Server es für lexware office, sevdesk, DATEV und andere gibt, was die Hersteller-APIs voraussetzen und wo ein Assistent in der Buchhaltung Grenzen braucht.

Stand: 19.10.2026

## Inhaltsverzeichnis

- [Das Wichtigste in Kürze](#das-wichtigste-in-kürze)
- [Offiziell oder Community: warum das wichtig ist](#offiziell-oder-community-warum-das-wichtig-ist)
- [Übersicht: MCP-Server für Buchhaltungssoftware](#übersicht-mcp-server-für-buchhaltungssoftware)
- [lexware office (lexoffice) MCP](#lexware-office-lexoffice-mcp)
- [sevdesk MCP](#sevdesk-mcp)
- [DATEV MCP](#datev-mcp)
- [BuchhaltungsButler, GetMyInvoices, Candis, Norman und weitere](#buchhaltungsbutler-getmyinvoices-candis-norman-und-weitere)
- [Was ein KI-Assistent in der Buchhaltung darf und was nicht](#was-ein-ki-assistent-in-der-buchhaltung-darf-und-was-nicht)
- [GoBD: Unveränderbarkeit, Protokollierung, Verfahrensdokumentation](#gobd-unveränderbarkeit-protokollierung-verfahrensdokumentation)
- [Einrichtung: ein Community-Server im Lesemodus](#einrichtung-ein-community-server-im-lesemodus)
- [E-Rechnungen: XRechnung und ZUGFeRD per MCP](#e-rechnungen-xrechnung-und-zugferd-per-mcp)
- [Checkliste vor dem Start](#checkliste-vor-dem-start)
- [Häufige Fragen](#häufige-fragen)
- [Weiterlesen](#weiterlesen)

## Das Wichtigste in Kürze

- Für lexware office, sevdesk und DATEV gab es am 19.10.2026 keinen MCP-Server des Herstellers. Es gibt aber mehrere Community-Server.
- Die lexware-office-API setzt den Tarif XL voraus, erlaubt laut Doku 2 Anfragen pro Sekunde und untersagt Lasttests. Polling soll vermieden werden.
- Die sevdesk-API ist laut Hilfe-Center ab dem Tarif "Buchhaltung Pro" enthalten. Der Token steht im Header `Authorization` ohne das Präfix `Bearer`.
- DATEV bietet keinen MCP-Server an. Die Cloud-APIs von DATEV sind auch ohne Partnerschaft nutzbar, setzen aber Registrierung im Developer Portal, ein Abonnement und für den Produktivbetrieb eine technische Prüfung durch DATEV voraus. Ohne API-Zugang ist das Dateiformat EXTF der einfachste Weg.
- Offizielle MCP-Server mit Buchhaltungsbezug gibt es zum Beispiel bei GetMyInvoices (nur lesend) und Candis (nur Entwickler-Doku, keine Buchhaltungsdaten).
- Ein Assistent sollte lesen und Entwürfe anlegen dürfen. Festschreiben, Versenden und Bezahlen gehören hinter eine menschliche Freigabe.
- Die API-Bedingungen ändern sich. Prüfen Sie jede Angabe hier vor dem Einsatz selbst in der Quelle.

## Offiziell oder Community: warum das wichtig ist

"Offiziell" heißt in dieser Übersicht: Der Hersteller der Buchhaltungssoftware betreibt oder veröffentlicht den MCP-Server selbst. "Community" heißt: Ein Dritter hat einen Server auf Basis der öffentlichen API gebaut. Das sagt nichts über die Qualität, wohl aber über diese Punkte:

- **Support**: Bei Fehlern im Community-Server hilft Ihnen der Hersteller der Buchhaltungssoftware nicht.
- **Rechte**: Ein Community-Server nutzt Ihren API-Schlüssel. Der hat oft alle Rechte Ihres Benutzers. Der sevdesk-Server `joosthel/sevdesk-mcp` schreibt dazu im README, ein sevdesk-API-Token habe "no scopes".
- **Pflege**: Ändert der Hersteller seine API, kann ein Community-Server ausfallen, bis der Autor nachzieht.
- **Lizenzbedingungen**: Manche APIs erlauben die Nutzung nur für "eigene Anwendungen". Ein gehosteter Dienst eines Dritten kann damit kollidieren.

Lesen Sie vor der Auswahl den Quelltext oder lassen Sie ihn lesen, prüfen Sie Lizenz, letzte Änderung und ob der Server einen Lesemodus hat. Die Kriterien dazu stehen in [MCP-Sicherheit](./mcp-sicherheit.md).

## Übersicht: MCP-Server für Buchhaltungssoftware

| System | Offizieller MCP-Server | Community-Server (Auswahl, GitHub am 19.10.2026) | API-Voraussetzung |
| --- | --- | --- | --- |
| lexware office | keiner gefunden | `JannikWempe/mcp-lexware-office` (MIT, 69 Sterne), `marselsel/Lexware-MCP-Server` (MIT, 42), `lazyants/lexware-mcp-server` (8) | Tarif XL, API-Key |
| sevdesk | keiner gefunden | `joosthel/sevdesk-mcp` (MIT, 6), `codestra/sevdesk-mcp` (ohne Lizenzangabe, 6), `Honeyfield-Org/sevdesk-mcp` (1) | ab "Buchhaltung Pro", API-Token |
| DATEV | keiner | `ppronobis/datev-mcp-server` (MIT, 5), `BadRix90/datev-mcp` (MIT, 2), `seamless-engineering/datev-extf-mcp` (MIT, 0) | Developer Portal, Freigabe; EXTF als Datei |
| BuchhaltungsButler | keiner gefunden | `ohneben/Buchhaltungsbutler-MCP` (MIT, 9) und weitere kleine Projekte | API Client und Secret |
| GetMyInvoices | ja, gehostet, nur lesend | - | in allen Tarifen laut Hersteller |
| Candis | ja, aber nur Entwickler-Doku | - | Candis-API per OAuth 2.0 |
| Norman | laut eigenem Blog ja | - | Herstellerangabe, nicht geprüft |

"Keiner gefunden" bedeutet: In der Hersteller-Doku und bei einer Websuche am 19.10.2026 war kein offizieller Server zu finden. Das kann sich schnell ändern. Die vollständige, gepflegte Liste mit Lizenz, Transport und Lesen/Schreiben steht in der [Sammelliste](../liste.md).

## lexware office (lexoffice) MCP

lexoffice heißt seit 2025 lexware office. Suchanfragen wie "lexoffice mcp" und "lexware mcp" meinen dasselbe Produkt.

### Server

Einen MCP-Server von Lexware selbst gab es am 19.10.2026 nicht. Die Partnerseite (https://www.lexware.de/partner/public-api/) beschreibt nur die REST-API. Community-Server, jeweils laut README:

- `JannikWempe/mcp-lexware-office`: lokal per stdio, standardmäßig nur lesend ("Read-only by default: writes require explicit opt-in via environment variable"), laut README auf Basis des TypeScript-SDK v2 mit Protokoll 2026-07-28.
- `marselsel/Lexware-MCP-Server`: selbst gehosteter Remote-Server mit OAuth 2.1 oder statischem Bearer-Token. Drei Stufen: Lesen (immer aktiv), Entwürfe (Standard an), Festschreiben (Standard aus). Das README warnt: "finalized invoices are legally binding".
- `lazyants/lexware-mcp-server`: lokal per npx, aufgeteilt in mehrere Teil-Server, um die Zahl der Werkzeuge zu begrenzen. Lizenzangabe auf GitHub: NOASSERTION.

### API-Voraussetzungen

Diese Punkte stammen aus der Entwickler-Doku und dem Hilfe-Center, abgerufen am 16.10.2026:

- **Tarif**: Die Public API ist nur ab "Lexware Office XL" nutzbar, in S, M und L lässt sich kein Schlüssel erzeugen (https://help.lexware.de/de-form/articles/548863-alles-rund-um-public-api).
- **Basis-URL**: `https://api.lexware.io`, Authentifizierung mit `Authorization: Bearer <API-Key>`. Der Schlüssel wird unter https://app.lexware.de/addons/public-api erzeugt, kann eingeschränkte Rechte haben und gilt höchstens 24 Monate (https://developers.lexware.io/docs/).
- **Rate Limit**: 2 Anfragen pro Sekunde über alle Endpunkte, bei Überschreitung HTTP 429. Das Limit kann laut Doku kurzfristig geändert werden.
- **Kein Polling, keine Lasttests**: "Polling von Ressourcen ist unbedingt zu vermeiden", stattdessen Webhooks. Performance- und Lasttests über die Public API sind nicht erlaubt (https://developers.lexware.io/cookbooks/public-api/).
- **Testkonto**: kostenlos für 30 Tage mit XL-Funktionen, eine dauerhafte Sandbox gibt es nicht.
- **Nutzungsbedingungen**: Die Lizenz- und Nutzungsbedingungen (https://agb.lexware.de/lexware-office/public-api-lizenz--und-nutzungsbedingungen) erlauben laut einer Zusammenfassung die Nutzung für eigene Anwendungen und schließen Unterlizenzen aus. Den Wortlaut haben wir nicht selbst geprüft. Lesen Sie ihn, bevor Sie einen gehosteten Dienst eines Dritten mit Ihrem Schlüssel betreiben lassen.

Für MCP heißt das: Ein Assistent, der in einer Schleife Belege abfragt, stößt schnell an 2 Anfragen pro Sekunde. Ein guter Server fasst Abfragen zusammen und wiederholt bei 429 erst nach einer Pause.

```bash
curl -s -H "Authorization: Bearer $LEXWARE_API_KEY" -H "Accept: application/json" \
  "https://api.lexware.io/v1/voucherlist?voucherType=invoice&voucherStatus=open"
```

Dieser Aufruf ist nicht getestet (kein XL-Konto im Test). Er zeigt nur die Form laut Doku.

## sevdesk MCP

### Server

Einen offiziellen sevdesk-MCP-Server gab es am 19.10.2026 nicht. Community-Server, laut README:

- `joosthel/sevdesk-mcp`: alle API-Operationen, Schreibschutz über `SEVDESK_READ_ONLY=true`, dazu Prüfwerkzeuge für typische Fehlbuchungen (zum Beispiel Reverse Charge nach § 13b UStG). Lizenz MIT, letzter Push 20.08.2026.
- `codestra/sevdesk-mcp`: ohne Lizenzangabe auf GitHub. Ohne Lizenz räumt der Autor keine Nutzungsrechte ein, die über die GitHub-Nutzungsbedingungen (Ansehen und Forken auf GitHub) hinausgehen. Kopieren, Ändern und Weitergeben sind dann grundsätzlich nicht erlaubt.
- `Honeyfield-Org/sevdesk-mcp`: 52 Werkzeuge laut README, letzter Push 16.02.2026.

### API-Voraussetzungen

- **Tarif**: Die REST-API ist ab "Buchhaltung Pro" enthalten (sevdesk-Systemversion 2.0, Deutschland), laut https://hilfe.sevdesk.de/de/articles/9374668-sevdesk-api, abgerufen am 16.10.2026.
- **Basis-URL**: `https://my.sevdesk.de/api/v1`. Die OpenAPI-Spezifikation liegt unter https://api.sevdesk.de/openapi.yaml ("sevdesk API 2.0.0", 119 Pfade).
- **Authentifizierung**: Header `Authorization` mit dem 32-stelligen Token, **ohne** `Bearer`. Die Übergabe im URL-Parameter wurde am 29.04.2025 abgeschaltet (https://tech.sevdesk.com/api_news/posts/2025_02_06-authentication-method-removed/).
- **Paginierung**: `limit` muss eine Zahl von 1 bis 1000 sein, sonst antwortet die API mit 400 (seit 30.05.2025).
- **Rate Limit**: Eine veröffentlichte Zahl haben wir nicht gefunden.
- **Export**: Die API hat Endpunkte für DATEV-Exporte, etwa `/Export/datevCSV` und `/Export/createDatevCsvZipExportJob`.

```bash
curl -s -H "Authorization: $SEVDESK_API_TOKEN" \
  "https://my.sevdesk.de/api/v1/Invoice?status=200&limit=50"
```

Auch dieser Aufruf ist nicht getestet. Achten Sie auf den Header: `Authorization: Bearer ...` funktioniert bei sevdesk laut OpenAPI-Spezifikation nicht.

## DATEV MCP

### Kein offizieller Server

DATEV stellt keinen MCP-Server bereit. Das DATEV Developer Portal (https://developer.datev.de/de/) beschreibt API-Produkte mit OAuth 2.0 und OpenID Connect, aber keinen MCP-Endpunkt. Für Suchanfragen wie "datev mcp", "datev claude mcp" oder "datev unternehmen online mcp" gibt es deshalb nur Community-Projekte und kommerzielle Zwischenschichten.

### Welche Wege es gibt

- **DATEV-Cloud-APIs**: auch ohne Partnerschaft zugänglich. Registrierung im Developer Portal, App anlegen, API-Produkte abonnieren, dann Sandbox. Für die Produktion ist eine technische Abnahme nötig, Cloud-Integrationen Dritter durchlaufen einen Freigabeprozess (https://developer.datev.de/de/guides/interface-requirements). Access Tokens gelten 15 Minuten.
- **DATEVconnect**: ein lokaler REST-Dienst im Firmennetz, der eine installierte DATEV-Umgebung voraussetzt. Ohne DATEV-Installation lässt er sich nicht testen. Details dazu haben wir nur aus Sekundärquellen.
- **EXTF-Datei (DATEV-Format, Buchungsstapel)**: eine CSV-Datei mit festem Kopf, die Ihre Steuerberatung in DATEV einliest. Das geht offline und ohne API-Zugang.

### Server

- `ppronobis/datev-mcp-server`, `BadRix90/datev-mcp`: kleine Community-Projekte, MIT.
- `seamless-engineering/datev-extf-mcp`: prüft und schreibt EXTF-Dateien lokal, im offiziellen MCP-Registry als `engineering.seamless/datev-extf`.
- Kommerzielle Zwischenschichten wie belege.ai bieten laut Herstellerseite einen nur lesenden Remote-MCP mit OAuth 2.1 und PKCE.

Dieses Repository enthält einen eigenen, getesteten Server für das DATEV-Format (EXTF Buchungsstapel). Aufbau, Grenzen und Einrichtung beschreibt die [Anleitung zum DATEV-Format (EXTF)](./datev-mcp-server.md).

## BuchhaltungsButler, GetMyInvoices, Candis, Norman und weitere

### BuchhaltungsButler

Kein offizieller Server gefunden. `ohneben/Buchhaltungsbutler-MCP` (MIT, 9 Sterne, letzter Push 06.10.2026) setzt laut README ein Konto mit API-Zugang (API Client und API Secret) voraus, ordnet die 54 API-Endpunkte in lesend und schreibend ein und setzt die MCP-Annotationen `readOnlyHint` und `destructiveHint`. Daneben gibt es weitere kleine Projekte mit 0-1 Sternen.

### GetMyInvoices

Laut Hersteller (https://sites.getmyinvoices.com/en/mcp/, abgerufen am 16.10.2026) gibt es einen gehosteten, offiziellen MCP-Server unter `https://api.getmyinvoices.com/accounts/mcp-v1/public/index.php`. Er ist nur lesend: Er kann Belege nicht anlegen, ändern, freigeben oder löschen. Er ist laut Hersteller in allen Tarifen ohne Aufpreis enthalten, auch im Testzeitraum.

### Candis

Candis betreibt einen offiziellen MCP-Server unter `https://developer.candis.io/mcp`. Er durchsucht laut Hersteller die Entwickler-Doku und hilft bei Code, er liefert keine Rechnungsdaten. Die Candis-API selbst (Export, Stammdaten, Rechnungsdaten) nutzt OAuth 2.0 mit Authorization Code Flow (https://developer.candis.io/docs/getting-started).

### Norman

Der Anbieter Norman schreibt in seinem Blog (https://norman.finance/de/blog/mcp-server-buchhaltung, aktualisiert 11.08.2026), er betreibe einen eigenen MCP-Server mit Schreibzugriff, gelistet in den Verzeichnissen von Claude und ChatGPT. Das ist eine Herstellerangabe, wir haben den Server nicht getestet.

### Weitere

- **WISO Steuer**: laut derselben Übersicht kein MCP-Server.
- **ELSTER**: kein offizieller MCP. Die Übermittlung läuft über die Bibliothek ERiC, die eine Registrierung als Softwarehersteller und eine Prüfung voraussetzt (https://www.elster.de/elsterweb/infoseite/entwickler).
- **Banken (FinTS, EBICS)**: Eine GitHub-Suche am 16.10.2026 fand keine MCP-Server.

## Was ein KI-Assistent in der Buchhaltung darf und was nicht

Ein MCP-Server gibt dem Sprachmodell Werkzeuge. Was das Modell damit tut, entscheidet es anhand von Text, und dieser Text kann auch aus Belegen oder Rechnungen stammen, die ein Dritter geschrieben hat. Daraus folgt eine einfache Aufteilung.

**Sinnvoll und mit geringem Risiko:**

- Offene Posten, Umsätze und Belege lesen und zusammenfassen ("Welche Rechnungen sind seit mehr als 30 Tagen offen?").
- Fehlende Belege zu Banktransaktionen finden.
- Entwürfe anlegen: Rechnungsentwürfe, Angebotsentwürfe, Belege mit Status "offen", die ein Mensch vor dem Festschreiben prüft.
- Plausibilitätsprüfungen vorschlagen, etwa doppelte Belege oder ungewöhnliche Steuersätze.
- Exporte vorbereiten, die die Steuerberatung danach prüft.

**Nur mit ausdrücklicher Freigabe durch einen Menschen oder gar nicht:**

- Rechnungen festschreiben oder abschließen. Bei lexware office ist eine abgeschlossene Rechnung laut dem README von `marselsel/Lexware-MCP-Server` rechtlich bindend.
- Rechnungen, Mahnungen oder Angebote per E-Mail versenden.
- Zahlungen auslösen oder Banktransaktionen als bezahlt markieren.
- Buchungen festschreiben, stornieren oder löschen.
- Steuermeldungen übermitteln.

Praktisch heißt das:

- Wählen Sie Server mit getrenntem Lese- und Schreibmodus und starten Sie im Lesemodus.
- Nehmen Sie schreibende Werkzeuge nie in eine automatische Freigabeliste Ihres Clients auf.
- Legen Sie, wo die Software es erlaubt, einen eigenen Benutzer mit eingeschränkten Rechten für den API-Schlüssel an.
- Lesen Sie bei jeder Bestätigung die Parameter des Tool-Aufrufs, nicht nur den Namen des Werkzeugs.

## GoBD: Unveränderbarkeit, Protokollierung, Verfahrensdokumentation

Die GoBD sind ein BMF-Schreiben vom 28.11.2019, zuletzt geändert am 14.07.2025. Sie regeln, wie Bücher und Aufzeichnungen elektronisch zu führen sind. Ob und wie ein KI-Assistent Ihre GoBD-Pflichten berührt, klären Sie mit Ihrer Steuerberatung. Die folgenden Stellen sind Anhaltspunkte, keine Bewertung Ihres Falls (Text der Fassung 2019, abgerufen über https://www.datev.de/content/dam/markenassets/themen-und-produktgruppen/zielgruppen/zielgruppenuebergreifend/gobd/bmf_gobd_neufassung_2019.pdf am 19.10.2026):

- **Unveränderbarkeit (Rz. 58-59, 107-110)**: Eine Buchung darf nicht so verändert werden, dass der ursprüngliche Inhalt nicht mehr feststellbar ist (§ 146 Abs. 4 AO). Rz. 109 nennt als unzulässiges Beispiel, Grundaufzeichnungen zu exportieren, unprotokolliert zu bearbeiten und wieder zu importieren. Eine Möglichkeit ist deshalb, dass der Assistent nur Entwürfe erzeugt, die in der Buchhaltungssoftware selbst protokolliert festgeschrieben werden. Ob das für Ihren Ablauf genügt, klären Sie mit Ihrer Steuerberatung.
- **Internes Kontrollsystem (Rz. 100)**: Dazu gehören laut GoBD unter anderem Zugangs- und Zugriffsberechtigungskontrollen. Ein API-Schlüssel mit eingeschränkten Rechten und eine Freigabe vor dem Festschreiben passen in dieses Bild.
- **Verfahrensdokumentation (Rz. 151-155)**: Für jedes DV-System muss eine Verfahrensdokumentation vorhanden sein, aus der Inhalt, Aufbau, Ablauf und Ergebnisse ersichtlich sind. Wenn ein KI-Assistent Teil des Ablaufs wird, etwa beim Vorkontieren, gehört er in diese Beschreibung, mit Server, Version, Rechten und Freigabeschritten.
- **Protokollierung**: Halten Sie fest, welches Werkzeug wann mit welchen Parametern gelaufen ist. Manche Server liefern dafür ein Prüfprotokoll mit, zum Beispiel `JannikWempe/mcp-lexware-office` laut README pro HTTP-Aufruf.

Die Randziffern beziehen sich auf die Fassung 2019; prüfen Sie sie in der aktuellen Fassung.

Die Buchhaltungssoftware selbst bleibt das führende System. Der MCP-Server sollte nichts tun, was die Software nicht über ihre eigene API mit Protokollierung erlaubt.

## Einrichtung: ein Community-Server im Lesemodus

Am Beispiel von `JannikWempe/mcp-lexware-office` sieht eine Konfiguration für Claude Desktop oder Claude Code laut README so aus. Das README nennt `#semver:^3`, das bei jedem Start den neuesten 3.x-Tag lädt; hier ist stattdessen der feste Tag `v3.0.1` eingetragen (neuester Tag auf GitHub am 20.10.2026):

```json
{
  "mcpServers": {
    "lexware-office": {
      "command": "npx",
      "args": ["-y", "--package=github:JannikWempe/mcp-lexware-office#v3.0.1", "lexware-office"],
      "env": {
        "LEXWARE_OFFICE_API_KEY": "IHR_API_KEY",
        "LEXWARE_OFFICE_READ_ONLY": "true"
      }
    }
  }
}
```

Für sevdesk mit `joosthel/sevdesk-mcp` nennt das README diesen Befehl für Claude Code, hier mit fester Version `0.5.0` (aktuelle Version auf npm am 20.10.2026) statt ohne Versionsangabe:

```bash
claude mcp add --scope user sevdesk \
  --env SEVDESK_API_TOKEN=REPLACE_ME \
  --env SEVDESK_READ_ONLY=true \
  -- npx -y sevdesk-mcp@0.5.0
```

Beide Beispiele sind aus den jeweiligen README übernommen und nicht getestet, weil uns kein XL-Konto und kein sevdesk-Konto mit API-Zugang zur Verfügung stand. Hinweise zur Einrichtung der Clients stehen in [MCP-Clients einrichten](./mcp-clients-einrichten.md).

Zwei Punkte zu `npx`: Ohne feste Version lädt `npx` bei jedem Start den aktuellen Stand, auch eine geänderte oder kompromittierte Fassung. Legen Sie deshalb eine Version fest, die Sie selbst geprüft haben, und heben Sie sie erst nach Durchsicht der Änderungen an. Und speichern Sie den API-Schlüssel nicht in einer Datei, die in ein Git-Repository gelangt.

## E-Rechnungen: XRechnung und ZUGFeRD per MCP

Für E-Rechnungen gibt es im Schwester-Repository https://github.com/pexon-consulting/e-rechnung einen eigenen, lokal laufenden MCP-Server (`erechnung-mcp`, Paket `e-rechnung` mit Extra `mcp`). Er kann laut README XRechnung und ZUGFeRD lesen, gegen die KoSIT-Regeln validieren, erzeugen, als HTML anzeigen und Eingangsrechnungen als DATEV-Buchungsstapel exportieren. Er arbeitet nur in einem festgelegten Ordner und überschreibt keine Dateien.

Auch hier gilt: Bei einem Cloud-Sprachmodell gehen die Rechnungsinhalte an dessen Anbieter. Rechnungen stammen von Dritten und können Anweisungen an das Modell enthalten.

## Checkliste vor dem Start

1. Tarif prüfen: lexware office XL, sevdesk ab "Buchhaltung Pro", DATEV-APIs mit Registrierung, Abonnement und technischer Prüfung oder per EXTF-Datei.
2. API-Nutzungsbedingungen des Herstellers lesen, besonders zu Rate Limits, Polling und Weitergabe des Schlüssels.
3. Server auswählen: Herkunft, Lizenz, letzte Änderung, Lesemodus vorhanden.
4. Version festlegen (npm-Version, Git-Tag oder Image-Digest).
5. Eigenen Benutzer oder Schlüssel mit möglichst wenigen Rechten anlegen.
6. Im Lesemodus starten und schreibende Werkzeuge nicht automatisch freigeben.
7. Klären, welches Sprachmodell die Daten sieht und wo es betrieben wird (siehe [MCP und DSGVO](./mcp-dsgvo.md)).
8. Den Ablauf in der Verfahrensdokumentation beschreiben und mit der Steuerberatung abstimmen.
9. Ein Protokoll der Tool-Aufrufe aufbewahren.

## Häufige Fragen

### Gibt es einen offiziellen lexoffice MCP Server?

Nein, am 19.10.2026 bot Lexware keinen eigenen MCP-Server an. Es gibt mehrere Community-Server auf Basis der Public API. Diese setzt den Tarif lexware office XL voraus.

### Hat sevdesk einen MCP Server?

Keinen offiziellen. Community-Server wie `joosthel/sevdesk-mcp` nutzen die sevdesk-API, die ab dem Tarif "Buchhaltung Pro" enthalten ist. Starten Sie im Lesemodus, weil ein sevdesk-Token laut README alle Rechte des Benutzers hat.

### Gibt es einen DATEV MCP Server?

DATEV selbst veröffentlicht keinen. Es gibt kleine Community-Server und kommerzielle Zwischenschichten. Ohne eigenen API-Zugang über das DATEV Developer Portal ist das Dateiformat EXTF der einfachste Weg, siehe die [Anleitung zum DATEV-Format (EXTF)](./datev-mcp-server.md).

### Kann ein KI-Assistent meine Buchhaltung selbstständig machen?

Er kann lesen, zusammenfassen und Entwürfe vorbereiten. Festschreiben, Versenden und Bezahlen sollten Sie selbst freigeben. Ob Buchungen steuerlich richtig sind, klärt Ihre Steuerberatung.

### Ist MCP in der Buchhaltung GoBD-konform?

MCP ist nur ein Protokoll und für sich weder konform noch nicht konform. Entscheidend sind Rechte, Protokollierung, Unveränderbarkeit in der Buchhaltungssoftware und die Verfahrensdokumentation. Die Bewertung Ihres Ablaufs gehört zu Ihrer Steuerberatung.

## Weiterlesen

- [Übersicht: MCP-Server für deutsche Geschäftssysteme](../../README.md)
- [MCP-Server-Liste](../liste.md)
- [Was ist ein MCP-Server?](./was-ist-ein-mcp-server.md)
- [MCP vs. API: der Unterschied](./mcp-vs-api.md)
- [MCP-Server erstellen](./mcp-server-erstellen.md)
- [MCP-Clients einrichten](./mcp-clients-einrichten.md)
- [MCP-Sicherheit](./mcp-sicherheit.md)
- [MCP und DSGVO](./mcp-dsgvo.md)
- [Anleitung zum DATEV-Format (EXTF)](./datev-mcp-server.md)
- [SAP MCP Server](./sap-mcp-server.md)
- [Power BI MCP](./power-bi-mcp.md)
- [HubSpot MCP](./hubspot-mcp.md)
- [Postgres MCP Server](./postgres-mcp.md)
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
