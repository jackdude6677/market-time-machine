"""Simple in‑memory relationship discovery map.

Provides Node and Relationship dataclasses and a mutable RelationshipMap.
The implementation stores the fields required by the brief and offers basic
query helpers used by the tests.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Node:
    """A graph node.

    identifier: unique string (e.g., ticker)
    kind: type of node (company, sector, commodity, ...)
    """
    identifier: str
    kind: str


@dataclass
class Relationship:
    """Edge between two nodes with metadata required by the brief."""
    src: Node
    dst: Node
    rel_type: str
    evidence: str = ""
    first_timestamp: Optional[datetime.datetime] = None
    last_timestamp: Optional[datetime.datetime] = None
    strength: float = 0.0
    confidence: float = 0.0
    market_conditions: str = ""
    predictive_performance: float = 0.0

    def update_timestamp(self, ts: datetime.datetime) -> None:
        """Update first/last timestamps based on *ts*."""
        if self.first_timestamp is None or ts < self.first_timestamp:
            self.first_timestamp = ts
        if self.last_timestamp is None or ts > self.last_timestamp:
            self.last_timestamp = ts


class RelationshipMap:
    """Container for nodes and relationships.

    Nodes are stored in a dict keyed by identifier. Relationships are kept in a
    list; look‑ups are linear which is fine for the unit tests.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, Node] = {}
        self._edges: List[Relationship] = []

    # Node handling ---------------------------------------------------
    def add_node(self, identifier: str, kind: str) -> Node:
        """Add a node or return existing one."""
        if identifier in self._nodes:
            return self._nodes[identifier]
        node = Node(identifier, kind)
        self._nodes[identifier] = node
        return node

    def get_node(self, identifier: str) -> Optional[Node]:
        return self._nodes.get(identifier)

    # Relationship handling ------------------------------------------
    def add_relationship(
        self,
        src_id: str,
        dst_id: str,
        rel_type: str,
        *,
        evidence: str = "",
        timestamp: Optional[datetime.datetime] = None,
        strength: float = 0.0,
        confidence: float = 0.0,
        market_conditions: str = "",
        predictive_performance: float = 0.0,
    ) -> Relationship:
        """Create or update a relationship.

        If a relationship with the same src, dst and type exists, its metadata
        is merged (timestamps are extended, numeric fields overwritten with the
        latest call). Zero values are considered valid and should overwrite
        existing values when explicitly provided.
        """
        src = self.add_node(src_id, "unknown")
        dst = self.add_node(dst_id, "unknown")
        for edge in self._edges:
            if edge.src == src and edge.dst == dst and edge.rel_type == rel_type:
                # merge metadata
                edge.evidence = evidence or edge.evidence
                edge.strength = strength if strength is not None else edge.strength
                edge.confidence = confidence if confidence is not None else edge.confidence
                edge.market_conditions = market_conditions or edge.market_conditions
                edge.predictive_performance = (
                    predictive_performance or edge.predictive_performance
                )
                if timestamp:
                    edge.update_timestamp(timestamp)
                return edge
        # new edge
        edge = Relationship(
            src=src,
            dst=dst,
            rel_type=rel_type,
            evidence=evidence,
            first_timestamp=timestamp,
            last_timestamp=timestamp,
            strength=strength,
            confidence=confidence,
            market_conditions=market_conditions,
            predictive_performance=predictive_performance,
        )
        self._edges.append(edge)
        return edge


    def get_relationships(
        self,
        src_id: Optional[str] = None,
        dst_id: Optional[str] = None,
        rel_type: Optional[str] = None,
    ) -> List[Relationship]:
        """Return relationships filtered by optional criteria."""
        result: List[Relationship] = []
        for edge in self._edges:
            if src_id is not None and edge.src.identifier != src_id:
                continue
            if dst_id is not None and edge.dst.identifier != dst_id:
                continue
            if rel_type is not None and edge.rel_type != rel_type:
                continue
            result.append(edge)
        return result

    # Utility --------------------------------------------------------
    def clear(self) -> None:
        self._nodes.clear()
        self._edges.clear()

    def __len__(self) -> int:
        return len(self._edges)


__all__ = ["Node", "Relationship", "RelationshipMap"]
