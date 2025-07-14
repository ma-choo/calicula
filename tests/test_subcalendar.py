# test_subcalendar.py

import unittest
from subcalendar import Assignment, Subcalendar

class TestAssignment(unittest.TestCase):
    def test_creation(self):
        a = Assignment("Test", "20250714", False, studytime=30)
        self.assertEqual(a.name, "Test")
        self.assertEqual(a.date.strftime("%Y%m%d"), "20250714")
        self.assertEqual(a.studytime, 30)
        self.assertFalse(a.completed)

    def test_toggle_completion(self):
        a = Assignment("Toggle", "20250714", False)
        a.toggle_completion()
        self.assertTrue(a.completed)

    def test_rename(self):
        a = Assignment("Old", "20250714", False)
        a.rename("New")
        self.assertEqual(a.name, "New")

class TestSubcalendar(unittest.TestCase):
    # test assignments are ordered by date
    def test_insert_and_order(self):
        cal = Subcalendar("Test")
        a1 = Assignment("A", "20250715", False)
        a2 = Assignment("B", "20250714", False)
        cal.insert_assignment(a1)
        cal.insert_assignment(a2)
        self.assertEqual(cal.assignments[0].name, "B")

    def test_toggle_hidden(self):
        cal = Subcalendar("Test")
        self.assertFalse(cal.hidden)
        cal.toggle_hidden()
        self.assertTrue(cal.hidden)
