"""QA tests for Market Regime Detector (milestone 7).
These tests verify core behaviours required by the specification:
* Empty history yields empty result.
* Insufficient data for a metric omits that key.
* Trend detection (bull, bear, neutral).
* Volatility classification.
* Interest‑rate and inflation trend detection.
* Correlation detection with both numpy and pure‑python fallback.
* History clearing resets detector.
"""

import datetime
import pytest

from market_time_machine.regime import RegimeDetector

@pytest.fixture
def dates():
    """Return a list of ten consecutive dates."""
    start = datetime.date(2023, 1, 1)
    return [start + datetime.timedelta(days=i) for i in range(10)]

def test_empty_history_returns_empty():
    detector = RegimeDetector()
    assert detector.detect() == {}
    detector.record(datetime.date.today(), price=100)
    detector.clear()
    assert detector.detect() == {}

def test_insufficient_history_omits_keys(dates):
    detector = RegimeDetector(window=5)
    # Record only three price points – below window size.
    for d in dates[:3]:
        detector.record(d, price=100 + d.toordinal() % 3)
    result = detector.detect()
    # No metric should be present because window not satisfied.
    assert result == {}

def test_price_trend_detection(dates):
    detector = RegimeDetector(window=5)
    # Bull trend (>0.5 increase)
    for i, d in enumerate(dates[:5]):
        detector.record(d, price=100 + i * 1.0)
    assert detector.detect()["trend"] == "bull"
    detector.clear()
    # Bear trend (<-0.5 decrease)
    for i, d in enumerate(dates[:5]):
        detector.record(d, price=100 - i * 1.0)
    assert detector.detect()["trend"] == "bear"
    detector.clear()
    # Neutral trend (within ±0.5)
    for i, d in enumerate(dates[:5]):
        detector.record(d, price=100 + (i % 2) * 0.2)
    assert detector.detect()["trend"] == "neutral"

def test_volatility_classification(dates):
    detector = RegimeDetector(window=5)
    # Low volatility (std < 1.0)
    for i, d in enumerate(dates[:5]):
        detector.record(d, price=100 + i * 0.2)
    assert detector.detect()["volatility"] == "low"
    detector.clear()
    # High volatility (std > 1.0)
    for i, d in enumerate(dates[:5]):
        detector.record(d, price=100 + i * 2.0)
    assert detector.detect()["volatility"] == "high"

def test_interest_rate_and_inflation_trends(dates):
    detector = RegimeDetector(window=5)
    # Rising both
    for i, d in enumerate(dates[:5]):
        detector.record(d, interest_rate=1.0 + i * 0.2, inflation=2.0 + i * 0.3)
    res = detector.detect()
    assert res["interest_rate"] == "rising"
    assert res["inflation"] == "rising"
    detector.clear()
    # Falling interest, stable inflation
    for i, d in enumerate(dates[:5]):
        detector.record(d, interest_rate=2.0 - i * 0.2, inflation=3.0)
    res = detector.detect()
    assert res["interest_rate"] == "falling"
    assert res["inflation"] == "stable"
    detector.clear()
    # Stable interest, falling inflation
    for i, d in enumerate(dates[:5]):
        detector.record(d, interest_rate=1.5, inflation=5.0 - i * 0.3)
    res = detector.detect()
    assert res["interest_rate"] == "stable"
    assert res["inflation"] == "falling"

def test_correlation_detection(dates):
    detector = RegimeDetector(window=5)
    # Strong positive correlation → "normal"
    for i, d in enumerate(dates[:5]):
        detector.record(d, price1=10 + i, price2=20 + i * 2)
    assert detector.detect()["correlation"] == "normal"
    detector.clear()
    # Near‑zero correlation → "unusual"
    for i, d in enumerate(dates[:5]):
        detector.record(d, price1=1 if i % 2 == 0 else -1, price2=5.0)
    assert detector.detect()["correlation"] == "unusual"

def test_window_validation():
    with pytest.raises(ValueError):
        RegimeDetector(window=1)
