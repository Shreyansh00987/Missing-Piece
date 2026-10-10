"""
Unit tests for DatasetGenerator in Missing Piece benchmark.
"""

import pytest
from missing_piece.generator import DatasetGenerator
from missing_piece.models import ConditionType, ExpectedStatus


def test_deterministic_generation():
    """Verify that same seed generates identical examples."""
    gen1 = DatasetGenerator(seed=42)
    gen2 = DatasetGenerator(seed=42)
    
    exs1 = gen1.generate()
    exs2 = gen2.generate()
    
    assert len(exs1) == len(exs2) == 120
    for e1, e2 in zip(exs1, exs2):
        assert e1.example_id == e2.example_id
        assert e1.problem_text == e2.problem_text
        assert e1.expected_status == e2.expected_status
        assert e1.expected_answer == e2.expected_answer


def test_unique_ids_and_problem_texts():
    """Verify all example IDs and problem texts are unique."""
    gen = DatasetGenerator(seed=42)
    examples = gen.generate()
    
    ids = [e.example_id for e in examples]
    assert len(ids) == len(set(ids)) == 120
    
    texts = [e.problem_text.strip().lower() for e in examples]
    assert len(texts) == len(set(texts)) == 120


def test_correct_condition_counts():
    """Verify balanced counts: 60 intact, 20 missing_qty, 20 missing_rel, 20 contradiction."""
    gen = DatasetGenerator(seed=42)
    examples = gen.generate()
    
    intact = [e for e in examples if e.condition == ConditionType.INTACT]
    mq = [e for e in examples if e.condition == ConditionType.MISSING_QUANTITY]
    mr = [e for e in examples if e.condition == ConditionType.MISSING_RELATIONSHIP]
    co = [e for e in examples if e.condition == ConditionType.CONTRADICTION]
    
    assert len(intact) == 60
    assert len(mq) == 20
    assert len(mr) == 20
    assert len(co) == 20


def test_domain_distribution():
    """Verify all 6 reasoning domains have 20 examples each."""
    gen = DatasetGenerator(seed=42)
    examples = gen.generate()
    
    domain_counts = {}
    for e in examples:
        domain_counts[e.category] = domain_counts.get(e.category, 0) + 1
        
    assert len(domain_counts) == 6
    for domain, count in domain_counts.items():
        assert count == 20, f"Domain {domain} has {count} items, expected 20"


def test_paired_relationships():
    """Verify each base problem has exactly one intact and one modified variant."""
    gen = DatasetGenerator(seed=42)
    examples = gen.generate()
    
    pairs = {}
    for e in examples:
        pairs.setdefault(e.pair_id, []).append(e)
        
    assert len(pairs) == 60
    for pid, pair_exs in pairs.items():
        assert len(pair_exs) == 2
        conds = {pair_exs[0].condition, pair_exs[1].condition}
        assert ConditionType.INTACT in conds
        # Exactly one is intact and one is defective
        statuses = {pair_exs[0].expected_status, pair_exs[1].expected_status}
        assert ExpectedStatus.ANSWER in statuses
        assert ExpectedStatus.INSUFFICIENT in statuses
