#!/usr/bin/env python3
"""Validiert daten/server.yaml und erzeugt docs/liste.md sowie die Übersicht in README.md.

Aufruf:
    python3 scripts/liste_bauen.py                 # validieren und schreiben
    python3 scripts/liste_bauen.py --check         # Exit 1, wenn erzeugte Dateien veraltet sind
    python3 scripts/liste_bauen.py --aktualisieren # Sterne, letzten Push und Archivstatus per gh api holen

Abhängigkeiten: Python-Standardbibliothek und PyYAML.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATEN = ROOT / "daten" / "server.yaml"
LISTE = ROOT / "docs" / "liste.md"
README = ROOT / "README.md"
MARKER_START = "<!-- liste:start -->"
MARKER_ENDE = "<!-- liste:end -->"

KATEGORIEN = [
    "ERP",
    "Buchhaltung und Steuern",
    "E-Rechnung",
    "CRM und Vertrieb",
    "BI und Analytics",
    "Datenbanken",
    "Personal (HR)",
    "E-Commerce",
    "Zusammenarbeit",
    "Logistik und Versand",
    "Banking und Zahlungen",
    "Dokumente und DMS",
    "Behörden und Open Data",
]

# Kategorien mit weniger als zwei Einträgen brauchen hier eine Begründung.
KATEGORIE_AUSNAHMEN: dict[str, str] = {}

FELDER = [
    "name",
    "kategorie",
    "system",
    "url",
    "repo",
    "typ",
    "herkunft",
    "transport",
    "auth",
    "zugriff",
    "lizenz",
    "sprache",
    "sterne",
    "zuletzt_aktiv",
    "archiviert",
    "protokoll",
    "hinweis",
    "quelle",
    "geprueft_am",
]
PFLICHT = [
    "name",
    "kategorie",
    "system",
    "url",
    "typ",
    "herkunft",
    "transport",
    "auth",
    "zugriff",
    "lizenz",
    "hinweis",
    "quelle",
    "geprueft_am",
]
TYPEN = ["offiziell", "community", "kommerziell"]
TRANSPORTE = ["stdio", "http", "beides", "remote-gehostet"]
ZUGRIFFE = ["lesen", "lesen-schreiben"]
LIZENZ_SONDERWERTE = ["proprietär", "keine", "unklar"]
SPDX_MUSTER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]*$")
DATUM_MUSTER = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REPO_MUSTER = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")

# Offizielle Einträge müssen eine Quelle auf einer dieser Hersteller-Adressen haben.
HERSTELLER_QUELLEN: dict[str, list[str]] = {
    "SAP": ["sap.com", "github.com/SAP", "github.com/cap-js", "github.com/UI5"],
    "Microsoft": ["microsoft.com", "github.com/microsoft", "github.com/Azure"],
    "Odoo": ["odoo.com"],
    "JTL-Software": ["jtl-software.com"],
    "GetMyInvoices": ["getmyinvoices.com"],
    "Candis": ["candis.io"],
    "HubSpot": ["hubspot.com"],
    "Salesforce": ["salesforce.com", "github.com/salesforcecli"],
    "Pipedrive": ["pipedrive.com"],
    "Tableau (Salesforce)": ["github.com/tableau", "tableau.com"],
    "Qlik": ["qlik.com"],
    "Google": ["github.com/googleapis", "cloud.google.com"],
    "Oracle": ["oracle.com", "github.com/oracle"],
    "MariaDB": ["github.com/MariaDB", "mariadb.com"],
    "Personio": ["personio.de", "personio.com"],
    "Factorial": ["factorialhr.com"],
    "Shopware": ["shopware.com"],
    "Shopify": ["shopify.dev", "shopify.com"],
    "Atlassian": ["github.com/atlassian", "atlassian.com"],
    "Notion": ["notion.com"],
    "Slack": ["slack.dev", "slack.com"],
    "DHL": ["dhl.com"],
    "Sendcloud": ["sendcloud.dev", "sendcloud.com"],
    "Stripe": ["stripe.com"],
    "PayPal": ["paypal.com"],
    "Mollie": ["mollie.com"],
    "Qonto": ["qonto.com"],
}

TYP_ANZEIGE = {"offiziell": "offiziell", "community": "Community", "kommerziell": "kommerziell"}
ZUGRIFF_ANZEIGE = {"lesen": "lesen", "lesen-schreiben": "lesen und schreiben"}
TRANSPORT_ANZEIGE = {
    "stdio": "stdio",
    "http": "HTTP",
    "beides": "stdio und HTTP",
    "remote-gehostet": "gehostet",
}

HINWEIS_ALLGEMEIN = (
    "> **Hinweis:** Technisches Hilfswerk, keine Beratung. Technische Informationen nach "
    "Stand 19.10.2026, ohne Gewähr für Vollständigkeit und Richtigkeit. Keine Rechts-, Steuer- "
    "oder Datenschutzberatung; die Autoren sind keine Rechtsanwälte, Steuerberater oder "
    "Datenschutzbeauftragten. Was ein KI-Assistent mit diesen Servern erzeugt, stammt vom "
    "Sprachmodell und nicht von uns; für den Output von KI-Systemen übernehmen wir keine "
    "Haftung. Prüfen Sie jede Ausgabe, bevor Sie sie verwenden. Produktnamen sind Marken ihrer "
    "Inhaber; es besteht keine Verbindung zu den genannten Herstellern."
)
HINWEIS_STEUER = (
    "> Die Autoren erbringen keine Hilfeleistung in Steuersachen im Sinne des "
    "Steuerberatungsgesetzes. Ob und wie Buchungen steuerlich richtig sind, klären Sie mit "
    "Ihrer Steuerberatung. DATEV ist eine Marke der DATEV eG; dieses Projekt ist kein Produkt "
    "der DATEV eG und nicht von ihr geprüft oder freigegeben."
)

KATEGORIE_ANLEITUNGEN: dict[str, list[tuple[str, str]]] = {
    "ERP": [("SAP MCP Server", "sap-mcp-server.md"), ("Business Central MCP", "business-central-mcp.md")],
    "Buchhaltung und Steuern": [
        ("MCP Buchhaltung", "buchhaltung-mcp.md"),
        ("MCP-Server für das DATEV-Format (EXTF)", "datev-mcp-server.md"),
    ],
    "CRM und Vertrieb": [("HubSpot MCP Server", "hubspot-mcp.md")],
    "BI und Analytics": [("Power BI MCP Server", "power-bi-mcp.md")],
    "Datenbanken": [("Postgres MCP Server", "postgres-mcp.md")],
}

KATEGORIE_TEXTE: dict[str, list[str]] = {
    "ERP": [
        "SAP veröffentlicht vor allem Entwicklungswerkzeuge (ABAP, CAP, Fiori, UI5). Für den "
        "Zugriff auf Geschäftsdaten aus S/4HANA ist der offizielle Weg die Integration Suite. "
        "Eine ausführlichere SAP-Übersicht pflegt marianfoo/sap-ai-mcp-servers.",
        "Für weclapp und Xentral haben wir keinen Server des Herstellers gefunden. JTL bietet "
        "bisher nur einen Dokumentations-Server an.",
    ],
    "Buchhaltung und Steuern": [
        "Für DATEV, Lexware Office, sevdesk und BuchhaltungsButler haben wir keinen Server des "
        "Herstellers gefunden; alle Einträge dazu sind Community-Projekte.",
        "**ELSTER:** Die Finanzverwaltung bietet keinen MCP-Server an. Die offizielle "
        "Schnittstelle für Übermittlungen ist die Bibliothek ERiC, für die sich Hersteller "
        "registrieren müssen. Die beiden gelisteten ELSTER-Server arbeiten stattdessen mit dem "
        "Webportal. Ob das mit den Nutzungsbedingungen von ELSTER vereinbar ist, klären Sie "
        "vor dem Einsatz.",
    ],
    "E-Rechnung": [
        "Einen Server von KoSIT oder FeRD haben wir nicht gefunden. Achten Sie darauf, ob ein "
        "Server lokal validiert oder die Rechnung an einen externen Dienst schickt: "
        "Rechnungen enthalten personenbezogene Daten und Geschäftsdaten.",
    ],
    "CRM und Vertrieb": [
        "HubSpot, Salesforce, Pipedrive und Microsoft betreiben eigene, gehostete Server. "
        "Community-Server sind vor allem für lokale Setups und abweichende Rechtekonzepte "
        "verbreitet.",
    ],
    "BI und Analytics": [
        "Bei Power BI und Fabric gibt es mehrere offizielle Server mit unterschiedlichem "
        "Zweck: Modellierung, Abfragen und Verwaltung.",
    ],
    "Datenbanken": [
        "Viele Datenbank-Server führen beliebiges SQL aus. Verbinden Sie sie mit einem "
        "eigenen Datenbankbenutzer mit minimalen Rechten, nicht mit einem Administrator.",
    ],
    "Personal (HR)": [
        "HR-Systeme enthalten besonders schutzbedürftige Daten. Klären Sie den Einsatz mit "
        "Ihrer Datenschutzbeauftragten oder Ihrem Datenschutzbeauftragten und, wo vorhanden, "
        "mit dem Betriebsrat. Für SAP SuccessFactors haben wir keinen Server von SAP gefunden.",
    ],
    "E-Commerce": [
        "Shopware hat den MCP-Server in den Kern übernommen. JTL steht unter ERP.",
    ],
    "Zusammenarbeit": [
        "Microsoft betreibt die Server für Outlook, Teams und SharePoint als Teil von Agent 365 "
        "je Tenant. Nextcloud ist für selbst betriebene Installationen aufgeführt.",
    ],
    "Logistik und Versand": [
        "Die Kategorie hat zwei Einträge: die Server von DHL (nur Sandbox) und Sendcloud. "
        "Gepflegte Community-Server für Versanddienstleister haben wir nicht gefunden.",
    ],
    "Banking und Zahlungen": [
        "**FinTS und EBICS:** Einen MCP-Server für FinTS (HBCI) oder EBICS haben wir nicht "
        "gefunden, ebenso keinen eigenen Server von Sparkassen, Volksbanken oder Direktbanken. "
        "Wer Kontoumsätze deutscher Banken anbinden will, braucht eine eigene Anbindung, zum "
        "Beispiel auf Basis der Bibliothek python-fints (LGPL-3.0). EBICS setzt einen Vertrag "
        "mit der Bank voraus.",
    ],
    "Dokumente und DMS": [
        "Für DocuWare, d.velop und ELO haben wir keinen Server des Herstellers gefunden. "
        "DocuWare verweist auf die Aura-API, d.velop kündigt ein Agent Center für das vierte "
        "Quartal 2026 an.",
    ],
    "Behörden und Open Data": [
        "Eigene MCP-Server von Behörden haben wir nicht gefunden. Viele Server bauen auf den "
        "Schnittstellen auf, die bund.dev dokumentiert. Das Python-Paket bundesAPI/deutschland "
        "ist kein MCP-Server, eignet sich aber als Baustein.",
    ],
}

CHECKLISTE = [
    "**Herkunft:** Stammt der Server vom Hersteller des Systems oder aus der Community? "
    "Stimmen Repository, Paketname und Herausgeber überein?",
    "**Wartung:** Wann gab es die letzte Änderung? Werden Issues beantwortet? Ist das "
    "Repository archiviert?",
    "**Lizenz:** Ohne Lizenzdatei räumt der Autor keine Nutzungsrechte ein. AGPL-3.0 gilt "
    "auch, wenn Sie den Server Dritten über das Netz bereitstellen.",
    "**Rechte:** Gibt es einen Nur-Lese-Modus? Nutzen Sie einen eigenen technischen Benutzer "
    "mit minimalen Rechten und starten Sie mit einem Testsystem.",
    "**Anmeldung:** OAuth mit kurzlebigen Tokens ist API-Schlüsseln mit Vollzugriff "
    "vorzuziehen. Schlüssel gehören nicht in Konfigurationsdateien im Repository.",
    "**Datenfluss:** Läuft der Server lokal, bei Ihnen oder beim Anbieter? Bei gehosteten "
    "Diensten klären Sie Auftragsverarbeitung, Speicherort und Protokollierung.",
    "**Transport:** stdio-Server laufen als lokaler Prozess. HTTP-Server binden Sie nicht "
    "ungeschützt an öffentliche Adressen.",
    "**Tool-Beschreibungen:** Lesen Sie, welche Tools der Server anbietet und was sie "
    "auslösen. Inhalte aus E-Mails, Tickets oder Dokumenten können Anweisungen an das Modell "
    "enthalten.",
    "**Versionen:** Pinnen Sie Paketversionen statt immer die neueste Version zu laden, und "
    "lesen Sie Änderungen vor einem Update.",
    "**Protokollversion:** Die aktuelle MCP-Spezifikation ist 2026-07-28. Viele Server und "
    "Clients sprechen noch 2025-11-25; der Transport SSE ist veraltet.",
]

KOPF_KOMMENTAR = (
    "# MCP-Server für deutsche Geschäftssysteme. Quelle für docs/liste.md und README.md.\n"
    "# Felder und erlaubte Werte: scripts/liste_bauen.py. Erzeugen: python3 scripts/liste_bauen.py\n"
)


class Validierungsfehler(Exception):
    pass


def lade(pfad: Path = DATEN) -> list[dict]:
    roh = yaml.safe_load(pfad.read_text(encoding="utf-8"))
    if not isinstance(roh, dict) or not isinstance(roh.get("server"), list):
        raise Validierungsfehler("server.yaml braucht einen Schlüssel 'server' mit einer Liste")
    eintraege = []
    for e in roh["server"]:
        if not isinstance(e, dict):
            raise Validierungsfehler(f"Eintrag ist kein Objekt: {e!r}")
        eintraege.append({k: _normalisiere(v) for k, v in e.items()})
    return eintraege


def _normalisiere(wert):
    if isinstance(wert, (dt.date, dt.datetime)):
        return wert.isoformat()[:10]
    return wert


def _ist_datum(wert) -> bool:
    if not isinstance(wert, str) or not DATUM_MUSTER.match(wert):
        return False
    try:
        dt.date.fromisoformat(wert)
    except ValueError:
        return False
    return True


def _ist_url(wert) -> bool:
    if not isinstance(wert, str):
        return False
    teile = urlparse(wert)
    return teile.scheme == "https" and bool(teile.netloc)


def _hersteller_quelle_ok(eintrag: dict) -> bool:
    erlaubt = HERSTELLER_QUELLEN.get(eintrag.get("herkunft", ""), [])
    quelle = str(eintrag.get("quelle", ""))
    teile = urlparse(quelle)
    host = teile.netloc.lower()
    pfad = host + teile.path
    for muster in erlaubt:
        if "/" in muster:
            if pfad.lower().startswith(muster.lower() + "/") or pfad.lower() == muster.lower():
                return True
        elif host == muster or host.endswith("." + muster):
            return True
    return False


def validiere(eintraege: list[dict]) -> list[str]:
    fehler: list[str] = []
    urls: dict[str, str] = {}
    for i, e in enumerate(eintraege):
        kennung = f"Eintrag {i + 1} ({e.get('name', '?')})"
        for feld in e:
            if feld not in FELDER:
                fehler.append(f"{kennung}: unbekanntes Feld '{feld}'")
        for feld in PFLICHT:
            wert = e.get(feld)
            if wert is None or (isinstance(wert, str) and not wert.strip()):
                fehler.append(f"{kennung}: Pflichtfeld '{feld}' fehlt")
        if e.get("kategorie") not in KATEGORIEN:
            fehler.append(f"{kennung}: unbekannte Kategorie '{e.get('kategorie')}'")
        if e.get("typ") not in TYPEN:
            fehler.append(f"{kennung}: typ muss einer von {TYPEN} sein")
        if e.get("transport") not in TRANSPORTE:
            fehler.append(f"{kennung}: transport muss einer von {TRANSPORTE} sein")
        if e.get("zugriff") not in ZUGRIFFE:
            fehler.append(f"{kennung}: zugriff muss einer von {ZUGRIFFE} sein")
        lizenz = e.get("lizenz")
        if lizenz and lizenz not in LIZENZ_SONDERWERTE and not SPDX_MUSTER.match(str(lizenz)):
            fehler.append(f"{kennung}: lizenz '{lizenz}' ist weder SPDX noch {LIZENZ_SONDERWERTE}")
        for feld in ("url", "quelle"):
            if e.get(feld) is not None and not _ist_url(e.get(feld)):
                fehler.append(f"{kennung}: {feld} ist keine https-URL")
        url = str(e.get("url", "")).rstrip("/").lower()
        if url in urls:
            fehler.append(f"{kennung}: url doppelt (auch bei {urls[url]})")
        urls[url] = str(e.get("name"))
        datumsfeld = "geprueft_am"
        if not _ist_datum(e.get(datumsfeld)):
            fehler.append(f"{kennung}: {datumsfeld} ist kein gültiges Datum JJJJ-MM-TT")
        if e.get("zuletzt_aktiv") not in (None, "") and not _ist_datum(e.get("zuletzt_aktiv")):
            fehler.append(f"{kennung}: zuletzt_aktiv ist kein gültiges Datum JJJJ-MM-TT")
        sterne = e.get("sterne")
        if sterne is not None and (not isinstance(sterne, int) or isinstance(sterne, bool) or sterne < 0):
            fehler.append(f"{kennung}: sterne muss eine nicht negative Zahl sein")
        if sterne is not None and not e.get("repo"):
            fehler.append(f"{kennung}: sterne nur mit GitHub-Repository (Feld repo)")
        if e.get("archiviert") is not None and not isinstance(e.get("archiviert"), bool):
            fehler.append(f"{kennung}: archiviert muss true oder false sein")
        repo = e.get("repo")
        if repo is not None and not REPO_MUSTER.match(str(repo)):
            fehler.append(f"{kennung}: repo muss die Form besitzer/name haben")
        protokoll = e.get("protokoll")
        if protokoll not in (None, ""):
            teile = [t.strip() for t in str(protokoll).split(",")]
            if not all(_ist_datum(t) for t in teile):
                fehler.append(f"{kennung}: protokoll muss eine Liste von Datumsangaben sein")
        if e.get("typ") == "offiziell" and not _hersteller_quelle_ok(e):
            fehler.append(f"{kennung}: offizieller Eintrag ohne Quelle beim Hersteller")
    for kat in KATEGORIEN:
        anzahl = sum(1 for e in eintraege if e.get("kategorie") == kat)
        if anzahl < 2 and kat not in KATEGORIE_AUSNAHMEN:
            fehler.append(f"Kategorie '{kat}' hat {anzahl} Einträge und keine Begründung")
    return fehler


# ------------------------------------------------------------------ Darstellung


def stand(eintraege: list[dict]) -> str:
    return max(e["geprueft_am"] for e in eintraege)


def _datum_de(iso: str) -> str:
    j, m, t = iso.split("-")
    return f"{t}.{m}.{j}"


def ist_veraltet(eintrag: dict) -> bool:
    aktiv = eintrag.get("zuletzt_aktiv")
    if not aktiv:
        return False
    grenze = dt.date.fromisoformat(eintrag["geprueft_am"]) - dt.timedelta(days=365)
    return dt.date.fromisoformat(aktiv) < grenze


def sortiert(eintraege: list[dict]) -> list[dict]:
    def key(e: dict):
        return (
            0 if e["typ"] == "offiziell" else 1,
            -(e.get("sterne") or -1),
            e["name"].lower(),
        )

    return sorted(eintraege, key=key)


def anker(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def _zelle(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def hinweis_text(e: dict) -> str:
    teile = []
    if e.get("archiviert"):
        teile.append("Archiviert.")
    if ist_veraltet(e):
        teile.append(f"Letzte Änderung im Repository am {_datum_de(e['zuletzt_aktiv'])}.")
    teile.append(e["hinweis"].strip())
    if e.get("protokoll"):
        teile.append(f"Protokoll {e['protokoll']}.")
    return " ".join(teile)


def tabelle(eintraege: list[dict]) -> list[str]:
    zeilen = [
        "| Server | Typ | Transport | Auth | Zugriff | Lizenz | Hinweis |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for e in sortiert(eintraege):
        server = f"[{_zelle(e['name'])}]({e['url']})<br>{_zelle(e['system'])}"
        zeilen.append(
            "| "
            + " | ".join(
                [
                    server,
                    TYP_ANZEIGE[e["typ"]],
                    TRANSPORT_ANZEIGE[e["transport"]],
                    _zelle(e["auth"]),
                    ZUGRIFF_ANZEIGE[e["zugriff"]],
                    _zelle(e["lizenz"]),
                    _zelle(hinweis_text(e)),
                ]
            )
            + " |"
        )
    return zeilen


def baue_liste(eintraege: list[dict]) -> str:
    st = _datum_de(stand(eintraege))
    gesamt = len(eintraege)
    je_typ = {t: sum(1 for e in eintraege if e["typ"] == t) for t in TYPEN}
    z: list[str] = []
    z.append("# MCP-Server-Liste für deutsche Geschäftssysteme")
    z.append("")
    z.append(
        "Diese Liste sammelt MCP-Server für Geschäftssysteme, die in Deutschland verbreitet sind: "
        "ERP, Buchhaltung, E-Rechnung, CRM, BI, Datenbanken, HR, E-Commerce, Zusammenarbeit, "
        "Versand, Zahlungen, Dokumentenmanagement und offene Daten von Behörden. Je Kategorie "
        "stehen zuerst die Server der Hersteller, danach Community- und kommerzielle Server."
    )
    z.append("")
    z.append(
        "Grundlagen: [Was ist ein MCP-Server?](anleitungen/was-ist-ein-mcp-server.md). Vor dem "
        "Einsatz: [MCP Sicherheit](anleitungen/mcp-sicherheit.md) und "
        "[MCP und DSGVO](anleitungen/mcp-dsgvo.md). Übersicht aller Anleitungen in der "
        "[README](../README.md#anleitungen)."
    )
    z.append("")
    z.append(
        f"**Stand:** {st}. {gesamt} Einträge, davon {je_typ['offiziell']} offiziell, "
        f"{je_typ['community']} Community und {je_typ['kommerziell']} kommerziell. Die Liste wird "
        "aus `daten/server.yaml` erzeugt; Änderungen bitte dort vornehmen."
    )
    z.append("")
    z.append(HINWEIS_ALLGEMEIN)
    z.append("")
    z.append("## Legende")
    z.append("")
    z.append("- **Typ:** *offiziell* = vom Hersteller des Systems veröffentlicht. *Community* = von "
             "Dritten, meist Open Source. *kommerziell* = Angebot eines Drittanbieters, das Kosten "
             "verursachen kann.")
    z.append("- **Transport:** *stdio* = lokaler Prozess. *HTTP* = Streamable HTTP, Sie betreiben "
             "den Server selbst. *stdio und HTTP* = beides möglich. *gehostet* = der Anbieter "
             "betreibt den Server.")
    z.append("- **Zugriff:** *lesen* = nur lesende Tools, mindestens in der Standardeinstellung. "
             "*lesen und schreiben* = der Server kann Daten ändern, oft abschaltbar.")
    z.append("- **Lizenz:** SPDX-Kennung des Repositorys. *proprietär* = Dienst oder Software des "
             "Herstellers. *keine* = keine Lizenzdatei im Repository. *unklar* = GitHub erkennt "
             "die Lizenz nicht. SSPL, Elastic, BUSL, FSL oder CC-BY-NC sind keine "
             "Open-Source-Lizenzen und können den Einsatz im Unternehmen einschränken.")
    z.append("- **Reihenfolge:** offizielle Server zuerst, danach nach GitHub-Sternen. Sterne "
             "zeigen Bekanntheit, nicht Qualität oder Sicherheit.")
    z.append("- **Hinweis:** Archivierte Repositorys und Repositorys ohne Änderung seit mehr als "
             "zwölf Monaten sind dort vermerkt.")
    z.append("")
    z.append("## Inhalt")
    z.append("")
    for kat in KATEGORIEN:
        anzahl = sum(1 for e in eintraege if e["kategorie"] == kat)
        z.append(f"- [{kat}](#{anker(kat)}) ({anzahl})")
    z.append(f"- [So prüfen Sie einen MCP-Server vor dem Einsatz](#{anker('So prüfen Sie einen MCP-Server vor dem Einsatz')})")
    z.append(f"- [Eintrag vorschlagen](#{anker('Eintrag vorschlagen')})")
    z.append("")
    for kat in KATEGORIEN:
        teil = [e for e in eintraege if e["kategorie"] == kat]
        z.append(f"## {kat}")
        z.append("")
        for absatz in KATEGORIE_TEXTE.get(kat, []):
            z.append(absatz)
            z.append("")
        if kat in KATEGORIE_ANLEITUNGEN:
            links = ", ".join(f"[{t}](anleitungen/{d})" for t, d in KATEGORIE_ANLEITUNGEN[kat])
            z.append(f"Anleitung: {links}")
            z.append("")
        if kat in KATEGORIE_AUSNAHMEN:
            z.append(KATEGORIE_AUSNAHMEN[kat])
            z.append("")
        if kat == "Buchhaltung und Steuern":
            z.append(HINWEIS_STEUER)
            z.append("")
        z.extend(tabelle(teil))
        z.append("")
    z.append("## So prüfen Sie einen MCP-Server vor dem Einsatz")
    z.append("")
    for punkt in CHECKLISTE:
        z.append(f"- [ ] {punkt}")
    z.append("")
    z.append("## Eintrag vorschlagen")
    z.append("")
    z.append("Ein Server fehlt oder eine Angabe ist veraltet? Öffnen Sie ein Issue oder einen "
             "Pull Request mit einer Änderung an `daten/server.yaml`.")
    z.append("")
    z.append("- Der Server ist öffentlich zugänglich, funktioniert und betrifft ein System, das in "
             "Deutschland verbreitet ist.")
    z.append("- Keine leeren Repositorys und keine Forks ohne eigene Änderungen.")
    z.append("- Für offizielle Server nennen Sie eine Quelle beim Hersteller.")
    z.append("- Der Hinweis ist kurz und sachlich, ohne Werbung und ohne Wertung über Personen "
             "oder andere Projekte.")
    z.append("- Danach `python3 scripts/liste_bauen.py` ausführen; das Skript validiert die Daten "
             "und erzeugt diese Datei neu.")
    z.append("")
    z.append(HINWEIS_ALLGEMEIN)
    z.append("")
    return "\n".join(z)


def baue_readme_block(eintraege: list[dict]) -> str:
    z = [MARKER_START, ""]
    z.append(f"Stand {_datum_de(stand(eintraege))}: {len(eintraege)} Server in {len(KATEGORIEN)} "
             "Kategorien. Je Kategorie die offiziellen Server und bis zu drei Community-Server "
             "(nach GitHub-Sternen). Vollständige Liste mit Transport, Auth und Lizenz: "
             "[docs/liste.md](docs/liste.md).")
    z.append("")
    for kat in KATEGORIEN:
        teil = [e for e in eintraege if e["kategorie"] == kat]
        offiziell = [e for e in sortiert(teil) if e["typ"] == "offiziell"]
        andere = [e for e in sortiert(teil) if e["typ"] != "offiziell"][:3]
        teile = []
        if offiziell:
            teile.append("offiziell: " + ", ".join(f"[{e['name']}]({e['url']})" for e in offiziell))
        if andere:
            teile.append("weitere: " + ", ".join(f"[{e['name']}]({e['url']})" for e in andere))
        z.append(f"- **{kat}** - " + "; ".join(teile))
    z.append("")
    z.append(MARKER_ENDE)
    return "\n".join(z)


def readme_neu(alt: str, block: str) -> str | None:
    if MARKER_START not in alt or MARKER_ENDE not in alt:
        return None
    anfang = alt.index(MARKER_START)
    ende = alt.index(MARKER_ENDE, anfang) + len(MARKER_ENDE)
    return alt[:anfang] + block + alt[ende:]


# ------------------------------------------------------------------ YAML schreiben


def _skalar(wert) -> str:
    if wert is None:
        return ""
    if isinstance(wert, bool):
        return "true" if wert else "false"
    if isinstance(wert, int):
        return str(wert)
    if isinstance(wert, str) and _ist_datum(wert):
        return wert
    text = yaml.safe_dump(wert, allow_unicode=True, width=100000, default_style=None)
    text = text.strip()
    if text.endswith("\n..."):
        text = text[: -len("\n...")]
    elif text.endswith("..."):
        text = text[:-3].rstrip()
    return text


def schreibe_yaml(eintraege: list[dict], pfad: Path = DATEN) -> None:
    zeilen = [KOPF_KOMMENTAR.rstrip("\n"), "server:"]
    letzte = None
    for e in eintraege:
        if e.get("kategorie") != letzte:
            letzte = e.get("kategorie")
            zeilen.append(f"# ---------------------------------------------------------------- {letzte}")
        erste = True
        for feld in FELDER:
            if feld not in e or e[feld] is None or e[feld] == "":
                continue
            praefix = "- " if erste else "  "
            zeilen.append(f"{praefix}{feld}: {_skalar(e[feld])}")
            erste = False
    pfad.write_text("\n".join(zeilen) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ GitHub


def hole_repo(repo: str) -> dict | None:
    abfrage = (
        "{stars: .stargazers_count, pushed: .pushed_at, archived: .archived, "
        "license: .license.spdx_id, language: .language, full: .full_name}"
    )
    try:
        out = subprocess.run(
            ["gh", "api", f"repos/{repo}", "--jq", abfrage],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        ).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        print(f"WARNUNG: {repo} nicht abrufbar: {exc}", file=sys.stderr)
        return None
    return json.loads(out)


def aktualisiere(eintraege: list[dict]) -> None:
    cache: dict[str, dict | None] = {}
    for e in eintraege:
        repo = e.get("repo")
        if not repo:
            continue
        if repo not in cache:
            cache[repo] = hole_repo(repo)
        daten = cache[repo]
        if not daten:
            continue
        if daten.get("full") and daten["full"].lower() != repo.lower():
            print(f"HINWEIS: {repo} leitet weiter auf {daten['full']}", file=sys.stderr)
        e["sterne"] = int(daten["stars"])
        e["zuletzt_aktiv"] = str(daten["pushed"])[:10]
        e["archiviert"] = bool(daten["archived"])
        if not e.get("lizenz"):
            spdx = daten.get("license")
            e["lizenz"] = "keine" if not spdx else ("unklar" if spdx == "NOASSERTION" else spdx)
        if not e.get("sprache") and daten.get("language"):
            e["sprache"] = daten["language"]


# ------------------------------------------------------------------ Hauptprogramm


def _anzeige(pfad: Path) -> str:
    try:
        return str(pfad.relative_to(ROOT))
    except ValueError:
        return str(pfad)


def erzeuge(eintraege: list[dict]) -> tuple[str, str | None]:
    liste = baue_liste(eintraege)
    readme = None
    if README.exists():
        readme = readme_neu(README.read_text(encoding="utf-8"), baue_readme_block(eintraege))
    return liste, readme


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="nur vergleichen, Exit 1 bei veralteten Dateien")
    parser.add_argument("--aktualisieren", action="store_true", help="GitHub-Daten per gh api auffrischen")
    args = parser.parse_args(argv)

    eintraege = lade()
    if args.aktualisieren:
        aktualisiere(eintraege)
        schreibe_yaml(eintraege)
        eintraege = lade()

    fehler = validiere(eintraege)
    if fehler:
        for f in fehler:
            print(f"FEHLER: {f}", file=sys.stderr)
        return 2

    liste, readme = erzeuge(eintraege)
    if args.check:
        veraltet = []
        if not LISTE.exists() or LISTE.read_text(encoding="utf-8") != liste:
            veraltet.append(_anzeige(LISTE))
        if readme is not None and README.read_text(encoding="utf-8") != readme:
            veraltet.append(_anzeige(README))
        if veraltet:
            print("Veraltet: " + ", ".join(veraltet) + ". Bitte scripts/liste_bauen.py ausführen.", file=sys.stderr)
            return 1
        print(f"Aktuell: {len(eintraege)} Einträge.")
        return 0

    LISTE.parent.mkdir(parents=True, exist_ok=True)
    LISTE.write_text(liste, encoding="utf-8")
    print(f"{_anzeige(LISTE)} geschrieben ({len(eintraege)} Einträge).")
    if readme is None:
        grund = "README.md fehlt" if not README.exists() else "Marker fehlen in README.md"
        print(f"README nicht aktualisiert: {grund}.")
    else:
        README.write_text(readme, encoding="utf-8")
        print("README.md: Bereich zwischen den Markern ersetzt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
