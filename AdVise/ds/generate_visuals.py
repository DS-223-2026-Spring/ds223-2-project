"""
generate_visuals.py
AdVise — Milestone 4
Generates visual outputs and summary tables from prediction results.
Run after predict.py has produced outputs/predictions.csv

Usage:
    python generate_visuals.py
    python generate_visuals.py --predictions-path outputs/predictions.csv
"""

import argparse
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — safe for Docker/server
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── paths ──────────────────────────────────────────────────────────────────────
THIS_DIR    = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(THIS_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# ── color palette (consistent across all charts) ───────────────────────────────
TIER_COLORS = {
    "high":   "#2ecc71",
    "medium": "#f39c12",
    "low":    "#e74c3c",
}
BRAND_COLOR = "#4A90D9"


def load_predictions(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Predictions not found at {path}. Run predict.py first.")
    df = pd.read_csv(path, low_memory=False)
    print(f"Loaded {len(df):,} prediction rows.")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# CHART 1 — Tier Distribution per Target
# ──────────────────────────────────────────────────────────────────────────────
def plot_tier_distribution(df: pd.DataFrame):
    pred_cols = [c for c in df.columns if c.startswith("predicted_")]
    if not pred_cols:
        print("No predicted columns found, skipping tier distribution.")
        return

    for col in pred_cols:
        target_name = col.replace("predicted_", "").replace("_tier", "")
        counts = df[col].value_counts().reindex(["high", "medium", "low"], fill_value=0)
        colors = [TIER_COLORS.get(t, BRAND_COLOR) for t in counts.index]

        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.bar(counts.index, counts.values, color=colors, edgecolor="white", linewidth=0.8)

        # Add count labels on bars
        for bar, val in zip(bars, counts.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    str(val), ha="center", va="bottom", fontsize=11, fontweight="bold")

        ax.set_title(f"Predicted Tier Distribution — {target_name.upper()}", fontsize=13, pad=12)
        ax.set_xlabel("Tier", fontsize=11)
        ax.set_ylabel("Number of Campaigns", fontsize=11)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.spines[["top", "right"]].set_visible(False)
        plt.tight_layout()

        out = os.path.join(OUTPUTS_DIR, f"chart_tier_distribution_{target_name}.png")
        plt.savefig(out, dpi=150)
        plt.close()
        print(f"Saved: {out}")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 2 — Confidence Score Distribution
# ──────────────────────────────────────────────────────────────────────────────
def plot_confidence_distribution(df: pd.DataFrame):
    if "confidence_score" not in df.columns:
        print("No confidence_score column, skipping.")
        return

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(df["confidence_score"], bins=20, color=BRAND_COLOR, edgecolor="white", linewidth=0.6)
    ax.axvline(df["confidence_score"].mean(), color="#e74c3c", linestyle="--",
               linewidth=1.5, label=f"Mean: {df['confidence_score'].mean():.2f}")
    ax.set_title("Confidence Score Distribution", fontsize=13, pad=12)
    ax.set_xlabel("Confidence Score", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.legend(fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    out = os.path.join(OUTPUTS_DIR, "chart_confidence_distribution.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved: {out}")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 3 — Feature Importance per Target
# ──────────────────────────────────────────────────────────────────────────────
def plot_feature_importance():
    try:
        from modeling_related_files import get_feature_importance, TRAIN_TARGETS
    except ImportError:
        from modeling_related_files import get_feature_importance
        TRAIN_TARGETS = ["ctr", "conversion_rate", "reach_score"]

    for target in TRAIN_TARGETS:
        try:
            fi = get_feature_importance(target)
            top = fi.head(10)

            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.barh(top["feature"][::-1], top["importance"][::-1],
                           color=BRAND_COLOR, edgecolor="white")
            ax.set_title(f"Top 10 Feature Importances — {target.upper()}", fontsize=13, pad=12)
            ax.set_xlabel("Importance", fontsize=11)
            ax.spines[["top", "right"]].set_visible(False)
            plt.tight_layout()

            out = os.path.join(OUTPUTS_DIR, f"chart_feature_importance_{target}.png")
            plt.savefig(out, dpi=150)
            plt.close()
            print(f"Saved: {out}")
        except Exception as e:
            print(f"Skipping feature importance for {target}: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 4 — Segment Summary per Target
# ──────────────────────────────────────────────────────────────────────────────
def plot_segment_summary(df: pd.DataFrame):
    if "performance_segment" not in df.columns:
        print("No performance_segment column, skipping.")
        return

    counts = df["performance_segment"].value_counts()
    colors = [TIER_COLORS["high"], TIER_COLORS["medium"], TIER_COLORS["low"]][:len(counts)]

    fig, ax = plt.subplots(figsize=(7, 4))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    for t in autotexts:
        t.set_fontsize(10)
    ax.set_title("Campaign Performance Segments", fontsize=13, pad=12)
    plt.tight_layout()

    out = os.path.join(OUTPUTS_DIR, "chart_segment_summary.png")
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Saved: {out}")


# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY TABLE — per target
# ──────────────────────────────────────────────────────────────────────────────
def generate_summary_table(df: pd.DataFrame):
    pred_cols = [c for c in df.columns if c.startswith("predicted_")]
    summary_rows = []

    for col in pred_cols:
        target_name = col.replace("predicted_", "").replace("_tier", "")
        subset = df[df["target"] == target_name] if "target" in df.columns else df
        counts = subset[col].value_counts().reindex(["high", "medium", "low"], fill_value=0)
        total = counts.sum()
        avg_conf = subset["confidence_score"].mean() if "confidence_score" in subset.columns else None

        summary_rows.append({
            "target":           target_name,
            "total_predictions": total,
            "high_count":        counts["high"],
            "medium_count":      counts["medium"],
            "low_count":         counts["low"],
            "high_pct":          round(counts["high"] / total * 100, 1) if total else 0,
            "medium_pct":        round(counts["medium"] / total * 100, 1) if total else 0,
            "low_pct":           round(counts["low"] / total * 100, 1) if total else 0,
            "avg_confidence":    round(avg_conf, 4) if avg_conf is not None else None,
        })

    summary_df = pd.DataFrame(summary_rows)
    out = os.path.join(OUTPUTS_DIR, "summary_table.csv")
    summary_df.to_csv(out, index=False)
    print(f"\nSummary table saved: {out}")
    print(summary_df.to_string(index=False))
    return summary_df


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--predictions-path",
        default=os.path.join(OUTPUTS_DIR, "predictions.csv"),
        help="Path to predictions CSV produced by predict.py",
    )
    args = parser.parse_args()

    df = load_predictions(args.predictions_path)

    print("\n--- Tier Distribution Charts ---")
    plot_tier_distribution(df)

    print("\n--- Confidence Distribution Chart ---")
    plot_confidence_distribution(df)

    print("\n--- Feature Importance Charts ---")
    plot_feature_importance()

    print("\n--- Segment Summary Chart ---")
    plot_segment_summary(df)

    print("\n--- Summary Table ---")
    generate_summary_table(df)

    print("\nAll visual outputs saved to outputs/")