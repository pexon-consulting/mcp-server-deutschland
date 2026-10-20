"""Catalog of check codes with severity, explanation and source quality.

Source quality:
- "primär": directly from DATEV material on developer.datev.de (seen 2026-10-19)
- "abgeleitet": follows from primary rules, but DATEV does not state it as a check
- "sekundär": from third-party documentation only, not confirmed by DATEV (ungeprüft)
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import Severity


@dataclass(frozen=True)
class CodeInfo:
    code: str
    severity: Severity
    explanation: str
    source: str


_CODES: list[CodeInfo] = [
    # file level
    CodeInfo("DATEI_LEER", "fehler", "Die Datei ist leer.", "primär"),
    CodeInfo("DATEI_ZU_GROSS", "warnung", "Die Datei ist größer als 50 MB. Für den Upload über den Buchungsdatenservice wird eine Grenze von 50 MB genannt.", "sekundär"),
    CodeInfo("DATEINAME_PRAEFIX", "warnung", "Der Dateiname beginnt nicht mit EXTF_ und endet nicht auf .csv. DATEV nennt ein festes Präfix EXTF_.", "primär"),
    CodeInfo("ZEICHENSATZ_UNGUELTIG", "fehler", "Die Datei lässt sich weder als Windows-1252 noch als Unicode mit BOM lesen.", "primär"),
    CodeInfo("UTF8_OHNE_BOM", "warnung", "Die Datei ist UTF-8 ohne Byte Order Mark. DATEV liest Unicode nur mit BOM, sonst als Windows-1252; Umlaute werden dann falsch dargestellt.", "primär"),
    CodeInfo("UNICODE_MIT_BOM", "hinweis", "Die Datei ist Unicode mit BOM. Das geht laut DATEV beim manuellen Import und über die API accounting:extf-files, nicht mit dem Programm KrStaPv.", "primär"),
    CodeInfo("ZEILENENDE_KEIN_CRLF", "fehler", "Eine Zeile endet nicht mit CR/LF. DATEV verlangt CR/LF am Ende jeder Zeile.", "primär"),
    CodeInfo("LETZTE_ZEILE_OHNE_CRLF", "warnung", "Die letzte Zeile endet nicht mit CR/LF.", "primär"),
    CodeInfo("ANFUEHRUNGSZEICHEN_OFFEN", "fehler", "Ein Textfeld ist nicht korrekt in Anführungszeichen eingeschlossen. Anführungszeichen im Text müssen verdoppelt werden.", "primär"),
    CodeInfo("STEUERZEICHEN", "fehler", "Ein Feld enthält ein Steuerzeichen (z. B. Tabulator oder Zeilenumbruch). Das ist in Textfeldern nicht zulässig.", "primär"),
    CodeInfo("KEINE_BUCHUNGEN", "warnung", "Die Datei enthält keine Buchungszeilen.", "abgeleitet"),
    CodeInfo("ZU_VIELE_BUCHUNGEN", "warnung", "Mehr als 99.999 Buchungen in einer Datei. Für den Buchungsdatenservice wird diese Grenze genannt. Die Buchungszeilen werden dann nicht gelesen und nicht geprüft.", "sekundär"),
    CodeInfo("BEFUNDE_GEKUERZT", "hinweis", "Ab 10.000 Befunden werden weitere Befunde nur noch gezählt, nicht einzeln aufgeführt. Die Zahlen für Fehler, Warnungen und Hinweise enthalten sie trotzdem.", "abgeleitet"),
    # header
    CodeInfo("HEADER_FELDANZAHL", "fehler", "Der Header hat nicht genau 31 Felder.", "primär"),
    CodeInfo("HEADER_KENNZEICHEN", "fehler", "Feld 1 des Headers ist nicht \"EXTF\" (Fremdsoftware) oder \"DTVF\" (DATEV-Programm).", "primär"),
    CodeInfo("HEADER_KENNZEICHEN_DTVF", "warnung", "Kennzeichen DTVF steht für Exporte aus DATEV-Programmen. Dateien aus Fremdsoftware tragen EXTF.", "primär"),
    CodeInfo("HEADER_VERSION", "fehler", "Die Header-Version (Feld 2) ist nicht 700.", "primär"),
    CodeInfo("HEADER_FORMATKATEGORIE", "fehler", "Die Formatkategorie (Feld 3) ist nicht 21 (Buchungsstapel). Andere Kategorien prüft dieses Werkzeug nicht.", "primär"),
    CodeInfo("HEADER_FORMATNAME", "fehler", "Der Formatname (Feld 4) ist nicht \"Buchungsstapel\".", "primär"),
    CodeInfo("HEADER_FORMATVERSION", "fehler", "Die Formatversion (Feld 5) ist nicht 13 (oder 12).", "primär"),
    CodeInfo("HEADER_FORMATVERSION_ALT", "warnung", "Formatversion 12 ist älter; aktuell ist 13. Für den Buchungsdatenservice nennt DATEV mindestens 12.", "primär"),
    CodeInfo("HEADER_ZEITSTEMPEL", "fehler", "Der Zeitstempel (Feld 6) hat nicht das Format JJJJMMTTHHMMSSmmm.", "primär"),
    CodeInfo("HEADER_BERATERNUMMER", "fehler", "Die Beraternummer (Feld 11) liegt nicht zwischen 1001 und 9999999.", "primär"),
    CodeInfo("HEADER_MANDANTENNUMMER", "fehler", "Die Mandantennummer (Feld 12) liegt nicht zwischen 1 und 99999.", "primär"),
    CodeInfo("HEADER_WJ_BEGINN", "fehler", "WJ-Beginn (Feld 13) ist kein gültiges Datum JJJJMMTT.", "primär"),
    CodeInfo("HEADER_SACHKONTENLAENGE", "fehler", "Die Sachkontenlänge (Feld 14) liegt nicht zwischen 4 und 8.", "primär"),
    CodeInfo("HEADER_DATUM_VON", "fehler", "Datum von (Feld 15) ist kein gültiges Datum JJJJMMTT.", "primär"),
    CodeInfo("HEADER_DATUM_BIS", "fehler", "Datum bis (Feld 16) ist kein gültiges Datum JJJJMMTT.", "primär"),
    CodeInfo("HEADER_ZEITRAUM", "fehler", "Datum von liegt nach Datum bis.", "abgeleitet"),
    CodeInfo("HEADER_ZEITRAUM_AUSSERHALB_WJ", "fehler", "Der Zeitraum des Stapels liegt nicht vollständig im Wirtschaftsjahr ab WJ-Beginn. Weil das Belegdatum kein Jahr enthält, muss der Stapel in einem Wirtschaftsjahr liegen.", "abgeleitet"),
    CodeInfo("HEADER_BEZEICHNUNG", "warnung", "Die Bezeichnung (Feld 17) ist länger als 30 Zeichen oder enthält andere Zeichen als Buchstaben, Ziffern, _, Punkt, Schrägstrich und Leerzeichen.", "primär"),
    CodeInfo("HEADER_DIKTATKUERZEL", "warnung", "Das Diktatkürzel (Feld 18) ist nicht leer, 2 oder 4 Großbuchstaben.", "primär"),
    CodeInfo("HEADER_BUCHUNGSTYP", "fehler", "Der Buchungstyp (Feld 19) ist nicht 1 oder 2.", "primär"),
    CodeInfo("HEADER_RECHNUNGSLEGUNGSZWECK", "fehler", "Der Rechnungslegungszweck (Feld 20) ist nicht 0, 30, 40, 50 oder 64.", "primär"),
    CodeInfo("HEADER_FESTSCHREIBUNG", "fehler", "Die Festschreibung (Feld 21) ist nicht 0 oder 1.", "primär"),
    CodeInfo("HEADER_FESTSCHREIBUNG_LEER", "hinweis", "Feld 21 (Festschreibung) ist leer; DATEV verwendet dann die Vorgabe 1 = Festschreibung.", "primär"),
    CodeInfo("HEADER_WKZ", "fehler", "Die Währung (Feld 22) besteht nicht aus 3 Großbuchstaben.", "primär"),
    CodeInfo("HEADER_SACHKONTENRAHMEN", "warnung", "Der Sachkontenrahmen (Feld 27) ist nicht leer, 2 oder 4 Ziffern.", "primär"),
    CodeInfo("HEADER_FELD", "warnung", "Ein weiteres Header-Feld entspricht nicht dem regulären Ausdruck der Formatbeschreibung (Länge oder Leerfeld).", "primär"),
    # columns
    CodeInfo("SPALTENZEILE_FEHLT", "fehler", "Zeile 2 mit den Spaltenüberschriften fehlt.", "primär"),
    CodeInfo("SPALTENANZAHL", "fehler", "Die Spaltenzeile hat nicht 125 Spalten (Formatversion 13) bzw. 124 (Formatversion 12).", "primär"),
    CodeInfo("VERSION_GEMISCHT", "fehler", "Header und Spaltenzeile gehören zu unterschiedlichen Formatversionen (z. B. Header 12, aber 125 Spalten).", "abgeleitet"),
    CodeInfo("SPALTENNAME_ABWEICHEND", "warnung", "Eine Spaltenüberschrift weicht von der DATEV-Schreibweise ab.", "primär"),
    CodeInfo("SPALTENNAME_SCHREIBWEISE", "hinweis", "Eine Spaltenüberschrift weicht nur in Bindestrich oder Leerzeichen von der DATEV-Schreibweise ab.", "primär"),
    CodeInfo("ZEILE_ZU_VIELE_FELDER", "fehler", "Eine Buchungszeile hat mehr Felder als die Spaltenzeile.", "abgeleitet"),
    CodeInfo("ZEILE_ZU_WENIGE_FELDER", "warnung", "Eine Buchungszeile hat weniger Felder als die Spaltenzeile; fehlende Felder werden hier als leer gelesen. Wie DATEV das behandelt, ist ungeprüft.", "abgeleitet"),
    # bookings
    CodeInfo("UMSATZ_FEHLT", "fehler", "Der Umsatz (Feld 1) ist leer.", "primär"),
    CodeInfo("UMSATZ_FORMAT", "fehler", "Der Umsatz hat nicht das Format 1234,56 (Komma als Dezimaltrenner, höchstens 10 Vor- und 2 Nachkommastellen, kein Tausenderpunkt).", "primär"),
    CodeInfo("UMSATZ_OHNE_NACHKOMMA", "warnung", "Der Umsatz hat keine zwei Nachkommastellen (z. B. 100 statt 100,00). Die Formatbeschreibung verlangt sie; die DATEV-Musterdatei enthält trotzdem solche Werte.", "primär"),
    CodeInfo("UMSATZ_NICHT_POSITIV", "fehler", "Der Umsatz ist 0 oder negativ. Er muss positiv sein; die Richtung steht im Soll/Haben-Kennzeichen.", "primär"),
    CodeInfo("SOLL_HABEN_UNGUELTIG", "fehler", "Das Soll/Haben-Kennzeichen (Feld 2) ist nicht \"S\" oder \"H\".", "primär"),
    CodeInfo("KONTO_FEHLT", "fehler", "Konto (Feld 7) ist leer.", "primär"),
    CodeInfo("KONTO_FORMAT", "fehler", "Konto enthält andere Zeichen als Ziffern oder besteht nur aus Nullen.", "primär"),
    CodeInfo("KONTO_ZU_LANG", "fehler", "Konto ist länger als Sachkontenlänge + 1 (Personenkonten dürfen nur eine Stelle länger sein als Sachkonten).", "primär"),
    CodeInfo("GEGENKONTO_FEHLT", "fehler", "Gegenkonto (Feld 8) ist leer.", "primär"),
    CodeInfo("GEGENKONTO_FORMAT", "fehler", "Gegenkonto enthält andere Zeichen als Ziffern oder besteht nur aus Nullen.", "primär"),
    CodeInfo("GEGENKONTO_ZU_LANG", "fehler", "Gegenkonto ist länger als Sachkontenlänge + 1.", "primär"),
    CodeInfo("KONTO_GLEICH_GEGENKONTO", "warnung", "Konto und Gegenkonto sind gleich.", "abgeleitet"),
    CodeInfo("BU_SCHLUESSEL_FORMAT", "fehler", "Der BU-Schlüssel (Feld 9) enthält andere Zeichen als Ziffern oder mehr als 4 Ziffern.", "primär"),
    CodeInfo("BU_SCHLUESSEL_KURZ", "warnung", "Der BU-Schlüssel hat weniger als 4 Ziffern. Der reguläre Ausdruck der Formatbeschreibung verlangt genau 4; ob DATEV kürzere Schlüssel gleich behandelt, ist ungeprüft. Der Server füllt nicht mit Nullen auf. Mit der Steuerberatung klären.", "primär"),
    CodeInfo("BELEGDATUM_FEHLT", "fehler", "Das Belegdatum (Feld 10) ist leer.", "primär"),
    CodeInfo("BELEGDATUM_FORMAT", "fehler", "Das Belegdatum ist kein gültiges Datum im Format TTMM (oder existiert im ermittelten Jahr nicht, z. B. 2902).", "primär"),
    CodeInfo("BELEGDATUM_AUSSERHALB_ZEITRAUM", "fehler", "Das Belegdatum liegt außerhalb von Datum von/bis des Headers.", "abgeleitet"),
    CodeInfo("BELEGDATUM_AUSSERHALB_WJ", "fehler", "Das Belegdatum liegt außerhalb des Wirtschaftsjahres ab WJ-Beginn und lässt sich als TTMM nicht eindeutig darstellen.", "abgeleitet"),
    CodeInfo("BELEGFELD1_ZU_LANG", "fehler", "Belegfeld 1 ist länger als 36 Zeichen.", "primär"),
    CodeInfo("BELEGFELD1_ZEICHEN", "fehler", "Belegfeld 1 enthält unerlaubte Zeichen. Erlaubt sind A-Z, a-z, 0-9, _ und $ & % * + - /; nicht erlaubt sind z. B. Leerzeichen, Umlaute, Punkt, Komma, Semikolon, Doppelpunkt.", "primär"),
    CodeInfo("BELEGFELD2_ZU_LANG", "fehler", "Belegfeld 2 ist zu lang: beim Prüfen länger als 36 Zeichen, beim Schreiben länger als 12 Zeichen.", "primär"),
    CodeInfo("BELEGFELD2_UEBER_12", "warnung", "Belegfeld 2 ist länger als 12 Zeichen. Die deutsche DATEV-Formatbeschreibung erlaubt 36, die englische 12; sicher ist höchstens 12.", "primär"),
    CodeInfo("BELEGFELD2_ZEICHEN", "fehler", "Belegfeld 2 enthält unerlaubte Zeichen (wie Belegfeld 1).", "primär"),
    CodeInfo("BUCHUNGSTEXT_ZU_LANG", "fehler", "Der Buchungstext (Feld 14) ist länger als 60 Zeichen.", "primär"),
    CodeInfo("KOST_FORMAT", "fehler", "KOST1 oder KOST2 ist länger als 36 Zeichen oder enthält andere Zeichen als Buchstaben (auch Umlaute), Ziffern, _ und Leerzeichen.", "primär"),
    CodeInfo("FORMELZEICHEN_AM_ANFANG", "warnung", "Ein Textfeld beginnt mit =, +, -, @, Tabulator oder Wagenrücklauf. Tabellenprogramme wie Excel werten so einen Wert beim Öffnen der CSV als Formel aus. DATEV wertet keine Formeln aus.", "sekundär"),
    CodeInfo("FORMELZEICHEN_BEIM_SCHREIBEN", "fehler", "Beim Schreiben lehnt dieser Server Buchungstext, Belegfeld 1, Belegfeld 2, KOST1 und KOST2 ab, die mit = oder @ beginnen, damit Tabellenprogramme den Wert nicht als Formel ausführen.", "sekundär"),
    CodeInfo("WKZ_UNGUELTIG", "fehler", "WKZ Umsatz (Feld 3) besteht nicht aus 3 Großbuchstaben.", "primär"),
    CodeInfo("FESTSCHREIBUNG_UNGUELTIG", "fehler", "Festschreibung (Feld 114) ist nicht leer, 0 oder 1.", "primär"),
    CodeInfo("FESTSCHREIBUNG_LEER", "hinweis", "Festschreibung (Feld 114) ist leer; laut DATEV bedeutet das 'nicht definiert; wird automatisch festgeschrieben'.", "primär"),
    CodeInfo("FESTSCHREIBUNG_WIDERSPRUCH", "warnung", "Der Header sagt 'keine Festschreibung', aber mindestens eine Buchung hat Festschreibung 1. Laut DATEV wird dann der ganze Stapel festgeschrieben.", "primär"),
    CodeInfo("FESTSCHREIBUNG_EINZELN", "fehler", "Beim Schreiben: Der Kopf sagt 'keine Festschreibung', aber mindestens eine Buchung verlangt Festschreibung. Laut DATEV würde dann der ganze Stapel nach dem Import festgeschrieben; der Server schreibt so eine Datei nicht. Setzen Sie die Festschreibung im Kopf oder lassen Sie sie bei der Buchung weg.", "primär"),
    CodeInfo("LEISTUNGSDATUM_OHNE_STEUERPERIODE", "warnung", "Feld 115 (Leistungsdatum) ist gefüllt, Feld 116 (Datum Zuord. Steuerperiode) aber leer. Laut Formatbeschreibung gehören dann beide dazu; die DATEV-Musterdatei enthält trotzdem eine solche Zeile, daher nur Warnung.", "primär"),
    CodeInfo("TEXT_OHNE_ANFUEHRUNGSZEICHEN", "warnung", "Ein Textfeld steht nicht in Anführungszeichen. DATEV verlangt Anführungszeichen für alle Textfelder.", "primär"),
    CodeInfo("ZAHL_IN_ANFUEHRUNGSZEICHEN", "hinweis", "Ein Zahlenfeld steht in Anführungszeichen.", "primär"),
    CodeInfo("EINGABE_UNGUELTIG", "fehler", "Ein Wert in der Eingabe (JSON, CSV oder Tool-Aufruf) lässt sich nicht lesen, z. B. ein Datum oder Betrag in unbekanntem Format.", "abgeleitet"),
    CodeInfo("ZEICHEN_NICHT_CP1252", "fehler", "Ein Text enthält Zeichen, die es in Windows-1252 nicht gibt (z. B. Emoji). Die Datei wird in Windows-1252 geschrieben.", "primär"),
]

CODES: dict[str, CodeInfo] = {c.code: c for c in _CODES}


def severity_of(code: str) -> Severity:
    return CODES[code].severity
