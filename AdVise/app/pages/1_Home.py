import os
import pandas as pd
import streamlit as st
from ui_components import page_header, metric_card, placeholder_box, inject_global_css

st.set_page_config(page_title="AdVise — Home", layout="wide")
inject_global_css()

# ── DS outputs path (mirrors 3_Prediction_Results.py) ────────────────────────
def ds_outputs_root() -> str:
    env = os.environ.get("ADVISE_DS_OUTPUTS", "").strip()
    if env:
        return env
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../ds/outputs")
    )

DS_OUTPUTS   = ds_outputs_root()
SUMMARY_PATH = os.path.join(DS_OUTPUTS, "summary_table.csv")
PRED_PATH    = os.path.join(DS_OUTPUTS, "predictions.csv")


@st.cache_data
def load_summary(path: str):
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


@st.cache_data
def load_predictions_sample(path: str, n: int = 5000):
    if os.path.exists(path):
        return pd.read_csv(path, low_memory=False, nrows=n)
    return None


summary = load_summary(SUMMARY_PATH)
pred_df  = load_predictions_sample(PRED_PATH)

page_header(
    "AdVise Dashboard",
    "Business overview for campaign planning, creative testing, and prediction results.",
)

# ── KPI row — pulled from real summary_table.csv when available ───────────────
m1, m2, m3, m4 = st.columns(4, gap="large")

if summary is not None:
    # Build per-target lookup
    summ = summary.set_index("target")

    def _avg_conf(target):
        try:
            return f"{float(summ.loc[target, 'avg_confidence']):.1%}"
        except Exception:
            return "–"

    def _high_pct(target):
        try:
            return f"{float(summ.loc[target, 'high_pct']):.1f}%"
        except Exception:
            return "–"

    def _total(target):
        try:
            return f"{int(summ.loc[target, 'total_predictions']):,}"
        except Exception:
            return "–"

    with m1:
        metric_card("Total predictions", _total("ctr"), "Across all batch targets")
    with m2:
        metric_card("Avg confidence — CTR", _avg_conf("ctr"), "Mean model certainty on CTR tier")
    with m3:
        metric_card("High tier — Conversion", _high_pct("conversion_rate"), "% campaigns predicted high")
    with m4:
        metric_card("High tier — Reach", _high_pct("reach_score"), "% campaigns predicted high reach")

else:
    # Static placeholders until DS outputs are available
    with m1:
        metric_card("Campaigns", "24", "Total campaigns tracked")
    with m2:
        metric_card("Avg. CTR", "2.6%", "Estimated click-through rate")
    with m3:
        metric_card("Conversion", "3.8%", "Predicted conversion rate")
    with m4:
        metric_card("Success Score", "81/100", "Overall campaign quality")

st.divider()

# ── Feature cards ─────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    with st.container(border=True):
        st.subheader("🖼 Creative Upload")
        st.write("Upload campaign images or videos for pre-launch evaluation.")

with col2:
    with st.container(border=True):
        st.subheader("⚙️ Campaign Setup")
        st.write("Enter budget, platform, audience, CTA type, duration, and campaign objective.")

with col3:
    with st.container(border=True):
        st.subheader("📈 Prediction Results")
        st.write("Review predicted CTR, conversion rate, reach score, and ranked recommendations.")

st.divider()

# ── Tabs: Data / Charts / Model Results ───────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋  Campaign Table", "📊  Batch Charts", "🤖  Model Summary"])

# ── Tab 1: sample predictions table ─────────────────────────────────────────
with tab1:
    if pred_df is not None:
        display_cols = [
            c for c in pred_df.columns
            if c in (
                "platform", "campaign_intent", "product_type", "audience_temperature",
                "budget", "duration_days", "target",
                "predicted_ctr_tier", "predicted_conversion_rate_tier",
                "predicted_reach_score_tier", "confidence_score", "performance_segment",
            )
        ]
        st.caption(f"Showing 50 of {len(pred_df):,} sampled rows from predictions.csv")
        st.dataframe(pred_df[display_cols].head(50), use_container_width=True)

        # Quick filter row
        st.markdown("**Filter**")
        fc1, fc2, fc3 = st.columns(3)
        platforms = ["All"] + sorted(pred_df["platform"].dropna().unique().tolist()) if "platform" in pred_df.columns else ["All"]
        intents   = ["All"] + sorted(pred_df["campaign_intent"].dropna().unique().tolist()) if "campaign_intent" in pred_df.columns else ["All"]
        segments  = ["All"] + sorted(pred_df["performance_segment"].dropna().unique().tolist()) if "performance_segment" in pred_df.columns else ["All"]

        with fc1:
            sel_platform = st.selectbox("Platform", platforms, key="home_platform")
        with fc2:
            sel_intent = st.selectbox("Intent", intents, key="home_intent")
        with fc3:
            sel_segment = st.selectbox("Segment", segments, key="home_segment")

        filtered = pred_df.copy()
        if sel_platform != "All" and "platform" in filtered.columns:
            filtered = filtered[filtered["platform"] == sel_platform]
        if sel_intent != "All" and "campaign_intent" in filtered.columns:
            filtered = filtered[filtered["campaign_intent"] == sel_intent]
        if sel_segment != "All" and "performance_segment" in filtered.columns:
            filtered = filtered[filtered["performance_segment"] == sel_segment]

        st.caption(f"{len(filtered):,} rows after filter")
        if display_cols:
            st.dataframe(filtered[display_cols].head(50), use_container_width=True)
    else:
        st.info("predictions.csv not found. Run `predict.py` then `generate_visuals.py`.")
        st.dataframe(
            {
                "Campaign": ["Campaign A", "Campaign B", "Campaign C"],
                "Platform": ["Instagram", "TikTok", "Facebook"],
                "Status":   ["Draft", "Ready", "Tested"],
                "Predicted CTR": ["2.6%", "3.1%", "2.2%"],
            },
            use_container_width=True,
        )

# ── Tab 2: DS batch charts ────────────────────────────────────────────────────
with tab2:
    def _chart(fname):
        p = os.path.join(DS_OUTPUTS, fname)
        if os.path.exists(p):
            st.image(p, use_container_width=True)
        else:
            st.info(f"`{fname}` not generated yet.")

    st.markdown("##### Tier Distributions")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.caption("CTR")
        _chart("chart_tier_distribution_ctr.png")
    with c2:
        st.caption("Conversion Rate")
        _chart("chart_tier_distribution_conversion_rate.png")
    with c3:
        st.caption("Reach Score")
        _chart("chart_tier_distribution_reach_score.png")

    st.markdown("##### Confidence & Segments")
    c1, c2 = st.columns(2)
    with c1:
        _chart("chart_confidence_distribution.png")
    with c2:
        _chart("chart_segment_summary.png")

    st.markdown("##### Feature Importances")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.caption("CTR")
        _chart("chart_feature_importance_ctr.png")
    with c2:
        st.caption("Conversion Rate")
        _chart("chart_feature_importance_conversion_rate.png")
    with c3:
        st.caption("Reach Score")
        _chart("chart_feature_importance_reach_score.png")

# ── Tab 3: Model summary table ────────────────────────────────────────────────
with tab3:
    if summary is not None:
        st.caption("Summary generated by `predict.py` + `generate_visuals.py` on the full training dataset.")
        # Display as a styled dataframe
        display_summary = summary.copy()
        if "avg_confidence" in display_summary.columns:
            display_summary["avg_confidence"] = display_summary["avg_confidence"].map(lambda x: f"{x:.1%}")
        for col in ("high_pct", "medium_pct", "low_pct"):
            if col in display_summary.columns:
                display_summary[col] = display_summary[col].map(lambda x: f"{x:.1f}%")

        st.dataframe(display_summary, use_container_width=True)

        # Bar chart: avg confidence per target
        chart_data = summary.set_index("target")[["avg_confidence"]]
        st.bar_chart(chart_data, use_container_width=True)
    else:
        with st.container(border=True):
            st.subheader("Model Output")
            st.info(
                "No model summary found. Run `python ds/predict.py` followed by "
                "`python ds/generate_visuals.py` to populate this section."
            )