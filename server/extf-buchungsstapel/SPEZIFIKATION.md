# Spezifikation: DATEV-Format (EXTF), Buchungsstapel

Diese Datei hält fest, welche Regeln `extf-buchungsstapel-mcp` umsetzt und woher sie stammen. Sie ist eine eigene Zusammenfassung, keine Kopie der DATEV-Dokumentation. Maßgeblich ist immer die aktuelle Formatbeschreibung der DATEV eG. Der Server kennt 83 Prüfcodes; die vollständige Liste steht im [README](README.md#prüfcodes).

Stand: 20.10.2026

## Quellen

Primärquellen sind Seiten der DATEV eG. Die Seiten des DATEV Developer Portals werden per JavaScript gerendert; sie wurden am 19.10.2026 im Browser geöffnet und ausgelesen. Einige Unterseiten ändern beim Anklicken die Adresse nicht, dort ist der Navigationspfad angegeben.

| Kürzel | Quelle | Art |
|---|---|---|
| P1 | DATEV-Format, Formatbeschreibung, Header: https://developer.datev.de/de/file-formats/details/datev-format/format-description/header | primär |
| P2 | DATEV-Format, Formatbeschreibung, Buchungsstapel: https://developer.datev.de/de/file-formats/details/datev-format/format-description/booking-batch | primär |
| P3 | DATEV-Format, Einstieg (Dateiaufbau, technischer Aufbau, Spaltenüberschriften): https://developer.datev.de/de/file-formats/details/datev-format/getting-started | primär |
| P4 | DATEV-Format, Navigation "Zeichensatz" (erreichbar über P3) | primär |
| P5 | DATEV-Format, Navigation "Import/Export" und "Tools" (erreichbar über P3) | primär |
| P6 | DATEV-Format, Navigation "Changelog" (erreichbar über P3) | primär |
| P7 | DATEV-Format, Navigation "Musterdaten", Datei `EXTF_Buchungsstapel.csv` aus dem ZIP der Musterdaten (erreichbar über P3) | primär |
| P8 | API-Produkt accounting:extf-files, Dokumentation: https://developer.datev.de/de/product-detail/accounting-extf-files/2.0/documentation/erste-schritte. Die Seite "Erste Schritte" enthält am 19.10.2026 nur Registrierung, Organisation, App, Abonnement und Produktion. Die Aussagen zu Mindestversion, Prüfumfang und Dateitrennung stehen vermutlich unter dem Reiter "Vorgaben", der keine eigene Adresse hat (`.../documentation/vorgaben` leitet auf "Erste Schritte" um); dort wurden sie nicht erneut nachgelesen | primär, Fundstelle der Aussagen in Abschnitt 6 **ungeprüft** |
| S1 | Integrationsdokumentation eines Drittanbieters zum DATEV Buchungsdatenservice: https://docs.pushdocs.io/integrations-datev_buchungsdatenservice | sekundär |
| S2 | Unabhängige TypeScript-Implementierung `@seamless-engineering/datev-extf` 0.1.0 (MIT), nur zum Abgleich in Tests | sekundär |
| S3 | OWASP, CSV Injection: https://owasp.org/www-community/attacks/CSV_Injection | sekundär |

Einstufung in den Tabellen:

- **primär**: steht so in einer DATEV-Quelle (P1-P8).
- **abgeleitet**: folgt aus einer Primärquelle, ist dort aber nicht wörtlich als Regel formuliert.
- **sekundär**: nur aus Drittquellen; der Server meldet solche Punkte beim Prüfen höchstens als Warnung. Beim Schreiben kann er strenger sein (z. B. `FORMELZEICHEN_BEIM_SCHREIBEN`).
- **ungeprüft**: nicht primär belegt; der Server behandelt den Punkt vorsichtig (Warnung oder Hinweis statt Fehler, oder strengere Variante beim Schreiben).

## 1. Dateiaufbau

| Regel | Umsetzung im Server | Quelle | Einstufung |
|---|---|---|---|
| Dateiname mit Präfix `EXTF_` und Endung `.csv` | Schreiben: Vorgabename `EXTF_Buchungsstapel_...csv`. Prüfen: Warnung `DATEINAME_PRAEFIX` | P3 | primär (Warnung, weil der Name für die Prüfung des Inhalts keine Rolle spielt) |
| Zeile 1 Header, Zeile 2 Spaltenüberschriften, ab Zeile 3 Buchungen | Fehler `SPALTENZEILE_FEHLT`, Warnung `KEINE_BUCHUNGEN` | P3 | primär |
| Felder durch Semikolon getrennt | Tokenizer trennt nur außerhalb von Anführungszeichen | P3 | primär |
| Jede Zeile endet mit CR/LF | Schreiben immer CR/LF. Prüfen: Fehler `ZEILENENDE_KEIN_CRLF`, Warnung `LETZTE_ZEILE_OHNE_CRLF` | P3 | primär (letzte Zeile: abgeleitet aus "am Ende jeder Zeile") |
| Textfelder in Anführungszeichen, innere Anführungszeichen verdoppelt | Schreiben: alle Textfelder in `"..."`, auch leere (`""`). Prüfen: Warnung `TEXT_OHNE_ANFUEHRUNGSZEICHEN`, Hinweis `ZAHL_IN_ANFUEHRUNGSZEICHEN`, Fehler `ANFUEHRUNGSZEICHEN_OFFEN` | P3 | primär |
| Keine Steuerzeichen in Textfeldern | Fehler `STEUERZEICHEN` (Tab, Zeilenumbruch, andere Zeichen unter 0x20) | P3 | primär |
| Dezimaltrennzeichen Komma, keine Tausendertrennzeichen | Schreiben `1190,00`. Prüfen über das Muster des Feldes Umsatz | P3, P2 | primär |
| Header immer 31 Felder | Fehler `HEADER_FELDANZAHL` | P1 | primär |
| Formatversion 13: 125 Spalten; Formatversion 12: 124 Spalten (ohne "Abw. Skontokonto") | Schreiben nur Version 13. Prüfen: Fehler `SPALTENANZAHL`, `VERSION_GEMISCHT`; Warnung `HEADER_FORMATVERSION_ALT` für 12 | P3, P6 | primär (124 für Version 12: abgeleitet aus dem Changelog, Feld 125 kam hinzu) |
| Header mit Formatversion 12 nicht mit Spalten der Version 13 mischen (und umgekehrt) | Fehler `VERSION_GEMISCHT` | abgeleitet aus P3 und P6 | abgeleitet |
| Mehr Felder als Spalten in einer Buchungszeile | Fehler `ZEILE_ZU_VIELE_FELDER` | abgeleitet aus P3 | abgeleitet |
| Weniger Felder als Spalten | Warnung `ZEILE_ZU_WENIGE_FELDER` | ungeprüft, ob DATEV fehlende Felder am Zeilenende als leer liest | ungeprüft |
| Ein Stapel je Buchungsperiode empfohlen | Kein eigener Prüfcode; Belegdaten müssen im Zeitraum des Headers liegen | P2 | primär |
| Höchstens 99.999 Buchungen je Datei | Warnung `ZU_VIELE_BUCHUNGEN`; die Buchungszeilen werden dann nicht gelesen und nicht geprüft (Schutz vor Speicherüberlauf) | S1 | sekundär |
| Höchstens 50 MB je Datei | Warnung `DATEI_ZU_GROSS` (Kommandozeile). Die MCP-Tools lesen größere Dateien gar nicht ein | S1 | sekundär |
| Ab 10.000 Befunden | Weitere Befunde werden nur gezählt, Hinweis `BEFUNDE_GEKUERZT`; die Zahlen für Fehler, Warnungen und Hinweise bleiben vollständig | eigene Entscheidung dieses Servers | abgeleitet |
| Textfelder, die mit `=`, `+`, `-`, `@`, Tabulator oder Wagenrücklauf beginnen | Prüfen: Warnung `FORMELZEICHEN_AM_ANFANG` für alle Textfelder des Headers und der Buchungszeilen (Zahlenfelder wie Umsatz sind ausgenommen). Schreiben: Fehler `FORMELZEICHEN_BEIM_SCHREIBEN` bei `=` oder `@` am Anfang von Feld 11, 12, 14, 37 und 38 | S3; DATEV wertet keine Formeln aus, Tabellenprogramme schon | sekundär (Sicherheitsregel dieses Servers, keine DATEV-Regel) |

## 2. Zeichensatz

| Regel | Umsetzung im Server | Quelle | Einstufung |
|---|---|---|---|
| Standard ist ISO-8859-1 bzw. Codepage 1252 | Schreiben immer Windows-1252, `€` wird zu Byte 0x80 | P4 | primär |
| Unicode (UTF-8, UTF-16, UTF-32) nur mit Byte Order Mark | Lesen: BOM wird erkannt, Hinweis `UNICODE_MIT_BOM`. UTF-8 ohne BOM mit Umlauten: Warnung `UTF8_OHNE_BOM` | P4 | primär |
| Unicode nur beim manuellen Import und über die Online-API, nicht über die Stapelverarbeitung (KrStaPv) | Darum schreibt der Server nie Unicode; nur als Hinweistext | P4 | primär |
| Bytes, die in Windows-1252 nicht belegt sind (z. B. 0x81) | Fehler `ZEICHENSATZ_UNGUELTIG` | abgeleitet aus P4 | abgeleitet |
| Zeichen außerhalb von Windows-1252 in der Eingabe (z. B. Emojis) | Schreiben verweigert, Fehler `ZEICHEN_NICHT_CP1252` | abgeleitet aus P4 | abgeleitet |

## 3. Header (Zeile 1)

Die Spalte "Format" fasst die regulären Ausdrücke und Wertebereiche aus P1 in eigenen Worten zusammen. Leerfelder schreibt der Server so, wie sie im Beispiel-Header von P1 stehen (leer oder `""`). Prüfcodes: `HEADER_KENNZEICHEN`, `HEADER_VERSION`, `HEADER_FORMATKATEGORIE`, `HEADER_FORMATNAME`, `HEADER_FORMATVERSION`, `HEADER_ZEITSTEMPEL`, `HEADER_BERATERNUMMER`, `HEADER_MANDANTENNUMMER`, `HEADER_WJ_BEGINN`, `HEADER_SACHKONTENLAENGE`, `HEADER_DATUM_VON`, `HEADER_DATUM_BIS`, `HEADER_BEZEICHNUNG`, `HEADER_DIKTATKUERZEL`, `HEADER_BUCHUNGSTYP`, `HEADER_RECHNUNGSLEGUNGSZWECK`, `HEADER_FESTSCHREIBUNG`, `HEADER_WKZ`, `HEADER_SACHKONTENRAHMEN`, `HEADER_FELD`.

| Nr. | Name | Pflicht | Format | Bedeutung |
|---|---|---|---|---|
| 1 | Kennzeichen | Pflicht | "EXTF" oder "DTVF" | EXTF für Dateien aus Fremdsoftware, DTVF für Dateien aus DATEV-Programmen. |
| 2 | Versionsnummer | Pflicht | 700 | Version des Headers. |
| 3 | Formatkategorie | Pflicht | 21 | Art der Daten; 21 steht für Buchungsstapel. |
| 4 | Formatname | Pflicht | "Buchungsstapel" | Name der Formatkategorie. |
| 5 | Formatversion | Pflicht | 13 | Version des Satzaufbaus; für Buchungsstapel 13 (12 mit 124 Spalten). |
| 6 | Erzeugt am | Pflicht | JJJJMMTTHHMMSSmmm (17 Ziffern) | Zeitstempel der Erzeugung. |
| 7 | Importiert | Leerfeld | leer | Bleibt leer. |
| 8 | Herkunft | optional | Text, 0-2 Zeichen | Kürzel der Herkunft der Daten. |
| 9 | Exportiert von | optional | Text, 0-25 Zeichen | Name der exportierenden Person oder Anwendung. |
| 10 | Importiert von | optional | Text, 0-25 Zeichen | Name der importierenden Person. |
| 11 | Beraternummer | Pflicht | 1001-9999999 | Beraternummer des Bestands in DATEV. |
| 12 | Mandantennummer | Pflicht | 1-99999 | Mandantennummer des Bestands in DATEV. |
| 13 | WJ-Beginn | Pflicht | JJJJMMTT | Beginn des Wirtschaftsjahres; daraus ergibt sich das Jahr der Belegdaten. |
| 14 | Sachkontenlänge | Pflicht | 4-8 | Stellenzahl der Sachkonten; muss zur Einstellung des Mandanten in DATEV passen. |
| 15 | Datum von | Pflicht | JJJJMMTT | Beginn des Zeitraums des Stapels. |
| 16 | Datum bis | Pflicht | JJJJMMTT | Ende des Zeitraums des Stapels. |
| 17 | Bezeichnung | optional | Text, 0-30 Zeichen | Bezeichnung des Stapels, z. B. Rechnungsausgang 02/2026. |
| 18 | Diktatkürzel | optional | leer, 2 oder 4 Großbuchstaben | Kürzel der bearbeitenden Person in Großbuchstaben. |
| 19 | Buchungstyp | optional | 1 oder 2 | 1 = Finanzbuchführung, 2 = Jahresabschluss. |
| 20 | Rechnungslegungszweck | optional | 0, 30, 40, 50, 64 | 0 = unabhängig, 30 Steuerrecht, 40 Kalkulatorik, 50 Handelsrecht, 64 IFRS. |
| 21 | Festschreibung | optional | 0 oder 1 | 0 = keine Festschreibung, 1 = Festschreibung (DATEV-Vorgabe, wenn leer). |
| 22 | WKZ | optional | "EUR" oder anderer ISO-Code | Währung des Stapels. |
| 23 | Reserviert | Leerfeld | leer | Bleibt leer. |
| 24 | Derivatskennzeichen | Leerfeld | "" | Bleibt leer (leerer Text). |
| 25 | Reserviert | Leerfeld | leer | Bleibt leer. |
| 26 | Reserviert | Leerfeld | leer | Bleibt leer. |
| 27 | Sachkontenrahmen | optional | Text, leer, 2 oder 4 Ziffern | Kontenrahmen der Buchungen, z. B. "03" oder "04". |
| 28 | ID der Branchenlösung | optional | 0-4 Ziffern | Nur bei einer DATEV-Branchenlösung. |
| 29 | Reserviert | Leerfeld | leer | Bleibt leer. |
| 30 | Reserviert | Leerfeld | "" | Bleibt leer (leerer Text). |
| 31 | Anwendungsinformation | optional | Text, 0-16 Zeichen | Verarbeitungskennzeichen der abgebenden Anwendung. |

Weitere Regeln zum Header:

| Regel | Umsetzung im Server | Quelle | Einstufung |
|---|---|---|---|
| Beispiel-Header aus P1 | Der Writer erzeugt ihn bei gleichen Eingaben Byte für Byte; Test `test_header_matches_datev_example_byte_for_byte` | P1 | primär |
| Kennzeichen DTVF ist DATEV-Programmen vorbehalten | Schreiben immer `EXTF`; Lesen von `DTVF`: Warnung `HEADER_KENNZEICHEN_DTVF` | P1 | primär |
| Datum von nicht nach Datum bis | Fehler `HEADER_ZEITRAUM` | abgeleitet aus P1 | abgeleitet |
| Zeitraum innerhalb eines Wirtschaftsjahres (WJ-Beginn bis ein Jahr später) | Fehler `HEADER_ZEITRAUM_AUSSERHALB_WJ` | abgeleitet aus P1/P2 (Jahr der Belegdaten aus WJ-Beginn) | abgeleitet |
| Festschreibung leer heißt bei DATEV "festschreiben" | Schreiben: der Server setzt Feld 21 ausdrücklich, Vorgabe `0`. Lesen von leerem Feld 21: Hinweis `HEADER_FESTSCHREIBUNG_LEER` | P1 | primär (Vorgabe 0 ist eine vorsichtige Entscheidung dieses Servers) |
| Bezeichnung (Feld 17): Buchstaben, Ziffern, _, Punkt, Schrägstrich, Leerzeichen, höchstens 30 Zeichen (im DATEV-Ausdruck `[\w.-/ ]` ist `.-/` ein Bereich und umfasst nur Punkt und Schrägstrich, keinen Bindestrich) | Warnung `HEADER_BEZEICHNUNG`. Ob Umlaute als "Buchstabe" zählen, ist **ungeprüft**; der Server akzeptiert sie | P1 | primär, Umlaute ungeprüft |

## 4. Buchungszeilen (ab Zeile 3)

Der Server schreibt alle 125 Felder. Er füllt die Felder unten; alle anderen bleiben leer (Textfelder als `""`). Gelesen und geprüft werden zusätzlich die Anzahl der Felder, das Quoting aller Felder und Steuerzeichen.

| Feld | Regel | Umsetzung im Server | Quelle | Einstufung |
|---|---|---|---|---|
| 1 Umsatz | Positiv, nicht 0, bis 10 Vorkommastellen, genau 2 Nachkommastellen, Komma als Trenner | Fehler `UMSATZ_FEHLT`, `UMSATZ_FORMAT`, `UMSATZ_NICHT_POSITIV`. Fehlende Nachkommastellen (`100`): nur Warnung `UMSATZ_OHNE_NACHKOMMA`, weil die DATEV-Musterdatei (P7) selbst einen solchen Wert enthält | P2, P7 | primär |
| 2 Soll/Haben-Kennzeichen | `S` oder `H`, bezogen auf Feld 7 (Konto) | Fehler `SOLL_HABEN_UNGUELTIG`; Kleinbuchstaben und leer gelten als Fehler | P2 | primär (leer als Fehler: vorsichtiger als die DATEV-Vorgabe `S`) |
| 3 WKZ Umsatz | Leer oder ISO-Währungscode | Fehler `WKZ_UNGUELTIG` bei anderem Muster als drei Großbuchstaben | P2 | primär (Muster abgeleitet) |
| 7 Konto, 8 Gegenkonto | Nur Ziffern, nicht nur Nullen, höchstens 9 Stellen; Sachkonten haben die Sachkontenlänge aus Header-Feld 14, Personenkonten eine Stelle mehr | Fehler `KONTO_FEHLT`, `KONTO_FORMAT`, `KONTO_ZU_LANG` (und `GEGENKONTO_...`) bei mehr als Sachkontenlänge + 1 Stellen. Warnung `KONTO_GLEICH_GEGENKONTO` | P2 | primär (Warnung bei Gleichheit: abgeleitet) |
| 9 BU-Schlüssel | P2 nennt 4 Ziffern in Anführungszeichen | Fehler `BU_SCHLUESSEL_FORMAT`, wenn nicht 1-4 Ziffern. Warnung `BU_SCHLUESSEL_KURZ` bei 1-3 Ziffern; der Server schreibt sie unverändert und füllt nicht mit Nullen auf, weil die Bedeutung von `"0009"` gegenüber `"9"` ungeprüft ist | P2 | primär für 4 Ziffern; **ungeprüft**, ob DATEV 1-3 Ziffern ohne führende Nullen gleich behandelt. Welche Schlüssel fachlich passen, prüft der Server nicht |
| 10 Belegdatum | `TTMM`; das Jahr ergibt sich aus Header-Feld 13 (WJ-Beginn) | Fehler `BELEGDATUM_FEHLT`, `BELEGDATUM_FORMAT` (auch 31.02. oder 29.02. außerhalb von Schaltjahren), `BELEGDATUM_AUSSERHALB_ZEITRAUM` (außerhalb Datum von/bis), `BELEGDATUM_AUSSERHALB_WJ` (beim Schreiben) | P2 | primär (Jahresermittlung bei abweichendem WJ: abgeleitet) |
| 11 Belegfeld 1 | Höchstens 36 Zeichen; erlaubt Buchstaben, Ziffern, `_ $ & % * + - /`; keine Leerzeichen, Umlaute, Punkte, Kommas, Semikolons, Doppelpunkte | Fehler `BELEGFELD1_ZU_LANG`, `BELEGFELD1_ZEICHEN`; Buchstaben nur A-Z und a-z | P2 | primär |
| 12 Belegfeld 2 | Zeichen wie Feld 11; Länge laut deutscher Formatbeschreibung 36, laut englischer Fassung 12 Zeichen | Schreiben: höchstens 12 Zeichen (Fehler `BELEGFELD2_ZU_LANG`). Prüfen: Fehler `BELEGFELD2_ZU_LANG` über 36, Warnung `BELEGFELD2_UEBER_12` über 12, Fehler `BELEGFELD2_ZEICHEN` | P2 (DE und EN widersprechen sich, abgerufen 19.10.2026) | primär, Länge **ungeprüft** |
| 14 Buchungstext | Höchstens 60 Zeichen | Fehler `BUCHUNGSTEXT_ZU_LANG`. Formelzeichen am Anfang siehe Abschnitt 1 | P2 | primär |
| 37 KOST1, 38 KOST2 | Höchstens 36 Zeichen, `[\w ]`: Buchstaben, Ziffern, _ und Leerzeichen | Fehler `KOST_FORMAT`. Umlaute sind erlaubt; beim Schreiben müssen alle Zeichen in Windows-1252 darstellbar sein (`ZEICHEN_NICHT_CP1252`) | P2 | primär |
| 114 Festschreibung | `0` oder `1`; leer heißt "nicht definiert, wird automatisch festgeschrieben"; eine `1` in einer Zeile schreibt den ganzen Stapel fest | Schreiben: Feld 114 immer ausdrücklich (`0` oder `1`). Steht im Header 0 und verlangt eine Buchung 1, schreibt der Server nichts (Fehler `FESTSCHREIBUNG_EINZELN`), weil das den ganzen Stapel festschreiben würde. Prüfen: Fehler `FESTSCHREIBUNG_UNGUELTIG`, Hinweis `FESTSCHREIBUNG_LEER`, Warnung `FESTSCHREIBUNG_WIDERSPRUCH` (Zeile 1, Header 0) | P2 | primär |
| 115 Leistungsdatum, 116 Datum Zuord. Steuerperiode | Ist 115 gefüllt, gehört auch 116 dazu | Warnung `LEISTUNGSDATUM_OHNE_STEUERPERIODE`; nur Warnung, weil die DATEV-Musterdatei (P7) eine solche Zeile enthält | P2, P7 | primär |

Nicht umgesetzt: fachliche Prüfungen, die Kontenrahmen oder Mandantendaten voraussetzen (Automatikkonten, gültige BU-Schlüssel je Konto, Steuersätze, OPOS-Regeln, EU-Felder, SEPA-Felder). Der Server enthält bewusst keine Listen aus SKR03 oder SKR04.

## 5. Spaltenüberschriften (Zeile 2), Formatversion 13

Die 125 Überschriften stehen in `src/extf_buchungsstapel_mcp/columns.py` und entsprechen der Liste in P3 (Stand 19.10.2026, Schreibweise mit normalem Bindestrich, z. B. "Beleginfo - Art 1" und "Zusatzinformation- Inhalt 1" ohne Leerzeichen vor dem Bindestrich). Die Liste wurde gegen S2 abgeglichen (0 Abweichungen) und ist in der DATEV-Musterdatei P7 identisch.

Beim Prüfen vergleicht der Server tolerant: Abweichungen nur bei Groß-/Kleinschreibung, Leerzeichen oder Strichvarianten ergeben den Hinweis `SPALTENNAME_SCHREIBWEISE`, andere Abweichungen die Warnung `SPALTENNAME_ABWEICHEND`. DATEV ordnet die Spalten nach Position zu (abgeleitet aus P3: "Überschriftszeile gemäß Formatbeschreibung"); ob abweichende Überschriften den Import stoppen, ist **ungeprüft**.

Die Spalte "Typ" gibt an, ob der Server das Feld als Text (in Anführungszeichen) schreibt. Sie folgt den Feldtypen in P2.

| Nr. | Spaltenüberschrift | Typ |
|---|---|---|
| 1 | Umsatz (ohne Soll/Haben-Kz) | Zahl/Datum |
| 2 | Soll/Haben-Kennzeichen | Text |
| 3 | WKZ Umsatz | Text |
| 4 | Kurs | Zahl/Datum |
| 5 | Basis-Umsatz | Zahl/Datum |
| 6 | WKZ Basis-Umsatz | Text |
| 7 | Konto | Zahl/Datum |
| 8 | Gegenkonto (ohne BU-Schlüssel) | Zahl/Datum |
| 9 | BU-Schlüssel | Text |
| 10 | Belegdatum | Zahl/Datum |
| 11 | Belegfeld 1 | Text |
| 12 | Belegfeld 2 | Text |
| 13 | Skonto | Zahl/Datum |
| 14 | Buchungstext | Text |
| 15 | Postensperre | Zahl/Datum |
| 16 | Diverse Adressnummer | Text |
| 17 | Geschäftspartnerbank | Zahl/Datum |
| 18 | Sachverhalt | Zahl/Datum |
| 19 | Zinssperre | Zahl/Datum |
| 20 | Beleglink | Text |
| 21 | Beleginfo - Art 1 | Text |
| 22 | Beleginfo - Inhalt 1 | Text |
| 23 | Beleginfo - Art 2 | Text |
| 24 | Beleginfo - Inhalt 2 | Text |
| 25 | Beleginfo - Art 3 | Text |
| 26 | Beleginfo - Inhalt 3 | Text |
| 27 | Beleginfo - Art 4 | Text |
| 28 | Beleginfo - Inhalt 4 | Text |
| 29 | Beleginfo - Art 5 | Text |
| 30 | Beleginfo - Inhalt 5 | Text |
| 31 | Beleginfo - Art 6 | Text |
| 32 | Beleginfo - Inhalt 6 | Text |
| 33 | Beleginfo - Art 7 | Text |
| 34 | Beleginfo - Inhalt 7 | Text |
| 35 | Beleginfo - Art 8 | Text |
| 36 | Beleginfo - Inhalt 8 | Text |
| 37 | KOST1 - Kostenstelle | Text |
| 38 | KOST2 - Kostenstelle | Text |
| 39 | Kost-Menge | Zahl/Datum |
| 40 | EU-Land u. UStID (Bestimmung) | Text |
| 41 | EU-Steuersatz (Bestimmung) | Zahl/Datum |
| 42 | Abw. Versteuerungsart | Text |
| 43 | Sachverhalt L+L | Zahl/Datum |
| 44 | Funktionsergänzung L+L | Zahl/Datum |
| 45 | BU 49 Hauptfunktionstyp | Zahl/Datum |
| 46 | BU 49 Hauptfunktionsnummer | Zahl/Datum |
| 47 | BU 49 Funktionsergänzung | Zahl/Datum |
| 48 | Zusatzinformation - Art 1 | Text |
| 49 | Zusatzinformation- Inhalt 1 | Text |
| 50 | Zusatzinformation - Art 2 | Text |
| 51 | Zusatzinformation- Inhalt 2 | Text |
| 52 | Zusatzinformation - Art 3 | Text |
| 53 | Zusatzinformation- Inhalt 3 | Text |
| 54 | Zusatzinformation - Art 4 | Text |
| 55 | Zusatzinformation- Inhalt 4 | Text |
| 56 | Zusatzinformation - Art 5 | Text |
| 57 | Zusatzinformation- Inhalt 5 | Text |
| 58 | Zusatzinformation - Art 6 | Text |
| 59 | Zusatzinformation- Inhalt 6 | Text |
| 60 | Zusatzinformation - Art 7 | Text |
| 61 | Zusatzinformation- Inhalt 7 | Text |
| 62 | Zusatzinformation - Art 8 | Text |
| 63 | Zusatzinformation- Inhalt 8 | Text |
| 64 | Zusatzinformation - Art 9 | Text |
| 65 | Zusatzinformation- Inhalt 9 | Text |
| 66 | Zusatzinformation - Art 10 | Text |
| 67 | Zusatzinformation- Inhalt 10 | Text |
| 68 | Zusatzinformation - Art 11 | Text |
| 69 | Zusatzinformation- Inhalt 11 | Text |
| 70 | Zusatzinformation - Art 12 | Text |
| 71 | Zusatzinformation- Inhalt 12 | Text |
| 72 | Zusatzinformation - Art 13 | Text |
| 73 | Zusatzinformation- Inhalt 13 | Text |
| 74 | Zusatzinformation - Art 14 | Text |
| 75 | Zusatzinformation- Inhalt 14 | Text |
| 76 | Zusatzinformation - Art 15 | Text |
| 77 | Zusatzinformation- Inhalt 15 | Text |
| 78 | Zusatzinformation - Art 16 | Text |
| 79 | Zusatzinformation- Inhalt 16 | Text |
| 80 | Zusatzinformation - Art 17 | Text |
| 81 | Zusatzinformation- Inhalt 17 | Text |
| 82 | Zusatzinformation - Art 18 | Text |
| 83 | Zusatzinformation- Inhalt 18 | Text |
| 84 | Zusatzinformation - Art 19 | Text |
| 85 | Zusatzinformation- Inhalt 19 | Text |
| 86 | Zusatzinformation - Art 20 | Text |
| 87 | Zusatzinformation- Inhalt 20 | Text |
| 88 | Stück | Zahl/Datum |
| 89 | Gewicht | Zahl/Datum |
| 90 | Zahlweise | Zahl/Datum |
| 91 | Forderungsart | Text |
| 92 | Veranlagungsjahr | Zahl/Datum |
| 93 | Zugeordnete Fälligkeit | Zahl/Datum |
| 94 | Skontotyp | Zahl/Datum |
| 95 | Auftragsnummer | Text |
| 96 | Buchungstyp | Text |
| 97 | USt-Schlüssel (Anzahlungen) | Zahl/Datum |
| 98 | EU-Land (Anzahlungen) | Text |
| 99 | Sachverhalt L+L (Anzahlungen) | Zahl/Datum |
| 100 | EU-Steuersatz (Anzahlungen) | Zahl/Datum |
| 101 | Erlöskonto (Anzahlungen) | Zahl/Datum |
| 102 | Herkunft-Kz | Text |
| 103 | Buchungs GUID | Text |
| 104 | KOST-Datum | Zahl/Datum |
| 105 | SEPA-Mandatsreferenz | Text |
| 106 | Skontosperre | Zahl/Datum |
| 107 | Gesellschaftername | Text |
| 108 | Beteiligtennummer | Zahl/Datum |
| 109 | Identifikationsnummer | Text |
| 110 | Zeichnernummer | Text |
| 111 | Postensperre bis | Zahl/Datum |
| 112 | Bezeichnung SoBil-Sachverhalt | Text |
| 113 | Kennzeichen SoBil-Buchung | Zahl/Datum |
| 114 | Festschreibung | Zahl/Datum |
| 115 | Leistungsdatum | Zahl/Datum |
| 116 | Datum Zuord. Steuerperiode | Zahl/Datum |
| 117 | Fälligkeit | Zahl/Datum |
| 118 | Generalumkehr (GU) | Text |
| 119 | Steuersatz | Zahl/Datum |
| 120 | Land | Text |
| 121 | Abrechnungsreferenz | Text |
| 122 | BVV-Position | Zahl/Datum |
| 123 | EU-Land u. UStID (Ursprung) | Text |
| 124 | EU-Steuersatz (Ursprung) | Zahl/Datum |
| 125 | Abw. Skontokonto | Zahl/Datum |

## 6. Import in DATEV (nur Hinweise, der Server importiert nicht)

| Aussage | Quelle | Einstufung |
|---|---|---|
| Import in DATEV Rechnungswesen über Stapelverarbeitung, automatisiert über `KrStaPv.exe` | P5 | primär |
| Import über die Online-API accounting:extf-files (DATEV-Rechenzentrum) | P5, P8 | primär |
| DATEV stellt ein Prüfprogramm für das DATEV-Format zum Download bereit | P5 | primär |
| accounting:extf-files: Sandbox nach Abonnement, Produktion nach technischer Abnahme | P8 (Seite "Erste Schritte") | primär |
| accounting:extf-files: Mindestanforderung Header 700, Buchungsstapel-Format 12 | P8, vermutlich Reiter "Vorgaben" | **ungeprüft** (Fundstelle nicht erneut nachgelesen) |
| Der Buchungsdatenservice prüft nur grundlegend; die vollständige Prüfung passiert in der DATEV-Anwendung | P8, vermutlich Reiter "Vorgaben" | **ungeprüft** (Fundstelle nicht erneut nachgelesen) |
| Dateien nach Monat und Geschäftsvorfall-Art trennen | P8 (vermutlich Reiter "Vorgaben"), S1 | **ungeprüft** bei DATEV, sekundär über S1 |

## 7. Abgleich mit Referenzen

- DATEV-Musterdatei P7 (`EXTF_Buchungsstapel.csv`, 54 Buchungen): 0 Fehler, 3 Warnungen (`UTF8_OHNE_BOM`, `UMSATZ_OHNE_NACHKOMMA`, `LEISTUNGSDATUM_OHNE_STEUERPERIODE`). Die Datei wird wegen der Urheberrechte der DATEV eG nicht mitgeliefert; der Test läuft, wenn `EXTF_MUSTERDATEI` gesetzt ist.
- S2: Die Golden-Files dieses Pakets ergeben dort 0 Fehler; eine mit S2 geschriebene Datei ergibt hier 0 Fehler. Der Test läuft, wenn `EXTF_TS_PROJEKT` gesetzt ist.
- Das Prüfprogramm von DATEV (P5) und ein echter Import in DATEV Rechnungswesen wurden **nicht** ausprobiert.

> **Hinweis:** Eigene Zusammenfassung nach Stand 19.10.2026, ohne Gewähr für Vollständigkeit und Richtigkeit. Maßgeblich ist die aktuelle Formatbeschreibung der DATEV eG im DATEV Developer Portal. Keine Steuerberatung. DATEV ist eine Marke der DATEV eG; dieses Projekt ist kein Produkt der DATEV eG und nicht von ihr geprüft oder freigegeben.
