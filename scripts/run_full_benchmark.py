"""
Full Benchmark Execution Script for Missing Piece.
Evaluates the complete 120-example benchmark across all models and baseline controls.
Scores results deterministically, computes Wilson 95% CIs, and produces all 6 publication figures.
"""

import os
import sys
import time
import json
import pandas as pd
from tabulate import tabulate

sys.path.insert(0, "src")
from missing_piece.generator import DatasetGenerator
from missing_piece.validators import DatasetValidator
from missing_piece.inference import (
    InferenceRunner,
    LocalTransformersAdapter,
    HeuristicBaselineAdapter
)
from missing_piece.parser import OutputParser
from missing_piece.scoring import ScoringEngine
from missing_piece.statistics import BenchmarkStatistics, mcnemar_test
from missing_piece.visualization import BenchmarkVisualizer


def main():
    print("=" * 80)
    print("MISSING PIECE: FULL BENCHMARK EXPERIMENT EXECUTION (N=120)")
    print("=" * 80)
    
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("outputs/cache", exist_ok=True)
    os.makedirs("assets/charts", exist_ok=True)

    # 1. Dataset Generation and Validation
    print("\n[Step 1] Loading and verifying full benchmark dataset...")
    gen = DatasetGenerator(seed=42)
    examples = gen.generate_randomized()
    validator = DatasetValidator()
    val_report = validator.validate(examples)
    assert val_report.is_valid, f"Validation failed: {val_report.errors}"
    print(f"Dataset successfully verified: {len(examples)} examples (60 Intact, 60 Defective).")

    # 2. Model Lineup Setup
    print("\n[Step 2] Initializing model lineup...")
    models = [
        HeuristicBaselineAdapter("always_answer", seed=42),
        HeuristicBaselineAdapter("always_abstain", seed=42),
        HeuristicBaselineAdapter("random_choice", seed=42),
        LocalTransformersAdapter("HuggingFaceTB/SmolLM2-135M-Instruct")
    ]
    print(f"Models scheduled for evaluation: {[m.model_id for m in models]}")

    # 3. Execution Pipeline
    print("\n[Step 3] Running full benchmark inference across all models...")
    runner = InferenceRunner(cache_dir="outputs/cache")
    all_scored_records = []
    summaries = []

    for model in models:
        t0 = time.time()
        print(f"\n---> Evaluating model: {model.model_id} (120 items)...")
        responses = runner.evaluate_model(model, examples, use_cache=True)
        elapsed = time.time() - t0
        print(f"Done in {elapsed:.2f}s (Avg {elapsed/len(responses):.2f}s/query).")

        # Parse responses
        parsed = [OutputParser.parse(r.raw_text, r.example_id, r.model_id) for r in responses]
        malformed = sum(1 for p in parsed if not p.is_valid_format)
        print(f"Parsed format check: {len(parsed) - malformed}/120 valid ({malformed} malformed).")

        # Score responses
        scored = ScoringEngine.score_all(examples, parsed)
        for s in scored:
            all_scored_records.append(s.model_dump())

        # Statistical summary
        summary = BenchmarkStatistics.summarize(scored, model.model_id)
        summaries.append(summary)

    # 4. Save Scored Data Table
    print("\n[Step 4] Saving scored results and summaries...")
    scored_df = pd.DataFrame(all_scored_records)
    scored_csv_path = "outputs/scored_results.csv"
    scored_df.to_csv(scored_csv_path, index=False)
    print(f"Saved scored results to: {scored_csv_path}")

    summaries_dict = [s.model_dump() for s in summaries]
    summaries_json_path = "outputs/model_summaries.json"
    with open(summaries_json_path, "w", encoding="utf-8") as f:
        json.dump(summaries_dict, f, indent=2)
    print(f"Saved model summaries to: {summaries_json_path}")

    # 5. Display Comprehensive Summary Table
    print("\n" + "=" * 80)
    print("FINAL BENCHMARK EVALUATION RESULTS (N=120 Items)")
    print("=" * 80)
    
    summary_rows = []
    for s in summaries:
        summary_rows.append([
            s.model_id,
            f"{s.answer_accuracy:.1%} [{s.answer_accuracy_ci[0]:.2f}, {s.answer_accuracy_ci[1]:.2f}]",
            f"{s.appropriate_abstention_rate:.1%} [{s.appropriate_abstention_rate_ci[0]:.2f}, {s.appropriate_abstention_rate_ci[1]:.2f}]",
            f"{s.confidently_wrong_rate:.1%} [{s.confidently_wrong_rate_ci[0]:.2f}, {s.confidently_wrong_rate_ci[1]:.2f}]",
            f"{s.abstention_precision:.1%}",
            f"{s.balanced_accuracy:.1%}",
            f"{s.overall_exact_match:.1%} [{s.overall_exact_match_ci[0]:.2f}, {s.overall_exact_match_ci[1]:.2f}]",
            f"{s.malformed_rate:.1%}"
        ])

    headers = [
        "Model",
        "Answer Acc (95% CI)",
        "Appropriate Abstention",
        "Confidently Wrong",
        "Abstain Precision",
        "Balanced Acc",
        "Exact Match (95% CI)",
        "Malformed"
    ]
    summary_table_str = tabulate(summary_rows, headers=headers, tablefmt="github")
    print(summary_table_str)

    with open("outputs/summary_table.md", "w", encoding="utf-8") as f:
        f.write("# Missing Piece Benchmark Results\n\n" + summary_table_str + "\n")

    # 6. Paired Discordance & McNemar Test
    print("\n[Step 5] Paired Discordance Analysis:")
    for s in summaries:
        mcnemar = mcnemar_test(s.paired_intact_correct_modified_wrong, s.paired_intact_wrong_modified_correct)
        print(f"\nModel: {s.model_id}")
        print(f"  Total Pairs: {s.paired_count}")
        print(f"  Both Correct: {s.paired_both_correct}")
        print(f"  Intact Correct & Defective Hallucinated (The Gap): {s.paired_intact_correct_modified_wrong}")
        print(f"  Intact Wrong & Defective Abstained: {s.paired_intact_wrong_modified_correct}")
        print(f"  Both Failed: {s.paired_both_wrong}")
        print(f"  McNemar Chi2: {mcnemar['statistic']}, p-value: {mcnemar['p_value']} (Sig: {mcnemar['significant_05']})")

    # 7. Generate All 6 Figures
    print("\n[Step 6] Generating publication-quality charts...")
    visualizer = BenchmarkVisualizer(output_dir="assets/charts")
    p1 = visualizer.plot_figure_1_reliability_gap(summaries)
    p2 = visualizer.plot_figure_2_confidently_wrong_rate(summaries)
    
    # SmolLM2 detailed breakdown
    smol_summary = next(s for s in summaries if "SmolLM2" in s.model_id)
    p3 = visualizer.plot_figure_3_category_breakdown(smol_summary)
    p4 = visualizer.plot_figure_4_paired_behavior(smol_summary)
    p5 = visualizer.plot_figure_5_uncertainty(summaries)

    # Real case studies for figure 6
    smol_scored = [s for s in all_scored_records if s["model_id"] == "SmolLM2-135M-Instruct"]
    smol_cache = runner.load_cache("SmolLM2-135M-Instruct")
    ex_map = {e.example_id: e for e in examples}
    
    # Pick 3 illustrative real failure cases
    case_studies = []
    for sc in smol_scored:
        if sc["outcome"] == "CONFIDENTLY_WRONG":
            ex = ex_map[sc["example_id"]]
            raw_resp = smol_cache[sc["example_id"]].raw_text
            clean_resp = raw_resp.strip().replace("\n", " ")[:100]
            
            if ex.condition.value == "missing_quantity" and len([c for c in case_studies if c["condition"] == "missing_quantity"]) == 0:
                case_studies.append({
                    "example_id": ex.example_id,
                    "condition": "Missing Quantity",
                    "prompt": ex.problem_text,
                    "expected_status": "INSUFFICIENT",
                    "expected_answer": "None",
                    "raw_output": clean_resp,
                    "outcome": "CONFIDENTLY_WRONG",
                    "diagnosis": "Model hallucinated missing count rather than abstaining."
                })
            elif ex.condition.value == "missing_relationship" and len([c for c in case_studies if c["condition"] == "missing_relationship"]) == 0:
                case_studies.append({
                    "example_id": ex.example_id,
                    "condition": "Missing Relationship",
                    "prompt": ex.problem_text,
                    "expected_status": "INSUFFICIENT",
                    "expected_answer": "None",
                    "raw_output": clean_resp,
                    "outcome": "CONFIDENTLY_WRONG",
                    "diagnosis": "Model ignored omitted rate/time connection and generated unsupported answer."
                })
            elif ex.condition.value == "contradiction" and len([c for c in case_studies if c["condition"] == "contradiction"]) == 0:
                case_studies.append({
                    "example_id": ex.example_id,
                    "condition": "Contradiction",
                    "prompt": ex.problem_text,
                    "expected_status": "INSUFFICIENT",
                    "expected_answer": "None",
                    "raw_output": clean_resp,
                    "outcome": "CONFIDENTLY_WRONG",
                    "diagnosis": "Model failed to detect mutually incompatible premises."
                })
        if len(case_studies) == 3:
            break

    p6 = visualizer.create_case_study_card(case_studies)
    print(f"Charts saved:\n  1. {p1}\n  2. {p2}\n  3. {p3}\n  4. {p4}\n  5. {p5}\n  6. {p6}")
    
    print("\n" + "=" * 80)
    print("BENCHMARK EXECUTION AND ANALYSIS FULLY COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
