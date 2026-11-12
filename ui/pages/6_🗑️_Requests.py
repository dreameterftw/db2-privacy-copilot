"""Create rights requests and review human approvals."""

import html
import os
import secrets
import sys

import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api_client import call_api
from ui.theme import apply_workspace_theme


st.set_page_config(
    page_title="Requests · Db2 Privacy Copilot",
    page_icon="🗑️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_workspace_theme()

if not st.session_state.get("authenticated"):
    st.warning("Please sign in to access rights requests.")
    if st.button("Go to sign in"):
        st.switch_page("pages/1_🔐_Login.py")
    st.stop()

role = st.session_state.get("user_role", "VIEWER")


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

        .request-summary {
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
            font-size: 23px;
            font-weight: 700;
            line-height: 1.2;
            overflow-wrap: anywhere;
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

        div.stButton > button,
        div.stFormSubmitButton > button {
            min-height: 40px;
            border: 1px solid #d3dfda;
            border-radius: 7px;
            background: #ffffff;
            color: #24413c;
            font-size: 12px;
            font-weight: 600;
            transition: background 120ms ease, border-color 120ms ease;
        }

        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {
            border-color: #398778;
            background: #edf5f2;
            color: #173b39;
        }

        div.stButton > button:focus,
        div.stFormSubmitButton > button:focus {
            box-shadow: 0 0 0 3px rgba(57, 135, 120, 0.2);
        }

        [data-testid="stTabs"] [role="tab"] {
            color: #647572;
            font-size: 13px;
            font-weight: 600;
        }

        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            color: #173b39;
        }

        [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
            background-color: #398778;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #dce6e2;
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
    user_role = html.escape(str(role))
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
    <div class="page-kicker">Privacy operations</div>
    <h1 class="page-title">Rights requests</h1>
    <p class="page-subtitle">
        Create an erasure review plan and manage DPO approvals.
    </p>
    """,
    unsafe_allow_html=True,
)

create_tab, approve_tab = st.tabs(["Create request", "Review approvals"])


with create_tab:
    st.markdown(
        '<div class="section-heading">Request erasure review</div>'
        '<div class="section-caption">Create a dry-run plan for an authorized reviewer.</div>',
        unsafe_allow_html=True,
    )

    if role == "VIEWER":
        st.info("Analyst or DPO access is required to submit a request.")
    else:
        with st.form("create_erasure_request"):
            subject_id = st.number_input("Patient ID", min_value=1, step=1)
            submitted = st.form_submit_button(
                "Create request for DPO review",
                type="primary",
            )

        if submitted:
            try:
                result = call_api(
                    "POST",
                    "/requests",
                    role,
                    {"subject_id": int(subject_id)},
                )
                st.session_state["last_request_plan"] = result
                st.success("Request created. It is now waiting for DPO approval.")
            except RuntimeError as error:
                st.error(str(error))

        result = st.session_state.get("last_request_plan")

        if result:
            st.markdown(
                '<div class="section-heading">Dry-run plan</div>'
                '<div class="section-caption">Review the estimated impact and retention status.</div>',
                unsafe_allow_html=True,
            )

            plan_steps = result.get("steps", [])
            plan_columns = st.columns(3, gap="medium")

            with plan_columns[0]:
                st.markdown(
                    f"""
                    <div class="request-summary">
                        <div class="summary-label">Plan steps</div>
                        <div class="summary-value">{result.get("total_steps", 0)}</div>
                        <div class="summary-caption">Actions in this plan</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with plan_columns[1]:
                st.markdown(
                    f"""
                    <div class="request-summary">
                        <div class="summary-label">Estimated rows</div>
                        <div class="summary-value">{result.get("total_rows", 0)}</div>
                        <div class="summary-caption">Rows potentially affected</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with plan_columns[2]:
                retention_status = (
                    "Review needed"
                    if result.get("has_unverified")
                    else "Verified"
                )
                st.markdown(
                    f"""
                    <div class="request-summary">
                        <div class="summary-label">Retention review</div>
                        <div class="summary-value">{retention_status}</div>
                        <div class="summary-caption">Status of applicable rules</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            for index, step in enumerate(plan_steps, start=1):
                action = html.escape(str(step.get("action", "Action")))
                table = html.escape(str(step.get("table", "Unknown table")))
                estimated_rows = html.escape(str(step.get("est_rows", 0)))
                reason = step.get("reason", "")
                rule_verified = bool(step.get("rule_verified"))

                with st.expander(
                    f"{index}. {step.get('action', 'Action')} "
                    f"{step.get('table', 'Unknown table')} "
                    f"({step.get('est_rows', 0)} estimated rows)"
                ):
                    st.markdown(f"**{action} {table}**")
                    if reason:
                        st.write(reason)
                    st.caption(
                        f"{estimated_rows} estimated rows · Retention rule: "
                        f"{'verified' if rule_verified else 'unverified'}"
                    )

            plan_hash = html.escape(
                str(result.get("plan_hash", "unavailable"))
            )
            st.caption(f"Plan hash: `{plan_hash}`")


with approve_tab:
    st.markdown(
        '<div class="section-heading">Pending DPO approvals</div>'
        '<div class="section-caption">Review request plans before approving execution.</div>',
        unsafe_allow_html=True,
    )

    if role != "DPO":
        st.info("DPO access is required to approve pending requests.")

    try:
        pending = call_api(
            "GET",
            "/requests?status_filter=PENDING_APPROVAL",
            role,
        )
        requests = pending.get("requests", [])

        if not requests:
            st.success("There are no requests waiting for approval.")

        for request in requests:
            request_id = request["id"]
            details = call_api("GET", f"/requests/{request_id}", role)
            plan = details.get("plan") or {}
            simulation = plan.get("simulation", {})
            steps = plan.get("steps", [])

            with st.container(border=True):
                heading = st.columns([2, 1, 1])
                request_type = html.escape(str(details.get("type", "Request")))
                subject_id = html.escape(str(plan.get("subject_id", "—")))
                due_at = html.escape(str(details.get("due_at", "—")))

                heading[0].markdown(f"**Request #{request_id}** · {request_type}")
                heading[1].write(f"Patient ID: {subject_id}")
                heading[2].write(f"Due: {due_at}")

                plan_hash = html.escape(str(details.get("plan_hash", "")))
                st.caption(f"Plan hash: `{plan_hash}`")

                if simulation.get("has_unverified"):
                    st.warning("This plan includes unverified retention rules.")

                if steps:
                    for step in steps:
                        action = html.escape(str(step.get("action", "Action")))
                        table = html.escape(str(step.get("table", "Unknown table")))
                        estimated_rows = html.escape(str(step.get("est_rows", 0)))
                        reason = html.escape(str(step.get("reason", "")))

                        st.markdown(
                            f"**{action} {table}** · {estimated_rows} estimated rows"
                        )
                        if reason:
                            st.caption(reason)
                else:
                    st.caption("No plan steps are available.")

                if role == "DPO":
                    token_key = f"approval_id_{request_id}"
                    st.session_state.setdefault(token_key, secrets.token_hex(16))

                    with st.form(f"approve_request_{request_id}"):
                        approval_id = st.text_input(
                            "Approval reference",
                            value=st.session_state[token_key],
                            help="A unique reference is recorded with this approval.",
                        )
                        confirmed = st.checkbox(
                            "I reviewed this plan and approve the listed actions."
                        )
                        approve = st.form_submit_button(
                            "Approve and execute",
                            type="primary",
                        )

                    if approve:
                        if not confirmed:
                            st.error(
                                "Confirm that you reviewed the plan before approving."
                            )
                        elif not approval_id.strip():
                            st.error("Enter an approval reference.")
                        else:
                            try:
                                outcome = call_api(
                                    "POST",
                                    f"/requests/{request_id}/approve",
                                    role,
                                    {"approval_id": approval_id.strip()},
                                )
                                st.success(
                                    f"Request completed for subject "
                                    f"{outcome['subject_id']}. The action was audited."
                                )
                                st.rerun()
                            except RuntimeError as error:
                                st.error(str(error))

    except RuntimeError as error:
        st.error(str(error))
