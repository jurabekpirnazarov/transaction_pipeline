from __future__ import annotations

import csv
from typing import Dict, Iterable, List, Tuple, Set

from .utils import to_iso_date, parse_amount


def read_and_clean_csv(csv_path: str, logger) -> Tuple[List[Dict[str, object]], int]:
    """
    Read a CSV and return (clean_rows, dropped_count).
    Cleaning rules:
      - Standardize transaction_date to ISO (YYYY-MM-DD)
      - Remove rows with null/negative amounts
      - Remove rows with invalid dates (logged)
      - Remove duplicate transactions (by transaction_id)
    """
    clean_rows: List[Dict[str, object]] = []
    seen: Set[str] = set()
    dropped = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"transaction_id", "user_id", "transaction_date", "amount", "category"}
        if not required.issubset(reader.fieldnames or set()):
            missing = required - set(reader.fieldnames or [])
            raise ValueError(f"CSV missing required columns: {sorted(missing)}")

        for i, row in enumerate(reader, start=2):  # header is line 1
            txid = (row.get("transaction_id") or "").strip()
            if not txid:
                logger.warning("Row %d: missing transaction_id; dropped", i)
                dropped += 1
                continue
            if txid in seen:
                logger.info("Row %d: duplicate transaction_id=%s; dropped", i, txid)
                dropped += 1
                continue

            # Date
            date_raw = row.get("transaction_date")
            date_parsed = to_iso_date(date_raw)
            if not date_parsed.ok:
                logger.warning("Row %d: invalid date '%s' (%s); dropped", i, date_raw, date_parsed.error)
                dropped += 1
                continue

            # Amount
            amount = parse_amount(row.get("amount"))
            if amount is None:
                logger.warning("Row %d: missing/invalid amount; dropped", i)
                dropped += 1
                continue
            if amount < 0:
                logger.info("Row %d: negative amount %s; dropped", i, amount)
                dropped += 1
                continue

            # user_id
            try:
                user_id = int(str(row.get("user_id")).strip())
            except Exception:
                logger.warning("Row %d: invalid user_id '%s'; dropped", i, row.get("user_id"))
                dropped += 1
                continue

            clean_rows.append(
                {
                    "transaction_id": txid,
                    "user_id": user_id,
                    "transaction_date": date_parsed.value,
                    "amount": amount,
                    "category": (row.get("category") or "").strip() or None,
                }
            )
            seen.add(txid)

    return clean_rows, dropped
