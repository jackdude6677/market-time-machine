"""Market Regime Detector.

A lightweight, deterministic implementation that analyses recent market
metrics (price, volatility, interest rates, inflation, etc.) and
produces a simple regime description.

The detector works on a sliding window of recent observations.  It is
intentionally simple – the goal is to provide deterministic behaviour
suitable for unit‑tests without requiring external data sources.
"""

from __future__ import annotations

import datetime
import statistics
from collections import defaultdict
from typing import Any, Dict, List, Tuple

# Optional numpy for correlation; fallback to pure python if unavailable.
try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None


class RegimeDetector:
    """Detect market regimes from recent metric observations.

    Parameters
    ----------
    window: int, default 5
        Number of most recent observations used for each metric.
    """

    def __init__(self, window: int = 5) -> None:
        if window < 2:
            raise ValueError("window must be >= 2")
        self.window = window
        # metric -> list of (date, value)
        self._history: Dict[str, List[Tuple[datetime.date, float]]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Data recording
    # ------------------------------------------------------------------
    def record(self, date: datetime.date, **metrics: float) -> None:
        """Record one or more metric values for *date*.

        Example
        -------
        >>> detector.record(datetime.date(2023, 1, 1), price=100.0, interest_rate=1.5)
        """
        for name, value in metrics.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"Metric {name!r} must be numeric")
            self._history[name].append((date, float(value)))

    # ------------------------------------------------------------------
    # Helper to fetch the most recent *window* values for a metric.
    # ------------------------------------------------------------------
    def _recent(self, name: str) -> List[float] | None:
        hist = self._history.get(name, [])
        if len(hist) < self.window:
            return None
        # Return only the values, discarding dates.
        return [v for _, v in hist[-self.window :]]

    # ------------------------------------------------------------------
    # Regime detection logic – deterministic, rule‑based.
    # ------------------------------------------------------------------
    def detect(self) -> Dict[str, str]:
        """Return a dictionary describing the current regime.

        Keys include ``trend``, ``volatility``, ``interest_rate``,
        ``inflation`` and ``correlation`` when enough data is present.
        """
        result: Dict[str, str] = {}

        # ----- price trend (bull / bear / neutral) -----
        price_vals = self._recent("price")
        if price_vals:
            diff = price_vals[-1] - price_vals[0]
            if diff > 0.5:
                result["trend"] = "bull"
            elif diff < -0.5:
                result["trend"] = "bear"
            else:
                result["trend"] = "neutral"

        # ----- volatility (high / low) -----
        if price_vals and len(price_vals) > 1:
            # Use standard deviation of price levels directly for volatility.
            std = statistics.stdev(price_vals) if len(price_vals) > 1 else 0.0
            result["volatility"] = "high" if std > 1.0 else "low"

        # ----- interest rate trend -----
        ir_vals = self._recent("interest_rate")
        if ir_vals:
            diff = ir_vals[-1] - ir_vals[0]
            if diff > 0.1:
                result["interest_rate"] = "rising"
            elif diff < -0.1:
                result["interest_rate"] = "falling"
            else:
                result["interest_rate"] = "stable"

        # ----- inflation trend -----
        inf_vals = self._recent("inflation")
        if inf_vals:
            diff = inf_vals[-1] - inf_vals[0]
            if diff > 0.1:
                result["inflation"] = "rising"
            elif diff < -0.1:
                result["inflation"] = "falling"
            else:
                result["inflation"] = "stable"

        # ----- correlation between two price series -----
        p1 = self._recent("price1")
        p2 = self._recent("price2")
        if p1 and p2 and len(p1) == len(p2):
            if np is not None:
                corr = float(np.corrcoef(p1, p2)[0, 1])
                # numpy may return nan when one series has zero variance
                if np.isnan(corr):
                    corr = 0.0
            else:
                # Simple Pearson correlation implementation
                mean1 = sum(p1) / len(p1)
                mean2 = sum(p2) / len(p2)
                num = sum((a - mean1) * (b - mean2) for a, b in zip(p1, p2))
                den1 = sum((a - mean1) ** 2 for a in p1)
                den2 = sum((b - mean2) ** 2 for b in p2)
                denom = (den1 * den2) ** 0.5
                corr = num / denom if denom != 0 else 0.0
            result["correlation"] = "unusual" if abs(corr) < 0.2 else "normal"

        return result

    # ------------------------------------------------------------------
    # Convenience: clear history (useful for tests).
    # ------------------------------------------------------------------
    def clear(self) -> None:
        """Remove all recorded observations."""
        self._history.clear()

__all__ = ["RegimeDetector"]
