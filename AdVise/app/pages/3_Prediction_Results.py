import streamlit as st
from ui_components import (
    load_css,
    page_header,
    metric_card,
    recommendation_card,
    placeholder_box,
)

st.set_page_config(page_title="Prediction Results", layout="wide")
load_css()

page_header(
    "Prediction Results",
    "Ranked creative results, primary KPI, and recommendation blocks."
)

result = st.session_state.get("prediction_result")
payload = st.session_state.get("campaign_payload")

if not result:
    st.warning("No prediction result found yet. Please analyze a campaign first.")
    placeholder_box(
        "Waiting for Prediction Run",
        "After the Campaign Input page submits to /v1/predictions/preview, results will appear here."
    )
    st.stop()

best_creative = result.get("best_creative", "Creative A")
primary_kpi = result.get("primary_kpi", "Predicted CTR")
creatives = result.get("creatives", [])
tips = result.get("tips", [])

st.success(f"Best Creative: {best_creative}")

if payload:
    with st.expander("Campaign submitted for analysis", expanded=False):
        st.json(payload)

st.divider()

m1, m2, m3, m4 = st.columns(4)

top_creative = creatives[0] if creatives else {}

with m1:
    metric_card("Primary KPI", primary_kpi, "Main optimization target")

with m2:
    metric_card("Top CTR", top_creative.get("ctr", "2.8%"), "Best predicted CTR")

with m3:
    metric_card(
        "Top Conversion",
        top_creative.get("conversion_rate", "3.9%"),
        "Best predicted conversion"
    )

with m4:
    metric_card(
        "Top Engagement",
        f"{top_creative.get('engagement_score', 86)}/100",
        "Best engagement score"
    )

st.divider()

st.markdown("### Creative Ranking")

if creatives:
    cols = st.columns(len(creatives))

    for col, creative in zip(cols, creatives):
        with col:
            with st.container(border=True):
                st.markdown(f"### Rank #{creative.get('rank')}")
                st.markdown(f"**{creative.get('name')}**")
                st.metric("CTR", creative.get("ctr"))
                st.metric("Conversion", creative.get("conversion_rate"))
                st.metric("Engagement", f"{creative.get('engagement_score')}/100")
                st.info(creative.get("recommendation"))
else:
    placeholder_box(
        "Creative Ranking",
        "Rank #1–#3 creative cards will appear here after backend scoring."
    )

st.divider()

left, right = st.columns(2, gap="large")

with left:
    placeholder_box(
        "Prediction Visualization",
        "Future chart comparing CTR, conversion rate, engagement score, and reach score by creative."
    )

with right:
    st.markdown("### Recommendation Blocks")

    if tips:
        for tip in tips:
            recommendation_card(tip)
    else:
        recommendation_card("Recommendation blocks will appear here after model scoring.")

st.divider()

st.markdown("### PM Endpoint Mapping")

with st.container(border=True):
    st.write("This screen is prepared for:")
    st.code(
        """
POST /v1/predictions/preview
GET  /v1/prediction-runs/{run_id}
        """,
        language="text"
    )