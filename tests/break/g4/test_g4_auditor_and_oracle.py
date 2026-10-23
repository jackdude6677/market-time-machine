"""Breaker tests for Auditor and Oracle future price firewall.

These tests are expected to FAIL because the current implementation of
`market_time_machine.oracle.Oracle.get_price` allows access to future dates,
while the specification (and the original test suite) requires a
`PermissionError` to be raised.  The `Auditor` class relies on this behavior
to detect a leak; it records a violation when the price is accessible.
"""

import datetime
import pytest

from market_time_machine.oracle import Oracle
from market_time_machine.auditor import Auditor


def test_oracle_future_price_raises_permission_error():
    """Oracle should raise PermissionError for future price access.

    The test deliberately requests a price for a date after the current
    simulation date.  The correct behaviour is to raise ``PermissionError``.
    The current implementation returns a price, so this test will fail.
    """
    oracle = Oracle(start="2020-01-01", end="2020-01-10")
    # Determine a future trading day (at least two days ahead)
    future = oracle.current_date + datetime.timedelta(days=3)
    while not oracle.is_trading_day(future):
        future += datetime.timedelta(days=1)
    with pytest.raises(PermissionError):
        oracle.get_price("FAKE", future)


def test_auditor_detects_future_price_leak():
    """Auditor should report a violation when future price is accessible.

    The auditor's ``check_future_price_leak`` method records a violation if
    ``oracle.get_price`` does *not* raise ``PermissionError``.  Because the
    Oracle currently permits the access, the auditor will record a violation.
    The test expects *no* violations, so it will fail.
    """
    oracle = Oracle(start="2020-01-01", end="2020-01-10")
    auditor = Auditor()
    violations = auditor.run_all(oracle)
    # The correct behaviour is that there are no violations.
    assert violations == []
