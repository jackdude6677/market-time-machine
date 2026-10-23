"""Break tests for Oracle core.

These tests expose a bug where the information firewall does not block
future price queries. The correct behavior is to raise ``PermissionError``
when a price for a date beyond ``oracle.current_date`` is requested.
"""

import datetime
import pytest

from market_time_machine.oracle import Oracle


def test_future_price_access_is_blocked():
    # Initialize a short simulation period.
    oracle = Oracle(start="2022-01-03", end="2022-01-10")  # start on Monday
    # Determine a future trading day after the current simulation date.
    future = oracle.current_date
    # advance at least one trading day forward
    while True:
        future = future + datetime.timedelta(days=1)
        if oracle.is_trading_day(future):
            break
    # The oracle should raise PermissionError for future price access.
    with pytest.raises(PermissionError):
        oracle.get_price("AAPL", future)
