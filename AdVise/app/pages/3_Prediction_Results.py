import streamlit as st
from ui_components import (
    load_css,
    page_header,
    metric_card,
    creative_score,
    recommendation_card,
    placeholder_box,
)

st.set_page_config(page_title="Prediction Results", layout="wide")
load_css()

page_header(
    "Prediction Results",
    "Dashboard for predicted campaign performance and creative comparison."
)

st.success("Best Creative: Creative A")

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("CTR", "2.6%", "Predicted click-through rate")

with m2:
    metric_card("Conversion Rate", "3.8%", "Predicted conversion result")

with m3:
    metric_card("Engagement", "81/100", "Predicted engagement score")

with m4:
    metric_card("Reach Score", "74/100", "Estimated reach quality")

st.divider()

left, right = st.columns(2)

with left:
    placeholder_box(
        "Prediction Chart",
        "Future chart for CTR, conversion rate, engagement, and reach."
    )

with right:
    placeholder_box(
        "Model Output Table",
        "Backend prediction results will be displayed here."
    )

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Creative Comparison")

    creative_score(
        "Creative A",
        "Winning creative with strong CTA and clear product focus.",
        91
    )

    creative_score(
        "Creative B",
        "Good alternative, but CTA placement can be improved.",
        83
    )

    creative_score(
        "Creative C",
        "Needs improvement because text density is high.",
        78
    )

with right:
    st.subheader("Recommendations")

    recommendation_card("Launch with Creative A as the primary asset.")
    recommendation_card("Improve CTA visibility for better conversion.")
    recommendation_card("Reduce text density in weaker creatives.")
    recommendation_card("Keep campaign messaging aligned with selected intent.")