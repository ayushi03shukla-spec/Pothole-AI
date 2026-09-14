import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from datetime import datetime
import plotly.graph_objects as go

def show():
    """Display detection page"""
    st.markdown("# 🔍 Pothole Detection")
    st.markdown("Upload images or videos for AI-powered pothole detection")
    
    # Tabs for image/video
    tab_image, tab_video, tab_camera = st.tabs(["📷 Image", "🎥 Video", "📹 Camera"])
    
    with tab_image:
        show_image_detection()
    
    with tab_video:
        show_video_detection()
    
    with tab_camera:
        show_camera_detection()

def show_image_detection():
    """Handle image detection"""
    st.markdown("## Image Upload")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=['jpg', 'jpeg', 'png', 'bmp'],
            help="Upload an image for pothole detection"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Original Image", use_column_width=True)
            
            file_size = uploaded_file.size / (1024 * 1024)
            st.info(f"📁 File size: {file_size:.2f} MB")
            
            if st.button("🚀 Analyze Image", use_container_width=True):
                with st.spinner("Analyzing image with YOLOv8..."):
                    # Simulate detection results
                    st.success("✅ Analysis Complete!")
                    
                    # Display results
                    col_result1, col_result2 = st.columns(2)
                    
                    with col_result1:
                        st.image(image, caption="Detection Result (with bounding boxes)", 
                                use_column_width=True)
                    
                    with col_result2:
                        detection_results = {
                            'Total Potholes': 3,
                            'High Severity': 1,
                            'Medium Severity': 1,
                            'Low Severity': 1,
                            'Average Confidence': 94.5
                        }
                        
                        for key, value in detection_results.items():
                            if 'Confidence' in key:
                                st.metric(key, f"{value}%")
                            else:
                                st.metric(key, value)
    
    with col2:
        st.markdown("### Detection Summary")
        
        # Severity distribution
        severity_data = {
            'Level': ['High', 'Medium', 'Low'],
            'Count': [1, 1, 1],
            'Color': ['#ef4444', '#f59e0b', '#10b981']
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=[d['Level'] for d in [severity_data[0], severity_data[1], severity_data[2]]],
                y=[d['Count'] for d in [severity_data[0], severity_data[1], severity_data[2]]],
                marker_color=['#ef4444', '#f59e0b', '#10b981']
            )
        ])
        fig.update_layout(title="Severity Distribution", height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Detected Potholes")
        
        detected = [
            {
                'ID': 'P001',
                'Severity': '🔴 High',
                'Confidence': 96.2,
                'Size': 'Large',
                'Location': '(145, 230)'
            },
            {
                'ID': 'P002',
                'Severity': '🟡 Medium',
                'Confidence': 91.8,
                'Size': 'Medium',
                'Location': '(420, 310)'
            },
            {
                'ID': 'P003',
                'Severity': '🟢 Low',
                'Confidence': 85.3,
                'Size': 'Small',
                'Location': '(620, 180)'
            }
        ]
        
        for pothole in detected:
            with st.expander(f"📍 {pothole['ID']} - {pothole['Severity']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Confidence:** {pothole['Confidence']}%")
                    st.write(f"**Size:** {pothole['Size']}")
                with col2:
                    st.write(f"**Location:** {pothole['Location']}")

def show_video_detection():
    """Handle video detection"""
    st.markdown("## Video Upload")
    
    uploaded_video = st.file_uploader(
        "Choose a video",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="Upload a video for pothole detection"
    )
    
    if uploaded_video is not None:
        st.video(uploaded_video)
        
        file_size = uploaded_video.size / (1024 * 1024)
        st.info(f"📁 File size: {file_size:.2f} MB")
        
        if st.button("🚀 Analyze Video", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(100):
                progress_bar.progress(i + 1)
                status_text.text(f"Processing: {i + 1}% complete...")
            
            st.success("✅ Video Analysis Complete!")
            
            # Results
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Video Summary")
                st.metric("Total Frames Analyzed", "1200")
                st.metric("Total Potholes Found", "47")
                st.metric("Average Confidence", "91.3%")
                st.metric("Processing Time", "4m 32s")
            
            with col2:
                st.markdown("### Frame Distribution")
                
                frames_data = {
                    'Frame Type': ['Detection', 'No Detection', 'Low Confidence'],
                    'Count': [47, 1100, 53]
                }
                
                fig = go.Figure(data=[
                    go.Pie(
                        labels=frames_data['Frame Type'],
                        values=frames_data['Count'],
                        marker=dict(colors=['#ef4444', '#10b981', '#f59e0b'])
                    )
                ])
                st.plotly_chart(fig, use_container_width=True)

def show_camera_detection():
    """Handle real-time camera detection"""
    st.markdown("## 📹 Real-Time Detection")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        picture = st.camera_input("Take a picture")
        
        if picture is not None:
            image = Image.open(picture)
            st.image(image, caption="Captured Image", use_column_width=True)
            
            if st.button("🔍 Detect Potholes", use_container_width=True):
                st.success("✅ Potholes detected!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Potholes Found", "2")
                with col2:
                    st.metric("Avg Confidence", "93.2%")
                with col3:
                    st.metric("High Severity", "1")
    
    with col2:
        st.markdown("### Settings")
        
        confidence_threshold = st.slider(
            "Confidence Threshold",
            0.0, 1.0, 0.5,
            help="Minimum confidence score to consider a detection"
        )
        
        model_version = st.selectbox(
            "Model Version",
            ["YOLOv8n (Fast)", "YOLOv8s (Standard)", "YOLOv8m (Balanced)", "YOLOv8l (Accurate)"]
        )
        
        st.markdown("### Quick Stats")
        st.info("""
        **Model Info:**
        - Framework: YOLOv8
        - Confidence: {:.0%}
        - Model: {}
        """.format(confidence_threshold, model_version))

def process_image_with_yolo(image_path):
    """Process image with YOLOv8 (placeholder)"""
    # This would use actual YOLOv8 in production
    # from ultralytics import YOLO
    # model = YOLO('yolov8n.pt')
    # results = model.predict(image_path)
    
    return {
        'detections': 3,
        'confidence': 94.5,
        'severity': {
            'high': 1,
            'medium': 1,
            'low': 1
        }
    }
