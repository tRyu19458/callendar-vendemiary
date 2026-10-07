from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import calendar
import datetime

__all__ = [
    "RepublicanDate",
    "Sansculottide",
    "gregorian_to_republican",
    "republican_to_gregorian",
]

# Month names of the French Republican calendar. Each year has 12 months of
# 30 days, plus up to 5 (or 6 in leap years) complementary days at the end.
_MONTH_NAMES = (
    "Vendemiaire",
    "Brumaire",
    "Frimaire",
    "Nivose",
    "Pluviose",
    "Ventose",
    "Germinal",
    "Floreal",
    "Prairial",
    "Messidor",
    "Thermidor",
    "Fructidor",
)

# Names of the complementary "sansculottide" days at year end. There are
# 5 in a common year, 6 in a leap Republican year.
_SANS_NAMES = (
    "Virtue",
    "Genius",
    "Labor",
    "Opinion",
    "Rewards",
    "Revolution",
)

# Gregorian date on which Republican Year I begins (the proclamation of
# the Republic, as reckoned retroactively by the calendar's authors).
_REPUBLICAN_EPOCH = (1792, 9, 22)


def _gregorian_leap(year: int) -> bool:
    return calendar.isleap(year)


def _gregorian_to_ordinal(y: int, m: int, d: int) -> int:
    return datetime.date(y, m, d).toordinal()


def _ordinal_to_gregorian(n: int) -> Tuple[int, int, int]:
    t = datetime.date.fromordinal(n)
    return (t.year, t.month, t.day)


def _republican_leap(year: int) -> bool:
    """Determine whether a Republican year is leap (has a 6th sansculottide).

    The original Romme proposal used an arithmetic leap rule similar to the
    Gregorian calendar: every 4th year leap, but not every 100th unless also
    every 400th. The Republic applied this rule retroactively from Year III
    (which was leap). Years I and II were not leap under the arithmetic rule.
    """
    if year < 1:
        raise ValueError("Republican year must be positive", year)
    # Year III is the anchor; every 4th year from III is leap, with century
    # exceptions following the Gregorian pattern measured from that anchor.
    offset = year - 3
    return offset % 4 == 0 and (offset % 100 != 0 or offset % 400 == 0)


@dataclass(frozen=True)
class Sansculottide:
    """A complementary day at the end of the Republican year.

    Using a dedicated type rather than overloading ``RepublicanDate`` makes the
    structural distinction clear and lets callers distinguish the two cases by
    ``isinstance`` rather than inspecting fields.
    """

    year: int
    index: int  # 1-based: 1=Virtue ... 6=Revolution

    def __post_init__(self) -> None:
        if self.year < 1:
            raise ValueError("year must be >= 1")
        if self.index < 1 or self.index > 6:
            raise ValueError("sansculottide index must be in 1..6")
        if self.index == 6 and not _republican_leap(self.year):
            raise ValueError(
                "the sixth sansculottide exists only in leap Republican years"
            )

    @property
    def name(self) -> str:
        return _SANS_NAMES[self.index - 1]

    def __str__(self) -> str:
        return f"{self.name} Day, Year {roman(self.year)}"


@dataclass(frozen=True)
class RepublicanDate:
    """A day within one of the twelve 30-day Republican months."""

    year: int
    month: int  # 1..12
    day: int  # 1..30

    def __post_init__(self) -> None:
        if self.year < 1:
            raise ValueError("year must be >= 1")
        if self.month < 1 or self.month > 12:
            raise ValueError("month must be in 1..12")
        if self.day < 1 or self.day > 30:
            raise ValueError("day must be in 1..30")

    @property
    def month_name(self) -> str:
        return _MONTH_NAMES[self.month - 1]

    def __str__(self) -> str:
        return f"{self.day} {self.month_name} Year {roman(self.year)}"


def roman(n: int) -> str:
    """Render a positive integer in Roman numerals, as used in Republican dates."""
    if n < 1:
        raise ValueError("Roman numerals require n >= 1", n)
    table = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"),
        (1, "I"),
    ]
    out = []
    for value, sym in table:
        while n >= value:
            out.append(sym)
            n -= value
    return "".join(out)


def gregorian_to_republican(
    year: int, month: int, day: int
) -> "RepublicanDate | Sansculottide":
    """Convert a Gregorian date to a Republican calendar date.

    Accepts dates on or after 1792-09-22, the epoch of Year I. The result is
    either a ``RepublicanDate`` (for a day in one of the twelve 30-day months)
    or a ``Sansculottide`` (for a complementary day at year end).
    """
    g = datetime.date(year, month, day)
    e = datetime.date(*_REPUBLICAN_EPOCH)
    if g < e:
        raise ValueError(
            "date is before the Republican epoch (1792-09-22)",
            (year, month, day),
        )

    # Days elapsed since the Republican epoch (day 0 of Year I is the epoch
    # itself, which is day 1 of the calendar — so subtract).
    delta = (g - e).days
    return _delta_to_republican(delta)


def _delta_to_republican(delta: int) -> "RepublicanDate | Sansculottide":
    """Map an offset in days from the epoch onto a Republican date."""
    # Walk forward year by year. Years vary in length (365 or 366), so we
    # cannot just divide. The bound is small in practice so this is fine.
    year = 1
    while True:
        length = 366 if _republican_leap(year) else 365
        if delta < length:
            break
        delta -= length
        year += 1

    # delta is now the day-of-year, 0-based, within the Republican year.
    if delta < 360:
        month = delta // 30 + 1
        day = delta % 30 + 1
        return RepublicanDate(year=year, month=month, day=day)
    else:
        return Sansculottide(year=year, index=delta - 360 + 1)


def republican_to_gregorian(
    target: "RepublicanDate | Sansculottide",
) -> Tuple[int, int, int]:
    """Convert a Republican date to a Gregorian (y, m, d) triple."""
    days = _republican_day_of_year(target)
    for y in range(1, target.year):
        days += 366 if _republican_leap(y) else 365
    base = _gregorian_to_ordinal(*_REPUBLICAN_EPOCH)
    return _ordinal_to_gregorian(base + days)


def _republican_day_of_year(target: "RepublicanDate | Sansculottide") -> int:
    """Return the 0-based offset of ``target`` within its Republican year."""
    if isinstance(target, Sansculottide):
        return 360 + (target.index - 1)
    if isinstance(target, RepublicanDate):
        return (target.month - 1) * 30 + (target.day - 1)
    raise TypeError("expected RepublicanDate or Sansculottide", type(target))
