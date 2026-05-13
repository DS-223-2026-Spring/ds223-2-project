import streamlit as st

# ── Brand tokens ──────────────────────────────────────────────────────────────
PRIMARY      = "#4A90D9"
SUCCESS      = "#2ecc71"
WARNING      = "#f39c12"
DANGER       = "#e74c3c"
BG_DARK      = "#ffffff"
SURFACE      = "#f5f7fa"
BORDER       = "#e0e4ef"
TEXT_MUTED   = "#6b7280"

TIER_COLOR = {"high": SUCCESS, "medium": WARNING, "low": DANGER}


def inject_global_css():
    """Call once per page (e.g. in app.py or at the top of each page)."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'DM Sans', sans-serif;
        }}

        /* ── Page background ── */
        .stApp {{
            background: {BG_DARK};
        }}

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {{
            background: {SURFACE};
            border-right: 1px solid {BORDER};
        }}

        /* ── Headers ── */
        h1, h2, h3 {{
            font-family: 'Space Mono', monospace !important;
            letter-spacing: -0.02em;
        }}

        /* ── Metric value ── */
        [data-testid="stMetricValue"] {{
            font-family: 'Space Mono', monospace !important;
            font-size: 1.6rem !important;
        }}

        /* ── Container borders ── */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            border-color: {BORDER} !important;
            border-radius: 12px !important;
            background: {SURFACE} !important;
        }}

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab"] {{
            font-family: 'Space Mono', monospace;
            font-size: 0.8rem;
            letter-spacing: 0.05em;
        }}

        /* ── Buttons ── */
        .stButton > button[kind="primary"] {{
            background: {PRIMARY} !important;
            border: none !important;
            border-radius: 8px !important;
            font-family: 'Space Mono', monospace !important;
            letter-spacing: 0.05em;
            font-size: 0.85rem;
        }}

        /* ── Divider ── */
        hr {{
            border-color: {BORDER} !important;
            margin: 1.5rem 0 !important;
        }}

        /* ── Caption / muted ── */
        .caption-muted {{
            color: {TEXT_MUTED};
            font-size: 0.78rem;
        }}

        /* ── Tier badge ── */
        .tier-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            font-family: 'Space Mono', monospace;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}
        .tier-high   {{ background: #e8f8ef; color: #1a7a40; border: 1px solid #2ecc7144; }}
        .tier-medium {{ background: #fef6e4; color: #9a6000; border: 1px solid #f39c1244; }}
        .tier-low    {{ background: #fdeaea; color: #9a1a1a; border: 1px solid #e74c3c44; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str | None = None):
    inject_global_css()
    st.markdown(
        f"""
        <div style="margin-bottom:0.5rem">
          <h1 style="margin-bottom:0.1rem">{title}</h1>
          {"<p style='color:#8b8fa8;font-size:0.9rem;margin-top:0'>" + subtitle + "</p>" if subtitle else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()


def metric_card(label: str, value: str, help_text: str | None = None):
    with st.container(border=True):
        st.metric(label=label, value=value, help=help_text)


def feature_card(title: str, text: str):
    with st.container(border=True):
        st.subheader(title)
        st.write(text)


def placeholder_box(title: str, text: str):
    with st.container(border=True):
        st.subheader(title)
        st.info(text)


def recommendation_card(text: str, rank: int | None = None, score: float | None = None):
    """Styled recommendation row."""
    badge = f"#{rank} " if rank is not None else ""
    score_str = f"  ·  score **{score:.2f}**" if score is not None else ""
    with st.container(border=True):
        if rank is not None:
            st.markdown(f"**{badge}**{score_str}")
        st.write(text)


def tier_badge(tier: str) -> str:
    """Return HTML badge for a tier string."""
    t = (tier or "").strip().lower()
    cls = f"tier-{t}" if t in ("high", "medium", "low") else "tier-medium"
    return f'<span class="tier-badge {cls}">{tier}</span>'


def creative_score(name: str, description: str, score: int):
    with st.container(border=True):
        st.write(f"**{name}**")
        st.caption(description)
        st.progress(score / 100)
        st.write(f"Score: **{score}/100**")