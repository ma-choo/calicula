# test_utils.py

import unittest
from utils import contains_bad_chars, zeller, get_days_in_month

class TestUtils(unittest.TestCase):
    def test_contains_bad_chars(self):
        self.assertTrue(contains_bad_chars("bad,name"))
        self.assertTrue(contains_bad_chars("bad<name"))
        self.assertTrue(contains_bad_chars("bad>name"))
        self.assertTrue(contains_bad_chars("bad:name"))
        self.assertTrue(contains_bad_chars("bad\"name"))
        self.assertTrue(contains_bad_chars("bad/name"))
        self.assertTrue(contains_bad_chars("bad\\name"))
        self.assertTrue(contains_bad_chars("bad|name"))
        self.assertFalse(contains_bad_chars("good name"))

    def test_zeller_offset(self):
        self.assertEqual(zeller(6, 2024), 1) # this month on this year should have an offset of 1

    def test_days_in_month(self):
        # check september, april, june, november have 30 days
        for month in [3, 5, 8, 10]:  # note: zero-based months
            self.assertEqual(get_days_in_month(month, 2023), 30)

        # check all the rest have 31
        for month in [0, 2, 4, 6, 7, 9, 11]:
            self.assertEqual(get_days_in_month(month, 2023), 31)

        self.assertEqual(get_days_in_month(1, 2025), 28)  # check february has 28 days on a non leap year

        self.assertEqual(get_days_in_month(1, 2024), 29)  # 29 days on a leap year