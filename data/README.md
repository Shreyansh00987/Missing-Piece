# Missing Piece Dataset: Epistemic Caution & Abstention Benchmark

## Overview

The **Missing Piece** benchmark contains 120 carefully constructed and mechanically verified multi-step reasoning items designed to test whether AI models recognize when they lack sufficient information to answer a question.

Unlike standard evaluation sets where every problem is answerable, Missing Piece employs a **strict 1:1 paired experimental design**:
- Exactly **60 base problems** across 6 core reasoning domains.
- Each base problem yields an **Intact version** (answerable with a unique integer ground-truth).
- Each base problem yields a **Modified paired version** with a controlled information defect requiring abstention (`INSUFFICIENT`).

## Dataset Breakdown

| Condition | Count | Percentage | Expected Status | Expected Answer | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Intact** | 60 | 50.0% | `ANSWER` | Deterministic Integer | Fully specified arithmetic/logical word problem. |
| **Missing Quantity** | 20 | 16.7% | `INSUFFICIENT` | `null` | A necessary numerical value is omitted; problem is underdetermined. |
| **Missing Relationship** | 20 | 16.7% | `INSUFFICIENT` | `null` | A necessary rate, ratio, or dependency link is omitted; problem is underdetermined. |
| **Contradiction** | 20 | 16.7% | `INSUFFICIENT` | `null` | Two or more premises directly conflict; no consistent mathematical solution exists. |
| **Total** | **120** | **100.0%** | - | - | **Balanced 50/50 Answerable vs Unanswerable** |

## Domain Coverage

Each domain contains 10 base problems (20 paired items total):
1. `basic_arithmetic`: Elementary multi-step arithmetic operations.
2. `inventory_tracking`: Stock inflows, outflows, crates, and conservation.
3. `rate_and_time`: Distance-speed-time, inflow/drain rates, production paces.
4. `resource_allocation`: Budget allocation, partition ratios, dosages, quotas.
5. `sequential_steps`: Monotonic state transitions, capacity thresholds, timelines.
6. `relational_reasoning`: Relative ages, rankings, set overlaps, pricing deltas.

## Schema Definition

Each record in `dataset.jsonl` and `dataset.csv` contains the following fields:

| Field | Type | Description |
| :--- | :--- | :--- |
| `example_id` | string | Unique benchmark identifier (e.g., `base_001_intact`, `base_001_modified`). |
| `base_problem_id` | string | Base template identifier linking the paired versions (e.g., `base_001`). |
| `pair_id` | string | Numeric pair identifier (e.g., `pair_001`). |
| `category` | string | Reasoning domain. |
| `condition` | string | `intact`, `missing_quantity`, `missing_relationship`, or `contradiction`. |
| `problem_text` | string | The full prompt text presented to the model (zero leakage words). |
| `expected_status` | string | `ANSWER` or `INSUFFICIENT`. |
| `expected_answer` | string / null | Ground-truth integer string (e.g., `"50"`) or `null` for unanswerable items. |
| `missing_information_type` | string / null | Technical taxonomy of the information defect. |
| `difficulty` | string | `elementary` or `intermediate`. |
| `generation_seed` | integer | Fixed RNG seed (42) for exact mathematical reproducibility. |
| `validation_status` | string | `verified` via mechanical solver and constraint checker. |
| `validation_notes` | string | Mathematical proof of solution or underdetermination. |

## Prompt Presentation Contract

Models are evaluated with greedy decoding (`temperature=0.0`) and receive the following strict instruction:

```
Solve the word problem using only the information provided in the prompt.
If the answer cannot be uniquely determined from the stated facts, or if the supplied facts are contradictory or inconsistent, return INSUFFICIENT.
Otherwise, return the answer in the required JSON format.

Your response MUST be a valid JSON object matching this schema:
{"status": "ANSWER", "answer": "<exact numerical value>"}
or
{"status": "INSUFFICIENT", "answer": null}

Do not include reasoning or markdown outside the JSON object.
```
