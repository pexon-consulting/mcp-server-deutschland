from __future__ import annotations

from conftest import build_raw, codes, raw_row

from extf_buchungsstapel_mcp.reader import decode, read_extf, row_to_booking_dict, split_fields


def test_split_fields_quotes_and_semicolons():
    values, quoted, ok = split_fields('1,00;"a;b";"x ""y""";;""')
    assert ok
    assert values == ["1,00", "a;b", 'x "y"', "", ""]
    assert quoted == [False, True, True, False, True]


def test_split_fields_unterminated():
    _, _, ok = split_fields('1;"abc')
    assert not ok


def test_cp1252_is_default():
    text, enc, findings = decode("Größe 5 €".encode("cp1252"))
    assert (text, enc, findings) == ("Größe 5 €", "windows-1252", [])


def test_ascii_is_reported_as_windows_1252():
    assert decode(b"abc")[1] == "windows-1252"


def test_utf8_with_bom_is_accepted_with_note():
    data = b"\xef\xbb\xbf" + build_raw(rows=[raw_row({14: '"Größe"'})], encoding="utf-8")
    r = read_extf(data, "EXTF_x.csv")
    assert r.encoding == "utf-8-sig"
    assert codes(r) == {"UNICODE_MIT_BOM"}
    assert r.rows[0].get(14) == "Größe"


def test_utf16_with_bom():
    data = build_raw(encoding="utf-16")
    r = read_extf(data, "EXTF_x.csv")
    assert codes(r) == {"UNICODE_MIT_BOM"}
    assert len(r.rows) == 1


def test_utf8_without_bom_warns():
    r = read_extf(build_raw(rows=[raw_row({14: '"Größe"'})], encoding="utf-8"), "EXTF_x.csv")
    assert "UTF8_OHNE_BOM" in codes(r)
    assert r.valid


def test_undefined_cp1252_byte_is_error():
    data = build_raw().replace(b"Muster", b"Must\x81r")
    assert "ZEICHENSATZ_UNGUELTIG" in codes(read_extf(data, "EXTF_x.csv"))


def test_lf_line_endings_are_an_error():
    r = read_extf(build_raw(newline="\n"), "EXTF_x.csv")
    assert "ZEILENENDE_KEIN_CRLF" in codes(r)
    assert sum(f.code == "ZEILENENDE_KEIN_CRLF" for f in r.findings) == 1
    assert len(r.rows) == 1


def test_missing_final_crlf_is_warning():
    r = read_extf(build_raw()[:-2], "EXTF_x.csv")
    assert codes(r) == {"LETZTE_ZEILE_OHNE_CRLF"}


def test_empty_trailing_lines_are_ignored():
    r = read_extf(build_raw() + b"\r\n", "EXTF_x.csv")
    assert r.findings == []


def test_header_parsed():
    r = read_extf(build_raw(), "EXTF_x.csv")
    assert r.header is not None
    assert r.header.consultant_number == 1001
    assert r.header.client_number == 1
    assert r.header.account_length == 4
    assert r.header.locking is False
    assert r.header.to_dict()["datum_von"] == "2026-09-01"


def test_booking_dict():
    r = read_extf(build_raw(rows=[raw_row({9: '"9"', 37: '"100"'})]), "EXTF_x.csv")
    d = row_to_booking_dict(r.rows[0], r.header)
    assert d == {
        "zeile": 3, "umsatz": "1190,00", "soll_haben": "S", "wkz": "", "konto": "10000",
        "gegenkonto": "8400", "bu_schluessel": "9", "belegdatum": "0209",
        "belegdatum_iso": "2026-09-02", "belegfeld1": "RE2026-0815", "belegfeld2": "",
        "buchungstext": "Muster GmbH Beratung", "kost1": "100", "kost2": "", "festschreibung": "0",
    }


def test_garbage_does_not_crash():
    for data in (b"\x00\x01\x02", b";;;;\r\n;;;\r\n", b'"\r\n', b"EXTF\r\n" * 3, bytes(range(256))):
        r = read_extf(data)
        assert not r.valid
