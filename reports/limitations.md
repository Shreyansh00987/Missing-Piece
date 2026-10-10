# MISSING PIECE: Threats to Validity, Limitations, and Boundary Conditions

**Document Status:** Complete  
**Benchmark Version:** 1.0.0  
**Scope:** Critical Evaluation of Experimental Constraints  

---

## 1. Internal Validity

### 1.1 Synthetic Problem Templates
* **Limitation:** The benchmark relies on parameterized word problem templates rather than naturalistic queries scraped from human discourse or multi-turn conversational logs.
* **Mitigation & Boundary:** Synthetic templates were chosen intentionally to enable deterministic, mechanically proven ground truths and to isolate single semantic alterations between intact and defective variants. We explicitly do *not* claim that performance on synthetic arithmetic problems represents all real-world AI reasoning.

### 1.2 Output Contract Rigidity
* **Limitation:** The benchmark enforces a strict JSON schema: `{"status": "ANSWER", "answer": "<n>"}` or `{"status": "INSUFFICIENT", "answer": null}`. Certain models may possess the capability to identify missing information in unstructured free-form prose, but fail to adhere strictly to the JSON schema.
* **Mitigation & Boundary:** The output parser employs multi-stage recovery (direct JSON, markdown code block extraction, and regex outermost-brace matching). Furthermore, malformed responses are reported separately in all benchmark tables rather than silently penalizing mathematical competence.

### 1.3 Temperature and Decoding Determinism
* **Limitation:** Greedy decoding ($T=0.0$) was employed across all evaluations to ensure exact mathematical reproducibility. However, greedy decoding captures only the mode of the model's conditional token distribution.
* **Mitigation & Boundary:** For an epistemic benchmark evaluating whether a model commits to an unsupported answer, greedy mode evaluation is the strictest standard of default model behavior.

---

## 2. Statistical Validity & Sample Size

### 2.1 Sample Size Constraints (N=120, 60 Pairs)
* **Limitation:** The benchmark contains 120 total evaluation instances (60 answerable, 60 unanswerable) across 6 domains. While this sample size is sufficient to identify statistically significant effects ($p < 0.001$ via McNemar's test), it cannot support fine-grained subgroup analyses across small domain intersections without wider confidence bounds.
* **Mitigation & Boundary:** Every proportion is reported alongside exact 95% Wilson score confidence intervals. We explicitly avoid overstating the precision of category-level percentages.

### 2.2 Pairing Asymmetry Across Defect Types
* **Limitation:** The 60 base problems allocate 20 pairs to Missing Quantity, 20 pairs to Missing Relationship, and 20 pairs to Contradiction. Comparing performance across defect categories involves different base problem templates.
* **Mitigation & Boundary:** Within each defect category, the comparison between Intact and Defective is strictly paired (identical base templates).

---

## 3. Construct Validity

### 3.1 Defining Inconsistency as "INSUFFICIENT"
* **Limitation:** In classical logic, the Principle of Explosion states that from a contradiction, any proposition follows. One could argue philosophically that asking "How many packages did the van deliver?" when given contradictory totals has an undefined status rather than "insufficient information."
* **Mitigation & Boundary:** We explicitly define the benchmark operational task: *Can the provided premises support a single, unique, consistent real-world answer?* When premises are inconsistent, no unique real-world quantity is supported, justifying the abstention label `INSUFFICIENT`.

### 3.2 Distinguishing Arithmetic Incapacity from Epistemic Failure
* **Limitation:** If a model returns an incorrect number on an intact problem, it has suffered an arithmetic or reasoning failure. If it also returns a number on the defective problem, it has committed an epistemic hallucination.
* **Mitigation & Boundary:** Our 4-way paired classification cleanly separates these behaviors:
  - Both Correct ($a$)
  - The Reliability Gap: Solved Intact, Hallucinated Defective ($b$)
  - Arithmetic Error Only: Failed Intact, Abstained Defective ($c$)
  - Both Failed ($d$)

---

## 4. External Validity

### 4.1 Generality to Production AI Systems
* **Limitation:** Performance on MISSING PIECE should not be construed as a general measure of model safety, alignment, or factual truthfulness across open-domain web retrieval.
* **Boundary:** MISSING PIECE measures a specific, vital failure mode: **the compulsion of autoregressive language models to solve rather than withhold when problems are structurally underspecified.**
