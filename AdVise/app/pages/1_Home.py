import streamlit as st
from ui_components import page_header, feature_card, metric_card, placeholder_box

st.set_page_config(page_title="AdVise Home", layout="wide")

page_header(
    "AdVise Dashboard",
    "Business overview for campaign planning, creative testing, and prediction results."
)

m1, m2, m3, m4 = st.columns(4, gap="large")

with m1:
    metric_card("Campaigns", "24", "Total campaigns tracked")

with m2:
    metric_card("Avg. CTR", "2.6%", "Estimated click-through rate")

with m3:
    metric_card("Conversion", "3.8%", "Predicted conversion rate")

with m4:
    metric_card("Success Score", "81/100", "Overall campaign quality")

st.divider()

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    feature_card(
        "Creative Upload",
        "Upload campaign images or videos for pre-launch evaluation."
    )

with col2:
    feature_card(
        "Campaign Setup",
        "Enter budget, platform, audience, CTA type, duration, and campaign objective."
    )

with col3:
    feature_card(
        "Prediction Results",
        "Review predicted CTR, conversion rate, engagement, ranking, and recommendations."
    )

st.divider()

left, right = st.columns(2, gap="large")

with left:
    placeholder_box(
        "Campaign Performance Overview",
        "Future chart area for campaign performance by platform, audience, and objective."
    )

with right:
    placeholder_box(
        "Creative Quality Overview",
        "Future comparison area for creative strength, CTA clarity, and audience fit."
    )

st.divider()

st.subheader("Prepared Frontend Areas")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Data Table", "Filters", "Charts", "Model Results"]
)

with tab1:
    st.dataframe(
        {
            "Campaign": ["Campaign A", "Campaign B", "Campaign C"],
            "Platform": ["Instagram", "TikTok", "Facebook"],
            "Status": ["Draft", "Ready", "Tested"],
            "Predicted CTR": ["2.6%", "3.1%", "2.2%"],
        },
        use_container_width=True
    )

with tab2:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.selectbox("Platform", ["All", "Instagram", "Facebook", "TikTok"])

    with col2:
        st.selectbox("Intent", ["All", "Sales", "Awareness", "Traffic"])

    with col3:
        st.selectbox("Audience", ["All", "Cold", "Warm", "Hot"])


with tab3:
    st.bar_chart(
        {
            "CTR": [2.6, 3.1, 2.2],
            "Conversion": [3.8, 4.1, 3.3],
        }
    )

with tab4:
    with st.container(border=True):
        st.subheader("Model Output")
        st