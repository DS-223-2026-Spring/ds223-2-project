import streamlit as st
from ui_components import page_header, inject_global_css
from api_client import get_status

st.set_page_config(
    page_title="AdVise",
    layout="wide",
    page_icon="📊",
)

inject_global_css()

status, status_code = get_status()

page_header(
    "AdVise",
    "AI-powered campaign success prediction platform.",
)

# ── Connection banner ──────────────────────────────────────────────────────────
if status_code == 200:
    st.success("✓ Backend connected")
else:
    st.warning(
        "Backend not reachable — frontend can still be explored with placeholder data."
    )

st.write(
    "AdVise helps marketers upload creatives, enter campaign details, analyze expected "
    "performance, and review ranked recommendations before spending campaign budget."
)

st.divider()

# ── User flow + API readiness ─────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.subheader("User Flow")
        steps = [
            ("1. Upload Creatives", "Add campaign images or videos (up to 3)."),
            ("2. Enter Campaign Details", "Budget, platform, audience, CTA, and intent."),
            ("3. Analyze Campaign", "Send data to the prediction endpoint."),
            ("4. Review Results", "Compare creative rankings and recommendations."),
        ]
        for title, caption in steps:
            st.write(f"**{title}**")
            st.caption(caption)

with col2:
    with st.container(border=True):
        st.subheader("API Readiness")
        endpoints = [
            ("GET", "/v1/status", "Health check"),
            ("GET", "/v1/meta/enums", "Dropdown vocabulary"),
            ("POST", "/v1/predictions/preview", "Live prediction"),
            ("GET", "/v1/prediction-runs/{id}", "Run history"),
        ]
        for method, path, desc in endpoints:
            color = "#4A90D9" if method == "GET" else "#2ecc71"
            st.markdown(
                f'<code style="color:{color};background:#1a1d27;padding:2px 6px;'
                f'border-radius:4px;font-size:0.75rem">{method}</code> '
                f'`{path}` — {desc}',
                unsafe_allow_html=True,
            )