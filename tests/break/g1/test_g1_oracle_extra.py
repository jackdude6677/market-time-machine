import datetime
import pytest
from market_time_machine.oracle import Oracle

def test_get_price_future_blocked():
    """Oracle should not allow retrieving price for dates beyond current simulation date."""
    oracle = Oracle(start="2023-01-02", end="2023-01-10")
    # current_date is 2023-01-02
    future = datetime.date(2023, 1, 5)
    with pytest.raises(PermissionError):
        oracle.get_price(ticker="AAA", date=future)

def test_record_forecast_before_start_not_allowed():
    """Recording a forecast for a date before simulation start should raise ValueError."""
    oracle = Oracle(start="2023-01-02", end="2023-01-10")
    past = datetime.date(2022, 12, 30)
    with pytest.raises(ValueError):
        oracle.record_forecast(ticker="AAA", forecast_date=past, prediction=123)
