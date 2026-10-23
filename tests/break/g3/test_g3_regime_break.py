"""Break tests for RegimeDetector.

__test__ = False  # Prevent pytest collection conflict with qa test
"""

import datetime
import pytest

from market_time_machine.regime import RegimeDetector


def test_non_numeric_metric_raises_value_error():
    """The detector should reject non‑numeric metric values.

    The implementation raises ``TypeError``; the test expects ``ValueError``
    to expose the bug.
    """
    detector = RegimeDetector()
    today = datetime.date.today()
    with pytest.raises(ValueError):
        detector.record(today, price="not-a-number")


def test_missing_history_returns_empty_dict():
    """When no sufficient history is present, ``detect`` should return an empty dict.

    The current implementation returns an empty dict, so this test will pass.
    It is included for completeness.
    """
    detector = RegimeDetector()
    assert detector.detect() == {}
