"""Simple input format (JSON or CSV) for header and bookings.

JSON:
    {"kopf": {...}, "buchungen": [{...}, ...]}
CSV (UTF-8, delimiter ; or , or tab, first line = keys):
    `belegdatum;umsatz;soll_haben;konto;gegenkonto;bu_schluessel;belegfeld1;buchungstext`

Keys are documented in README.md (section "Eingabeformat").
"""

from __future__ import annotations

import csv
import io
import json
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from .model import Booking, ExtfValidationError, Finding, Header
from .rules import make

HEADER_KEYS = {
    "beraternummer", "mandantennummer", "wj_beginn", "sachkontenlaenge", "datum_von", "datum_bis",
    "bezeichnung", "diktatkuerzel", "festschreibung", "wkz", "sachkontenrahmen", "herkunft", "exportiert_von",
}
BOOKING_KEYS = {
    "umsatz", "soll_haben", "konto", "gegenkonto", "belegdatum", "bu_schluessel", "belegfeld1",
    "belegfeld2", "buchungstext", "kost1", "kost2", "festschreibung", "wkz",
}
REQUIRED_HEADER = ("beraternummer", "mandantennummer", "wj_beginn", "sachkontenlaenge", "datum_von", "datum_bis")
REQUIRED_BOOKING = ("umsatz", "soll_haben", "konto", "gegenkonto", "belegdatum")

_AMOUNT_RE = re.compile(r"^[+-]?\d+([.,]\d{1,2})?$")


class InputError(ExtfValidationError):
    pass


def _err(message: str, where: str | None = None, value: Any = None) -> Finding:
    return make("EINGABE_UNGUELTIG", message, field=where, value=None if value is None else str(value))


def parse_amount(value: Any) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("Wahrheitswert statt Betrag")
    if isinstance(value, (int, Decimal)):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(repr(value))
    s = str(value).strip().replace(" ", "")
    if not _AMOUNT_RE.match(s):
        raise ValueError(
            "Betrag erwartet, z. B. 1190,00 oder 1190.00; höchstens 2 Nachkommastellen, "
            "kein Tausenderpunkt (1.190 wäre mehrdeutig)"
        )
    try:
        return Decimal(s.replace(",", "."))
    except InvalidOperation as exc:  # pragma: no cover - regex guards this
        raise ValueError("Betrag nicht lesbar") from exc


def parse_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y%m%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError("Datum erwartet als JJJJ-MM-TT oder TT.MM.JJJJ")


def parse_bool(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in ("1", "true", "ja", "wahr"):
        return True
    if s in ("0", "false", "nein", "falsch"):
        return False
    raise ValueError("0/1 oder true/false erwartet")


def _str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value).strip()


def header_from_dict(d: dict[str, Any]) -> Header:
    errors: list[Finding] = []
    unknown = sorted(set(d) - HEADER_KEYS)
    if unknown:
        errors.append(_err(f"Unbekannte Felder im Kopf: {', '.join(unknown)}.", "kopf"))
    for key in REQUIRED_HEADER:
        if d.get(key) in (None, ""):
            errors.append(_err(f"Pflichtfeld fehlt: {key}.", f"kopf.{key}"))
    if errors:
        raise InputError(errors)
    vals: dict[str, Any] = {}
    for key, conv in (("beraternummer", int), ("mandantennummer", int), ("sachkontenlaenge", int)):
        try:
            vals[key] = conv(_str(d[key]))
        except ValueError:
            errors.append(_err("Ganze Zahl erwartet.", f"kopf.{key}", d[key]))
    for key in ("wj_beginn", "datum_von", "datum_bis"):
        try:
            vals[key] = parse_date(d[key])
        except ValueError as exc:
            errors.append(_err(str(exc) + ".", f"kopf.{key}", d[key]))
    try:
        locking = parse_bool(d.get("festschreibung"))
    except ValueError as exc:
        errors.append(_err(str(exc) + ".", "kopf.festschreibung", d.get("festschreibung")))
        locking = None
    if errors:
        raise InputError(errors)
    return Header(
        consultant_number=vals["beraternummer"],
        client_number=vals["mandantennummer"],
        fiscal_year_start=vals["wj_beginn"],
        account_length=vals["sachkontenlaenge"],
        date_from=vals["datum_von"],
        date_to=vals["datum_bis"],
        description=_str(d.get("bezeichnung")),
        dictation_code=_str(d.get("diktatkuerzel")),
        locking=bool(locking),
        currency=_str(d.get("wkz")) or "EUR",
        chart_of_accounts=_str(d.get("sachkontenrahmen")),
        origin=_str(d.get("herkunft")),
        exported_by=_str(d.get("exportiert_von")),
    )


def booking_from_dict(d: dict[str, Any], index: int) -> Booking:
    """`index` is 0-based; messages name the booking as number index+1."""
    where = f"buchungen[{index}]"
    errors: list[Finding] = []
    unknown = sorted(set(d) - BOOKING_KEYS)
    if unknown:
        errors.append(_err(f"Unbekannte Felder: {', '.join(unknown)}.", where))
    for key in REQUIRED_BOOKING:
        if d.get(key) in (None, ""):
            errors.append(_err(f"Pflichtfeld fehlt: {key}.", f"{where}.{key}"))
    if errors:
        raise InputError(errors)
    amount = belegdatum = locking = None
    try:
        amount = parse_amount(d["umsatz"])
    except ValueError as exc:
        errors.append(_err(str(exc) + ".", f"{where}.umsatz", d["umsatz"]))
    try:
        belegdatum = parse_date(d["belegdatum"])
    except ValueError as exc:
        errors.append(_err(str(exc) + ".", f"{where}.belegdatum", d["belegdatum"]))
    try:
        locking = parse_bool(d.get("festschreibung"))
    except ValueError as exc:
        errors.append(_err(str(exc) + ".", f"{where}.festschreibung", d.get("festschreibung")))
    if errors:
        raise InputError(errors)
    return Booking(
        amount=amount,
        debit_credit=_str(d["soll_haben"]).upper(),
        account=_str(d["konto"]),
        contra_account=_str(d["gegenkonto"]),
        document_date=belegdatum,
        bu_key=_str(d.get("bu_schluessel")),
        document_field_1=_str(d.get("belegfeld1")),
        document_field_2=_str(d.get("belegfeld2")),
        text=_str(d.get("buchungstext")),
        cost_center_1=_str(d.get("kost1")),
        cost_center_2=_str(d.get("kost2")),
        locking=locking,
        currency=_str(d.get("wkz")),
    )


def bookings_from_dicts(items: list[dict[str, Any]]) -> list[Booking]:
    out: list[Booking] = []
    errors: list[Finding] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(_err("Objekt erwartet.", f"buchungen[{i}]"))
            continue
        try:
            out.append(booking_from_dict(item, i))
        except InputError as exc:
            errors.extend(exc.findings)
    if errors:
        raise InputError(errors)
    return out


def load_json(text: str) -> tuple[Header | None, list[Booking]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError([_err(f"Kein gültiges JSON (Zeile {exc.lineno}, Spalte {exc.colno}).")]) from exc
    if isinstance(data, list):
        return None, bookings_from_dicts(data)
    if not isinstance(data, dict) or "buchungen" not in data:
        raise InputError([_err("Erwartet wird ein Objekt mit 'buchungen' (und optional 'kopf') oder eine Liste von Buchungen.")])
    header = header_from_dict(data["kopf"]) if data.get("kopf") else None
    items = data["buchungen"]
    if not isinstance(items, list):
        raise InputError([_err("'buchungen' muss eine Liste sein.", "buchungen")])
    return header, bookings_from_dicts(items)


def load_csv(text: str) -> list[Booking]:
    text = text.lstrip("\ufeff")
    first = text.splitlines()[0] if text else ""
    delimiter = max((";", ",", "\t"), key=first.count)
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    rows = []
    for row in reader:
        if not any((v or "").strip() for v in row.values()):
            continue
        rows.append({k.strip().lower(): v for k, v in row.items() if k is not None and (v or "").strip() != ""})
    return bookings_from_dicts(rows)
