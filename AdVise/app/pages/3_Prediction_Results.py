import streamlit as st
from ui_components import page_header, metric_card, creative_score, recommendation_card

st.set_page_config(page_title="Prediction Results", layout="wide")

page_header(
    "Prediction Results",
    "Dashboard for predicted campaign performance and creative comparison."
)

st.success("Best Creative: Creative A")

st.subheader("Model Output Area")

m1, m2, m3 = st.columns(3)

with m1:
    metric_card("Conversion Rate", "3.8%")

with m2:
    metric_card("CTR", "2.6%")

with m3:
    metric_card("Engagement Score", "81/100")

st.divider()

st.subheader("Charts Placeholder")
st.write("Future charts for CTR, conversion rate, engagement, and creative performance will be displayed here.")

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