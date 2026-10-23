import datetime
import pytest
from market_time_machine.oracle import Oracle
from market_time_machine.accounting import Portfolio, Order
from market_time_machine.trading_engine import TradingEngine

def simple_trader(oracle: Oracle, current_date: datetime.date):
    ticker = "AAA"
    price = oracle.get_price(ticker, current_date)
    forecast = [(ticker, {"prediction": "up"})]
    order = Order(asset=ticker, quantity=1, price=price, sector="Tech")
    return forecast, [order]

def test_locked_decision_forecast_mutable():
    """LockedDecision should protect its ForecastRecord from mutation.

    The test mutates the ``prediction`` field of the stored forecast and
    expects the mutation to be prevented (e.g., by raising an error or
    leaving the original unchanged). The current implementation stores a
    mutable ``ForecastRecord`` which allows the change, so this test will
    fail.
    """
    oracle = Oracle(start="2023-01-02", end="2023-01-05")
    portfolio = Portfolio(initial_cash=1000.0)
    engine = TradingEngine(oracle, portfolio, simple_trader)
    engine.step()
    ld = engine.get_locked()[0]
    # Attempt to mutate the forecast prediction – should raise or have no effect.
    original = ld.forecast.prediction.copy()
    ld.forecast.prediction = {"prediction": "down"}
    # If mutation succeeded, the original dict will be replaced.
    assert ld.forecast.prediction == original, "ForecastRecord should be immutable"
