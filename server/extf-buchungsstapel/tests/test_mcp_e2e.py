"""End-to-end: start the real server over stdio and talk to it with the official MCP client."""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import sys
from pathlib import Path

import pytest
from conftest import FIXTURES

from mcp import Client
from mcp.client.stdio import StdioServerParameters

EXAMPLE = json.loads((FIXTURES / "eingabe_beispiel.json").read_text(encoding="utf-8"))


def server_params(folder: Path) -> StdioServerParameters:
    script = Path(sys.executable).parent / ("extf-buchungsstapel-mcp.exe" if os.name == "nt" else "extf-buchungsstapel-mcp")
    if script.exists():
        command, args = str(script), []
    else:  # pragma: no cover - editable installs without scripts
        command, args = sys.executable, ["-c", "from extf_buchungsstapel_mcp.server import main; main()"]
    env = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "SYSTEMROOT", "TMPDIR", "LANG")}
    env["EXTF_ORDNER"] = str(folder)
    return StdioServerParameters(command=command, args=args, env=env)


def run(coro):
    return asyncio.run(coro)


def structured(result) -> dict:
    assert not result.is_error, result.content
    data = result.structured_content
    assert isinstance(data, dict)
    # the text block mirrors the structured content
    assert json.loads(result.content[0].text) == data
    return data


async def session(folder: Path, fn, **client_kw):
    async with Client(server_params(folder), **client_kw) as c:
        return await fn(c)


@pytest.fixture
def folder(tmp_path):
    d = tmp_path / "ordner"
    d.mkdir()
    return d


def test_tools_list_schemas_and_annotations(folder):
    async def go(c):
        return c.server_info, (await c.list_tools()).tools

    info, tools = run(session(folder, go))
    assert info.name == "extf-buchungsstapel"
    by_name = {t.name: t for t in tools}
    assert set(by_name) == {"buchungsstapel_erstellen", "extf_pruefen", "extf_lesen", "felder_erklaeren"}
    for t in tools:
        assert t.description and t.title
        assert t.input_schema["type"] == "object"
        assert t.output_schema and t.output_schema["type"] == "object"
        assert t.annotations.open_world_hint is False
        assert t.annotations.destructive_hint is False
    w = by_name["buchungsstapel_erstellen"].annotations
    assert (w.read_only_hint, w.idempotent_hint) == (False, False)
    for name in ("extf_pruefen", "extf_lesen", "felder_erklaeren"):
        a = by_name[name].annotations
        assert (a.read_only_hint, a.idempotent_hint) == (True, True)
    schema = by_name["buchungsstapel_erstellen"].input_schema
    assert set(schema["required"]) == {"kopf", "buchungen"}
    assert "geschrieben" in by_name["buchungsstapel_erstellen"].output_schema["properties"]


def test_full_workflow(folder):
    async def go(c):
        created = structured(await c.call_tool("buchungsstapel_erstellen", {**EXAMPLE, "dateiname": "EXTF_test.csv"}))
        again = await c.call_tool("buchungsstapel_erstellen", {**EXAMPLE, "dateiname": "EXTF_test.csv"})
        checked = structured(await c.call_tool("extf_pruefen", {"datei": "EXTF_test.csv"}))
        read = structured(await c.call_tool("extf_lesen", {"datei": "EXTF_test.csv", "limit": 2}))
        page2 = structured(await c.call_tool("extf_lesen", {"datei": "EXTF_test.csv", "limit": 2, "offset": 2}))
        explained = structured(await c.call_tool("felder_erklaeren", {"begriff": "Belegfeld 1"}))
        return created, again, checked, read, page2, explained

    created, again, checked, read, page2, explained = run(session(folder, go))
    assert created["geschrieben"] is True
    assert created["datei"] == "EXTF_test.csv"
    assert created["buchungen"] == 3
    assert created["fehler"] == 0
    assert created["kopfzeile"].startswith('"EXTF";700;21;"Buchungsstapel";13;')
    data = (folder / "EXTF_test.csv").read_bytes()
    assert len(data) == created["bytes"]
    assert "Bürobedarf".encode("cp1252") in data

    assert again.is_error
    assert "existiert bereits" in again.content[0].text
    assert (folder / "EXTF_test.csv").read_bytes() == data

    assert checked["gueltig"] is True and checked["fehler"] == 0 and checked["buchungen"] == 3
    assert checked["kopf"]["beraternummer"] == 1001
    assert checked["zeichensatz"] == "windows-1252"

    assert read["buchungen_gesamt"] == 3 and read["weitere"] is True and len(read["buchungen"]) == 2
    assert read["buchungen"][1]["buchungstext"] == "Bürobedarf Größe A4"
    assert read["buchungen"][1]["umsatz"] == "59,50"
    assert page2["weitere"] is False and page2["buchungen"][0]["konto"] == "70000"

    assert explained["treffer"][0]["nummer"] == 11


def test_invalid_booking_writes_nothing(folder):
    bad = json.loads(json.dumps(EXAMPLE))
    bad["buchungen"][0]["belegfeld1"] = "RE 2026.1"
    bad["buchungen"][1]["belegdatum"] = "2026-10-01"

    async def go(c):
        return structured(await c.call_tool("buchungsstapel_erstellen", bad))

    res = run(session(folder, go))
    assert res["geschrieben"] is False
    assert {b["code"] for b in res["befunde"]} >= {"BELEGFELD1_ZEICHEN", "BELEGDATUM_AUSSERHALB_ZEITRAUM"}
    assert list(folder.iterdir()) == []


def test_review_cases_write_nothing(folder):
    thousands = json.loads(json.dumps(EXAMPLE))
    thousands["buchungen"][0]["umsatz"] = "1.190"
    locked = json.loads(json.dumps(EXAMPLE))
    locked["buchungen"][1]["festschreibung"] = True
    formula = json.loads(json.dumps(EXAMPLE))
    formula["buchungen"][2]["buchungstext"] = '=HYPERLINK("http://beispiel.example/?x";"Klick")'

    async def go(c):
        return [structured(await c.call_tool("buchungsstapel_erstellen", data)) for data in (thousands, locked, formula)]

    res = run(session(folder, go))
    assert all(r["geschrieben"] is False for r in res)
    assert [{b["code"] for b in r["befunde"]} for r in res] == [
        {"EINGABE_UNGUELTIG"}, {"FESTSCHREIBUNG_EINZELN"}, {"FORMELZEICHEN_BEIM_SCHREIBEN"},
    ]
    assert "kein Tausenderpunkt" in res[0]["befunde"][0]["meldung"]
    assert list(folder.iterdir()) == []


def test_errors_are_tool_errors(folder, tmp_path):
    (tmp_path / "geheim.csv").write_text("x")

    async def go(c):
        return [
            await c.call_tool("extf_pruefen", {"datei": "../geheim.csv"}),
            await c.call_tool("extf_lesen", {"datei": "fehlt.csv"}),
            await c.call_tool("buchungsstapel_erstellen", {**EXAMPLE, "dateiname": "../x.csv"}),
            await c.call_tool("felder_erklaeren", {"begriff": "gibtsnicht-xyz"}),
            await c.call_tool("extf_lesen", {"datei": "x.csv", "limit": 0}),
        ]

    results = run(session(folder, go))
    assert all(r.is_error for r in results)
    assert "Nur ein Dateiname" in results[0].content[0].text
    assert "gibt es im Arbeitsordner nicht" in results[1].content[0].text
    assert list(folder.iterdir()) == []


def test_existing_foreign_file_is_checked(folder):
    shutil.copy(FIXTURES / "EXTF_golden_datev_kopf.csv", folder / "EXTF_import.csv")

    async def go(c):
        return structured(await c.call_tool("extf_pruefen", {"datei": "EXTF_import.csv", "max_befunde": 1}))

    res = run(session(folder, go))
    assert res["gueltig"] is True
    assert res["kopf"]["beraternummer"] == 29098


def test_legacy_initialize_handshake(folder):
    async def go(c):
        return c.protocol_version, [t.name for t in (await c.list_tools()).tools]

    version, names = run(session(folder, go, mode="legacy"))
    assert version
    assert "extf_pruefen" in names


def test_server_without_folder_reports_tool_error(tmp_path):
    params = server_params(tmp_path)
    params.env.pop("EXTF_ORDNER")

    async def go():
        async with Client(params) as c:
            return await c.call_tool("extf_pruefen", {"datei": "x.csv"})

    res = run(go())
    assert res.is_error
    assert "EXTF_ORDNER" in res.content[0].text
