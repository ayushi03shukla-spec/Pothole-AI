import streamlit as st
import pandas as pd
from datetime import datetime

def show():
    """Display user profile page"""
    st.markdown("# 👤 User Profile")

    if not st.session_state.user:
        st.error("Please login first")
        return

    user = st.session_state.user

    # Profile header
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("### Avatar")
        st.write(f"👤 {user['name'][0].upper()}")

    with col2:
        st.markdown("### Profile Information")
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Role:** {user['role'].replace('_', ' ').title()}")
        st.write(f"**Joined:** {user.get('login_time', datetime.now()).strftime('%B %d, %Y')}")

    # Tabs
    tab_info, tab_stats, tab_settings, tab_security = st.tabs(
        ["📋 Information", "📊 Statistics", "⚙️ Settings", "🔒 Security"]
    )

    with tab_info:
        show_information()

    with tab_stats:
        show_statistics()

    with tab_settings:
        show_settings()

    with tab_security:
        show_security()

def show_information():
    """Show user information"""
    st.markdown("## Edit Profile Information")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Full Name", value=st.session_state.user['name'])
        email = st.text_input("Email Address", value=st.session_state.user['email'])
        phone = st.text_input("Phone Number", placeholder="+91 XXXXX XXXXX")

    with col2:
        city = st.text_input("City", placeholder="e.g., Delhi")
        state = st.text_input("State", placeholder="e.g., Delhi")
        bio = st.text_area("Bio", placeholder="Tell us about yourself", height=100)

    if st.button("💾 Save Changes", use_container_width=True):
        st.success("✅ Profile updated successfully!")

def show_statistics():
    """Show user statistics"""
    st.markdown("## Your Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Detections", "42")

    with col2:
        st.metric("Reports Generated", "8")

    with col3:
        st.metric("Days Active", "23")

    with col4:
        st.metric("Average Confidence", "92.1%")

    # Activity chart
    st.markdown("### Activity Summary")

    import plotly.graph_objects as go
    import pandas as pd

    dates = pd.date_range(start='2024-09-08', periods=7)
    activity = [5, 8, 6, 9, 7, 11, 6]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dates.strftime('%a'),
        y=activity,
        marker_color='#3b82f6'
    ))
    fig.update_layout(
        title="Weekly Detections",
        xaxis_title="Day",
        yaxis_title="Detections",
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

    # Leaderboard
    st.markdown("### Top Contributors")

    leaderboard = pd.DataFrame({
        'Rank': [1, 2, 3, 4, 5],
        'Name': ['Akshati', 'Anushka', 'Anamika', 'Anika', 'Ayushi'],
        'Detections': [156, 143, 127, 118, 105],
        'Reports': [32, 28, 24, 21, 19]
    })

    st.dataframe(leaderboard, use_container_width=True, hide_index=True)

def show_settings():
    """Show settings"""
    st.markdown("## Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Preferences")

        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        notifications = st.checkbox("Enable Notifications", value=True)
        email_updates = st.checkbox("Email Updates", value=True)
        marketing = st.checkbox("Marketing Emails", value=False)

    with col2:
        st.markdown("### Privacy")

        profile_visibility = st.selectbox("Profile Visibility", ["Public", "Private", "Friends Only"])
        data_sharing = st.selectbox("Data Sharing", ["Full", "Limited", "None"])
        analytics = st.checkbox("Allow Analytics", value=True)

    if st.button("💾 Save Preferences", use_container_width=True):
        st.success("✅ Preferences saved!")

def show_security():
    """Show security settings"""
    st.markdown("## Security")

    st.markdown("### Password")

    col1, col2 = st.columns(2)

    with col1:
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")

    with col2:
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("🔐 Change Password", use_container_width=True):
            if not all([current_password, new_password, confirm_password]):
                st.error("❌ Please fill all fields")
            elif new_password != confirm_password:
                st.error("❌ Passwords do not match")
            else:
                st.success("✅ Password changed successfully!")

    # Two-factor authentication
    st.markdown("### Two-Factor Authentication")

    if st.checkbox("Enable 2FA", value=False):
        st.info("📱 Scan QR code with your authenticator app:")
        st.image("https://via.placeholder.com/200", width=200)

        code = st.text_input("Enter 6-digit code:")

        if st.button("Verify 2FA"):
            if len(code) == 6 and code.isdigit():
                st.success("✅ 2FA enabled!")
            else:
                st.error("❌ Invalid code")

    # Active sessions
    st.markdown("### Active Sessions")

    sessions = pd.DataFrame({
        'Device': ['Chrome - Windows', 'Safari - iPhone', 'Edge - Windows'],
        'Last Active': ['Now', '2 hours ago', '1 day ago'],
        'Location': ['Delhi, India', 'Bangalore, India', 'Delhi, India']
    })

    st.dataframe(sessions, use_container_width=True, hide_index=True)

    if st.button("🚪 Logout All Other Sessions", use_container_width=True):
        st.warning("⚠️ Logged out all other sessions")
