"""
Unit tests for OutputParser in Missing Piece benchmark.
"""

import pytest
from missing_piece.parser import OutputParser


def test_parse_valid_answer_json():
    raw = '{"status": "ANSWER", "answer": "20"}'
    parsed = OutputParser.parse(raw, "ex1", "test_model")
    assert parsed.is_valid_format is True
    assert parsed.status == "ANSWER"
    assert parsed.answer == "20"
    assert parsed.parse_error is None


def test_parse_valid_insufficient_json():
    raw = '{"status": "INSUFFICIENT", "answer": null}'
    parsed = OutputParser.parse(raw, "ex2", "test_model")
    assert parsed.is_valid_format is True
    assert parsed.status == "INSUFFICIENT"
    assert parsed.answer is None
    assert parsed.parse_error is None


def test_parse_markdown_wrapped_json():
    raw = """Here is the solution:
```json
{
  "status": "ANSWER",
  "answer": "45"
}
```
Hope this helps!"""
    parsed = OutputParser.parse(raw, "ex3", "test_model")
    assert parsed.is_valid_format is True
    assert parsed.status == "ANSWER"
    assert parsed.answer == "45"


def test_parse_empty_and_whitespace():
    raw = "   \n\t  "
    parsed = OutputParser.parse(raw, "ex4", "test_model")
    assert parsed.is_valid_format is False
    assert "Empty" in parsed.parse_error


def test_parse_missing_status_key():
    raw = '{"answer": "20"}'
    parsed = OutputParser.parse(raw, "ex5", "test_model")
    assert parsed.is_valid_format is False
    assert "Missing required 'status'" in parsed.parse_error


def test_parse_invalid_status_value():
    raw = '{"status": "MAYBE", "answer": "20"}'
    parsed = OutputParser.parse(raw, "ex6", "test_model")
    assert parsed.is_valid_format is False
    assert "Invalid status value 'MAYBE'" in parsed.parse_error


def test_parse_answer_status_with_null_answer():
    raw = '{"status": "ANSWER", "answer": null}'
    parsed = OutputParser.parse(raw, "ex7", "test_model")
    assert parsed.is_valid_format is False
    assert "null or missing" in parsed.parse_error


def test_parse_answer_with_units():
    raw = '{"status": "ANSWER", "answer": "$45 dollars"}'
    parsed = OutputParser.parse(raw, "ex8", "test_model")
    assert parsed.is_valid_format is True
    assert parsed.answer == "45"
