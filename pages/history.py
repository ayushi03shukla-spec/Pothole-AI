import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def show():
    """Display detection history page"""
    st.markdown("# 📜 Detection History")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        severity_filter = st.multiselect(
            "Severity",
            ["🔴 High", "🟡 Medium", "🟢 Low"],
            default=["🔴 High", "🟡 Medium", "🟢 Low"],
            key="severity_hist"
        )
    
    with col2:
        status_filter = st.multiselect(
            "Status",
            ["🔍 Detected", "📋 Reported", "✅ Verified", "🔧 Fixed"],
            default=["🔍 Detected", "📋 Reported", "✅ Verified"],
            key="status_hist"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["Date (Newest)", "Date (Oldest)", "Confidence", "Severity"]
        )
    
    with col4:
        items_per_page = st.selectbox(
            "Items per page",
            [10, 25, 50, 100]
        )
    
    # Generate sample data
    detections = generate_detection_data(100)
    df = pd.DataFrame(detections)
    
    # Apply filters
    df_filtered = df.copy()
    
    if severity_filter:
        df_filtered = df_filtered[df_filtered['Severity'].isin(severity_filter)]
    
    if status_filter:
        df_filtered = df_filtered[df_filtered['Status'].isin(status_filter)]
    
    # Sort
    if sort_by == "Date (Newest)":
        df_filtered = df_filtered.sort_values('Date', ascending=False)
    elif sort_by == "Date (Oldest)":
        df_filtered = df_filtered.sort_values('Date', ascending=True)
    elif sort_by == "Confidence":
        df_filtered = df_filtered.sort_values('Confidence', ascending=False)
    elif sort_by == "Severity":
        severity_order = {"🔴 High": 3, "🟡 Medium": 2, "🟢 Low": 1}
        df_filtered['severity_order'] = df_filtered['Severity'].map(severity_order)
        df_filtered = df_filtered.sort_values('severity_order', ascending=False)
        df_filtered = df_filtered.drop('severity_order', axis=1)
    
    # Pagination
    total_records = len(df_filtered)
    total_pages = (total_records + items_per_page - 1) // items_per_page
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown(f"**Total Records:** {total_records}")
    
    with col2:
        page = st.select_slider(
            "Page",
            options=range(1, total_pages + 1),
            value=1
        )
    
    with col3:
        st.markdown(f"**Page {page} of {total_pages}**")
    
    # Display records
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    df_page = df_filtered.iloc[start_idx:end_idx]
    
    # Display as expandable items
    for idx, row in df_page.iterrows():
        with st.expander(f"🔍 {row['ID']} | {row['Location']} | {row['Severity']} | {row['Date']}"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**Severity:** {row['Severity']}")
                st.write(f"**Status:** {row['Status']}")
            
            with col2:
                st.write(f"**Confidence:** {row['Confidence']}%")
                st.write(f"**Size:** {row['Size']}")
            
            with col3:
                st.write(f"**Location:** {row['Location']}")
                st.write(f"**Date:** {row['Date']}")
            
            with col4:
                col_delete, col_edit = st.columns(2)
                with col_delete:
                    if st.button("🗑️ Delete", key=f"delete_{idx}"):
                        st.success(f"Deleted {row['ID']}")
                
                with col_edit:
                    if st.button("✏️ Edit", key=f"edit_{idx}"):
                        st.info("Edit functionality available")
    
    # Summary statistics
    st.markdown("## 📊 Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Filtered", len(df_filtered))
    
    with col2:
        avg_confidence = df_filtered['Confidence'].mean()
        st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
    
    with col3:
        high_count = len(df_filtered[df_filtered['Severity'] == '🔴 High'])
        st.metric("High Severity", high_count)
    
    with col4:
        fixed_count = len(df_filtered[df_filtered['Status'] == '🔧 Fixed'])
        st.metric("Fixed", fixed_count)
    
    # Export options
    st.markdown("## 💾 Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export as CSV", use_container_width=True):
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                f"detections_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
    
    with col2:
        if st.button("📊 Export as JSON", use_container_width=True):
            import json
            json_str = df_filtered.to_json(orient='records', indent=2)
            st.download_button(
                "Download JSON",
                json_str,
                f"detections_{datetime.now().strftime('%Y%m%d')}.json",
                "application/json"
            )
    
    with col3:
        if st.button("📄 Export as PDF", use_container_width=True):
            st.info("PDF export feature coming soon")

def generate_detection_data(count=100):
    """Generate sample detection data"""
    import random
    
    locations = [
        'Ring Road, Delhi',
        'MG Road, Bangalore',
        'Brigade Road, Bangalore',
        'Connaught Place, Delhi',
        'Indiranagar, Bangalore',
        'Rajpath, Delhi',
        'M.G. Road Extension, Bangalore',
        'Nehru Place, Delhi',
        'St. Mark\'s Road, Bangalore'
    ]
    
    severities = ['🔴 High', '🟡 Medium', '🟢 Low']
    statuses = ['🔍 Detected', '📋 Reported', '✅ Verified', '🔧 Fixed']
    
    data = []
    for i in range(count):
        data.append({
            'ID': f'DT{i+1:05d}',
            'Location': random.choice(locations),
            'Severity': random.choice(severities),
            'Status': random.choice(statuses),
            'Confidence': round(random.uniform(70, 99), 1),
            'Size': random.choice(['Small', 'Medium', 'Large']),
            'Date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
        })
    
    return data
