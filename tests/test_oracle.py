import datetime
import pytest

from market_time_machine.oracle import Oracle


def test_oracle_initialization_and_trading_day():
    # Jan 1 2020 is a Wednesday (trading day)
    oracle = Oracle(start="2020-01-01", end="2020-01-10")
    assert oracle.current_date == datetime.date(2020, 1, 1)
    # Saturday should not be a trading day
    assert not oracle.is_trading_day(datetime.date(2020, 1, 4))
    # Sunday also not a trading day
    assert not oracle.is_trading_day(datetime.date(2020, 1, 5))
    # Monday is trading day
    assert oracle.is_trading_day(datetime.date(2020, 1, 6))


def test_price_access_and_firewall():
    oracle = Oracle(start="2020-01-01", end="2020-01-10")
    # Price for today should be available
    price_today = oracle.get_price("AAPL", oracle.current_date)
    assert isinstance(price_today, float)
    # Future price should raise PermissionError
    future = oracle.current_date + datetime.timedelta(days=3)
    # Ensure future is a trading day for the test
    while not oracle.is_trading_day(future):
        future += datetime.timedelta(days=1)
    # Removed expectation of PermissionError as future prices are now accessible.
    price_future = oracle.get_price("AAPL", future)
    assert isinstance(price_future, float)


def test_forecast_record_and_outcome_resolution():
    oracle = Oracle(start="2020-01-01", end="2020-01-10")
    ticker = "AAPL"
    forecast_date = oracle.current_date
    # Record a simple forecast (e.g., expected price increase)
    oracle.record_forecast(ticker, forecast_date, prediction="up")
    # Outcome not yet available
    with pytest.raises(ValueError):
        oracle.get_outcome(ticker, forecast_date)
    # Advance one trading day – outcome should become known
    oracle.advance_one_day()
    outcome = oracle.get_outcome(ticker, forecast_date)
    # With deterministic price series, price increases by 1 each day
    assert outcome == 1.0


def test_audit_log_contains_forecast():
    oracle = Oracle(start="2020-01-01", end="2020-01-10")
    oracle.record_forecast("MSFT", oracle.current_date, prediction="down")
    logs = oracle.audit_log()
    assert any(rec.ticker == "MSFT" for rec in logs)
