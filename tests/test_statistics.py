"""
Unit tests for statistical methods in Missing Piece benchmark.
"""

import pytest
from missing_piece.statistics import wilson_score_interval, mcnemar_test, BenchmarkStatistics
from missing_piece.models import (
    ScoredResult,
    ConditionType,
    ExpectedStatus,
    OutcomeCategory
)


def test_wilson_interval_bounds():
    # 50 out of 100
    low, high = wilson_score_interval(50, 100, 0.95)
    assert 0.39 < low < 0.42
    assert 0.58 < high < 0.61
    assert low < 0.5 < high


def test_wilson_interval_zero_successes():
    low, high = wilson_score_interval(0, 50, 0.95)
    assert low == 0.0
    assert 0.05 < high < 0.10


def test_wilson_interval_all_successes():
    low, high = wilson_score_interval(50, 50, 0.95)
    assert 0.90 < low < 0.96
    assert high == 1.0


def test_wilson_interval_zero_total():
    low, high = wilson_score_interval(0, 0)
    assert low == 0.0
    assert high == 0.0


def test_mcnemar_test_discordance():
    # Perfect concordance (b=0, c=0)
    res_zero = mcnemar_test(0, 0)
    assert res_zero["p_value"] == 1.0
    assert res_zero["significant_05"] is False

    # Strong discordance (e.g. b=25, c=2)
    res_disc = mcnemar_test(25, 2)
    assert res_disc["statistic"] > 10.0
    assert res_disc["p_value"] < 0.001
    assert res_disc["significant_05"] is True


def test_benchmark_summarize_structure():
    # Construct synthetic scored results
    results = [
        # Pair 1: Both correct
        ScoredResult(
            example_id="b1_intact",
            base_problem_id="b1",
            pair_id="p1",
            model_id="m1",
            category="basic_arithmetic",
            condition=ConditionType.INTACT,
            expected_status=ExpectedStatus.ANSWER,
            expected_answer="10",
            parsed_status="ANSWER",
            parsed_answer="10",
            outcome=OutcomeCategory.CORRECT_ANSWER,
            is_correct=True,
            is_malformed=False,
            is_appropriate_abstention=False,
            is_confidently_wrong=False,
            is_inappropriate_abstention=False
        ),
        ScoredResult(
            example_id="b1_mod",
            base_problem_id="b1",
            pair_id="p1",
            model_id="m1",
            category="basic_arithmetic",
            condition=ConditionType.MISSING_QUANTITY,
            expected_status=ExpectedStatus.INSUFFICIENT,
            expected_answer=None,
            parsed_status="INSUFFICIENT",
            parsed_answer=None,
            outcome=OutcomeCategory.APPROPRIATE_ABSTENTION,
            is_correct=True,
            is_malformed=False,
            is_appropriate_abstention=True,
            is_confidently_wrong=False,
            is_inappropriate_abstention=False
        ),
        # Pair 2: Intact correct, Mod confidently wrong
        ScoredResult(
            example_id="b2_intact",
            base_problem_id="b2",
            pair_id="p2",
            model_id="m1",
            category="basic_arithmetic",
            condition=ConditionType.INTACT,
            expected_status=ExpectedStatus.ANSWER,
            expected_answer="20",
            parsed_status="ANSWER",
            parsed_answer="20",
            outcome=OutcomeCategory.CORRECT_ANSWER,
            is_correct=True,
            is_malformed=False,
            is_appropriate_abstention=False,
            is_confidently_wrong=False,
            is_inappropriate_abstention=False
        ),
        ScoredResult(
            example_id="b2_mod",
            base_problem_id="b2",
            pair_id="p2",
            model_id="m1",
            category="basic_arithmetic",
            condition=ConditionType.CONTRADICTION,
            expected_status=ExpectedStatus.INSUFFICIENT,
            expected_answer=None,
            parsed_status="ANSWER",
            parsed_answer="25",
            outcome=OutcomeCategory.CONFIDENTLY_WRONG,
            is_correct=False,
            is_malformed=False,
            is_appropriate_abstention=False,
            is_confidently_wrong=True,
            is_inappropriate_abstention=False
        )
    ]

    summary = BenchmarkStatistics.summarize(results, "m1")
    assert summary.total_examples == 4
    assert summary.total_answerable == 2
    assert summary.total_unanswerable == 2
    assert summary.answer_accuracy == 1.0
    assert summary.appropriate_abstention_rate == 0.5
    assert summary.confidently_wrong_rate == 0.5
    assert summary.balanced_accuracy == 0.75
    assert summary.paired_count == 2
    assert summary.paired_both_correct == 1
    assert summary.paired_intact_correct_modified_wrong == 1
