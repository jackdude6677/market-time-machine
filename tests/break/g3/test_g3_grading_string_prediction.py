```python
"""Break test: WeeklyGrader should count plain‑string predictions.

The grading spec expects that a forecast whose prediction is the string
"up" or "down" is treated like a directional forecast. The implementation
only recognises dict‑based predictions or numeric values, so this test
expects a non‑zero prediction‑accuracy score but will receive 0, causing a
failure.
"""

import datetime

import pytest

from market_time_machine.oracle import Oracle
from market_time_machine.accounting import Portfolio, Order
from market_time_machine.grading import WeeklyGrader, WeekScore


def setup_week_with_string_pred(oracle: Oracle, portfolio: Portfolio,
                                start: datetime.date, ticker: str = "AAA"):
    """Record a plain‑string forecast and buy one share."""
    price = oracle.get_price(ticker, start)
    # Record a plain string prediction instead of a dict
    oracle.record_forecast(ticker, start, "up")
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


def test_prediction_accuracy_counts_string_predictions():
    oracle = Oracle(start="2023-01-02", end="2023-01-06")
    portfolio = Portfolio()
    grader = WeeklyGrader(portfolio, oracle)

    week_start = datetime.date(2023, 1, 2)
    week_end = datetime.date(2023, 1, 6)

    setup_week_with_string_pred(oracle, portfolio, week_start)
    advance_to(oracle, week_end)

    score: WeekScore = grader.grade_week(week_start, week_end)

    # Expect the prediction accuracy to be 10 points (1 correct out of 1)
    assert score.prediction_accuracy == 10.0
```
