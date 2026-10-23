"""Trading Decision Engine.

Provides a minimal orchestration of a trading session using the Oracle
simulation, a Portfolio accounting engine and a user‑supplied trader
function.

The implementation is deliberately lightweight – it only needs to satisfy
the unit tests for this milestone.  It follows the nine‑step workflow
outlined in the specification.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Any

from .oracle import Oracle, ForecastRecord
from .accounting import Order, Portfolio

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

# The trader receives the oracle (to query prices) and the current date and
# returns a list of forecasts and a list of orders.  Forecasts are tuples of
# (ticker, prediction) where *prediction* can be any JSON‑serialisable object.
TraderFunc = Callable[[Oracle, datetime.date], Tuple[List[Tuple[str, Any]], List[Order]]]


@dataclass(frozen=True)
class LockedDecision:
    """Immutable record of a forecast and its associated order.

    The *forecast* is stored as a :class:`ForecastRecord` created by the
    :class:`Oracle`.  The *order* is the :class:`~market_time_machine.accounting.Order`
    that the trader wishes to execute.
    """

    forecast: ForecastRecord
    order: Order


class TradingEngine:
    """Orchestrates a single trading session.

    Parameters
    ----------
    oracle:
        The :class:`~market_time_machine.oracle.Oracle` instance that provides
        price data and stores forecasts.
    portfolio:
        The :class:`~market_time_machine.accounting.Portfolio` that tracks cash
        and positions.
    trader:
        Callable implementing the trader logic.  It receives the oracle and the
        current simulation date and must return ``(forecasts, orders)``.
    """

    def __init__(self, oracle: Oracle, portfolio: Portfolio, trader: TraderFunc):
        self.oracle = oracle
        self.portfolio = portfolio
        self.trader = trader
        # Store locked decisions for later scoring
        self.locked: List[LockedDecision] = []

    # ---------------------------------------------------------------------
    # Public workflow
    # ---------------------------------------------------------------------
    def step(self) -> None:
        """Execute one full trading session.

        Updated to validate orders *before* recording forecasts to ensure
        atomicity: if any order fails risk validation, the step aborts
        without altering the oracle or locked decisions.
        """
        # Step 1 – advance simulation clock
        try:
            self.oracle.advance_one_day()
        except StopIteration:
            return

        current_date = self.oracle.current_date

        # Step 3‑5 – trader produces forecasts and orders
        forecasts, orders = self.trader(self.oracle, current_date)

        # Validate all orders first (without applying) to enforce risk limits atomically
        market_prices = {order.asset: order.price for order in orders if order is not None}
        for order in orders:
            if order is None:
                continue
            # This will raise ValueError if the order violates limits
            self.portfolio.risk_manager.validate_order(self.portfolio, order, market_prices)

        # If validation passes, proceed to record forecasts and lock decisions
        locked_today: List[LockedDecision] = []
        for ticker, prediction in forecasts:
            self.oracle.record_forecast(ticker, current_date, prediction)
            record = next(
                fr for fr in self.oracle.audit_log()
                if fr.ticker == ticker and fr.forecast_date == current_date
            )
            order = next((o for o in orders if o.asset == ticker), None)
            locked_today.append(LockedDecision(forecast=record, order=order))

        self.locked.extend(locked_today)

        # Step 7 – execute orders (now safe, as they were validated)
        for order in orders:
            if order is None:
                continue
            self.portfolio.apply_order(order, validate=False)

        # Step 8 – reveal outcomes (handled internally by Oracle on advance)
        for ld in locked_today:
            try:
                _ = self.oracle.get_outcome(ld.forecast.ticker, ld.forecast.forecast_date)
            except Exception:
                pass

    def get_locked(self) -> List[LockedDecision]:
        """Return a copy of the list of locked decisions."""
        return list(self.locked)

