"""Breaker test for Auditor future price leak detection.

The Auditor should record a violation when a future price is accessible.
Using the standard Oracle, future price access raises PermissionError, so the
Auditor currently does **not** record a violation. This test expects a
violation and therefore will fail.
"""

import datetime
import pytest
from market_time_machine.oracle import Oracle
from market_time_machine.auditor import Auditor


def test_auditor_detects_future_price_leak_failure():
    # Oracle with a short range.
    oracle = Oracle(start="2023-01-02", end="2023-01-05")
    auditor = Auditor()
    violations = auditor.run_all(oracle)

    # The auditor is expected to have recorded a violation about a future price leak.
    assert auditor.has_violations(), "Auditor did not record any violations"
    assert any("Future price leak" in v for v in violations), (
        f"Expected a future price leak violation, got: {violations}"
    )
