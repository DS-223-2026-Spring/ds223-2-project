import streamlit as st

st.set_page_config(
    page_title="AdVise",
    layout="wide",
    page_icon="📊"
)

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 AdVise")
st.subheader("Predict Before You Launch")

st.write(
    "AI-powered platform to evaluate campaign performance before spending budget."
)

st.divider()

st.info("Use the sidebar to navigate between pages.")