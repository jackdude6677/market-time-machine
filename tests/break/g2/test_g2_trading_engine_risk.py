import datetime
import pytest

from market_time_machine.oracle import Oracle
from market_time_machine.accounting import Portfolio, Order
from market_time_machine.trading_engine import TradingEngine

def trader_exceed_cash_limit(oracle: Oracle, current_date: datetime.date):
    """Trader that attempts to buy more shares than cash allows.

    After the engine advances the date, the price will be 101 (second day).
    Buying 10 shares costs 1010, exceeding the initial cash of 1000.
    The engine currently validates orders, raising an error.
    The test expects the order to be applied regardless, resulting in
    negative cash.
    """
    ticker = "AAA"
    price = oracle.get_price(ticker, current_date)
    forecast = [(ticker, {"prediction": "up"})]
    order = Order(asset=ticker, quantity=10, price=price, sector="Tech")
    return forecast, [order]

def test_order_applied_despite_insufficient_cash():
    oracle = Oracle(start="2023-01-02", end="2023-01-05")
    portfolio = Portfolio(initial_cash=1000.0)
    engine = TradingEngine(oracle, portfolio, trader_exceed_cash_limit)
    # The engine should not raise; after step cash will be negative.
    engine.step()
    # Expect the order to have been applied, cash should be negative.
    assert portfolio.cash < 0, "Cash should be negative after applying order without validation"
    pos = portfolio.get_position("AAA")
    assert pos.quantity == 10
