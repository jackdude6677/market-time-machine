"""Tests for PredictionCalibration metrics (milestone 8)."""

import datetime

import pytest

from market_time_machine.oracle import Oracle
from market_time_machine.calibration import PredictionCalibration


def setup_oracle_with_forecasts():
    """Create an Oracle, record several forecasts, and advance to resolve outcomes.

    Returns the Oracle instance ready for calibration analysis.
    """
    oracle = Oracle(start="2020-01-01", end="2020-01-10")
    ticker = "AAA"
    # Day 0 forecast: predicts up, high prob, expected return 2
    fdate0 = oracle.current_date
    oracle.record_forecast(
        ticker,
        fdate0,
        prediction={"prediction": "up", "prob_up": 0.8, "expected_return": 2},
    )
    # Advance one day
    oracle.advance_one_day()
    # Day 1 forecast: predicts down, low prob, expected return -1
    fdate1 = oracle.current_date
    oracle.record_forecast(
        ticker,
        fdate1,
        prediction={"prediction": "down", "prob_up": 0.2, "expected_return": -1},
    )
    oracle.advance_one_day()
    # Day 2 forecast: simple string prediction up (no prob, no expected return)
    fdate2 = oracle.current_date
    oracle.record_forecast(ticker, fdate2, prediction="up")
    oracle.advance_one_day()
    # Day 3 forecast: numeric positive prediction with prob_up
    fdate3 = oracle.current_date
    oracle.record_forecast(
        ticker,
        fdate3,
        prediction={"prediction": "up", "prob_up": 0.6, "expected_return": 0},
    )
    # Advance to the end so all outcomes are resolved
    while True:
        try:
            oracle.advance_one_day()
        except StopIteration:
            break
    return oracle


def test_directional_accuracy_and_brier_score():
    oracle = setup_oracle_with_forecasts()
    calib = PredictionCalibration(oracle)
    # With deterministic price increase, actual direction is always "up"
    # 3 out of 4 forecasts predict up => 0.75 accuracy
    assert pytest.approx(calib.directional_accuracy(), rel=1e-6) == 0.75
    # Brier scores for prob_up values 0.8, 0.2, 0.6
    # Expected mean = (0.04 + 0.64 + 0.16) / 3 = 0.28
    assert pytest.approx(calib.brier_score(), rel=1e-6) == 0.28


def test_probability_calibration_and_expected_return_mae():
    oracle = setup_oracle_with_forecasts()
    calib = PredictionCalibration(oracle)
    prob_cal = calib.probability_calibration()
    # Expect three buckets with count 1 each and avg_actual 1.0
    for bucket in (0.8, 0.2, 0.6):
        assert bucket in prob_cal
        count, avg = prob_cal[bucket]
        assert count == 1
        assert pytest.approx(avg, rel=1e-6) == 1.0


def test_all_metrics_dictionary():
    oracle = setup_oracle_with_forecasts()
    calib = PredictionCalibration(oracle)
    metrics = calib.all_metrics()
    expected_keys = {"directional_accuracy", "brier_score", "probability_calibration", "expected_return_mae"}
    assert set(metrics.keys()) == expected_keys
    # Spot‑check a couple of values
    assert pytest.approx(metrics["directional_accuracy"], rel=1e-6) == 0.75
    assert pytest.approx(metrics["expected_return_mae"], rel=1e-6) == 4/3
