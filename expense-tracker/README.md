# Expense tracker

Log a purchase in euros and get a monthly breakdown by category. Runs locally with Python 3.8+ and its standard library; no account or install required.

## Try it

From the repository root, run the following in a terminal. The example assumes a fresh log:

```console
$ cd expense-tracker
$ python3 tracker.py add 4.50 Lunch --date 2026-11-03
Added EUR 4.50 to Lunch.
$ python3 tracker.py add 3.20 Transport --date 2026-11-04
Added EUR 3.20 to Transport.
$ python3 tracker.py summary 2026-11
Spending for 2026-11
Lunch: EUR 4.50
Transport: EUR 3.20
Total: EUR 7.70
```

Omit `--date` to log a purchase for today, or run `python3 tracker.py summary` for the current month. Use the same category spelling to group purchases. Amounts are positive, with at most two decimal places, and totals are calculated in integer cents.

The program creates `expenses.csv` in the current directory. This default filename is ignored by Git so your spending stays out of commits. To use another log, put `--file PATH` before `add` or `summary`; keep personal logs outside the repository if you use a custom filename.

## Run the tests

From `expense-tracker/`, run `python3 -m unittest -v`. The tests use temporary files, not your own expense log.
