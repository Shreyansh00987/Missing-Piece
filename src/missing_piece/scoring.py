"""
Deterministic scoring engine for Missing Piece benchmark.
Evaluates model responses against mathematical ground truth and classifies outcomes.
"""

from typing import List, Dict, Optional
from missing_piece.models import (
    BenchmarkExample,
    ParsedResponse,
    ScoredResult,
    ExpectedStatus,
    OutcomeCategory,
    ConditionType
)


class ScoringEngine:
    """Evaluates parsed responses and generates deterministic scored results."""

    @staticmethod
    def score_example(example: BenchmarkExample, parsed: ParsedResponse) -> ScoredResult:
        """Score a single parsed response against a benchmark example."""
        # Handle malformed outputs
        if not parsed.is_valid_format or parsed.status is None:
            return ScoredResult(
                example_id=example.example_id,
                base_problem_id=example.base_problem_id,
                pair_id=example.pair_id,
                model_id=parsed.model_id,
                category=example.category,
                condition=example.condition,
                expected_status=example.expected_status,
                expected_answer=example.expected_answer,
                parsed_status=parsed.status,
                parsed_answer=parsed.answer,
                outcome=OutcomeCategory.MALFORMED,
                is_correct=False,
                is_malformed=True,
                is_appropriate_abstention=False,
                is_confidently_wrong=False,
                is_inappropriate_abstention=False
            )

        # Condition 1: Answerable (Intact)
        if example.expected_status == ExpectedStatus.ANSWER:
            if parsed.status == "INSUFFICIENT":
                # Model abstained when problem was answerable
                return ScoredResult(
                    example_id=example.example_id,
                    base_problem_id=example.base_problem_id,
                    pair_id=example.pair_id,
                    model_id=parsed.model_id,
                    category=example.category,
                    condition=example.condition,
                    expected_status=example.expected_status,
                    expected_answer=example.expected_answer,
                    parsed_status=parsed.status,
                    parsed_answer=parsed.answer,
                    outcome=OutcomeCategory.INAPPROPRIATE_ABSTENTION,
                    is_correct=False,
                    is_malformed=False,
                    is_appropriate_abstention=False,
                    is_confidently_wrong=False,
                    is_inappropriate_abstention=True
                )
            
            # Model provided an answer
            is_match = ScoringEngine._compare_answers(parsed.answer, example.expected_answer)
            outcome = OutcomeCategory.CORRECT_ANSWER if is_match else OutcomeCategory.INCORRECT_ANSWER
            
            return ScoredResult(
                example_id=example.example_id,
                base_problem_id=example.base_problem_id,
                pair_id=example.pair_id,
                model_id=parsed.model_id,
                category=example.category,
                condition=example.condition,
                expected_status=example.expected_status,
                expected_answer=example.expected_answer,
                parsed_status=parsed.status,
                parsed_answer=parsed.answer,
                outcome=outcome,
                is_correct=is_match,
                is_malformed=False,
                is_appropriate_abstention=False,
                is_confidently_wrong=False,
                is_inappropriate_abstention=False
            )

        # Condition 2: Unanswerable (Missing Quantity, Missing Relationship, Contradiction)
        else: # example.expected_status == ExpectedStatus.INSUFFICIENT
            if parsed.status == "INSUFFICIENT":
                # Model appropriately abstained!
                return ScoredResult(
                    example_id=example.example_id,
                    base_problem_id=example.base_problem_id,
                    pair_id=example.pair_id,
                    model_id=parsed.model_id,
                    category=example.category,
                    condition=example.condition,
                    expected_status=example.expected_status,
                    expected_answer=example.expected_answer,
                    parsed_status=parsed.status,
                    parsed_answer=parsed.answer,
                    outcome=OutcomeCategory.APPROPRIATE_ABSTENTION,
                    is_correct=True,
                    is_malformed=False,
                    is_appropriate_abstention=True,
                    is_confidently_wrong=False,
                    is_inappropriate_abstention=False
                )
            else:
                # Model supplied an answer to an unanswerable problem -> Confidently Wrong!
                return ScoredResult(
                    example_id=example.example_id,
                    base_problem_id=example.base_problem_id,
                    pair_id=example.pair_id,
                    model_id=parsed.model_id,
                    category=example.category,
                    condition=example.condition,
                    expected_status=example.expected_status,
                    expected_answer=example.expected_answer,
                    parsed_status=parsed.status,
                    parsed_answer=parsed.answer,
                    outcome=OutcomeCategory.CONFIDENTLY_WRONG,
                    is_correct=False,
                    is_malformed=False,
                    is_appropriate_abstention=False,
                    is_confidently_wrong=True,
                    is_inappropriate_abstention=False
                )

    @staticmethod
    def _compare_answers(candidate: Optional[str], ground_truth: Optional[str]) -> bool:
        """Compare candidate answer with ground truth."""
        if candidate is None or ground_truth is None:
            return False
        
        c = candidate.strip().lower()
        g = ground_truth.strip().lower()
        
        # Direct string equality
        if c == g:
            return True
            
        # Numerical equality (handling potential float representation e.g. 20 vs 20.0)
        try:
            return float(c) == float(g)
        except ValueError:
            return False

    @staticmethod
    def score_all(examples: List[BenchmarkExample], parsed_responses: List[ParsedResponse]) -> List[ScoredResult]:
        """Score an entire list of responses."""
        resp_map = {r.example_id: r for r in parsed_responses}
        results = []
        for ex in examples:
            if ex.example_id in resp_map:
                res = ScoringEngine.score_example(ex, resp_map[ex.example_id])
                results.append(res)
        return results
