import datetime
import pytest
from market_time_machine.oracle import Oracle

def test_forecast_future_date_not_allowed():
    """Oracle should forbid recording forecasts for dates beyond the current simulation date.
    The current implementation incorrectly allows it, so this test should fail.
    """
    # Simulation from 2023-01-02 to 2023-01-10 (both weekdays)
    oracle = Oracle(start="2023-01-02", end="2023-01-10")
    # Current date is start (2023-01-02). Try to record forecast for 2023-01-05 (future).
    future_date = datetime.date(2023, 1, 5)
    with pytest.raises(PermissionError):
        oracle.record_forecast(ticker="AAA", forecast_date=future_date, prediction=123)
