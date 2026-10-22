import datetime

import pytest

from market_time_machine.oracle import Oracle
from market_time_machine.accounting import Portfolio, Order
from market_time_machine.trading_engine import TradingEngine


def simple_trader(oracle: Oracle, current_date: datetime.date):
    """Trader that always forecasts and buys one share of AAA."""
    ticker = "AAA"
    price = oracle.get_price(ticker, current_date)
    forecast = [(ticker, {"prediction": "up"})]
    order = Order(asset=ticker, quantity=1, price=price, sector="Tech")
    return forecast, [order]


def test_trading_engine_two_steps():
    # Oracle from Monday to Thursday
    oracle = Oracle(start="2023-01-02", end="2023-01-05")
    portfolio = Portfolio(initial_cash=1000.0)
    engine = TradingEngine(oracle, portfolio, simple_trader)

    # First step: record forecast and execute order
    engine.step()
    assert len(engine.get_locked()) == 1
    ld1 = engine.get_locked()[0]
    # Position should have 1 share
    pos = portfolio.get_position("AAA")
    assert pos.quantity == 1
    # Outcome not yet available
    with pytest.raises(ValueError):
        oracle.get_outcome(ld1.forecast.ticker, ld1.forecast.forecast_date)

    # Second step: advance, resolve first outcome, record second forecast
    engine.step()
    assert len(engine.get_locked()) == 2
    ld2 = engine.get_locked()[1]
    # Position now has 2 shares
    pos = portfolio.get_position("AAA")
    assert pos.quantity == 2
    # First forecast outcome should be resolved (price increased by 1)
    outcome = oracle.get_outcome(ld1.forecast.ticker, ld1.forecast.forecast_date)
    assert outcome == 1  # price increments by 1 each day

    # Second forecast outcome not yet available
    with pytest.raises(ValueError):
        oracle.get_outcome(ld2.forecast.ticker, ld2.forecast.forecast_date)
