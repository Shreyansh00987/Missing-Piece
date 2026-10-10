"""
Unit tests for ScoringEngine in Missing Piece benchmark.
"""

import pytest
from missing_piece.scoring import ScoringEngine
from missing_piece.models import (
    BenchmarkExample,
    ParsedResponse,
    ConditionType,
    ExpectedStatus,
    OutcomeCategory
)


@pytest.fixture
def intact_example():
    return BenchmarkExample(
        example_id="ex_intact",
        base_problem_id="base_1",
        pair_id="pair_1",
        category="basic_arithmetic",
        condition=ConditionType.INTACT,
        problem_text="5 + 5 = ?",
        expected_status=ExpectedStatus.ANSWER,
        expected_answer="10"
    )


@pytest.fixture
def defective_example():
    return BenchmarkExample(
        example_id="ex_defective",
        base_problem_id="base_1",
        pair_id="pair_1",
        category="basic_arithmetic",
        condition=ConditionType.MISSING_QUANTITY,
        problem_text="5 + ? = ?",
        expected_status=ExpectedStatus.INSUFFICIENT,
        expected_answer=None
    )


def test_score_correct_answer(intact_example):
    parsed = ParsedResponse(
        example_id="ex_intact",
        model_id="test_model",
        status="ANSWER",
        answer="10",
        is_valid_format=True
    )
    res = ScoringEngine.score_example(intact_example, parsed)
    assert res.outcome == OutcomeCategory.CORRECT_ANSWER
    assert res.is_correct is True
    assert res.is_malformed is False


def test_score_incorrect_answer(intact_example):
    parsed = ParsedResponse(
        example_id="ex_intact",
        model_id="test_model",
        status="ANSWER",
        answer="99",
        is_valid_format=True
    )
    res = ScoringEngine.score_example(intact_example, parsed)
    assert res.outcome == OutcomeCategory.INCORRECT_ANSWER
    assert res.is_correct is False


def test_score_inappropriate_abstention(intact_example):
    parsed = ParsedResponse(
        example_id="ex_intact",
        model_id="test_model",
        status="INSUFFICIENT",
        answer=None,
        is_valid_format=True
    )
    res = ScoringEngine.score_example(intact_example, parsed)
    assert res.outcome == OutcomeCategory.INAPPROPRIATE_ABSTENTION
    assert res.is_correct is False
    assert res.is_inappropriate_abstention is True


def test_score_appropriate_abstention(defective_example):
    parsed = ParsedResponse(
        example_id="ex_defective",
        model_id="test_model",
        status="INSUFFICIENT",
        answer=None,
        is_valid_format=True
    )
    res = ScoringEngine.score_example(defective_example, parsed)
    assert res.outcome == OutcomeCategory.APPROPRIATE_ABSTENTION
    assert res.is_correct is True
    assert res.is_appropriate_abstention is True


def test_score_confidently_wrong(defective_example):
    parsed = ParsedResponse(
        example_id="ex_defective",
        model_id="test_model",
        status="ANSWER",
        answer="42",
        is_valid_format=True
    )
    res = ScoringEngine.score_example(defective_example, parsed)
    assert res.outcome == OutcomeCategory.CONFIDENTLY_WRONG
    assert res.is_correct is False
    assert res.is_confidently_wrong is True


def test_score_malformed_response(intact_example):
    parsed = ParsedResponse(
        example_id="ex_intact",
        model_id="test_model",
        status=None,
        answer=None,
        is_valid_format=False,
        parse_error="Failed JSON"
    )
    res = ScoringEngine.score_example(intact_example, parsed)
    assert res.outcome == OutcomeCategory.MALFORMED
    assert res.is_correct is False
    assert res.is_malformed is True
