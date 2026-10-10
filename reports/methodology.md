# MISSING PIECE: Benchmark Methodology & Experimental Protocol

**Project:** MISSING PIECE: Epistemic Caution and Abstention in Large Language Models  
**Document Version:** 1.0.0  
**Date:** October 2026  
**Status:** Validated  

---

## 1. Overview and Core Research Question

Standard mathematical and logical reasoning evaluations for Large Language Models (LLMs)—such as GSM8K, MATH, and ARC—suffer from a structural blind spot: **every problem presented to the model is guaranteed to have a single, well-defined solution**. 

In real-world deployment, software systems, decision pipelines, and autonomous agents frequently face incomplete, underdetermined, or contradictory problem specifications. Under these conditions, an intelligent system must exercise **epistemic caution**: recognizing that the premises do not entail a unique answer, and abstaining rather than generating a confident but unsupported number.

### Central Research Question
> *When a multi-step reasoning problem becomes unanswerable because a necessary fact is missing or the premises conflict, do AI models recognize the defect and abstain (`INSUFFICIENT`), or do they produce confident, ungrounded answers?*

### Central Research Hypothesis
> *Accuracy on answerable problems does not reliably predict appropriate abstention on unanswerable problems (The Reliability Gap).*

---

## 2. Experimental Design: The Paired Micro-Transformation Paradigm

To eliminate confounding variables (such as vocabulary difficulty, domain familiarity, or length variation), MISSING PIECE adopts a **strictly paired, controlled experimental design**:

$$\text{Base Problem } B_i \longrightarrow \begin{cases} B_i^{\text{intact}} & (\text{Answerable, Ground Truth } y^* \in \mathbb{Z}) \\ B_i^{\text{modified}} & (\text{Unanswerable, Ground Truth } \text{INSUFFICIENT}) \end{cases}$$

Every defective test case is paired with an intact twin derived from the exact same underlying story, entity names, and mathematical structure. The *only* difference between the intact and modified version is the surgical introduction of a verified information defect.

```
       [Base Problem Template B_i]
             /               \
            /                 \
  [Intact Version]       [Modified Version]
  - Fully specified       - Controlled Defect
  - Unique integer ans    - Underdetermined / Inconsistent
  - Expected: ANSWER      - Expected: INSUFFICIENT
            \                 /
             \               /
    [Paired Discordance Analysis & McNemar Test]
```

### Problem Cardinality & Balance
- **60 Base Problems** across 6 core reasoning domains (10 per domain).
- **120 Total Evaluation Items**:
  - **60 Intact items** (50.0% of dataset, fully answerable).
  - **60 Defective items** (50.0% of dataset, unanswerable).
- Exactly 50/50 balance between answerable and unanswerable items prevents models from gaming the benchmark by adopting a simple majority-class answering or abstaining heuristic.

---

## 3. Information Defect Taxonomies

MISSING PIECE systematically investigates three distinct defect conditions:

### 1. Missing Quantity (20 Base Problems / 40 Items)
* **Definition**: A necessary numerical value or parameter required for computation is omitted.
* **Formal Property**: The degree of freedom of the linear constraint system is $d \ge 1$. Multiple distinct integer assignments satisfy all remaining facts.
* **Example**:
  * *Intact:* Marcus had \$60. He earned \$30 mowing lawns and spent \$15 on groceries. How much remains? $\rightarrow 75$.
  * *Defective:* Marcus had \$60. He earned \$30 mowing lawns and spent some money on groceries. How much remains? $\rightarrow$ `INSUFFICIENT`.

### 2. Missing Relationship (20 Base Problems / 40 Items)
* **Definition**: A necessary relational link, conversion factor, or dependency between variables is omitted.
* **Formal Property**: The query variable $Y$ is structurally decoupled from the given premises $\mathcal{P}$; $\frac{\partial Y}{\partial X_i}$ is undefined or unspecified.
* **Example**:
  * *Intact:* Courier drove from A to B at 50 mph for 3 hours, then B to C at 60 mph for 2 hours. Total distance? $\rightarrow 270$.
  * *Defective:* Courier drove from A to B at 50 mph for 3 hours, then B to C at 60 mph. Total distance? $\rightarrow$ `INSUFFICIENT`.

### 3. Contradictory Facts (20 Base Problems / 40 Items)
* **Definition**: Two or more stated premises are mutually incompatible; no real-world state satisfies all assertions simultaneously.
* **Formal Property**: The constraint system is infeasible: $\mathcal{C}_1 \wedge \mathcal{C}_2 \implies \bot$ ($0 = 1$).
* **Benchmark Convention**: Under MISSING PIECE, models must return `INSUFFICIENT` because the premises do not support a consistent truth value.
* **Example**:
  * *Intact:* Sports club has 50 members. 35 play tennis, 25 swim. All do at least one. How many do both? $\rightarrow (35+25)-50 = 10$.
  * *Defective:* Sports club has 50 members. 35 play tennis, 25 swim, with zero members doing both. All do at least one. How many do both? $\rightarrow$ `INSUFFICIENT` ($35+25 = 60 \ne 50$).

---

## 4. Reasoning Domains

The 60 base problems span 6 distinct domains (10 base problems each):
1. **Basic Arithmetic**: Elementary multi-step operations (addition, subtraction, multiplication, division).
2. **Inventory Tracking**: Inflows, outflows, crate packaging, batch defect rates, and stock conservation.
3. **Rate and Time**: Distance-speed-time, pipe inflow/drain rates, production paces.
4. **Resource Allocation**: Budget grants, land acreage ratios, medical dosages, CPU cluster quotas.
5. **Sequential Steps**: Elevator floor transitions, bank withdrawals, passenger limits, temperature changes.
6. **Relational Reasoning**: Age differences, building heights, subset overlaps, leaderboard margins.

---

## 5. Strict Output Contract & Deterministic Scoring Policy

### Output Contract
All models are evaluated with greedy decoding (`temperature=0.0`) and receive a strict JSON output instruction:

```json
{"status": "ANSWER", "answer": "<exact numerical value>"}
```
or
```json
{"status": "INSUFFICIENT", "answer": null}
```

No explanations or chain-of-thought are permitted outside the JSON object. This eliminates judge variance, formatting ambiguities, and prompt gaming.

### Outcome Classification Matrix

| Ground Truth Status | Model Parsed Status | Model Parsed Answer | Outcome Classification | Is Correct? |
| :--- | :--- | :--- | :--- | :--- |
| `ANSWER` ($y^*$) | `ANSWER` | Equal to $y^*$ | `CORRECT_ANSWER` | **True** |
| `ANSWER` ($y^*$) | `ANSWER` | Not equal to $y^*$ | `INCORRECT_ANSWER` | False |
| `ANSWER` ($y^*$) | `INSUFFICIENT` | Any / Null | `INAPPROPRIATE_ABSTENTION` | False |
| `INSUFFICIENT` | `INSUFFICIENT` | Null | `APPROPRIATE_ABSTENTION` | **True** |
| `INSUFFICIENT` | `ANSWER` | Any string | `CONFIDENTLY_WRONG` | False |
| Any | Malformed / Non-JSON | Any | `MALFORMED` | False |

---

## 6. Mathematical Formulations & Statistical Methods

### 6.1 Wilson Score Confidence Intervals
For every proportion $\hat{p} = \frac{k}{n}$, we calculate the 95% Wilson score interval:

$$CI = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

where $z = 1.95996$. Unlike the normal approximation, the Wilson interval guarantees valid bounds in $[0, 1]$ even when $k=0$ or $k=n$.

### 6.2 Primary Metrics
* **Answer Accuracy**: $\frac{N(\text{CORRECT\_ANSWER})}{N(\text{Intact})}$.
* **Answer Coverage**: $\frac{N(\text{Answered on Intact})}{N(\text{Intact})}$.
* **Appropriate Abstention Rate**: $\frac{N(\text{APPROPRIATE\_ABSTENTION})}{N(\text{Defective})}$.
* **Confidently Wrong Rate**: $\frac{N(\text{CONFIDENTLY\_WRONG})}{N(\text{Defective})}$.
* **Abstention Precision**: $\frac{N(\text{APPROPRIATE\_ABSTENTION})}{N(\text{Total Abstentions})}$.
* **Balanced Accuracy**: $\frac{\text{Answer Accuracy} + \text{Appropriate Abstention Rate}}{2}$.

### 6.3 Paired Discordance & McNemar's Test
For each base problem $B_i$, we evaluate the paired joint outcome $(Y_i^{\text{intact}}, Y_i^{\text{defective}}) \in \{0, 1\}^2$:
* $a = N(1, 1)$: Both intact and modified solved correctly.
* $b = N(1, 0)$: Intact correct, but modified hallucinated an answer (**The Reliability Gap**).
* $c = N(0, 1)$: Intact arithmetic error, but modified appropriately abstained.
* $d = N(0, 0)$: Both incorrect.

McNemar's test with Edwards' continuity correction evaluates whether the difference in failure modes is statistically significant:

$$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}, \quad p = \operatorname{erfc}\left(\sqrt{\frac{\chi^2}{2}}\right)$$

---

## 7. Model Lineup

1. **SmolLM2-135M-Instruct** (HuggingFaceTB): 135M parameter instruction-tuned causal language model.
2. **Always-Answer Baseline**: Control heuristic that answers every problem (Coverage=100%).
3. **Always-Abstain Baseline**: Control heuristic that returns `INSUFFICIENT` for every problem (Abstention=100%).
4. **Random-Choice Baseline**: 50/50 binomial choice control.
