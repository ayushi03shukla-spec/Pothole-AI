import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def show():
    """Display dashboard page"""
    st.markdown("# 📊 Dashboard")
    st.markdown("Welcome to Pothole AI Detection System")
    
    # User greeting
    if st.session_state.user:
        st.info(f"👋 Welcome, **{st.session_state.user['name']}**!")
    
    # Statistics Cards
    st.markdown("## 📈 Statistics Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔍 Total Detections",
            value="247",
            delta="↑ 12 today"
        )
    
    with col2:
        st.metric(
            label="⚠️ High Severity",
            value="45",
            delta="↑ 3 today"
        )
    
    with col3:
        st.metric(
            label="✅ Fixed Issues",
            value="189",
            delta="↑ 8 today"
        )
    
    with col4:
        st.metric(
            label="⏳ Pending",
            value="13",
            delta="↓ 2 today"
        )
    
    # Charts Row 1
    st.markdown("## 📊 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Detections by Severity")
        
        severity_data = {
            'Severity': ['Low', 'Medium', 'High'],
            'Count': [80, 122, 45]
        }
        df_severity = pd.DataFrame(severity_data)
        
        fig_severity = go.Figure(data=[
            go.Bar(x=df_severity['Severity'], y=df_severity['Count'],
                   marker_color=['#10b981', '#f59e0b', '#ef4444'])
        ])
        fig_severity.update_layout(
            title="Distribution by Severity",
            xaxis_title="Severity Level",
            yaxis_title="Number of Detections",
            height=400
        )
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        st.markdown("### Detections by Status")
        
        status_data = {
            'Status': ['Detected', 'Reported', 'Verified', 'Fixed'],
            'Count': [58, 78, 96, 15]
        }
        df_status = pd.DataFrame(status_data)
        
        fig_status = go.Figure(data=[
            go.Pie(
                labels=df_status['Status'],
                values=df_status['Count'],
                marker=dict(colors=['#3b82f6', '#8b5cf6', '#ec4899', '#10b981'])
            )
        ])
        fig_status.update_layout(height=400)
        st.plotly_chart(fig_status, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Weekly Trend")
        
        dates = pd.date_range(start='2024-09-08', periods=7)
        detections = [28, 35, 42, 38, 45, 52, 40]
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=dates.strftime('%a'),
            y=detections,
            mode='lines+markers',
            line=dict(color='#3b82f6', width=3),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.2)'
        ))
        fig_trend.update_layout(
            title="Detections Trend (Last 7 Days)",
            xaxis_title="Day",
            yaxis_title="Detections",
            height=400
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        st.markdown("### Confidence Distribution")
        
        confidence_data = {
            'Range': ['50-60%', '60-70%', '70-80%', '80-90%', '90-100%'],
            'Count': [12, 28, 64, 102, 41]
        }
        df_confidence = pd.DataFrame(confidence_data)
        
        fig_confidence = go.Figure(data=[
            go.Histogram(
                x=df_confidence['Range'],
                y=df_confidence['Count'],
                marker_color='#8b5cf6'
            )
        ])
        fig_confidence.update_layout(
            title="AI Model Confidence Levels",
            xaxis_title="Confidence Range",
            yaxis_title="Count",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_confidence, use_container_width=True)
    
    # Recent Detections Table
    st.markdown("## 🔍 Recent Detections")
    
    recent_data = {
        'ID': ['DT001', 'DT002', 'DT003', 'DT004', 'DT005'],
        'Location': ['Ring Road, Delhi', 'MG Road, Bangalore', 'Brigade Road, Bangalore', 
                     'Connaught Place, Delhi', 'Indiranagar, Bangalore'],
        'Severity': ['🔴 High', '🟡 Medium', '🟢 Low', '🟡 Medium', '🔴 High'],
        'Confidence': ['95.2%', '87.6%', '72.3%', '91.4%', '93.8%'],
        'Status': ['🔍 Detected', '📋 Reported', '✅ Verified', '🔧 Fixed', '🔍 Detected'],
        'Date': ['2024-09-14', '2024-09-13', '2024-09-13', '2024-09-12', '2024-09-12']
    }
    
    df_recent = pd.DataFrame(recent_data)
    st.dataframe(df_recent, use_container_width=True, hide_index=True)
    
    # Quick Actions
    st.markdown("## ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📸 Upload Image", use_container_width=True):
            st.session_state.page = "detection"
            st.rerun()
    
    with col2:
        if st.button("🗺️ View Map", use_container_width=True):
            st.session_state.page = "map"
            st.rerun()
    
    with col3:
        if st.button("📜 History", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()
    
    with col4:
        if st.button("📄 Generate Report", use_container_width=True):
            st.session_state.page = "reports"
            st.rerun()
    
    # System Health
    st.markdown("## 🏥 System Health")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("""
        **API Status**
        
        🟢 Healthy
        """)
    
    with col2:
        st.info("""
        **Database**
        
        🟢 Connected
        """)
    
    with col3:
        st.info("""
        **ML Model**
        
        🟢 Running
        """)
    
    with col4:
        st.info("""
        **Uptime**
        
        99.8% (47 days)
        """)
