"""
database/seed_data.py
Adds a demo user + a handful of detections/potholes so Anamika (frontend)
and Prashant (maps) can build and test their UI against realistic data
before real uploads/model integration exist.

Run: python database/seed_data.py
Demo login -> email: demo@potholeai.com | password: demo1234
"""

import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db
from models.user import User
from models.detection import Detection
from models.pothole import Pothole

# Sample GPS points around Kanpur, India, for realistic map testing
SAMPLE_COORDS = [
    (26.4499, 80.3319),
    (26.4670, 80.3494),
    (26.5123, 80.2329),
    (26.4287, 80.3559),
    (26.4926, 80.2931),
]

SEVERITIES = ["low", "medium", "high"]


def main():
    app = create_app()
    with app.app_context():
        existing = User.query.filter_by(email="demo@potholeai.com").first()
        if existing:
            print("Demo user already exists — skipping seed.")
            return

        demo_user = User(name="Demo User", email="demo@potholeai.com", role="user")
        demo_user.set_password("demo1234")
        db.session.add(demo_user)
        db.session.commit()

        for i in range(5):
            lat, lng = SAMPLE_COORDS[i % len(SAMPLE_COORDS)]
            detection = Detection(
                user_id=demo_user.id,
                image_path=f"uploads/images/sample_{i+1}.jpg",
                latitude=lat + random.uniform(-0.002, 0.002),
                longitude=lng + random.uniform(-0.002, 0.002),
                status="processed",
                detected_at=datetime.utcnow() - timedelta(days=i),
            )
            db.session.add(detection)
            db.session.flush()  # get detection.id before commit

            num_potholes = random.randint(1, 3)
            confidences = []
            severities = []
            for _ in range(num_potholes):
                severity = random.choice(SEVERITIES)
                confidence = round(random.uniform(0.6, 0.97), 2)
                pothole = Pothole(
                    detection_id=detection.id,
                    x_min=10, y_min=10, x_max=120, y_max=100,
                    width=110, height=90, size=9900,
                    confidence=confidence,
                    severity=severity,
                )
                db.session.add(pothole)
                confidences.append(confidence)
                severities.append(severity)

            detection.pothole_count = num_potholes
            detection.confidence = round(sum(confidences) / len(confidences), 2)
            order = {"low": 1, "medium": 2, "high": 3}
            detection.severity = max(severities, key=lambda s: order[s])

        db.session.commit()
        print("✅ Seed data created.")
        print("   Login -> email: demo@potholeai.com | password: demo1234")


if __name__ == "__main__":
    main()
