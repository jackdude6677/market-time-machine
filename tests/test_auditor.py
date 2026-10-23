import datetime

import pytest

from market_time_machine.oracle import Oracle
from market_time_machine.auditor import Auditor


def test_auditor_detects_future_price_leak():
    # Simple simulation from Monday to Thursday
    oracle = Oracle(start="2023-01-02", end="2023-01-05")
    auditor = Auditor()
    violations = auditor.run_all(oracle)
    # The auditor should detect that a future price is accessible
    assert auditor.has_violations()
    assert any("Future price leak" in v for v in violations)

    # Ensure that the violation message contains the future date
    future_date = oracle.current_date + datetime.timedelta(days=1)
    # Advance to next trading day if weekend
    while not oracle.is_trading_day(future_date):
        future_date += datetime.timedelta(days=1)
    assert any(str(future_date) in v for v in violations)
