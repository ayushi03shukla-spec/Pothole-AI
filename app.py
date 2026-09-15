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
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    h1 {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Sidebar
with st.sidebar:
    st.markdown("## 🕳️ POTHOLE AI")
    st.markdown("---")
    st.markdown("### ⚙️ Navigation")

    if st.session_state.authenticated:
        selected_page = st.radio(
            "Choose a page:",
            ["📊 Dashboard", "🔍 Detection", "🗺️ Map View", "📜 History",
             "📄 Reports", "👤 Profile", "⚙️ Admin", "🚪 Logout"],
            label_visibility="collapsed"
        )

        if selected_page == "🚪 Logout":
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    else:
        selected_page = st.radio(
            "Choose a page:",
            ["🔐 Login", "📝 Register"],
            label_visibility="collapsed"
        )

    st.markdown("---")
    st.markdown("### 📋 Project Info")
    st.info("""
    **Pothole AI** - Smart Road Detection System

    🎯 **Objective:** Detect potholes on roads using AI

    📊 **Tech Stack:**
    - Python + YOLOv8
    - Streamlit (Frontend)
    - Flask (Backend)
    - MySQL (Database)

    👥 **Team:** Equal workload distribution
    """)

# Main content based on selected page
if st.session_state.authenticated:
    if selected_page == "📊 Dashboard":
        from app_pages import dashboard
        dashboard.show()

    elif selected_page == "🔍 Detection":
        from app_pages import detection
        detection.show()

    elif selected_page == "🗺️ Map View":
        from app_pages import map_view
        map_view.show()

    elif selected_page == "📜 History":
        from app_pages import history
        history.show()

    elif selected_page == "📄 Reports":
        from app_pages import reports
        reports.show()

    elif selected_page == "👤 Profile":
        from app_pages import profile
        profile.show()

    elif selected_page == "⚙️ Admin":
        from app_pages import admin
        admin.show()
else:
    if selected_page == "🔐 Login":
        from app_pages import auth
        auth.show_login()

    elif selected_page == "📝 Register":
        from app_pages import auth
        auth.show_register()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.8rem;'>
    <p>🕳️ Pothole AI v1.0.0 | Powered by Streamlit + YOLOv8 | © 2026 PSIT Kanpur</p>
</div>
""", unsafe_allow_html=True)
