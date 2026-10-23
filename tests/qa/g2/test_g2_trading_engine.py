"""Additional tests for the Trading Decision Engine.

These tests focus on requirements that are *not* covered by the existing
unit tests in ``tests/test_trading_engine.py``.  In particular we verify
that the engine respects risk limits and that forecasts cannot be recorded
for dates beyond the simulation horizon.
"""

import datetime

import pytest

from market_time_machine.oracle import Oracle
from market_time_machine.accounting import Portfolio, Order, RiskLimits
from market_time_machine.trading_engine import TradingEngine, LockedDecision


def trader_exceed_position_limit(oracle: Oracle, current_date: datetime.date):
    """Trader that tries to buy a position exceeding the 5% position limit.

    The portfolio starts with $1,000 cash and the price series starts at 100.
    Buying 1 share costs $100, which is exactly the 10% of equity – still
    within the default 5% limit, so we request 10 shares (cost $1,000) which
    would exceed the 5% ($50) limit.
    """
    ticker = "AAA"
    price = oracle.get_price(ticker, current_date)
    forecast = [(ticker, {"prediction": "up"})]
    # Attempt to buy 10 shares (value $1000) – exceeds 5% limit of $50.
    order = Order(asset=ticker, quantity=10, price=price, sector="Tech")
    return forecast, [order]


def test_risk_limit_enforced_by_trading_engine():
    # Oracle covering a few days
    oracle = Oracle(start="2023-01-02", end="2023-01-10")
    # Portfolio with default RiskLimits (5% max_position_pct)
    portfolio = Portfolio(initial_cash=1000.0)
    engine = TradingEngine(oracle, portfolio, trader_exceed_position_limit)
    # The engine validates risk limits; exceeding the limit should raise ValueError.
    with pytest.raises(ValueError, match="Position size exceeds limit"):
        engine.step()


def test_forecast_cannot_be_recorded_past_simulation_end():
    oracle = Oracle(start="2023-01-02", end="2023-01-05")
    # Attempt to record a forecast for a date beyond the end date.
    future_date = datetime.date(2023, 1, 10)
    with pytest.raises(PermissionError):
        oracle.record_forecast("AAA", future_date, {"prediction": "up"})

# The LockedDecision dataclass is mutable; ensure that modifications affect the object.
def test_locked_decision_is_immutable():
    """LockedDecision should be immutable – attempts to modify raise.

    The original test expected mutability, but the specification requires
    auditability, so the dataclass is frozen.  We verify that mutation
    raises ``dataclasses.FrozenInstanceError``.
    """
    from dataclasses import FrozenInstanceError
    oracle = Oracle(start="2023-01-02", end="2023-01-05")
    portfolio = Portfolio(initial_cash=1000.0)
    def simple_trader(o: Oracle, d: datetime.date):
        ticker = "AAA"
        price = o.get_price(ticker, d)
        return [(ticker, {"prediction": "up"})], [Order(asset=ticker, quantity=1, price=price, sector="Tech")]
    engine = TradingEngine(oracle, portfolio, simple_trader)
    engine.step()
    ld = engine.get_locked()[0]
    # Attempt to modify the forecast prediction – should raise.
    with pytest.raises(FrozenInstanceError):
        ld.forecast.prediction = {"prediction": "down"}
