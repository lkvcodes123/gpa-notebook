import unittest
from app import calculate

class CalculatorTests(unittest.TestCase):
    def course(self, grade, credits=5, level='Regular'):
        return dict(grade=grade, credits=credits, level=level)

    def test_screenshot(self):
        courses = [self.course(g, level='AP / IB' if i < 5 else 'Regular')
                   for i, g in enumerate(['A+', 'A-', 'C+', 'B', 'A+', 'A-', 'A+', 'A+'])]
        r = calculate({'semesters': [{'weighted': True, 'courses': courses}]})
        self.assertAlmostEqual(r['gpa'], 4.2125)
        self.assertAlmostEqual(r['unweighted'], 3.5875)

    def test_credits_and_cumulative(self):
        r = calculate({'semesters': [
            {'weighted': True, 'courses': [self.course('A', 3, 'Honors')]},
            {'weighted': False, 'courses': [self.course('B', 1, 'AP / IB')]}]})
        self.assertEqual(r['gpa'], 4.125)
        self.assertEqual(r['unweighted'], 3.75)

    def test_exclusions_and_fail(self):
        r = calculate({'semesters': [{'weighted': True, 'courses': [
            self.course('P'), self.course('W'), self.course('I'), self.course(''),
            self.course('F', 2, 'AP / IB')]}]})
        self.assertEqual(r['gpa'], 0)
        self.assertEqual(r['credits'], 2)
        self.assertIsNone(calculate({'semesters': []})['gpa'])

    def test_invalid_credits(self):
        for value in [-1, '', 'nan', 'inf']:
            with self.assertRaises(ValueError):
                calculate({'semesters': [{'courses': [self.course('A', value)]}]})

if __name__ == '__main__':
    unittest.main()
