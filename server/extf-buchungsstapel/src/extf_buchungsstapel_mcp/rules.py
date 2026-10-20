"""Check rules for header, column line and booking lines."""

from __future__ import annotations

import re
from datetime import date, datetime

from . import columns as C
from .codes import CODES
from .model import Finding, Header, Row

AMOUNT_RE = re.compile(r"^\d{1,10},\d{2}$")
AMOUNT_SHORT_RE = re.compile(r"^\d{1,10}(,\d)?$")
ACCOUNT_RE = re.compile(r"^\d{1,9}$")
BU_KEY_RE = re.compile(r"^\d{1,4}$")
DOCUMENT_FIELD_RE = re.compile(r"^[A-Za-z0-9_$&%*+\-/]*$")
COST_CENTER_RE = re.compile(r"^[\w ]*$")
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
TIMESTAMP_RE = re.compile(r"^20\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])([01]\d|2[0-3])[0-5]\d[0-5]\d{4}$")
DATE_RE = re.compile(r"^20\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])$")
DESCRIPTION_RE = re.compile(r"^[\w./ ]*$")
DICTATION_RE = re.compile(r"^([A-Z]{2}){0,2}$")
CHART_RE = re.compile(r"^(\d{2}){0,2}$")
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")

MAX_TEXT = 60
MAX_DOCUMENT_FIELD = 36
# DATEV DE allows 36 characters for Belegfeld 2, DATEV EN only 12; the writer uses the stricter value.
MAX_DOCUMENT_FIELD_2_SAFE = 12
MAX_COST_CENTER = 36
MAX_BOOKINGS = 99_999
MAX_FILE_BYTES = 50_000_000
MAX_FINDINGS = 10_000
# Spreadsheet programs evaluate cells starting with these characters as formulas.
FORMULA_START = ("=", "+", "-", "@", "\t", "\r")


def make(code: str, message: str | None = None, *, line: int | None = None,
         field: str | None = None, value: str | None = None) -> Finding:
    info = CODES[code]
    if value is not None and len(value) > 80:
        value = value[:77] + "..."
    return Finding(code, info.severity, message or info.explanation, line, field, value)


def parse_yyyymmdd(value: str) -> date | None:
    if not DATE_RE.match(value):
        return None
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except ValueError:
        return None


def fiscal_year_end(start: date) -> date:
    """Last day of the fiscal year that begins at `start` (12 months)."""
    year, month = start.year + 1, start.month
    try:
        nxt = start.replace(year=year, month=month)
    except ValueError:  # 29 Feb start
        nxt = date(year, month, 28)
    return date.fromordinal(nxt.toordinal() - 1)


def resolve_document_date(ttmm: str, fiscal_start: date) -> date | None:
    """Map TTMM into the fiscal year starting at `fiscal_start`."""
    if not re.fullmatch(r"\d{4}", ttmm):
        return None
    day, month = int(ttmm[:2]), int(ttmm[2:])
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    year = fiscal_start.year if (month, day) >= (fiscal_start.month, fiscal_start.day) else fiscal_start.year + 1
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _hf(n: int) -> str:
    info = C.HEADER_FIELDS[n - 1]
    return f"Header {n} {info.name}"


def check_header(values: list[str], quoted: list[bool], line: int = 1) -> tuple[Header | None, list[Finding]]:
    out: list[Finding] = []
    if len(values) != C.HEADER_FIELD_COUNT:
        out.append(make("HEADER_FELDANZAHL", f"Der Header hat {len(values)} statt 31 Felder.", line=line))
    v = list(values) + [""] * max(0, C.HEADER_FIELD_COUNT - len(values))
    q = list(quoted) + [False] * max(0, C.HEADER_FIELD_COUNT - len(quoted))

    def g(n: int) -> str:
        return v[n - 1]

    if g(1) not in ("EXTF", "DTVF"):
        out.append(make("HEADER_KENNZEICHEN", line=line, field=_hf(1), value=g(1)))
    elif g(1) == "DTVF":
        out.append(make("HEADER_KENNZEICHEN_DTVF", line=line, field=_hf(1), value=g(1)))
    if g(2) != str(C.HEADER_VERSION):
        out.append(make("HEADER_VERSION", f"Die Header-Version ist {g(2)!r}, erwartet wird 700.", line=line, field=_hf(2), value=g(2)))
    category_ok = g(3) == str(C.CATEGORY_BOOKING_BATCH)
    if not category_ok:
        out.append(make("HEADER_FORMATKATEGORIE", line=line, field=_hf(3), value=g(3)))
    if g(4) != C.CATEGORY_NAME:
        out.append(make("HEADER_FORMATNAME", line=line, field=_hf(4), value=g(4)))
    fmt_version: int | None = None
    if g(5) == "13":
        fmt_version = 13
    elif g(5) == "12":
        fmt_version = 12
        out.append(make("HEADER_FORMATVERSION_ALT", line=line, field=_hf(5), value=g(5)))
    else:
        out.append(make("HEADER_FORMATVERSION", line=line, field=_hf(5), value=g(5)))

    created: datetime | None = None
    if TIMESTAMP_RE.match(g(6)):
        try:
            created = datetime.strptime(g(6)[:14], "%Y%m%d%H%M%S").replace(microsecond=int(g(6)[14:]) * 1000)
        except ValueError:
            out.append(make("HEADER_ZEITSTEMPEL", line=line, field=_hf(6), value=g(6)))
    else:
        out.append(make("HEADER_ZEITSTEMPEL", line=line, field=_hf(6), value=g(6)))

    for n in (7, 23, 25, 26, 29):
        if g(n) != "":
            out.append(make("HEADER_FELD", f"Feld {n} muss leer sein.", line=line, field=_hf(n), value=g(n)))
    for n in (24, 30):
        if g(n) != "":
            out.append(make("HEADER_FELD", f"Feld {n} muss ein leerer Text sein.", line=line, field=_hf(n), value=g(n)))
    for n, maxlen in ((8, 2), (9, 25), (10, 25), (31, 16)):
        if len(g(n)) > maxlen:
            out.append(make("HEADER_FELD", f"Feld {n} ist länger als {maxlen} Zeichen.", line=line, field=_hf(n), value=g(n)))
    if not re.fullmatch(r"\d{0,4}", g(28)):
        out.append(make("HEADER_FELD", "Feld 28 darf nur 0-4 Ziffern enthalten.", line=line, field=_hf(28), value=g(28)))

    consultant = client = account_length = None
    if re.fullmatch(r"\d{4,7}", g(11)) and 1001 <= int(g(11)) <= 9_999_999:
        consultant = int(g(11))
    else:
        out.append(make("HEADER_BERATERNUMMER", line=line, field=_hf(11), value=g(11)))
    if re.fullmatch(r"\d{1,5}", g(12)) and 1 <= int(g(12)) <= 99_999:
        client = int(g(12))
    else:
        out.append(make("HEADER_MANDANTENNUMMER", line=line, field=_hf(12), value=g(12)))
    fy_start = parse_yyyymmdd(g(13))
    if fy_start is None:
        out.append(make("HEADER_WJ_BEGINN", line=line, field=_hf(13), value=g(13)))
    if re.fullmatch(r"[4-8]", g(14)):
        account_length = int(g(14))
    else:
        out.append(make("HEADER_SACHKONTENLAENGE", line=line, field=_hf(14), value=g(14)))
    d_from = parse_yyyymmdd(g(15))
    if d_from is None:
        out.append(make("HEADER_DATUM_VON", line=line, field=_hf(15), value=g(15)))
    d_to = parse_yyyymmdd(g(16))
    if d_to is None:
        out.append(make("HEADER_DATUM_BIS", line=line, field=_hf(16), value=g(16)))
    if d_from and d_to and d_from > d_to:
        out.append(make("HEADER_ZEITRAUM", f"Datum von ({d_from:%d.%m.%Y}) liegt nach Datum bis ({d_to:%d.%m.%Y}).", line=line, field=_hf(15)))
    if fy_start and d_from and d_to and d_from <= d_to:
        fy_end = fiscal_year_end(fy_start)
        if d_from < fy_start or d_to > fy_end:
            out.append(make(
                "HEADER_ZEITRAUM_AUSSERHALB_WJ",
                f"Zeitraum {d_from:%d.%m.%Y}-{d_to:%d.%m.%Y} liegt nicht im Wirtschaftsjahr "
                f"{fy_start:%d.%m.%Y}-{fy_end:%d.%m.%Y}.",
                line=line, field=_hf(15),
            ))

    if len(g(17)) > 30 or not DESCRIPTION_RE.match(g(17)):
        out.append(make("HEADER_BEZEICHNUNG", line=line, field=_hf(17), value=g(17)))
    if not DICTATION_RE.match(g(18)):
        out.append(make("HEADER_DIKTATKUERZEL", line=line, field=_hf(18), value=g(18)))
    if g(19) not in ("", "1", "2"):
        out.append(make("HEADER_BUCHUNGSTYP", line=line, field=_hf(19), value=g(19)))
    if g(20) not in ("", "0", "30", "40", "50", "64"):
        out.append(make("HEADER_RECHNUNGSLEGUNGSZWECK", line=line, field=_hf(20), value=g(20)))
    if g(21) == "":
        out.append(make("HEADER_FESTSCHREIBUNG_LEER", line=line, field=_hf(21)))
    elif g(21) not in ("0", "1"):
        out.append(make("HEADER_FESTSCHREIBUNG", line=line, field=_hf(21), value=g(21)))
    if g(22) != "" and not CURRENCY_RE.match(g(22)):
        out.append(make("HEADER_WKZ", line=line, field=_hf(22), value=g(22)))
    if not CHART_RE.match(g(27)):
        out.append(make("HEADER_SACHKONTENRAHMEN", line=line, field=_hf(27), value=g(27)))

    for n in sorted(C.HEADER_TEXT_FIELDS):
        if g(n) != "" and not q[n - 1]:
            out.append(make("TEXT_OHNE_ANFUEHRUNGSZEICHEN", line=line, field=_hf(n), value=g(n)))
        if g(n).startswith(FORMULA_START):
            out.append(make("FORMELZEICHEN_AM_ANFANG", line=line, field=_hf(n), value=_escaped(g(n))))

    header = None
    if category_ok and fmt_version and None not in (consultant, client, fy_start, account_length, d_from, d_to):
        header = Header(
            consultant_number=consultant,
            client_number=client,
            fiscal_year_start=fy_start,
            account_length=account_length,
            date_from=d_from,
            date_to=d_to,
            description=g(17),
            dictation_code=g(18),
            locking=g(21) != "0",
            currency=g(22) or "EUR",
            chart_of_accounts=g(27),
            origin=g(8),
            exported_by=g(9),
            application_info=g(31),
            booking_type=int(g(19)) if g(19) in ("1", "2") else 1,
            accounting_purpose=int(g(20)) if g(20) in ("0", "30", "40", "50", "64") else 0,
            created_at=created,
            format_version=fmt_version,
            marker=g(1),
        )
    return header, out


def check_columns(captions: list[str], header_version: int | None, line: int = 2) -> list[Finding]:
    out: list[Finding] = []
    n = len(captions)
    known = {len(cols): ver for ver, cols in C.COLUMNS_BY_VERSION.items()}
    if header_version in C.COLUMNS_BY_VERSION:
        expected = len(C.COLUMNS_BY_VERSION[header_version])
        if n != expected:
            if n in known:
                out.append(make(
                    "VERSION_GEMISCHT",
                    f"Header nennt Formatversion {header_version} ({expected} Spalten), die Spaltenzeile hat "
                    f"{n} Spalten wie Formatversion {known[n]}.",
                    line=line,
                ))
            else:
                out.append(make("SPALTENANZAHL", f"Die Spaltenzeile hat {n} statt {expected} Spalten.", line=line))
        reference = C.COLUMNS_BY_VERSION[header_version]
    else:
        if n not in known:
            out.append(make("SPALTENANZAHL", f"Die Spaltenzeile hat {n} Spalten; erwartet werden 125 (oder 124).", line=line))
        reference = C.BOOKING_COLUMNS_V13
    for i, (got, want) in enumerate(zip(captions, reference), start=1):
        if got == want:
            continue
        if C.normalize_caption(got) == C.normalize_caption(want):
            out.append(make("SPALTENNAME_SCHREIBWEISE", f"Spalte {i}: {got!r} statt {want!r}.", line=line, field=f"Spalte {i}", value=got))
        else:
            out.append(make("SPALTENNAME_ABWEICHEND", f"Spalte {i}: {got!r} statt {want!r}.", line=line, field=f"Spalte {i}", value=got))
    return out


def _fname(n: int) -> str:
    return f"{n} {C.BOOKING_COLUMNS_V13[n - 1]}"


def _escaped(value: str) -> str:
    return value.encode("unicode_escape").decode("ascii") if CONTROL_RE.search(value) else value


def check_amount(value: str, line: int | None) -> list[Finding]:
    f = _fname(C.F_AMOUNT)
    if value == "":
        return [make("UMSATZ_FEHLT", line=line, field=f)]
    if value.startswith("-") or value.startswith("+"):
        return [make("UMSATZ_NICHT_POSITIV", line=line, field=f, value=value)]
    if AMOUNT_RE.match(value):
        if int(value.replace(",", "")) == 0:
            return [make("UMSATZ_NICHT_POSITIV", line=line, field=f, value=value)]
        return []
    if AMOUNT_SHORT_RE.match(value):
        if int(value.replace(",", "")) == 0:
            return [make("UMSATZ_NICHT_POSITIV", line=line, field=f, value=value)]
        return [make("UMSATZ_OHNE_NACHKOMMA", line=line, field=f, value=value)]
    msg = None
    if re.fullmatch(r"\d+\.\d{1,2}", value):
        msg = f"Der Umsatz {value!r} verwendet einen Punkt als Dezimaltrenner; DATEV erwartet ein Komma ({value.replace('.', ',')})."
    return [make("UMSATZ_FORMAT", msg, line=line, field=f, value=value)]


def check_account(value: str, number: int, account_length: int | None, line: int | None) -> list[Finding]:
    prefix = "KONTO" if number == C.F_ACCOUNT else "GEGENKONTO"
    f = _fname(number)
    if value == "":
        return [make(f"{prefix}_FEHLT", line=line, field=f)]
    if not value.isascii() or not value.isdigit() or set(value) == {"0"}:
        return [make(f"{prefix}_FORMAT", line=line, field=f, value=value)]
    limit = (account_length + 1) if account_length else 9
    if len(value) > limit or len(value) > 9:
        detail = f" (Sachkontenlänge {account_length})" if account_length else ""
        return [make(f"{prefix}_ZU_LANG", f"{'Konto' if prefix == 'KONTO' else 'Gegenkonto'} {value} hat {len(value)} Stellen, erlaubt sind höchstens {min(limit, 9)}{detail}.", line=line, field=f, value=value)]
    return []


def check_document_field(value: str, number: int, line: int | None) -> list[Finding]:
    prefix = "BELEGFELD1" if number == C.F_DOCUMENT_FIELD_1 else "BELEGFELD2"
    out = []
    if len(value) > MAX_DOCUMENT_FIELD:
        out.append(make(f"{prefix}_ZU_LANG", f"{len(value)} Zeichen, erlaubt sind 36.", line=line, field=_fname(number), value=value))
    elif prefix == "BELEGFELD2" and len(value) > MAX_DOCUMENT_FIELD_2_SAFE:
        out.append(make("BELEGFELD2_UEBER_12", f"{len(value)} Zeichen; sicher sind höchstens 12.", line=line, field=_fname(number), value=value))
    if not DOCUMENT_FIELD_RE.match(value):
        bad = sorted({c for c in value if not DOCUMENT_FIELD_RE.match(c)})
        shown = ", ".join(repr(c) for c in bad[:8])
        out.append(make(f"{prefix}_ZEICHEN", f"Unerlaubte Zeichen: {shown}. Erlaubt sind A-Z, a-z, 0-9, _ und $ & % * + - /.", line=line, field=_fname(number), value=value))
    return out


def check_text(value: str, line: int | None) -> list[Finding]:
    if len(value) > MAX_TEXT:
        return [make("BUCHUNGSTEXT_ZU_LANG", f"{len(value)} Zeichen, erlaubt sind 60.", line=line, field=_fname(C.F_TEXT), value=value)]
    return []


def check_cost_center(value: str, number: int, line: int | None) -> list[Finding]:
    if len(value) > MAX_COST_CENTER or not COST_CENTER_RE.match(value):
        return [make("KOST_FORMAT", line=line, field=_fname(number), value=value)]
    return []


def check_row(row: Row, header: Header | None, expected_fields: int) -> list[Finding]:
    out: list[Finding] = []
    line = row.line
    n = len(row.values)
    if n > expected_fields:
        out.append(make("ZEILE_ZU_VIELE_FELDER", f"{n} statt {expected_fields} Felder.", line=line))
    elif n < expected_fields:
        out.append(make("ZEILE_ZU_WENIGE_FELDER", f"{n} statt {expected_fields} Felder.", line=line))

    out += check_amount(row.get(C.F_AMOUNT), line)
    dc = row.get(C.F_DEBIT_CREDIT)
    if dc not in ("S", "H"):
        out.append(make("SOLL_HABEN_UNGUELTIG", line=line, field=_fname(C.F_DEBIT_CREDIT), value=dc))
    cur = row.get(C.F_CURRENCY)
    if cur and not CURRENCY_RE.match(cur):
        out.append(make("WKZ_UNGUELTIG", line=line, field=_fname(C.F_CURRENCY), value=cur))
    length = header.account_length if header else None
    acc = row.get(C.F_ACCOUNT)
    contra = row.get(C.F_CONTRA_ACCOUNT)
    acc_f = check_account(acc, C.F_ACCOUNT, length, line)
    con_f = check_account(contra, C.F_CONTRA_ACCOUNT, length, line)
    out += acc_f + con_f
    if not acc_f and not con_f and acc == contra:
        out.append(make("KONTO_GLEICH_GEGENKONTO", line=line, field=_fname(C.F_CONTRA_ACCOUNT), value=contra))
    bu = row.get(C.F_BU_KEY)
    if bu and not BU_KEY_RE.match(bu):
        out.append(make("BU_SCHLUESSEL_FORMAT", line=line, field=_fname(C.F_BU_KEY), value=bu))
    elif bu and len(bu) < 4:
        out.append(make("BU_SCHLUESSEL_KURZ", line=line, field=_fname(C.F_BU_KEY), value=bu))

    ttmm = row.get(C.F_DOCUMENT_DATE)
    fdate = _fname(C.F_DOCUMENT_DATE)
    if ttmm == "":
        out.append(make("BELEGDATUM_FEHLT", line=line, field=fdate))
    elif header is not None:
        resolved = resolve_document_date(ttmm, header.fiscal_year_start)
        if resolved is None:
            out.append(make("BELEGDATUM_FORMAT", line=line, field=fdate, value=ttmm))
        elif not (header.date_from <= resolved <= header.date_to):
            out.append(make(
                "BELEGDATUM_AUSSERHALB_ZEITRAUM",
                f"Belegdatum {resolved:%d.%m.%Y} liegt außerhalb des Zeitraums "
                f"{header.date_from:%d.%m.%Y}-{header.date_to:%d.%m.%Y}.",
                line=line, field=fdate, value=ttmm,
            ))
    elif not re.fullmatch(r"(0[1-9]|[12]\d|3[01])(0[1-9]|1[0-2])", ttmm):
        out.append(make("BELEGDATUM_FORMAT", line=line, field=fdate, value=ttmm))

    out += check_document_field(row.get(C.F_DOCUMENT_FIELD_1), C.F_DOCUMENT_FIELD_1, line)
    out += check_document_field(row.get(C.F_DOCUMENT_FIELD_2), C.F_DOCUMENT_FIELD_2, line)
    out += check_text(row.get(C.F_TEXT), line)
    out += check_cost_center(row.get(C.F_COST_CENTER_1), C.F_COST_CENTER_1, line)
    out += check_cost_center(row.get(C.F_COST_CENTER_2), C.F_COST_CENTER_2, line)

    if row.get(C.F_SERVICE_DATE) and not row.get(C.F_TAX_PERIOD_DATE):
        out.append(make("LEISTUNGSDATUM_OHNE_STEUERPERIODE", line=line, field=_fname(C.F_TAX_PERIOD_DATE), value=row.get(C.F_SERVICE_DATE)))

    lock = row.get(C.F_LOCKING)
    if lock not in ("", "0", "1"):
        out.append(make("FESTSCHREIBUNG_UNGUELTIG", line=line, field=_fname(C.F_LOCKING), value=lock))

    for i in range(1, min(n, len(C.BOOKING_COLUMNS_V13)) + 1):
        val = row.values[i - 1]
        if CONTROL_RE.search(val):
            out.append(make("STEUERZEICHEN", line=line, field=_fname(i), value=val.encode("unicode_escape").decode("ascii")))
        if val == "":
            continue
        if i in C.TEXT_FIELDS and val.startswith(FORMULA_START):
            out.append(make("FORMELZEICHEN_AM_ANFANG", line=line, field=_fname(i), value=_escaped(val)))
        if i in C.TEXT_FIELDS and not row.quoted[i - 1]:
            out.append(make("TEXT_OHNE_ANFUEHRUNGSZEICHEN", line=line, field=_fname(i), value=val))
        elif i not in C.TEXT_FIELDS and row.quoted[i - 1]:
            out.append(make("ZAHL_IN_ANFUEHRUNGSZEICHEN", line=line, field=_fname(i), value=val))
    return out
