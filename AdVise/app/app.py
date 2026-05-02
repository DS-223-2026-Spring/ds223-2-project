import streamlit as st
from ui_components import load_css, page_header, placeholder_box
from api_client import get_status

st.set_page_config(
    page_title="AdVise",
    layout="wide",
    page_icon="📊"
)

load_css()

status, status_code = get_status()

page_header(
    "AdVise",
    "Predict campaign performance before launch."
)

if status_code == 200:
    st.success("Backend connected")
else:
    st.warning("Backend is not connected yet. You can still use the frontend layout with placeholder data.")

st.write(
    "AdVise helps marketers upload creatives, enter campaign details, analyze expected performance, "
    "and review ranked recommendations before spending campaign budget."
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    placeholder_box(
        "User Flow",
        "1. Upload creatives → 2. Enter campaign details → 3. Analyze → 4. Review ranked prediction results."
    )

with col2:
    placeholder_box(
        "Backend Integration",
        "This screen checks /v1/status and prepares the app for live API integration."
    )