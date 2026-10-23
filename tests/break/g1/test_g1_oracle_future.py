"""Break test for Oracle future price access.

The specification requires that requesting a price for a date beyond the
current simulation date raises ``PermissionError`` to enforce the information
firewall. The current implementation mistakenly allows such access, so this
test should fail.
"""

import datetime
import pytest

from market_time_machine.oracle import Oracle


def test_future_price_access_prohibited():
    # Initialise Oracle with a short simulation window.
    oracle = Oracle(start="2022-01-03", end="2022-01-10")
    # The oracle's current_date is the start date (2022-01-03).
    # Choose a future date that is after the current_date but within the
    # simulation bounds.
    future_date = datetime.date(2022, 1, 5)
    # Expect a PermissionError because the price is not yet available.
    with pytest.raises(PermissionError):
        oracle.get_price(ticker="AAPL", date=future_date)
