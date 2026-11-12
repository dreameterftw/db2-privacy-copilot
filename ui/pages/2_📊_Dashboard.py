"""
Main Dashboard - Overview and Quick Actions
"""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app import agents, audit
from app.config import settings
from app.db import query
from ui.api_client import call_api
from ui.theme import apply_workspace_theme


st.set_page_config(
    page_title="Dashboard · Db2 Privacy Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_workspace_theme()

# Check authentication
if not st.session_state.get("authenticated"):
    st.warning("Please sign in to access the dashboard.")
    if st.button("Go to sign in"):
        st.switch_page("pages/1_🔐_Login.py")
    st.stop()

# Dashboard styling, aligned with the sign-in page.
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

        .metric-card {
            min-height: 132px;
            border: 1px solid #dce6e2;
            border-radius: 9px;
            background: rgba(255, 255, 255, 0.9);
            padding: 17px 18px;
            margin: 0 0 8px;
        }

        .metric-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
        }

        .metric-label {
            color: #71817e;
            font-size: 12px;
            font-weight: 600;
        }

        .metric-icon {
            display: grid;
            place-items: center;
            width: 30px;
            height: 30px;
            border-radius: 8px;
            background: #e8f3ef;
            color: #31796c;
            font-size: 15px;
        }

        .metric-value {
            color: #173b39;
            font-size: 30px;
            font-weight: 700;
            line-height: 1.1;
            margin-top: 15px;
        }

        .action-note {
            border: 1px solid #dce6e2;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.72);
            color: #647572;
            font-size: 12px;
            line-height: 1.55;
            padding: 14px;
            margin: 0.25rem 0 0.75rem;
        }

        .activity-label {
            color: #173b39;
            font-weight: 700;
        }

        .footer-note {
            border-top: 1px solid #dce6e2;
            color: #71817e;
            font-size: 11px;
            margin-top: 1.5rem;
            padding-top: 14px;
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

        [data-testid="stAlert"] {
            border-radius: 8px;
        }

        @media (max-width: 700px) {
            [data-testid="stMainBlockContainer"] {
                padding-top: 1.25rem;
            }

            .page-title {
                font-size: 27px;
            }

            .metric-card {
                min-height: 116px;
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

    st.markdown(
        f"""
        <div class="account-card">
            <div class="account-name">{st.session_state.user_name}</div>
            <div class="account-role">{st.session_state.user_role}</div>
            <div class="account-email">{st.session_state.get("user_email", "N/A")}</div>
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
    f"""
    <div class="page-kicker">Privacy operations</div>
    <h1 class="page-title">Dashboard</h1>
    <p class="page-subtitle">
        Welcome back, <strong>{st.session_state.user_name}</strong>.
        Here’s your privacy compliance overview.
    </p>
    """,
    unsafe_allow_html=True,
)

# System overview
st.markdown(
    '<div class="section-heading">Workspace overview</div>'
    '<div class="section-caption">Current data discovery, requests, and audit activity.</div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    try:
        result = agents.discover_schema(settings.db2_schema)
        table_count = len(result.get("tables", []))
        value = table_count
    except Exception:
        value = "N/A"

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-top">
                <div class="metric-label">Tables discovered</div>
                <div class="metric-icon">▦</div>
            </div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    try:
        result = agents.classify_schema(settings.db2_schema)
        value = result.get("pii_columns", 0)
    except Exception:
        value = "N/A"

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-top">
                <div class="metric-label">PII columns</div>
                <div class="metric-icon">◇</div>
            </div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    try:
        rows = query(
            """
            SELECT COUNT(*) FROM REQUESTS
            WHERE STATUS = 'PENDING_APPROVAL'
            """
        )
        value = rows[0][0] if rows else 0
    except Exception:
        value = 0

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-top">
                <div class="metric-label">Pending requests</div>
                <div class="metric-icon">◷</div>
            </div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    try:
        records = audit.get_all_records()
        value = len(records)
    except Exception:
        value = 0

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-top">
                <div class="metric-label">Audit records</div>
                <div class="metric-icon">≡</div>
            </div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Quick actions
st.markdown(
    '<div class="section-heading">Quick actions</div>'
    '<div class="section-caption">Shortcuts available to your access profile.</div>',
    unsafe_allow_html=True,
)

action_col1, action_col2 = st.columns(2, gap="large")

with action_col1:
    if st.session_state.user_role in ["ANALYST", "DPO"]:
        if st.button("🔍  Run discovery scan", use_container_width=True):
            st.switch_page("pages/3_🔍_Discovery.py")

        if st.button("🏷️  Classify PII", use_container_width=True):
            st.switch_page("pages/4_🏷️_Classification.py")

        if st.button("➕  Create new request", use_container_width=True):
            st.switch_page("pages/6_🗑️_Requests.py")
    else:
        st.markdown(
            '<div class="action-note">Discovery, classification, and request creation '
            "are available to Analyst and DPO profiles.</div>",
            unsafe_allow_html=True,
        )

with action_col2:
    if st.session_state.user_role == "DPO":
        if st.button("✅  Review pending requests", use_container_width=True):
            st.switch_page("pages/6_🗑️_Requests.py")

        if st.button("🔍  Verify audit chain", use_container_width=True):
            st.switch_page("pages/7_📝_Audit.py")

        if st.button("⚙️  Manage retention rules", use_container_width=True):
            st.info("This feature is coming soon.")
    else:
        st.markdown(
            '<div class="action-note">Approval actions are available to the DPO profile.</div>',
            unsafe_allow_html=True,
        )

# Recent activity
st.markdown(
    '<div class="section-heading">Recent activity</div>'
    '<div class="section-caption">The latest events recorded in the audit log.</div>',
    unsafe_allow_html=True,
)

try:
    records = audit.get_all_records()[-10:]

    if records:
        for record in reversed(records):
            action_icon = {
                "STARTUP": "🚀",
                "CLASSIFICATION": "🏷️",
                "DISCOVERY": "🔍",
                "CONSENT_GRANTED": "✅",
                "CONSENT_WITHDRAWN": "❌",
                "REQUEST_CREATED": "📝",
                "ERASURE": "🗑️",
            }.get(record.action, "📌")

            with st.expander(
                f"{action_icon}  {record.action}  ·  {record.actor}  ·  {record.created_at}"
            ):
                detail_col, audit_col = st.columns([2, 1])

                with detail_col:
                    st.write(f"**Action:** {record.action}")
                    st.write(f"**Actor:** {record.actor}")
                    if record.subject:
                        st.write(f"**Subject ID:** {record.subject}")

                with audit_col:
                    st.write(f"**Hash:** `{record.hash[:16]}…`")
                    st.write(f"**ID:** {record.id}")

                if record.detail:
                    st.json(record.detail)
    else:
        st.info("No recent activity.")
except Exception as exc:
    st.error(f"Unable to load recent activity: {exc}")

# System health
st.markdown(
    '<div class="section-heading">System health</div>'
    '<div class="section-caption">API, database, and audit-chain status.</div>',
    unsafe_allow_html=True,
)

health_col, audit_col = st.columns(2, gap="large")

with health_col:
    try:
        health = call_api("GET", "/healthz", st.session_state.user_role)
    except RuntimeError as exc:
        st.error(f"API/database health check failed: {exc}")
    else:
        st.success("API: Connected")

        if health.get("database_mode") == "in_memory":
            st.info("Database: In-memory sample data")
        elif health.get("status") == "ok":
            st.success(f"Database: Connected to Db2 {health.get('db2', '')}".strip())
        else:
            st.warning("Database: Status unavailable")

    st.success("UI: Active")

with audit_col:
    try:
        is_valid, error = audit.verify_chain()
        if is_valid:
            st.success("Audit chain: Intact")
        else:
            st.error(f"Audit chain: Broken — {error}")
    except Exception as exc:
        st.warning(f"Audit chain: Unable to verify — {exc}")

# Role-specific guidance
st.markdown(
    '<div class="section-heading">Role guidance</div>'
    '<div class="section-caption">A brief reminder of the tasks available to you.</div>',
    unsafe_allow_html=True,
)

if st.session_state.user_role == "VIEWER":
    st.info(
        """
        **Viewer access**
        - Monitor system metrics and compliance status
        - View classification results and PII mappings
        - Review audit logs for transparency

        **Tip:** Use Discovery to understand the data relationships in your workspace.
        """
    )
elif st.session_state.user_role == "ANALYST":
    st.info(
        """
        **Analyst access**
        - Run discovery scans and PII classification
        - Create and manage consent records
        - Submit erasure requests for DPO approval
        - Review classification confidence scores

        **Tip:** Manually review low-confidence classifications before finalizing.
        """
    )
else:
    st.warning(
        """
        **DPO access**
        - Approve or reject erasure requests
        - Execute approved plans with guardrail validation
        - Verify audit-chain integrity
        - Manage retention rules and policies

        **Important:** Approval decisions are permanently recorded in the audit chain.
        """
    )

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div class="footer-note">
        Signed in as {st.session_state.user_name} · {st.session_state.user_role}
        · Session active · Db2 Privacy Copilot v0.1.0
    </div>
    """,
    unsafe_allow_html=True,
)
