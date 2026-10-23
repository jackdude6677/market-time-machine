"""Tests for Portfolio accounting and risk management per specification.

- Initial cash must be exactly $1000.
- Buying shares updates cash, position, avg cost.
- Risk limits: max position 5% of equity, no short, no leverage.
- Orders exceeding cash should be rejected.
"""

import pytest

from market_time_machine.accounting import Order, Portfolio, RiskLimits


def test_initial_portfolio_cash():
    p = Portfolio(initial_cash=1000.0)
    assert p.cash == 1000.0
    # No positions initially
    assert p.positions == {}


def test_buy_shares_updates_position_and_cash():
    # Use relaxed risk limits to allow the purchase.
    limits = RiskLimits(max_position_pct=1.0)  # 100% of equity
    p = Portfolio(initial_cash=1000.0, risk_limits=limits)
    order = Order(asset="AAPL", quantity=5, price=100.0, transaction_cost=1.0)
    p.apply_order(order)
    pos = p.get_position("AAPL")
    assert pos.quantity == 5
    assert pos.avg_cost == 100.0
    # Cash decreased by 5*100 + 1 transaction cost
    assert p.cash == pytest.approx(1000.0 - 5*100.0 - 1.0)
    # Realized P&L should reflect transaction cost as negative
    assert p.realized_pnl == pytest.approx(-1.0)


def test_sell_shares_realizes_profit_and_updates_cash():
    p = Portfolio(initial_cash=1000.0, risk_limits=RiskLimits(max_position_pct=1.0))
    # Buy first
    p.apply_order(Order(asset="AAPL", quantity=10, price=50.0, transaction_cost=0.0))
    # Sell some at higher price
    p.apply_order(Order(asset="AAPL", quantity=-5, price=60.0, transaction_cost=0.0))
    pos = p.get_position("AAPL")
    assert pos.quantity == 5
    # Profit = (60-50)*5 = 50
    assert p.realized_pnl == pytest.approx(50.0)
    # Cash increased by proceeds
    expected_cash = 1000.0 - 10*50.0 + 5*60.0
    assert p.cash == pytest.approx(expected_cash)


def test_risk_limit_position_size_exceeds_5_percent():
    limits = RiskLimits(max_position_pct=0.05)
    p = Portfolio(initial_cash=1000.0, risk_limits=limits)
    # Equity before order = cash = 1000
    # 5% of equity = 50, so buying >50 value should be rejected
    with pytest.raises(ValueError, match="Position size exceeds limit"):
        p.apply_order(Order(asset="AAPL", quantity=1, price=60.0, transaction_cost=0.0))
    # Buying exactly 0.5 shares at $100 (value 50) should be allowed
    p.apply_order(Order(asset="AAPL", quantity=0.5, price=100.0, transaction_cost=0.0))
    assert p.get_position("AAPL").quantity == 0.5


def test_no_short_selling_by_default():
    p = Portfolio(initial_cash=1000.0)
    # Attempt to sell without holdings should raise short-selling error
    with pytest.raises(ValueError, match="Short selling is disabled"):
        p.apply_order(Order(asset="AAPL", quantity=-1, price=100.0, transaction_cost=0.0))


def test_order_exceeding_cash_is_rejected():
    p = Portfolio(initial_cash=100.0)
    # Buying costing more than cash (including transaction cost) should fail
    with pytest.raises(ValueError, match="Insufficient cash"):
        p.apply_order(Order(asset="AAPL", quantity=2, price=60.0, transaction_cost=0.0))
