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

is_api_shape = isinstance(result, dict) and "recommendations" in result

if is_api_shape:
    target_metric = result.get("target_metric", "ctr")
    target_label = result.get("target_label") or ""
    predicted_tier = result.get("predicted_tier")
    conf = result.get("prediction_confidence")
    model_version = result.get("model_version", "")
    recommendations = result.get("recommendations") or []
    creative_features = result.get("creative_features")
    model_feature_snapshot = result.get("model_feature_snapshot")

    tier_display = predicted_tier if predicted_tier is not None else "—"
    st.success(f"Predicted tier: **{tier_display}** (target: `{target_metric}`)")

    if payload:
        with st.expander("Campaign Submitted for Analysis", expanded=False):
            st.json(payload)

    if creative_features:
        with st.expander("Extracted creative features (image)", expanded=False):
            st.json(creative_features)

    if model_feature_snapshot:
        with st.expander("Feature row sent to tier model", expanded=False):
            st.json(model_feature_snapshot)

    st.divider()
    st.subheader("Model Result Display")

    m1, m2, m3, m4 = st.columns(4, gap="large")

    with m1:
        metric_card("Target metric", str(target_metric), target_label or "Resolved from campaign intent")

    with m2:
        metric_card("Predicted tier", str(tier_display), "Tier label from classifier or placeholder")

    with m3:
        conf_s = f"{conf:.2f}" if isinstance(conf, (int, float)) else "—"
        metric_card("Confidence", conf_s, "Model confidence when a joblib classifier is loaded")

    with m4:
        metric_card("Model version", str(model_version), "Artifact label or intent-mapping version")

    st.divider()
    st.subheader("Recommendations")

    if recommendations:
        for rec in recommendations:
            if not isinstance(rec, dict):
                continue
            rank = rec.get("rank", "?")
            kpi = rec.get("primary_kpi", target_metric)
            score = rec.get("score")
            hint = rec.get("hint", "")
            score_s = f"{float(score):.2f}" if isinstance(score, (int, float)) else str(score)
            recommendation_card(f"**#{rank}** · {kpi} (score {score_s})\n\n{hint}")
    else:
        placeholder_box(
            "Recommendations",
            "The API returned no recommendation rows for this run.",
        )

    st.divider()
    st.subheader("Ranking overview")

    rec_rows = [r for r in recommendations if isinstance(r, dict)]
    if rec_rows:
        cols = st.columns(min(len(rec_rows), 3), gap="large")
        for col, rec in zip(cols, rec_rows[:3]):
            with col:
                with st.container(border=True):
                    st.markdown(f"### Rank #{rec.get('rank')}")
                    st.metric("Score", f"{rec.get('score', 0):.2f}")
                    st.caption(rec.get("primary_kpi", target_metric))
                    st.info(rec.get("hint", ""))
    else:
        placeholder_box(
            "Creative Ranking",
            "No ranked rows returned for this preview.",
        )

    st.divider()
    st.subheader("Prepared Filters, Tables, and Charts")

    filter_tab, table_tab, chart_tab, model_tab = st.tabs(
        ["Filters", "Prediction Table", "Charts", "Model Output"]
    )

    with filter_tab:
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            st.selectbox(
                "Filter by Rank",
                ["All"] + [str(r.get("rank")) for r in rec_rows if r.get("rank") is not None],
                key="api_filter_rank",
            )
        with col2:
            st.selectbox(
                "Filter by Metric",
                ["All", str(target_metric).upper()],
                key="api_filter_metric",
            )
        with col3:
            st.selectbox("Filter by Creative", ["All", "Ranked options"], key="api_filter_creative")
        st.info("Filters are wired to the preview API recommendation list.")

    with table_tab:
        if rec_rows:
            st.dataframe(rec_rows, use_container_width=True)
        else:
            st.info("No table rows for this run.")

    with chart_tab:
        if rec_rows:
            chart_data = {
                f"Rank {r.get('rank', '?')}": float(r.get("score") or 0) for r in rec_rows
            }
            st.bar_chart(chart_data)
            st.caption("Bar chart uses recommendation score from /v1/predictions/preview.")
        else:
            st.info("Charts need at least one recommendation row.")

    with model_tab:
        with st.container(border=True):
            st.subheader("Raw API response")
            st.json(result)

else:
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
            "Best predicted conversion",
        )

    with m4:
        metric_card(
            "Top Engagement",
            f"{top_creative.get('engagement_score', 86)}/100",
            "Best engagement score",
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
            "Rank #1–#3 creative cards will appear here after backend scoring.",
        )

    st.divider()

    st.subheader("Prepared Filters, Tables, and Charts")

    filter_tab, table_tab, chart_tab, model_tab = st.tabs(
        ["Filters", "Prediction Table", "Charts", "Model Output"]
    )

    with filter_tab:
        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            st.selectbox("Filter by Rank", ["All", "1", "2", "3"])

        with col2:
            st.selectbox(
                "Filter by Metric",
                ["CTR", "Conversion Rate", "Engagement Score"],
            )

        with col3:
            st.selectbox(
                "Filter by Creative",
                ["All"] + [creative.get("name") for creative in creatives],
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
            "This section is reserved for CTR, conversion, engagement, and reach comparison charts.",
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
        language="text",
    )
