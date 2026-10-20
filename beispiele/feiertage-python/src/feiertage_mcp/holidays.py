"""Gesetzliche Feiertage in Deutschland, ohne externe API berechnet.

Bewegliche Feiertage hängen am Ostersonntag (Gaußsche Osterformel in der
Fassung des anonymen gregorianischen Algorithmus). Regionale Feiertage, die nur
in einzelnen Gemeinden gelten (Fronleichnam in Teilen von Sachsen und Thüringen,
Mariä Himmelfahrt in Teilen Bayerns, Augsburger Friedensfest), sind nicht enthalten.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

STATES: dict[str, str] = {
    "BW": "Baden-Württemberg",
    "BY": "Bayern",
    "BE": "Berlin",
    "BB": "Brandenburg",
    "HB": "Bremen",
    "HH": "Hamburg",
    "HE": "Hessen",
    "MV": "Mecklenburg-Vorpommern",
    "NI": "Niedersachsen",
    "NW": "Nordrhein-Westfalen",
    "RP": "Rheinland-Pfalz",
    "SL": "Saarland",
    "SN": "Sachsen",
    "ST": "Sachsen-Anhalt",
    "SH": "Schleswig-Holstein",
    "TH": "Thüringen",
}

MIN_YEAR = 1995
MAX_YEAR = 2100


@dataclass(frozen=True)
class Holiday:
    day: date
    name: str
    nationwide: bool


def easter_sunday(year: int) -> date:
    """Ostersonntag im gregorianischen Kalender."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)


def _repentance_day(year: int) -> date:
    """Buß- und Bettag: der Mittwoch vor dem 23. November."""
    nov22 = date(year, 11, 22)
    return nov22 - timedelta(days=(nov22.weekday() - 2) % 7)


def check_state(state: str) -> str:
    code = state.strip().upper()
    if code not in STATES:
        allowed = ", ".join(STATES)
        raise ValueError(f"Unbekanntes Bundesland '{state}'. Erlaubt sind: {allowed}.")
    return code


def check_year(year: int) -> int:
    if not MIN_YEAR <= year <= MAX_YEAR:
        raise ValueError(f"Jahr {year} wird nicht unterstützt. Erlaubt ist {MIN_YEAR} bis {MAX_YEAR}.")
    return year


def holidays(year: int, state: str) -> list[Holiday]:
    """Alle landesweit geltenden gesetzlichen Feiertage eines Bundeslands, sortiert."""
    year = check_year(year)
    st = check_state(state)
    easter = easter_sunday(year)

    def nat(day: date, name: str) -> Holiday:
        return Holiday(day, name, True)

    def reg(day: date, name: str) -> Holiday:
        return Holiday(day, name, False)

    result = [
        nat(date(year, 1, 1), "Neujahr"),
        nat(easter - timedelta(days=2), "Karfreitag"),
        nat(easter + timedelta(days=1), "Ostermontag"),
        nat(date(year, 5, 1), "Tag der Arbeit"),
        nat(easter + timedelta(days=39), "Christi Himmelfahrt"),
        nat(easter + timedelta(days=50), "Pfingstmontag"),
        nat(date(year, 10, 3), "Tag der Deutschen Einheit"),
        nat(date(year, 12, 25), "1. Weihnachtstag"),
        nat(date(year, 12, 26), "2. Weihnachtstag"),
    ]

    if st in {"BW", "BY", "ST"}:
        result.append(reg(date(year, 1, 6), "Heilige Drei Könige"))
    if (st == "BE" and year >= 2019) or (st == "MV" and year >= 2023):
        result.append(reg(date(year, 3, 8), "Internationaler Frauentag"))
    if st == "BE" and year in (2020, 2025):
        result.append(reg(date(year, 5, 8), "Tag der Befreiung"))
    if st == "BB":
        result.append(reg(easter, "Ostersonntag"))
        result.append(reg(easter + timedelta(days=49), "Pfingstsonntag"))
    if st in {"BW", "BY", "HE", "NW", "RP", "SL"}:
        result.append(reg(easter + timedelta(days=60), "Fronleichnam"))
    if st == "SL":
        result.append(reg(date(year, 8, 15), "Mariä Himmelfahrt"))
    if st == "TH" and year >= 2019:
        result.append(reg(date(year, 9, 20), "Weltkindertag"))
    reformation = {"BB", "MV", "SN", "ST", "TH"}
    if year >= 2018:
        reformation |= {"HB", "HH", "NI", "SH"}
    if year == 2017:
        result.append(nat(date(year, 10, 31), "Reformationstag"))
    elif st in reformation:
        result.append(reg(date(year, 10, 31), "Reformationstag"))
    if st in {"BW", "BY", "NW", "RP", "SL"}:
        result.append(reg(date(year, 11, 1), "Allerheiligen"))
    if st == "SN":
        result.append(reg(_repentance_day(year), "Buß- und Bettag"))

    return sorted(result, key=lambda h: h.day)


def working_days(start: date, end: date, state: str, saturday_is_workday: bool = False) -> tuple[int, list[Holiday]]:
    """Arbeitstage von start bis end (beide inklusive) und die Feiertage, die auf Werktage fielen."""
    if end < start:
        raise ValueError(f"Das Enddatum {end.isoformat()} liegt vor dem Startdatum {start.isoformat()}.")
    if (end - start).days > 366 * 5:
        raise ValueError("Der Zeitraum darf höchstens fünf Jahre umfassen.")
    st = check_state(state)
    by_day: dict[date, Holiday] = {}
    for year in range(start.year, end.year + 1):
        for h in holidays(year, st):
            by_day[h.day] = h

    last_workday = 5 if saturday_is_workday else 4
    count = 0
    skipped: list[Holiday] = []
    day = start
    while day <= end:
        if day.weekday() <= last_workday:
            if day in by_day:
                skipped.append(by_day[day])
            else:
                count += 1
        day += timedelta(days=1)
    return count, skipped
