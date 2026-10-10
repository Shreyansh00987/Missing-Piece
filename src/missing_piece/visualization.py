"""
Publication-quality visualization suite for Missing Piece benchmark.
Adheres to editorial scientific research aesthetics:
- Restrained, intentional color palette.
- High typographic clarity and legible annotations.
- Wilson 95% score confidence intervals.
- Paired dumbbell / delta charts illustrating the Reliability Gap.
"""

import os
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from missing_piece.models import BenchmarkSummary, ScoredResult, ConditionType, ExpectedStatus

# Apply clean scientific publication styling
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.labelweight": "medium",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 15,
    "figure.titleweight": "bold",
    "figure.dpi": 300,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
    "axes.edgecolor": "#94A3B8",
    "axes.linewidth": 0.8,
})

# Editorial palette
COLOR_ACCENT_BLUE = "#2563EB"       # Solvable / Answerable
COLOR_SUCCESS_GREEN = "#059669"     # Appropriate Abstention
COLOR_DANGER_RED = "#DC2626"        # Confidently Wrong
COLOR_NEUTRAL_SLATE = "#64748B"     # Baseline / Neutral
COLOR_DARK_TEXT = "#0F172A"
COLOR_BG_CARD = "#F8FAFC"


class BenchmarkVisualizer:
    """Generates all 6 required benchmark figures."""

    def __init__(self, output_dir: str = "assets/charts"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_figure_1_reliability_gap(self, summaries: List[BenchmarkSummary]):
        """
        Figure 1: The Reliability Gap
        Compares Answer Accuracy on Answerable problems vs Appropriate Abstention on Unanswerable problems.
        """
        fig, ax = plt.subplots(figsize=(9, 5.2))
        
        models = [s.model_id for s in summaries]
        ans_acc = [s.answer_accuracy * 100 for s in summaries]
        abst_rate = [s.appropriate_abstention_rate * 100 for s in summaries]
        
        x = np.arange(len(models))
        width = 0.35
        
        rects1 = ax.bar(x - width/2, ans_acc, width, label="Answer Accuracy (Answerable N=60)", color=COLOR_ACCENT_BLUE, alpha=0.9, edgecolor="#1D4ED8")
        rects2 = ax.bar(x + width/2, abst_rate, width, label="Appropriate Abstention (Unanswerable N=60)", color=COLOR_SUCCESS_GREEN, alpha=0.9, edgecolor="#047857")
        
        # Add data labels
        for rect in rects1:
            h = rect.get_height()
            ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#1E3A8A")
        for rect in rects2:
            h = rect.get_height()
            ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#064E3B")

        ax.set_ylabel("Rate (%)")
        ax.set_title("Figure 1: The Reliability Gap in Problem-Solving vs Abstention", pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=10, ha="right")
        ax.set_ylim(0, 115)
        ax.legend(frameon=True, facecolor=COLOR_BG_CARD, edgecolor="#CBD5E1", loc="upper right")
        
        plt.tight_layout()
        path = os.path.join(self.output_dir, "viz1_reliability_gap.png")
        plt.savefig(path, dpi=300)
        plt.close()
        return path

    def plot_figure_2_confidently_wrong_rate(self, summaries: List[BenchmarkSummary]):
        """
        Figure 2: Confidently Wrong Rate on Unanswerable Problems
        Shows how often models supply a specific hallucinated number when information is deficient.
        """
        fig, ax = plt.subplots(figsize=(8.5, 4.8))
        
        models = [s.model_id for s in summaries]
        conf_wrong = [s.confidently_wrong_rate * 100 for s in summaries]
        errors_low = [(s.confidently_wrong_rate - s.confidently_wrong_rate_ci[0]) * 100 for s in summaries]
        errors_high = [(s.confidently_wrong_rate_ci[1] - s.confidently_wrong_rate_rate if hasattr(s, 'x') else s.confidently_wrong_rate_ci[1] - s.confidently_wrong_rate) * 100 for s in summaries]
        
        y_pos = np.arange(len(models))
        bars = ax.barh(y_pos, conf_wrong, color=COLOR_DANGER_RED, alpha=0.85, edgecolor="#991B1B", height=0.55)
        
        # Add Wilson error bars
        yerr = [
            [max(0, (s.confidently_wrong_rate - s.confidently_wrong_rate_ci[0]) * 100) for s in summaries],
            [max(0, (s.confidently_wrong_rate_ci[1] - s.confidently_wrong_rate) * 100) for s in summaries]
        ]
        ax.errorbar(conf_wrong, y_pos, xerr=yerr, fmt='none', ecolor="#450A0A", capsize=4, elinewidth=1.2)

        for i, v in enumerate(conf_wrong):
            ci = summaries[i].confidently_wrong_rate_ci
            ax.text(v + 3.5, i, f"{v:.1f}% (95% CI: [{ci[0]:.2f}, {ci[1]:.2f}])", va="center", fontsize=9, fontweight="bold", color="#7F1D1D")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(models)
        ax.set_xlabel("Confidently Wrong Rate on Defective Problems (%)")
        ax.set_title("Figure 2: Rate of Confident Hallucination on Unanswerable Problems", pad=15)
        ax.set_xlim(0, 125)
        
        plt.tight_layout()
        path = os.path.join(self.output_dir, "viz2_confidently_wrong_rate.png")
        plt.savefig(path, dpi=300)
        plt.close()
        return path

    def plot_figure_3_category_breakdown(self, summary: BenchmarkSummary):
        """
        Figure 3: Failure Category Breakdown for Evaluated Model
        Compares accuracy across: Intact, Missing Quantity, Missing Relationship, Contradiction.
        """
        fig, ax = plt.subplots(figsize=(8.5, 4.8))
        
        cond_map = summary.condition_breakdown
        categories = ["intact", "missing_quantity", "missing_relationship", "contradiction"]
        labels = ["Answerable (Intact)", "Missing Quantity", "Missing Relationship", "Contradictory Facts"]
        
        accs = [cond_map.get(c, {}).get("accuracy", 0.0) * 100 for c in categories]
        cis = [cond_map.get(c, {}).get("ci_95", (0.0, 0.0)) for c in categories]
        
        colors = [COLOR_ACCENT_BLUE, "#D97706", "#7C3AED", COLOR_DANGER_RED]
        bars = ax.bar(labels, accs, color=colors, alpha=0.85, width=0.55)
        
        # Wilson error bars
        yerr = [
            [max(0, accs[i] - cis[i][0] * 100) for i in range(len(categories))],
            [max(0, cis[i][1] * 100 - accs[i]) for i in range(len(categories))]
        ]
        ax.errorbar(range(len(categories)), accs, yerr=yerr, fmt='none', ecolor="#1E293B", capsize=4, elinewidth=1.2)

        for rect in bars:
            h = rect.get_height()
            ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 5),
                        textcoords="offset points", ha="center", va="bottom", fontsize=10, fontweight="bold")

        ax.set_ylabel("Decision Accuracy (%)")
        ax.set_title(f"Figure 3: Decision Accuracy by Information Defect Mode ({summary.model_id})", pad=15)
        ax.set_ylim(0, 115)
        
        plt.tight_layout()
        path = os.path.join(self.output_dir, "viz3_failure_category_breakdown.png")
        plt.savefig(path, dpi=300)
        plt.close()
        return path

    def plot_figure_4_paired_behavior(self, summary: BenchmarkSummary):
        """
        Figure 4: Paired Behavior Changes (Intact Twin vs Defective Twin)
        Shows distribution of the 60 problem pairs.
        """
        fig, ax = plt.subplots(figsize=(8.5, 5))
        
        quadrants = [
            ("Both Correct\n(Solved Intact & Abstained)", summary.paired_both_correct, COLOR_SUCCESS_GREEN),
            ("The Reliability Gap\n(Solved Intact, Hallucinated Defective)", summary.paired_intact_correct_modified_wrong, COLOR_DANGER_RED),
            ("Arithmetic Error Only\n(Failed Intact, Abstained Defective)", summary.paired_intact_wrong_modified_correct, "#F59E0B"),
            ("Both Failed\n(Failed Intact & Hallucinated)", summary.paired_both_wrong, COLOR_NEUTRAL_SLATE)
        ]
        
        labels = [q[0] for q in quadrants]
        counts = [q[1] for q in quadrants]
        colors = [q[2] for q in quadrants]
        
        bars = ax.barh(labels, counts, color=colors, alpha=0.88, height=0.55)
        
        for bar in bars:
            w = bar.get_width()
            pct = (w / summary.paired_count) * 100 if summary.paired_count > 0 else 0
            ax.text(w + 1.2, bar.get_y() + bar.get_height()/2, f"{int(w)} pairs ({pct:.1f}%)", va="center", fontsize=10, fontweight="bold")

        ax.set_xlabel("Number of Problem Pairs (Total N=60 Pairs)")
        ax.set_title(f"Figure 4: Paired Joint Outcomes across Twin Problems ({summary.model_id})", pad=15)
        ax.set_xlim(0, max(counts) + 12 if counts else 60)
        
        plt.tight_layout()
        path = os.path.join(self.output_dir, "viz4_paired_behavior_changes.png")
        plt.savefig(path, dpi=300)
        plt.close()
        return path

    def plot_figure_5_uncertainty(self, summaries: List[BenchmarkSummary]):
        """
        Figure 5: Uncertainty Indicators (Wilson 95% Confidence Intervals on Balanced Accuracy)
        """
        fig, ax = plt.subplots(figsize=(8.5, 4.5))
        
        models = [s.model_id for s in summaries]
        bal_acc = [s.balanced_accuracy * 100 for s in summaries]
        exact_match = [s.overall_exact_match * 100 for s in summaries]
        cis = [s.overall_exact_match_ci for s in summaries]
        
        y_pos = np.arange(len(models))
        
        # Plot point estimates with Wilson error bars
        xerr = [
            [max(0, exact_match[i] - cis[i][0] * 100) for i in range(len(models))],
            [max(0, cis[i][1] * 100 - exact_match[i]) for i in range(len(models))]
        ]
        
        ax.errorbar(exact_match, y_pos, xerr=xerr, fmt='o', color="#1E3A8A", ecolor="#3B82F6",
                    elinewidth=2, capsize=5, capthick=1.5, markersize=8, label="Overall Exact Match (with 95% Wilson CI)")
        
        # Plot balanced accuracy markers
        ax.plot(bal_acc, y_pos, 's', color="#059669", markersize=8, label="Balanced Accuracy")
        
        # Add chance / baseline reference line at 50%
        ax.axvline(x=50.0, color="#94A3B8", linestyle=":", linewidth=1.5, label="Balanced Random Baseline (50%)")

        for i, m in enumerate(models):
            ax.text(exact_match[i] + 3.0, i - 0.15, f"{exact_match[i]:.1f}% [{cis[i][0]*100:.1f}%, {cis[i][1]*100:.1f}%]",
                    fontsize=9, color="#1E293B", fontweight="medium")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(models)
        ax.set_xlabel("Accuracy (%)")
        ax.set_title("Figure 5: Metric Uncertainty & 95% Wilson Score Confidence Intervals", pad=15)
        ax.set_xlim(0, 115)
        ax.legend(frameon=True, facecolor=COLOR_BG_CARD, edgecolor="#CBD5E1", loc="lower right")
        
        plt.tight_layout()
        path = os.path.join(self.output_dir, "viz5_uncertainty_ci.png")
        plt.savefig(path, dpi=300)
        plt.close()
        return path

    def create_case_study_card(self, cases: List[Dict[str, Any]]):
        """
        Figure 6: Editorial Case Studies Table/Infographic
        Renders real benchmark failure cases showing prompt, defect, model output, and diagnosis.
        """
        fig, ax = plt.subplots(figsize=(11, 6.5))
        ax.axis("off")
        
        title_text = "Figure 6: Benchmark Case Studies: The Anatomy of Confident Hallucination"
        ax.text(0.02, 0.95, title_text, fontsize=14, fontweight="bold", color=COLOR_DARK_TEXT)
        ax.text(0.02, 0.90, "Real paired examples illustrating where epistemic caution fails in language models", fontsize=10.5, color=COLOR_NEUTRAL_SLATE)

        y = 0.82
        for case in cases[:3]:
            # Draw container card
            rect = plt.Rectangle((0.02, y - 0.23), 0.96, 0.22, transform=ax.transAxes,
                                 facecolor=COLOR_BG_CARD, edgecolor="#E2E8F0", linewidth=1)
            ax.add_patch(rect)
            
            # Badge
            badge_color = COLOR_DANGER_RED if case.get("outcome") == "CONFIDENTLY_WRONG" else COLOR_SUCCESS_GREEN
            ax.text(0.04, y - 0.03, f"[{case.get('condition', '').upper()}] - {case.get('example_id')}",
                    fontsize=9.5, fontweight="bold", color=COLOR_DARK_TEXT)
            ax.text(0.75, y - 0.03, f"Outcome: {case.get('outcome')}",
                    fontsize=9.5, fontweight="bold", color=badge_color)
            
            # Prompt text snippet
            prompt_snip = case.get("prompt", "")[:130] + ("..." if len(case.get("prompt", "")) > 130 else "")
            ax.text(0.04, y - 0.08, f"Prompt: \"{prompt_snip}\"", fontsize=9, style="italic", color="#334155")
            
            # Model response vs Expected
            ax.text(0.04, y - 0.13, f"Expected Status: {case.get('expected_status')} | Ground Truth: {case.get('expected_answer')}",
                    fontsize=9, fontweight="bold", color="#0F766E")
            ax.text(0.04, y - 0.17, f"Model Output: {case.get('raw_output')}",
                    fontsize=9, color="#BE123C", fontfamily="monospace")
            
            # Diagnosis
            ax.text(0.04, y - 0.21, f"Diagnosis: {case.get('diagnosis')}",
                    fontsize=8.5, color="#475569")
            
            y -= 0.26

        path = os.path.join(self.output_dir, "viz6_case_studies.png")
        plt.tight_layout()
        plt.savefig(path, dpi=300)
        plt.close()
        return path
