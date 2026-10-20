# Änderungen

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionen nach [Semantic Versioning](https://semver.org/lang/de/).

## 0.1.0 (19.10.2026)

Erste Veröffentlichung.

- Liste mit über 130 MCP-Servern für deutsche Geschäftssysteme in 13 Kategorien, erzeugt aus `daten/server.yaml` mit `scripts/liste_bauen.py`, inklusive Prüfung in der CI.
- `server/extf-buchungsstapel`: MCP-Server und Kommandozeile `extf-buchungsstapel` für Buchungsstapel im DATEV-Format (EXTF, Formatversion 13): erstellen, lesen, prüfen, Felder erklären. 83 Prüfcodes, nur lokaler Arbeitsordner, kein Netzwerk. Paketname `extf-buchungsstapel-mcp`.
- 13 Anleitungen: Grundlagen, Einrichtung in Clients, SAP, Power BI, HubSpot, Business Central, Postgres, Buchhaltung, DATEV, Sicherheit und DSGVO.
- Beispiele: Feiertags-Server in Python (`mcp` 2.3) und TypeScript (`@modelcontextprotocol/server` 2.3), jeweils mit Tests.
- CI: Liste, EXTF-Server unter Python 3.11 und 3.13, beide Beispiele, Prüfung auf Gedankenstriche. Dependabot für Actions, pip und npm.
