import streamlit as st
from ui_components import page_header

st.set_page_config(page_title="AdVise Home", layout="wide")

page_header(
    "AdVise",
    "AI-powered campaign success prediction platform."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Upload Creatives")
    st.write("Upload 1–3 campaign creatives.")

with col2:
    st.subheader("Input Campaign Data")
    st.write("Enter budget, audience, platform, CTA, and campaign intent.")

with col3:
    st.subheader("View Predictions")
    st.write("Review predicted performance and recommendations.")

st.success("Goal: help marketers choose stronger creatives before launch.")