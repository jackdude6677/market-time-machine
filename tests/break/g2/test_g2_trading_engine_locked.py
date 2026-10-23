import datetime
import pytest

from market_time_machine.oracle import Oracle
from market_time_machine.accounting import Portfolio, Order
from market_time_machine.trading_engine import TradingEngine

def trader_invalid_order(oracle: Oracle, current_date: datetime.date):
    """Trader that creates an order exceeding cash, causing validation failure.
    """
    ticker = "AAA"
    price = oracle.get_price(ticker, current_date)
    forecast = [(ticker, {"prediction": "up"})]
    # Order quantity 10 will exceed cash (price ~100)
    order = Order(asset=ticker, quantity=10, price=price, sector="Tech")
    return forecast, [order]

def test_locked_decisions_not_added_on_order_failure():
    oracle = Oracle(start="2023-01-02", end="2023-01-05")
    portfolio = Portfolio(initial_cash=1000.0)
    engine = TradingEngine(oracle, portfolio, trader_invalid_order)
    # Expect the step to raise a ValueError due to insufficient cash.
    with pytest.raises(ValueError):
        engine.step()
    # After failure, no locked decisions should be recorded.
    assert engine.get_locked() == [], "Locked decisions should be empty after order validation failure"
