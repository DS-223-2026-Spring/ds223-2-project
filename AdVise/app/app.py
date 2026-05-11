import streamlit as st
from ui_components import page_header, placeholder_box
from api_client import get_status

st.set_page_config(
    page_title="AdVise",
    layout="wide",
    page_icon="📊"
)

status, status_code = get_status()

page_header(
    "AdVise",
    "AI-powered campaign success prediction platform."
)

if status_code == 200:
    st.success("Backend connected")
else:
    st.warning("Backend is not connected yet. The frontend can still be tested with placeholder data.")

st.write(
    "AdVise helps marketers upload creatives, enter campaign details, analyze expected performance, "
    "and review ranked recommendations before spending campaign budget."
)

col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.subheader("User Flow")

        st.write("**1. Upload Creatives**")
        st.caption("Add campaign images or videos.")

        st.write("**2. Enter Campaign Details**")
        st.caption("Fill budget, platform, audience, CTA, and intent.")

        st.write("**3. Analyze Campaign**")
        st.caption("Send the data to the prediction endpoint.")

        st.write("**4. Review Results**")
        st.caption("Compare creative rankings and recommendations.")
        
with col2:
    placeholder_box(
        "API Readiness",
        "Prepared for /v1/status, /v1/meta/enums, /v1/predictions/preview, and prediction run results."
    )