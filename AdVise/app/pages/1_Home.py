import streamlit as st

st.set_page_config(page_title="AdVise Home", layout="wide")

st.title("AdVise")
st.subheader("Predict Before You Launch")

st.write(
    "Upload campaign creatives, enter campaign details, and receive predicted "
    "performance results before spending advertising budget."
)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Upload Creatives")
    st.write("Add 1–3 images or short videos for analysis.")

with col2:
    st.subheader("Input Metrics")
    st.write("Enter budget, platform, audience, CTA, intent, and duration.")

with col3:
    st.subheader("View Results")
    st.write("See predicted success metrics and best creative recommendation.")

st.divider()

st.success("Goal: help marketers choose stronger creatives before campaign launch.")