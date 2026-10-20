"""Header fields and column captions of the DATEV-Format, category Buchungsstapel.

Sources (seen 2026-10-19), see SPEZIFIKATION.md:
- column captions: sample file on developer.datev.de (getting-started page and
  Musterdaten download), 125 captions for format version 13
- field types (text vs. number): quoting in the field expressions of the
  Buchungsstapel format description on developer.datev.de
"""

from __future__ import annotations

from dataclasses import dataclass

FORMAT_DESCRIPTION_URL = (
    "https://developer.datev.de/de/file-formats/details/datev-format/format-description/booking-batch"
)
HEADER_DESCRIPTION_URL = (
    "https://developer.datev.de/de/file-formats/details/datev-format/format-description/header"
)

HEADER_VERSION = 700
CATEGORY_BOOKING_BATCH = 21
CATEGORY_NAME = "Buchungsstapel"
FORMAT_VERSION = 13
SUPPORTED_FORMAT_VERSIONS = (12, 13)
HEADER_FIELD_COUNT = 31


def _build_captions() -> tuple[str, ...]:
    cols = [
        "Umsatz (ohne Soll/Haben-Kz)",
        "Soll/Haben-Kennzeichen",
        "WKZ Umsatz",
        "Kurs",
        "Basis-Umsatz",
        "WKZ Basis-Umsatz",
        "Konto",
        "Gegenkonto (ohne BU-Schlüssel)",
        "BU-Schlüssel",
        "Belegdatum",
        "Belegfeld 1",
        "Belegfeld 2",
        "Skonto",
        "Buchungstext",
        "Postensperre",
        "Diverse Adressnummer",
        "Geschäftspartnerbank",
        "Sachverhalt",
        "Zinssperre",
        "Beleglink",
    ]
    for i in range(1, 9):
        cols += [f"Beleginfo - Art {i}", f"Beleginfo - Inhalt {i}"]
    cols += [
        "KOST1 - Kostenstelle",
        "KOST2 - Kostenstelle",
        "Kost-Menge",
        "EU-Land u. UStID (Bestimmung)",
        "EU-Steuersatz (Bestimmung)",
        "Abw. Versteuerungsart",
        "Sachverhalt L+L",
        "Funktionsergänzung L+L",
        "BU 49 Hauptfunktionstyp",
        "BU 49 Hauptfunktionsnummer",
        "BU 49 Funktionsergänzung",
    ]
    # DATEV writes "Zusatzinformation- Inhalt n" without a space before the hyphen.
    for i in range(1, 21):
        cols += [f"Zusatzinformation - Art {i}", f"Zusatzinformation- Inhalt {i}"]
    cols += [
        "Stück",
        "Gewicht",
        "Zahlweise",
        "Forderungsart",
        "Veranlagungsjahr",
        "Zugeordnete Fälligkeit",
        "Skontotyp",
        "Auftragsnummer",
        "Buchungstyp",
        "USt-Schlüssel (Anzahlungen)",
        "EU-Land (Anzahlungen)",
        "Sachverhalt L+L (Anzahlungen)",
        "EU-Steuersatz (Anzahlungen)",
        "Erlöskonto (Anzahlungen)",
        "Herkunft-Kz",
        "Buchungs GUID",
        "KOST-Datum",
        "SEPA-Mandatsreferenz",
        "Skontosperre",
        "Gesellschaftername",
        "Beteiligtennummer",
        "Identifikationsnummer",
        "Zeichnernummer",
        "Postensperre bis",
        "Bezeichnung SoBil-Sachverhalt",
        "Kennzeichen SoBil-Buchung",
        "Festschreibung",
        "Leistungsdatum",
        "Datum Zuord. Steuerperiode",
        "Fälligkeit",
        "Generalumkehr (GU)",
        "Steuersatz",
        "Land",
        "Abrechnungsreferenz",
        "BVV-Position",
        "EU-Land u. UStID (Ursprung)",
        "EU-Steuersatz (Ursprung)",
        "Abw. Skontokonto",
    ]
    return tuple(cols)


BOOKING_COLUMNS_V13: tuple[str, ...] = _build_captions()
# Format version 13 added field 125 (DATEV changelog, February 2024).
BOOKING_COLUMNS_V12: tuple[str, ...] = BOOKING_COLUMNS_V13[:124]

COLUMNS_BY_VERSION: dict[int, tuple[str, ...]] = {13: BOOKING_COLUMNS_V13, 12: BOOKING_COLUMNS_V12}

# 1-based field numbers whose expression in the DATEV format description is
# enclosed in quotes (text fields). Field 6 has no expression; DATEV's sample
# file quotes it, so it is treated as text.
TEXT_FIELDS: frozenset[int] = frozenset(
    {2, 3, 6, 9, 11, 12, 14, 16, 20}
    | set(range(21, 37))
    | {37, 38, 40, 42}
    | set(range(48, 88))
    | {91, 95, 96, 98, 102, 103, 105, 107, 109, 110, 112, 118, 120, 121, 123}
)

# Field numbers used by this package.
F_AMOUNT = 1
F_DEBIT_CREDIT = 2
F_CURRENCY = 3
F_ACCOUNT = 7
F_CONTRA_ACCOUNT = 8
F_BU_KEY = 9
F_DOCUMENT_DATE = 10
F_DOCUMENT_FIELD_1 = 11
F_DOCUMENT_FIELD_2 = 12
F_TEXT = 14
F_COST_CENTER_1 = 37
F_COST_CENTER_2 = 38
F_LOCKING = 114
F_SERVICE_DATE = 115
F_TAX_PERIOD_DATE = 116


@dataclass(frozen=True)
class FieldInfo:
    number: int
    name: str
    kind: str  # "Text" or "Zahl"
    description: str
    format: str
    used: bool


# Short descriptions in our own words for the fields this package writes and checks.
_CORE: dict[int, tuple[str, str]] = {
    1: ("Betrag der Buchung, immer positiv; die Richtung steht im Soll/Haben-Kennzeichen.",
        "bis 10 Vorkommastellen, Komma, genau 2 Nachkommastellen, nicht 0,00 (z. B. 1190,00)"),
    2: ("Gibt an, ob der Betrag auf dem Konto (Feld 7) im Soll oder im Haben steht.",
        "\"S\" oder \"H\""),
    3: ("Währung des Umsatzes; leer bedeutet die Währung aus dem Header (Feld 22).",
        "3 Großbuchstaben nach ISO 4217, z. B. \"EUR\""),
    7: ("Sach- oder Personenkonto der Buchung.",
        "nur Ziffern, nicht nur Nullen; Sachkonten höchstens Sachkontenlänge, Personenkonten Sachkontenlänge + 1"),
    8: ("Gegenkonto der Buchung (ohne BU-Schlüssel).",
        "wie Konto"),
    9: ("Steuerungskennzeichen, z. B. für einen Steuerschlüssel. Welcher Schlüssel richtig ist, klärt die Steuerberatung.",
        "Ziffern in Anführungszeichen; der reguläre Ausdruck der Formatbeschreibung verlangt 4 Ziffern. 1-3 Ziffern ergeben eine Warnung (ungeprüft, ob DATEV sie gleich behandelt)"),
    10: ("Datum des Belegs ohne Jahr; das Jahr ergibt sich aus dem Wirtschaftsjahr im Header.",
         "TTMM, z. B. 0105 für den 1. Mai"),
    11: ("Rechnungs- oder Belegnummer, dient auch als Schlüssel für den Ausgleich offener Posten.",
         "höchstens 36 Zeichen: A-Z, a-z, 0-9, _ und $ & % * + - /; keine Leerzeichen, Umlaute, Punkte, Kommas"),
    12: ("Zweite Belegnummer oder OPOS-Information, z. B. ein Fälligkeitsdatum.",
         "Zeichen wie Belegfeld 1; Länge laut deutscher Formatbeschreibung 36, laut englischer 12 Zeichen. "
         "Dieser Server schreibt höchstens 12 und warnt beim Prüfen ab 13"),
    14: ("Freier Buchungstext.",
         "höchstens 60 Zeichen, keine Steuerzeichen, Zeichensatz Windows-1252; beim Schreiben nicht mit = oder @ am Anfang"),
    37: ("Kostenstelle 1 für die Kostenrechnung.",
         "höchstens 36 Zeichen: Buchstaben (auch Umlaute), Ziffern, _ und Leerzeichen"),
    38: ("Kostenstelle 2 für die Kostenrechnung.",
         "wie KOST1"),
    114: ("Festschreibung je Buchung. Steht bei einer Buchung 1, wird laut DATEV der ganze Stapel nach dem Import festgeschrieben. "
          "Leer bedeutet laut DATEV 'nicht definiert; wird automatisch festgeschrieben', daher schreibt dieser Server den Wert immer aus. "
          "Steht im Header 0, lehnt der Server beim Schreiben eine Buchung mit 1 ab (FESTSCHREIBUNG_EINZELN).",
          "0 oder 1"),
}


def booking_field_info(number: int) -> FieldInfo:
    name = BOOKING_COLUMNS_V13[number - 1]
    kind = "Text" if number in TEXT_FIELDS else "Zahl"
    if number in _CORE:
        desc, fmt = _CORE[number]
        return FieldInfo(number, name, kind, desc, fmt, True)
    return FieldInfo(
        number,
        name,
        kind,
        "Wird von diesem Server nicht befüllt und nicht inhaltlich geprüft. Details stehen in der "
        "DATEV-Formatbeschreibung.",
        "Text in Anführungszeichen" if kind == "Text" else "Zahl ohne Anführungszeichen",
        False,
    )


@dataclass(frozen=True)
class HeaderFieldInfo:
    number: int
    name: str
    required: str  # "Pflicht", "optional" or "Leerfeld"
    description: str
    format: str


HEADER_FIELDS: tuple[HeaderFieldInfo, ...] = (
    HeaderFieldInfo(1, "Kennzeichen", "Pflicht", "EXTF für Dateien aus Fremdsoftware, DTVF für Dateien aus DATEV-Programmen.", "\"EXTF\" oder \"DTVF\""),
    HeaderFieldInfo(2, "Versionsnummer", "Pflicht", "Version des Headers.", "700"),
    HeaderFieldInfo(3, "Formatkategorie", "Pflicht", "Art der Daten; 21 steht für Buchungsstapel.", "21"),
    HeaderFieldInfo(4, "Formatname", "Pflicht", "Name der Formatkategorie.", "\"Buchungsstapel\""),
    HeaderFieldInfo(5, "Formatversion", "Pflicht", "Version des Satzaufbaus; für Buchungsstapel 13 (12 mit 124 Spalten).", "13"),
    HeaderFieldInfo(6, "Erzeugt am", "Pflicht", "Zeitstempel der Erzeugung.", "JJJJMMTTHHMMSSmmm (17 Ziffern)"),
    HeaderFieldInfo(7, "Importiert", "Leerfeld", "Bleibt leer.", "leer"),
    HeaderFieldInfo(8, "Herkunft", "optional", "Kürzel der Herkunft der Daten.", "Text, 0-2 Zeichen"),
    HeaderFieldInfo(9, "Exportiert von", "optional", "Name der exportierenden Person oder Anwendung.", "Text, 0-25 Zeichen"),
    HeaderFieldInfo(10, "Importiert von", "optional", "Name der importierenden Person.", "Text, 0-25 Zeichen"),
    HeaderFieldInfo(11, "Beraternummer", "Pflicht", "Beraternummer des Bestands in DATEV.", "1001-9999999"),
    HeaderFieldInfo(12, "Mandantennummer", "Pflicht", "Mandantennummer des Bestands in DATEV.", "1-99999"),
    HeaderFieldInfo(13, "WJ-Beginn", "Pflicht", "Beginn des Wirtschaftsjahres; daraus ergibt sich das Jahr der Belegdaten.", "JJJJMMTT"),
    HeaderFieldInfo(14, "Sachkontenlänge", "Pflicht", "Stellenzahl der Sachkonten; muss zur Einstellung des Mandanten in DATEV passen.", "4-8"),
    HeaderFieldInfo(15, "Datum von", "Pflicht", "Beginn des Zeitraums des Stapels.", "JJJJMMTT"),
    HeaderFieldInfo(16, "Datum bis", "Pflicht", "Ende des Zeitraums des Stapels.", "JJJJMMTT"),
    HeaderFieldInfo(17, "Bezeichnung", "optional", "Bezeichnung des Stapels, z. B. Rechnungsausgang 02/2026.", "Text, 0-30 Zeichen"),
    HeaderFieldInfo(18, "Diktatkürzel", "optional", "Kürzel der bearbeitenden Person in Großbuchstaben.", "leer, 2 oder 4 Großbuchstaben"),
    HeaderFieldInfo(19, "Buchungstyp", "optional", "1 = Finanzbuchführung, 2 = Jahresabschluss.", "1 oder 2"),
    HeaderFieldInfo(20, "Rechnungslegungszweck", "optional", "0 = unabhängig, 30 Steuerrecht, 40 Kalkulatorik, 50 Handelsrecht, 64 IFRS.", "0, 30, 40, 50, 64"),
    HeaderFieldInfo(21, "Festschreibung", "optional", "0 = keine Festschreibung, 1 = Festschreibung (DATEV-Vorgabe, wenn leer).", "0 oder 1"),
    HeaderFieldInfo(22, "WKZ", "optional", "Währung des Stapels.", "\"EUR\" oder anderer ISO-Code"),
    HeaderFieldInfo(23, "Reserviert", "Leerfeld", "Bleibt leer.", "leer"),
    HeaderFieldInfo(24, "Derivatskennzeichen", "Leerfeld", "Bleibt leer (leerer Text).", "\"\""),
    HeaderFieldInfo(25, "Reserviert", "Leerfeld", "Bleibt leer.", "leer"),
    HeaderFieldInfo(26, "Reserviert", "Leerfeld", "Bleibt leer.", "leer"),
    HeaderFieldInfo(27, "Sachkontenrahmen", "optional", "Kontenrahmen der Buchungen, z. B. \"03\" oder \"04\".", "Text, leer, 2 oder 4 Ziffern"),
    HeaderFieldInfo(28, "ID der Branchenlösung", "optional", "Nur bei einer DATEV-Branchenlösung.", "0-4 Ziffern"),
    HeaderFieldInfo(29, "Reserviert", "Leerfeld", "Bleibt leer.", "leer"),
    HeaderFieldInfo(30, "Reserviert", "Leerfeld", "Bleibt leer (leerer Text).", "\"\""),
    HeaderFieldInfo(31, "Anwendungsinformation", "optional", "Verarbeitungskennzeichen der abgebenden Anwendung.", "Text, 0-16 Zeichen"),
)

HEADER_TEXT_FIELDS: frozenset[int] = frozenset({1, 4, 8, 9, 10, 17, 18, 22, 24, 27, 30, 31})


def normalize_caption(caption: str) -> str:
    """Compare captions tolerantly: dash variants and spacing around hyphens."""
    s = caption.replace("\u2013", "-").replace("\u2014", "-").replace("\u2011", "-")
    s = " ".join(s.split())
    s = s.replace(" -", "-").replace("- ", "-")
    return s.casefold()
