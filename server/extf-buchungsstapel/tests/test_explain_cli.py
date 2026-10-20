from __future__ import annotations

import json

import pytest
from conftest import FIXTURES, build_raw, raw_row

from extf_buchungsstapel_mcp import columns as C
from extf_buchungsstapel_mcp.cli import main
from extf_buchungsstapel_mcp.codes import CODES
from extf_buchungsstapel_mcp.explain import explain


def test_explain_by_number():
    hit = explain("11")[0]
    assert hit["art"] == "spalte" and hit["nummer"] == 11 and hit["name"] == "Belegfeld 1"


def test_explain_by_name_and_code_and_header():
    assert explain("belegfeld 1")[0]["nummer"] == 11
    assert explain("KONTO_ZU_LANG")[0]["art"] == "pruefcode"
    hit = explain("Header 14")[0]
    assert hit["art"] == "header" and hit["nummer"] == 14
    assert explain("Abw. Skontokonto")[0]["nummer"] == 125


def test_explain_unknown():
    assert explain("gibtsnicht-xyz") == []


def test_all_columns_and_codes_are_explainable():
    for n in range(1, 126):
        assert explain(str(n))[0]["name"] == C.BOOKING_COLUMNS_V13[n - 1]
    for code in CODES:
        assert explain(code)[0]["name"] == code


def test_columns_v13_constants():
    assert len(C.BOOKING_COLUMNS_V13) == 125
    assert len(set(C.BOOKING_COLUMNS_V13)) == 125
    assert C.BOOKING_COLUMNS_V13[0] == "Umsatz (ohne Soll/Haben-Kz)"
    assert C.BOOKING_COLUMNS_V13[124] == "Abw. Skontokonto"
    assert len(C.HEADER_FIELDS) == 31
    assert all("\u2013" not in c and "\u2014" not in c for c in C.BOOKING_COLUMNS_V13)


def test_cli_pruefen_ok(tmp_path, capsys):
    f = tmp_path / "EXTF_ok.csv"
    f.write_bytes(build_raw())
    assert main(["prüfen", str(f)]) == 0
    assert "0 Fehler" in capsys.readouterr().out


def test_cli_pruefen_error_json(tmp_path, capsys):
    f = tmp_path / "EXTF_bad.csv"
    f.write_bytes(build_raw(rows=[raw_row({11: '"RE 1"'})]))
    assert main(["pruefen", str(f), "--json"]) == 1
    out = json.loads(capsys.readouterr().out)
    assert out["gueltig"] is False
    assert out["befunde"][0]["code"] == "BELEGFELD1_ZEICHEN"
    assert out["befunde"][0]["zeile"] == 3


def test_cli_lesen(capsys):
    assert main(["lesen", str(FIXTURES / "EXTF_golden_umlaute.csv"), "--json", "--limit", "1", "--offset", "1"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert [b["konto"] for b in out["buchungen"]] == ["70000"]


def test_cli_erstellen_json_and_no_overwrite(tmp_path, capsys):
    out = tmp_path / "EXTF_neu.csv"
    assert main(["erstellen", str(FIXTURES / "eingabe_beispiel.json"), "-o", str(out)]) == 0
    first = out.read_bytes()
    assert first.startswith(b'"EXTF";700;21;"Buchungsstapel";13;')
    assert main(["erstellen", str(FIXTURES / "eingabe_beispiel.json"), "-o", str(out)]) == 2
    assert out.read_bytes() == first
    assert "nicht überschrieben" in capsys.readouterr().err


def test_cli_erstellen_csv_needs_header(tmp_path):
    out = tmp_path / "EXTF_csv.csv"
    assert main(["erstellen", str(FIXTURES / "eingabe_beispiel.csv"), "-o", str(out)]) == 2
    kopf = tmp_path / "kopf.json"
    kopf.write_text(json.dumps(json.loads((FIXTURES / "eingabe_beispiel.json").read_text(encoding="utf-8"))["kopf"]))
    assert main(["erstellen", str(FIXTURES / "eingabe_beispiel.csv"), "-o", str(out), "--kopf", str(kopf)]) == 0


def test_cli_erstellen_csv_with_kopf_example(tmp_path, capsys):
    out = tmp_path / "EXTF_Belege_2026-09_csv.csv"
    args = ["erstellen", str(FIXTURES / "eingabe_beispiel.csv"), "--kopf", str(FIXTURES / "kopf_beispiel.json"), "-o", str(out)]
    assert main(args) == 0
    assert "3 Buchungen" in capsys.readouterr().out
    assert main(["prüfen", str(out)]) == 0


def test_readme_lists_every_code_and_the_right_count():
    import pathlib
    import re

    readme = (pathlib.Path(__file__).parent.parent / "README.md").read_text(encoding="utf-8")
    listed = re.findall(r"^\| `([A-Z0-9_]+)` \| (fehler|warnung|hinweis) \|", readme, re.M)
    assert [c for c, _ in listed] == list(CODES)
    assert all(CODES[c].severity == s for c, s in listed)
    assert f"{len(CODES)} Prüfcodes" in readme


def test_cli_erstellen_invalid_writes_nothing(tmp_path, capsys):
    src = tmp_path / "in.json"
    data = json.loads((FIXTURES / "eingabe_beispiel.json").read_text(encoding="utf-8"))
    data["buchungen"][0]["belegdatum"] = "2026-10-05"
    src.write_text(json.dumps(data), encoding="utf-8")
    out = tmp_path / "EXTF_x.csv"
    assert main(["erstellen", str(src), "-o", str(out)]) == 1
    assert not out.exists()
    assert "BELEGDATUM_AUSSERHALB_ZEITRAUM" in capsys.readouterr().out


def test_cli_erklaeren(capsys):
    assert main(["erklären", "Belegfeld 1"]) == 0
    assert "Belegfeld 1" in capsys.readouterr().out
    assert main(["erklaeren", "gibtsnicht-xyz"]) == 1


def test_cli_missing_file(tmp_path, capsys):
    assert main(["pruefen", str(tmp_path / "fehlt.csv")]) == 2


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
