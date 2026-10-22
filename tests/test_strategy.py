import pytest
from datetime import datetime, timedelta

from market_time_machine.strategy_engine import StrategyEngine, Strategy, Experiment


def test_create_and_modify_strategy():
    engine = StrategyEngine()
    strat = engine.create_strategy(hypothesis="test hypothesis")
    assert isinstance(strat, Strategy)
    assert strat.version == 1
    # modify creates new version
    new_strat = engine.modify_strategy(strat.id, hypothesis="new hypothesis", horizon=5)
    assert new_strat.version == 2
    assert new_strat.hypothesis == "new hypothesis"
    assert new_strat.horizon == 5
    # original unchanged
    orig = engine.get_strategy(strat.id, version=1)
    assert orig.hypothesis == "test hypothesis"
    assert orig.horizon == 1


def test_experiment_logging_and_retrieval():
    engine = StrategyEngine()
    strat = engine.create_strategy(hypothesis="exp test")
    now = datetime.utcnow()
    exp = engine.log_experiment(
        strategy_id=strat.id,
        hypothesis="exp test",
        data_cutoff=now - timedelta(days=1),
        model_version="v1",
        validation_period="30d",
        results={"passed": True, "metric": 0.5},
        decision="accept",
    )
    assert isinstance(exp, Experiment)
    assert exp.results["passed"] is True
    all_exps = engine.get_experiments()
    assert len(all_exps) == 1
    assert all_exps[0] == exp
    filtered = engine.get_experiments(strategy_id=strat.id)
    assert filtered == [exp]


def test_champion_and_challenger_flow():
    engine = StrategyEngine()
    # create initial champion
    champ = engine.create_strategy(hypothesis="champion")
    engine.set_champion(champ.id)
    assert engine.get_champion() == champ
    assert engine.get_baseline() == champ
    # create challenger and log passing experiment
    challenger = engine.create_strategy(hypothesis="challenger")
    engine.add_challenger(challenger.id)
    engine.log_experiment(
        strategy_id=challenger.id,
        hypothesis="challenger",
        data_cutoff=datetime.utcnow(),
        model_version="v1",
        validation_period="30d",
        results={"passed": True},
        decision="accept",
    )
    # promote challenger
    engine.promote_challenger(challenger.id)
    assert engine.get_champion() == challenger


def test_promote_without_passing_experiment_raises():
    engine = StrategyEngine()
    champ = engine.create_strategy(hypothesis="c")
    engine.set_champion(champ.id)
    challenger = engine.create_strategy(hypothesis="bad")
    engine.add_challenger(challenger.id)
    # log failing experiment
    engine.log_experiment(
        strategy_id=challenger.id,
        hypothesis="bad",
        data_cutoff=datetime.utcnow(),
        model_version="v1",
        validation_period="30d",
        results={"passed": False},
        decision="reject",
    )
    with pytest.raises(ValueError, match="Challenger has not passed validation"):
        engine.promote_challenger(challenger.id)


def test_invalid_operations_raise():
    engine = StrategyEngine()
    with pytest.raises(ValueError):
        engine.modify_strategy(999)
    with pytest.raises(ValueError):
        engine.log_experiment(
            strategy_id=999,
            hypothesis="x",
            data_cutoff=datetime.utcnow(),
            model_version="v",
            validation_period="30d",
            results={"passed": True},
            decision="accept",
        )
    # delete attribute should raise AttributeError
    with pytest.raises(AttributeError):
        del engine._strategies
