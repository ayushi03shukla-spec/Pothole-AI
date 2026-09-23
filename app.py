import streamlit as st
import os
from datetime import datetime
import sys

# Set page config
st.set_page_config(
    page_title="🕳️ Pothole AI - Detection System",
    page_icon="🕳️",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Custom CSS
st.markdown("""
<style>

/* =========================
   SIDEBAR
========================= */

section[data-testid="stSidebar"] {
    background-color: #0f172a;
    border-right: 1px solid #1e293b;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}


/* =========================
   BRAND
========================= */

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 4px 18px 4px;
}

.brand-icon {
    width: 42px;
    height: 42px;
    border-radius: 10px;

    display: flex;
    align-items: center;
    justify-content: center;

    background: #2563eb;
    color: white;

    font-size: 20px;
    font-weight: 700;
}

.brand-name {
    color: #f8fafc;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.brand-subtitle {
    color: #94a3b8;
    font-size: 11px;
    margin-top: 2px;
}


/* =========================
   DIVIDER
========================= */

.sidebar-divider {
    height: 1px;
    background: #1e293b;
    margin-bottom: 18px;
}


/* =========================
   NAVIGATION TITLES
========================= */

.nav-section-title {
    color: #64748b;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;

    margin: 8px 4px;
}

.management-title {
    margin-top: 22px;
}


/* =========================
   NAVIGATION
========================= */

section[data-testid="stSidebar"] .stRadio label {
    color: #cbd5e1 !important;
    font-size: 14px !important;
}

section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    gap: 3px;
}

section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
    padding: 11px 12px;
    border-radius: 8px;
    margin-bottom: 3px;
    transition: all 0.2s ease;
    cursor: pointer;
}
/* Sidebar navigation text */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
    margin: 0 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
}

/* Selected navigation text */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) p {
    color: #ffffff !important;
    font-weight: 600 !important;
}
/* Hide Streamlit radio circles */
section[data-testid="stSidebar"] div[data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}

section[data-testid="stSidebar"] div[data-testid="stRadio"] label > div:first-child {
    display: none !important;
}

/* Navigation item */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: transparent;
    border-radius: 8px;
    margin-bottom: 4px;
}

/* Navigation text */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
    color: #94a3b8 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* Hover */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: #1e293b !important;
}

/* Selected item */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
    background: #1d4ed8 !important;
}

/* Selected text */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) p {
    color: white !important;
    font-weight: 600 !important;
}

/* Navigation text */
section[data-testid="stSidebar"] .stRadio label p {
    color: #94a3b8 !important;
    font-size: 13px !important;
}

/* Hover */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
    background-color: #1e293b;
}

/* Radio circle */
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child {
    display: none;
}


/* =========================
   SYSTEM STATUS
========================= */

.system-status {
    display: flex;
    align-items: center;
    gap: 10px;

    padding: 11px 12px;

    background: #111c32;
    border: 1px solid #1e293b;

    border-radius: 9px;

    margin-top: 18px;
}

.status-dot {
    width: 8px;
    height: 8px;

    background: #22c55e;
    border-radius: 50%;
}

.status-title {
    color: #e2e8f0;
    font-size: 12px;
    font-weight: 600;
}

.status-subtitle {
    color: #64748b;
    font-size: 10px;
}


/* =========================
   PROJECT INFORMATION
========================= */

.project-info {
    padding: 5px 2px;
}

.info-title {
    color: #e2e8f0;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 7px;
}

.info-text {
    color: #94a3b8;
    font-size: 11px;
    line-height: 1.5;
    margin-bottom: 12px;
}

.info-row {
    display: flex;
    justify-content: space-between;

    padding: 6px 0;

    border-bottom: 1px solid #1e293b;

    color: #94a3b8;
    font-size: 11px;
}

.info-row strong {
    color: #cbd5e1;
}


/* =========================
   USER
========================= */

.sidebar-user {
    display: flex;
    align-items: center;
    gap: 10px;

    margin-top: 18px;
    padding: 10px;

    border-top: 1px solid #1e293b;
}

.user-avatar {
    width: 32px;
    height: 32px;

    border-radius: 50%;

    background: #2563eb;

    color: white;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 13px;
    font-weight: 600;
}

.user-name {
    color: #e2e8f0;
    font-size: 11px;
    font-weight: 600;
}

.user-role {
    color: #64748b;
    font-size: 10px;
}
/* =========================
   LOGIN INFORMATION
========================= */

.login-sidebar-info {
    margin-top: 30px;
    padding: 14px;

    background: #111c32;
    border: 1px solid #1e293b;

    border-radius: 10px;
}

.login-info-title {
    color: #e2e8f0;
    font-size: 13px;
    font-weight: 600;

    margin-bottom: 8px;
}

.login-info-text {
    color: #94a3b8;
    font-size: 11px;
    line-height: 1.5;

    margin-bottom: 12px;
}

.mini-feature {
    color: #94a3b8;
    font-size: 11px;

    padding: 4px 0;
}


/* =========================
   MAIN CONTENT
========================= */

.main {
    padding-top: 2rem;
}

h1 {
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}

</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# =========================
# PRODUCTION SIDEBAR
# =========================

with st.sidebar:

    # ---------- BRAND ----------
    st.markdown("""
    <div class="sidebar-brand">
        <div class="brand-icon">P</div>
        <div>
            <div class="brand-name">POTHOLE AI</div>
            <div class="brand-subtitle">Road Intelligence System</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='sidebar-divider'></div>",
        unsafe_allow_html=True
    )

    # ---------- NAVIGATION ----------
    if st.session_state.authenticated:

        st.markdown(
            "<div class='nav-section-title'>WORKSPACE</div>",
            unsafe_allow_html=True
        )

        selected_page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Detection",
                "Map View",
                "History",
                "Reports"
            ],
            label_visibility="collapsed"
        )

        st.markdown(
            "<div class='nav-section-title management-title'>MANAGEMENT</div>",
            unsafe_allow_html=True
        )

        management_page = st.radio(
             "Management",
             [
                 "Profile",
                 "Admin",
                 "Logout"
             ],
             index=None,
             label_visibility="collapsed"
        )

        if management_page is not None:
            selected_page = management_page
        # ---------- SYSTEM STATUS ----------
        st.markdown("""
        <div class="system-status">
            <div class="status-dot"></div>
            <div>
                <div class="status-title">System Operational</div>
                <div class="status-subtitle">AI services are running</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ---------- PROJECT INFORMATION ----------
        with st.expander("Project Information"):

            st.markdown("""
            <div class="project-info">

                <div class="info-title">
                    Pothole AI
                </div>

                <div class="info-text">
                    Smart road damage detection using
                    computer vision and YOLOv8.
                </div>

                <div class="info-row">
                    <span>AI Model</span>
                    <strong>YOLOv8</strong>
                </div>

                <div class="info-row">
                    <span>Backend</span>
                    <strong>Flask</strong>
                </div>

                <div class="info-row">
                    <span>Frontend</span>
                    <strong>Streamlit</strong>
                </div>

                <div class="info-row">
                    <span>Database</span>
                    <strong>SQLite</strong>
                </div>

            </div>
            """, unsafe_allow_html=True)

        # ---------- USER ----------
        # ---------- USER ----------
                # ---------- USER ----------
        user = st.session_state.get("user") or {}

        user_name = user.get("name") or "Authenticated User"
        user_role = user.get("role") or "Project Member"

        with st.container(border=True):
            st.markdown(
                f"**{user_name}**"
            )
            st.caption(user_role)
        # ---------- LOGOUT ----------
        if selected_page == "Logout":

            st.session_state.authenticated = False
            st.session_state.user = None

            st.rerun()

    else:

        # ---------- LOGIN / REGISTER ----------
        st.markdown(
            "<div class='nav-section-title'>ACCOUNT</div>",
            unsafe_allow_html=True
        )

        selected_page = st.radio(
            "Account",
            [
                "Login",
                "Register"
            ],
            label_visibility="collapsed"
        )
        st.markdown(
    '<div class="login-sidebar-info">'
    '<div class="login-info-title">Smart Road Monitoring</div>'
    '<div class="login-info-text">'
    'Detect potholes using AI-powered computer vision '
    'and visualize road damage insights.'
    '</div>'
    '<div class="mini-feature">✓ YOLOv8 Detection</div>'
    '<div class="mini-feature">✓ Detection History</div>'
    '<div class="mini-feature">✓ Road Mapping</div>'
    '</div>',
    unsafe_allow_html=True
)

       

# Main content based on selected page
if st.session_state.authenticated:

    if selected_page == "Dashboard":
        from app_pages import dashboard
        dashboard.show()

    elif selected_page == "Detection":
        from app_pages import detection
        detection.show()

    elif selected_page == "Map View":
        from app_pages import map_view
        map_view.show()

    elif selected_page == "History":
        from app_pages import history
        history.show()

    elif selected_page == "Reports":
        from app_pages import reports
        reports.show()

    elif selected_page == "Profile":
        from app_pages import profile
        profile.show()

    elif selected_page == "Admin":
        from app_pages import admin
        admin.show()
else:

    if selected_page == "Login":
        from app_pages import auth
        auth.show_login()

    elif selected_page == "Register":
        from app_pages import auth
        auth.show_register()
# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.8rem;'>
    <p>🕳️ Pothole AI v1.0.0 | Powered by Streamlit + YOLOv8 | © 2026 PSIT Kanpur</p>
</div>
""", unsafe_allow_html=True)
