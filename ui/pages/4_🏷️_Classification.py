"""
PII Classification Page
"""
import html
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app import agents
from app.config import settings
from ui.theme import apply_workspace_theme


st.set_page_config(
    page_title="Classification · Db2 Privacy Copilot",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_workspace_theme()

if not st.session_state.get("authenticated"):
    st.warning("Please sign in to access PII classification.")
    if st.button("Go to sign in"):
        st.switch_page("pages/1_🔐_Login.py")
    st.stop()


st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(ellipse at 12% 0%, rgba(36, 126, 113, 0.08), transparent 34%),
                #f4f7f6;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1440px;
            padding-top: 2.2rem;
            padding-bottom: 2.5rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid #dce6e2;
            background: #fbfcfb;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.5rem;
        }

        .brand-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 1.7rem;
        }

        .brand-mark {
            display: grid;
            place-items: center;
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: #173b39;
            color: #d9f3eb;
            font-size: 18px;
        }

        .brand-name {
            color: #173b39;
            font-size: 13px;
            font-weight: 700;
        }

        .brand-caption {
            color: #71817e;
            font-size: 11px;
            margin-top: 2px;
        }

        .account-card {
            border: 1px solid #dce6e2;
            border-radius: 8px;
            background: #ffffff;
            padding: 14px;
            margin: 1rem 0 1.25rem;
        }

        .account-name {
            color: #173b39;
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .account-role {
            color: #398778;
            font-size: 11px;
            font-weight: 700;
            margin-bottom: 7px;
        }

        .account-email {
            color: #71817e;
            font-size: 11px;
            overflow-wrap: anywhere;
        }

        .sidebar-heading {
            color: #82908d;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            margin: 1.25rem 0 0.5rem;
        }

        .page-kicker {
            color: #398778;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            margin: 0 0 8px;
        }

        .page-title {
            color: #173b39;
            font-size: 32px;
            font-weight: 700;
            line-height: 1.2;
            margin: 0;
        }

        .page-subtitle {
            color: #647572;
            font-size: 14px;
            line-height: 1.6;
            margin: 8px 0 0;
        }

        .section-heading {
            color: #243b38;
            font-size: 17px;
            font-weight: 700;
            margin: 1.5rem 0 0.2rem;
        }

        .section-caption {
            color: #71817e;
            font-size: 12px;
            margin: 0 0 0.9rem;
        }

        .classification-summary {
            border: 1px solid #dce6e2;
            border-radius: 9px;
            background: rgba(255, 255, 255, 0.9);
            padding: 16px 18px;
            margin: 0.5rem 0 1rem;
        }

        .summary-label {
            color: #71817e;
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .summary-value {
            color: #173b39;
            font-size: 26px;
            font-weight: 700;
            line-height: 1.15;
        }

        .summary-caption {
            color: #71817e;
            font-size: 11px;
            margin-top: 5px;
        }

        .empty-state {
            border: 1px dashed #cbd9d3;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.65);
            color: #647572;
            padding: 18px;
            font-size: 13px;
            line-height: 1.6;
        }

        div.stButton > button {
            min-height: 40px;
            border: 1px solid #d3dfda;
            border-radius: 7px;
            background: #ffffff;
            color: #24413c;
            font-size: 12px;
            font-weight: 600;
            transition: background 120ms ease, border-color 120ms ease;
        }

        div.stButton > button:hover {
            border-color: #398778;
            background: #edf5f2;
            color: #173b39;
        }

        div.stButton > button:focus {
            box-shadow: 0 0 0 3px rgba(57, 135, 120, 0.2);
        }

        [data-testid="stExpander"] {
            border: 1px solid #dce6e2;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.82);
        }

        @media (max-width: 700px) {
            [data-testid="stMainBlockContainer"] {
                padding-top: 1.25rem;
            }

            .page-title {
                font-size: 27px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# Sidebar
with st.sidebar:
    st.markdown(
        """
        <div class="brand-row">
            <div class="brand-mark">⌑</div>
            <div>
                <div class="brand-name">Db2 Privacy Copilot</div>
                <div class="brand-caption">Privacy operations workspace</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_name = html.escape(
        str(st.session_state.get("user_name", "Workspace user"))
    )
    user_role = html.escape(str(st.session_state.get("user_role", "VIEWER")))
    user_email = html.escape(str(st.session_state.get("user_email", "N/A")))

    st.markdown(
        f"""
        <div class="account-card">
            <div class="account-name">{user_name}</div>
            <div class="account-role">{user_role}</div>
            <div class="account-email">{user_email}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-heading">Workspace</div>', unsafe_allow_html=True)

    if st.button("📊  Dashboard", use_container_width=True):
        st.switch_page("pages/2_📊_Dashboard.py")

    if st.button("🔍  Discovery", use_container_width=True):
        st.switch_page("pages/3_🔍_Discovery.py")

    if st.button("🏷️  Classification", use_container_width=True):
        st.switch_page("pages/4_🏷️_Classification.py")

    if st.button("✅  Consents", use_container_width=True):
        st.switch_page("pages/5_✅_Consents.py")

    if st.button("🗑️  Requests", use_container_width=True):
        st.switch_page("pages/6_🗑️_Requests.py")

    if st.button("📝  Audit log", use_container_width=True):
        st.switch_page("pages/7_📝_Audit.py")

    st.markdown("---")

    if st.button("Sign out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.user_name = None
        st.session_state.user_email = None
        st.switch_page("app.py")


# Page heading
st.markdown(
    """
    <div class="page-kicker">Data inventory</div>
    <h1 class="page-title">PII classification</h1>
    <p class="page-subtitle">
        Identify personal data in your schema with pattern matching and semantic analysis.
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-heading">Classification scan</div>'
    '<div class="section-caption">Review detected personal data and confidence levels.</div>',
    unsafe_allow_html=True,
)

if st.button("🔍  Run classification", type="primary"):
    with st.spinner("Classifying columns…"):
        try:
            st.session_state.classification_result = agents.classify_schema(
                settings.db2_schema
            )
            st.session_state.classification_error = None
        except Exception as exc:
            st.session_state.classification_result = None
            st.session_state.classification_error = str(exc)

if st.session_state.get("classification_error"):
    st.error(f"Classification failed: {st.session_state.classification_error}")

result = st.session_state.get("classification_result")

if result:
    total_columns = result.get("total_columns", 0)
    pii_columns = result.get("pii_columns", 0)
    needs_review = result.get("needs_review", 0)
    by_label = result.get("by_label", {})

    st.success(f"Classification complete · {total_columns} columns analyzed.")

    metric_col1, metric_col2, metric_col3 = st.columns(3, gap="medium")

    with metric_col1:
        st.markdown(
            f"""
            <div class="classification-summary">
                <div class="summary-label">Columns analyzed</div>
                <div class="summary-value">{total_columns}</div>
                <div class="summary-caption">Across the configured schema</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metric_col2:
        st.markdown(
            f"""
            <div class="classification-summary">
                <div class="summary-label">PII columns</div>
                <div class="summary-value">{pii_columns}</div>
                <div class="summary-caption">Columns identified as personal data</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metric_col3:
        st.markdown(
            f"""
            <div class="classification-summary">
                <div class="summary-label">Need review</div>
                <div class="summary-value">{needs_review}</div>
                <div class="summary-caption">Detections flagged for verification</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-heading">Classification results</div>'
        '<div class="section-caption">Personal-data columns grouped by detected category.</div>',
        unsafe_allow_html=True,
    )

    classified_groups = [
        (label, columns)
        for label, columns in by_label.items()
        if label != "NOT_PII" and columns
    ]

    if classified_groups:
        for index, (label, columns) in enumerate(classified_groups):
            with st.expander(
                f"🏷️  {label}  ·  {len(columns)} columns",
                expanded=index == 0,
            ):
                st.dataframe(
                    [
                        {
                            "Table": column.get("table", ""),
                            "Column": column.get("column", ""),
                            "Confidence": f"{column.get('confidence', 0) * 100:.1f}%",
                            "Method": column.get("method", "—"),
                            "Status": (
                                "Review recommended"
                                if column.get("needs_review")
                                else "Classified"
                            ),
                        }
                        for column in columns
                    ],
                    hide_index=True,
                    use_container_width=True,
                )
    else:
        st.markdown(
            '<div class="empty-state">No PII columns were identified in this scan.</div>',
            unsafe_allow_html=True,
        )

else:
    st.markdown(
        """
        <div class="empty-state">
            No classification results to show yet. Run a scan to review detected
            personal data and any columns that may need verification.
        </div>
        """,
        unsafe_allow_html=True,
    )
