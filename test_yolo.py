from ultralytics import YOLO

model = YOLO("models/best.pt")

results = model("road.jpg", save=True)

print("Detection completed!")