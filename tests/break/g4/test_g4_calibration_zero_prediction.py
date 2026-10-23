"""Breaker test for PredictionCalibration directional accuracy with zero prediction.

The current implementation treats a numeric prediction of ``0`` as a “down”
direction, which leads to an incorrect directional accuracy when the
outcome is also zero (flat).  The test expects the accuracy to be ``1.0``,
so it should fail under the existing code.
"""

import pytest
from market_time_machine.oracle import Oracle, ForecastRecord
from market_time_machine.calibration import PredictionCalibration

def test_directional_accuracy_zero_prediction():
    # Create a short simulation period.
    oracle = Oracle(start="2020-01-01", end="2020-01-02")
    forecast_date = oracle.current_date

    # Record a forecast with a numeric zero prediction.
    oracle.record_forecast("AAA", forecast_date, prediction=0)

    # Manually set the outcome to zero (flat) to simulate no price change.
    # The internal storage is a dict keyed by (ticker, date).
    key = ("AAA", forecast_date)
    oracle._forecasts[key].outcome = 0  # type: ignore[attr-defined]

    # Initialise the calibration object and compute directional accuracy.
    calib = PredictionCalibration(oracle)
    acc = calib.directional_accuracy()

    # The correct behaviour would consider a zero prediction as “flat”,
    # yielding an accuracy of 1.0.  The current code returns 0.0, so this
    # assertion should fail.
    assert acc == 1.0, f"Expected accuracy 1.0, got {acc}"
