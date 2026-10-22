"""Tests for the portfolio accounting and risk management module.
"""

import pytest
from market_time_machine.accounting import (
    Portfolio,
    Order,
    RiskLimits,
)

# Helper market price dict
def price_dict(**prices):
    return prices

def test_initial_portfolio():
    p = Portfolio()
    assert p.cash == 1000.0
    assert p.equity({}) == 1000.0
    assert p.realized_pnl == 0.0

def test_buy_within_limits():
    p = Portfolio()
    # price $10, buying 5 shares costs $50, within 5% position limit ($50)
    order = Order(asset="AAA", quantity=5, price=10.0, sector="Tech")
    p.apply_order(order)
    pos = p.get_position("AAA")
    assert pos.quantity == 5
    assert pos.avg_cost == 10.0
    assert p.cash == 1000.0 - 5 * 10.0
    # equity with same price
    assert p.equity({"AAA": 10.0}) == 1000.0

def test_buy_exceeds_cash():
    p = Portfolio()
    order = Order(asset="BBB", quantity=200, price=10.0)  # $2000 > cash
    with pytest.raises(ValueError, match="Insufficient cash"):
        p.apply_order(order)

def test_position_limit():
    p = Portfolio()
    # default max position 5% of equity = $50
    # buying 6 shares at $10 = $60 exceeds limit
    order = Order(asset="CCC", quantity=6, price=10.0, sector="Health")
    with pytest.raises(ValueError, match="Position size exceeds limit"):
        p.apply_order(order)

def test_sector_limit():
    limits = RiskLimits(max_sector_pct=0.10)  # 10% sector limit
    p = Portfolio(risk_limits=limits)
    # First buy within sector limit
    order1 = Order(asset="DDD", quantity=3, price=10.0, sector="Energy")
    p.apply_order(order1)
    # Second order would push sector exposure >10% ($30 > $100 equity *0.10)
    order2 = Order(asset="EEE", quantity=2, price=10.0, sector="Energy")
    with pytest.raises(ValueError, match="Sector exposure exceeds limit"):
        p.apply_order(order2)

def test_gross_exposure_limit():
    limits = RiskLimits(max_gross_exposure_pct=0.5)  # 50% gross exposure
    p = Portfolio(risk_limits=limits)
    # Buying $600 worth exceeds 50% of $1000 equity
    order = Order(asset="FFF", quantity=60, price=10.0, sector="Finance")
    with pytest.raises(ValueError, match="Gross exposure exceeds limit"):
        p.apply_order(order)

def test_short_not_allowed():
    p = Portfolio()
    order = Order(asset="GGG", quantity=-5, price=10.0)
    with pytest.raises(ValueError, match="Short selling is disabled"):
        p.apply_order(order)

def test_realized_and_unrealized_pnl():
    p = Portfolio()
    # Buy 10 shares at $10
    buy = Order(asset="HHH", quantity=10, price=10.0, sector="Tech")
    p.apply_order(buy)
    # Unrealized P&L with price $12 should be $20
    assert p.unrealized_pnl({"HHH": 12.0}) == 20.0
    # Sell 5 shares at $12, transaction cost $0
    sell = Order(asset="HHH", quantity=-5, price=12.0)
    p.apply_order(sell)
    # Realized P&L = (12-10)*5 = $10
    assert p.realized_pnl == 10.0
    # Remaining position 5 shares avg cost $10, price $12 unrealized $10
    assert p.unrealized_pnl({"HHH": 12.0}) == 10.0
    # Equity = cash + market value of remaining shares
    expected_cash = 1000.0 - 10*10.0 + 5*12.0  # cash after buy and sell
    assert p.cash == expected_cash
    assert p.equity({"HHH": 12.0}) == expected_cash + 5*12.0

