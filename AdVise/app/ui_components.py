import streamlit as st


def load_css():
    return None


def page_header(title, subtitle=None):
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def feature_card(title, text):
    with st.container(border=True):
        st.subheader(title)
        st.write(text)


def metric_card(label, value, help_text=None):
    with st.container(border=True):
        st.metric(label=label, value=value, help=help_text)


def placeholder_box(title, text):
    with st.container(border=True):
        st.subheader(title)
        st.info(text)


def recommendation_card(text):
    st.info(text)


def creative_score(name, description, score):
    with st.container(border=True):
        st.write(f"**{name}**")
        st.caption(description)
        st.progress(score / 100)
        st.write(f"Score: **{score}/100**")