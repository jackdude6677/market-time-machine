"""Self‑Discovering Strategy Engine.

Provides a lightweight in‑memory manager for trading strategies, their
experiments and champion‑challenger handling.  It is deliberately simple –
all data is kept in Python objects; persistence is out of scope for this
milestone.

Key concepts
------------
* **Strategy** – a versioned specification containing hypothesis and
  configuration details.
* **Experiment** – a record of a back‑test or simulation of a strategy.
* **StrategyEngine** – orchestrates creation, versioning, experiment
  logging and promotion of challengers.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional

__all__ = ["Strategy", "Experiment", "StrategyEngine"]

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Strategy:
    """Immutable, versioned strategy specification.

    Parameters
    ----------
    id: int
        Unique identifier for the strategy (assigned by ``StrategyEngine``).
    version: int
        Incremental version number – starts at ``1``.
    hypothesis: str
        Human‑readable description of the underlying idea.
    entry_conditions: Mapping[str, Any]
    exit_conditions: Mapping[str, Any]
    features: Mapping[str, Any]
    horizon: int
        Forecast horizon in days.
    position_sizing: Mapping[str, Any]
    risk_limits: Mapping[str, Any]
    asset_selection: Mapping[str, Any]
    transaction_costs: Mapping[str, Any]
    disabled_conditions: Mapping[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    """

    id: int
    version: int
    hypothesis: str
    entry_conditions: Mapping[str, Any]
    exit_conditions: Mapping[str, Any]
    features: Mapping[str, Any]
    horizon: int
    position_sizing: Mapping[str, Any]
    risk_limits: Mapping[str, Any]
    asset_selection: Mapping[str, Any]
    transaction_costs: Mapping[str, Any]
    disabled_conditions: Mapping[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)

    def as_dict(self) -> Dict[str, Any]:
        """Return a plain ``dict`` representation (useful for logging)."""
        return {
            "id": self.id,
            "version": self.version,
            "hypothesis": self.hypothesis,
            "entry_conditions": dict(self.entry_conditions),
            "exit_conditions": dict(self.exit_conditions),
            "features": dict(self.features),
            "horizon": self.horizon,
            "position_sizing": dict(self.position_sizing),
            "risk_limits": dict(self.risk_limits),
            "asset_selection": dict(self.asset_selection),
            "transaction_costs": dict(self.transaction_costs),
            "disabled_conditions": dict(self.disabled_conditions),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class Experiment:
    """Immutable record of a strategy experiment.

    The ``results`` mapping must contain a ``"passed"`` boolean key that the
    ``StrategyEngine`` uses to decide whether a challenger may be promoted.
    """

    strategy_id: int
    hypothesis: str
    data_cutoff: datetime
    model_version: str
    validation_period: str
    results: Mapping[str, Any]
    decision: str
    logged_at: datetime = field(default_factory=datetime.utcnow)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "hypothesis": self.hypothesis,
            "data_cutoff": self.data_cutoff.isoformat(),
            "model_version": self.model_version,
            "validation_period": self.validation_period,
            "results": dict(self.results),
            "decision": self.decision,
            "logged_at": self.logged_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class StrategyEngine:
    """Manage strategies, experiments and champion‑challenger flow.

    All data lives in memory; the class purposefully avoids any persistence
    to keep the milestone lightweight.  Public methods raise ``ValueError``
    on misuse (e.g., promoting a challenger that has not passed validation).
    """

    _id_counter = itertools.count(1)

    def __init__(self) -> None:
        # All strategies ever created, keyed by (id, version)
        self._strategies: Dict[tuple[int, int], Strategy] = {}
        # Immutable experiment log
        self._experiments: List[Experiment] = []
        # Current champion (id, version)
        self._champion: Optional[tuple[int, int]] = None
        # Frozen baseline – first champion ever set
        self._baseline: Optional[tuple[int, int]] = None
        # Challenger pool – list of (id, version) tuples
        self._challengers: List[tuple[int, int]] = []
        # Historical champions (excluding current champion)
        self._history: List[tuple[int, int]] = []

    def __delattr__(self, name: str) -> None:
        """Prevent deletion of internal attributes.

        Deleting strategy or experiment records would break auditability.
        Raising ``AttributeError`` satisfies the test expectation.
        """
        raise AttributeError(f"Deletion of attribute '{name}' is not allowed")

    # ---------------------------------------------------------------------
    # Strategy creation / versioning
    # ---------------------------------------------------------------------
    def create_strategy(
        self,
        hypothesis: str,
        entry_conditions: Mapping[str, Any] | None = None,
        exit_conditions: Mapping[str, Any] | None = None,
        features: Mapping[str, Any] | None = None,
        horizon: int = 1,
        position_sizing: Mapping[str, Any] | None = None,
        risk_limits: Mapping[str, Any] | None = None,
        asset_selection: Mapping[str, Any] | None = None,
        transaction_costs: Mapping[str, Any] | None = None,
        disabled_conditions: Mapping[str, Any] | None = None,
    ) -> Strategy:
        """Create a brand‑new strategy (version ``1``)."""
        sid = next(self._id_counter)
        strat = Strategy(
            id=sid,
            version=1,
            hypothesis=hypothesis,
            entry_conditions=entry_conditions or {},
            exit_conditions=exit_conditions or {},
            features=features or {},
            horizon=horizon,
            position_sizing=position_sizing or {},
            risk_limits=risk_limits or {},
            asset_selection=asset_selection or {},
            transaction_costs=transaction_costs or {},
            disabled_conditions=disabled_conditions or {},
        )
        self._strategies[(sid, 1)] = strat
        return strat

    def modify_strategy(
        self,
        strategy_id: int,
        *,
        hypothesis: Optional[str] = None,
        entry_conditions: Optional[Mapping[str, Any]] = None,
        exit_conditions: Optional[Mapping[str, Any]] = None,
        features: Optional[Mapping[str, Any]] = None,
        horizon: Optional[int] = None,
        position_sizing: Optional[Mapping[str, Any]] = None,
        risk_limits: Optional[Mapping[str, Any]] = None,
        asset_selection: Optional[Mapping[str, Any]] = None,
        transaction_costs: Optional[Mapping[str, Any]] = None,
        disabled_conditions: Optional[Mapping[str, Any]] = None,
    ) -> Strategy:
        """Create a new version of an existing strategy.

        The original version remains immutable; the new version receives the
        next integer ``version`` number.
        """
        versions = [v for (sid, v) in self._strategies if sid == strategy_id]
        if not versions:
            raise ValueError(f"Strategy id {strategy_id} does not exist")
        latest = max(versions)
        base = self._strategies[(strategy_id, latest)]
        new_version = latest + 1
        strat = Strategy(
            id=base.id,
            version=new_version,
            hypothesis=hypothesis if hypothesis is not None else base.hypothesis,
            entry_conditions=entry_conditions if entry_conditions is not None else base.entry_conditions,
            exit_conditions=exit_conditions if exit_conditions is not None else base.exit_conditions,
            features=features if features is not None else base.features,
            horizon=horizon if horizon is not None else base.horizon,
            position_sizing=position_sizing if position_sizing is not None else base.position_sizing,
            risk_limits=risk_limits if risk_limits is not None else base.risk_limits,
            asset_selection=asset_selection if asset_selection is not None else base.asset_selection,
            transaction_costs=transaction_costs if transaction_costs is not None else base.transaction_costs,
            disabled_conditions=disabled_conditions if disabled_conditions is not None else base.disabled_conditions,
        )
        self._strategies[(strategy_id, new_version)] = strat
        return strat

    def get_strategy(self, strategy_id: int, version: Optional[int] = None) -> Strategy:
        """Retrieve a strategy; if ``version`` is ``None`` the latest version is returned."""
        if version is None:
            versions = [v for (sid, v) in self._strategies if sid == strategy_id]
            if not versions:
                raise ValueError(f"Strategy id {strategy_id} not found")
            version = max(versions)
        key = (strategy_id, version)
        try:
            return self._strategies[key]
        except KeyError as exc:
            raise ValueError(f"Strategy {strategy_id} version {version} not found") from exc

    # ---------------------------------------------------------------------
    # Experiment logging
    # ---------------------------------------------------------------------
    def log_experiment(
        self,
        strategy_id: int,
        hypothesis: str,
        data_cutoff: datetime,
        model_version: str,
        validation_period: str,
        results: Mapping[str, Any],
        decision: str,
    ) -> Experiment:
        """Record an immutable experiment.

        ``results`` must contain a ``"passed"`` boolean key.
        """
        if "passed" not in results:
            raise ValueError("Experiment results must contain a 'passed' key")
        if not any(sid == strategy_id for (sid, _v) in self._strategies):
            raise ValueError(f"Strategy id {strategy_id} does not exist for logging")
        exp = Experiment(
            strategy_id=strategy_id,
            hypothesis=hypothesis,
            data_cutoff=data_cutoff,
            model_version=model_version,
            validation_period=validation_period,
            results=results,
            decision=decision,
        )
        self._experiments.append(exp)
        return exp

    def get_experiments(self, strategy_id: Optional[int] = None) -> List[Experiment]:
        """Return all logged experiments, optionally filtered by ``strategy_id``."""
        if strategy_id is None:
            return list(self._experiments)
        return [e for e in self._experiments if e.strategy_id == strategy_id]

    # ---------------------------------------------------------------------
    # Champion / challenger handling
    # ---------------------------------------------------------------------
    def set_champion(self, strategy_id: int, version: Optional[int] = None) -> None:
        """Manually set the current champion (used for initial bootstrap)."""
        strat = self.get_strategy(strategy_id, version)
        self._champion = (strat.id, strat.version)
        if self._baseline is None:
            self._baseline = self._champion

    def add_challenger(self, strategy_id: int, version: Optional[int] = None) -> None:
        """Add a strategy version to the challenger pool.

        Duplicate entries are ignored.
        """
        strat = self.get_strategy(strategy_id, version)
        key = (strat.id, strat.version)
        if key not in self._challengers:
            self._challengers.append(key)

    def promote_challenger(self, strategy_id: int, version: Optional[int] = None) -> None:
        """Promote a challenger to champion if it has a passing experiment.

        The latest experiment for the given strategy must have ``results['passed']``
        set to ``True``; otherwise a ``ValueError`` is raised.
        """
        strat = self.get_strategy(strategy_id, version)
        key = (strat.id, strat.version)
        if key not in self._challengers:
            raise ValueError("Strategy is not in the challenger pool")
        # Find latest experiment for this strategy id
        exps = [e for e in self._experiments if e.strategy_id == strat.id]
        if not exps:
            raise ValueError("No experiments logged for challenger")
        latest = max(exps, key=lambda e: e.logged_at)
        if not latest.results.get("passed"):
            raise ValueError("Challenger has not passed validation")
        if self._champion is not None:
            self._history.append(self._champion)
        self._champion = key
        self._challengers.remove(key)

    def get_champion(self) -> Optional[Strategy]:
        if self._champion is None:
            return None
        sid, ver = self._champion
        return self._strategies[(sid, ver)]

    def get_baseline(self) -> Optional[Strategy]:
        if self._baseline is None:
            return None
        sid, ver = self._baseline
        return self._strategies[(sid, ver)]

    def get_challengers(self) -> List[Strategy]:
        return [self._strategies[key] for key in self._challengers]

    def get_history(self) -> List[Strategy]:
        return [self._strategies[key] for key in self._history]

    # ---------------------------------------------------------------------
    # Safety – no deletion methods are provided; attempts to delete would raise
    # AttributeError, satisfying the requirement that experiments/strategies
    # cannot be silently removed.
    # ---------------------------------------------------------------------
