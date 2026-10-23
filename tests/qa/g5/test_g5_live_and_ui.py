"""Tests for Live Paper‑Trading engine and Control UI requirements (milestones 10‑11).

The tests verify core functional behavior of the live engine (date advancement,
forecast locking, portfolio cash updates, error handling) and basic structural
requirements of the UI HTML/JS (required element IDs and data fetch).
"""

import datetime
import time
import threading
import re

import pytest

from market_time_machine.live import LivePaperTradingEngine
from market_time_machine.accounting import Order

# ---------------------------------------------------------------------------
# Helper trader used in several tests
# ---------------------------------------------------------------------------

def simple_trader(oracle, current_date):
    """Trader that records a forecast and buys one share of a dummy ticker.

    The price is obtained via ``oracle.get_price`` which should be allowed for the
    current simulation date but raise for future dates.
    """
    price = oracle.get_price("XYZ", current_date)
    forecast = ("XYZ", 1)  # dummy prediction value
    order = Order(asset="XYZ", quantity=1, price=price, sector="Tech", transaction_cost=0.0)
    return [forecast], [order]

# ---------------------------------------------------------------------------
# Live engine basic behavior
# ---------------------------------------------------------------------------

def test_live_engine_advances_and_updates_portfolio():
    start = "2022-01-03"  # Monday
    end = "2022-01-07"    # Friday
    engine = LivePaperTradingEngine(start, end, simple_trader, tick_seconds=0.01)
    engine.start()
    # Let a few ticks happen – enough for at least one step
    time.sleep(0.05)
    engine.stop()

    # The engine should have advanced beyond the start date
    assert engine.current_date() > datetime.date.fromisoformat(start)

    # At least one locked decision should be recorded
    locked = engine.get_locked()
    assert len(locked) >= 1
    forecast, order = locked[0]
    # Forecast is a ForecastRecord; check ticker attribute
    assert hasattr(forecast, "ticker") and forecast.ticker == "XYZ"
    assert isinstance(order, Order)
    assert order.asset == "XYZ"
    assert order.quantity == 1

    # Portfolio cash should have decreased by the price of the share (price on first day = 100)
    expected_price = 100.0  # deterministic dummy price series starts at 100
    assert engine.portfolio.cash == pytest.approx(1000.0 - expected_price)

def test_live_engine_future_price_access_is_blocked():
    # Create an engine but do not start it – current_date is set to one day before start
    start = "2022-01-03"
    end = "2022-01-10"
    engine = LivePaperTradingEngine(start, end, simple_trader, tick_seconds=0.1)
    # The oracle's current_date is start-1 day, so any date >= start is future
    future_date = datetime.date.fromisoformat(start)
    with pytest.raises(PermissionError):
        engine.oracle.get_price("XYZ", future_date)

def test_live_engine_start_twice_raises():
    start = "2022-01-03"
    end = "2022-01-07"
    engine = LivePaperTradingEngine(start, end, simple_trader, tick_seconds=0.1)
    engine.start()
    with pytest.raises(RuntimeError):
        engine.start()
    engine.stop()

def test_live_engine_is_running_flag_and_thread_cleanup():
    start = "2022-01-03"
    end = "2022-01-07"
    engine = LivePaperTradingEngine(start, end, simple_trader, tick_seconds=0.05)
    assert not engine.is_running()
    engine.start()
    # Give it a moment to start the thread
    time.sleep(0.02)
    assert engine.is_running()
    engine.stop()
    # After stop the thread should be joined and flag cleared
    assert not engine.is_running()

# ---------------------------------------------------------------------------
# UI structural tests (HTML & JS)
# ---------------------------------------------------------------------------

def test_ui_html_contains_required_sections():
    # Load the HTML file
    html_path = "app/index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    # Required element IDs according to the spec
    required_ids = [
        "status",
        "weekly-grades",
        "strategies",
        "relationships",
        "auditor",
        "controls",
        "capital",
        "positions",
        "grades-list",
        "strategies-list",
        "relationships-list",
        "auditor-list",
        "commands",
        "theme-toggle",
    ]
    for elem_id in required_ids:
        pattern = rf'id="{elem_id}"'
        assert re.search(pattern, html), f"Missing element with id '{elem_id}'"

def test_ui_script_fetches_demo_snapshot():
    script_path = "app/script.js"
    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()
    # The script should contain a fetch call to the demo data JSON file
    assert "fetch('data/demo_snapshot.json')" in script or "fetch(\"data/demo_snapshot.json\")" in script

