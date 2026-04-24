import streamlit as st

st.title("📊 Prediction Results")

st.divider()

st.success("🏆 Best Creative: Creative A")

# Metrics row
m1, m2, m3 = st.columns(3)

m1.metric("Conversion Rate", "3.8%")
m2.metric("CTR", "2.6%")
m3.metric("Engagement", "81%")

st.divider()

left, right = st.columns(2)

# Comparison
with left:
    st.markdown("### 📊 Creative Comparison")

    st.write("Creative A")
    st.progress(0.91)

    st.write("Creative B")
    st.progress(0.83)

    st.write("Creative C")
    st.progress(0.78)

# Recommendations
with right:
    st.markdown("### 💡 Recommendations")

    st.info("Use Creative A as primary asset")
    st.info("Improve CTA visibility")
    st.info("Reduce text density")