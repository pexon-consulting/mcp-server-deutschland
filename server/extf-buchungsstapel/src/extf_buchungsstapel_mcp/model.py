"""Data model: header, booking, finding. No MCP dependency."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

Severity = Literal["fehler", "warnung", "hinweis"]


@dataclass(frozen=True)
class Finding:
    """One check result. `line` is the 1-based line in the file (header = 1)."""

    code: str
    severity: Severity
    message: str
    line: int | None = None
    field: str | None = None
    value: str | None = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "schwere": self.severity,
            "zeile": self.line,
            "feld": self.field,
            "wert": self.value,
            "meldung": self.message,
        }


@dataclass
class Header:
    """Header (Verwaltungssatz) of a Buchungsstapel."""

    consultant_number: int
    client_number: int
    fiscal_year_start: date
    account_length: int
    date_from: date
    date_to: date
    description: str = ""
    dictation_code: str = ""
    locking: bool = False
    currency: str = "EUR"
    chart_of_accounts: str = ""
    origin: str = ""
    exported_by: str = ""
    application_info: str = ""
    booking_type: int = 1
    accounting_purpose: int = 0
    created_at: datetime | None = None
    format_version: int = 13
    marker: str = "EXTF"

    def to_dict(self) -> dict:
        return {
            "kennzeichen": self.marker,
            "formatversion": self.format_version,
            "beraternummer": self.consultant_number,
            "mandantennummer": self.client_number,
            "wj_beginn": self.fiscal_year_start.isoformat(),
            "sachkontenlaenge": self.account_length,
            "datum_von": self.date_from.isoformat(),
            "datum_bis": self.date_to.isoformat(),
            "bezeichnung": self.description,
            "diktatkuerzel": self.dictation_code,
            "festschreibung": self.locking,
            "wkz": self.currency,
            "sachkontenrahmen": self.chart_of_accounts,
            "erzeugt_am": self.created_at.isoformat(timespec="milliseconds") if self.created_at else None,
        }


@dataclass
class Booking:
    """One booking line. `document_date` carries the full date; the file stores TTMM."""

    amount: Decimal
    debit_credit: str
    account: str
    contra_account: str
    document_date: date
    bu_key: str = ""
    document_field_1: str = ""
    document_field_2: str = ""
    text: str = ""
    cost_center_1: str = ""
    cost_center_2: str = ""
    locking: bool | None = None
    currency: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["amount"] = format(self.amount, "f")
        d["document_date"] = self.document_date.isoformat()
        return d


@dataclass
class Report:
    """Result of reading and checking a file."""

    findings: list[Finding] = field(default_factory=list)
    encoding: str | None = None
    header: Header | None = None
    header_fields: list[str] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)
    rows: list["Row"] = field(default_factory=list)
    # Findings beyond the collection limit are only counted, per severity.
    dropped: dict[str, int] = field(default_factory=lambda: {"fehler": 0, "warnung": 0, "hinweis": 0})

    def add(self, finding: Finding, limit: int) -> None:
        if len(self.findings) < limit:
            self.findings.append(finding)
        else:
            self.dropped[finding.severity] += 1

    @property
    def dropped_total(self) -> int:
        return sum(self.dropped.values())

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "fehler"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warnung"]

    @property
    def notes(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "hinweis"]

    @property
    def error_count(self) -> int:
        return len(self.errors) + self.dropped["fehler"]

    @property
    def warning_count(self) -> int:
        return len(self.warnings) + self.dropped["warnung"]

    @property
    def note_count(self) -> int:
        return len(self.notes) + self.dropped["hinweis"]

    @property
    def valid(self) -> bool:
        return self.error_count == 0


@dataclass
class Row:
    line: int
    values: list[str]
    quoted: list[bool]

    def get(self, number: int) -> str:
        return self.values[number - 1] if number <= len(self.values) else ""

    def is_quoted(self, number: int) -> bool:
        return self.quoted[number - 1] if number <= len(self.quoted) else False


class ExtfValidationError(ValueError):
    """Raised by the writer when bookings or header contain errors."""

    def __init__(self, findings: list[Finding]):
        self.findings = findings
        errors = [f for f in findings if f.severity == "fehler"]
        first = "; ".join(_short(f) for f in errors[:5])
        more = f" (und {len(errors) - 5} weitere)" if len(errors) > 5 else ""
        super().__init__(f"{len(errors)} Fehler: {first}{more}")


def _short(f: Finding) -> str:
    where = f"Zeile {f.line}" if f.line else "Datei"
    if f.field:
        where += f", {f.field}"
    return f"[{f.code}] {where}: {f.message}"
