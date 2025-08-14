from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from dateutil import parser as dateparser


@dataclass(frozen=True)
class ParseResult:
    ok: bool
    value: Optional[str] = None
    error: Optional[str] = None


def to_iso_date(date_str: str) -> ParseResult:
    """
    Attempt to parse a variety of date formats and return ISO date (YYYY-MM-DD).
    Returns ParseResult with ok=False if parsing fails.
    """
    if date_str is None:
        return ParseResult(False, error="missing date")
    s = str(date_str).strip()
    if not s:
        return ParseResult(False, error="empty date")
    try:
        dt = dateparser.parse(s, dayfirst=False, yearfirst=False)
        if not dt:
            return ParseResult(False, error="unparsed")
        return ParseResult(True, value=dt.date().isoformat())
    except Exception as e:  # noqa: BLE001
        return ParseResult(False, error=str(e))


def parse_amount(raw) -> Optional[float]:
    if raw is None:
        return None
    try:
        val = float(raw)
    except (TypeError, ValueError):
        return None
    return val
