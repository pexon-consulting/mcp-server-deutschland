from __future__ import annotations

import hashlib
from datetime import date, datetime
from decimal import Decimal

import pytest
from conftest import FIXTURES, make_booking, make_header

from extf_buchungsstapel_mcp import columns as C
from extf_buchungsstapel_mcp.model import ExtfValidationError
from extf_buchungsstapel_mcp.reader import read_extf, row_to_booking_dict
from extf_buchungsstapel_mcp.writer import build_extf, format_amount, format_line, header_fields

# Kopfzeile aus dem Beispiel der DATEV-Formatbeschreibung (Header), Stand 19.10.2026.
DATEV_HEADER_EXAMPLE = (
    '"EXTF";700;21;"Buchungsstapel";13;20240130140440439;;"RE";"";"";29098;55003;20240101;4;'
    '20240101;20240831;"Buchungsstapel";"WD";1;0;0;"EUR";;"";;;"03";;;"";""'
)


def datev_example_header():
    return make_header(
        consultant_number=29098, client_number=55003, fiscal_year_start=date(2024, 1, 1),
        account_length=4, date_from=date(2024, 1, 1), date_to=date(2024, 8, 31),
        description="Buchungsstapel", dictation_code="WD", origin="RE", chart_of_accounts="03",
        created_at=datetime(2024, 1, 30, 14, 4, 40, 439000),
    )


def golden_cases():
    """Fixed inputs for the golden files in tests/fixtures."""
    return {
        "EXTF_golden_minimal.csv": (make_header(), [make_booking()]),
        "EXTF_golden_umlaute.csv": (
            make_header(description="Ausgaben Büro 09/2026", dictation_code="MM"),
            [
                make_booking(amount=Decimal("59.50"), account="4930", contra_account="1200",
                             document_date=date(2026, 9, 15), bu_key="9", document_field_1="ER-4711",
                             text="Bürobedarf Größe A4 für 5 €", cost_center_1="100"),
                make_booking(amount=Decimal("2380"), debit_credit="H", account="70000", contra_account="3400",
                             document_date=date(2026, 9, 30), document_field_1="LS/2026/09-1",
                             document_field_2="30092026", text='Nordlicht Beispiel GmbH "Wartung"; Teil 2'),
                make_booking(amount=Decimal("0.01"), account="1800", contra_account="1200",
                             document_date=date(2026, 9, 30), document_field_1="", text=""),
            ],
        ),
        "EXTF_golden_datev_kopf.csv": (
            datev_example_header(),
            [make_booking(document_date=date(2024, 1, 31), document_field_1="Rg32029", text="Beispiel")],
        ),
    }


def test_header_matches_datev_example_byte_for_byte():
    assert format_line(*header_fields(datev_example_header())) == DATEV_HEADER_EXAMPLE


@pytest.mark.parametrize("name", sorted(golden_cases()))
def test_golden_files(name):
    header, bookings = golden_cases()[name]
    expected = (FIXTURES / name).read_bytes()
    assert build_extf(header, bookings) == expected


@pytest.mark.parametrize("name", sorted(golden_cases()))
def test_golden_files_are_valid(name):
    r = read_extf((FIXTURES / name).read_bytes(), name)
    # The Umlaute file deliberately carries a short BU key ("9") to cover BU_SCHLUESSEL_KURZ.
    allowed = {"BU_SCHLUESSEL_KURZ"} if name == "EXTF_golden_umlaute.csv" else set()
    assert r.valid
    assert {f.code for f in r.findings if f.severity != "hinweis"} == allowed


def test_bytes_cp1252_crlf_quotes():
    data = build_extf(make_header(), [make_booking(text='Äpfel Öl Übung ß "x" 5 €')])
    assert data.count(b"\r\n") == 3
    assert b"\n" not in data.replace(b"\r\n", b"")
    assert b'"\xc4pfel \xd6l \xdcbung \xdf ""x"" 5 \x80"' in data
    assert "€".encode("cp1252") == b"\x80"
    assert not data.startswith(b"\xef\xbb\xbf")
    lines = data.split(b"\r\n")
    assert lines[1].decode("cp1252") == ";".join(C.BOOKING_COLUMNS_V13)
    assert lines[2].startswith(b'1190,00;"S";"";;;"";10000;8400;"";0209;"RE2026-0815";"";;"')
    assert lines[3] == b""


def test_every_line_has_right_field_count():
    data = build_extf(make_header(), [make_booking(text="a;b;c")])
    r = read_extf(data, "EXTF_x.csv")
    assert len(r.header_fields) == 31
    assert len(r.columns) == 125
    assert all(len(row.values) == 125 for row in r.rows)


def test_roundtrip_write_read():
    bookings = golden_cases()["EXTF_golden_umlaute.csv"][1]
    header = golden_cases()["EXTF_golden_umlaute.csv"][0]
    r = read_extf(build_extf(header, bookings), "EXTF_x.csv")
    got = [row_to_booking_dict(row, r.header) for row in r.rows]
    assert [g["umsatz"] for g in got] == ["59,50", "2380,00", "0,01"]
    assert [g["soll_haben"] for g in got] == ["S", "H", "S"]
    assert [g["konto"] for g in got] == ["4930", "70000", "1800"]
    assert [g["belegdatum_iso"] for g in got] == ["2026-09-15", "2026-09-30", "2026-09-30"]
    assert got[0]["buchungstext"] == "Bürobedarf Größe A4 für 5 €"
    assert got[1]["buchungstext"] == 'Nordlicht Beispiel GmbH "Wartung"; Teil 2'
    assert got[0]["bu_schluessel"] == "9"
    assert got[0]["kost1"] == "100"
    assert [g["festschreibung"] for g in got] == ["0", "0", "0"]
    assert r.header.description == "Ausgaben Büro 09/2026"


def test_format_amount():
    assert format_amount(Decimal("1234.5")) == "1234,50"
    assert format_amount(Decimal("0.01")) == "0,01"
    assert format_amount(Decimal("9999999999.99")) == "9999999999,99"


def test_header_locking_and_empty_description():
    line = format_line(*header_fields(make_header(locking=True, description="")))
    parts = line.split(";")
    assert parts[20] == "1"
    assert parts[16] == '""'


@pytest.mark.parametrize("kw,code", [
    (dict(amount=Decimal("0")), "UMSATZ_NICHT_POSITIV"),
    (dict(amount=Decimal("-1")), "UMSATZ_NICHT_POSITIV"),
    (dict(debit_credit="X"), "SOLL_HABEN_UNGUELTIG"),
    (dict(account="123456"), "KONTO_ZU_LANG"),
    (dict(document_date=date(2026, 10, 1)), "BELEGDATUM_AUSSERHALB_ZEITRAUM"),
    (dict(text="x" * 61), "BUCHUNGSTEXT_ZU_LANG"),
    (dict(document_field_1="RE 1"), "BELEGFELD1_ZEICHEN"),
    (dict(text="Zeile1\nZeile2"), "STEUERZEICHEN"),
])
def test_writer_refuses_invalid_bookings(kw, code):
    with pytest.raises(ExtfValidationError) as exc:
        build_extf(make_header(), [make_booking(**kw)])
    assert code in {f.code for f in exc.value.findings}
    assert all(f.line for f in exc.value.findings if f.code == code)


def test_writer_refuses_invalid_header():
    with pytest.raises(ExtfValidationError) as exc:
        build_extf(make_header(account_length=3), [make_booking()])
    assert "HEADER_SACHKONTENLAENGE" in {f.code for f in exc.value.findings}


def test_single_locked_booking_is_refused_before_writing():
    with pytest.raises(ExtfValidationError) as exc:
        build_extf(make_header(), [make_booking(), make_booking(locking=True)])
    hit = [f for f in exc.value.findings if f.code == "FESTSCHREIBUNG_EINZELN"]
    assert len(hit) == 1 and hit[0].severity == "fehler" and hit[0].line == 4


def test_locking_consistent_with_header_is_written():
    data = build_extf(make_header(locking=True), [make_booking(locking=True), make_booking(locking=False)])
    r = read_extf(data, "EXTF_x.csv")
    assert r.findings == []
    assert [row.get(114) for row in r.rows] == ["1", "0"]


@pytest.mark.parametrize("kw,field", [
    (dict(text="=cmd|' /C calc'!A0"), "14 Buchungstext"),
    (dict(text='=HYPERLINK("http://beispiel.example/?x";"Klick")'), "14 Buchungstext"),
    (dict(text="@SUMME(A1)"), "14 Buchungstext"),
    (dict(cost_center_1="=1"), "37 KOST1 - Kostenstelle"),
    (dict(cost_center_2="@x"), "38 KOST2 - Kostenstelle"),
    (dict(document_field_1="=1"), "11 Belegfeld 1"),
    (dict(document_field_2="@1"), "12 Belegfeld 2"),
])
def test_writer_refuses_formula_start(kw, field):
    with pytest.raises(ExtfValidationError) as exc:
        build_extf(make_header(), [make_booking(**kw)])
    hits = [f for f in exc.value.findings if f.code == "FORMELZEICHEN_BEIM_SCHREIBEN"]
    assert [(f.field, f.severity) for f in hits] == [(field, "fehler")]
    assert not any(f.code == "FORMELZEICHEN_AM_ANFANG" and f.field == field for f in exc.value.findings)


def test_writer_allows_plus_and_minus_with_warning():
    data = build_extf(make_header(), [make_booking(text="+49 Telefon", document_field_1="-RE1")])
    r = read_extf(data, "EXTF_x.csv")
    assert r.valid
    assert sorted(f.field for f in r.findings if f.code == "FORMELZEICHEN_AM_ANFANG") == ["11 Belegfeld 1", "14 Buchungstext"]


@pytest.mark.parametrize("length", [13, 36])
def test_writer_refuses_document_field_2_over_12(length):
    with pytest.raises(ExtfValidationError) as exc:
        build_extf(make_header(), [make_booking(document_field_2="1" * length)])
    got = [f.code for f in exc.value.findings]
    assert got == ["BELEGFELD2_ZU_LANG"]


def test_writer_accepts_document_field_2_with_12():
    r = read_extf(build_extf(make_header(), [make_booking(document_field_2="1" * 12)]), "EXTF_x.csv")
    assert r.findings == []


def test_short_bu_key_is_written_unchanged_with_warning():
    data = build_extf(make_header(), [make_booking(bu_key="9")])
    r = read_extf(data, "EXTF_x.csv")
    assert r.rows[0].get(9) == "9"
    assert {f.code for f in r.findings} == {"BU_SCHLUESSEL_KURZ"}


def test_writer_accepts_umlauts_in_cost_center_but_checks_cp1252():
    r = read_extf(build_extf(make_header(), [make_booking(cost_center_1="Küche", cost_center_2="Büro Süd")]), "EXTF_x.csv")
    assert r.findings == []
    assert r.rows[0].get(37) == "Küche"
    with pytest.raises(ExtfValidationError) as exc:
        build_extf(make_header(), [make_booking(cost_center_1="K\u0101che")])
    assert "ZEICHEN_NICHT_CP1252" in {f.code for f in exc.value.findings}


def test_writer_is_deterministic_with_created_at():
    a = build_extf(make_header(), [make_booking()])
    b = build_extf(make_header(), [make_booking()])
    assert hashlib.sha256(a).hexdigest() == hashlib.sha256(b).hexdigest()
