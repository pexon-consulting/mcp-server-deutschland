"""Tests für daten/server.yaml und scripts/liste_bauen.py."""

from __future__ import annotations

import copy
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKRIPT = ROOT / "scripts" / "liste_bauen.py"

_spec = importlib.util.spec_from_file_location("liste_bauen", SKRIPT)
lb = importlib.util.module_from_spec(_spec)
sys.modules["liste_bauen"] = lb
_spec.loader.exec_module(lb)

GEDANKENSTRICHE = ("\u2014", "\u2013")
FIRMA = "pe" + "xon"
ERECHNUNG_URL = "https://github.com/" + FIRMA + "-consulting/e-rechnung"

# Wortbestandteile, in denen ae/oe/ue korrekt sind (deutsch oder englisch).
UMLAUT_AUSNAHMEN = (
    "quell", "query", "queue", "steuer", "bauen", "manuell", "neu", "true", "zuerst",
    "confluence", "aktuell", "individuell", "eventuell", "virtuell", "issue", "value",
    "blue", "dauer", "feuer", "treue", "sequenz", "duell", "request", "continue",
)


@pytest.fixture(scope="module")
def eintraege() -> list[dict]:
    return lb.lade()


def _texte(eintrag: dict) -> list[str]:
    return [str(v) for v in eintrag.values() if v is not None]


def test_schema_valide(eintraege):
    assert lb.validiere(eintraege) == []


@pytest.mark.parametrize(
    "patch, erwartet",
    [
        ({"typ": "inoffiziell"}, "typ muss"),
        ({"transport": "sse"}, "transport muss"),
        ({"zugriff": "schreiben"}, "zugriff muss"),
        ({"kategorie": "Sonstiges"}, "unbekannte Kategorie"),
        ({"geprueft_am": "2026-13-01"}, "geprueft_am"),
        ({"zuletzt_aktiv": "gestern"}, "zuletzt_aktiv"),
        ({"sterne": "viele"}, "sterne"),
        ({"archiviert": "ja"}, "archiviert"),
        ({"lizenz": "MIT License"}, "lizenz"),
        ({"url": "http://example.com"}, "url ist keine https-URL"),
        ({"hinweis": ""}, "Pflichtfeld 'hinweis'"),
        ({"farbe": "blau"}, "unbekanntes Feld"),
        ({"protokoll": "neu"}, "protokoll"),
    ],
)
def test_schema_erkennt_fehler(eintraege, patch, erwartet):
    kaputt = copy.deepcopy(eintraege)
    kaputt[0].update(patch)
    fehler = lb.validiere(kaputt)
    assert any(erwartet in f for f in fehler), fehler


def test_keine_doppelten_urls(eintraege):
    urls = [e["url"].rstrip("/").lower() for e in eintraege]
    doppelt = {u for u in urls if urls.count(u) > 1}
    assert not doppelt
    kaputt = copy.deepcopy(eintraege) + [copy.deepcopy(eintraege[0])]
    assert any("url doppelt" in f for f in lb.validiere(kaputt))


def test_jede_kategorie_mindestens_zwei(eintraege):
    for kat in lb.KATEGORIEN:
        anzahl = sum(1 for e in eintraege if e["kategorie"] == kat)
        assert anzahl >= 2 or lb.KATEGORIE_AUSNAHMEN.get(kat, "").strip(), kat


def test_erzeugte_dateien_aktuell():
    lauf = subprocess.run(
        [sys.executable, str(SKRIPT), "--check"], capture_output=True, text=True, cwd=ROOT
    )
    assert lauf.returncode == 0, lauf.stderr


def test_check_meldet_veraltete_liste(tmp_path, monkeypatch):
    monkeypatch.setattr(lb, "LISTE", tmp_path / "liste.md")
    monkeypatch.setattr(lb, "README", tmp_path / "README.md")
    (tmp_path / "liste.md").write_text("alt\n", encoding="utf-8")
    assert lb.main(["--check"]) == 1


def test_readme_marker_werden_ersetzt(eintraege):
    alt = "# Titel\n\nVorher\n<!-- liste:start -->\nalt\n<!-- liste:end -->\nNachher\n"
    neu = lb.readme_neu(alt, lb.baue_readme_block(eintraege))
    assert neu.startswith("# Titel\n\nVorher\n<!-- liste:start -->")
    assert neu.endswith("<!-- liste:end -->\nNachher\n")
    assert "docs/liste.md" in neu
    assert lb.readme_neu("ohne Marker", "x") is None


def _textdateien() -> list[Path]:
    dateien = [lb.DATEN, lb.LISTE, SKRIPT, Path(__file__)]
    if lb.README.exists():
        dateien.append(lb.README)
    return dateien


def test_keine_gedankenstriche():
    for pfad in _textdateien():
        text = pfad.read_text(encoding="utf-8")
        for zeichen in GEDANKENSTRICHE:
            assert zeichen not in text, f"{pfad.name} enthält U+{ord(zeichen):04X}"


def test_keine_umlaut_ersatzschreibung_in_hinweisen(eintraege):
    texte = [e["hinweis"] for e in eintraege]
    texte += [s for abschnitte in lb.KATEGORIE_TEXTE.values() for s in abschnitte]
    texte += lb.CHECKLISTE
    funde = []
    for text in texte:
        for wort in re.findall(r"[A-Za-zÄÖÜäöüß0-9_./@-]+", text):
            if any(z in wort for z in "/_.@0123456789") and not wort.endswith("."):
                continue
            klein = wort.lower().rstrip(".")
            if not re.search(r"ae|oe|ue", klein):
                continue
            if any(a in klein for a in UMLAUT_AUSNAHMEN):
                continue
            funde.append(wort)
    assert not funde, funde


def test_offizielle_eintraege_haben_herstellerquelle(eintraege):
    for e in eintraege:
        if e["typ"] == "offiziell":
            assert e["herkunft"] in lb.HERSTELLER_QUELLEN, e["name"]
            assert lb._hersteller_quelle_ok(e), f"{e['name']}: {e['quelle']}"


def test_herstellerquelle_wird_erzwungen(eintraege):
    kaputt = copy.deepcopy(eintraege)
    offiziell = next(e for e in kaputt if e["typ"] == "offiziell")
    offiziell["quelle"] = "https://example.com/blog"
    assert any("ohne Quelle beim Hersteller" in f for f in lb.validiere(kaputt))


def test_firmenname_nur_im_e_rechnung_eintrag(eintraege):
    for e in eintraege:
        if e["url"] == ERECHNUNG_URL:
            continue
        for text in _texte(e):
            assert FIRMA not in text.lower(), e["name"]
    for pfad in (lb.LISTE, SKRIPT):
        for zeile in pfad.read_text(encoding="utf-8").splitlines():
            if FIRMA in zeile.lower():
                assert ERECHNUNG_URL in zeile, f"{pfad.name}: {zeile[:80]}"
    if lb.README.exists():
        block = lb.baue_readme_block(eintraege)
        for zeile in block.splitlines():
            if FIRMA in zeile.lower():
                assert ERECHNUNG_URL in zeile


def test_veraltete_und_archivierte_repos_sind_vermerkt(eintraege):
    for e in eintraege:
        text = lb.hinweis_text(e)
        if e.get("archiviert"):
            assert text.startswith("Archiviert."), e["name"]
        if lb.ist_veraltet(e):
            assert "Letzte Änderung im Repository" in text, e["name"]


def test_sterne_nur_mit_repo(eintraege):
    for e in eintraege:
        if e.get("sterne") is not None:
            assert e.get("repo"), e["name"]


def test_hinweis_abschnitte_enthalten():
    text = lb.LISTE.read_text(encoding="utf-8")
    assert lb.HINWEIS_ALLGEMEIN in text
    assert lb.HINWEIS_STEUER in text
    assert "## So prüfen Sie einen MCP-Server vor dem Einsatz" in text
    assert "## Eintrag vorschlagen" in text


def test_tabellen_sortierung(eintraege):
    for kat in lb.KATEGORIEN:
        teil = lb.sortiert([e for e in eintraege if e["kategorie"] == kat])
        typen = [e["typ"] == "offiziell" for e in teil]
        assert typen == sorted(typen, reverse=True), kat
        rest = [e.get("sterne") or -1 for e in teil if e["typ"] != "offiziell"]
        assert rest == sorted(rest, reverse=True), kat
