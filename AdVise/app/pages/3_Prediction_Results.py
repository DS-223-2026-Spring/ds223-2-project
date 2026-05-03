import streamlit as st
from ui_components import page_header, metric_card, recommendation_card, placeholder_box

st.set_page_config(page_title="Prediction Results", layout="wide")

page_header(
    "Prediction Results",
    "Prepared page for model result display, creative rankings, tables, filters, and charts."
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

top_creative = creatives[0] if creatives else {}

st.success(f"Best Creative: {best_creative}")

if payload:
    with st.expander("Campaign Submitted for Analysis", expanded=False):
        st.json(payload)

st.divider()

st.subheader("Model Result Display")

m1, m2, m3, m4 = st.columns(4, gap="large")

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

st.subheader("Creative Ranking Cards")

if creatives:
    cols = st.columns(len(creatives), gap="large")

    for col, creative in zip(cols, creatives):
        with col:
            with st.container(border=True):
                st.markdown(f"### Rank #{creative.get('rank')}")
                st.write(f"**Creative:** {creative.get('name')}")
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

st.subheader("Prepared Filters, Tables, and Charts")

filter_tab, table_tab, chart_tab, model_tab = st.tabs(
    ["Filters", "Prediction Table", "Charts", "Model Output"]
)

with filter_tab:
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        selected_rank = st.selectbox("Filter by Rank", ["All", "1", "2", "3"])

    with col2:
        selected_metric = st.selectbox(
            "Filter by Metric",
            ["CTR", "Conversion Rate", "Engagement Score"]
        )

    with col3:
        selected_creative = st.selectbox(
            "Filter by Creative",
            ["All"] + [creative.get("name") for creative in creatives]
        )

    st.info("These filters are prepared for future interactive results exploration.")

with table_tab:
    if creatives:
        st.dataframe(creatives, use_container_width=True)
    else:
        st.info("Prediction table will appear after model results are available.")

with chart_tab:
    if creatives:
        chart_data = {
            creative.get("name", "Creative"): creative.get("engagement_score", 0)
            for creative in creatives
        }

        st.bar_chart(chart_data)
        st.caption("Current placeholder chart shows engagement score by creative.")
    else:
        st.info("Charts will appear after prediction results are available.")

with model_tab:
    with st.container(border=True):
        st.subheader("Final Model Output Area")
        st.write("Primary KPI:", primary_kpi)
        st.write("Best Creative:", best_creative)
        st.write("Expected source: POST /v1/predictions/preview")
        st.info("Full backend model output will be displayed here after API integration.")

st.divider()

left, right = st.columns(2, gap="large")

with left:
    placeholder_box(
        "Future Visualization Area",
        "This section is reserved for CTR, conversion, engagement, and reach comparison charts."
    )

with right:
    st.subheader("Recommendation Blocks")

    if tips:
        for tip in tips:
            recommendation_card(tip)
    else:
        recommendation_card("Recommendation blocks will appear here after model scoring.")

st.divider()

st.subheader("PM Endpoint Mapping")

with st.container(border=True):
    st.code(
        """
POST /v1/predictions/preview
GET  /v1/prediction-runs/{run_id}
        """,
        language="text"
    )