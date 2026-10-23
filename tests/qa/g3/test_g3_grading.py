"""QA tests for the Weekly Grading System (milestone 6).
These tests verify edge‑case behaviour required by the specification:
* Zero volatility should yield 0 risk‑adjusted points.
* Plain‑string predictions ("up"/"down") are interpreted as direction.
* Discipline points are awarded only when a forecast has a matching position.
* Learning bonus is granted only when the net return improves over the previous week.
"""

import datetime
import pytest

from market_time_machine.grading import WeeklyGrader, WeekScore
from market_time_machine.accounting import Portfolio, Order
from market_time_machine.oracle import Oracle

@pytest.fixture
def portfolio():
    return Portfolio(initial_cash=1000.0)

@pytest.fixture
def oracle():
    # Short simulation covering two weeks of trading days.
    return Oracle(start="2023-01-02", end="2023-01-20")

def advance_to(oracle: Oracle, target: datetime.date):
    while oracle.current_date < target:
        try:
            oracle.advance_one_day()
        except StopIteration:
            break

def record_forecast_and_order(oracle, portfolio, date, ticker="AAA", direction="up", qty=1):
    """Record a forecast and place an order.

    The Oracle enforces a strict information firewall: forecasts can only be
    recorded on or before the current simulation date.  This helper advances the
    simulation clock as needed so the caller can specify any trading date within
    the simulation range.
    """
    # Advance the oracle to the forecast date if necessary.
    while oracle.current_date < date:
        try:
            oracle.advance_one_day()
        except StopIteration:
            break
    # Record a forecast with plain string prediction.
    oracle.record_forecast(ticker, date, direction)
    price = oracle.get_price(ticker, date)
    order = Order(asset=ticker, quantity=qty, price=price, sector="Tech")
    portfolio.apply_order(order)
    return order

def test_risk_adjusted_zero_volatility_returns_zero_points(portfolio, oracle):
    # No trades, equity stays constant → zero volatility.
    start = datetime.date(2023, 1, 2)
    end = datetime.date(2023, 1, 6)
    grader = WeeklyGrader(portfolio, oracle)
    score: WeekScore = grader.grade_week(start, end)
    assert score.risk_adjusted == pytest.approx(0.0, abs=1e-6)

def test_prediction_accuracy_handles_string_predictions(portfolio, oracle):
    # Record a forecast with plain string "up" and a matching order.
    forecast_date = datetime.date(2023, 1, 3)
    record_forecast_and_order(oracle, portfolio, forecast_date, "up", qty=1)
    # Advance to make outcome known.
    advance_to(oracle, forecast_date)
    start = datetime.date(2023, 1, 2)
    end = datetime.date(2023, 1, 6)
    grader = WeeklyGrader(portfolio, oracle)
    score: WeekScore = grader.grade_week(start, end)
    # One correct prediction → >0 points (scaled to 10).
    assert score.prediction_accuracy > 0.0

def test_discipline_points_awarded_only_with_position(portfolio, oracle):
    # Forecast without creating a position.
    forecast_date = datetime.date(2023, 1, 4)
    oracle.record_forecast("BBB", forecast_date, "up")
    # No order applied.
    start = datetime.date(2023, 1, 2)
    end = datetime.date(2023, 1, 6)
    grader = WeeklyGrader(portfolio, oracle)
    score: WeekScore = grader.grade_week(start, end)
    assert score.discipline == pytest.approx(0.0)

def test_learning_bonus_given_when_return_improves(portfolio, oracle):
    grader = WeeklyGrader(portfolio, oracle)
    # Week 1: no return (no trades).
    w1_start = datetime.date(2023, 1, 2)
    w1_end = datetime.date(2023, 1, 6)
    score1 = grader.grade_week(w1_start, w1_end)
    assert score1.learning == 0.0
    # Week 2: make a profitable trade.
    trade_date = datetime.date(2023, 1, 9)
    record_forecast_and_order(oracle, portfolio, trade_date, "up", qty=1)
    advance_to(oracle, datetime.date(2023, 1, 13))
    w2_start = datetime.date(2023, 1, 9)
    w2_end = datetime.date(2023, 1, 13)
    score2 = grader.grade_week(w2_start, w2_end)
    assert score2.learning == pytest.approx(5.0)
