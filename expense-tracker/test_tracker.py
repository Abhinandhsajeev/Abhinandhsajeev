from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).with_name('tracker.py')


class TrackerTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.file = Path(tmp.name) / 'expenses.csv'

    def cli(self, *args, check=True):
        return subprocess.run([sys.executable, SCRIPT, '--file', self.file, *args],
                              capture_output=True, text=True, check=check)

    def test_summary_groups_categories_and_filters_month(self):
        for amount, category, day in [('0.10', 'food, drinks', '11-01'),
                                      ('0.20', 'food, drinks', '11-30'),
                                      ('2', 'train', '11-01'), ('7', 'rent', '12-01')]:
            self.cli('add', amount, category, '--date', '2026-' + day)
        self.assertEqual(self.cli('summary', '2026-11').stdout.splitlines(),
                         ['Spending for 2026-11', 'food, drinks: EUR 0.30',
                          'train: EUR 2.00', 'Total: EUR 2.30'])

    def test_invalid_purchases_create_no_file(self):
        for args in [('1.234', 'food'), ('0', 'food'), ('5', ' '),
                     ('4', 'food', '--date', '2026-02-30')]:
            with self.subTest(args=args):
                self.assertNotEqual(self.cli('add', *args, check=False).returncode, 0)
                self.assertFalse(self.file.exists())

    def test_no_entries(self):
        self.assertIn('Total: EUR 0.00', self.cli('summary', '2026-11').stdout)

    def test_unrelated_file_untouched(self):
        self.file.write_text('keep me\n')
        self.assertNotEqual(self.cli('add', '1', 'food', check=False).returncode, 0)
        self.assertEqual(self.file.read_text(), 'keep me\n')
