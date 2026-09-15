import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show():
    """Display admin dashboard"""
    st.markdown("# ⚙️ Admin Dashboard")

    # Check admin access
    if st.session_state.user and st.session_state.user.get('role') != 'admin':
        st.warning("⚠️ Admin access required")
        return

    # Tabs
    tab_overview, tab_users, tab_system, tab_logs = st.tabs(
        ["📊 Overview", "👥 Users", "🔧 System", "📋 Logs"]
    )

    with tab_overview:
        show_overview()

    with tab_users:
        show_users()

    with tab_system:
        show_system()

    with tab_logs:
        show_logs()

def show_overview():
    """Show admin overview"""
    st.markdown("## System Overview")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Users", "156")

    with col2:
        st.metric("Total Detections", "2,347")

    with col3:
        st.metric("Total Reports", "89")

    with col4:
        st.metric("System Uptime", "99.8%")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### User Growth")

        import pandas as pd
        dates = pd.date_range(start='2024-09-01', end='2024-09-14', freq='D')
        users = [50, 58, 65, 72, 81, 92, 103, 115, 127, 138, 147, 152, 155, 156]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates.strftime('%m-%d'),
            y=users,
            mode='lines+markers',
            line=dict(color='#10b981'),
            fill='tozeroy'
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### API Usage")

        endpoints = ['Detection', 'Map', 'Reports', 'Auth', 'Profile']
        calls = [1250, 890, 450, 1100, 320]

        fig = go.Figure(data=[
            go.Bar(x=endpoints, y=calls, marker_color='#3b82f6')
        ])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def show_users():
    """Show user management"""
    st.markdown("## User Management")

    # Search and filter
    col1, col2, col3 = st.columns(3)

    with col1:
        search = st.text_input("Search users...", placeholder="Name or email")

    with col2:
        role_filter = st.selectbox("Filter by role", ["All", "Admin", "User", "Moderator"])

    with col3:
        status_filter = st.selectbox("Filter by status", ["All", "Active", "Inactive", "Banned"])

    # User list
    users = pd.DataFrame({
        'ID': [f'U{i:03d}' for i in range(1, 11)],
        'Name': ['Akshati', 'Anushka', 'Anamika', 'Anika', 'Ayushi',
                'Prashant', 'User 7', 'User 8', 'User 9', 'User 10'],
        'Email': [f'user{i}@pothole.ai' for i in range(1, 11)],
        'Role': ['Admin', 'Moderator', 'User', 'User', 'User', 'Admin', 'User', 'User', 'User', 'User'],
        'Status': ['🟢 Active', '🟢 Active', '🟢 Active', '🟢 Active', '🟡 Inactive',
                  '🟢 Active', '🟢 Active', '🟢 Active', '🔴 Banned', '🟢 Active'],
        'Joined': ['2024-08-15', '2024-08-18', '2024-08-20', '2024-08-22', '2024-08-25',
                  '2024-08-16', '2024-08-28', '2024-09-01', '2024-09-02', '2024-09-05']
    })

    # Display with actions
    for idx, user in users.iterrows():
        with st.expander(f"👤 {user['Name']} | {user['Email']} | {user['Status']}"):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.write(f"**ID:** {user['ID']}")
                st.write(f"**Role:** {user['Role']}")

            with col2:
                st.write(f"**Status:** {user['Status']}")
                st.write(f"**Joined:** {user['Joined']}")

            with col3:
                if st.button("✏️ Edit", key=f"edit_{idx}"):
                    st.info("Edit user details...")

            with col4:
                if st.button("🗑️ Delete", key=f"delete_{idx}"):
                    st.warning(f"Deleted {user['Name']}")

def show_system():
    """Show system management"""
    st.markdown("## System Management")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### System Status")

        status_info = {
            'API Server': '🟢 Running',
            'Database': '🟢 Connected',
            'ML Model': '🟢 Active',
            'Cache': '🟢 Enabled',
            'Backup': '🟢 Scheduled'
        }

        for service, status in status_info.items():
            st.write(f"{service}: {status}")

    with col2:
        st.markdown("### System Resources")

        import plotly.graph_objects as go

        fig = go.Figure(data=[
            go.Indicator(
                mode="gauge+number",
                value=65,
                title="CPU Usage",
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={'axis': {'range': [0, 100]},
                       'bar': {'color': "darkblue"}}
            )
        ])
        st.plotly_chart(fig, use_container_width=True)

    # Maintenance
    st.markdown("### Maintenance")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Restart API", use_container_width=True):
            st.warning("⚠️ API restarting...")
            st.success("✅ API restarted")

    with col2:
        if st.button("💾 Backup Database", use_container_width=True):
            st.info("📦 Backup in progress...")
            st.success("✅ Backup completed")

    with col3:
        if st.button("🧹 Clear Cache", use_container_width=True):
            st.warning("🗑️ Clearing cache...")
            st.success("✅ Cache cleared")

    # Database info
    st.markdown("### Database Information")

    db_stats = pd.DataFrame({
        'Table': ['users', 'detections', 'reports', 'locations', 'logs'],
        'Records': [156, 2347, 89, 1203, 45678],
        'Size': ['2.4 MB', '524 MB', '23.5 MB', '156 MB', '189 MB']
    })

    st.dataframe(db_stats, use_container_width=True, hide_index=True)

def show_logs():
    """Show system logs"""
    st.markdown("## System Logs")

    # Filter logs
    log_level = st.selectbox("Log Level", ["All", "Error", "Warning", "Info"])

    # Sample logs
    logs = [
        ("2024-09-14 14:30:45", "INFO", "User logged in", "Anamika"),
        ("2024-09-14 14:25:12", "INFO", "Report generated", "DT001-RPT"),
        ("2024-09-14 14:20:33", "WARNING", "High API usage detected", "Detection API"),
        ("2024-09-14 14:15:01", "INFO", "Database backup completed", "DB-AUTO-001"),
        ("2024-09-14 14:10:45", "ERROR", "ML model timeout", "YOLOv8"),
        ("2024-09-14 14:05:22", "INFO", "User registered", "newuser@test.com"),
        ("2024-09-14 14:00:10", "WARNING", "Low disk space", "95% used"),
        ("2024-09-14 13:55:33", "INFO", "Cache cleared", "Cache Manager"),
    ]

    # Display logs
    for timestamp, level, message, details in logs:
        level_emoji = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌"}
        st.write(f"{level_emoji.get(level, '📝')} {timestamp} | {level} | {message} | {details}")

    # Export logs
    if st.button("📥 Export Logs", use_container_width=True):
        log_data = "\n".join([f"{t} | {l} | {m} | {d}" for t, l, m, d in logs])
        st.download_button(
            "Download Logs",
            log_data,
            "system_logs.txt",
            "text/plain"
        )
