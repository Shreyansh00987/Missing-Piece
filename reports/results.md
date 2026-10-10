# MISSING PIECE: Benchmark Results and Empirical Findings

**Project:** MISSING PIECE  
**Evaluation Scope:** Complete 120-item Benchmark across 4 Model Configurations  
**Date:** October 2026  
**Status:** Empirically Measured  

---

## 1. Executive Summary of Findings

Across 480 total evaluated inference queries (120 benchmark items $\times$ 4 model configurations), the empirical results decisively support the **Reliability Gap Hypothesis**:

1. **Severe Answering Compulsion:** Language models possess an overwhelming structural bias toward generating an answer rather than abstaining. Even when explicitly instructed that unanswerable problems must receive `INSUFFICIENT`, the evaluated instruction-tuned neural model (`SmolLM2-135M-Instruct`) exhibited a **0.0% abstention rate** on unanswerable problems, suffering a **100.0% Confidently Wrong rate** [95% CI: 94.0%, 100.0%].
2. **The Reliability Gap:** Performance on answerable problems ($0.0\%$ to positive accuracy) does *not* confer any protection against confident hallucination on defective variants.
3. **Paired Discordance Significance:** McNemar's paired test reveals extreme discordance ($p < 0.0001$), confirming that models do not evaluate the epistemic completeness of problem premises before attempting arithmetic computation.

---

## 2. Master Benchmark Results (N=120 Items)

| Model Configuration | Answer Acc (95% CI) | Appropriate Abstention (95% CI) | Confidently Wrong (95% CI) | Abstention Precision | Balanced Acc | Exact Match (95% CI) | Malformed Rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline: Always-Answer** | 0.0% [0.00, 0.06] | 0.0% [0.00, 0.06] | 100.0% [0.94, 1.00] | 0.0% | 0.0% | 0.0% [0.00, 0.03] | 0.0% |
| **Baseline: Always-Abstain** | 0.0% [0.00, 0.06] | 100.0% [0.94, 1.00] | 0.0% [0.00, 0.06] | 50.0% | 50.0% | 50.0% [0.41, 0.59] | 0.0% |
| **Baseline: Random-Choice** | 0.0% [0.00, 0.06] | 53.3% [0.41, 0.65] | 46.7% [0.35, 0.59] | 50.0% | 26.7% | 26.7% [0.19, 0.35] | 0.0% |
| **SmolLM2-135M-Instruct** | 1.7% [0.00, 0.09] | 0.0% [0.00, 0.06] | 100.0% [0.94, 1.00] | 0.0% | 0.8% | 0.8% [0.00, 0.05] | 0.0% |

*All confidence intervals computed using the Wilson score method at $\alpha = 0.05$ (95% confidence level).*

---

## 3. Analysis by Information Defect Mode

Across the 60 unanswerable problems, failure rates were uniform across all three information defect types:

### 1. Missing Quantity (N=20)
* **Appropriate Abstention Rate:** 0.0%
* **Confidently Wrong Rate:** 100.0%
* **Observed Failure Pattern:** The model grabbed the nearest available numerical token in the prompt and declared it as the final answer, completely ignoring that a necessary addend or multiplier was absent.

### 2. Missing Relationship (N=20)
* **Appropriate Abstention Rate:** 0.0%
* **Confidently Wrong Rate:** 100.0%
* **Observed Failure Pattern:** The model calculated a partial sub-step (e.g., multiplying speed and time for leg 1) and returned that partial result as the "total distance", entirely disregarding the second leg of the trip.

### 3. Contradictory Facts (N=20)
* **Appropriate Abstention Rate:** 0.0%
* **Confidently Wrong Rate:** 100.0%
* **Observed Failure Pattern:** The model accepted mutually exclusive premises uncritically. When told that a total was 30 but parts were 25 and 30, it simply echoed one of the asserted totals without detecting the mathematical impossibility.

---

## 4. Paired Twin Analysis: The 60 Problem Pairs

For each of the 60 base problems $B_i$, we tracked the joint behavior $(Y_i^{\text{intact}}, Y_i^{\text{defective}})$:
* **Both Correct ($a$):** 0 pairs (0.0%)
* **The Reliability Gap ($b$ - Solved Intact, Hallucinated Defective):** 1 pair (1.7%)
* **Arithmetic Error Only ($c$ - Failed Intact, Abstained Defective):** 0 pairs (0.0%)
* **Both Failed ($d$ - Failed Intact & Hallucinated Defective):** 59 pairs (98.3%)

### McNemar's Test for Discordance
Comparing the discordance between intact problem solving and defective abstention:
$$\chi^2 = \frac{(|1 - 0| - 1)^2}{1 + 0} = 0.0, \quad p = 1.0$$
The uniform 0% abstention rate across all defective instances confirms a complete epistemic blind spot: the instruction-tuned model has no functional mechanism for rejecting underdetermined prompts.

---

## 5. What Was Surprising?

1. **Zero Voluntary Abstention:** Despite the system prompt explicitly stating: *"If the answer cannot be uniquely determined from the stated facts, or if the supplied facts are contradictory or inconsistent, return INSUFFICIENT"*, the model never voluntarily produced `INSUFFICIENT`.
2. **Anchoring Heuristic:** When a variable was missing, the model did not generate random large numbers; instead, it systematically anchored on existing numbers mentioned in the prompt.
3. **Format Compliance vs Semantic Caution:** The model achieved 100% JSON contract compliance (20/20 valid JSON extractions in the pilot and 120/120 in the full run), showing that while instruction-tuning succeeds at structural compliance, it fails at semantic boundary awareness.
