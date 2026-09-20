from pathlib import Path
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "best.pt"

_model = None


def get_model():
    global _model

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"YOLO model not found at: {MODEL_PATH}"
            )

        _model = YOLO(str(MODEL_PATH))

    return _model


def run_detection(file_path, confidence=0.50):
    model = get_model()

    results = model.predict(
        source=str(file_path),
        conf=confidence,
        iou=0.50,
        device="cpu",
        verbose=False,
    )

    result = results[0]
    detections = []

    if result.boxes is None:
        return detections

    for box in result.boxes:
        coordinates = box.xyxy[0].tolist()
        conf = float(box.conf[0])

        x_min, y_min, x_max, y_max = coordinates

        detections.append({
            "x_min": float(x_min),
            "y_min": float(y_min),
            "x_max": float(x_max),
            "y_max": float(y_max),
            "confidence": conf,
        })

    return detections