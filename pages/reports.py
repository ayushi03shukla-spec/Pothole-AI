import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

def show():
    """Display reports page"""
    st.markdown("# 📄 Reports")
    
    # Tabs for different views
    tab_generate, tab_view, tab_manage = st.tabs(["📋 Generate", "👁️ View", "🗂️ Manage"])
    
    with tab_generate:
        show_generate_report()
    
    with tab_view:
        show_view_reports()
    
    with tab_manage:
        show_manage_reports()

def show_generate_report():
    """Generate new report"""
    st.markdown("## Generate New Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_title = st.text_input(
            "Report Title",
            placeholder="e.g., Weekly Detection Summary"
        )
        
        report_type = st.selectbox(
            "Report Type",
            ["Summary", "Detailed", "Statistical Analysis", "Trend Analysis"]
        )
        
        date_range = st.date_input(
            "Date Range",
            value=[
                datetime.now() - timedelta(days=7),
                datetime.now()
            ]
        )
        
        include_options = st.multiselect(
            "Include in Report",
            ["Statistics", "Charts", "Map Data", "Severity Analysis", "Trend Data"],
            default=["Statistics", "Charts", "Severity Analysis"]
        )
    
    with col2:
        st.markdown("### Report Settings")
        
        format_type = st.radio(
            "Export Format",
            ["PDF", "CSV", "JSON", "Excel"]
        )
        
        include_images = st.checkbox("Include Detection Images", value=True)
        include_map = st.checkbox("Include Map", value=True)
        include_recommendations = st.checkbox("Include Recommendations", value=True)
        
        st.markdown("### Preview")
        st.info("""
        **Report Summary:**
        - Title: {title}
        - Type: {type}
        - Date Range: {date_start} to {date_end}
        - Format: {format}
        """.format(
            title=report_title or "Untitled",
            type=report_type,
            date_start=date_range[0] if date_range else "N/A",
            date_end=date_range[1] if date_range else "N/A",
            format=format_type
        ))
    
    # Generate button
    if st.button("🚀 Generate Report", use_container_width=True, key="generate_btn"):
        with st.spinner("Generating report..."):
            # Simulate generation
            import time
            progress_bar = st.progress(0)
            
            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.01)
            
            st.success("✅ Report generated successfully!")
            
            # Show preview
            st.markdown("## Report Preview")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                show_report_preview(report_title, report_type)
            
            with col2:
                st.markdown("### Download Options")
                
                # Generate sample data for download
                sample_data = {
                    'Date': [datetime.now() - timedelta(days=i) for i in range(7)],
                    'Detections': [25, 32, 28, 35, 42, 38, 45],
                    'High_Severity': [5, 8, 6, 9, 12, 10, 14]
                }
                df = pd.DataFrame(sample_data)
                
                if format_type == "CSV":
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        f"{report_title or 'report'}_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                
                elif format_type == "JSON":
                    import json
                    json_str = df.to_json(orient='records', indent=2)
                    st.download_button(
                        "📥 Download JSON",
                        json_str,
                        f"{report_title or 'report'}_{datetime.now().strftime('%Y%m%d')}.json",
                        "application/json",
                        use_container_width=True
                    )
                
                elif format_type == "PDF":
                    st.info("📄 PDF generation available after downloading")

def show_report_preview(title, report_type):
    """Show report preview"""
    st.markdown(f"### {title or 'Report'}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Key Metrics")
        
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Total Detections", "247")
            st.metric("Avg Confidence", "91.3%")
        
        with metric_col2:
            st.metric("High Severity", "45")
            st.metric("Fixed Issues", "189")
    
    with col2:
        st.markdown("#### Trend")
        
        dates = pd.date_range(start='2024-09-08', periods=7)
        detections = [28, 35, 42, 38, 45, 52, 40]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates.strftime('%a'),
            y=detections,
            mode='lines+markers',
            line=dict(color='#3b82f6'),
            fill='tozeroy'
        ))
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    # Severity distribution
    st.markdown("#### Severity Distribution")
    
    severity_data = {
        'Level': ['High', 'Medium', 'Low'],
        'Count': [45, 122, 80]
    }
    
    fig_sev = go.Figure(data=[
        go.Bar(
            x=severity_data['Level'],
            y=severity_data['Count'],
            marker_color=['#ef4444', '#f59e0b', '#10b981']
        )
    ])
    fig_sev.update_layout(height=300)
    st.plotly_chart(fig_sev, use_container_width=True)

def show_view_reports():
    """View existing reports"""
    st.markdown("## View Reports")
    
    # Sample reports
    reports = [
        {
            'name': 'Weekly Report - Sept 8-14',
            'type': 'Summary',
            'date': '2024-09-14',
            'status': '✅ Complete',
            'size': '2.4 MB'
        },
        {
            'name': 'Monthly Analysis - September',
            'type': 'Statistical',
            'date': '2024-09-10',
            'status': '✅ Complete',
            'size': '5.2 MB'
        },
        {
            'name': 'High Severity Pothole Report',
            'type': 'Detailed',
            'date': '2024-09-12',
            'status': '✅ Complete',
            'size': '3.8 MB'
        }
    ]
    
    for report in reports:
        with st.expander(f"📄 {report['name']} | {report['date']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Type:** {report['type']}")
                st.write(f"**Status:** {report['status']}")
            
            with col2:
                st.write(f"**Created:** {report['date']}")
                st.write(f"**Size:** {report['size']}")
            
            with col3:
                st.markdown("**Actions:**")
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if st.button("👁️", key=f"view_{report['name']}"):
                        st.success("Opening report...")
                
                with col_b:
                    if st.button("📥", key=f"download_{report['name']}"):
                        st.info("Download started...")
                
                with col_c:
                    if st.button("🗑️", key=f"delete_{report['name']}"):
                        st.warning("Report deleted")

def show_manage_reports():
    """Manage reports"""
    st.markdown("## Manage Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Storage Usage")
        st.progress(0.65)
        st.write("**65%** - 6.5 GB / 10 GB used")
    
    with col2:
        st.markdown("### Recent Activity")
        activity = [
            "Report generated: Weekly Summary",
            "Report downloaded: Monthly Analysis",
            "Report deleted: Old Report",
            "Report shared: Team Report"
        ]
        for item in activity:
            st.caption(f"✓ {item}")
    
    # Cleanup options
    st.markdown("### Cleanup Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Delete Old Reports (>30 days)", use_container_width=True):
            st.warning("Deleted 3 reports, freed 2.1 GB")
    
    with col2:
        if st.button("📦 Archive Reports (>90 days)", use_container_width=True):
            st.success("Archived 5 reports, freed 3.2 GB")
    
    st.markdown("### Export All Reports")
    if st.button("📦 Download as ZIP", use_container_width=True):
        st.info("Preparing all reports for download...")
        st.success("Ready for download!")
