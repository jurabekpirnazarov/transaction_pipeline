import io
import csv
import tempfile
from txnproc.clean import read_and_clean_csv
from txnproc.utils import to_iso_date


def make_csv(tmp_path, rows):
    path = tmp_path / "data.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["transaction_id","user_id","transaction_date","amount","category"])
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


class DummyLogger:
    def __init__(self):
        self.messages = []
    def warning(self, *args, **kwargs):
        self.messages.append(("WARNING", args[0] if args else ""))
    def info(self, *args, **kwargs):
        self.messages.append(("INFO", args[0] if args else ""))


def test_to_iso_date():
    # Accepts common formats
    assert to_iso_date("2024-01-02").ok
    assert to_iso_date("01/02/2024").ok
    assert to_iso_date("Jan 2, 2024").ok
    assert not to_iso_date("").ok


def test_read_and_clean_csv(tmp_path):
    logger = DummyLogger()
    csv_path = make_csv(tmp_path, [
        {"transaction_id":"t1","user_id":"1","transaction_date":"2024-01-02","amount":"10.5","category":"food"},
        {"transaction_id":"t2","user_id":"2","transaction_date":"02/03/2024","amount":"-3","category":"travel"}, # negative
        {"transaction_id":"t1","user_id":"1","transaction_date":"2024-01-02","amount":"10.5","category":"food"},  # duplicate
        {"transaction_id":"t3","user_id":"x","transaction_date":"2024-01-02","amount":"5","category":"misc"},     # bad user_id
        {"transaction_id":"t4","user_id":"4","transaction_date":"bad","amount":"1","category":"misc"},           # bad date
        {"transaction_id":"t5","user_id":"5","transaction_date":"2024-06-01","amount":"","category":"misc"},     # missing amount
        {"transaction_id":"t6","user_id":"6","transaction_date":"2024/06/02","amount":"7.75","category":""},     # ok, empty category
    ])
    rows, dropped = read_and_clean_csv(csv_path, logger=logger)
    # Expected kept: t1, t6
    assert len(rows) == 2
    ids = {r["transaction_id"] for r in rows}
    assert ids == {"t1", "t6"}
    assert dropped == 5
