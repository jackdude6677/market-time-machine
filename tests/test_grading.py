"""Tests for the weekly grading system.

The tests construct a simple scenario with deterministic price series from the
Oracle and a single asset. They verify component scores and the learning bonus.
"""

import datetime
import pytest

from market_time_machine.oracle import Oracle
from market_time_machine.accounting import Portfolio, Order
from market_time_machine.grading import WeeklyGrader, WeekScore


def setup_week(oracle: Oracle, portfolio: Portfolio, start: datetime.date, ticker: str = "AAA"):
    """Record a forecast for *ticker* on *start* and buy one share.

    The forecast predicts an upward move ("up"). The function returns the
    ``Order`` that was applied so the test can verify discipline.
    """
    price = oracle.get_price(ticker, start)
    oracle.record_forecast(ticker, start, {"prediction": "up"})
    order = Order(asset=ticker, quantity=1, price=price, sector="Tech")
    portfolio.apply_order(order)
    return order


def advance_to(oracle: Oracle, target: datetime.date):
    """Advance the oracle day‑by‑day until *target* is the current date."""
    while oracle.current_date < target:
        try:
            oracle.advance_one_day()
        except StopIteration:
            break


def test_weekly_grading_components():
    # Simulation covers two weeks of trading days
    oracle = Oracle(start="2023-01-02", end="2023-01-13")
    portfolio = Portfolio()
    grader = WeeklyGrader(portfolio, oracle)

    # ----- Week 1 -----
    week1_start = datetime.date(2023, 1, 2)  # Monday
    week1_end = datetime.date(2023, 1, 6)    # Friday
    setup_week(oracle, portfolio, week1_start)
    advance_to(oracle, week1_end)
    score1: WeekScore = grader.grade_week(week1_start, week1_end)

    assert score1.net_performance > 0
    assert score1.risk_adjusted == 20.0
    assert score1.drawdown == 20.0
    assert score1.prediction_accuracy == 10.0
    assert score1.discipline == 10.0
    assert score1.learning == 0.0
    assert score1.overall == (
        score1.net_performance + score1.risk_adjusted + score1.drawdown +
        score1.prediction_accuracy + score1.discipline + score1.learning
    )

    # ----- Week 2 -----
    week2_start = datetime.date(2023, 1, 9)  # Next Monday
    week2_end = datetime.date(2023, 1, 13)   # Friday
    setup_week(oracle, portfolio, week2_start)
    advance_to(oracle, week2_end)
    score2: WeekScore = grader.grade_week(week2_start, week2_end)

    assert score2.learning == 5.0
    assert score2.risk_adjusted == 20.0
    assert score2.drawdown == 20.0
    assert score2.prediction_accuracy == 10.0
    assert score2.discipline == 10.0
    assert score2.net_performance > 0
    assert score2.overall == (
        score2.net_performance + score2.risk_adjusted + score2.drawdown +
        score2.prediction_accuracy + score2.discipline + score2.learning
    )
