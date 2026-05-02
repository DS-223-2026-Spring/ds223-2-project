import streamlit as st
from ui_components import load_css, page_header, feature_card, metric_card, placeholder_box

st.set_page_config(page_title="AdVise Home", layout="wide")
load_css()

page_header(
    "AdVise Dashboard",
    "Business overview for campaign planning, creative testing, and prediction results."
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    metric_card("Campaigns", "24", "Total campaigns tracked")

with m2:
    metric_card("Avg. CTR", "2.6%", "Estimated click-through rate")

with m3:
    metric_card("Conversion", "3.8%", "Predicted conversion rate")

with m4:
    metric_card("Success Score", "81/100", "Overall campaign quality")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    feature_card(
        "Creative Upload",
        "Upload campaign images or videos and prepare them for evaluation before launch."
    )

with col2:
    feature_card(
        "Campaign Setup",
        "Enter budget, platform, audience, CTA type, duration, and campaign objective."
    )

with col3:
    feature_card(
        "Prediction Results",
        "Review predicted CTR, conversion rate, engagement score, and recommendations."
    )

st.divider()

left, right = st.columns(2)

with left:
    placeholder_box(
        "Campaign Performance Overview",
        "Future chart showing campaign performance by platform, audience, and objective."
    )

with right:
    placeholder_box(
        "Creative Quality Overview",
        "Future visual comparison of creative strength, CTA clarity, and audience fit."
    )