"""
utils/mock_detector.py

★★★ THIS IS THE ONE FILE AYUSHI REPLACES IN PHASE 3 (Days 11-15) ★★★

Per the execution plan: Anika builds the backend using sample JSON /
dummy predictions during Phase 2 (Days 6-10) while Ayushi trains
YOLOv8 in parallel. When best.pt is ready, ONLY this file changes —
every route, database table, and frontend API contract stays identical.

--------------------------------------------------------------------
CURRENT STATE (Phase 2): returns realistic fake detections.
FUTURE STATE (Phase 3):  loads best.pt and runs real inference.
--------------------------------------------------------------------

Real version will look like this (Ayushi fills this in):

    from ultralytics import YOLO
    model = YOLO("models/best.pt")

    def run_detection(file_path: str) -> list[dict]:
        results = model(file_path)
        detections = []
        for box in results[0].boxes:
            x_min, y_min, x_max, y_max = box.xyxy[0].tolist()
            detections.append({
                "x_min": x_min, "y_min": y_min,
                "x_max": x_max, "y_max": y_max,
                "confidence": float(box.conf[0]),
            })
        return detections

The output SHAPE (list of dicts with x_min/y_min/x_max/y_max/confidence)
is the contract the rest of the backend depends on — keep it identical.
"""

import random


def run_detection(file_path: str) -> list:
    """
    Simulates a YOLOv8 pothole detection pass on an uploaded file.
    Returns a list of bounding boxes with confidence scores, exactly the
    shape the real model will return.
    """
    num_detections = random.randint(0, 4)
    detections = []

    for _ in range(num_detections):
        x_min = random.uniform(0, 500)
        y_min = random.uniform(0, 300)
        width = random.uniform(40, 180)
        height = random.uniform(30, 140)

        detections.append({
            "x_min": round(x_min, 2),
            "y_min": round(y_min, 2),
            "x_max": round(x_min + width, 2),
            "y_max": round(y_min + height, 2),
            "confidence": round(random.uniform(0.55, 0.98), 2),
        })

    return detections


def compute_severity(size: float) -> str:
    """
    Converts a bounding-box pixel area into a severity label.
    Thresholds are placeholders — Ayushi/Anushka can tune these once
    real-world box sizes are validated against actual pothole depth/size.
    """
    if size < 3000:
        return "low"
    elif size < 9000:
        return "medium"
    return "high"


def overall_severity(pothole_severities: list) -> str:
    """Detection-level severity = worst pothole found in that scan."""
    if not pothole_severities:
        return "none"
    order = {"low": 1, "medium": 2, "high": 3}
    return max(pothole_severities, key=lambda s: order.get(s, 0))
