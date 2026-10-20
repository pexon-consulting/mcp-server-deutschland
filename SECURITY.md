# Sicherheit

## Sicherheitslücke melden

Bitte melden Sie Sicherheitsprobleme nicht in einem öffentlichen Issue. Nutzen Sie stattdessen die private Meldung über GitHub: Reiter **Security**, dann **Report a vulnerability** ([direkter Link](https://github.com/pexon-consulting/mcp-server-deutschland/security/advisories/new)).

Hilfreich sind:

- betroffene Datei oder betroffenes Tool und Version (Tag oder Commit),
- Schritte zum Nachstellen, möglichst mit einer Beispieldatei ohne echte Buchungsdaten,
- Ihre Einschätzung der Auswirkung.

Bitte schicken Sie keine echten Buchhaltungs-, Kunden- oder Personaldaten mit.

Wir bemühen uns, Meldungen zeitnah zu sichten und zu beheben. Dieses Projekt wird freiwillig gepflegt; ein Anspruch auf Antwort, Behebung oder eine bestimmte Frist besteht nicht.

## Geltungsbereich

| Teil | Abgedeckt |
|---|---|
| `server/extf-buchungsstapel` (MCP-Server und Kommandozeile) | ja, Details in [server/extf-buchungsstapel/SECURITY.md](server/extf-buchungsstapel/SECURITY.md) |
| `beispiele/` | ja, als Lehrbeispiele ohne Betriebszusage |
| `scripts/` und `daten/server.yaml` | ja, etwa falsche oder irreführende Einträge |
| Server Dritter aus der Liste | nein, bitte direkt beim jeweiligen Projekt oder Hersteller melden |

Wenn ein Eintrag in der Liste auf ein bösartiges oder kompromittiertes Projekt zeigt, melden Sie das bitte ebenfalls privat. Wir entfernen oder markieren den Eintrag.

## Unterstützte Versionen

Sicherheitskorrekturen gibt es nur für den neuesten Stand auf `main` und das neueste Release.
