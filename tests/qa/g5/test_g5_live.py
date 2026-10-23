"""Tests for Live Paper‑Trading Transition (milestone 10).

These tests verify that the live engine:
- advances the simulation clock,
- records forecasts and orders,
- updates portfolio cash,
- isolates its Oracle from future‑date forecast attempts,
- provides a stable `is_running` flag and `get_locked` placeholders,
- does not interfere with a separate historical TradingEngine instance.
"""

import datetime
import time

import pytest

from market_time_machine.live import LivePaperTradingEngine
from market_time_machine.accounting import Order, Portfolio
from market_time_machine.oracle import Oracle


def trader_simple(oracle, current_date):
    """Trader that forecasts the current date and buys one share."""
    price = oracle.get_price("XYZ", current_date)
    forecast = ("XYZ", 1)  # dummy prediction
    order = Order(asset="XYZ", quantity=1, price=price, sector="Tech", transaction_cost=0.0)
    return [forecast], [order]


def trader_future_forecast(oracle, current_date):
    """Trader that attempts to forecast a future date (should raise)."""
    future = current_date + datetime.timedelta(days=5)
    # This forecast will be passed to TradingEngine which will call
    # Oracle.record_forecast with `forecast_date == current_date`,
    # so we need to raise manually to simulate a misuse.
    # We'll directly call Oracle.record_forecast to trigger the error.
    oracle.record_forecast("XYZ", future, prediction=1)
    return [], []


def test_live_engine_advances_and_updates_portfolio():
    start = "2022-01-03"  # Monday
    end = "2022-01-07"    # Friday
    engine = LivePaperTradingEngine(start, end, trader_simple, tick_seconds=0.01)
    engine.start()
    time.sleep(0.05)   # allow several ticks
    engine.stop()

    # The engine must have advanced at least one day.
    assert engine.current_date() > datetime.date.fromisoformat(start)

    # At least one locked decision should be present.
    locked = engine.get_locked()
    assert len(locked) >= 1
    forecast, order = locked[0]
    assert forecast.ticker == "XYZ"
    assert order.asset == "XYZ"
    assert order.quantity == 1

    # Portfolio cash should have decreased by the price of one share.
    # Deterministic price series: first trading day price = 100.
    expected_price = 100.0
    assert engine.portfolio.cash == pytest.approx(1000.0 - expected_price)


def test_live_engine_future_forecast_is_blocked():
    start = "2022-01-03"
    end = "2022-01-05"
    engine = LivePaperTradingEngine(start, end, trader_future_forecast, tick_seconds=0.01)

    # The engine should raise PermissionError when the trader tries to record a future forecast.
    with pytest.raises(PermissionError):
        engine._engine.step()  # invoke a single step manually


def test_live_engine_is_running_flag_and_locked_placeholders():
    start = "2022-01-03"
    end = "2022-01-04"
    engine = LivePaperTradingEngine(start, end, trader_simple, tick_seconds=0.5)

    # Before start, engine is not running.
    assert not engine.is_running()

    engine.start()
    time.sleep(0.1)
    # Engine should be running while the thread is alive.
    assert engine.is_running()

    # Stop the engine and ensure flag flips.
    engine.stop()
    assert not engine.is_running()

    # get_locked should return a list whose length matches steps executed.
    steps = len(engine.get_locked())
    assert steps >= 1
    # All entries should be tuples (forecast, order) or None placeholders.
    for entry in engine.get_locked():
        assert isinstance(entry, tuple) or entry is None


def test_live_and_historical_isolation():
    """Create a live engine and a historical TradingEngine and ensure they keep
    separate portfolios and Oracles."""
    # Live engine
    live = LivePaperTradingEngine("2022-01-03", "2022-01-05", trader_simple, tick_seconds=0.01)
    live.start()
    time.sleep(0.03)
    live.stop()

    # Historical engine (direct TradingEngine)
    oracle = Oracle("2022-01-03", "2022-01-05")
    portfolio = Portfolio()
    from market_time_machine.trading_engine import TradingEngine
    hist_engine = TradingEngine(oracle, portfolio, trader_simple)

    # Run two steps manually.
    hist_engine.step()
    hist_engine.step()

    # Portfolios should differ (different cash consumption due to separate runs).
    assert live.portfolio.cash != portfolio.cash
    # Oracles should have independent current dates.
    assert live.current_date() != oracle.current_date
