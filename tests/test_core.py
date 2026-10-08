import unittest

from callendar_vendemiary import (
    RepublicanDate,
    Sansculottide,
    gregorian_to_republican,
    republican_to_gregorian,
)
from callendar_vendemiary.core import roman, _republican_leap


class EpochTests(unittest.TestCase):
    def test_epoch_maps_to_vendemiaire_1_year_i(self):
        r = gregorian_to_republican(1792, 9, 22)
        self.assertIsInstance(r, RepublicanDate)
        self.assertEqual(r, RepublicanDate(year=1, month=1, day=1))

    def test_day_before_epoch_raises(self):
        with self.assertRaises(ValueError):
            gregorian_to_republican(1792, 9, 21)

    def test_round_trip_epoch(self):
        r = gregorian_to_republican(1792, 9, 22)
        self.assertEqual(republican_to_gregorian(r), (1792, 9, 22))


class RoundTripTests(unittest.TestCase):
    def test_round_trip_famous_bastille(self):
        # 14 July 1789 predates the calendar, so out of range.
        with self.assertRaises(ValueError):
            gregorian_to_republican(1789, 7, 14)

    def test_round_trip_first_brumaire_known_equation(self):
        # 22 Vendemiaire Year II == 13 October 1793.
        r = gregorian_to_republican(1793, 10, 13)
        self.assertEqual(r, RepublicanDate(year=2, month=1, day=22))
        self.assertEqual(republican_to_gregorian(r), (1793, 10, 13))

    def test_round_trip_last_day_of_year_i(self):
        # Year I ends on 21 September 1793 Gregorian — the 5th sansculottide.
        r = gregorian_to_republican(1793, 9, 21)
        self.assertIsInstance(r, Sansculottide)
        self.assertEqual(r, Sansculottide(year=1, index=5))
        self.assertEqual(republican_to_gregorian(r), (1793, 9, 21))

    def test_round_trip_year_iii_leap_sansculottide_six(self):
        # Year III is leap under the arithmetic rule; the 6th sansculottide
        # corresponds to 22 September 1795 Gregorian (a Tuesday).
        r = gregorian_to_republican(1795, 9, 22)
        self.assertIsInstance(r, Sansculottide)
        self.assertEqual(r, Sansculottide(year=3, index=6))
        self.assertEqual(republican_to_gregorian(r), (1795, 9, 22))

    def test_round_trip_last_day_of_leap_year_three(self):
        # The day AFTER the 6th sansculottide of Year III is 1 Vendemiaire IV.
        r = gregorian_to_republican(1795, 9, 23)
        self.assertEqual(r, RepublicanDate(year=4, month=1, day=1))

    def test_round_trip_arbitrary_modern_date(self):
        # 1 Vendemiaire CCXX (year 220) under the arithmetic rule.
        # Year 220 started on the Gregorian day that the arithmetic rule
        # predicts; we assert internal consistency rather than a fixed
        # Gregorian figure to avoid coupling the test to the exact leap drift.
        r = gregorian_to_republican(2011, 9, 23)
        # We don't hardcode the Republican year here because the drift
        # between the arithmetic rule and astronomical autumn equinox is
        # exactly the kind of ambiguity this library declines to resolve.
        # We do assert that the conversion round-trips.
        g = republican_to_gregorian(r)
        self.assertEqual(g, (2011, 9, 23))


class MonthNameTests(unittest.TestCase):
    def test_month_name_and_str(self):
        r = RepublicanDate(year=1, month=1, day=1)
        self.assertEqual(r.month_name, "Vendemiaire")
        self.assertIn("Vendemiaire", str(r))
        self.assertIn("I", str(r))

    def test_sansculottide_name_and_str(self):
        s = Sansculottide(year=3, index=6)
        self.assertEqual(s.name, "Revolution")
        self.assertIn("Revolution", str(s))
        self.assertIn("III", str(s))


class LeapTests(unittest.TestCase):
    def test_year_one_not_leap(self):
        self.assertFalse(_republican_leap(1))

    def test_year_three_leap(self):
        self.assertTrue(_republican_leap(3))

    def test_year_two_hundred_not_leap(self):
        # 200 is divisible by 4 and 100 but not 400 — not leap.
        self.assertFalse(_republican_leap(200))

    def test_year_four_hundred_leap(self):
        # Year 403 sits at offset 400 from the Year III anchor: divisible
        # by 400, so leap despite being a century boundary.
        self.assertTrue(_republican_leap(403))

    def test_sixth_sansculottide_rejected_in_common_year(self):
        with self.assertRaises(ValueError):
            Sansculottide(year=1, index=6)

    def test_sixth_sansculottide_allowed_in_leap_year(self):
        Sansculottide(year=3, index=6)  # must not raise


class ValidationTests(unittest.TestCase):
    def test_invalid_month(self):
        with self.assertRaises(ValueError):
            RepublicanDate(year=1, month=13, day=1)

    def test_invalid_day(self):
        with self.assertRaises(ValueError):
            RepublicanDate(year=1, month=1, day=31)

    def test_invalid_year(self):
        with self.assertRaises(ValueError):
            RepublicanDate(year=0, month=1, day=1)

    def test_sans_index_out_of_range(self):
        with self.assertRaises(ValueError):
            Sansculottide(year=1, index=0)
        with self.assertRaises(ValueError):
            Sansculottide(year=1, index=7)


class RomanTests(unittest.TestCase):
    def test_simple_values(self):
        self.assertEqual(roman(1), "I")
        self.assertEqual(roman(4), "IV")
        self.assertEqual(roman(9), "IX")
        self.assertEqual(roman(40), "XL")
        self.assertEqual(roman(90), "XC")
        self.assertEqual(roman(400), "CD")
        self.assertEqual(roman(900), "CM")

    def test_year_three(self):
        self.assertEqual(roman(3), "III")

    def test_rejects_zero(self):
        with self.assertRaises(ValueError):
            roman(0)


class EndOfMonthBoundaryTests(unittest.TestCase):
    def test_day_30_of_last_month_then_sansculottide(self):
        # 30 Fructidor Year I == 16 September 1793 — the last day of the
        # twelfth month, the day before the sansculottides begin.
        r = gregorian_to_republican(1793, 9, 16)
        self.assertEqual(r, RepublicanDate(year=1, month=12, day=30))
        self.assertEqual(republican_to_gregorian(r), (1793, 9, 16))

    def test_first_sansculottide(self):
        r = gregorian_to_republican(1793, 9, 17)
        self.assertEqual(r, Sansculottide(year=1, index=1))


class MonthLengthUniformityTests(unittest.TestCase):
    def test_every_month_has_thirty_days(self):
        # Pick the 30th of every month in Year I and confirm the next day is
        # the 1st of the next month (or sansculottide for month 12).
        for m in range(1, 13):
            r = RepublicanDate(year=1, month=m, day=30)
            g = republican_to_gregorian(r)
            r_next = gregorian_to_republican(*g)
            # move one Gregorian day forward
            import datetime as _dt
            g2 = (_dt.date(*g) + _dt.timedelta(days=1)).timetuple()[:3]
            r_after = gregorian_to_republican(*g2)
            if m < 12:
                self.assertEqual(
                    r_after,
                    RepublicanDate(year=1, month=m + 1, day=1),
                    f"month {m} boundary",
                )
            else:
                self.assertEqual(
                    r_after,
                    Sansculottide(year=1, index=1),
                    "month 12 boundary",
                )


if __name__ == "__main__":
    unittest.main()
