# Transaction Pipeline (CSV → Cleaned → SQLite)

A small, modular Python app that ingests a CSV of user transactions, cleans the data, and stores it in a SQLite database. It also provides a simple CLI for loading and summarizing data.

## Features
- Robust date parsing to ISO format (YYYY-MM-DD)
- Drops invalid rows (missing/negative amounts, bad dates, duplicates by `transaction_id`)
- SQLite schema with indices
- CLI for `init-db`, `load`, and `summary`
- Logging to stderr or a file
- Basic unit tests with `pytest`

## Install & Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
Initialize the database schema:
```bash
python -m txnproc.cli --db transactions.db init-db
```

Load a CSV (logs to stderr by default):
```bash
python -m txnproc.cli --db transactions.db load --csv path/to/transactions.csv
# or with a log file and verbose mode
python -m txnproc.cli --db transactions.db load --csv path/to/transactions.csv --log-file clean.log -v
```

Show a summary:
```bash
python -m txnproc.cli --db transactions.db summary
```

### CSV Columns
Required headers:
```
transaction_id,user_id,transaction_date,amount,category
```
- `transaction_date` may be in various human formats; it will be parsed to `YYYY-MM-DD`.
- Rows with missing/invalid/negative amounts, invalid dates, or duplicate `transaction_id` will be dropped (and logged).

## Project Layout
```
txnproc/
  __init__.py
  utils.py        # parsing helpers
  db.py           # SQLite schema, insert + summary
  clean.py        # CSV reading & cleaning
  cli.py          # argparse-based CLI
tests/
  test_clean.py   # basic unit tests
README.md
requirements.txt
```

## Tests
```bash
pytest -q
```

## Notes
- The schema uses a TEXT date column storing ISO strings for simplicity, with indices for common lookups.
- Conflicts on primary key are ignored at insert-time (reported as "skipped").
```

