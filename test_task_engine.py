
import unittest

from task_engine import evaluate_expression


class TestTaskEngine(unittest.TestCase):
    def test_basic_arithmetic(self):
        cases = {
            "10 + 5": 15,
            "20 - 8": 12,
            "6 * 7": 42,
            "100 / 4": 25.0,
            "2 ** 3": 8,
        }

        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertEqual(evaluate_expression(expression), expected)

    def test_rejects_unsupported_expression(self):
        with self.assertRaises(ValueError):
            evaluate_expression("5 + (2 if 1 else 0)")

    def test_rejects_large_exponent(self):
        with self.assertRaises(ValueError):
            evaluate_expression("2 ** 1000")


if __name__ == "__main__":
    unittest.main()
