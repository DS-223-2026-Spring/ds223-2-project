import streamlit as st

st.title("Prediction Results")

st.subheader("Winning Creative")
st.write("Creative A is predicted to perform best.")

st.metric("Creative Score", "91")
st.metric("Predicted Conversion Rate", "3.8%")
st.metric("Predicted CTR", "2.6%")
st.metric("Predicted Reach Score", "74/100")
st.metric("Predicted Lead Rate", "4.1%")
st.metric("Predicted Engagement Score", "81/100")
st.metric("Brand Consistency", "88/100")

st.subheader("Creative Comparison")
st.write("Creative A - Winning creative")
st.write("Creative B - Good alternative")
st.write("Creative C - Needs improvement")

st.subheader("Recommendations")
st.write("Launch with Creative A as the primary asset.")
st.write("Use a strong CTA that aligns with the campaign intent.")
st.write("Reduce text density where needed.")