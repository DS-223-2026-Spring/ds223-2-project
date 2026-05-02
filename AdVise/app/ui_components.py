import streamlit as st


def load_css():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f3f6fb;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        .main-title {
            font-size: 42px;
            font-weight: 800;
            color: #111827;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            font-size: 18px;
            color: #6b7280;
            margin-bottom: 2rem;
        }

        .business-card {
            background: #ffffff;
            border-radius: 20px;
            padding: 24px;
            min-height: 210px;
            height: 210px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
            border: 1px solid #e5e7eb;
        }

        .business-card h3 {
            font-size: 22px;
            margin-bottom: 12px;
            color: #111827;
        }

        .business-card p {
            color: #6b7280;
            font-size: 15px;
            line-height: 1.5;
        }

        .panel {
            background: #ffffff;
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
            border: 1px solid #e5e7eb;
            min-height: 300px;
        }

        .placeholder-card {
            background: #ffffff;
            border: 1px dashed #cbd5e1;
            border-radius: 20px;
            padding: 32px;
            min-height: 300px;
            height: 300px;
            text-align: center;
            color: #64748b;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        }

        .metric-card {
            background: #ffffff;
            border-radius: 20px;
            padding: 22px;
            min-height: 180px;
            height: 180px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
            border: 1px solid #e5e7eb;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .metric-card h4 {
            font-size: 18px;
            line-height: 1.25;
            min-height: 46px;
            margin: 0;
            color: #111827;
        }       

        .metric-value {
            font-size: 30px;
            font-weight: 800;
            color: #2563eb;
            margin: 0;
        }

        .metric-label {
            font-size: 13px;
            color: #6b7280;
            margin: 0;
            line-height: 1.3;
        }

        
    

        .recommendation-card {
            background: #ffffff;
            border-left: 5px solid #2563eb;
            border-radius: 16px;
            padding: 16px 18px;
            margin-bottom: 14px;
            color: #1f2937;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
        }

        div[data-testid="stFileUploader"] section {
            background-color: #ffffff;
            border-radius: 16px;
            border: 1px dashed #cbd5e1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def page_header(title, subtitle=None):
    st.markdown(f"<div class='main-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def feature_card(title, text):
    st.markdown(
        f"""
        <div class="business-card">
            <h3>{title}</h3>
            <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def metric_card(label, value, help_text=None):
    st.markdown(
        f"""
        <div class="metric-card">
            <h4>{label}</h4>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{help_text if help_text else ""}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def placeholder_box(title, text):
    st.markdown(
        f"""
        <div class="placeholder-card">
            <h3>{title}</h3>
            <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def recommendation_card(text):
    st.markdown(
        f"""
        <div class="recommendation-card">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )


def creative_score(name, description, score):
    st.write(f"**{name}**")
    st.caption(description)
    st.progress(score / 100)
    st.write(f"Score: **{score}/100**")