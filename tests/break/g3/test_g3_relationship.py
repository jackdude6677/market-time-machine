"""Tests exposing bugs in the RelationshipMap implementation.

The current implementation fails to correctly update numeric metadata fields
when a falsy value (e.g., 0.0) is provided.  The tests assert that the
metadata is overwritten with the supplied value, causing the tests to fail.
"""

import datetime
import pytest

from market_time_machine.relationship import RelationshipMap

@pytest.fixture
def rel_map():
    return RelationshipMap()

def test_zero_strength_overwrites_existing(rel_map):
    # First add a relationship with non‑zero strength.
    ts1 = datetime.datetime(2023, 1, 1, 12, 0)
    rel = rel_map.add_relationship(
        "A", "B", "correlates", strength=5.0, timestamp=ts1
    )
    assert rel.strength == 5.0
    # Now add the same relationship with strength=0.0 – should overwrite.
    ts2 = datetime.datetime(2023, 1, 2, 12, 0)
    rel2 = rel_map.add_relationship(
        "A", "B", "correlates", strength=0.0, timestamp=ts2
    )
    # The buggy implementation keeps the old strength (5.0).
    assert rel2.strength == 0.0
    # Timestamp should be updated to the later one.
    assert rel2.last_timestamp == ts2

def test_zero_confidence_overwrites_existing(rel_map):
    ts1 = datetime.datetime(2023, 1, 1, 12, 0)
    rel = rel_map.add_relationship(
        "X", "Y", "influences", confidence=0.8, timestamp=ts1
    )
    assert rel.confidence == 0.8
    # Overwrite with zero confidence.
    ts2 = datetime.datetime(2023, 1, 3, 12, 0)
    rel2 = rel_map.add_relationship(
        "X", "Y", "influences", confidence=0.0, timestamp=ts2
    )
    assert rel2.confidence == 0.0
