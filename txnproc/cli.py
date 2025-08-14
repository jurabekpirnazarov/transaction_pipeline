from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional

from .db import init_db, insert_transactions, summary
from .clean import read_and_clean_csv


def setup_logger(log_file: Optional[str], verbose: bool) -> logging.Logger:
    logger = logging.getLogger("txnproc")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    handler = logging.FileHandler(log_file) if log_file else logging.StreamHandler(sys.stderr)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
    handler.setFormatter(fmt)

    # Avoid duplicate handlers if run multiple times (e.g., tests)
    if not logger.handlers:
        logger.addHandler(handler)
    else:
        logger.handlers = [handler]

    return logger


def cmd_init_db(args) -> None:
    init_db(args.db)
    print(f"Initialized database at {args.db}")


def cmd_load(args) -> None:
    logger = setup_logger(args.log_file, args.verbose)
    init_db(args.db)
    rows, dropped = read_and_clean_csv(args.csv, logger=logger)
    inserted, skipped = insert_transactions(args.db, rows)
    print(f"Loaded CSV: {args.csv}")
    print(f" - cleaned rows inserted: {inserted}")
    print(f" - dropped during cleaning: {dropped}")
    print(f" - skipped at insert (PK conflicts/invalid): {skipped}")


def cmd_summary(args) -> None:
    s = summary(args.db)
    print("Summary")
    print("-------")
    print(f"Total transactions: {s['total_transactions']}")
    print("Per-category totals and averages:")
    print("category,count,total,average")
    for row in s["per_category"]:
        print(f"{row['category']},{row['count']},{row['total']},{row['average']}")
    dr = s["date_range"]
    print(f"Date range: {dr['start']} -> {dr['end']}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="txnproc", description="CSV -> cleaned data -> SQLite")
    p.add_argument("--db", required=True, help="Path to SQLite database")
    sub = p.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init-db", help="Initialize database schema")
    p_init.set_defaults(func=cmd_init_db)

    p_load = sub.add_parser("load", help="Load data from CSV into DB (with cleaning)")
    p_load.add_argument("--csv", required=True, help="Path to input CSV")
    p_load.add_argument("--log-file", help="Optional log file path")
    p_load.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    p_load.set_defaults(func=cmd_load)

    p_sum = sub.add_parser("summary", help="Show summary stats")
    p_sum.set_defaults(func=cmd_summary)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
