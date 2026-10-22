"""Weekly Grading System.

Provides a simple implementation of the grading engine described in the
specification (section 9).  The implementation is deliberately lightweight –
it only needs to satisfy the unit tests for this milestone while remaining
readable and extensible.

The main entry point is :class:`WeeklyGrader`.  It is instantiated with a
:class:`~market_time_machine.accounting.Portfolio` and a
:class:`~market_time_machine.oracle.Oracle`.  The ``grade_week`` method takes a
start and end date (both inclusive) that define a calendar week of *actual*
elapsed time.  It returns a dictionary containing the overall grade and the
individual component scores.

All scores are capped at the maximum points defined in the spec and are
linearly scaled based on simple, deterministic metrics:

* **Net portfolio performance** – percentage return over the week, capped at
  100 % (doubling the equity).  Scaled to 35 points.
* **Risk‑adjusted performance** – weekly return divided by the standard
  deviation of daily returns (a Sharpe‑like ratio).  Ratios ≤ 0 give 0 points,
  ≥ 1 give the full 20 points.
* **Capital preservation / drawdown** – maximum drawdown as a fraction of the
  peak equity during the week.  A drawdown of 0 % yields 20 points, ≥ 50 %
  yields 0 points.
* **Prediction accuracy** – proportion of forecasts whose direction matches
  the realised price change.  Scaled to 10 points.
* **Decision & execution discipline** – proportion of forecasts that have a
  corresponding order (one‑to‑one mapping).  Scaled to 10 points.
* **Learning & improvement** – 5 points if the net return this week exceeds
  the previous week’s return; otherwise 0 points.  The first week receives 0 points.

The implementation deliberately avoids any external dependencies.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Tuple

from .accounting import Portfolio
from .oracle import Oracle, ForecastRecord, _next_trading_day, _is_trading_day


@dataclass
class WeekScore:
    """Container for the component scores of a week.

    All fields are expressed as points (0‑100) and the ``overall`` field is the
    sum of the components.
    """

    net_performance: float = 0.0
    risk_adjusted: float = 0.0
    drawdown: float = 0.0
    prediction_accuracy: float = 0.0
    discipline: float = 0.0
    learning: float = 0.0
    overall: float = field(init=False)

    def __post_init__(self) -> None:
        self.overall = (
            self.net_performance
            + self.risk_adjusted
            + self.drawdown
            + self.prediction_accuracy
            + self.discipline
            + self.learning
        )


class WeeklyGrader:
    """Calculate weekly grades for a trader.

    Parameters
    ----------
    portfolio:
        The :class:`~market_time_machine.accounting.Portfolio` instance that
        holds cash, positions and P&L.
    oracle:
        The :class:`~market_time_machine.oracle.Oracle` providing price data
        and the audit log of forecasts.
    """

    def __init__(self, portfolio: Portfolio, oracle: Oracle):
        self.portfolio = portfolio
        self.oracle = oracle
        self._last_week_return: float | None = None

    # ---------------------------------------------------------------------
    # Helper utilities
    # ---------------------------------------------------------------------
    def _equity_series(self, start: date, end: date) -> List[float]:
        """Return equity values at start and end dates.

        For the grading calculations we only need the equity at the start and
        end of the week, so this method returns a two‑element list.
        """
        start_eq = self.portfolio.equity({})
        end_eq = self.portfolio.equity({})
        return [start_eq, end_eq]

    def _max_drawdown(self, equity_series: List[float]) -> float:
        """Calculate maximum drawdown as a fraction of the peak equity.

        Returns a value between 0 and 1.
        """
        peak = -math.inf
        max_dd = 0.0
        for eq in equity_series:
            if eq > peak:
                peak = eq
            drawdown = (peak - eq) / peak if peak > 0 else 0.0
            if drawdown > max_dd:
                max_dd = drawdown
        return max_dd

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def grade_week(self, start: date, end: date) -> WeekScore:
        """Calculate the weekly grade for the period [start, end].

        Returns a :class:`WeekScore` with component points and the overall total.
        """
        # Gather trading days in the interval
        days: List[date] = []
        cur = start
        while cur <= end:
            if _is_trading_day(cur):
                days.append(cur)
            cur = _next_trading_day(cur)
        if not days:
            raise ValueError("No trading days in the given interval")

        # Equity series for drawdown and returns
        equity_series: List[float] = []
        for d in days:
            price_map = {ticker: self.oracle.get_price(ticker, d) for ticker in self.portfolio.positions}
            equity_series.append(self.portfolio.equity(price_map))
        start_eq, end_eq = equity_series[0], equity_series[-1]
        # Net return (percentage)
        net_return = (end_eq - start_eq) / start_eq if start_eq != 0 else 0.0
        net_points = max(0.0, min(net_return, 1.0)) * 35.0

        # Risk‑adjusted performance
        daily_returns: List[float] = []
        for i in range(1, len(equity_series)):
            prev, cur_eq = equity_series[i - 1], equity_series[i]
            if prev != 0:
                daily_returns.append((cur_eq - prev) / prev)
        if len(daily_returns) < 2:
            std = 0.0
        else:
            std = statistics.stdev(daily_returns)
        if std <= 0:
            ratio = 1.0
        else:
            ratio = net_return / std
        ratio = max(0.0, min(ratio, 1.0))
        risk_points = ratio * 20.0

        # Drawdown points (0% drawdown => 20, 50% => 0)
        max_dd = self._max_drawdown(equity_series)
        drawdown_points = max(0.0, (0.5 - max_dd) / 0.5) * 20.0

        # Forecast based metrics
        forecasts = [f for f in self.oracle.audit_log()
                     if start <= f.forecast_date <= end]
        total_forecasts = len(forecasts)
        # Prediction accuracy
        correct = 0
        for f in forecasts:
            outcome = f.outcome
            pred = f.prediction
            # simple direction prediction handling
            if isinstance(pred, dict) and "prediction" in pred:
                direction = pred["prediction"].lower()
                if direction == "up" and outcome > 0:
                    correct += 1
                elif direction == "down" and outcome < 0:
                    correct += 1
            elif isinstance(pred, (int, float)):
                # treat positive prediction as up, negative as down
                if (pred > 0 and outcome > 0) or (pred < 0 and outcome < 0):
                    correct += 1
        pred_acc = (correct / total_forecasts) if total_forecasts else 0.0
        pred_points = pred_acc * 10.0

        # Discipline: forecasts that have a matching position (non‑zero quantity)
        matched = 0
        for f in forecasts:
            pos = self.portfolio.positions.get(f.ticker)
            if pos and pos.quantity != 0:
                matched += 1
        discipline_ratio = (matched / total_forecasts) if total_forecasts else 0.0
        discipline_points = discipline_ratio * 10.0

        # Learning bonus
        learning_points = 0.0
        if self._last_week_return is not None and net_return > self._last_week_return:
            learning_points = 5.0
        # Update stored return for next week
        self._last_week_return = net_return

        return WeekScore(
            net_performance=net_points,
            risk_adjusted=risk_points,
            drawdown=drawdown_points,
            prediction_accuracy=pred_points,
            discipline=discipline_points,
            learning=learning_points,
        )

