from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import pytest
from conftest import FIXTURES

from extf_buchungsstapel_mcp.importer import InputError, load_csv, load_json, parse_amount, parse_date
from extf_buchungsstapel_mcp.reader import read_extf
from extf_buchungsstapel_mcp.writer import build_extf


@pytest.mark.parametrize("raw,expected", [
    ("1190,00", "1190.00"), ("1190.00", "1190.00"), (1190, "1190"), (59.5, "59.5"),
    (0.1, "0.1"), ("  12,5 ", "12.5"), (Decimal("3.30"), "3.30"),
])
def test_parse_amount(raw, expected):
    assert parse_amount(raw) == Decimal(expected)


@pytest.mark.parametrize("raw", ["1.190,00", "1,190.00", "abc", "", True, "12e3"])
def test_parse_amount_rejects(raw):
    with pytest.raises(ValueError):
        parse_amount(raw)


@pytest.mark.parametrize("raw", ["1.190", "10.000", "2.380", "1,190", "0.125"])
def test_amount_thousands_dot_rejected(raw):
    with pytest.raises(ValueError, match="kein Tausenderpunkt"):
        parse_amount(raw)


def test_amount_thousands_dot_is_input_error():
    data = json.loads((FIXTURES / "eingabe_beispiel.json").read_text(encoding="utf-8"))
    data["buchungen"][0]["umsatz"] = "1.190"
    with pytest.raises(InputError) as exc:
        load_json(json.dumps(data))
    assert [(f.code, f.field) for f in exc.value.findings] == [("EINGABE_UNGUELTIG", "buchungen[0].umsatz")]


def test_kopf_example_matches_json_example():
    kopf = json.loads((FIXTURES / "kopf_beispiel.json").read_text(encoding="utf-8"))
    full = json.loads((FIXTURES / "eingabe_beispiel.json").read_text(encoding="utf-8"))
    assert kopf == full["kopf"]


@pytest.mark.parametrize("raw", ["2026-09-02", "02.09.2026", "20260902", date(2026, 9, 2)])
def test_parse_date(raw):
    assert parse_date(raw) == date(2026, 9, 2)


def test_parse_date_rejects():
    with pytest.raises(ValueError):
        parse_date("09/02/2026")


def test_example_json_builds_valid_file():
    header, bookings = load_json((FIXTURES / "eingabe_beispiel.json").read_text(encoding="utf-8"))
    assert header is not None and len(bookings) == 3
    r = read_extf(build_extf(header, bookings), "EXTF_x.csv")
    assert r.valid and r.findings == []


def test_example_csv_builds_valid_file():
    bookings = load_csv((FIXTURES / "eingabe_beispiel.csv").read_text(encoding="utf-8-sig"))
    header, _ = load_json((FIXTURES / "eingabe_beispiel.json").read_text(encoding="utf-8"))
    assert len(bookings) == 3
    assert bookings[1].text == "Bürobedarf Größe A4"
    assert build_extf(header, bookings)


def test_csv_with_comma_delimiter_and_bom():
    text = "\ufeffbelegdatum,umsatz,soll_haben,konto,gegenkonto\n2026-09-02,\"1190,00\",S,10000,8400\n"
    b = load_csv(text)
    assert b[0].amount == Decimal("1190.00")


def test_missing_and_unknown_keys_are_reported_together():
    with pytest.raises(InputError) as exc:
        load_json(json.dumps({"buchungen": [{"umsatz": 1, "foo": 2}, {"umsatz": "x", "soll_haben": "S", "konto": 1,
                                                                    "gegenkonto": 2, "belegdatum": "2026-09-01"}]}))
    fields = [f.field for f in exc.value.findings]
    assert "buchungen[0]" in fields
    assert "buchungen[0].soll_haben" in fields
    assert "buchungen[1].umsatz" in fields
    assert all(f.code == "EINGABE_UNGUELTIG" for f in exc.value.findings)


def test_bad_json():
    with pytest.raises(InputError):
        load_json("{")
    with pytest.raises(InputError):
        load_json('{"kopf": {}}')


def test_header_errors():
    data = json.loads((FIXTURES / "eingabe_beispiel.json").read_text(encoding="utf-8"))
    data["kopf"]["beraternummer"] = "abc"
    data["kopf"]["datum_von"] = "Sept"
    with pytest.raises(InputError) as exc:
        load_json(json.dumps(data))
    assert {f.field for f in exc.value.findings} == {"kopf.beraternummer", "kopf.datum_von"}
