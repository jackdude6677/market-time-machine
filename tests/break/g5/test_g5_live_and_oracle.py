"""Breaker tests for Market Time Machine.

These tests expose real bugs in the live paper‑trading engine and the
Oracle's forecast recording logic.
"""

import datetime
import time
import pytest

from market_time_machine.live import LivePaperTradingEngine
from market_time_machine.oracle import Oracle, ForecastRecord
from market_time_machine.accounting import Order

# Helper trader that does nothing (no forecasts, no orders)
def idle_trader(oracle, current_date):
    return [], []


def test_live_engine_multiple_ticks_expected():
    """LivePaperTradingEngine should advance the simulation for each tick.

    The engine is supposed to run continuously, advancing one trading day
    per ``tick_seconds``. The current implementation only performs a single
    step, so the date will not move far enough.
    """
    start = "2022-01-03"  # Monday
    end = "2022-01-10"    # Next Monday
    engine = LivePaperTradingEngine(start, end, idle_trader, tick_seconds=0.01)
    engine.start()
    # Sleep long enough for several ticks to occur if the engine looped.
    time.sleep(0.2)
    engine.stop()
    # Expect at least three days have been processed.
    expected_min_date = datetime.date.fromisoformat(start) + datetime.timedelta(days=3)
    assert engine.current_date() >= expected_min_date, "Engine did not process multiple ticks"


def test_oracle_prevents_future_forecast():
    """Oracle.record_forecast must reject forecasts for dates beyond the current simulation date.

    The current implementation allows future dates up to the simulation end,
    which creates a look‑ahead leakage bug.
    """
    start = "2022-01-03"
    end = "2022-01-07"
    oracle = Oracle(start, end)
    # Current date is the start date (2022‑01‑03). Try to record a forecast for two days ahead.
    future_date = datetime.date.fromisoformat(start) + datetime.timedelta(days=2)
    with pytest.raises(PermissionError):
        oracle.record_forecast("XYZ", future_date, prediction=1)


def test_live_engine_start_twice_raises():
    """Calling ``start`` on a running LivePaperTradingEngine should raise RuntimeError.

    The engine currently clears the thread flag after the first run finishes,
    allowing a second ``start`` without error. This test expects the proper
    guard to be in place.
    """
    start = "2022-01-03"
    end = "2022-01-07"
    engine = LivePaperTradingEngine(start, end, idle_trader, tick_seconds=0.01)
    engine.start()
    # Immediately attempt to start again while the first thread may still be alive.
    with pytest.raises(RuntimeError):
        engine.start()
    engine.stop()
