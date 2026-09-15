from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model.train(
    data="dataset/data.yaml",
    epochs=30,
    imgsz=320,
    batch=2,
    workers=0,
    device="cpu",
    project="runs/detect",
    name="pothole_yolo_final",
    patience=10,
    pretrained=True,
    save=True,
    plots=True
)

print("Final training completed.")
