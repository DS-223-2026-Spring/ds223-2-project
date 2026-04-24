import streamlit as st

st.set_page_config(page_title="Campaign Input", layout="wide")

st.title("Campaign Input")
st.write("Upload creatives and enter campaign information to prepare a prediction.")

st.divider()

left, right = st.columns([1, 2])

with left:
    st.subheader("Creative Upload")

    uploaded_files = st.file_uploader(
        "Upload 1–3 creatives",
        type=["png", "jpg", "jpeg", "mp4", "mov"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded")

with right:
    st.subheader("Campaign Metrics")

    col1, col2, col3 = st.columns(3)

    with col1:
        budget = st.number_input("Budget", min_value=0, value=6000)
        age_group = st.selectbox("Age Group", ["18–24", "25–34", "35–44", "45+"])
        device_type = st.selectbox("Device Type", ["Mobile", "Desktop", "Tablet"])
        career = st.text_input("Career", "Professionals")
        campaign_duration = st.number_input("Campaign Duration (days)", min_value=1, value=14)

    with col2:
        product_type = st.text_input("Product Type", "Skincare")
        region = st.text_input("Region", "Europe")
        customer_type = st.selectbox("Customer Type", ["New", "Returning"])
        campaign_intent = st.selectbox("Campaign Intent", ["Sales", "Awareness", "Traffic", "Leads", "Engagement"])
        cta_type = st.selectbox("CTA Type", ["Buy now", "Sign up", "Learn more", "Go to page"])

    with col3:
        audience_metrics = st.text_input("Audience Metrics", "Interest-based targeting")
        audience_temperature = st.selectbox("Audience Temperature", ["Cold", "Warm", "Hot"])
        gender = st.selectbox("Gender", ["All", "Male", "Female"])
        platform = st.selectbox("Platform", ["Instagram", "Facebook", "Google", "TikTok"])
        discount_offered = st.text_input("Discount Offered", "15%")

st.divider()

if st.button("Predict Campaign Performance"):
    st.success("Prediction request placeholder. Backend connection will be added later.")