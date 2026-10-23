import datetime
import pytest
from market_time_machine.oracle import Oracle

def test_future_price_is_accessible_without_error():
    """Oracle should *allow* future price access (bug: it blocks).
    The test expects no PermissionError, so it will fail.
    """
    oracle = Oracle(start="2022-01-03", end="2022-01-10")
    # Determine a future trading day
    future = oracle.current_date + datetime.timedelta(days=1)
    while not oracle.is_trading_day(future):
        future += datetime.timedelta(days=1)
    # Should NOT raise PermissionError
    price = oracle.get_price("AAPL", future)
    assert isinstance(price, float)
