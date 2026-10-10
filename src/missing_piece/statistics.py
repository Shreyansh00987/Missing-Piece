"""
Statistical analysis engine for Missing Piece benchmark.
Implements:
- Wilson 95% score confidence intervals for binary proportions.
- Key abstention and accuracy metrics.
- Paired discordance analysis (intact vs defective twin).
- McNemar's test for paired behavioral shifts.
"""

import math
from typing import List, Dict, Any, Tuple, Optional
from missing_piece.models import (
    ScoredResult,
    BenchmarkSummary,
    ConditionType,
    ExpectedStatus,
    OutcomeCategory
)


def wilson_score_interval(successes: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate Wilson score confidence interval for a binomial proportion.
    Accurate and well-behaved even with small sample sizes or near boundary (0 or 1).
    """
    if total <= 0:
        return (0.0, 0.0)
    
    # Common z-values
    if abs(confidence - 0.95) < 1e-3:
        z = 1.959963984540054
    elif abs(confidence - 0.99) < 1e-3:
        z = 2.5758293035489004
    elif abs(confidence - 0.90) < 1e-3:
        z = 1.6448536269514722
    else:
        # Normal quantile approximation
        z = 1.96

    p = successes / total
    denominator = 1.0 + (z**2) / total
    center = (p + (z**2) / (2.0 * total)) / denominator
    spread = (z * math.sqrt((p * (1.0 - p) / total) + ((z**2) / (4.0 * (total**2))))) / denominator
    
    lower = max(0.0, center - spread)
    upper = min(1.0, center + spread)
    return (round(lower, 4), round(upper, 4))


def mcnemar_test(b: int, c: int) -> Dict[str, Any]:
    """
    Perform McNemar's test for paired nominal data with continuity correction.
    b: Number of pairs where Item A succeeded and Item B failed.
    c: Number of pairs where Item A failed and Item B succeeded.
    """
    total_discordant = b + c
    if total_discordant == 0:
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "total_discordant": 0,
            "significant_05": False
        }
    
    # McNemar's chi-squared with Edwards' continuity correction
    chi2 = ((abs(b - c) - 1.0) ** 2) / total_discordant
    
    # P-value approximation from 1-degree-of-freedom Chi-squared distribution:
    # using survival function approximation or normal approximation
    # For df=1, p-value = erfc(sqrt(chi2 / 2))
    p_value = math.erfc(math.sqrt(max(0.0, chi2) / 2.0))
    
    return {
        "statistic": round(chi2, 4),
        "p_value": round(p_value, 6),
        "total_discordant": total_discordant,
        "significant_05": (p_value < 0.05)
    }


class BenchmarkStatistics:
    """Computes comprehensive benchmark summary and statistics from scored results."""

    @staticmethod
    def summarize(results: List[ScoredResult], model_id: Optional[str] = None) -> BenchmarkSummary:
        if not results:
            raise ValueError("No scored results provided to summarize.")

        mid = model_id or results[0].model_id
        model_results = [r for r in results if r.model_id == mid]
        
        total_examples = len(model_results)
        answerable = [r for r in model_results if r.expected_status == ExpectedStatus.ANSWER]
        unanswerable = [r for r in model_results if r.expected_status == ExpectedStatus.INSUFFICIENT]

        n_ans = len(answerable)
        n_unans = len(unanswerable)

        # 1. Answerable metrics
        correct_ans = sum(1 for r in answerable if r.outcome == OutcomeCategory.CORRECT_ANSWER)
        answered_ans = sum(1 for r in answerable if r.outcome in (OutcomeCategory.CORRECT_ANSWER, OutcomeCategory.INCORRECT_ANSWER))
        
        answer_accuracy = correct_ans / n_ans if n_ans > 0 else 0.0
        answer_accuracy_ci = wilson_score_interval(correct_ans, n_ans)
        answer_coverage = answered_ans / n_ans if n_ans > 0 else 0.0

        # 2. Unanswerable metrics
        appropriate_abstain = sum(1 for r in unanswerable if r.outcome == OutcomeCategory.APPROPRIATE_ABSTENTION)
        confidently_wrong = sum(1 for r in unanswerable if r.outcome == OutcomeCategory.CONFIDENTLY_WRONG)
        
        appropriate_abstention_rate = appropriate_abstain / n_unans if n_unans > 0 else 0.0
        appropriate_abstention_rate_ci = wilson_score_interval(appropriate_abstain, n_unans)
        
        confidently_wrong_rate = confidently_wrong / n_unans if n_unans > 0 else 0.0
        confidently_wrong_rate_ci = wilson_score_interval(confidently_wrong, n_unans)

        # Total abstentions across all problems
        total_abstentions = sum(1 for r in model_results if r.parsed_status == "INSUFFICIENT")
        abstention_precision = appropriate_abstain / total_abstentions if total_abstentions > 0 else 0.0

        # 3. Overall Exact Match & Balanced Accuracy
        total_correct = sum(1 for r in model_results if r.is_correct)
        overall_exact_match = total_correct / total_examples if total_examples > 0 else 0.0
        overall_exact_match_ci = wilson_score_interval(total_correct, total_examples)
        
        balanced_accuracy = (answer_accuracy + appropriate_abstention_rate) / 2.0
        malformed_count = sum(1 for r in model_results if r.is_malformed)
        malformed_rate = malformed_count / total_examples if total_examples > 0 else 0.0

        # 4. Condition Breakdown
        condition_breakdown: Dict[str, Dict[str, Any]] = {}
        for cond in ConditionType:
            cond_res = [r for r in model_results if r.condition == cond]
            if cond_res:
                n_c = len(cond_res)
                c_correct = sum(1 for r in cond_res if r.is_correct)
                c_wrong = sum(1 for r in cond_res if r.is_confidently_wrong)
                condition_breakdown[cond.value] = {
                    "total": n_c,
                    "correct": c_correct,
                    "accuracy": round(c_correct / n_c, 4),
                    "ci_95": wilson_score_interval(c_correct, n_c),
                    "confidently_wrong": c_wrong,
                    "confidently_wrong_rate": round(c_wrong / n_c, 4) if n_c > 0 else 0.0
                }

        # 5. Category (Domain) Breakdown
        category_breakdown: Dict[str, Dict[str, Any]] = {}
        all_categories = sorted(list({r.category for r in model_results}))
        for cat in all_categories:
            cat_res = [r for r in model_results if r.category == cat]
            n_cat = len(cat_res)
            cat_correct = sum(1 for r in cat_res if r.is_correct)
            category_breakdown[cat] = {
                "total": n_cat,
                "correct": cat_correct,
                "accuracy": round(cat_correct / n_cat, 4),
                "ci_95": wilson_score_interval(cat_correct, n_cat)
            }

        # 6. Paired Analysis (Intact vs Modified Twin)
        paired_dict: Dict[str, Dict[str, ScoredResult]] = {}
        for r in model_results:
            paired_dict.setdefault(r.pair_id, {})[r.condition.value] = r

        paired_count = len(paired_dict)
        both_correct = 0
        intact_correct_mod_wrong = 0
        intact_wrong_mod_correct = 0
        both_wrong = 0

        for pid, pair_items in paired_dict.items():
            intact_item = pair_items.get(ConditionType.INTACT.value)
            # Find the defective item (not intact)
            mod_item = next((v for k, v in pair_items.items() if k != ConditionType.INTACT.value), None)
            
            if intact_item and mod_item:
                intact_ok = intact_item.is_correct
                mod_ok = mod_item.is_correct
                
                if intact_ok and mod_ok:
                    both_correct += 1
                elif intact_ok and not mod_ok:
                    intact_correct_mod_wrong += 1
                elif not intact_ok and mod_ok:
                    intact_wrong_mod_correct += 1
                else:
                    both_wrong += 1

        return BenchmarkSummary(
            model_id=mid,
            total_examples=total_examples,
            total_answerable=n_ans,
            total_unanswerable=n_unans,
            answer_accuracy=round(answer_accuracy, 4),
            answer_accuracy_ci=answer_accuracy_ci,
            answer_coverage=round(answer_coverage, 4),
            appropriate_abstention_rate=round(appropriate_abstention_rate, 4),
            appropriate_abstention_rate_ci=appropriate_abstention_rate_ci,
            confidently_wrong_rate=round(confidently_wrong_rate, 4),
            confidently_wrong_rate_ci=confidently_wrong_rate_ci,
            abstention_precision=round(abstention_precision, 4),
            overall_exact_match=round(overall_exact_match, 4),
            overall_exact_match_ci=overall_exact_match_ci,
            balanced_accuracy=round(balanced_accuracy, 4),
            malformed_rate=round(malformed_rate, 4),
            condition_breakdown=condition_breakdown,
            category_breakdown=category_breakdown,
            paired_count=paired_count,
            paired_both_correct=both_correct,
            paired_intact_correct_modified_wrong=intact_correct_mod_wrong,
            paired_intact_wrong_modified_correct=intact_wrong_mod_correct,
            paired_both_wrong=both_wrong
        )
