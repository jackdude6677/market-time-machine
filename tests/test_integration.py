"""Integration test for live paper‑trading mode.

The test runs a short live simulation using :class:`market_time_machine.live.LivePaperTradingEngine`
with a trivial trader that always buys one share of a dummy ticker.
It verifies that the engine advances the simulation clock, records a forecast,
executes an order, and updates the portfolio cash.
"""

import datetime
import time

import pytest

from market_time_machine.live import LivePaperTradingEngine
from market_time_machine.accounting import Order


def simple_trader(oracle, current_date):
    """Trader that forecasts ``+1`` and buys one share at the current price.
    """
    price = oracle.get_price("XYZ", current_date)
    forecast = ("XYZ", 1)  # dummy prediction
    order = Order(asset="XYZ", quantity=1, price=price, sector="Tech", transaction_cost=0.0)
    return [forecast], [order]


def test_live_paper_trading_runs_and_updates():
    # Use a short date range for quick test.
    start = "2022-01-03"  # Monday
    end = "2022-01-07"    # Friday
    engine = LivePaperTradingEngine(start, end, simple_trader, tick_seconds=0.01)
    engine.start()
    # Allow a few ticks to occur.
    time.sleep(0.05)
    engine.stop()

    # At least one day should have been processed.
    assert engine.current_date() > datetime.date.fromisoformat(start)

    # There should be at least one locked decision (forecast + order).
    locked = engine.get_locked()
    assert len(locked) >= 1
    forecast, order = locked[0]
    assert forecast.ticker == "XYZ"
    assert order.asset == "XYZ"
    assert order.quantity == 1

    # Portfolio cash should have decreased by price + transaction cost.
    # Initial cash is $1000.
    portfolio_cash = engine.portfolio.cash
    # price on start day is deterministic: 100 (first trading day)
    expected_price = 100.0
    assert portfolio_cash == pytest.approx(1000.0 - expected_price)
