"""Explain booking fields, header fields and check codes."""

from __future__ import annotations

import re

from . import columns as C
from .codes import CODES


def _norm(s: str) -> str:
    s = s.casefold().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", "", s)


def _booking(n: int) -> dict:
    info = C.booking_field_info(n)
    return {
        "art": "spalte",
        "nummer": n,
        "name": info.name,
        "typ": info.kind,
        "beschreibung": info.description,
        "format": info.format,
        "von_diesem_server_genutzt": info.used,
        "quelle": C.FORMAT_DESCRIPTION_URL,
    }


def _header(n: int) -> dict:
    info = C.HEADER_FIELDS[n - 1]
    return {
        "art": "header",
        "nummer": n,
        "name": info.name,
        "typ": "Text" if n in C.HEADER_TEXT_FIELDS else "Zahl",
        "beschreibung": info.description,
        "format": info.format,
        "pflicht": info.required,
        "quelle": C.HEADER_DESCRIPTION_URL,
    }


def _code(code: str) -> dict:
    info = CODES[code]
    return {
        "art": "pruefcode",
        "name": info.code,
        "schwere": info.severity,
        "beschreibung": info.explanation,
        "quelle": info.source,
    }


def explain(term: str, limit: int = 10) -> list[dict]:
    """Look up a term: check code, 'header 14', field number, or (part of) a name."""
    t = term.strip()
    if not t:
        return []
    up = t.upper()
    if up in CODES:
        return [_code(up)]
    m = re.fullmatch(r"(?i)\s*(header|kopf)\s*(?:feld\s*)?(\d{1,2})\s*", t)
    if m:
        n = int(m.group(2))
        return [_header(n)] if 1 <= n <= C.HEADER_FIELD_COUNT else []
    m = re.fullmatch(r"(?i)\s*(?:feld|spalte|nr\.?)?\s*(\d{1,3})\s*", t)
    if m:
        n = int(m.group(1))
        return [_booking(n)] if 1 <= n <= len(C.BOOKING_COLUMNS_V13) else []

    key = _norm(t)
    results: list[dict] = []
    exact: list[dict] = []
    for n, name in enumerate(C.BOOKING_COLUMNS_V13, start=1):
        nn = _norm(name)
        if nn == key:
            exact.append(_booking(n))
        elif key and key in nn:
            results.append(_booking(n))
    for info in C.HEADER_FIELDS:
        nn = _norm(info.name)
        if nn == key:
            exact.append(_header(info.number))
        elif key and key in nn and info.required != "Leerfeld":
            results.append(_header(info.number))
    for code in CODES:
        if key and key in _norm(code):
            results.append(_code(code))
    combined = exact + results
    return combined[:limit]
