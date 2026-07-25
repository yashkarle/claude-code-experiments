"""Tests for tracker.rules using a throwaway SQLite db."""

import itertools
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Point the db module at a temp file before importing anything that uses it.
import tracker.db as db  # noqa: E402

_tmpdir = tempfile.mkdtemp()
db.DB_PATH = os.path.join(_tmpdir, "test.db")

from tracker.rules import evaluate, should_send  # noqa: E402

_url_counter = itertools.count()


def setup_product(target_price=None, drop_pct=None):
    db.init_db()
    url = f"https://example.com/p{next(_url_counter)}"
    pid = db.add_product(url, "Test Product", "EUR", target_price, drop_pct)
    return pid


def iso_days_ago(days):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def test_target_price_fires():
    pid = setup_product(target_price=100.0)
    row_id = db.record_price(pid, 120.0, checked_at=iso_days_ago(1))
    fired = evaluate(db.get_product(pid), row_id, 120.0)
    assert not any(f.rule == "target_price" for f in fired)

    row_id2 = db.record_price(pid, 95.0, checked_at=iso_days_ago(0))
    fired2 = evaluate(db.get_product(pid), row_id2, 95.0)
    assert any(f.rule == "target_price" for f in fired2)


def test_drop_pct_fires_on_big_drop():
    pid = setup_product(drop_pct=10)
    r1 = db.record_price(pid, 100.0, checked_at=iso_days_ago(2))
    evaluate(db.get_product(pid), r1, 100.0)

    r2 = db.record_price(pid, 85.0, checked_at=iso_days_ago(0))  # 15% drop
    fired = evaluate(db.get_product(pid), r2, 85.0)
    assert any(f.rule == "drop_pct" for f in fired)


def test_drop_pct_does_not_fire_on_small_drop():
    pid = setup_product(drop_pct=10)
    r1 = db.record_price(pid, 100.0, checked_at=iso_days_ago(2))
    evaluate(db.get_product(pid), r1, 100.0)

    r2 = db.record_price(pid, 97.0, checked_at=iso_days_ago(0))  # 3% drop
    fired = evaluate(db.get_product(pid), r2, 97.0)
    assert not any(f.rule == "drop_pct" for f in fired)


def test_historical_low_requires_enough_history():
    pid = setup_product()
    # History spans less than 30 days -> rule should not fire even on a new low.
    r1 = db.record_price(pid, 100.0, checked_at=iso_days_ago(5))
    r2 = db.record_price(pid, 50.0, checked_at=iso_days_ago(0))
    fired = evaluate(db.get_product(pid), r2, 50.0)
    assert not any(f.rule == "historical_low" for f in fired)


def test_historical_low_fires_with_enough_history():
    pid = setup_product()
    db.record_price(pid, 150.0, checked_at=iso_days_ago(80))
    db.record_price(pid, 120.0, checked_at=iso_days_ago(40))
    r3 = db.record_price(pid, 110.0, checked_at=iso_days_ago(0))
    fired = evaluate(db.get_product(pid), r3, 110.0)
    assert any(f.rule == "historical_low" for f in fired)


def test_should_send_dedupes_same_price():
    pid = setup_product(target_price=100.0)
    r1 = db.record_price(pid, 90.0, checked_at=iso_days_ago(1))
    fired1 = evaluate(db.get_product(pid), r1, 90.0)
    target_rule = next(f for f in fired1 if f.rule == "target_price")
    assert should_send(pid, target_rule) is True
    db.record_alert(pid, target_rule.rule, 90.0)

    # Same price again on next check -> should NOT re-send.
    r2 = db.record_price(pid, 90.0, checked_at=iso_days_ago(0))
    fired2 = evaluate(db.get_product(pid), r2, 90.0)
    target_rule2 = next(f for f in fired2 if f.rule == "target_price")
    assert should_send(pid, target_rule2) is False


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"PASS {t.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
