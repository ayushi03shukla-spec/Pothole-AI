"""
routes/detection_routes.py

Runs pothole detection on a previously uploaded image
and stores each detected pothole in the database.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.detection import Detection
from models.pothole import Pothole
from utils.yolo_detector import run_detection


detection_bp = Blueprint(
    "detection",
    __name__,
    url_prefix="/api/detect"
)


@detection_bp.route("/<int:detection_id>", methods=["POST"])
@jwt_required()
def run_detect(detection_id):
    """Run YOLO detection for a previously uploaded file."""

    user_id = int(get_jwt_identity())

    detection = Detection.query.get(detection_id)

    if not detection:
        return jsonify({"error": "Detection not found"}), 404

    if str(detection.user_id) != str(user_id):
        return jsonify({
            "error": "Not authorized to access this detection"
        }), 403

    file_path = detection.image_path or detection.video_path

    if not file_path:
        return jsonify({
            "error": "Detection has no associated file"
        }), 400

    # Get confidence threshold from the frontend.
    confidence = request.args.get(
        "confidence",
        default=0.50,
        type=float
    )

    # Keep threshold within a safe range.
    confidence = max(0.25, min(confidence, 0.90))

    try:
        raw_boxes = run_detection(
            file_path,
            confidence=confidence
        )

    except Exception as e:
        detection.status = "failed"
        db.session.commit()

        return jsonify({
            "error": f"Detection failed: {str(e)}"
        }), 500

    # Remove previous pothole records if this detection is re-run.
    Pothole.query.filter_by(
        detection_id=detection.id
    ).delete()

    confidences = []

    for box in raw_boxes:

        width = box["x_max"] - box["x_min"]
        height = box["y_max"] - box["y_min"]
        size = width * height

        # IMPORTANT:
        # A normal RGB image does not provide reliable physical
        # pothole depth in millimetres.
        #
        # Therefore we do NOT claim Low / Medium / High severity
        # from bounding-box pixel area.
        severity = "undetermined"

        pothole = Pothole(
            detection_id=detection.id,

            x_min=box["x_min"],
            y_min=box["y_min"],
            x_max=box["x_max"],
            y_max=box["y_max"],

            width=width,
            height=height,
            size=size,

            confidence=box["confidence"],
            severity=severity,
        )

        db.session.add(pothole)
        confidences.append(box["confidence"])

    # Update overall detection information.
    detection.pothole_count = len(raw_boxes)

    detection.confidence = (
        round(
            sum(confidences) / len(confidences),
            2
        )
        if confidences
        else 0.0
    )

    if raw_boxes:
        detection.severity = "undetermined"
    else:
        detection.severity = "none"

    detection.status = "processed"

    db.session.commit()

    return jsonify({
        "message": "Detection complete",
        "detection": detection.to_dict(
            include_potholes=True
        ),
    }), 200


@detection_bp.route("/<int:detection_id>", methods=["GET"])
@jwt_required()
def get_detection(detection_id):
    """Get a previously processed detection."""

    user_id = int(get_jwt_identity())

    detection = Detection.query.get(detection_id)

    if not detection:
        return jsonify({
            "error": "Detection not found"
        }), 404

    if str(detection.user_id) != str(user_id):
        return jsonify({
            "error": "Not authorized to access this detection"
        }), 403

    return jsonify({
        "detection": detection.to_dict(
            include_potholes=True
        )
    }), 200
