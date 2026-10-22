"""Oracle core for Market Time Machine.

Provides a minimal in‑memory simulation of historical market data, a
simulation clock, and a simple information firewall.  The implementation
is deliberately lightweight – it only needs to satisfy the unit tests
for this milestone.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Dict, Tuple, Any, List


def _is_trading_day(date: datetime.date) -> bool:
    """Return True if *date* is a weekday (Mon‑Fri)."""
    return date.weekday() < 5


def _next_trading_day(date: datetime.date) -> datetime.date:
    """Return the next calendar day that is a trading day.

    The function moves forward one day at a time until it lands on a
    weekday.  Weekends are therefore skipped.
    """
    nxt = date + datetime.timedelta(days=1)
    while not _is_trading_day(nxt):
        nxt += datetime.timedelta(days=1)
    return nxt


@dataclass
class ForecastRecord:
    ticker: str
    forecast_date: datetime.date
    prediction: Any
    recorded_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    outcome: Any = None  # Filled when the outcome becomes known


class Oracle:
    """A very small Oracle implementation.

    The Oracle generates deterministic dummy price data (starting at 100
    and increasing by 1 each trading day).  It tracks a simulation clock
    and enforces that only data up to the current simulated date can be
    accessed.
    """

    def __init__(self, start: str | datetime.date, end: str | datetime.date):
        self.start_date = (
            datetime.datetime.strptime(start, "%Y-%m-%d").date()
            if isinstance(start, str)
            else start
        )
        self.end_date = (
            datetime.datetime.strptime(end, "%Y-%m-%d").date()
            if isinstance(end, str)
            else end
        )
        if self.start_date > self.end_date:
            raise ValueError("start date must be before end date")
        # Initialise clock at the start date (must be a trading day)
        self.current_date = self.start_date
        while not _is_trading_day(self.current_date):
            self.current_date = _next_trading_day(self.current_date)
        # Forecast storage keyed by (ticker, forecast_date)
        self._forecasts: Dict[Tuple[str, datetime.date], ForecastRecord] = {}

    # ---------------------------------------------------------------------
    # Simulation clock handling
    # ---------------------------------------------------------------------
    def advance_one_day(self) -> None:
        """Advance the simulation clock to the next trading day.

        Raises ``StopIteration`` when the end of the simulation period is
        reached.
        """
        next_day = _next_trading_day(self.current_date)
        if next_day > self.end_date:
            raise StopIteration("Simulation has reached the end date")
        self.current_date = next_day
        # After moving the clock we can resolve any outcomes that become
        # known on this new date.
        self._resolve_outcomes()

    # ---------------------------------------------------------------------
    # Price data (firewalled)
    # ---------------------------------------------------------------------
    def _price_for_date(self, date: datetime.date) -> float:
        """Deterministic dummy price for *date*.

        The price starts at 100 on the first trading day and increments
        by 1 for each subsequent trading day.
        """
        # Count trading days from start_date (inclusive) to *date* (inclusive)
        if date < self.start_date:
            raise ValueError("date is before simulation start")
        days = 0
        cur = self.start_date
        while cur <= date:
            if _is_trading_day(cur):
                days += 1
            cur += datetime.timedelta(days=1)
        return 100.0 + (days - 1)  # first day price = 100

    def get_price(self, ticker: str, date: datetime.date) -> float:
        """Return the price for *ticker* on *date* if allowed.

        Access is only permitted when *date* is on or before the current
        simulation date.  Attempting to retrieve a future price raises a
        ``PermissionError``.
        """
        if date > self.current_date:
            raise PermissionError("Future price data is not available")
        # In this minimal implementation the ticker is ignored – all
        # tickers share the same deterministic price series.
        return self._price_for_date(date)

    # ---------------------------------------------------------------------
    # Forecast handling
    # ---------------------------------------------------------------------
    def record_forecast(self, ticker: str, forecast_date: datetime.date, prediction: Any) -> None:
        """Store a forecast made by the Trader.

        ``forecast_date`` must be on or before the current simulation
        date; otherwise a ``PermissionError`` is raised.
        """
        if forecast_date > self.current_date:
            raise PermissionError("Cannot record a forecast for a future date")
        key = (ticker, forecast_date)
        if key in self._forecasts:
            raise ValueError("Forecast for this ticker/date already recorded")
        self._forecasts[key] = ForecastRecord(ticker, forecast_date, prediction)

    def _resolve_outcomes(self) -> None:
        """Resolve outcomes for any forecasts whose next‑day price is now known.

        This private helper is called after each clock advance.
        """
        for (ticker, fdate), record in list(self._forecasts.items()):
            # Outcome is defined as price change from forecast date to the
            # following trading day.
            if record.outcome is not None:
                continue
            # The next trading day after the forecast date
            next_day = _next_trading_day(fdate)
            if next_day <= self.current_date:
                price_today = self._price_for_date(fdate)
                price_next = self._price_for_date(next_day)
                record.outcome = price_next - price_today

    def get_outcome(self, ticker: str, forecast_date: datetime.date) -> Any:
        """Return the outcome for a previously recorded forecast.

        If the outcome is not yet known a ``ValueError`` is raised.
        """
        key = (ticker, forecast_date)
        if key not in self._forecasts:
            raise KeyError("No such forecast recorded")
        record = self._forecasts[key]
        if record.outcome is None:
            raise ValueError("Outcome not yet available")
        return record.outcome

    # ---------------------------------------------------------------------
    # Audit utilities (simple)
    # ---------------------------------------------------------------------
    def audit_log(self) -> List[ForecastRecord]:
        """Return a list of all forecast records (immutable snapshot)."""
        return list(self._forecasts.values())

    # ---------------------------------------------------------------------
    # Helper for tests / external callers
    # ---------------------------------------------------------------------
    def is_trading_day(self, date: datetime.date) -> bool:
        return _is_trading_day(date)
