import streamlit as st
from ui_components import page_header

st.set_page_config(page_title="Campaign Input", layout="wide")

page_header(
    "Campaign Input",
    "Upload creatives and enter campaign details."
)

left, right = st.columns([1, 2])

with left:
    st.subheader("Creative Upload Area")

    uploaded_files = st.file_uploader(
        "Upload 1–3 creatives",
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded")
    else:
        st.info("Upload area placeholder for campaign images or videos.")

with right:
    st.subheader("Campaign Form")

    col1, col2 = st.columns(2)

    with col1:
        budget = st.number_input("Budget", min_value=0)
        platform = st.selectbox("Platform", ["Instagram", "Facebook", "TikTok"])
        campaign_intent = st.selectbox(
            "Campaign Intent",
            ["Sales", "Awareness", "Traffic", "Leads", "Engagement"]
        )

    with col2:
        duration = st.number_input("Duration", min_value=1)
        audience = st.selectbox("Audience", ["Cold", "Warm", "Hot"])
        cta_type = st.selectbox("CTA Type", ["Buy Now", "Sign Up", "Learn More", "Go to Page"])

st.divider()

st.subheader("Filters Placeholder")
st.write("Future filters for platform, audience type, campaign intent, and creative type will appear here.")

st.subheader("Form Summary Placeholder")
st.write("A summary of entered campaign data will be shown here before submitting.")

if st.button("Run Prediction"):
    st.success("Prediction placeholder. Backend connection will be added later.")