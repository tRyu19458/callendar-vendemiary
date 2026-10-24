# Callendar Vendemiary

Translates dates between the French Republican calendar and the Gregorian system, for dates on or after 1792-09-22.

## Usage

```python
from callendar_vendemiary import (
    RepublicanDate,
    Sansculottide,
    gregorian_to_republican,
    republican_to_gregorian,
)

# 14 Vendemiaire Year II corresponds to 5 October 1793.
r = gregorian_to_republican(1793, 10, 5)
assert r == RepublicanDate(year=2, month=1, day=14)
assert r.month_name == "Vendemiaire"

# Round-trip back to Gregorian.
assert republican_to_gregorian(r) == (1793, 10, 5)

# The complementary days at year end are a distinct type.
s = gregorian_to_republican(1793, 9, 21)
assert isinstance(s, Sansculottide)
assert s == Sansculottide(year=1, index=5)
assert s.name == "Rewards"
```

## Why this exists

The French Republican calendar was used officially in France from 1793 until its abolition in 1805, and sporadically by historians ever since. Converting between it and the Gregorian calendar is a matter of arithmetic — except for one stubborn ambiguity: the leap-year rule.

The calendar's original proposer, Gilbert Romme, specified a Gregorian-style rule (every 4th year leap, skip every 100th, restore every 400th). The Republic only ever applied it for a handful of years before abolishing the calendar, so the rule was never tested against a century boundary. Later revivals disagree: some follow Romme's arithmetic rule, others tie Republican leap years to the astronomical autumn equinox as observed in Paris, which causes the two schemes to drift apart by several days over a couple of centuries.

This library implements **Romme's arithmetic rule**, applied retroactively from Year III (the first leap year under that rule). The trade-off is simplicity and determinism at the cost of astronomical fidelity: conversions for dates far from 1805 will diverge from any equinox-based almanac. Pick this library if you want a pure-function, zero-dependency converter and can tolerate that divergence; do not pick it if you need agreement with a specific modern equinox-based calendar.

## The awkward edge

A Republican year has 12 months of exactly 30 days each, plus 5 complementary "sansculottide" days (6 in leap years) at year end. These complementary days are not part of any month. This library represents them with a separate `Sansculottide` type rather than overloading `RepublicanDate` with a synthetic month 13, so callers can distinguish the two cases by `isinstance` rather than by inspecting fields. Asking for the sixth sansculottide in a common Republican year raises `ValueError`.

## Exported names

- `gregorian_to_republican(year, month, day) -> RepublicanDate | Sansculottide`
- `republican_to_gregorian(target) -> tuple[int, int, int]`
- `RepublicanDate` — frozen dataclass with `year`, `month` (1–12), `day` (1–30), and a `month_name` property.
- `Sansculottide` — frozen dataclass with `year`, `index` (1–6), and a `name` property.

Dates before 1792-09-22 raise `ValueError`. Roman-numeral year rendering is available via `callendar_vendemiary.core.roman(n)`.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

## Limitations

Values are coerced to floats, so very large integers lose precision. If you need
exact integer aggregates over a window, this is the wrong tool.

