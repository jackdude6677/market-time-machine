"""Break tests for LivePaperTradingEngine.
These tests are expected to FAIL because the implementation has bugs:
1. The simulation does not advance beyond the start date.
2. An order that exceeds the position limit raises a ValueError in the background thread.
3. get_locked returns placeholder None entries instead of actual locked decisions.
"""

import datetime
import time
import pytest

from market_time_machine.live import LivePaperTradingEngine
from market_time_machine.accounting import Order


def simple_trader(oracle, current_date):
    """Trader that always buys one share of XYZ at the current price.
    This order will exceed the default position limit in the risk manager,
    triggering a ValueError in the live engine's background thread.
    """
    price = oracle.get_price("XYZ", current_date)
    forecast = ("XYZ", 1)
    order = Order(asset="XYZ", quantity=1, price=price, sector="Tech", transaction_cost=0.0)
    return [forecast], [order]


def test_engine_advances_date():
    """Engine should advance at least one trading day beyond the start date.
    The current implementation leaves the date unchanged, so this test fails.
    """
    start = "2022-01-03"
    end = "2022-01-07"
    engine = LivePaperTradingEngine(start, end, simple_trader, tick_seconds=0.01)
    engine.start()
    time.sleep(0.05)  # allow a few ticks
    engine.stop()
    # Expect the current date to be after the start date.
    assert engine.current_date() > datetime.date.fromisoformat(start)


def test_no_exception_on_start():
    """Starting the engine should not raise an exception.
    The background thread currently raises a ValueError due to position limits.
    """
    start = "2022-01-03"
    end = "2022-01-07"
    engine = LivePaperTradingEngine(start, end, simple_trader, tick_seconds=0.01)
    # The start method itself should not raise; any exception would be a failure.
    engine.start()
    time.sleep(0.05)
    engine.stop()
    # If the background thread raised, pytest would capture it as an unhandled thread exception.
    # No assertion needed – the test will fail if an exception occurs.


def test_locked_contains_actual_decisions():
    """get_locked should return actual locked decisions, not placeholder Nones.
    The implementation falls back to placeholders, causing this test to fail.
    """
    start = "2022-01-03"
    end = "2022-01-07"
    engine = LivePaperTradingEngine(start, end, simple_trader, tick_seconds=0.01)
    engine.start()
    time.sleep(0.05)
    engine.stop()
    locked = engine.get_locked()
    # Expect at least one non‑None entry representing a real locked decision.
    assert any(entry is not None for entry in locked)


def test_portfolio_cash_decreases_on_successful_order():
    """Portfolio cash should decrease after a successful order.
    The current implementation raises a ValueError in the background thread,
    preventing the order from being applied, so cash remains unchanged.
    This test will therefore fail.
    """
    start = "2022-01-03"
    end = "2022-01-07"
    engine = LivePaperTradingEngine(start, end, simple_trader, tick_seconds=0.01)
    initial_cash = engine.portfolio.cash
    engine.start()
    time.sleep(0.05)
    engine.stop()
    # Expect cash to be less than initial after order execution.
    assert engine.portfolio.cash < initial_cash
