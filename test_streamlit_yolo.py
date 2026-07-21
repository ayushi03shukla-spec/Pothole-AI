from ultralytics import YOLO
import streamlit as st
from PIL import Image

model = YOLO("runs/detect/train-4/weights/best.pt")

st.title("Pothole Detection using YOLOv8")

uploaded_file = st.file_uploader(
    "Upload Road Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    results = model(image)

    annotated_image = results[0].plot()

    st.image(
        annotated_image,
        caption="Detected Potholes",
        use_container_width=True
    )

    detections = len(results[0].boxes)

    st.success(
        f"Potholes Detected: {detections}"
    )