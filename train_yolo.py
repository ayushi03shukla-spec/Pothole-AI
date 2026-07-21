from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="Pothole Detection.v9i.yolov8/data.yaml",
    epochs=3,
    imgsz=320,
    batch=2,
    workers=0,
    device="cpu"
)

print("Training Complete!")