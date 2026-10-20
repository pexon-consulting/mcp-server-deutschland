"""MCP-Server "Feiertage und Arbeitstage in Deutschland" (Python-SDK mcp 2.3)."""

from __future__ import annotations

import logging
import sys
from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from .holidays import STATES, check_state, holidays, working_days

# Bei stdio gehört stdout dem Protokoll. Logs gehen deshalb nach stderr.
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("feiertage-mcp")

mcp = MCPServer(
    "feiertage",
    version="0.1.0",
    instructions="Gesetzliche Feiertage und Arbeitstage je Bundesland in Deutschland, offline berechnet.",
)

READ_ONLY = ToolAnnotations(read_only_hint=True, idempotent_hint=True, open_world_hint=False)

StateCode = Annotated[str, Field(description="Kürzel des Bundeslands, z. B. BY, NW, BE", min_length=2, max_length=2)]


class HolidayOut(BaseModel):
    date: str = Field(description="Datum im Format JJJJ-MM-TT")
    name: str
    weekday: str
    nationwide: bool = Field(description="true, wenn der Feiertag in ganz Deutschland gilt")


class HolidayList(BaseModel):
    year: int
    state: str
    state_name: str
    count: int
    holidays: list[HolidayOut]


class WorkingDays(BaseModel):
    start: str
    end: str
    state: str
    working_days: int
    holidays_on_workdays: list[HolidayOut]


WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]


def _out(h) -> HolidayOut:
    return HolidayOut(date=h.day.isoformat(), name=h.name, weekday=WEEKDAYS[h.day.weekday()], nationwide=h.nationwide)


def _parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ToolError(f"{field} '{value}' ist kein gültiges Datum. Erwartet wird JJJJ-MM-TT, z. B. 2026-12-24.")


@mcp.tool(title="Feiertage eines Bundeslands", annotations=READ_ONLY)
def list_holidays(
    year: Annotated[int, Field(description="Jahr, 1995 bis 2100")],
    state: StateCode,
) -> HolidayList:
    """Listet die gesetzlichen Feiertage eines Jahres für ein Bundesland."""
    log.info("list_holidays year=%s state=%s", year, state)
    try:
        code = check_state(state)
        items = holidays(year, code)
    except ValueError as exc:
        raise ToolError(str(exc))
    return HolidayList(
        year=year,
        state=code,
        state_name=STATES[code],
        count=len(items),
        holidays=[_out(h) for h in items],
    )


@mcp.tool(title="Arbeitstage zählen", annotations=READ_ONLY)
def count_working_days(
    start: Annotated[str, Field(description="Erster Tag, JJJJ-MM-TT (inklusive)")],
    end: Annotated[str, Field(description="Letzter Tag, JJJJ-MM-TT (inklusive)")],
    state: StateCode,
    saturday_is_workday: Annotated[bool, Field(description="Samstag als Arbeitstag zählen")] = False,
) -> WorkingDays:
    """Zählt die Arbeitstage zwischen zwei Daten (Mo-Fr ohne gesetzliche Feiertage des Bundeslands)."""
    log.info("count_working_days %s..%s state=%s", start, end, state)
    first = _parse_date(start, "start")
    last = _parse_date(end, "end")
    try:
        code = check_state(state)
        count, skipped = working_days(first, last, code, saturday_is_workday)
    except ValueError as exc:
        raise ToolError(str(exc))
    return WorkingDays(
        start=first.isoformat(),
        end=last.isoformat(),
        state=code,
        working_days=count,
        holidays_on_workdays=[_out(h) for h in skipped],
    )


def main() -> None:
    log.info("feiertage-mcp startet (stdio)")
    mcp.run()


if __name__ == "__main__":
    main()
