"""
models/detection.py
Detections table — one row per uploaded image/video scan.
Matches the whiteboard ER diagram:
id (PK), user_id (FK), image_path, video_path, longitude, latitude,
detected_at, confidence, severity

This is the record Anamika's dashboard lists, Prashant's map pins, and
the CSV/PDF reports export.
"""

from datetime import datetime
from extensions import db


class Detection(db.Model):
    __tablename__ = "detections"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    image_path = db.Column(db.String(255), nullable=True)
    video_path = db.Column(db.String(255), nullable=True)

    # Location — filled in by frontend (GPS/geolocation) or map click (Prashant's module)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # Aggregate result fields (top-level summary of this scan)
    confidence = db.Column(db.Float, nullable=True)       # highest/average confidence found
    severity = db.Column(db.String(20), nullable=True)     # 'low' | 'medium' | 'high'
    pothole_count = db.Column(db.Integer, default=0)

    status = db.Column(db.String(20), default="pending")   # pending | processed | failed

    detected_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One detection -> many pothole bounding boxes
    potholes = db.relationship(
        "Pothole", backref="detection", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self, include_potholes: bool = False) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "image_path": self.image_path,
            "video_path": self.video_path,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "confidence": self.confidence,
            "severity": self.severity,
            "pothole_count": self.pothole_count,
            "status": self.status,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }
        if include_potholes:
            data["potholes"] = [p.to_dict() for p in self.potholes]
        return data

    def __repr__(self):
        return f"<Detection {self.id} user={self.user_id} severity={self.severity}>"
