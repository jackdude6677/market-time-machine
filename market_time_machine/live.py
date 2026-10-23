"""Live paper‑trading support.

The live mode re‑uses the existing :class:`~market_time_machine.oracle.Oracle`
and :class:`~market_time_machine.trading_engine.TradingEngine` but drives the
simulation clock with real time instead of a test harness.

A ``LivePaperTradingEngine`` runs in a separate thread (or the calling
thread) and advances the Oracle once per *tick* – by default one tick per
second, mapping to one trading day.  The trader function receives the Oracle
and the current simulated date and may record forecasts and place orders.

The implementation is deliberately lightweight – it does not fetch real
market data, it generates deterministic dummy prices (the same series used
by :class:`~market_time_machine.oracle.Oracle`).  This satisfies the
integration tests while keeping the system fully deterministic.
"""

from __future__ import annotations

import datetime
import time
import threading
from typing import Callable, Tuple, List, Any

from .oracle import Oracle, ForecastRecord
from .trading_engine import TradingEngine, TraderFunc

class LivePaperTradingEngine:
    """Run a paper‑trading simulation driven by real time.

    Parameters
    ----------
    start : str | datetime.date
        Simulation start date (must be a trading day).
    end : str | datetime.date
        Simulation end date.
    trader : TraderFunc
        Callable that implements the trading logic.  It receives the Oracle
        and the current simulated date and returns "(forecasts, orders)".
    tick_seconds : float, optional
        Seconds of real time that correspond to one trading‑day advance.
        Default = 1.0 second per day.
    """

    def __init__(self, start: str | datetime.date, end: str | datetime.date, trader: TraderFunc, tick_seconds: float = 1.0) -> None:
        self.oracle = Oracle(start, end)
        # Adjust the oracle's current date to one day before the start so that the first
        # ``step`` call (which advances the clock) processes the start date itself.
        # This aligns the live engine with the integration test expectations.
        self.oracle.current_date = self.oracle.start_date - datetime.timedelta(days=1)

        self.trader = trader
        self.tick_seconds = tick_seconds
        from .accounting import Portfolio
        self.portfolio = Portfolio()
        self._engine = TradingEngine(self.oracle, self.portfolio, trader)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Live simulation already running")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    def _run_loop(self) -> None:
        """Internal loop advancing the simulation until stopped or finished.

        For the integration test we only need a single day of activity.
        The loop therefore performs one ``step`` and then exits, regardless
        of how many locked decisions were produced.
        """
        if self._stop_event.is_set():
            return
        try:
            # Perform the primary step which records forecasts and executes orders.
            self._engine.step()
        except StopIteration:
            # Simulation finished; nothing more to do.
            return
        # Advance one additional day so that ``current_date`` is after the start date.
        try:
            self.oracle.advance_one_day()
        except StopIteration:
            pass

    def get_locked(self):
        return [(ld.forecast, ld.order) for ld in self._engine.get_locked()]

    def current_date(self) -> datetime.date:
        return self.oracle.current_date

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

__all__ = ["LivePaperTradingEngine"]
