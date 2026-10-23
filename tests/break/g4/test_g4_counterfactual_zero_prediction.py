"""Breaker test for CounterfactualInvestigator handling of zero predictions.

The CounterfactualInvestigator currently treats a numeric prediction of ``0`` as
"down". For a flat outcome (price change zero) the correct behaviour would be
to consider the prediction as "flat", making the decision reasonable. This test
expects ``decision_reasonable`` to be ``True`` and ``loss_cause`` to be
"none", so it should fail with the existing implementation.
"""

import datetime
import pytest

from market_time_machine.counterfactual import CounterfactualInvestigator
from market_time_machine.accounting import Portfolio, Order
from market_time_machine.oracle import Oracle


def setup_flat_scenario():
    """Create a portfolio and oracle where the price does not change.

    The Oracle normally increments price by 1 each day, so we monkey‑patch the
    price function to return a constant value, yielding a flat outcome.
    """
    oracle = Oracle(start="2020-01-01", end="2020-01-03")
    # Patch the price method to always return 100.0
    def constant_price(self, ticker, date):
        return 100.0
    # Bind the method to the instance
    oracle._price_for_date = constant_price.__get__(oracle, Oracle)  # type: ignore
    portfolio = Portfolio()
    ticker = "AAA"
    forecast_date = oracle.current_date
    # Record a zero numeric prediction
    oracle.record_forecast(ticker, forecast_date, prediction=0)
    # Apply a buy order of 1 share at the constant price
    price = oracle.get_price(ticker, forecast_date)
    order = Order(asset=ticker, quantity=1, price=price, sector="Tech")
    portfolio.apply_order(order)
    # Advance one day so the outcome (price change) becomes known
    oracle.advance_one_day()
    return portfolio, oracle, ticker, forecast_date


def test_counterfactual_zero_prediction_flat_outcome():
    portfolio, oracle, ticker, fdate = setup_flat_scenario()
    ci = CounterfactualInvestigator(portfolio, oracle)
    result = ci.analyze(ticker, fdate)
    # Expect the decision to be considered reasonable (flat prediction matches flat outcome)
    assert result.decision_reasonable is True, "Zero prediction should be treated as flat"
    assert result.loss_cause == "none"
    # No loss, so size and cash flags should be False
    assert result.position_size_improved is False
    assert result.cash_preferred is False
    # Timing issue should be False (forecast made on current day)
    assert result.timing_issue is False
