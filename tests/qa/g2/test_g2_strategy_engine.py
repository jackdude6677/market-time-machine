"""Additional tests for the Self‑Discovering Strategy Engine.

These tests extend the coverage of ``tests/test_strategy.py`` by checking
behaviour that is not exercised there, such as duplicate challenger handling
and error conditions for promotion.
"""

import pytest
from datetime import datetime, timedelta

from market_time_machine.strategy_engine import StrategyEngine, Strategy, Experiment


def test_duplicate_challenger_is_ignored():
    engine = StrategyEngine()
    strat = engine.create_strategy(hypothesis="base")
    engine.add_challenger(strat.id)
    # Adding the same challenger again should not raise and should not duplicate.
    engine.add_challenger(strat.id)
    challengers = engine.get_challengers()
    assert len(challengers) == 1
    assert challengers[0].id == strat.id


def test_promote_without_challenger_in_pool_raises():
    engine = StrategyEngine()
    champ = engine.create_strategy(hypothesis="champ")
    engine.set_champion(champ.id)
    challenger = engine.create_strategy(hypothesis="chall")
    # Log a passing experiment but do NOT add to challenger pool.
    engine.log_experiment(
        strategy_id=challenger.id,
        hypothesis="chall",
        data_cutoff=datetime.utcnow(),
        model_version="v1",
        validation_period="30d",
        results={"passed": True},
        decision="accept",
    )
    with pytest.raises(ValueError, match="Strategy is not in the challenger pool"):
        engine.promote_challenger(challenger.id)


def test_modify_nonexistent_strategy_raises():
    engine = StrategyEngine()
    with pytest.raises(ValueError, match="Strategy id 999 does not exist"):
        engine.modify_strategy(999, hypothesis="new")


def test_get_champion_returns_none_when_not_set():
    engine = StrategyEngine()
    assert engine.get_champion() is None


def test_get_history_accumulates_champions():
    engine = StrategyEngine()
    # First champion
    champ1 = engine.create_strategy(hypothesis="c1")
    engine.set_champion(champ1.id)
    # Second champion via challenger promotion
    champ2 = engine.create_strategy(hypothesis="c2")
    engine.add_challenger(champ2.id)
    engine.log_experiment(
        strategy_id=champ2.id,
        hypothesis="c2",
        data_cutoff=datetime.utcnow(),
        model_version="v1",
        validation_period="30d",
        results={"passed": True},
        decision="accept",
    )
    engine.promote_challenger(champ2.id)
    history = engine.get_history()
    assert len(history) == 1
    assert history[0].id == champ1.id
