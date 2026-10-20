from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from extf_buchungsstapel_mcp import columns as C
from extf_buchungsstapel_mcp.model import Booking, Header
from extf_buchungsstapel_mcp.writer import format_line, header_fields

FIXTURES = Path(__file__).parent / "fixtures"
CREATED = datetime(2026, 10, 19, 9, 30, 0, 123000)


def make_header(**kw) -> Header:
    base = dict(
        consultant_number=1001,
        client_number=1,
        fiscal_year_start=date(2026, 1, 1),
        account_length=4,
        date_from=date(2026, 9, 1),
        date_to=date(2026, 9, 30),
        description="Rechnungsausgang 09/2026",
        chart_of_accounts="03",
        created_at=CREATED,
    )
    base.update(kw)
    return Header(**base)


def make_booking(**kw) -> Booking:
    base = dict(
        amount=Decimal("1190.00"),
        debit_credit="S",
        account="10000",
        contra_account="8400",
        document_date=date(2026, 9, 2),
        document_field_1="RE2026-0815",
        text="Muster GmbH Beratung",
    )
    base.update(kw)
    return Booking(**base)


def header_line(**kw) -> str:
    return format_line(*header_fields(make_header(**kw)))


def raw_row(overrides: dict[int, str] | None = None, count: int = 125) -> str:
    """A valid booking line; `overrides` maps field number to the raw (already quoted) text."""
    values = [""] * count
    quoted = [(i + 1) in C.TEXT_FIELDS for i in range(count)]
    values[0] = "1190,00"
    values[1] = "S"
    values[6] = "10000"
    values[7] = "8400"
    values[9] = "0209"
    values[10] = "RE2026-0815"
    values[13] = "Muster GmbH Beratung"
    if count >= 114:
        values[113] = "0"
    line = format_line(values, quoted).split(";")
    for n, raw in (overrides or {}).items():
        line[n - 1] = raw
    return ";".join(line)


def build_raw(rows: list[str] | None = None, header: str | None = None, captions: str | None = None,
              newline: str = "\r\n", encoding: str = "cp1252") -> bytes:
    lines = [header if header is not None else header_line(),
             captions if captions is not None else ";".join(C.BOOKING_COLUMNS_V13)]
    lines += rows if rows is not None else [raw_row()]
    return (newline.join(lines) + newline).encode(encoding)


def codes(report) -> set[str]:
    return {f.code for f in report.findings}


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    d = tmp_path / "arbeitsordner"
    d.mkdir()
    monkeypatch.setenv("EXTF_ORDNER", str(d))
    return d
