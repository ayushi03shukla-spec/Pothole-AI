from pathlib import Path
from ultralytics import YOLO

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "best.pt"

_model = None


def get_model():
    global _model

    if _model is None:
        _model = YOLO(str(MODEL_PATH))

    return _model


def detect_image(image, confidence=0.25):
    model = get_model()

    results = model.predict(
        source=image,
        conf=confidence,
        device="cpu",
        verbose=False
    )

    return results[0]
