"""Tests for the Market Regime Detector.

The RegimeDetector records metric observations and provides a deterministic
description of the current market regime.  The tests cover:

* Empty history → empty result.
* Price trend detection (bull, bear, neutral).
* Volatility classification (high / low).
* Interest‑rate and inflation trend detection.
* Correlation detection between two price series.
* History clearing.
"""

import datetime

import pytest

from market_time_machine.regime import RegimeDetector


@pytest.fixture
def dates():
    """Yield a list of consecutive trading dates."""
    start = datetime.date(2023, 1, 1)
    return [start + datetime.timedelta(days=i) for i in range(10)]


def test_empty_history_returns_empty():
    detector = RegimeDetector()
    assert detector.detect() == {}
    # Even after clear, still empty
    detector.clear()
    assert detector.detect() == {}


def test_price_trend_bull_and_neutral_and_bear(dates):
    detector = RegimeDetector(window=5)

    # Bull trend: price rises more than 0.5 over the window
    for i, d in enumerate(dates[:5]):
        detector.record(d, price=100 + i * 1.0)  # increase by 1 each day
    result = detector.detect()
    assert result["trend"] == "bull"

    detector.clear()
    # Bear trend: price falls more than 0.5
    for i, d in enumerate(dates[:5]):
        detector.record(d, price=100 - i * 1.0)
    result = detector.detect()
    assert result["trend"] == "bear"

    detector.clear()
    # Neutral trend: change within ±0.5
    for i, d in enumerate(dates[:5]):
        detector.record(d, price=100 + (i % 2) * 0.2)  # small wiggle
    result = detector.detect()
    assert result["trend"] == "neutral"


def test_volatility_classification(dates):
    detector = RegimeDetector(window=5)

    # Low volatility: price changes of 0.2 → std < 1.0
    for i, d in enumerate(dates[:5]):
        detector.record(d, price=100 + i * 0.2)
    result = detector.detect()
    assert result["volatility"] == "low"

    detector.clear()
    # High volatility: price changes of 2.0 → std > 1.0
    for i, d in enumerate(dates[:5]):
        detector.record(d, price=100 + i * 2.0)
    result = detector.detect()
    assert result["volatility"] == "high"


def test_interest_rate_and_inflation_trends(dates):
    detector = RegimeDetector(window=5)

    # Rising interest rate and inflation
    for i, d in enumerate(dates[:5]):
        detector.record(d, interest_rate=1.0 + i * 0.2, inflation=2.0 + i * 0.3)
    result = detector.detect()
    assert result["interest_rate"] == "rising"
    assert result["inflation"] == "rising"

    detector.clear()
    # Falling interest rate and stable inflation
    for i, d in enumerate(dates[:5]):
        detector.record(d, interest_rate=2.0 - i * 0.2, inflation=3.0)
    result = detector.detect()
    assert result["interest_rate"] == "falling"
    assert result["inflation"] == "stable"

    detector.clear()
    # Stable interest rate and falling inflation
    for i, d in enumerate(dates[:5]):
        detector.record(d, interest_rate=1.5, inflation=5.0 - i * 0.3)
    result = detector.detect()
    assert result["interest_rate"] == "stable"
    assert result["inflation"] == "falling"


def test_correlation_detection(dates):
    detector = RegimeDetector(window=5)

    # Perfect positive correlation → correlation normal
    for i, d in enumerate(dates[:5]):
        detector.record(d, price1=10 + i, price2=20 + i * 2)
    result = detector.detect()
    assert result["correlation"] == "normal"

    detector.clear()
    # Near zero correlation → unusual
    # price1 alternating, price2 constant
    for i, d in enumerate(dates[:5]):
        detector.record(d, price1=1 if i % 2 == 0 else -1, price2=5.0)
    result = detector.detect()
    assert result["correlation"] == "unusual"


def test_clear_resets_history():
    detector = RegimeDetector()
    today = datetime.date.today()
    detector.record(today, price=100, interest_rate=1.0, inflation=2.0)
    detector.clear()
    # After clear, detection should be empty regardless of window size
    assert detector.detect() == {}
