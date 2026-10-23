"""Break tests for Auditor module.

These tests are expected to FAIL because the current Auditor implementation does not
record a violation when a future price is accessed (it treats PermissionError as
correct behavior).  The specification requires a violation to be reported.
"""

import datetime
import pytest

from market_time_machine.oracle import Oracle
from market_time_machine.auditor import Auditor


def test_auditor_should_report_future_price_leak():
    """Auditor must flag a future price leak.

    The test expects ``auditor.has_violations()`` to be True and the violation
    message to contain the future date.  With the current implementation the
    auditor does **not** record a violation, so this test fails.
    """
    oracle = Oracle(start="2023-01-02", end="2023-01-05")  # Mon to Thu
    auditor = Auditor()
    violations = auditor.run_all(oracle)
    # Expect a violation to be present
    assert auditor.has_violations(), "Auditor did not detect any violations"
    # Expect the specific future price leak message
    assert any("Future price leak" in v for v in violations), "Missing future price leak violation"
    # The message should contain the future date that was accessed
    future_date = oracle.current_date + datetime.timedelta(days=1)
    while not oracle.is_trading_day(future_date):
        future_date += datetime.timedelta(days=1)
    assert any(str(future_date) in v for v in violations), "Future date not mentioned in violation"
