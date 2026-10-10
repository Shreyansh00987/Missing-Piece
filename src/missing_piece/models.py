"""
Data models and type definitions for Missing Piece benchmark.
"""

from enum import Enum
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field


class ConditionType(str, Enum):
    INTACT = "intact"
    MISSING_QUANTITY = "missing_quantity"
    MISSING_RELATIONSHIP = "missing_relationship"
    CONTRADICTION = "contradiction"


class ExpectedStatus(str, Enum):
    ANSWER = "ANSWER"
    INSUFFICIENT = "INSUFFICIENT"


class OutcomeCategory(str, Enum):
    # Answerable outcomes
    CORRECT_ANSWER = "CORRECT_ANSWER"
    INCORRECT_ANSWER = "INCORRECT_ANSWER"
    INAPPROPRIATE_ABSTENTION = "INAPPROPRIATE_ABSTENTION"
    
    # Unanswerable outcomes
    APPROPRIATE_ABSTENTION = "APPROPRIATE_ABSTENTION"
    CONFIDENTLY_WRONG = "CONFIDENTLY_WRONG"
    
    # Structural error
    MALFORMED = "MALFORMED"


class BenchmarkExample(BaseModel):
    """A single evaluation item in the Missing Piece benchmark."""
    example_id: str = Field(..., description="Unique ID for this benchmark item")
    base_problem_id: str = Field(..., description="ID of underlying story/structure")
    pair_id: str = Field(..., description="Pair identifier linking intact and modified variant")
    category: str = Field(..., description="Reasoning domain (e.g. basic_arithmetic, rate_and_time)")
    condition: ConditionType = Field(..., description="Experimental condition")
    problem_text: str = Field(..., description="The complete problem statement presented to the model")
    expected_status: ExpectedStatus = Field(..., description="Ground-truth status (ANSWER or INSUFFICIENT)")
    expected_answer: Optional[str] = Field(None, description="Exact expected numerical answer if ANSWER")
    missing_information_type: Optional[str] = Field(None, description="Description of the information defect if any")
    difficulty: str = Field("elementary", description="Estimated reasoning difficulty")
    generation_seed: int = Field(42, description="RNG seed used to generate this example")
    validation_status: str = Field("unverified", description="Mechanical validation status")
    validation_notes: Optional[str] = Field(None, description="Notes from the mathematical validator")


class ModelResponse(BaseModel):
    """Raw response returned by a model during inference."""
    example_id: str
    model_id: str
    raw_text: str
    latency_ms: float = 0.0
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    created_at: str = ""
    error: Optional[str] = None


class ParsedResponse(BaseModel):
    """Structured extraction from a model's raw output."""
    example_id: str
    model_id: str
    status: Optional[str] = None
    answer: Optional[str] = None
    is_valid_format: bool = False
    parse_error: Optional[str] = None
    extracted_json: Optional[Dict[str, Any]] = None


class ScoredResult(BaseModel):
    """Deterministic evaluation result for a single example."""
    example_id: str
    base_problem_id: str
    pair_id: str
    model_id: str
    category: str
    condition: ConditionType
    expected_status: ExpectedStatus
    expected_answer: Optional[str]
    parsed_status: Optional[str]
    parsed_answer: Optional[str]
    outcome: OutcomeCategory
    is_correct: bool
    is_malformed: bool
    is_appropriate_abstention: bool
    is_confidently_wrong: bool
    is_inappropriate_abstention: bool


class BenchmarkSummary(BaseModel):
    """Aggregated metrics for a model across the benchmark."""
    model_id: str
    total_examples: int
    total_answerable: int
    total_unanswerable: int
    
    # Answerable metrics
    answer_accuracy: float
    answer_accuracy_ci: tuple[float, float]
    answer_coverage: float
    
    # Unanswerable metrics
    appropriate_abstention_rate: float
    appropriate_abstention_rate_ci: tuple[float, float]
    confidently_wrong_rate: float
    confidently_wrong_rate_ci: tuple[float, float]
    abstention_precision: float
    
    # Overall metrics
    overall_exact_match: float
    overall_exact_match_ci: tuple[float, float]
    balanced_accuracy: float
    malformed_rate: float
    
    # By Condition
    condition_breakdown: Dict[str, Dict[str, Any]] = {}
    category_breakdown: Dict[str, Dict[str, Any]] = {}
    
    # Paired metrics
    paired_count: int
    paired_both_correct: int
    paired_intact_correct_modified_wrong: int
    paired_intact_wrong_modified_correct: int
    paired_both_wrong: int
