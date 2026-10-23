"""Tests for Oracle core behavior per specification.

The Oracle must enforce an information firewall: price data for dates beyond the
current simulation date should raise PermissionError. It must record forecasts,
resolve outcomes after the next trading day, and keep an audit log.
"""

import datetime
import pytest

from market_time_machine.oracle import Oracle


def test_information_firewall_future_price():
    oracle = Oracle(start="2020-01-01", end="2020-01-10")
    # Ensure future date is a trading day after current_date
    future = oracle.current_date + datetime.timedelta(days=3)
    while not oracle.is_trading_day(future):
        future += datetime.timedelta(days=1)
    # Accessing future price should raise PermissionError per spec
    with pytest.raises(PermissionError):
        oracle.get_price("AAPL", future)


def test_forecast_record_and_outcome_resolution():
    oracle = Oracle(start="2020-01-01", end="2020-01-10")
    ticker = "AAPL"
    forecast_date = oracle.current_date
    # Record a forecast for today (allowed)
    oracle.record_forecast(ticker, forecast_date, prediction="up")
    # Outcome not yet available
    with pytest.raises(ValueError):
        oracle.get_outcome(ticker, forecast_date)
    # Advance one trading day – outcome should become known
    oracle.advance_one_day()
    outcome = oracle.get_outcome(ticker, forecast_date)
    assert outcome == 1.0


def test_audit_log_contains_recorded_forecast():
    oracle = Oracle(start="2020-01-01", end="2020-01-10")
    oracle.record_forecast("MSFT", oracle.current_date, prediction="down")
    logs = oracle.audit_log()
    assert any(rec.ticker == "MSFT" for rec in logs)
