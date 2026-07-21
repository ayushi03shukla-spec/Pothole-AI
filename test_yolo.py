from ultralytics import YOLO

model = YOLO("runs/detect/train-4/weights/best.pt")

results = model("road.jpg", save=True)

print("Detection completed!")