import streamlit as st

st.title("🚀 AdVise Platform")

st.markdown("### Predict campaign success before launch")

st.write(
    "Upload creatives, input campaign data, and receive AI-driven predictions."
)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🎨 Upload Creatives")
    st.write("Images or videos for analysis")

with col2:
    st.markdown("### 📊 Input Metrics")
    st.write("Budget, audience, platform")

with col3:
    st.markdown("### 🤖 Get Predictions")
    st.write("Performance & recommendations")

st.divider()

st.success("Make smarter marketing decisions with AI.")