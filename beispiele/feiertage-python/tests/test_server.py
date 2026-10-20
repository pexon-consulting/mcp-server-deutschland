import sys
from datetime import date

import pytest

from mcp import Client
from mcp.client.stdio import StdioServerParameters

from feiertage_mcp.holidays import easter_sunday, holidays, working_days
from feiertage_mcp.server import mcp

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_easter_sunday():
    assert easter_sunday(2024) == date(2024, 3, 31)
    assert easter_sunday(2026) == date(2026, 4, 5)
    assert easter_sunday(2027) == date(2027, 3, 28)


def test_state_specific_holidays():
    names_by = {h.name for h in holidays(2026, "BY")}
    names_be = {h.name for h in holidays(2026, "BE")}
    assert "Fronleichnam" in names_by and "Fronleichnam" not in names_be
    assert "Internationaler Frauentag" in names_be
    assert [h.day for h in holidays(2026, "SN") if h.name == "Buß- und Bettag"] == [date(2026, 11, 18)]


def test_working_days_december_2026_nrw():
    count, skipped = working_days(date(2026, 12, 1), date(2026, 12, 31), "NW")
    assert count == 22
    assert [h.name for h in skipped] == ["1. Weihnachtstag"]


async def test_in_process_tools():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        assert [t.name for t in tools.tools] == ["list_holidays", "count_working_days"]
        result = await client.call_tool("list_holidays", {"year": 2026, "state": "BY"})
        assert not result.is_error
        assert result.structured_content["count"] == 12


async def test_tool_error_for_unknown_state():
    async with Client(mcp) as client:
        result = await client.call_tool("list_holidays", {"year": 2026, "state": "XX"})
        assert result.is_error
        assert "Unbekanntes Bundesland" in result.content[0].text


async def test_stdio_roundtrip():
    params = StdioServerParameters(command=sys.executable, args=["-m", "feiertage_mcp.server"])
    async with Client(params) as client:
        result = await client.call_tool(
            "count_working_days", {"start": "2026-12-01", "end": "2026-12-31", "state": "NW"}
        )
        assert result.structured_content["working_days"] == 22
