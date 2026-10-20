"""One test per check code, on raw file content."""

from __future__ import annotations

from datetime import date

import pytest
from conftest import build_raw, codes, header_line, make_booking, make_header, raw_row

from extf_buchungsstapel_mcp import columns as C
from extf_buchungsstapel_mcp import reader
from extf_buchungsstapel_mcp.codes import CODES
from extf_buchungsstapel_mcp.reader import read_extf
from extf_buchungsstapel_mcp.writer import validate


def check(data: bytes, filename: str | None = "EXTF_test.csv"):
    return read_extf(data, filename)


def test_valid_baseline_has_no_findings():
    r = check(build_raw())
    assert r.findings == []
    assert r.valid


def hdr(n: int, value: str) -> str:
    parts = header_line().split(";")
    parts[n - 1] = value
    return ";".join(parts)


HEADER_CASES = [
    ("HEADER_KENNZEICHEN", 1, '"XTF"'),
    ("HEADER_KENNZEICHEN_DTVF", 1, '"DTVF"'),
    ("HEADER_VERSION", 2, "510"),
    ("HEADER_FORMATKATEGORIE", 3, "16"),
    ("HEADER_FORMATNAME", 4, '"Debitoren/Kreditoren"'),
    ("HEADER_FORMATVERSION", 5, "9"),
    ("HEADER_ZEITSTEMPEL", 6, "20261019"),
    ("HEADER_ZEITSTEMPEL", 6, "20260230093000123"),
    ("HEADER_BERATERNUMMER", 11, "999"),
    ("HEADER_BERATERNUMMER", 11, "12345678"),
    ("HEADER_MANDANTENNUMMER", 12, "0"),
    ("HEADER_MANDANTENNUMMER", 12, "100000"),
    ("HEADER_WJ_BEGINN", 13, "20261301"),
    ("HEADER_SACHKONTENLAENGE", 14, "3"),
    ("HEADER_SACHKONTENLAENGE", 14, "9"),
    ("HEADER_DATUM_VON", 15, "2026-09-01"),
    ("HEADER_DATUM_BIS", 16, "20260931"),
    ("HEADER_BEZEICHNUNG", 17, '"' + "x" * 31 + '"'),
    ("HEADER_BEZEICHNUNG", 17, '"Ausgang; Teil 1"'),
    ("HEADER_DIKTATKUERZEL", 18, '"abc"'),
    ("HEADER_BUCHUNGSTYP", 19, "3"),
    ("HEADER_RECHNUNGSLEGUNGSZWECK", 20, "10"),
    ("HEADER_FESTSCHREIBUNG", 21, "2"),
    ("HEADER_FESTSCHREIBUNG_LEER", 21, ""),
    ("HEADER_WKZ", 22, '"Euro"'),
    ("HEADER_SACHKONTENRAHMEN", 27, '"3"'),
    ("HEADER_FELD", 7, "1"),
    ("HEADER_FELD", 24, '"x"'),
    ("HEADER_FELD", 8, '"ABC"'),
    ("HEADER_FELD", 28, "12345"),
    ("TEXT_OHNE_ANFUEHRUNGSZEICHEN", 4, "Buchungsstapel"),
]


@pytest.mark.parametrize("code,field,value", HEADER_CASES)
def test_header_rules(code, field, value):
    r = check(build_raw(header=hdr(field, value)))
    assert code in codes(r), [f.code for f in r.findings]
    assert CODES[code].severity in ("fehler", "warnung", "hinweis")
    hit = next(f for f in r.findings if f.code == code)
    assert hit.line == 1
    assert hit.message


def test_header_field_count():
    r = check(build_raw(header=header_line() + ";"))
    assert "HEADER_FELDANZAHL" in codes(r)


def test_header_period_reversed():
    h = hdr(15, "20260930")
    h = ";".join(h.split(";")[:15] + ["20260901"] + h.split(";")[16:])
    r = check(build_raw(header=h))
    assert "HEADER_ZEITRAUM" in codes(r)


def test_header_period_outside_fiscal_year():
    r = check(build_raw(header=hdr(16, "20270115"), rows=[raw_row()]))
    assert "HEADER_ZEITRAUM_AUSSERHALB_WJ" in codes(r)


def test_header_version_12_is_warning_and_needs_124_columns():
    caps = ";".join(C.BOOKING_COLUMNS_V12)
    r = check(build_raw(header=hdr(5, "12"), captions=caps, rows=[raw_row(count=124)]))
    assert codes(r) == {"HEADER_FORMATVERSION_ALT"}
    assert r.valid


def test_mixed_versions():
    r = check(build_raw(header=hdr(5, "12")))
    assert "VERSION_GEMISCHT" in codes(r)
    r = check(build_raw(captions=";".join(C.BOOKING_COLUMNS_V12), rows=[raw_row(count=124)]))
    assert "VERSION_GEMISCHT" in codes(r)


def test_column_count():
    r = check(build_raw(captions=";".join(C.BOOKING_COLUMNS_V13[:100]), rows=[raw_row(count=100)]))
    assert "SPALTENANZAHL" in codes(r)


def test_column_name_differs():
    caps = list(C.BOOKING_COLUMNS_V13)
    caps[13] = "Text"
    r = check(build_raw(captions=";".join(caps)))
    assert "SPALTENNAME_ABWEICHEND" in codes(r)


def test_column_name_dash_variant_is_only_a_note():
    caps = [c.replace(" - ", " \u2013 ") for c in C.BOOKING_COLUMNS_V13]
    r = check(build_raw(captions=";".join(caps)))
    assert codes(r) == {"SPALTENNAME_SCHREIBWEISE"}
    assert r.valid


def test_missing_caption_line():
    data = (header_line() + "\r\n").encode("cp1252")
    assert "SPALTENZEILE_FEHLT" in codes(check(data))


def test_no_bookings():
    assert "KEINE_BUCHUNGEN" in codes(check(build_raw(rows=[])))


def test_too_many_bookings(monkeypatch):
    monkeypatch.setattr(reader, "MAX_BOOKINGS", 2)
    r = check(build_raw(rows=[raw_row()] * 3))
    assert "ZU_VIELE_BUCHUNGEN" in codes(r)
    assert r.valid  # warning only


def test_file_too_large(monkeypatch):
    monkeypatch.setattr(reader, "MAX_FILE_BYTES", 100)
    r = check(build_raw())
    assert "DATEI_ZU_GROSS" in codes(r)
    assert r.valid


def test_empty_file():
    assert codes(check(b"")) == {"DATEI_LEER"}


def test_filename_prefix():
    assert "DATEINAME_PRAEFIX" in codes(check(build_raw(), "buchungen.csv"))
    assert "DATEINAME_PRAEFIX" not in codes(check(build_raw(), "EXTF_buchungen.CSV"))


def test_row_too_many_fields():
    assert "ZEILE_ZU_VIELE_FELDER" in codes(check(build_raw(rows=[raw_row() + ";"])))


def test_row_too_few_fields():
    r = check(build_raw(rows=[raw_row(count=120)]))
    assert "ZEILE_ZU_WENIGE_FELDER" in codes(r)


ROW_CASES = [
    ("UMSATZ_FEHLT", {1: ""}),
    ("UMSATZ_FORMAT", {1: "1190.00"}),
    ("UMSATZ_FORMAT", {1: "1.190,00"}),
    ("UMSATZ_FORMAT", {1: "12,345"}),
    ("UMSATZ_FORMAT", {1: "12345678901,00"}),
    ("UMSATZ_FORMAT", {1: "abc"}),
    ("UMSATZ_OHNE_NACHKOMMA", {1: "100"}),
    ("UMSATZ_OHNE_NACHKOMMA", {1: "100,5"}),
    ("UMSATZ_NICHT_POSITIV", {1: "0,00"}),
    ("UMSATZ_NICHT_POSITIV", {1: "-5,00"}),
    ("UMSATZ_NICHT_POSITIV", {1: "0"}),
    ("SOLL_HABEN_UNGUELTIG", {2: '"X"'}),
    ("SOLL_HABEN_UNGUELTIG", {2: '"s"'}),
    ("SOLL_HABEN_UNGUELTIG", {2: '""'}),
    ("WKZ_UNGUELTIG", {3: '"eur"'}),
    ("KONTO_FEHLT", {7: ""}),
    ("KONTO_FORMAT", {7: "12A4"}),
    ("KONTO_FORMAT", {7: "0000"}),
    ("KONTO_ZU_LANG", {7: "123456"}),
    ("GEGENKONTO_FEHLT", {8: ""}),
    ("GEGENKONTO_FORMAT", {8: "84 00"}),
    ("GEGENKONTO_ZU_LANG", {8: "1234567890"}),
    ("KONTO_GLEICH_GEGENKONTO", {7: "8400"}),
    ("BU_SCHLUESSEL_FORMAT", {9: '"12345"'}),
    ("BU_SCHLUESSEL_FORMAT", {9: '"9a"'}),
    ("BU_SCHLUESSEL_KURZ", {9: '"9"'}),
    ("BU_SCHLUESSEL_KURZ", {9: '"401"'}),
    ("BELEGFELD2_UEBER_12", {12: '"' + "1" * 13 + '"'}),
    ("FORMELZEICHEN_AM_ANFANG", {14: '"=HYPERLINK(""http://beispiel.example/?x"";""Klick"")"'}),
    ("FORMELZEICHEN_AM_ANFANG", {14: '"+49 Telefon"'}),
    ("FORMELZEICHEN_AM_ANFANG", {14: '"-Rabatt"'}),
    ("FORMELZEICHEN_AM_ANFANG", {14: '"@SUMME(A1)"'}),
    ("FORMELZEICHEN_AM_ANFANG", {14: '"\tText"'}),
    ("FORMELZEICHEN_AM_ANFANG", {11: '"-RE1"'}),
    ("FORMELZEICHEN_AM_ANFANG", {37: '"=1"'}),
    ("FORMELZEICHEN_AM_ANFANG", {20: '"=cmd"'}),
    ("BELEGDATUM_FEHLT", {10: ""}),
    ("BELEGDATUM_FORMAT", {10: "3209"}),
    ("BELEGDATUM_FORMAT", {10: "0213"}),
    ("BELEGDATUM_FORMAT", {10: "209"}),
    ("BELEGDATUM_FORMAT", {10: "3102"}),
    ("BELEGDATUM_AUSSERHALB_ZEITRAUM", {10: "0110"}),
    ("BELEGDATUM_AUSSERHALB_ZEITRAUM", {10: "3108"}),
    ("BELEGFELD1_ZU_LANG", {11: '"' + "A" * 37 + '"'}),
    ("BELEGFELD1_ZEICHEN", {11: '"RE 2026"'}),
    ("BELEGFELD1_ZEICHEN", {11: '"RE.2026"'}),
    ("BELEGFELD1_ZEICHEN", {11: '"Größe1"'}),
    ("BELEGFELD1_ZEICHEN", {11: '"RE:1"'}),
    ("BELEGFELD1_ZEICHEN", {11: '"RE,1"'}),
    ("BELEGFELD1_ZEICHEN", {11: '"RE;1"'}),
    ("BELEGFELD2_ZU_LANG", {12: '"' + "1" * 37 + '"'}),
    ("BELEGFELD2_ZEICHEN", {12: '"01.10.26"'}),
    ("BUCHUNGSTEXT_ZU_LANG", {14: '"' + "x" * 61 + '"'}),
    ("KOST_FORMAT", {37: '"' + "1" * 37 + '"'}),
    ("KOST_FORMAT", {38: '"K-100"'}),
    ("FESTSCHREIBUNG_UNGUELTIG", {114: "2"}),
    ("FESTSCHREIBUNG_LEER", {114: ""}),
    ("LEISTUNGSDATUM_OHNE_STEUERPERIODE", {115: "15092026"}),
    ("TEXT_OHNE_ANFUEHRUNGSZEICHEN", {14: "Muster GmbH"}),
    ("ZAHL_IN_ANFUEHRUNGSZEICHEN", {7: '"10000"'}),
    ("STEUERZEICHEN", {14: '"Text\tmit Tab"'}),
    ("ANFUEHRUNGSZEICHEN_OFFEN", {14: '"offen'}),
    ("ANFUEHRUNGSZEICHEN_OFFEN", {14: 'ab"c'}),
    ("ANFUEHRUNGSZEICHEN_OFFEN", {14: '"a"b'}),
]


@pytest.mark.parametrize("code,overrides", ROW_CASES)
def test_row_rules(code, overrides):
    r = check(build_raw(rows=[raw_row(overrides)]))
    assert code in codes(r), [(f.code, f.value) for f in r.findings]
    hit = next(f for f in r.findings if f.code == code)
    assert hit.line == 3
    assert hit.message


def test_allowed_document_field_characters():
    r = check(build_raw(rows=[raw_row({11: '"Rg32029/2024-A_$&%*+"', 12: '"x"'})]))
    assert r.findings == []


def test_four_digit_bu_key_is_fine():
    assert check(build_raw(rows=[raw_row({9: '"0001"'})])).findings == []


@pytest.mark.parametrize("length,expected", [(12, set()), (13, {"BELEGFELD2_UEBER_12"}), (36, {"BELEGFELD2_UEBER_12"}),
                                             (37, {"BELEGFELD2_ZU_LANG"})])
def test_document_field_2_length(length, expected):
    r = check(build_raw(rows=[raw_row({12: '"' + "1" * length + '"'})]))
    assert codes(r) == expected


def test_cost_center_allows_umlauts():
    r = check(build_raw(rows=[raw_row({37: '"Küche"', 38: '"Büro Süd"'})]))
    assert r.findings == []


def test_negative_numbers_are_no_formula_warning():
    r = check(build_raw(rows=[raw_row({1: "-5,00", 4: "-1,5"})]))
    assert "UMSATZ_NICHT_POSITIV" in codes(r)
    assert "FORMELZEICHEN_AM_ANFANG" not in codes(r)


def test_formula_in_header_text_field():
    r = check(build_raw(header=hdr(9, '"=cmd"')))
    hit = next(f for f in r.findings if f.code == "FORMELZEICHEN_AM_ANFANG")
    assert hit.line == 1 and hit.field.startswith("Header 9")


def test_findings_are_capped_but_counted(monkeypatch):
    monkeypatch.setattr(reader, "MAX_FINDINGS", 5)
    r = check(build_raw(rows=[raw_row({11: '"RE 1"'}) for _ in range(10)]))
    assert len(r.findings) == 6
    assert r.findings[-1].code == "BEFUNDE_GEKUERZT"
    assert r.error_count == 10 and r.dropped["fehler"] == 5
    assert not r.valid


def test_findings_cap_keeps_errors_visible_in_validity(monkeypatch):
    monkeypatch.setattr(reader, "MAX_FINDINGS", 3)
    rows = [raw_row({9: '"9"'}) for _ in range(5)] + [raw_row({11: '"RE 1"'})]
    r = check(build_raw(rows=rows))
    assert r.errors == [] and r.error_count == 1
    assert not r.valid


def test_too_many_bookings_stops_reading(monkeypatch):
    monkeypatch.setattr(reader, "MAX_BOOKINGS", 2)
    r = check(build_raw(rows=[raw_row({11: '"RE 1"'})] * 3))
    assert codes(r) == {"ZU_VIELE_BUCHUNGEN"}
    assert r.rows == []


def test_text_with_semicolon_and_doubled_quotes_is_fine():
    r = check(build_raw(rows=[raw_row({14: '"Müller; ""Wartung"" 5 €"'})]))
    assert r.findings == []
    assert r.rows[0].get(14) == 'Müller; "Wartung" 5 €'


def test_personal_account_one_digit_longer_is_ok():
    r = check(build_raw(rows=[raw_row({7: "12345", 8: "8400"})]))
    assert r.findings == []


def test_sachkontenlaenge_8_allows_9_digits():
    r = check(build_raw(header=hdr(14, "8"), rows=[raw_row({7: "123456789", 8: "84000000"})]))
    assert r.findings == []


def test_document_date_uses_fiscal_year_not_calendar_year():
    # WJ 01.07.2026-30.06.2027, Stapel Januar 2027: 1501 must be 15.01.2027.
    h = header_line(fiscal_year_start=date(2026, 7, 1), date_from=date(2027, 1, 1), date_to=date(2027, 1, 31))
    r = check(build_raw(header=h, rows=[raw_row({10: "1501"})]))
    assert r.findings == []
    assert reader.row_to_booking_dict(r.rows[0], r.header)["belegdatum_iso"] == "2027-01-15"


def test_leap_day():
    h = header_line(fiscal_year_start=date(2028, 1, 1), date_from=date(2028, 2, 1), date_to=date(2028, 2, 29))
    assert check(build_raw(header=h, rows=[raw_row({10: "2902"})])).findings == []
    h = header_line(date_from=date(2026, 2, 1), date_to=date(2026, 2, 28))
    assert "BELEGDATUM_FORMAT" in codes(check(build_raw(header=h, rows=[raw_row({10: "2902"})])))


def test_locking_conflict():
    r = check(build_raw(rows=[raw_row({114: "1"})]))
    assert "FESTSCHREIBUNG_WIDERSPRUCH" in codes(r)
    r = check(build_raw(header=hdr(21, "1"), rows=[raw_row({114: "1"})]))
    assert "FESTSCHREIBUNG_WIDERSPRUCH" not in codes(r)


def test_writer_side_codes():
    h = make_header()
    f = validate(h, [make_booking(document_date=date(2025, 12, 31))])
    assert "BELEGDATUM_AUSSERHALB_WJ" in {x.code for x in f}
    f = validate(h, [make_booking(text="Smiley \U0001F600")])
    assert "ZEICHEN_NICHT_CP1252" in {x.code for x in f}
    f = validate(h, [make_booking(amount=__import__("decimal").Decimal("1.005"))])
    assert "UMSATZ_FORMAT" in {x.code for x in f}
    f = validate(make_header(format_version=12), [make_booking()])
    assert "HEADER_FORMATVERSION" in {x.code for x in f}


def test_every_code_is_tested_somewhere():
    import pathlib
    import re

    text = "".join(p.read_text(encoding="utf-8") for p in pathlib.Path(__file__).parent.glob("test_*.py"))
    used = set(re.findall(r'"([A-Z0-9_]{6,})"', text))
    missing = sorted(set(CODES) - used)
    assert missing == [], f"Ohne Test: {missing}"
