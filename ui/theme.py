"""Shared visual system for the Streamlit workspace."""

import streamlit as st


def apply_workspace_theme() -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#14263d; --muted:#5d6e80; --blue:#1769aa; --line:#e2e8ef; }
        .stApp { background:#f6f8fb; color:var(--ink); }
        [data-testid="stHeader"] { background:rgba(246,248,251,.92); }
        [data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--line); }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#526477; }
        .block-container { max-width:1320px; padding-top:2rem; padding-bottom:3rem; }
        h1 { color:var(--ink); letter-spacing:-.035em; font-weight:700; }
        h2,h3 { color:#203850; letter-spacing:-.02em; }
        [data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-radius:12px; padding:18px 20px; box-shadow:0 2px 8px #14263d08; }
        [data-testid="stMetricLabel"] { color:var(--muted); }
        [data-testid="stMetricValue"] { color:var(--ink); }
        [data-testid="stVerticalBlockBorderWrapper"] { background:#fff; border-color:var(--line); border-radius:12px; }
        .stButton > button, .stFormSubmitButton > button { border-radius:8px; min-height:42px; font-weight:600; }
        .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] { background:#1769aa; border-color:#1769aa; }
        div[data-testid="stTabs"] button { font-weight:600; }
        [data-testid="stExpander"] { background:#fff; border:1px solid var(--line); border-radius:10px; }
        [data-testid="stAlert"] { border-radius:10px; }
        code { color:#1769aa; }
        </style>
        """,
        unsafe_allow_html=True,
    )
