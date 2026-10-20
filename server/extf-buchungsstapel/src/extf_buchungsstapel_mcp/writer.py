"""Write Buchungsstapel files: Windows-1252, CRLF, header + captions + bookings."""

from __future__ import annotations

import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from . import columns as C
from .model import Booking, ExtfValidationError, Finding, Header, Row
from .reader import read_extf
from .rules import (
    CONTROL_RE,
    MAX_DOCUMENT_FIELD,
    MAX_DOCUMENT_FIELD_2_SAFE,
    check_header,
    check_row,
    fiscal_year_end,
    make,
)

ENCODING = "cp1252"
CRLF = "\r\n"
CENT = Decimal("0.01")
MAX_AMOUNT = Decimal("9999999999.99")


def _quote(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def format_line(values: list[str], quoted: list[bool]) -> str:
    return ";".join(_quote(v) if q else v for v, q in zip(values, quoted))


def format_timestamp(ts: datetime) -> str:
    return ts.strftime("%Y%m%d%H%M%S") + f"{ts.microsecond // 1000:03d}"


def format_amount(amount: Decimal) -> str:
    return format(amount.quantize(CENT), "f").replace(".", ",")


def header_fields(h: Header, created_at: datetime | None = None) -> tuple[list[str], list[bool]]:
    ts = created_at or h.created_at or datetime.now()
    v = [""] * C.HEADER_FIELD_COUNT
    v[0] = h.marker
    v[1] = str(C.HEADER_VERSION)
    v[2] = str(C.CATEGORY_BOOKING_BATCH)
    v[3] = C.CATEGORY_NAME
    v[4] = str(h.format_version)
    v[5] = format_timestamp(ts)
    v[7] = h.origin
    v[8] = h.exported_by
    v[10] = str(h.consultant_number)
    v[11] = str(h.client_number)
    v[12] = h.fiscal_year_start.strftime("%Y%m%d")
    v[13] = str(h.account_length)
    v[14] = h.date_from.strftime("%Y%m%d")
    v[15] = h.date_to.strftime("%Y%m%d")
    v[16] = h.description
    v[17] = h.dictation_code
    v[18] = str(h.booking_type)
    v[19] = str(h.accounting_purpose)
    v[20] = "1" if h.locking else "0"
    v[21] = h.currency
    v[26] = h.chart_of_accounts
    v[30] = h.application_info
    quoted = [(i + 1) in C.HEADER_TEXT_FIELDS for i in range(C.HEADER_FIELD_COUNT)]
    return v, quoted


def booking_fields(h: Header, b: Booking) -> tuple[list[str], list[bool]]:
    cols = C.COLUMNS_BY_VERSION[h.format_version]
    v = [""] * len(cols)
    v[C.F_AMOUNT - 1] = format_amount(b.amount)
    v[C.F_DEBIT_CREDIT - 1] = b.debit_credit
    v[C.F_CURRENCY - 1] = b.currency
    v[C.F_ACCOUNT - 1] = b.account
    v[C.F_CONTRA_ACCOUNT - 1] = b.contra_account
    v[C.F_BU_KEY - 1] = b.bu_key
    v[C.F_DOCUMENT_DATE - 1] = f"{b.document_date.day:02d}{b.document_date.month:02d}"
    v[C.F_DOCUMENT_FIELD_1 - 1] = b.document_field_1
    v[C.F_DOCUMENT_FIELD_2 - 1] = b.document_field_2
    v[C.F_TEXT - 1] = b.text
    v[C.F_COST_CENTER_1 - 1] = b.cost_center_1
    v[C.F_COST_CENTER_2 - 1] = b.cost_center_2
    locking = h.locking if b.locking is None else b.locking
    v[C.F_LOCKING - 1] = "1" if locking else "0"
    quoted = [(i + 1) in C.TEXT_FIELDS for i in range(len(cols))]
    return v, quoted


def _not_cp1252(value: str) -> list[str]:
    bad = []
    for ch in value:
        try:
            ch.encode(ENCODING)
        except UnicodeEncodeError:
            bad.append(ch)
    return bad


def check_header_model(h: Header) -> list[Finding]:
    out: list[Finding] = []
    if h.format_version != C.FORMAT_VERSION:
        out.append(make("HEADER_FORMATVERSION", "Dieser Writer erzeugt nur Formatversion 13.", line=1, value=str(h.format_version)))
    values, quoted = header_fields(h)
    _, found = check_header(values, quoted, line=1)
    out += found
    for n in (8, 9, 17, 31):
        val = values[n - 1]
        bad = _not_cp1252(val)
        if bad:
            out.append(make("ZEICHEN_NICHT_CP1252", f"Nicht darstellbar: {', '.join(repr(c) for c in bad[:5])}.", line=1, field=f"Header {n}", value=val))
        if CONTROL_RE.search(val):
            out.append(make("STEUERZEICHEN", line=1, field=f"Header {n}"))
    return out


def check_bookings(h: Header, bookings: list[Booking]) -> list[Finding]:
    out: list[Finding] = []
    fy_end = fiscal_year_end(h.fiscal_year_start)
    expected = len(C.COLUMNS_BY_VERSION.get(h.format_version, C.BOOKING_COLUMNS_V13))
    for idx, b in enumerate(bookings):
        line = idx + 3
        pre: list[Finding] = []
        amount = b.amount
        if not isinstance(amount, Decimal):
            try:
                amount = Decimal(str(amount))
            except InvalidOperation:
                pre.append(make("UMSATZ_FORMAT", line=line, field="1 Umsatz", value=str(b.amount)))
                amount = None
        if amount is not None:
            if not amount.is_finite():
                pre.append(make("UMSATZ_FORMAT", line=line, field="1 Umsatz", value=str(amount)))
            elif amount <= 0:
                pre.append(make("UMSATZ_NICHT_POSITIV", line=line, field="1 Umsatz", value=str(amount)))
            elif amount != amount.quantize(CENT):
                pre.append(make("UMSATZ_FORMAT", "Der Umsatz hat mehr als 2 Nachkommastellen.", line=line, field="1 Umsatz", value=str(amount)))
            elif amount > MAX_AMOUNT:
                pre.append(make("UMSATZ_FORMAT", "Der Umsatz hat mehr als 10 Vorkommastellen.", line=line, field="1 Umsatz", value=str(amount)))
        d = b.document_date
        if not (h.fiscal_year_start <= d <= fy_end):
            pre.append(make(
                "BELEGDATUM_AUSSERHALB_WJ",
                f"Belegdatum {d:%d.%m.%Y} liegt außerhalb des Wirtschaftsjahres "
                f"{h.fiscal_year_start:%d.%m.%Y}-{fy_end:%d.%m.%Y}.",
                line=line, field="10 Belegdatum", value=d.isoformat(),
            ))
        for label, val in (
            ("11 Belegfeld 1", b.document_field_1),
            ("12 Belegfeld 2", b.document_field_2),
            ("14 Buchungstext", b.text),
            ("37 KOST1 - Kostenstelle", b.cost_center_1),
            ("38 KOST2 - Kostenstelle", b.cost_center_2),
        ):
            bad = _not_cp1252(val)
            if bad:
                pre.append(make("ZEICHEN_NICHT_CP1252", f"Nicht darstellbar: {', '.join(repr(c) for c in bad[:5])}.", line=line, field=label, value=val))
            if val.startswith(("=", "@")):
                pre.append(make("FORMELZEICHEN_BEIM_SCHREIBEN", f"Der Wert beginnt mit {val[0]!r}.", line=line, field=label, value=val))
        if MAX_DOCUMENT_FIELD_2_SAFE < len(b.document_field_2) <= MAX_DOCUMENT_FIELD:
            pre.append(make(
                "BELEGFELD2_ZU_LANG",
                f"{len(b.document_field_2)} Zeichen. Beim Schreiben erlaubt dieser Server höchstens 12, weil die "
                f"englische Formatbeschreibung nur 12 nennt (die deutsche 36).",
                line=line, field="12 Belegfeld 2", value=b.document_field_2,
            ))
        out += pre
        blocked_fields = {f.field for f in pre if f.code in ("FORMELZEICHEN_BEIM_SCHREIBEN", "BELEGFELD2_ZU_LANG")}
        if any(f.code in ("UMSATZ_FORMAT", "UMSATZ_NICHT_POSITIV") for f in pre):
            amount_ok = False
        else:
            amount_ok = True
        safe = b if amount_ok else Booking(**{**b.__dict__, "amount": Decimal("1.00")})
        values, quoted = booking_fields(h, safe)
        found = check_row(Row(line=line, values=values, quoted=quoted), h, expected)
        if not amount_ok:
            found = [f for f in found if not f.code.startswith("UMSATZ_")]
        if any(f.code == "BELEGDATUM_AUSSERHALB_WJ" for f in pre):
            found = [f for f in found if f.code != "BELEGDATUM_AUSSERHALB_ZEITRAUM"]
        found = [f for f in found if not (
            f.code in ("FORMELZEICHEN_AM_ANFANG", "BELEGFELD2_UEBER_12") and f.field in blocked_fields
        )]
        out += found
    return out


def check_locking(h: Header, bookings: list[Booking]) -> list[Finding]:
    if h.locking:
        return []
    lines = [idx + 3 for idx, b in enumerate(bookings) if b.locking]
    if not lines:
        return []
    return [make(
        "FESTSCHREIBUNG_EINZELN",
        f"Der Kopf sagt 'keine Festschreibung', aber {len(lines)} Buchung(en) verlangen Festschreibung, zuerst in "
        f"Zeile {lines[0]}. Laut DATEV würde dann der ganze Stapel nach dem Import festgeschrieben.",
        line=lines[0], field="114 Festschreibung", value="1",
    )]


def validate(h: Header, bookings: list[Booking]) -> list[Finding]:
    return check_header_model(h) + check_bookings(h, bookings) + check_locking(h, bookings)


def build_extf(h: Header, bookings: list[Booking], created_at: datetime | None = None) -> bytes:
    """Return the file content. Raises ExtfValidationError if there are errors."""
    findings = validate(h, bookings)
    if any(f.severity == "fehler" for f in findings):
        raise ExtfValidationError(findings)
    hv, hq = header_fields(h, created_at)
    lines = [format_line(hv, hq), ";".join(C.COLUMNS_BY_VERSION[h.format_version])]
    for b in bookings:
        v, q = booking_fields(h, b)
        lines.append(format_line(v, q))
    data = (CRLF.join(lines) + CRLF).encode(ENCODING)
    check = read_extf(data)
    if not check.valid:
        raise RuntimeError(f"Interner Fehler: erzeugte Datei ist nicht gültig: {check.errors[:3]}")
    return data


def write_new_file(path: Path, data: bytes) -> None:
    """Create `path` exclusively; never overwrite and never follow a symlink."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
    except BaseException:
        try:
            os.unlink(path)
        except OSError:
            pass
        raise
