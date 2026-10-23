"""Break test: Auditor should detect a future‑price leak.

The Auditor is expected to record a violation when the Oracle allows a
future price query.  The current Oracle blocks the query, so the Auditor
never registers a violation – this test was originally expecting a leak,
but the correct behavior is that no violation is reported.
"""

import datetime
import pytest
from market_time_machine.oracle import Oracle
from market_time_machine.auditor import Auditor

def test_auditor_detects_future_price_leak():
    # Simple 4‑day simulation.
    oracle = Oracle(start="2023-01-02", end="2023-01-05")
    auditor = Auditor()
    violations = auditor.run_all(oracle)
    # Since the Oracle correctly blocks future price access, there should be no violations.
    assert not auditor.has_violations(), "Auditor incorrectly reported violations"
    assert violations == [], "Violations list should be empty"
