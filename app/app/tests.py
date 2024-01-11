"""Sample Tests.
"""
from django.test import SimpleTestCase

from app import calc


class CalcTest(SimpleTestCase):
    """Test Calc module."""

    def test_add_numbers(self):
        result = calc.add(x=5, y=6)
        self.assertEqual(result, 11)

    def test_subtract_numbers(self):
        result = calc.subtract(10, 15)
        self.assertEqual(result, 5)
