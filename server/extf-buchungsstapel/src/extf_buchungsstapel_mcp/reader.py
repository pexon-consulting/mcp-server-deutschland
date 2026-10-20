"""Read and check existing EXTF files (Windows-1252, or Unicode with BOM)."""

from __future__ import annotations

import codecs
import re
from datetime import date

from . import columns as C
from .model import Finding, Header, Report, Row
from .rules import (
    MAX_BOOKINGS,
    MAX_FILE_BYTES,
    MAX_FINDINGS,
    check_columns,
    check_header,
    check_row,
    make,
    resolve_document_date,
)

FILENAME_RE = re.compile(r"^EXTF_.*\.csv$", re.IGNORECASE)


def decode(data: bytes) -> tuple[str | None, str | None, list[Finding]]:
    """Return (text, encoding label, findings)."""
    boms = (
        (codecs.BOM_UTF32_LE, "utf-32"),
        (codecs.BOM_UTF32_BE, "utf-32"),
        (codecs.BOM_UTF8, "utf-8-sig"),
        (codecs.BOM_UTF16_LE, "utf-16"),
        (codecs.BOM_UTF16_BE, "utf-16"),
    )
    for bom, enc in boms:
        if data.startswith(bom):
            try:
                text = data.decode(enc)
            except UnicodeDecodeError as exc:
                return None, None, [make("ZEICHENSATZ_UNGUELTIG", f"Ungültige Byte-Folge für {enc} an Position {exc.start}.")]
            return text.lstrip("\ufeff"), enc, [make("UNICODE_MIT_BOM")]
    if data.isascii():
        return data.decode("ascii"), "windows-1252", []
    try:
        text = data.decode("utf-8")
        return text, "utf-8", [make("UTF8_OHNE_BOM")]
    except UnicodeDecodeError:
        pass
    try:
        return data.decode("cp1252"), "windows-1252", []
    except UnicodeDecodeError as exc:
        return None, None, [make("ZEICHENSATZ_UNGUELTIG", f"Byte 0x{data[exc.start]:02X} an Position {exc.start} ist in Windows-1252 nicht belegt.")]


def split_fields(line: str) -> tuple[list[str], list[bool], bool]:
    """Split one line at semicolons. Returns (values, quoted flags, ok)."""
    values: list[str] = []
    quoted: list[bool] = []
    i, n = 0, len(line)
    ok = True
    while True:
        if i < n and line[i] == '"':
            i += 1
            buf: list[str] = []
            closed = False
            while i < n:
                c = line[i]
                if c == '"':
                    if i + 1 < n and line[i + 1] == '"':
                        buf.append('"')
                        i += 2
                        continue
                    i += 1
                    closed = True
                    break
                buf.append(c)
                i += 1
            if not closed:
                ok = False
            if i < n and line[i] != ";":
                ok = False
                j = line.find(";", i)
                j = n if j == -1 else j
                buf.append(line[i:j])
                i = j
            values.append("".join(buf))
            quoted.append(True)
        else:
            j = line.find(";", i)
            j = n if j == -1 else j
            val = line[i:j]
            if '"' in val:
                ok = False
            values.append(val)
            quoted.append(False)
            i = j
        if i >= n:
            break
        i += 1  # skip ';'
        if i == n:
            values.append("")
            quoted.append(False)
            break
    return values, quoted, ok


def split_lines(text: str) -> tuple[list[str], list[Finding]]:
    out: list[Finding] = []
    parts = text.split("\n")
    lines: list[str] = []
    bad_lf: list[int] = []
    for idx, part in enumerate(parts):
        last = idx == len(parts) - 1
        if last:
            if part == "":
                break
            out.append(make("LETZTE_ZEILE_OHNE_CRLF", line=idx + 1))
            lines.append(part)
            break
        if part.endswith("\r"):
            lines.append(part[:-1])
        else:
            bad_lf.append(idx + 1)
            lines.append(part)
    if bad_lf:
        more = f" (insgesamt {len(bad_lf)} Zeilen)" if len(bad_lf) > 1 else ""
        out.append(make("ZEILENENDE_KEIN_CRLF", f"Zeile {bad_lf[0]} endet nur mit LF statt CR/LF{more}.", line=bad_lf[0]))
    return lines, out


def read_extf(data: bytes, filename: str | None = None) -> Report:
    """Parse and check a Buchungsstapel. Never raises on bad content."""
    report = Report()
    f = report.findings
    if filename is not None and not FILENAME_RE.match(filename):
        f.append(make("DATEINAME_PRAEFIX", value=filename))
    if not data:
        f.append(make("DATEI_LEER"))
        return report
    if len(data) > MAX_FILE_BYTES:
        f.append(make("DATEI_ZU_GROSS", f"Die Datei hat {len(data):,} Bytes.".replace(",", ".")))
    text, encoding, dec = decode(data)
    f.extend(dec)
    report.encoding = encoding
    if text is None:
        return report
    lines, lf = split_lines(text)
    f.extend(lf)
    if not lines or (len(lines) == 1 and lines[0] == ""):
        f.append(make("DATEI_LEER"))
        return report

    h_values, h_quoted, ok = split_fields(lines[0])
    if not ok:
        f.append(make("ANFUEHRUNGSZEICHEN_OFFEN", line=1))
    report.header_fields = h_values
    header, hf = check_header(h_values, h_quoted, line=1)
    f.extend(hf)
    report.header = header

    if len(lines) < 2:
        f.append(make("SPALTENZEILE_FEHLT", line=2))
        return report
    caps, _, ok = split_fields(lines[1])
    if not ok:
        f.append(make("ANFUEHRUNGSZEICHEN_OFFEN", line=2))
    report.columns = caps
    version = header.format_version if header else None
    if version is None and len(h_values) >= 5 and h_values[4] in ("12", "13"):
        version = int(h_values[4])
    f.extend(check_columns(caps, version, line=2))
    expected = len(C.COLUMNS_BY_VERSION[version]) if version in C.COLUMNS_BY_VERSION else len(caps)

    rows = lines[2:]
    while rows and rows[-1] == "":
        rows.pop()
    if not rows:
        f.append(make("KEINE_BUCHUNGEN", line=3))
    if len(rows) > MAX_BOOKINGS:
        f.append(make(
            "ZU_VIELE_BUCHUNGEN",
            f"Die Datei enthält {len(rows):,} Buchungen. Die Buchungszeilen wurden nicht gelesen und nicht geprüft.".replace(",", "."),
        ))
        return report

    empty_lock_lines: list[int] = []
    lock_one = False
    for offset, raw in enumerate(rows):
        line_no = offset + 3
        values, quoted, ok = split_fields(raw)
        if not ok:
            report.add(make("ANFUEHRUNGSZEICHEN_OFFEN", line=line_no), MAX_FINDINGS)
        row = Row(line=line_no, values=values, quoted=quoted)
        report.rows.append(row)
        for finding in check_row(row, header, expected):
            report.add(finding, MAX_FINDINGS)
        lock = row.get(C.F_LOCKING)
        if lock == "":
            empty_lock_lines.append(line_no)
        elif lock == "1":
            lock_one = True
    if empty_lock_lines:
        f.append(make(
            "FESTSCHREIBUNG_LEER",
            f"Feld 114 (Festschreibung) ist in {len(empty_lock_lines)} Buchung(en) leer, zuerst in Zeile "
            f"{empty_lock_lines[0]}. Laut DATEV bedeutet leer 'nicht definiert; wird automatisch festgeschrieben'.",
            line=empty_lock_lines[0],
        ))
    if header is not None and not header.locking and lock_one:
        f.append(make("FESTSCHREIBUNG_WIDERSPRUCH"))
    if report.dropped_total:
        d = report.dropped
        f.append(make(
            "BEFUNDE_GEKUERZT",
            f"{report.dropped_total:,} weitere Befunde wurden nur gezählt ({d['fehler']:,} Fehler, "
            f"{d['warnung']:,} Warnungen, {d['hinweis']:,} Hinweise).".replace(",", "."),
        ))
    return report


def row_to_booking_dict(row: Row, header: Header | None) -> dict:
    """Structured view of a booking line; raw values are kept as strings."""
    ttmm = row.get(C.F_DOCUMENT_DATE)
    iso: str | None = None
    if header is not None:
        resolved: date | None = resolve_document_date(ttmm, header.fiscal_year_start)
        iso = resolved.isoformat() if resolved else None
    return {
        "zeile": row.line,
        "umsatz": row.get(C.F_AMOUNT),
        "soll_haben": row.get(C.F_DEBIT_CREDIT),
        "wkz": row.get(C.F_CURRENCY),
        "konto": row.get(C.F_ACCOUNT),
        "gegenkonto": row.get(C.F_CONTRA_ACCOUNT),
        "bu_schluessel": row.get(C.F_BU_KEY),
        "belegdatum": ttmm,
        "belegdatum_iso": iso,
        "belegfeld1": row.get(C.F_DOCUMENT_FIELD_1),
        "belegfeld2": row.get(C.F_DOCUMENT_FIELD_2),
        "buchungstext": row.get(C.F_TEXT),
        "kost1": row.get(C.F_COST_CENTER_1),
        "kost2": row.get(C.F_COST_CENTER_2),
        "festschreibung": row.get(C.F_LOCKING),
    }
