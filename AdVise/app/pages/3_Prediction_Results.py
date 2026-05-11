import streamlit as st
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(__file__).replace("pages", ""))
from ui_components import page_header, metric_card

st.set_page_config(page_title="Prediction Results", layout="wide")

page_header(
    "Prediction Results",
    "Prepared page for model result display, creative rankings, tables, filters, and charts."
)

# ── paths ──────────────────────────────────────────────────────────────────────
DS_OUTPUTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ds/outputs"))

SUMMARY_PATH = os.path.join(DS_OUTPUTS, "summary_table.csv")
CHARTS = {
    "ctr":             os.path.join(DS_OUTPUTS, "chart_tier_distribution_ctr.png"),
    "conversion_rate": os.path.join(DS_OUTPUTS, "chart_tier_distribution_conversion_rate.png"),
    "reach_score":     os.path.join(DS_OUTPUTS, "chart_tier_distribution_reach_score.png"),
    "confidence":      os.path.join(DS_OUTPUTS, "chart_confidence_distribution.png"),
    "segment":         os.path.join(DS_OUTPUTS, "chart_segment_summary.png"),
    "fi_ctr":          os.path.join(DS_OUTPUTS, "chart_feature_importance_ctr.png"),
    "fi_conversion":   os.path.join(DS_OUTPUTS, "chart_feature_importance_conversion_rate.png"),
    "fi_reach":        os.path.join(DS_OUTPUTS, "chart_feature_importance_reach_score.png"),
}

# ── load summary ───────────────────────────────────────────────────────────────
@st.cache_data
def load_summary():
    if os.path.exists(SUMMARY_PATH):
        return pd.read_csv(SUMMARY_PATH)
    return None

summary = load_summary()

# ── SECTION 1: KPI metrics from summary table ─────────────────────────────────
st.subheader("Model Summary")

if summary is not None:
    cols = st.columns(len(summary))
    for i, row in summary.iterrows():
        with cols[i]:
            st.metric(label=f"{row['target'].upper()} — Avg Confidence",
                      value=f"{float(row['avg_confidence']):.2%}")
            st.caption(f"High: {row['high_pct']}% | Mid: {row['medium_pct']}% | Low: {row['low_pct']}%")
            st.caption(f"Total predictions: {int(row['total_predictions']):,}")
else:
    st.warning("Summary table not found. Run predict.py and generate_visuals.py first.")

    if creative_features:
        with st.expander("Extracted creative features (image)", expanded=False):
            st.json(creative_features)

# ── SECTION 2: Tier distribution charts ───────────────────────────────────────
st.subheader("Predicted Tier Distributions")

c1, c2, c3 = st.columns(3)
for col, key, label in [
    (c1, "ctr",             "CTR"),
    (c2, "conversion_rate", "Conversion Rate"),
    (c3, "reach_score",     "Reach Score"),
]:
    with col:
        st.caption(label)
        if os.path.exists(CHARTS[key]):
            st.image(CHARTS[key], use_container_width=True)
        else:
            st.info(f"Chart not found: {key}")

    st.divider()
    st.subheader("Model Result Display")

# ── SECTION 3: Confidence + Segment ───────────────────────────────────────────
st.subheader("Confidence & Segments")

c1, c2 = st.columns(2)
with c1:
    if os.path.exists(CHARTS["confidence"]):
        st.image(CHARTS["confidence"], use_container_width=True)
with c2:
    if os.path.exists(CHARTS["segment"]):
        st.image(CHARTS["segment"], use_container_width=True)

st.divider()

# ── SECTION 4: Feature importance ─────────────────────────────────────────────
st.subheader("Feature Importances")

c1, c2, c3 = st.columns(3)
for col, key, label in [
    (c1, "fi_ctr",        "CTR"),
    (c2, "fi_conversion", "Conversion Rate"),
    (c3, "fi_reach",      "Reach Score"),
]:
    with col:
        st.caption(label)
        if os.path.exists(CHARTS[key]):
            st.image(CHARTS[key], use_container_width=True)
        else:
            st.info(f"Chart not found: {key}")

st.divider()

# ── SECTION 5: Raw predictions table ──────────────────────────────────────────
st.subheader("Predictions Data Sample")

pred_path = os.path.join(DS_OUTPUTS, "predictions.csv")
if os.path.exists(pred_path):
    df = pd.read_csv(pred_path, low_memory=False, nrows=500)
    pred_cols = [c for c in df.columns if c.startswith("predicted_") or
                 c in ["confidence_score", "performance_segment", "target"]]
    st.dataframe(df[pred_cols].head(50), use_container_width=True)
else:
    st.info("predictions.csv not found. Run predict.py first.")
