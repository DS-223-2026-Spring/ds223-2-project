import streamlit as st


def page_header(title, subtitle=None):
    st.title(title)
    if subtitle:
        st.write(subtitle)
    st.divider()


def section_title(title):
    st.subheader(title)


def metric_card(label, value, help_text=None):
    st.metric(label=label, value=value, help=help_text)


def recommendation_card(text):
    st.info(text)


def creative_score(name, description, score):
    st.write(f"**{name}**")
    st.write(description)
    st.progress(score / 100)


def placeholder_box(text):
    st.warning(text)