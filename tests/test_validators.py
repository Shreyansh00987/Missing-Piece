"""
Unit tests for DatasetValidator in Missing Piece benchmark.
"""

import pytest
from missing_piece.generator import DatasetGenerator
from missing_piece.validators import DatasetValidator
from missing_piece.models import BenchmarkExample, ConditionType, ExpectedStatus


def test_validator_passes_on_benchmark_dataset():
    """Verify that generated benchmark passes all validation checks."""
    gen = DatasetGenerator(seed=42)
    examples = gen.generate()
    validator = DatasetValidator()
    report = validator.validate(examples)
    
    assert report.is_valid is True
    assert len(report.errors) == 0
    assert all(report.checks.values())


def test_validator_catches_duplicate_text():
    """Verify validator flags duplicate problem text."""
    gen = DatasetGenerator(seed=42)
    examples = gen.generate()
    # Duplicate the first text into the second
    examples[1].problem_text = examples[0].problem_text
    
    validator = DatasetValidator()
    report = validator.validate(examples)
    
    assert report.is_valid is False
    assert report.checks["unique_problem_texts"] is False


def test_validator_catches_leakage_token():
    """Verify validator catches prohibited prompt keywords."""
    gen = DatasetGenerator(seed=42)
    examples = gen.generate()
    examples[0].problem_text += " Note: This problem has missing information."
    
    validator = DatasetValidator()
    report = validator.validate(examples)
    
    assert report.is_valid is False
    assert report.checks["no_prompt_leakage"] is False


def test_validator_catches_unbalanced_conditions():
    """Verify validator catches unbalanced condition counts."""
    gen = DatasetGenerator(seed=42)
    examples = gen.generate()[:100] # truncate
    
    validator = DatasetValidator()
    report = validator.validate(examples)
    
    assert report.is_valid is False
    assert report.checks["cardinality_120"] is False
