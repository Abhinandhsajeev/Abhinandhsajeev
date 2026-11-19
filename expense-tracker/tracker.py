"""A small, local-only EUR expense log."""

import argparse
import csv
from datetime import date
from pathlib import Path
import re

HEADER = ['date', 'category', 'amount_eur']


def cents(value):
    if not re.fullmatch(r'[0-9]+(?:\.[0-9]{1,2})?', value):
        raise ValueError('amount must look like 4 or 4.50')
    euros, _, fraction = value.partition('.')
    total = int(euros) * 100 + int(fraction.ljust(2, '0'))
    if total == 0:
        raise ValueError('amount must be greater than zero')
    return total


def money(total):
    return f'{total // 100}.{total % 100:02d}'


def day(value):
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError('use YYYY-MM-DD for dates')
    return value


def entries(path):
    if not path.exists():
        return
    with path.open(newline='', encoding='utf-8') as source:
        rows = csv.reader(source, strict=True)
        if next(rows, None) != HEADER:
            raise ValueError('unexpected CSV header')
        for when, category, amount in rows:
            if not category.strip():
                raise ValueError('category cannot be blank')
            yield day(when), category, cents(amount)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', type=Path, default=Path('expenses.csv'))
    commands = parser.add_subparsers(dest='command', required=True)
    add = commands.add_parser('add', help='record a purchase')
    add.add_argument('amount')
    add.add_argument('category')
    add.add_argument('--date', default=date.today().isoformat())
    summary = commands.add_parser('summary', help='show spending by category')
    summary.add_argument('month', nargs='?', default=date.today().isoformat()[:7])
    args = parser.parse_args()

    try:
        if args.command == 'add':
            amount = money(cents(args.amount))
            category = args.category.strip()
            if not category:
                raise ValueError('category cannot be blank')
            when = day(args.date)
            # Refuse to append to an unrelated or damaged CSV.
            for _ in entries(args.file):
                pass
            new = not args.file.exists()
            with args.file.open('a', newline='', encoding='utf-8') as dest:
                writer = csv.writer(dest)
                if new:
                    writer.writerow(HEADER)
                writer.writerow([when, category, amount])
            print(f'Added EUR {amount} to {category}.')
        else:
            day(args.month + '-01')
            totals = {}
            for when, category, amount in entries(args.file):
                if when[:7] == args.month:
                    totals[category] = totals.get(category, 0) + amount
            print(f'Spending for {args.month}')
            for category in sorted(totals):
                print(f'{category}: EUR {money(totals[category])}')
            print(f'Total: EUR {money(sum(totals.values()))}')
    except (OSError, ValueError, csv.Error) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
