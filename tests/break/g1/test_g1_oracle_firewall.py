import datetime
import pytest
from market_time_machine.oracle import Oracle

def test_future_price_access_is_blocked():
    """Oracle should raise PermissionError when accessing a future price.
    The current implementation allows it, so this test will fail.
    """
    oracle = Oracle(start="2022-01-03", end="2022-01-10")  # Monday to next Monday
    # Ensure future date is a trading day after current_date
    future = oracle.current_date + datetime.timedelta(days=1)
    while not oracle.is_trading_day(future):
        future += datetime.timedelta(days=1)
    with pytest.raises(PermissionError):
        oracle.get_price("AAPL", future)
