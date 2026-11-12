"""
Consent Management Page
"""
import html
import os
import sys
from datetime import date

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app import consent
from ui.theme import apply_workspace_theme


st.set_page_config(
    page_title="Consents · Db2 Privacy Copilot",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_workspace_theme()

if not st.session_state.get("authenticated"):
    st.warning("Please sign in to access consent management.")
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
    <div class="page-kicker">Privacy operations</div>
    <h1 class="page-title">Consent management</h1>
    <p class="page-subtitle">
        Grant, withdraw, and review patient consent records.
    </p>
    """,
    unsafe_allow_html=True,
)

tab_grant, tab_withdraw, tab_view = st.tabs(
    ["Grant consent", "Withdraw consent", "View consents"]
)


with tab_grant:
    st.markdown(
        '<div class="section-heading">Grant consent</div>'
        '<div class="section-caption">Record an approved purpose and its validity period.</div>',
        unsafe_allow_html=True,
    )

    with st.form("grant_form"):
        patient_id = st.number_input("Patient ID", min_value=1, step=1)
        purpose = st.selectbox(
            "Purpose",
            ["MARKETING", "RESEARCH", "TREATMENT", "ANALYTICS"],
        )
        start_date = st.date_input("Start date", value=date.today())
        end_date = st.date_input("End date", value=date(2027, 12, 31))

        submitted = st.form_submit_button("Grant consent", type="primary")

    if submitted:
        if end_date < start_date:
            st.error("End date must be on or after the start date.")
        else:
            try:
                consent.grant(
                    patient_id,
                    purpose,
                    start_date.isoformat(),
                    end_date.isoformat(),
                )
                st.success(f"Consent granted for patient {patient_id}.")
            except Exception as exc:
                st.error(f"Could not grant consent: {exc}")


with tab_withdraw:
    st.markdown(
        '<div class="section-heading">Withdraw consent</div>'
        '<div class="section-caption">Set the effective date for a consent withdrawal.</div>',
        unsafe_allow_html=True,
    )

    with st.form("withdraw_form"):
        withdraw_patient_id = st.number_input(
            "Patient ID",
            min_value=1,
            step=1,
            key="withdraw_patient_id",
        )
        withdraw_purpose = st.selectbox(
            "Purpose",
            ["MARKETING", "RESEARCH", "TREATMENT", "ANALYTICS"],
            key="withdraw_purpose",
        )
        effective_date = st.date_input(
            "Effective date",
            value=date.today(),
            key="withdraw_effective_date",
        )

        submitted = st.form_submit_button("Withdraw consent", type="primary")

    if submitted:
        try:
            consent.withdraw(
                withdraw_patient_id,
                withdraw_purpose,
                effective_date.isoformat(),
            )
            st.success(f"Consent withdrawn for patient {withdraw_patient_id}.")
        except Exception as exc:
            st.error(f"Could not withdraw consent: {exc}")


with tab_view:
    st.markdown(
        '<div class="section-heading">View consents</div>'
        '<div class="section-caption">Review the current consent records for a patient.</div>',
        unsafe_allow_html=True,
    )

    view_patient_id = st.number_input(
        "Patient ID",
        min_value=1,
        step=1,
        key="view_patient_id",
    )

    if st.button("Load consents", type="primary"):
        try:
            consents = consent.current_consents(view_patient_id)

            if consents:
                for record in consents:
                    granted = record.get("granted", False)
                    status = "Granted" if granted else "Withdrawn"
                    purpose_label = html.escape(str(record.get("purpose", "Unknown")))
                    bus_start = html.escape(str(record.get("bus_start", "—")))
                    bus_end = html.escape(str(record.get("bus_end", "—")))

                    with st.container(border=True):
                        st.markdown(f"**{purpose_label}** · {status}")
                        st.caption(f"Valid: {bus_start} to {bus_end}")
            else:
                st.info(f"No consents found for patient {view_patient_id}.")
        except Exception as exc:
            st.error(f"Could not load consents: {exc}")
