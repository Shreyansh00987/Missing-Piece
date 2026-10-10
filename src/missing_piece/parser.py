"""
Robust JSON output parser for Missing Piece benchmark.
Extracts and validates structured model outputs against the benchmark contract.
"""

import json
import re
from typing import Optional, Dict, Any, Tuple
from missing_piece.models import ParsedResponse


class OutputParser:
    """Parses model responses according to the benchmark JSON contract."""

    @staticmethod
    def parse(raw_text: str, example_id: str = "", model_id: str = "") -> ParsedResponse:
        """Parse raw text from model into a validated ParsedResponse object."""
        if not raw_text or not raw_text.strip():
            return ParsedResponse(
                example_id=example_id,
                model_id=model_id,
                status=None,
                answer=None,
                is_valid_format=False,
                parse_error="Empty or whitespace-only response"
            )

        cleaned = raw_text.strip()
        
        # 1. Attempt direct JSON parsing
        data, err = OutputParser._extract_json_dict(cleaned)
        if data is None:
            return ParsedResponse(
                example_id=example_id,
                model_id=model_id,
                status=None,
                answer=None,
                is_valid_format=False,
                parse_error=f"Could not extract valid JSON: {err}"
            )

        # 2. Validate schema requirements
        status = data.get("status")
        if status is None:
            return ParsedResponse(
                example_id=example_id,
                model_id=model_id,
                status=None,
                answer=None,
                is_valid_format=False,
                parse_error="Missing required 'status' key",
                extracted_json=data
            )

        status_str = str(status).strip().upper()
        if status_str not in ("ANSWER", "INSUFFICIENT"):
            return ParsedResponse(
                example_id=example_id,
                model_id=model_id,
                status=status_str,
                answer=None,
                is_valid_format=False,
                parse_error=f"Invalid status value '{status_str}'. Must be 'ANSWER' or 'INSUFFICIENT'.",
                extracted_json=data
            )

        raw_answer = data.get("answer")
        answer_str: Optional[str] = None
        
        if status_str == "INSUFFICIENT":
            # For INSUFFICIENT, answer can be None/null or empty or absent
            if raw_answer is not None and str(raw_answer).strip() != "" and str(raw_answer).lower() != "null":
                # Model provided an answer despite saying INSUFFICIENT, or non-null
                answer_str = str(raw_answer).strip()
            else:
                answer_str = None
        else: # status_str == "ANSWER"
            if raw_answer is None or str(raw_answer).strip() == "" or str(raw_answer).lower() == "null":
                return ParsedResponse(
                    example_id=example_id,
                    model_id=model_id,
                    status="ANSWER",
                    answer=None,
                    is_valid_format=False,
                    parse_error="Status is 'ANSWER' but 'answer' field is null or missing.",
                    extracted_json=data
                )
            # Normalize answer: clean surrounding formatting, commas, currency symbols
            ans_clean = str(raw_answer).strip().replace(",", "").replace("$", "").replace("miles", "").strip()
            # Extract first continuous numeric sequence if formatted with units
            num_match = re.search(r'-?\d+(?:\.\d+)?', ans_clean)
            if num_match:
                answer_str = num_match.group(0)
                # If it's a whole number with .0, strip trailing .0
                if answer_str.endswith(".0"):
                    answer_str = answer_str[:-2]
            else:
                answer_str = ans_clean

        return ParsedResponse(
            example_id=example_id,
            model_id=model_id,
            status=status_str,
            answer=answer_str,
            is_valid_format=True,
            parse_error=None,
            extracted_json=data
        )

    @staticmethod
    def _extract_json_dict(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Try parsing JSON directly, then via markdown code blocks, then via bracket matching."""
        # A. Try parsing entire text directly
        try:
            val = json.loads(text)
            if isinstance(val, dict):
                return val, None
        except Exception:
            pass

        # B. Try extracting from markdown code blocks ```json ... ``` or ``` ... ```
        block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL | re.IGNORECASE)
        if block_match:
            try:
                val = json.loads(block_match.group(1))
                if isinstance(val, dict):
                    return val, None
            except Exception:
                pass

        # C. Try regex search for outermost curly braces
        brace_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if brace_match:
            try:
                val = json.loads(brace_match.group(0))
                if isinstance(val, dict):
                    return val, None
            except Exception:
                pass

        return None, "No valid JSON object structure found in response"
