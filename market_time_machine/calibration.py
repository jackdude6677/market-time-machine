"""Prediction Calibration utilities.

Provides simple metrics to evaluate the quality of forecasts recorded in the
:class:`~market_time_machine.oracle.Oracle`.  The implementation is kept
lightweight – it only supports the fields used by the unit tests.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

from .oracle import Oracle, ForecastRecord


class PredictionCalibration:
    """Collect forecasts from an :class:`Oracle` and compute calibration metrics.

    The class does not store its own copy of forecasts – it queries the
    Oracle's audit log when metrics are requested.  This keeps the state
    consistent with the rest of the system.
    """

    def __init__(self, oracle: Oracle):
        self.oracle = oracle

    # ---------------------------------------------------------------------
    # Helper utilities
    # ---------------------------------------------------------------------
    def _all_forecasts(self) -> List[ForecastRecord]:
        return self.oracle.audit_log()

    # ---------------------------------------------------------------------
    # Public metric methods
    # ---------------------------------------------------------------------
    def directional_accuracy(self) -> float:
        """Proportion of forecasts where the predicted direction matches the outcome.

        Handles string predictions ("up"/"down"), numeric predictions (positive/negative),
        and dictionary predictions with a ``"prediction"`` key.  The special case
        of a numeric prediction of ``0`` is treated as "flat" and matches an
        outcome of ``0``.
        """
        records = self._all_forecasts()
        if not records:
            return 0.0
        correct = 0
        total = 0
        for rec in records:
            if rec.outcome is None:
                continue
            pred = rec.prediction
            # Determine predicted direction
            if isinstance(pred, dict) and "prediction" in pred:
                pred_dir = str(pred["prediction"]).lower()
            elif isinstance(pred, str):
                pred_dir = pred.lower()
            elif isinstance(pred, (int, float)):
                if pred > 0:
                    pred_dir = "up"
                elif pred < 0:
                    pred_dir = "down"
                else:
                    pred_dir = "flat"
            else:
                continue
            actual_dir = "up" if rec.outcome > 0 else "down" if rec.outcome < 0 else "flat"
            if pred_dir == actual_dir:
                correct += 1
            total += 1
        return correct / total if total else 0.0

    def brier_score(self) -> float:
        """Mean Brier score for forecasts that include a ``prob_up`` probability.

        Brier score = (forecast_probability - actual_outcome)^2 where actual
        outcome is 1 for an upward move and 0 otherwise.
        """
        records = self._all_forecasts()
        scores: List[float] = []
        for rec in records:
            if rec.outcome is None:
                continue
            prob = None
            if isinstance(rec.prediction, dict) and "prob_up" in rec.prediction:
                prob = rec.prediction["prob_up"]
            if prob is None:
                continue
            actual = 1.0 if rec.outcome > 0 else 0.0
            scores.append((prob - actual) ** 2)
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    def probability_calibration(self) -> Dict[float, Tuple[int, float]]:
        """Return calibration buckets.

        Buckets are the probability rounded to one decimal place.  The returned
        mapping is ``{bucket: (count, avg_actual)}`` where ``avg_actual`` is the
        average of the binary actual outcomes in that bucket.
        """
        bucket_counts: Dict[float, int] = defaultdict(int)
        bucket_success: Dict[float, int] = defaultdict(int)
        for rec in self._all_forecasts():
            if rec.outcome is None:
                continue
            prob = None
            if isinstance(rec.prediction, dict) and "prob_up" in rec.prediction:
                prob = rec.prediction["prob_up"]
            if prob is None:
                continue
            bucket = round(prob, 1)
            bucket_counts[bucket] += 1
            if rec.outcome > 0:
                bucket_success[bucket] += 1
        result: Dict[float, Tuple[int, float]] = {}
        for b, cnt in bucket_counts.items():
            success = bucket_success[b]
            result[b] = (cnt, success / cnt)
        return result

    def expected_return_mae(self) -> float:
        """Mean absolute error of ``expected_return`` forecasts.

        Only forecasts that contain an ``expected_return`` key are considered.
        """
        errors: List[float] = []
        for rec in self._all_forecasts():
            if rec.outcome is None:
                continue
            if isinstance(rec.prediction, dict) and "expected_return" in rec.prediction:
                pred = rec.prediction["expected_return"]
                errors.append(abs(pred - rec.outcome))
        if not errors:
            return 0.0
        return sum(errors) / len(errors)

    def all_metrics(self) -> Dict[str, object]:
        """Return a dictionary with the most common metrics.
        """
        return {
            "directional_accuracy": self.directional_accuracy(),
            "brier_score": self.brier_score(),
            "probability_calibration": self.probability_calibration(),
            "expected_return_mae": self.expected_return_mae(),
        }

"""End of calibration module."""
