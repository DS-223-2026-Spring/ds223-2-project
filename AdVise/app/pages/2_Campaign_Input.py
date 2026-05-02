import streamlit as st
from ui_components import load_css, page_header, placeholder_box

st.set_page_config(page_title="Campaign Input", layout="wide")
load_css()

page_header(
    "Campaign Input",
    "Prepare campaign information and creative assets for prediction."
)

left, right = st.columns([1.1, 1.9], gap="large")

with left:
    st.markdown("### Creative Assets")

    uploaded_files = st.file_uploader(
        "Upload 1–3 creatives",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg", "mp4"]
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded")
    else:
        st.info("Upload campaign image or video creatives.")

    placeholder_box(
        "Creative Preview",
        "Uploaded creative preview will appear here."
    )

with right:
    st.markdown("### Campaign Details")

    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            budget = st.number_input("Budget", min_value=0)
            platform = st.selectbox(
                "Platform",
                ["Instagram", "Facebook", "TikTok", "Google Ads"]
            )
            campaign_intent = st.selectbox(
                "Campaign Intent",
                ["Sales", "Awareness", "Traffic", "Leads", "Engagement"]
            )

        with col2:
            duration = st.number_input("Duration", min_value=1)
            audience = st.selectbox("Audience", ["Cold", "Warm", "Hot"])
            cta_type = st.selectbox(
                "CTA Type",
                ["Buy Now", "Sign Up", "Learn More", "Go to Page"]
            )

    st.markdown("### Campaign Summary")

    with st.container(border=True):
        s1, s2, s3 = st.columns(3)

        with s1:
            st.metric("Budget", f"${budget}")
            st.metric("Duration", f"{duration} days")

        with s2:
            st.metric("Platform", platform)
            st.metric("Audience", audience)

        with s3:
            st.metric("Intent", campaign_intent)
            st.metric("CTA", cta_type)

    st.button("Run Prediction", use_container_width=True)