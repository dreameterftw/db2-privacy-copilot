"""
Sign-in page for Db2 Privacy Copilot.
"""
import sys

import streamlit as st

sys.path.insert(0, "..")

from ui.theme import apply_workspace_theme


st.set_page_config(
    page_title="Sign in · Db2 Privacy Copilot",
    page_icon="🔐",
    layout="wide",
)

apply_workspace_theme()

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        .stApp {
            background:
                radial-gradient(ellipse at 12% 0%, rgba(36, 126, 113, 0.12), transparent 34%),
                #f4f7f6;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1120px;
            padding-top: 3.5rem;
            padding-bottom: 3rem;
        }

        .brand-row {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 3.5rem;
        }

        .brand-mark {
            display: grid;
            place-items: center;
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: #173b39;
            color: #d9f3eb;
            font-size: 21px;
        }

        .brand-name {
            color: #173b39;
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 0;
        }

        .brand-caption {
            color: #71817e;
            font-size: 12px;
            margin-top: 2px;
        }

        .intro-kicker {
            color: #398778;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0;
            text-transform: uppercase;
            margin-bottom: 12px;
        }

        .intro-title {
            color: #173b39;
            font-size: 42px;
            font-weight: 700;
            letter-spacing: 0;
            line-height: 1.12;
            margin: 0 0 12px;
        }

        .intro-copy {
            color: #647572;
            font-size: 16px;
            line-height: 1.6;
            margin: 0 0 30px;
            max-width: 620px;
        }

        .section-heading {
            color: #243b38;
            font-size: 14px;
            font-weight: 700;
            margin: 0 0 14px;
        }

        .role-card {
            min-height: 226px;
            border: 1px solid #dce6e2;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.88);
            padding: 20px;
            margin-bottom: 10px;
        }

        .role-card-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 18px;
        }

        .role-name {
            color: #173b39;
            font-size: 17px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .role-person {
            color: #71817e;
            font-size: 13px;
        }

        .role-badge {
            border-radius: 999px;
            background: #e8f3ef;
            color: #31796c;
            font-size: 10px;
            font-weight: 700;
            padding: 5px 9px;
            white-space: nowrap;
        }

        .role-email {
            color: #536663;
            font-size: 13px;
            margin-bottom: 10px;
        }

        .role-description {
            color: #647572;
            font-size: 13px;
            line-height: 1.5;
            min-height: 40px;
        }

        .role-permissions {
            border-top: 1px solid #e8eeeb;
            color: #72817e;
            font-size: 11px;
            line-height: 1.5;
            margin-top: 14px;
            padding-top: 12px;
        }

        div.stButton > button {
            min-height: 42px;
            border: 1px solid #173b39;
            border-radius: 7px;
            background: #173b39;
            color: #ffffff;
            font-size: 13px;
            font-weight: 600;
            transition: background 120ms ease, border-color 120ms ease;
        }

        div.stButton > button:hover {
            border-color: #28665d;
            background: #28665d;
            color: #ffffff;
        }

        div.stButton > button:focus {
            box-shadow: 0 0 0 3px rgba(57, 135, 120, 0.22);
        }

        .security-note {
            border-top: 1px solid #dce6e2;
            color: #647572;
            font-size: 12px;
            line-height: 1.6;
            margin-top: 32px;
            padding-top: 18px;
        }

        .security-note strong {
            color: #354c48;
        }

        @media (max-width: 700px) {
            [data-testid="stMainBlockContainer"] {
                padding-top: 1.5rem;
            }

            .brand-row {
                margin-bottom: 2rem;
            }

            .intro-title {
                font-size: 34px;
            }

            .role-card {
                min-height: auto;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if st.session_state.authenticated:
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
    st.success(
        f"Signed in as {st.session_state.user_name} · {st.session_state.user_role}"
    )

    col_continue, col_logout, _ = st.columns([1.4, 1.1, 5])
    with col_continue:
        if st.button("Continue to dashboard", use_container_width=True):
            st.switch_page("pages/2_📊_Dashboard.py")
    with col_logout:
        if st.button("Sign out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.user_name = None
            st.session_state.user_email = None
            st.rerun()

    st.stop()

st.markdown(
    """
    <div class="brand-row">
        <div class="brand-mark">⌑</div>
        <div>
            <div class="brand-name">Db2 Privacy Copilot</div>
            <div class="brand-caption">Privacy operations workspace</div>
        </div>
    </div>

    <div class="intro-kicker">Secure workspace access</div>
    <h1 class="intro-title">Sign in to your<br>privacy workspace.</h1>
    <p class="intro-copy">
        Choose an access profile to continue. Your workspace permissions are
        determined by your assigned role.
    </p>
    <div class="section-heading">Choose an access profile</div>
    """,
    unsafe_allow_html=True,
)

# Demo profiles for this starter sign-in flow.
users = {
    "VIEWER": {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "desc": "Read-only access to dashboards, discovery, and compliance reports.",
        "permissions": "Discovery · Classification · Audit logs",
        "badge": "READ ONLY",
    },
    "ANALYST": {
        "name": "Bob Smith",
        "email": "bob@example.com",
        "desc": "Review data and manage day-to-day privacy requests and consents.",
        "permissions": "Viewer access · Requests · Consents",
        "badge": "OPERATIONS",
    },
    "DPO": {
        "name": "Charlie Davis",
        "email": "charlie@example.com",
        "desc": "Oversight access for approvals, erasure, and audit verification.",
        "permissions": "Analyst access · Approvals · Erasure",
        "badge": "FULL ACCESS",
    },
}

columns = st.columns(3, gap="medium")

for column, (role, info) in zip(columns, users.items()):
    with column:
        st.markdown(
            f"""
            <div class="role-card">
                <div class="role-card-top">
                    <div>
                        <div class="role-name">{role.title()}</div>
                        <div class="role-person">{info['name']}</div>
                    </div>
                    <div class="role-badge">{info['badge']}</div>
                </div>
                <div class="role-email">{info['email']}</div>
                <div class="role-description">{info['desc']}</div>
                <div class="role-permissions">{info['permissions']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(f"Continue as {role.title()}", key=f"login_{role}", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_role = role
            st.session_state.user_name = info["name"]
            st.session_state.user_email = info["email"]
            st.switch_page("pages/2_📊_Dashboard.py")

st.markdown(
    """
    <div class="security-note">
        <strong>Security notice</strong><br>
        These sample profiles are for demonstration only. This sign-in flow is not
        an identity provider. Before using the workspace with real personal data,
        connect your organization’s identity provider and configure unique
        <code>VIEWER_TOKEN</code>, <code>ANALYST_TOKEN</code>, and
        <code>DPO_TOKEN</code> values.
    </div>
    """,
    unsafe_allow_html=True,
)

_, back_column = st.columns([5, 1.8])
with back_column:
    if st.button("← Back to landing page", use_container_width=True):
        st.switch_page("app.py")
