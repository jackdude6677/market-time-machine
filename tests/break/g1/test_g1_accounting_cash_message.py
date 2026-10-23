"""Break test for cash insufficient error message.

The specification and existing unit tests expect a ``ValueError`` containing the phrase
``Insufficient cash`` when an order would overdraw the portfolio. The current
implementation raises ``Leverage is disabled`` because the cash‑check logic is
duplicated and the first condition triggers. This test should therefore fail.
"""

import pytest
from market_time_machine.accounting import Portfolio, Order


def test_insufficient_cash_error_message():
    p = Portfolio()
    # Attempt to buy more than available cash.
    order = Order(asset="XYZ", quantity=200, price=10.0)
    with pytest.raises(ValueError, match="Insufficient cash"):
        p.apply_order(order)
