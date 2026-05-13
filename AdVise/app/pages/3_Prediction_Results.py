import base64
import os
import sys
from io import BytesIO

import pandas as pd
import streamlit as st

_sys_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _sys_root not in sys.path:
    sys.path.insert(0, _sys_root)

from ui_components import (
    inject_global_css,
    metric_card,
    page_header,
    recommendation_card,
    tier_badge,
)

st.set_page_config(page_title="Prediction Results — AdVise", layout="wide")
inject_global_css()

page_header(
    "Prediction Results",
    "Live preview for your campaign — one KPI resolved from your selected intent.",
)


# ── Paths ─────────────────────────────────────────────────────────────────────
def ds_outputs_root() -> str:
    env = os.environ.get("ADVISE_DS_OUTPUTS", "").strip()
    if env:
        return env
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ds/outputs"))


DS_OUTPUTS   = ds_outputs_root()
SUMMARY_PATH = os.path.join(DS_OUTPUTS, "summary_table.csv")
PRED_PATH    = os.path.join(DS_OUTPUTS, "predictions.csv")


def chart_path(name: str) -> str:
    return os.path.join(DS_OUTPUTS, name)


@st.cache_data
def load_summary(path: str):
    return pd.read_csv(path) if os.path.exists(path) else None


summary = load_summary(SUMMARY_PATH)
result  = st.session_state.get("prediction_result")
payload = st.session_state.get("campaign_payload")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Live prediction (from POST /v1/predictions/preview)
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("Your Campaign Preview")

if isinstance(result, dict) and "recommendations" in result:
    target_metric   = result.get("target_metric", "")
    predicted_tier  = result.get("predicted_tier")
    conf            = result.get("prediction_confidence")
    model_version   = result.get("model_version", "")
    recommendations = result.get("recommendations") or []
    creative_features = result.get("creative_features")
    snapshot        = result.get("model_feature_snapshot")

    tier_s  = predicted_tier if predicted_tier is not None else "–"
    badge_html = tier_badge(tier_s)

    st.markdown(
        f"**Intent:** `{result.get('campaign_intent')}` → "
        f"**metric:** `{target_metric}` → predicted tier: {badge_html} "
        f"<span style='color:#8b8fa8;font-size:0.8rem'>({model_version})</span>",
        unsafe_allow_html=True,
    )

    # ── KPI row ──────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4, gap="large")
    with m1:
        metric_card("Target metric", str(target_metric), "Metric resolved from your campaign intent.")
    with m2:
        metric_card("Predicted tier", str(tier_s), "Classifier output for resolved metric.")
    with m3:
        c_s = f"{conf:.2f}" if isinstance(conf, (int, float)) else "–"
        metric_card("Confidence", c_s, "Model certainty at inference time.")
    with m4:
        metric_card("Model version", str(model_version), "ds-* = joblib classifier.")

    st.divider()

    # ── On-demand visuals ────────────────────────────────────────────────────
    st.markdown("##### On-demand visuals (this submission)")
    viz_l, viz_r = st.columns([1, 1], gap="large")

    with viz_l:
        # Creative image
        if isinstance(payload, dict) and payload.get("creative_image_base64"):
            try:
                raw = base64.standard_b64decode(payload["creative_image_base64"])
                st.image(BytesIO(raw), caption="Submitted creative (sent to API)")
            except Exception:
                st.caption("Could not decode creative image from session.")
        else:
            st.info("No image in this run — upload an image on Campaign Input to preview it here.")

        # Tier confidence bar
        pred_l  = (predicted_tier or "").strip().lower()
        tiers   = ["low", "medium", "high"]
        conf_f  = float(conf) if isinstance(conf, (int, float)) else 0.0
        tier_df = pd.DataFrame(
            {
                "tier":   tiers,
                "weight": [conf_f if t == pred_l else 0.0 for t in tiers],
            }
        )
        st.caption("Tier confidence emphasis (height = model confidence on predicted tier)")
        st.bar_chart(tier_df.set_index("tier"), use_container_width=True)

    with viz_r:
        # Recommendation scores
        rec_rows = [
            {"rank": int(r["rank"]), "score": float(r["score"])}
            for r in recommendations
            if isinstance(r, dict)
            and r.get("rank") is not None
            and r.get("score") is not None
        ]
        if rec_rows:
            rdf = pd.DataFrame(rec_rows).sort_values("rank")
            st.caption(f"Recommendation scores (all use **{target_metric}**)")
            st.bar_chart(rdf.set_index("rank")[["score"]], use_container_width=True)
        else:
            st.info("No scored recommendation rows to chart.")

    # ── Expandable detail ────────────────────────────────────────────────────
    if payload:
        with st.expander("Submitted JSON payload", expanded=False):
            st.json(payload)

    if creative_features:
        with st.expander("Extracted creative features (API / image)", expanded=True):
            st.json(creative_features)

    if snapshot:
        with st.expander("Feature snapshot sent to tier model", expanded=False):
            st.json(snapshot)

    # ── Recommendations list ─────────────────────────────────────────────────
    st.divider()
    st.markdown("##### Recommendations")
    for rec in recommendations:
        if not isinstance(rec, dict):
            continue
        rk    = rec.get("rank", "?")
        kpi   = rec.get("primary_kpi", target_metric)
        score = rec.get("score")
        hint  = rec.get("hint", "")
        sc    = f"{float(score):.2f}" if isinstance(score, (int, float)) else str(score)
        recommendation_card(hint, rank=rk, score=float(score) if isinstance(score, (int, float)) else None)

# ── Fallback: old placeholder shape ──────────────────────────────────────────
elif isinstance(result, dict) and ("creatives" in result or "tips" in result):
    st.warning(
        "Showing **fallback placeholder** results. "
        "Submit **Analyze Campaign** with the backend reachable for live predictions."
    )

    creatives = result.get("creatives", [])
    if creatives:
        st.markdown("##### Creative Rankings")
        for c in creatives:
            if not isinstance(c, dict):
                continue
            with st.container(border=True):
                cols = st.columns([0.1, 0.9])
                with cols[0]:
                    st.markdown(f"### #{c.get('rank')}")
                with cols[1]:
                    st.markdown(f"**{c.get('name')}**")
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("CTR", c.get("ctr", "–"))
                    col_b.metric("Conversion", c.get("conversion_rate", "–"))
                    col_c.metric("Engagement", c.get("engagement_score", "–"))
                    st.caption(c.get("recommendation", ""))

    tips = result.get("tips") or []
    if tips:
        st.markdown("##### Tips")
        for t in tips:
            recommendation_card(t)

# ── No result yet ─────────────────────────────────────────────────────────────
else:
    st.info(
        "No preview yet. Go to **Campaign Input**, submit **Analyze Campaign**, "
        "then return here. The API returns **one** `target_metric` per `campaign_intent`."
    )

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Offline batch reports (DS outputs)
# ══════════════════════════════════════════════════════════════════════════════
st.divider()

with st.expander(
    "📊  Dataset-wide offline reports (pre-generated by `predict.py` / `generate_visuals.py`)",
    expanded=False,
):
    st.caption(
        "These artifacts score the **entire** training table across "
        "**CTR, conversion_rate, and reach_score** — not filtered to your intent. "
        "Use **Your Campaign Preview** above for your specific prediction."
    )

    # ── Summary metrics ───────────────────────────────────────────────────────
    if summary is not None:
        cols = st.columns(len(summary))
        for i, row in summary.iterrows():
            with cols[i]:
                st.metric(
                    label=f"{str(row['target']).upper()} — avg confidence",
                    value=f"{float(row['avg_confidence']):.1%}",
                )
                st.caption(
                    f"High: {row['high_pct']}% · Mid: {row['medium_pct']}% · Low: {row['low_pct']}%"
                )
                st.caption(f"Total: {int(row['total_predictions']):,}")
    else:
        st.warning(
            f"`summary_table.csv` not found under `{DS_OUTPUTS}`. "
            "Run `predict.py` then `generate_visuals.py`."
        )

    def _chart(fname: str, caption: str | None = None):
        p = chart_path(fname)
        if caption:
            st.caption(caption)
        if os.path.exists(p):
            st.image(p, use_container_width=True)
        else:
            st.info(f"`{fname}` not generated yet.")

    # ── Tier distributions ────────────────────────────────────────────────────
    st.markdown("###### Tier distributions — all targets")
    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        _chart("chart_tier_distribution_ctr.png", "CTR")
    with bc2:
        _chart("chart_tier_distribution_conversion_rate.png", "Conversion Rate")
    with bc3:
        _chart("chart_tier_distribution_reach_score.png", "Reach Score")

    # ── Confidence & segments ─────────────────────────────────────────────────
    st.markdown("###### Confidence distribution & performance segments")
    c1, c2 = st.columns(2)
    with c1:
        _chart("chart_confidence_distribution.png")
    with c2:
        _chart("chart_segment_summary.png")

    # ── Feature importances ───────────────────────────────────────────────────
    st.markdown("###### Feature importances — all targets")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        _chart("chart_feature_importance_ctr.png", "CTR")
    with fc2:
        _chart("chart_feature_importance_conversion_rate.png", "Conversion Rate")
    with fc3:
        _chart("chart_feature_importance_reach_score.png", "Reach Score")

    # ── Predictions CSV sample ────────────────────────────────────────────────
    st.markdown("###### Batch predictions sample")
    if os.path.exists(PRED_PATH):
        df = pd.read_csv(PRED_PATH, low_memory=False, nrows=500)
        pred_cols = [
            c for c in df.columns
            if c.startswith("predicted_")
            or c in ("confidence_score", "performance_segment", "target")
        ]
        st.dataframe(df[pred_cols].head(50), use_container_width=True)
    else:
        st.info("`predictions.csv` not found.")

# ── HTTP reference ────────────────────────────────────────────────────────────
st.divider()
st.markdown("###### HTTP reference")
with st.container(border=True):
    st.code(
        "POST /v1/predictions/preview        # one target_metric per campaign_intent\n"
        "GET  /v1/prediction-runs/{run_id}   # retrieve a past run",
        language="text",
    )