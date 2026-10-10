"""
Unit tests for InferenceRunner, Caching, and Heuristic Baselines.
"""

import os
import shutil
import pytest
from missing_piece.inference import HeuristicBaselineAdapter, InferenceRunner
from missing_piece.models import BenchmarkExample, ConditionType, ExpectedStatus


@pytest.fixture
def temp_cache_dir(tmp_path):
    d = tmp_path / "test_cache"
    d.mkdir()
    return str(d)


@pytest.fixture
def sample_examples():
    return [
        BenchmarkExample(
            example_id="t1_intact",
            base_problem_id="t1",
            pair_id="p1",
            category="basic_arithmetic",
            condition=ConditionType.INTACT,
            problem_text="What is 10 + 10?",
            expected_status=ExpectedStatus.ANSWER,
            expected_answer="20"
        ),
        BenchmarkExample(
            example_id="t1_modified",
            base_problem_id="t1",
            pair_id="p1",
            category="basic_arithmetic",
            condition=ConditionType.MISSING_QUANTITY,
            problem_text="What is 10 + ?",
            expected_status=ExpectedStatus.INSUFFICIENT,
            expected_answer=None
        )
    ]


def test_heuristic_always_answer():
    adapter = HeuristicBaselineAdapter("always_answer")
    raw, lat = adapter.generate("Any problem")
    assert '"status": "ANSWER"' in raw
    assert '"answer": "20"' in raw
    assert lat >= 0.0


def test_heuristic_always_abstain():
    adapter = HeuristicBaselineAdapter("always_abstain")
    raw, lat = adapter.generate("Any problem")
    assert '"status": "INSUFFICIENT"' in raw
    assert '"answer": null' in raw


def test_inference_runner_caching(temp_cache_dir, sample_examples):
    runner = InferenceRunner(cache_dir=temp_cache_dir)
    adapter = HeuristicBaselineAdapter("always_abstain")
    
    # 1. First run generates and writes to cache
    resp1 = runner.evaluate_model(adapter, sample_examples)
    assert len(resp1) == 2
    
    cache_file = runner._get_cache_path(adapter.model_id)
    assert os.path.exists(cache_file)
    
    # 2. Second run reads directly from cache without recomputing
    cached_items = runner.load_cache(adapter.model_id)
    assert len(cached_items) == 2
    assert "t1_intact" in cached_items
    assert "t1_modified" in cached_items
    
    resp2 = runner.evaluate_model(adapter, sample_examples, use_cache=True)
    assert len(resp2) == 2
    assert resp2[0].raw_text == resp1[0].raw_text
