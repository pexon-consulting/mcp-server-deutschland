# MCP und DSGVO: Datenschutz bei MCP-Servern im Unternehmen

Diese Anleitung zeigt, welche Datenflüsse beim Einsatz von MCP-Servern entstehen und welche Fragen der DSGVO, des BDSG und des Betriebsverfassungsgesetzes Sie vor dem Einsatz klären sollten. Sie ersetzt keine Rechtsberatung, sondern ordnet die technischen Fakten für Gespräche mit Datenschutzbeauftragten, Rechtsabteilung und Betriebsrat.

Stand: 19.10.2026

## Inhaltsverzeichnis

- [Wichtiger Hinweis vorab](#wichtiger-hinweis-vorab)
- [Das Wichtigste in Kürze](#das-wichtigste-in-kürze)
- [Wohin die Daten fließen](#wohin-die-daten-fließen)
- [Lokale und Remote-MCP-Server](#lokale-und-remote-mcp-server)
- [Rollen: Verantwortlicher und Auftragsverarbeiter](#rollen-verantwortlicher-und-auftragsverarbeiter)
- [Auftragsverarbeitung und Drittlandübermittlung](#auftragsverarbeitung-und-drittlandübermittlung)
- [Rechtsgrundlage und Informationspflichten](#rechtsgrundlage-und-informationspflichten)
- [Datenminimierung durch Tool-Design](#datenminimierung-durch-tool-design)
- [Protokollierung und Löschung](#protokollierung-und-löschung)
- [Beschäftigtendaten und Betriebsrat](#beschäftigtendaten-und-betriebsrat)
- [Datenschutz-Folgenabschätzung](#datenschutz-folgenabschätzung)
- [EU AI Act: KI-Kompetenz nach Art. 4](#eu-ai-act-ki-kompetenz-nach-art-4)
- [Checkliste](#checkliste)
- [Quellen](#quellen)
- [Häufige Fragen](#häufige-fragen)
- [Weiterlesen](#weiterlesen)

## Wichtiger Hinweis vorab

Dieser Text ist keine Rechtsberatung und kann sie nicht ersetzen. Die Autoren sind keine Rechtsanwälte und keine Datenschutzbeauftragten. Die Darstellung beruht auf öffentlich zugänglichen Quellen mit Stand 19.10.2026 und gibt unsere Lesart wieder. Gerichte und Aufsichtsbehörden können Fragen anders beurteilen, und die Rechtslage ändert sich.

Für jeden konkreten Einsatz bleibt der Betreiber verantwortlich, also das Unternehmen, das den MCP-Server und den KI-Client einsetzt. Ob eine Verarbeitung zulässig ist, welche Verträge nötig sind und ob eine Datenschutz-Folgenabschätzung erforderlich ist, hängt vom Einzelfall ab. Ziehen Sie Ihre Datenschutzbeauftragte oder Ihren Datenschutzbeauftragten und bei Bedarf eine Rechtsanwältin oder einen Rechtsanwalt hinzu.

## Das Wichtigste in Kürze

- **Ein lokaler MCP-Server macht die Verarbeitung nicht lokal.** Was ein Werkzeug zurückgibt, landet im Kontext des Sprachmodells. Läuft das Modell bei einem Cloud-Anbieter, gehen die Daten dorthin.
- **Rollen klären:** Ihr Unternehmen ist in der Regel Verantwortlicher. Der Modellanbieter und gegebenenfalls der Betreiber eines Remote-MCP-Servers kommen als Auftragsverarbeiter in Betracht.
- **Verträge:** Für Auftragsverarbeiter brauchen Sie einen Vertrag nach Art. 28 DSGVO, bei Anbietern außerhalb des EWR zusätzlich eine Grundlage nach Art. 44 ff. DSGVO.
- **Tool-Design ist Datenschutz:** Werkzeuge, die nur die nötigen Felder liefern, setzen den Grundsatz der Datenminimierung technisch um.
- **Betriebsrat:** Protokolle über Tool-Aufrufe können geeignet sein, Verhalten oder Leistung zu überwachen. Das spricht für eine Mitbestimmung nach § 87 Abs. 1 Nr. 6 BetrVG.

## Wohin die Daten fließen

Ein typischer Ablauf mit einem Postgres- oder CRM-Server:

```text
Mitarbeiterin                 KI-Client (Host)             Modellanbieter
     |  Frage: "Welche Rechnungen   |                            |
     |  sind offen?"                |                            |
     | ---------------------------> |  Frage + Tool-Liste        |
     |                              | -------------------------> |
     |                              |  "rufe execute_sql auf"    |
     |                              | <------------------------- |
     |                              |                            |
     |                       MCP-Server (lokal oder remote)      |
     |                              |  SQL-Ergebnis mit          |
     |                              |  Kundennamen, Beträgen     |
     |                              | -------------------------> |
     |                              |  formulierte Antwort       |
     |  Antwort                     | <------------------------- |
     | <--------------------------- |                            |
```

Entscheidend ist der dritte Pfeil nach rechts: Das Ergebnis des Werkzeugs geht als Text an das Modell. Bei einem Cloud-Modell verlassen damit Kundennamen, Beträge, E-Mail-Adressen oder Notizen das Unternehmen. Dazu kommen die Frage selbst, die Tool-Beschreibungen und je nach Client der bisherige Gesprächsverlauf.

Daten können an weiteren Stellen liegen:

- im Verlauf des KI-Clients (lokal oder in der Cloud des Client-Anbieters),
- in Protokollen des MCP-Servers oder eines Gateways,
- in Protokollen des Zielsystems (Datenbank, CRM),
- beim Modellanbieter, je nach Vertrag für Missbrauchserkennung oder Fehleranalyse für eine bestimmte Zeit.

Für den Datenschutz zählt die ganze Kette, nicht nur der MCP-Server. Die technischen Grundlagen dazu stehen in [Was ist ein MCP-Server?](./was-ist-ein-mcp-server.md) und [MCP vs. API](./mcp-vs-api.md).

## Lokale und Remote-MCP-Server

| Aspekt | Lokaler Server (stdio) | Remote-Server (HTTP) |
| --- | --- | --- |
| Wo läuft der Code? | Auf dem Rechner der Nutzerin oder in Ihrem Container | Beim Betreiber des Servers |
| Wer sieht die Rohdaten aus dem Zielsystem? | Nur Ihr Rechner, danach das Modell | Der Betreiber des Servers, danach das Modell |
| Zugangsdaten | Liegen bei Ihnen (Umgebungsvariablen) | Oft beim Betreiber oder als OAuth-Token |
| Zusätzlicher Empfänger | Keiner außer dem Modellanbieter | Betreiber des Remote-Servers |
| Vertragsfragen | Modellanbieter | Modellanbieter und Server-Betreiber |

Ein Remote-Server des Herstellers Ihres Zielsystems (etwa eines CRM) ist datenschutzrechtlich oft weniger neu, als es klingt: Die Daten liegen dort ohnehin, und häufig gibt es schon einen Vertrag. Klären Sie aber, ob der MCP-Dienst vom bestehenden Vertrag erfasst ist und ob er weitere Unterauftragnehmer einbindet.

Der vollständig lokale Weg ist ein lokales Modell auf eigener Hardware zusammen mit lokalen Servern. Dann verlässt nichts das Unternehmen, die Qualität der Tool-Aufrufe hängt aber stark vom Modell ab.

## Rollen: Verantwortlicher und Auftragsverarbeiter

Die DSGVO unterscheidet den Verantwortlichen (Art. 4 Nr. 7), der über Zwecke und Mittel entscheidet, und den Auftragsverarbeiter (Art. 4 Nr. 8), der im Auftrag verarbeitet. Bei gemeinsamer Entscheidung über Zwecke und Mittel kommt eine gemeinsame Verantwortlichkeit nach Art. 26 in Betracht. Der EDSA hat die Abgrenzung in den Leitlinien 07/2020 erläutert.

Für einen typischen MCP-Einsatz liegt nach unserer Lesart folgende Zuordnung nahe:

- **Ihr Unternehmen** entscheidet, welche Daten mit welchem Werkzeug zu welchem Zweck verarbeitet werden. Es ist damit in der Regel Verantwortlicher.
- **Der Modellanbieter** verarbeitet Eingaben und Ausgaben, um Ihnen den Dienst zu erbringen. Bei Business- und API-Angeboten bieten viele Anbieter einen Vertrag zur Auftragsverarbeitung an. Ob der Anbieter Daten zusätzlich für eigene Zwecke nutzt (etwa Training), entscheidet über die Rolle mit und steht in den Vertragsbedingungen.
- **Der Betreiber eines Remote-MCP-Servers** verarbeitet die Daten aus dem Zielsystem und kommt ebenfalls als Auftragsverarbeiter in Betracht.
- **Der Anbieter des KI-Clients** ist relevant, wenn der Client Verläufe in seiner Cloud speichert.

Bei Verbraucher-Konten der KI-Dienste fehlt oft ein solcher Vertrag, und die Bedingungen erlauben teils eine Nutzung der Inhalte zur Verbesserung der Dienste. Für Geschäftsdaten sind solche Konten nach unserer Einschätzung in der Regel ungeeignet. Prüfen Sie die konkreten Bedingungen des Anbieters.

## Auftragsverarbeitung und Drittlandübermittlung

### Vertrag nach Art. 28 DSGVO

Setzt der Verantwortliche einen Auftragsverarbeiter ein, braucht es einen Vertrag oder ein anderes Rechtsinstrument mit den Inhalten aus Art. 28 Abs. 3 DSGVO: unter anderem Gegenstand, Dauer, Art und Zweck der Verarbeitung, Weisungsbindung, Vertraulichkeit, technische und organisatorische Maßnahmen nach Art. 32, Regeln für Unterauftragsverarbeiter (Art. 28 Abs. 2 und 4), Unterstützung bei Betroffenenrechten sowie Löschung oder Rückgabe nach Ende des Auftrags.

Für MCP-Einsätze lohnt der Blick auf drei Punkte: Wie lange speichert der Anbieter Eingaben und Ausgaben? Wird für Training genutzt? Welche Unterauftragnehmer und Standorte sind beteiligt?

### Drittlandübermittlung nach Art. 44 ff. DSGVO

Sitzt der Modellanbieter oder der Server-Betreiber außerhalb des EWR oder greift von dort zu, braucht die Übermittlung eine Grundlage nach Kapitel V der DSGVO:

- **Angemessenheitsbeschluss (Art. 45):** Für die USA gilt der Durchführungsbeschluss (EU) 2023/1795 vom 10.07.2023 zum EU-US Data Privacy Framework, aber nur für Unternehmen, die nach diesem Rahmen zertifiziert sind. Das EuG hat die Nichtigkeitsklage dagegen mit Urteil vom 03.09.2025 (T-553/23, Latombe/Kommission) abgewiesen. Dagegen ist ein Rechtsmittel beim EuGH anhängig (C-703/25 P, eingelegt am 31.10.2025). Nach unserer Recherche war es am 19.10.2026 noch nicht entschieden.
- **Geeignete Garantien (Art. 46):** insbesondere die Standardvertragsklauseln nach Durchführungsbeschluss (EU) 2021/914, in der Regel mit einer Bewertung der Rechtslage im Zielland.
- **Ausnahmen (Art. 49):** eng auszulegen und für regelmäßige Übermittlungen nach unserer Einschätzung kaum geeignet.

Viele Anbieter bieten inzwischen eine Datenverarbeitung in der EU an. Das kann die Prüfung vereinfachen, ersetzt sie aber nicht, etwa wenn Support oder Unterauftragnehmer aus Drittländern zugreifen.

## Rechtsgrundlage und Informationspflichten

### Rechtsgrundlage nach Art. 6 DSGVO

Jede Verarbeitung personenbezogener Daten braucht eine Rechtsgrundlage nach Art. 6 Abs. 1 DSGVO. Bei der Auswertung von Kunden- und Lieferantendaten kommen je nach Zweck vor allem in Betracht:

- lit. b, wenn die Verarbeitung für die Erfüllung eines Vertrags mit der betroffenen Person erforderlich ist,
- lit. c, wenn eine rechtliche Verpflichtung besteht,
- lit. f, berechtigte Interessen, nach einer Abwägung mit den Interessen der Betroffenen.

Der EDSA hat in der Stellungnahme 28/2024 vom 17.12.2024 den Drei-Stufen-Test für berechtigte Interessen im Zusammenhang mit KI-Modellen erläutert: legitimes Interesse, Erforderlichkeit, Abwägung. Die Stellungnahme betrifft Entwicklung und Einsatz von KI-Modellen, die Prüfschritte lassen sich aber auf den Einsatz eines Assistenten mit MCP-Werkzeugen übertragen.

Für besondere Kategorien personenbezogener Daten (Art. 9, etwa Gesundheitsdaten) gelten strengere Voraussetzungen. Solche Daten sollten Werkzeuge nach Möglichkeit gar nicht liefern.

### Zweckbindung

Daten, die für die Rechnungsstellung erhoben wurden, dürfen nicht ohne Weiteres für beliebige neue Zwecke ausgewertet werden (Art. 5 Abs. 1 lit. b, Art. 6 Abs. 4). Ein Assistent, der "alles über den Kunden" zusammenträgt, kann eine Zweckänderung bedeuten. Definieren Sie den Zweck des Einsatzes vorab schriftlich.

### Informationspflichten nach Art. 13 und 14 DSGVO

Werden Daten bei der betroffenen Person erhoben, informieren Sie nach Art. 13 unter anderem über Zwecke, Rechtsgrundlage, Empfänger oder Kategorien von Empfängern und eine etwaige Drittlandübermittlung. Für Daten, die nicht bei der Person erhoben wurden, gilt Art. 14. Kommt ein Modellanbieter als neuer Empfänger hinzu, kann es nötig sein, Datenschutzhinweise für Kunden und Beschäftigte anzupassen.

Trifft das System Entscheidungen mit rechtlicher Wirkung allein automatisiert, ist zusätzlich Art. 22 DSGVO zu beachten. Bei den meisten MCP-Einsätzen bereitet der Assistent Informationen vor, die Entscheidung trifft ein Mensch.

## Datenminimierung durch Tool-Design

Nach Art. 5 Abs. 1 lit. c DSGVO müssen Daten "dem Zweck angemessen und erheblich sowie auf das für die Zwecke der Verarbeitung notwendige Maß beschränkt" sein. Art. 25 verlangt Datenschutz durch Technikgestaltung. Bei MCP ist das Werkzeug der Hebel, denn was das Werkzeug nicht liefert, sieht das Modell nicht.

Vergleich zweier Werkzeuge für dieselbe Frage "Welche Rechnungen sind überfällig?":

| Werkzeug | Was es liefert | Bewertung |
| --- | --- | --- |
| `execute_sql` (beliebiges SQL) | Alles, was die Rolle lesen darf, auch Ansprechpartner, E-Mail, Notizen | Datenminimierung hängt vom Modell ab |
| `mahnliste()` (eigenes Werkzeug) | Rechnungsnummer, Kundennummer, Betrag, Tage überfällig | Minimierung ist im Werkzeug festgelegt |

Praktische Muster:

- **Views statt Tabellen:** Die Datenbankrolle des Servers liest eine View ohne Namen und Kontaktdaten. Wie das geht, zeigt [Postgres MCP Server](./postgres-mcp.md).
- **Pseudonyme Kennungen:** Kundennummer statt Name. Die Zuordnung erfolgt im Zielsystem, nicht im Chat.
- **Aggregation:** Summen und Anzahlen statt Einzelzeilen, wo die Frage das erlaubt.
- **Freitextfelder auslassen:** Notizen und Kommentare enthalten oft mehr personenbezogene Daten als erwartet und sind zudem ein Einfallstor für Prompt Injection.
- **Kleine Ergebnismengen:** Ein festes Limit pro Aufruf.

Eigene Werkzeuge dieser Art bauen Sie mit dem Python- oder TypeScript-SDK, siehe [MCP-Server erstellen](./mcp-server-erstellen.md).

## Protokollierung und Löschung

Protokolle sind aus Sicherheitsgründen sinnvoll (siehe [MCP Sicherheit](./mcp-sicherheit.md)), sie enthalten aber selbst personenbezogene Daten: Wer hat wann was gefragt, und welche Kundendaten kamen zurück?

- **Was protokollieren?** Zeitpunkt, Nutzerkennung, Werkzeug, Parameter und Status reichen für die Nachvollziehbarkeit oft aus. Vollständige Ergebnisse nur, wenn ein Zweck das erfordert.
- **Wie lange?** Eine feste Frist definieren und technisch umsetzen (Art. 5 Abs. 1 lit. e, Speicherbegrenzung).
- **Wer darf lesen?** Zugriff auf Protokolle beschränken und dokumentieren. Das ist auch für den Betriebsrat ein zentraler Punkt.
- **Wo liegen Kopien?** Verläufe im KI-Client und beim Modellanbieter haben eigene Fristen. Prüfen Sie Einstellungen zur Aufbewahrung und zum Löschen.
- **Verzeichnis:** Den Einsatz im Verzeichnis von Verarbeitungstätigkeiten nach Art. 30 DSGVO aufnehmen.

Ein Löschkonzept sollte auch Betroffenenanfragen abdecken: Wenn eine Person Auskunft nach Art. 15 verlangt, müssen Sie wissen, wo ihre Daten in der MCP-Kette gelandet sein können.

## Beschäftigtendaten und Betriebsrat

### Mitbestimmung nach § 87 Abs. 1 Nr. 6 BetrVG

Der Betriebsrat hat mitzubestimmen bei der "Einführung und Anwendung von technischen Einrichtungen, die dazu bestimmt sind, das Verhalten oder die Leistung der Arbeitnehmer zu überwachen". Das BAG legt "dazu bestimmt" weit aus: Es genügt, dass die Einrichtung zur Überwachung objektiv geeignet ist. Auf die Absicht des Arbeitgebers kommt es nicht an (BAG, Beschluss vom 13.12.2016, 1 ABR 7/15).

Ein MCP-Einsatz erfüllt das nach unserer Einschätzung häufig, weil Client, Gateway oder Server protokollieren, wer welche Werkzeuge wie oft nutzt. Hinzu kommt, dass Werkzeuge selbst Beschäftigtendaten liefern können, etwa Tickets mit Bearbeitern oder CRM-Aktivitäten mit Vertriebsmitarbeitern.

Eine Abgrenzung zeigt das ArbG Hamburg (Beschluss vom 16.01.2024, 24 BVGa 1/24): Bei der Nutzung von ChatGPT über private Konten im Browser sah das Gericht keine Mitbestimmung nach Nr. 6, weil der Arbeitgeber keine Daten über die Nutzung erhielt. Bei MCP-Einsätzen mit Firmenkonten, zentraler Konfiguration und Protokollen ist die Lage nach unserer Lesart anders. Eine Entscheidung eines Landesarbeitsgerichts zur Einordnung ist uns dazu nicht bekannt.

### Weitere Rechte des Betriebsrats

- **§ 90 Abs. 1 Nr. 3 BetrVG:** Unterrichtung über die Planung von Arbeitsverfahren und Arbeitsabläufen "einschließlich des Einsatzes von Künstlicher Intelligenz".
- **§ 80 Abs. 3 BetrVG:** Muss der Betriebsrat die Einführung oder Anwendung von Künstlicher Intelligenz beurteilen, gilt die Hinzuziehung eines Sachverständigen insoweit als erforderlich.

Ein bewährter Weg ist eine Betriebsvereinbarung oder eine Rahmenvereinbarung für KI-Werkzeuge, die zugelassene Server, Zwecke, Protokollierung, Auswertungsverbote und Zugriffsrechte festlegt. Neue MCP-Server lassen sich dann über eine Anlage ergänzen.

### Rechtsgrundlage für Beschäftigtendaten

Für Beschäftigtendaten sind Art. 88 DSGVO und § 26 BDSG einschlägig. Der EuGH hat mit Urteil vom 30.03.2023 (C-34/21) zu einer gleichlautenden hessischen Regelung entschieden, dass eine nationale Norm, die nur die allgemeinen DSGVO-Regeln wiederholt, keine spezifischere Vorschrift im Sinne von Art. 88 ist. Seitdem ist umstritten, wie weit § 26 Abs. 1 BDSG trägt. Viele stützen sich ergänzend auf Art. 6 Abs. 1 DSGVO. Klären Sie die Rechtsgrundlage mit Ihrem Datenschutzbeauftragten.

## Datenschutz-Folgenabschätzung

Nach Art. 35 Abs. 1 DSGVO ist eine Datenschutz-Folgenabschätzung (DSFA) durchzuführen, wenn eine Form der Verarbeitung, "insbesondere bei Verwendung neuer Technologien", voraussichtlich ein hohes Risiko für die Rechte und Freiheiten natürlicher Personen zur Folge hat. Art. 35 Abs. 3 nennt Regelbeispiele, Art. 35 Abs. 4 verweist auf Listen der Aufsichtsbehörden. Die DSK hat eine solche Liste veröffentlicht.

Prüfpunkte, die bei MCP-Einsätzen für eine DSFA sprechen können:

- Ein KI-Assistent mit Zugriff auf umfangreiche Kunden- oder Beschäftigtendaten (neue Technologie, Umfang).
- Zusammenführen von Daten aus mehreren Systemen über mehrere Server (Profilbildung).
- Besondere Kategorien nach Art. 9 oder Daten über Beschäftigte.
- Systematische Auswertung von Verhalten, etwa über Protokolle.
- Übermittlung in Drittländer.
- Schreibende Werkzeuge mit Wirkung auf Betroffene (Mahnungen, Kündigungen, Kontosperren).

Die DSFA muss nach Art. 35 Abs. 7 mindestens eine systematische Beschreibung der Verarbeitung, eine Bewertung von Notwendigkeit und Verhältnismäßigkeit, eine Bewertung der Risiken und die geplanten Abhilfemaßnahmen enthalten. Auch wenn keine DSFA erforderlich ist, empfiehlt es sich, die Abwägung kurz zu dokumentieren.

Hilfreich für die Bewertung sind die Orientierungshilfen der DSK zu KI (Mai 2024), zu technischen und organisatorischen Maßnahmen bei KI-Systemen (Juni 2025) und zu generativen KI-Systemen mit RAG-Methode (Oktober 2025). RAG ist nicht dasselbe wie MCP, viele Fragen zu externen Datenquellen im Kontext eines Modells sind aber ähnlich.

## EU AI Act: KI-Kompetenz nach Art. 4

Art. 4 der KI-Verordnung (EU) 2024/1689 gilt seit dem 02.02.2025. Er wurde durch die Verordnung (EU) 2026/1744 vom 08.07.2026 geändert. Nach der geänderten Fassung müssen Anbieter und Betreiber von KI-Systemen Maßnahmen ergreifen, um die Entwicklung der KI-Kompetenz ihres Personals und anderer Personen, die in ihrem Auftrag mit KI-Systemen arbeiten, zu unterstützen. Ein bestimmtes Kompetenzniveau müssen sie nicht garantieren. Für Unternehmen, die MCP-Werkzeuge einführen, heißt das praktisch: Schulung zu Risiken, Datenflüssen und Freigaben einplanen und dokumentieren. Quellen: AI Act Service Desk der EU-Kommission und Amtsblatt (siehe unten).

Hinweis zur DSGVO selbst: Änderungen im Rahmen des "Digital-Omnibus" sind Stand 19.10.2026 noch im Gesetzgebungsverfahren. Prüfen Sie vor Entscheidungen den aktuellen Stand.

## Checkliste

### Vor dem Einsatz

- [ ] Zweck schriftlich festlegen: Welche Fragen soll der Assistent beantworten, welche Daten braucht er dafür?
- [ ] Datenfluss aufzeichnen: Client, Modellanbieter, MCP-Server, Zielsystem, Protokolle.
- [ ] Rollen zuordnen: Verantwortlicher, Auftragsverarbeiter, gegebenenfalls gemeinsame Verantwortung.
- [ ] Vertrag nach Art. 28 DSGVO mit dem Modellanbieter und gegebenenfalls dem Betreiber des Remote-Servers.
- [ ] Drittlandübermittlung bewerten (Art. 45, 46 DSGVO), Datenstandort und Unterauftragnehmer klären.
- [ ] Rechtsgrundlage nach Art. 6 DSGVO und bei Beschäftigtendaten nach Art. 88 DSGVO und § 26 BDSG festlegen.
- [ ] Prüfen, ob eine DSFA nach Art. 35 DSGVO erforderlich ist, Ergebnis dokumentieren.
- [ ] Betriebsrat frühzeitig unterrichten (§ 90 BetrVG) und Mitbestimmung nach § 87 Abs. 1 Nr. 6 BetrVG klären.
- [ ] Verzeichnis von Verarbeitungstätigkeiten nach Art. 30 DSGVO ergänzen.
- [ ] Datenschutzhinweise nach Art. 13 und 14 DSGVO prüfen.

### Technik

- [ ] Nur Business- oder API-Konten mit passenden Vertragsbedingungen, keine Verbraucher-Konten.
- [ ] Nutzung von Eingaben für Training beim Anbieter ausschließen, soweit möglich.
- [ ] Werkzeuge mit minimalen Feldern, Views, Limits und ohne Freitextfelder.
- [ ] Lesemodus und eigene Service-Konten (siehe [MCP Sicherheit](./mcp-sicherheit.md)).
- [ ] Protokollierung mit festgelegtem Umfang, Frist und Zugriffsrechten.
- [ ] Aufbewahrung von Verläufen im Client und beim Anbieter einstellen.

### Organisation

- [ ] Freigabeliste zugelassener MCP-Server und Clients.
- [ ] Schulung zu Datenflüssen und Risiken (auch mit Blick auf Art. 4 KI-Verordnung).
- [ ] Prozess für Auskunfts- und Löschanfragen um die MCP-Kette ergänzen.
- [ ] Regelmäßige Überprüfung, besonders bei neuen Servern, Modellen oder Anbietern.

## Quellen

Alle abgerufen am 19.10.2026, sofern nicht anders angegeben.

- DSGVO, Verordnung (EU) 2016/679: https://eur-lex.europa.eu/eli/reg/2016/679/oj
- BDSG: https://www.gesetze-im-internet.de/bdsg_2018/
- BetrVG, § 80, § 87, § 90: https://www.gesetze-im-internet.de/betrvg/
- Durchführungsbeschluss (EU) 2023/1795 (Data Privacy Framework) und EuG-Urteil T-553/23 vom 03.09.2025: https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=celex%3A62023TJ0553
- Rechtsmittel C-703/25 P, eingelegt am 31.10.2025: https://eur-lex.europa.eu/eli/C/2025/6610/oj
- EDSA, Stellungnahme 28/2024 vom 17.12.2024: https://www.edpb.europa.eu/our-work-tools/our-documents/opinion-board-art-64/opinion-282024-certain-data-protection-aspects_en
- EDSA, Leitlinien 07/2020 zu den Begriffen Verantwortlicher und Auftragsverarbeiter: https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-072020-concepts-controller-and-processor-gdpr_de
- BAG, Beschluss vom 13.12.2016, 1 ABR 7/15: https://www.bundesarbeitsgericht.de/wp-content/uploads/2021/01/1-ABR-7-15.pdf
- ArbG Hamburg, Beschluss vom 16.01.2024, 24 BVGa 1/24: https://recht.nulegal.eu/rechtsprechung/arbg-hamburg/2024-01-16/24-bvga-1-24
- DSK, Orientierungshilfe "Künstliche Intelligenz und Datenschutz", Version 1.0 vom 06.05.2024: https://www.datenschutzkonferenz-online.de/media/oh/20240506_DSK_Orientierungshilfe_KI_und_Datenschutz.pdf
- DSK, Orientierungshilfe zu technischen und organisatorischen Maßnahmen bei KI-Systemen, Juni 2025: https://www.datenschutz-berlin.de/fileadmin/user_upload/pdf/publikationen/DSK/2025/20250617-DSK-OH_KI-Systeme.pdf
- DSK, Übersicht der Orientierungshilfen (darunter RAG, Oktober 2025): https://www.datenschutzkonferenz-online.de/orientierungshilfen.html
- KI-Verordnung, Art. 4: https://ai-act-service-desk.ec.europa.eu/de/ai-act/article-4
- Verordnung (EU) 2026/1744: https://eur-lex.europa.eu/legal-content/DE/TXT/PDF/?uri=OJ%3AL_202601744
- EU-Kommission, FAQ zur KI-Kompetenz: https://digital-strategy.ec.europa.eu/de/faqs/ai-literacy-questions-answers

Nicht gesondert geprüft haben wir für diesen Text: die EuGH-Entscheidung C-34/21 im Volltext, die aktuelle Fassung der DSK-Liste nach Art. 35 Abs. 4 DSGVO und den Volltext der EDSA-Leitlinien 07/2020.

## Häufige Fragen

### Ist MCP DSGVO-konform?

MCP ist ein Protokoll und als solches weder konform noch nicht konform. Entscheidend ist der konkrete Einsatz: welche Daten Werkzeuge liefern, welcher Modellanbieter sie verarbeitet, welche Verträge bestehen und wie protokolliert wird.

### Bleiben die Daten bei einem lokalen MCP-Server im Unternehmen?

Nur, wenn auch das Sprachmodell lokal läuft. Bei einem Cloud-Modell gehen die Ergebnisse der Werkzeuge an den Modellanbieter. Der lokale Server ändert nur, dass kein weiterer Betreiber die Rohdaten sieht.

### Brauche ich einen AV-Vertrag für einen MCP-Server?

Für einen lokal betriebenen Open-Source-Server in der Regel nicht, weil kein Dritter Daten verarbeitet. Für den Modellanbieter und für Betreiber von Remote-MCP-Servern kommt ein Vertrag nach Art. 28 DSGVO in Betracht. Die Einordnung im Einzelfall klären Sie mit Ihrem Datenschutzbeauftragten.

### Hat der Betriebsrat bei MCP-Servern mitzubestimmen?

Häufig ja, nach § 87 Abs. 1 Nr. 6 BetrVG. Ohne Einigung mit dem Betriebsrat oder Spruch der Einigungsstelle darf die Einrichtung dann nicht eingeführt werden. Nach der Rechtsprechung des BAG genügt es, dass eine technische Einrichtung objektiv geeignet ist, Verhalten oder Leistung zu überwachen. Protokolle über Tool-Aufrufe erfüllen das oft. Zusätzlich bestehen Unterrichtungsrechte nach § 90 BetrVG.

### Brauche ich eine Datenschutz-Folgenabschätzung für MCP?

Das hängt vom Umfang und von der Art der Daten ab. Bei umfangreichen Kunden- oder Beschäftigtendaten, bei Zusammenführung mehrerer Systeme oder bei Drittlandübermittlungen spricht viel dafür. Dokumentieren Sie die Prüfung in jedem Fall.

## Weiterlesen

- [Übersicht: MCP-Server für deutsche Geschäftssysteme](../../README.md)
- [MCP-Server-Liste](../liste.md)
- [Was ist ein MCP-Server?](./was-ist-ein-mcp-server.md)
- [MCP vs. API: der Unterschied](./mcp-vs-api.md)
- [MCP-Server erstellen](./mcp-server-erstellen.md)
- [MCP-Clients einrichten](./mcp-clients-einrichten.md)
- [MCP Sicherheit](./mcp-sicherheit.md)
- [Anleitung zum DATEV-Format (EXTF)](./datev-mcp-server.md)
- [SAP MCP Server](./sap-mcp-server.md)
- [Power BI MCP](./power-bi-mcp.md)
- [HubSpot MCP](./hubspot-mcp.md)
- [Postgres MCP Server](./postgres-mcp.md)
- [MCP-Server für Buchhaltung](./buchhaltung-mcp.md)
- [Business Central MCP](./business-central-mcp.md)

> **Hinweis:** Technische Informationen nach Stand 19.10.2026, ohne Gewähr für Vollständigkeit
> und Richtigkeit. Keine Rechts- oder Steuerberatung; die Autoren sind keine Rechtsanwälte,
> Steuerberater oder Datenschutzbeauftragten. Produktnamen sind Marken ihrer Inhaber; es besteht
> keine Verbindung zu den genannten Herstellern.
