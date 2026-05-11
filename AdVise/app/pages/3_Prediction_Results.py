import base64
import os
import sys
from io import BytesIO

import pandas as pd
import streamlit as st

_sys_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _sys_root not in sys.path:
    sys.path.insert(0, _sys_root)

from ui_components import metric_card, page_header, recommendation_card

st.set_page_config(page_title="Prediction Results", layout="wide")

page_header(
    "Prediction Results",
    "Live preview for your campaign: one KPI from your intent (see docs/api/v1-endpoints.md).",
)


def ds_outputs_root() -> str:
    env = os.environ.get("ADVISE_DS_OUTPUTS", "").strip()
    if env:
        return env
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../ds/outputs")
    )


DS_OUTPUTS = ds_outputs_root()
SUMMARY_PATH = os.path.join(DS_OUTPUTS, "summary_table.csv")
PRED_PATH = os.path.join(DS_OUTPUTS, "predictions.csv")


def chart_path(name: str) -> str:
    return os.path.join(DS_OUTPUTS, name)


@st.cache_data
def load_summary(path: str):
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


summary = load_summary(SUMMARY_PATH)
result = st.session_state.get("prediction_result")
payload = st.session_state.get("campaign_payload")

DOCS_INTENT = (
    "Docs: **docs/api/v1-endpoints.md** — *Single outcome per preview*; mapping in "
    "**`AdVise/api/campaign_intent.py`** (`INTENT_TO_TARGET_METRIC`). "
    "One **`campaign_intent`** → one **`target_metric`** per request."
)

# ──────────────────────────────────────────────────────────────────────────────
# 1) YOUR INPUT — POST /v1/predictions/preview (single KPI for chosen intent)
# ─────────────────────────────────────────────────────────────────────────────-
st.subheader("Your campaign preview")
st.caption(DOCS_INTENT)

if isinstance(result, dict) and "recommendations" in result:
    target_metric = result.get("target_metric", "")
    predicted_tier = result.get("predicted_tier")
    conf = result.get("prediction_confidence")
    model_version = result.get("model_version", "")
    recommendations = result.get("recommendations") or []
    creative_features = result.get("creative_features")
    snapshot = result.get("model_feature_snapshot")

    tier_s = predicted_tier if predicted_tier is not None else "–"
    st.success(
        f"**One prediction for your intent:** `{result.get('campaign_intent')}` → "
        f"**`{target_metric}`** — predicted tier **{tier_s}** (`{model_version}`)"
    )

    m1, m2, m3, m4 = st.columns(4, gap="large")
    with m1:
        metric_card(
            "Target metric (this run only)",
            str(target_metric),
            result.get("target_label") or "",
        )
    with m2:
        metric_card("Predicted tier", str(tier_s), "Single classifier for resolved metric.")
    with m3:
        c_s = f"{conf:.2f}" if isinstance(conf, (int, float)) else "–"
        metric_card("Confidence", c_s, "Model certainty when inference runs.")
    with m4:
        metric_card("Model version", str(model_version), "ds-* = joblib classifier.")

    st.markdown("##### On-demand visuals (this submission)")
    viz_l, viz_r = st.columns([1, 1], gap="large")
    with viz_l:
        if isinstance(payload, dict) and payload.get("creative_image_base64"):
            try:
                raw = base64.standard_b64decode(payload["creative_image_base64"])
                st.image(BytesIO(raw), caption="First creative (sent to API for extraction)")
            except Exception:  # noqa: BLE001
                st.caption("Could not decode creative image from session payload.")
        else:
            st.info("No image in this run; upload an image on Campaign Input to preview it here.")

        pred_l = (predicted_tier or "").strip().lower()
        tiers = ["low", "medium", "high"]
        conf_f = float(conf) if isinstance(conf, (int, float)) else 0.0
        tier_df = pd.DataFrame(
            {
                "tier": tiers,
                "weight": [conf_f if t == pred_l else 0.0 for t in tiers],
            }
        )
        st.caption("Tier emphasis (height = model confidence on the predicted tier)")
        st.bar_chart(tier_df.set_index("tier"), use_container_width=True)

    with viz_r:
        rec_rows = [
            {"rank": int(r["rank"]), "score": float(r["score"])}
            for r in recommendations
            if isinstance(r, dict) and r.get("rank") is not None and r.get("score") is not None
        ]
        if rec_rows:
            st.caption(f"Recommendation scores (all rows use **{target_metric}** only)")
            rdf = pd.DataFrame(rec_rows).sort_values("rank")
            st.bar_chart(rdf.set_index("rank")[["score"]], use_container_width=True)
        else:
            st.info("No scored recommendation rows to chart.")

    if payload:
        with st.expander("Submitted JSON payload", expanded=False):
            st.json(payload)

    if creative_features:
        with st.expander("Extracted creative features (API / image)", expanded=True):
            st.json(creative_features)

    if snapshot:
        with st.expander("Feature snapshot sent to tier model", expanded=False):
            st.json(snapshot)

    st.markdown("##### Recommendations")
    for rec in recommendations:
        if not isinstance(rec, dict):
            continue
        rk = rec.get("rank", "?")
        kpi = rec.get("primary_kpi", target_metric)
        score = rec.get("score")
        hint = rec.get("hint", "")
        sc = f"{float(score):.2f}" if isinstance(score, (int, float)) else str(score)
        recommendation_card(f"**#{rk}** · {kpi} (score {sc})\n\n{hint}")

elif isinstance(result, dict) and ("creatives" in result or "tips" in result):
    st.warning(
        "Showing **fallback placeholder** creatives (legacy shape). "
        "Use Campaign Input → Analyze with the API reachable for live `/v1/predictions/preview` JSON."
    )
    creatives = result.get("creatives", [])
    for c in creatives[:3]:
        if isinstance(c, dict):
            st.write(f"Rank {c.get('rank')} — {c.get('name')}")
    tips = result.get("tips") or []
    for t in tips:
        recommendation_card(t)

else:
    st.info(
        "No preview yet. Go to **Campaign Input**, submit **Analyze Campaign**, then return here. "
        "The API returns **one** `target_metric` for your **campaign_intent** "
        "(see **docs/api/v1-endpoints.md**)."
    )

# ──────────────────────────────────────────────────────────────────────────────
# 2) OFFLINE BATCH — all three metrics on full training_dataset (not per-intent)
# ─────────────────────────────────────────────────────────────────────────────-
with st.expander(
    "Dataset-wide offline reports (pre-generated `predict.py` / `generate_visuals.py`)",
    expanded=False,
):
    st.caption(
        "These artifacts score the **entire** training table with **CTR, conversion_rate, and "
        "reach_score** models separately. They do **not** filter to your selected intent. "
        "For your campaign, use **Your campaign preview** above."
    )

    if summary is not None:
        cols = st.columns(len(summary))
        for i, row in summary.iterrows():
            with cols[i]:
                st.metric(
                    label=f"{str(row['target']).upper()} — avg confidence",
                    value=f"{float(row['avg_confidence']):.2%}",
                )
                st.caption(
                    f"High: {row['high_pct']}% | Mid: {row['medium_pct']}% | Low: {row['low_pct']}%"
                )
                st.caption(f"Total predictions: {int(row['total_predictions']):,}")
    else:
        st.warning(
            f"**summary_table.csv** not found under `{DS_OUTPUTS}`. "
            "Run the batch-visuals profile or host-side `predict.py` + `generate_visuals.py`."
        )

    st.markdown("###### Batch: tier distributions (all targets)")

    CHART_KEYS = (
        ("CTR", "chart_tier_distribution_ctr.png"),
        ("Conversion rate", "chart_tier_distribution_conversion_rate.png"),
        ("Reach score", "chart_tier_distribution_reach_score.png"),
    )

    bc1, bc2, bc3 = st.columns(3)
    for col, (label, fname) in zip((bc1, bc2, bc3), CHART_KEYS):
        path = chart_path(fname)
        with col:
            st.caption(label)
            if os.path.exists(path):
                st.image(path, use_container_width=True)
            else:
                st.info("Chart not generated yet.")

    st.markdown("###### Batch: confidence & segments")
    c1, c2 = st.columns(2)
    with c1:
        p = chart_path("chart_confidence_distribution.png")
        if os.path.exists(p):
            st.image(p, use_container_width=True)
        else:
            st.info("Confidence chart not found.")
    with c2:
        p = chart_path("chart_segment_summary.png")
        if os.path.exists(p):
            st.image(p, use_container_width=True)
        else:
            st.info("Segment chart not found.")

    st.markdown("###### Batch: feature importances (all targets)")
    fi_specs = (
        ("CTR", "chart_feature_importance_ctr.png"),
        ("Conversion rate", "chart_feature_importance_conversion_rate.png"),
        ("Reach score", "chart_feature_importance_reach_score.png"),
    )
    fc1, fc2, fc3 = st.columns(3)
    for col, (lab, fname) in zip((fc1, fc2, fc3), fi_specs):
        path = chart_path(fname)
        with col:
            st.caption(lab)
            if os.path.exists(path):
                st.image(path, use_container_width=True)
            else:
                st.info("Chart not found.")

    st.markdown("###### Batch: predictions sample CSV")
    if os.path.exists(PRED_PATH):
        df = pd.read_csv(PRED_PATH, low_memory=False, nrows=500)
        pred_cols = [
            c
            for c in df.columns
            if c.startswith("predicted_")
            or c in ("confidence_score", "performance_segment", "target")
        ]
        st.dataframe(df[pred_cols].head(50), use_container_width=True)
    else:
        st.info("`predictions.csv` not found.")

st.divider()
st.markdown("###### HTTP reference")
with st.container(border=True):
    st.code(
        """
POST /v1/predictions/preview   # One target_metric per campaign_intent (see campaign_intent.py)
GET  /v1/prediction-runs/{run_id}
""",
        language="text",
    )
