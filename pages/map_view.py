import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np

def show():
    """Display map view page"""
    st.markdown("# 🗺️ Pothole Locations Map")
    
    # Sidebar filters
    st.sidebar.markdown("### 🔍 Filters")
    
    severity_filter = st.sidebar.multiselect(
        "Severity",
        ["🔴 High", "🟡 Medium", "🟢 Low"],
        default=["🔴 High", "🟡 Medium", "🟢 Low"]
    )
    
    status_filter = st.sidebar.multiselect(
        "Status",
        ["🔍 Detected", "📋 Reported", "✅ Verified", "🔧 Fixed"],
        default=["🔍 Detected", "📋 Reported", "✅ Verified"]
    )
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=[pd.Timestamp('2024-09-01'), pd.Timestamp('2024-09-14')]
    )
    
    # Sample data
    potholes_data = {
        'name': ['Pothole 1', 'Pothole 2', 'Pothole 3', 'Pothole 4', 'Pothole 5'],
        'latitude': [28.7041, 28.7024, 28.7055, 28.7010, 28.7050],
        'longitude': [77.1025, 77.1035, 77.1015, 77.1045, 77.1005],
        'severity': ['🔴 High', '🟡 Medium', '🟢 Low', '🔴 High', '🟡 Medium'],
        'status': ['🔍 Detected', '📋 Reported', '✅ Verified', '🔧 Fixed', '🔍 Detected'],
        'confidence': [95.2, 87.6, 72.3, 91.4, 88.9],
        'size': ['Large', 'Medium', 'Small', 'Large', 'Medium']
    }
    
    df_potholes = pd.DataFrame(potholes_data)
    
    # Create map
    center_lat = 28.7041
    center_lon = 77.1025
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,
        tiles="OpenStreetMap"
    )
    
    # Add markers for each pothole
    severity_colors = {
        '🔴 High': 'red',
        '🟡 Medium': 'orange',
        '🟢 Low': 'green'
    }
    
    for idx, row in df_potholes.iterrows():
        color = severity_colors.get(row['severity'], 'blue')
        
        popup_text = f"""
        <b>{row['name']}</b><br>
        Severity: {row['severity']}<br>
        Status: {row['status']}<br>
        Confidence: {row['confidence']}%<br>
        Size: {row['size']}<br>
        Location: ({row['latitude']:.4f}, {row['longitude']:.4f})
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=8,
            popup=folium.Popup(popup_text, max_width=250),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    # Display map
    st_folium(m, width=1400, height=600)
    
    # Statistics
    st.markdown("## 📊 Map Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Potholes", len(df_potholes))
    
    with col2:
        high_severity = len(df_potholes[df_potholes['severity'] == '🔴 High'])
        st.metric("High Severity", high_severity)
    
    with col3:
        avg_confidence = df_potholes['confidence'].mean()
        st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
    
    with col4:
        fixed_count = len(df_potholes[df_potholes['status'] == '🔧 Fixed'])
        st.metric("Fixed", fixed_count)
    
    # Detailed list
    st.markdown("## 📋 Pothole Details")
    
    # Format data for display
    display_data = df_potholes.copy()
    display_data['Latitude'] = display_data['latitude'].round(4)
    display_data['Longitude'] = display_data['longitude'].round(4)
    display_data['Confidence'] = display_data['confidence'].apply(lambda x: f"{x}%")
    
    display_columns = ['name', 'severity', 'status', 'Confidence', 'size', 'Latitude', 'Longitude']
    st.dataframe(
        display_data[display_columns].rename(columns={'name': 'Pothole'}),
        use_container_width=True,
        hide_index=True
    )
    
    # Cluster heatmap
    st.markdown("## 🔥 Density Heatmap")
    
    # Create heatmap
    m_heat = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,
        tiles="OpenStreetMap"
    )
    
    # Add heat layer
    from folium.plugins import HeatMap
    
    heat_data = [[row['latitude'], row['longitude'], row['confidence']/100] 
                 for idx, row in df_potholes.iterrows()]
    
    HeatMap(heat_data).add_to(m_heat)
    
    st_folium(m_heat, width=1400, height=500)
    
    # Export options
    st.markdown("## 💾 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export as CSV", use_container_width=True):
            csv = df_potholes.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "potholes.csv",
                "text/csv"
            )
    
    with col2:
        if st.button("📊 Export as JSON", use_container_width=True):
            import json
            json_str = df_potholes.to_json()
            st.download_button(
                "Download JSON",
                json_str,
                "potholes.json",
                "application/json"
            )
    
    with col3:
        if st.button("🗺️ Export Map", use_container_width=True):
            m.save('pothole_map.html')
            st.success("Map saved as pothole_map.html")
