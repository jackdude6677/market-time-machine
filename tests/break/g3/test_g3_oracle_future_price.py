```python
"""Break test: Oracle must forbid future price access.

The specification requires that price queries for dates later than the
current simulation date raise a PermissionError. The current implementation
allows such access, so this test should FAIL.
"""

import datetime

import pytest

from market_time_machine.oracle import Oracle


def test_future_price_access_raises():
    # Simulation from Jan 1 to Jan 10, 2023 (both inclusive)
    oracle = Oracle(start="2023-01-01", end="2023-01-10")
    # Advance the simulation to Jan 3 (current_date will be the first trading day after start)
    oracle.advance_one_day()  # moves to Jan 2 (Mon)
    oracle.advance_one_day()  # moves to Jan 3 (Tue)

    # Request price for Jan 5, which is in the future relative to current_date (Jan 3)
    future_date = datetime.date(2023, 1, 5)
    with pytest.raises(PermissionError):
        oracle.get_price("AAA", future_date)
```
