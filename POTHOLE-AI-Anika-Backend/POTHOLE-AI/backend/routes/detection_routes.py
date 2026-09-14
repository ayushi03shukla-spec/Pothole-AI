"""
routes/detection_routes.py
Runs pothole detection on a previously uploaded file, and stores each
found pothole in the Potholes table.

Currently calls utils/mock_detector.py (dummy JSON, per Phase 2 plan).
Once Ayushi delivers best.pt, this route does NOT change — only
mock_detector.py's internals change.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.detection import Detection
from models.pothole import Pothole
from utils.mock_detector import run_detection, compute_severity, overall_severity

detection_bp = Blueprint("detection", __name__, url_prefix="/api/detect")


@detection_bp.route("/<int:detection_id>", methods=["POST"])
@jwt_required()
def run_detect(detection_id):
    user_id = int(get_jwt_identity())
    detection = Detection.query.get(detection_id)

    if not detection:
        return jsonify({"error": "Detection not found"}), 404
    if str(detection.user_id) != str(user_id):
        return jsonify({"error": "Not authorized to access this detection"}), 403

    file_path = detection.image_path or detection.video_path
    if not file_path:
        return jsonify({"error": "Detection has no associated file"}), 400

    try:
        raw_boxes = run_detection(file_path)
    except Exception as e:
        detection.status = "failed"
        db.session.commit()
        return jsonify({"error": f"Detection failed: {str(e)}"}), 500

    severities = []
    confidences = []

    # Clear any previous potholes for this detection (re-run support)
    Pothole.query.filter_by(detection_id=detection.id).delete()

    for box in raw_boxes:
        width = box["x_max"] - box["x_min"]
        height = box["y_max"] - box["y_min"]
        size = width * height
        severity = compute_severity(size)

        pothole = Pothole(
            detection_id=detection.id,
            x_min=box["x_min"], y_min=box["y_min"],
            x_max=box["x_max"], y_max=box["y_max"],
            width=width, height=height, size=size,
            confidence=box["confidence"],
            severity=severity,
        )
        db.session.add(pothole)
        severities.append(severity)
        confidences.append(box["confidence"])

    detection.pothole_count = len(raw_boxes)
    detection.confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
    detection.severity = overall_severity(severities)
    detection.status = "processed"

    db.session.commit()

    return jsonify({
        "message": "Detection complete",
        "detection": detection.to_dict(include_potholes=True),
    }), 200


@detection_bp.route("/<int:detection_id>", methods=["GET"])
@jwt_required()
def get_detection(detection_id):
    user_id = int(get_jwt_identity())
    detection = Detection.query.get(detection_id)

    if not detection:
        return jsonify({"error": "Detection not found"}), 404
    if str(detection.user_id) != str(user_id):
        return jsonify({"error": "Not authorized to access this detection"}), 403

    return jsonify({"detection": detection.to_dict(include_potholes=True)}), 200
