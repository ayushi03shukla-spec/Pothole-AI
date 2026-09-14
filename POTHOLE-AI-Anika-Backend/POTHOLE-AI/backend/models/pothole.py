"""
models/pothole.py
Potholes table — each row is ONE bounding box found inside a Detection.
A single image can contain multiple potholes, so this is a child table.

Matches the whiteboard ER diagram:
id (PK), detection_id (FK), size, x_min, y_min, x_max, y_max, width,
height, severity
"""

from extensions import db


class Pothole(db.Model):
    __tablename__ = "potholes"

    id = db.Column(db.Integer, primary_key=True)
    detection_id = db.Column(db.Integer, db.ForeignKey("detections.id"), nullable=False)

    # Bounding box coordinates (pixels), as returned by YOLOv8
    x_min = db.Column(db.Float, nullable=False)
    y_min = db.Column(db.Float, nullable=False)
    x_max = db.Column(db.Float, nullable=False)
    y_max = db.Column(db.Float, nullable=False)

    width = db.Column(db.Float, nullable=True)   # x_max - x_min
    height = db.Column(db.Float, nullable=True)  # y_max - y_min
    size = db.Column(db.Float, nullable=True)     # width * height, used for severity calc

    confidence = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(20), nullable=True)  # 'low' | 'medium' | 'high'

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "detection_id": self.detection_id,
            "bbox": {
                "x_min": self.x_min,
                "y_min": self.y_min,
                "x_max": self.x_max,
                "y_max": self.y_max,
            },
            "width": self.width,
            "height": self.height,
            "size": self.size,
            "confidence": self.confidence,
            "severity": self.severity,
        }

    def __repr__(self):
        return f"<Pothole {self.id} detection={self.detection_id} severity={self.severity}>"
