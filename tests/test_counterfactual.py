"""Tests for the Counterfactual Investigator module.
"""

import datetime

import pytest

from market_time_machine.counterfactual import CounterfactualInvestigator
from market_time_machine.accounting import Portfolio, Order
from market_time_machine.oracle import Oracle


def setup_scenario(forecast_pred: str, advance_days: int = 1):
    """Create a portfolio, oracle, record a forecast and a buy order.

    Parameters
    ----------
    forecast_pred: prediction string, e.g., "up" or "down".
    advance_days: how many days to advance the oracle after recording.
    """
    oracle = Oracle(start="2020-01-01", end="2020-01-10")
    portfolio = Portfolio()
    ticker = "AAA"
    forecast_date = oracle.current_date
    # Record forecast
    oracle.record_forecast(ticker, forecast_date, prediction=forecast_pred)
    # Apply a buy order of 1 share at current price
    price = oracle.get_price(ticker, forecast_date)
    order = Order(asset=ticker, quantity=1, price=price, sector="Tech")
    portfolio.apply_order(order)
    # Advance the clock the requested number of trading days
    for _ in range(advance_days):
        try:
            oracle.advance_one_day()
        except StopIteration:
            break
    return portfolio, oracle, ticker, forecast_date


def test_counterfactual_up_reasonable():
    portfolio, oracle, ticker, fdate = setup_scenario("up", advance_days=1)
    ci = CounterfactualInvestigator(portfolio, oracle)
    result = ci.analyze(ticker, fdate)
    # With an "up" forecast and a deterministic price increase, the decision is reasonable
    assert result.decision_reasonable is True
    assert result.loss_cause == "none"
    # No loss, so no improvement by changing size or cash
    assert result.position_size_improved is False
    assert result.cash_preferred is False
    # Timing issue should be false (forecast made on current day)
    assert result.timing_issue is False
    # No alternative asset with better outcome
    assert result.alternative_asset is None

def test_counterfactual_down_unreasonable():
    portfolio, oracle, ticker, fdate = setup_scenario("down", advance_days=1)
    ci = CounterfactualInvestigator(portfolio, oracle)
    result = ci.analyze(ticker, fdate)
    # Forecast direction mismatches actual upward move
    assert result.decision_reasonable is False
    assert result.loss_cause == "forecast"
    # Still no loss (outcome positive), so size/cash flags remain False
    assert result.position_size_improved is False
    assert result.cash_preferred is False
    assert result.timing_issue is False
    assert result.alternative_asset is None

def test_counterfactual_timing_issue():
    # Record forecast two days before analysis
    oracle = Oracle(start="2020-01-01", end="2020-01-10")
    portfolio = Portfolio()
    ticker = "AAA"
    forecast_date = oracle.current_date
    oracle.record_forecast(ticker, forecast_date, prediction="up")
    price = oracle.get_price(ticker, forecast_date)
    order = Order(asset=ticker, quantity=1, price=price, sector="Tech")
    portfolio.apply_order(order)
    # Advance two trading days so that timing_issue should be True
    for _ in range(2):
        try:
            oracle.advance_one_day()
        except StopIteration:
            break
    ci = CounterfactualInvestigator(portfolio, oracle)
    result = ci.analyze(ticker, forecast_date)
    assert result.timing_issue is True
    # Other fields follow the "up" scenario
    assert result.decision_reasonable is True
    assert result.loss_cause == "none"
