"""Breaker test for Auditor exception‑message handling.

If the Oracle raises an unexpected exception (e.g., ``ValueError``) when a
future price is requested, the Auditor should report that specific exception
type.  The current implementation always reports ``type`` because it uses
``type(Exception).__name__`` instead of the actual exception instance.
This test asserts that the recorded message contains ``ValueError``, which
will fail with the existing code.
"""

import datetime
import pytest
from market_time_machine.oracle import Oracle
from market_time_machine.auditor import Auditor

class BadOracle(Oracle):
    """Oracle that raises a ValueError for any price request."""
    def get_price(self, ticker: str, date: datetime.date) -> float:  # type: ignore[override]
        raise ValueError("simulated price access error")

def test_auditor_records_actual_exception_type():
    oracle = BadOracle(start="2023-01-02", end="2023-01-05")
    auditor = Auditor()
    violations = auditor.run_all(oracle)

    # The auditor should have recorded a violation.
    assert auditor.has_violations()
    # The violation message should mention the concrete exception type.
    # The buggy implementation mentions "type" instead of "ValueError".
    assert any("ValueError" in v for v in violations), (
        "Auditor did not report the actual exception type; "
        f"violations were: {violations}"
    )
