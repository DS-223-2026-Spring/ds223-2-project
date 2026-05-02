import streamlit as st
from ui_components import load_css, page_header, placeholder_box

st.set_page_config(
    page_title="AdVise",
    layout="wide",
    page_icon="📊"
)

load_css()

page_header(
    "AdVise",
    "Predict campaign performance before launch."
)

st.write(
    "AdVise is an AI-powered marketing analytics platform that helps evaluate campaign creatives, "
    "campaign inputs, predicted results, and recommendations before spending budget."
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    placeholder_box(
        "Final App Layout",
        "Use the sidebar to move between Home, Campaign Input, and Prediction Results pages."
    )

with col2:
    placeholder_box(
        "Backend Integration Area",
        "The frontend layout is ready. Backend API and model outputs will be connected later."
    )