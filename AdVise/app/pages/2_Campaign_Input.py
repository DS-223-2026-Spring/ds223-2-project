import streamlit as st

st.title("📝 Campaign Setup")

st.divider()

left, right = st.columns([1, 2])

# Upload Section
with left:
    st.markdown("### 🎨 Upload Creatives")
    uploaded = st.file_uploader(
        "Upload 1–3 files",
        accept_multiple_files=True
    )
    if uploaded:
        st.success(f"{len(uploaded)} file(s) uploaded")

# Inputs Section
with right:
    st.markdown("### 📊 Campaign Details")

    col1, col2 = st.columns(2)

    with col1:
        budget = st.number_input("Budget", 0, value=6000)
        platform = st.selectbox("Platform", ["Instagram", "Facebook", "TikTok"])
        intent = st.selectbox("Intent", ["Sales", "Awareness"])

    with col2:
        duration = st.number_input("Duration (days)", 1, value=14)
        audience = st.selectbox("Audience", ["Cold", "Warm", "Hot"])
        cta = st.selectbox("CTA", ["Buy Now", "Learn More"])

st.divider()

if st.button("🚀 Run Prediction"):
    st.success("Prediction will be shown on results page.")