"""Break tests for the live paper‑trading engine.

The engine should advance the simulation clock by exactly one trading day
per iteration and deduct cash only for the trades that actually occur.
Because the current implementation calls ``oracle.advance_one_day`` twice
per loop, the date jumps two days while only one forecast is locked, and
cash is deducted more than once per day.  Both assertions below therefore
fail.
"""

import datetime
import time

import pytest

from market_time_machine.live import LivePaperTradingEngine
from market_time_machine.accounting import Order


def simple_trader(oracle, current_date):
    """Trader that always buys one share of a dummy ticker."""
    price = oracle.get_price("XYZ", current_date)
    order = Order(asset="XYZ", quantity=1, price=price, sector="Tech", transaction_cost=0.0)
    # No forecasts needed for this test.
    return [], [order]


def test_live_engine_advances_one_day_per_locked_decision():
    start = "2022-01-03"  # Monday
    end = "2022-01-07"    # Friday
    engine = LivePaperTradingEngine(start, end, simple_trader, tick_seconds=0.02)
    engine.start()
    # Let the loop run a few ticks.
    time.sleep(0.07)
    engine.stop()

    # Number of trading days that have actually passed.
    days_advanced = 0
    cur = datetime.date.fromisoformat(start)
    while cur < engine.current_date():
        cur = cur + datetime.timedelta(days=1)
        if cur.weekday() < 5:
            days_advanced += 1

    locked = engine.get_locked()
    # Expected: one locked decision per day advanced.
    assert days_advanced == len(locked), (
        f"Engine advanced {days_advanced} trading days but only {len(locked)} decisions were locked"
    )


def test_live_engine_cash_is_deducted_once_per_trade():
    start = "2022-01-03"
    end = "2022-01-07"
    engine = LivePaperTradingEngine(start, end, simple_trader, tick_seconds=0.02)
    engine.start()
    time.sleep(0.07)
    engine.stop()

    # Expected cash after N trades = initial cash – N * price_of_XYZ_on_start
    # Price on the start day is deterministic: 100.0
    expected_price = 100.0
    locked = engine.get_locked()
    expected_cash = 1000.0 - expected_price * len(locked)
    assert engine.portfolio.cash == pytest.approx(expected_cash), (
        f"Cash {engine.portfolio.cash} does not match expected {expected_cash} after {len(locked)} trades"
    )

