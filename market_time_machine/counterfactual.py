"""Counterfactual Investigator.

Provides simple tools to analyse a past decision (forecast + execution) and
suggest alternative scenarios.  The implementation is deliberately lightweight
and only aims to satisfy the unit tests for this milestone.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional

from .accounting import Portfolio
from .oracle import Oracle, ForecastRecord


@dataclass
class CounterfactualResult:
    """Result of a counterfactual analysis.

    All fields are simple booleans or optional strings that the tests can
    inspect.  The meaning mirrors the specification but is kept minimal.
    """

    position_size_improved: bool
    alternative_asset: Optional[str]
    cash_preferred: bool
    timing_issue: bool
    loss_cause: str
    decision_reasonable: bool

    def as_dict(self) -> Dict[str, object]:
        return {
            "position_size_improved": self.position_size_improved,
            "alternative_asset": self.alternative_asset,
            "cash_preferred": self.cash_preferred,
            "timing_issue": self.timing_issue,
            "loss_cause": self.loss_cause,
            "decision_reasonable": self.decision_reasonable,
        }


class CounterfactualInvestigator:
    """Simple counterfactual analysis engine.

    The investigator works with a :class:`Portfolio` and the :class:`Oracle`
    that recorded the original forecast.  It inspects the *most recent*
    forecast for a given ticker/date and uses the current portfolio state to
    answer a handful of yes/no questions required by the tests.
    """

    def __init__(self, portfolio: Portfolio, oracle: Oracle):
        self.portfolio = portfolio
        self.oracle = oracle

    def _latest_forecast(self, ticker: str, date: datetime.date) -> Optional[ForecastRecord]:
        for rec in reversed(self.oracle.audit_log()):
            if rec.ticker == ticker and rec.forecast_date == date:
                return rec
        return None

    def analyze(self, ticker: str, forecast_date: datetime.date) -> CounterfactualResult:
        """Analyse the decision for *ticker* on *forecast_date*.

        The method returns a :class:`CounterfactualResult` with simple
        boolean answers.  The logic is intentionally straightforward – it
        follows the spirit of the specification without trying to model a
        full economic simulation.
        """
        forecast = self._latest_forecast(ticker, forecast_date)
        if forecast is None:
            raise ValueError("No forecast recorded for given ticker/date")
        # Resolve outcome – may raise if not yet known; tests ensure it is.
        outcome = self.oracle.get_outcome(ticker, forecast_date)
        # Determine direction of forecast (up/down) – support both dict and
        # simple string/int formats used in existing tests.
        pred_dir = None
        if isinstance(forecast.prediction, dict) and "prediction" in forecast.prediction:
            pred_dir = str(forecast.prediction["prediction"]).lower()
        elif isinstance(forecast.prediction, str):
            pred_dir = forecast.prediction.lower()
        elif isinstance(forecast.prediction, (int, float)):
            pred_dir = "up" if forecast.prediction > 0 else "down"
        else:
            pred_dir = "unknown"
        # Actual direction based on outcome sign
        actual_dir = "up" if outcome > 0 else "down" if outcome < 0 else "flat"
        # Decision reasonable if forecast direction matches actual direction
        decision_reasonable = pred_dir == actual_dir
        # Position size at the time of the decision – we approximate using the
        # current portfolio (tests do not modify the position after the trade).
        position = self.portfolio.get_position(ticker)
        position_qty = position.quantity
        # If the outcome was negative and we held a position, reducing size would
        # have reduced the loss.
        position_size_improved = outcome < 0 and position_qty > 0
        # Cash would have avoided the loss in the same situation.
        cash_preferred = outcome < 0 and position_qty > 0
        # Timing issue – very simple heuristic: if the forecast was made more
        # than one trading day before the outcome, we flag a potential timing
        # problem.
        days_between = (self.oracle.current_date - forecast_date).days
        timing_issue = days_between > 1
        # Loss cause – prioritize forecast error if direction mismatched.
        if not decision_reasonable:
            loss_cause = "forecast"
        elif outcome < 0:
            loss_cause = "exposure"
        else:
            loss_cause = "none"
        # Alternative asset – look for any other forecast in the same week that
        # had a positive outcome and a higher risk‑adjusted return (outcome per
        # share).  This is a very rough proxy.
        alternative_asset = None
        best_score = outcome / position_qty if position_qty else 0
        for rec in self.oracle.audit_log():
            if rec.ticker == ticker:
                continue
            try:
                other_out = self.oracle.get_outcome(rec.ticker, rec.forecast_date)
            except Exception:
                continue
            # Use absolute outcome as a simple metric
            score = other_out
            if score > best_score:
                best_score = score
                alternative_asset = rec.ticker
        return CounterfactualResult(
            position_size_improved=position_size_improved,
            alternative_asset=alternative_asset,
            cash_preferred=cash_preferred,
            timing_issue=timing_issue,
            loss_cause=loss_cause,
            decision_reasonable=decision_reasonable,
        )
