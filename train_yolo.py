from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model.train(
    data="dataset/data.yaml",
    epochs=3,
    imgsz=320,
    batch=2,
    workers=0,
    device="cpu",
    project="runs",
    name="pothole_yolo_test"
)

print("Training test completed.")
