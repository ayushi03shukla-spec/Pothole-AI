"""
routes/detection_routes.py

Runs YOLO pothole detection on a previously uploaded image,
then uses Depth Anything V2 to estimate pothole severity.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.detection import Detection
from models.pothole import Pothole
from utils.yolo_detector import run_detection
from utils.depth_estimator import analyze_image


detection_bp = Blueprint(
    "detection",
    __name__,
    url_prefix="/api/detect"
)


def get_overall_severity(severities):
    """
    Determine the overall detection severity.

    Priority:
        high > medium > low > undetermined
    """

    if "high" in severities:
        return "high"

    if "medium" in severities:
        return "medium"

    if "low" in severities:
        return "low"

    return "undetermined"


@detection_bp.route(
    "/<int:detection_id>",
    methods=["POST"]
)
@jwt_required()
def run_detect(detection_id):
    """
    Run YOLO detection and automatic depth-based
    severity estimation.
    """

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

    # Automatic severity currently works with images.
    file_path = detection.image_path

    if not file_path:
        return jsonify({
            "error": "Detection does not contain an image file"
        }), 400

    # ---------------------------------------------------------
    # YOLO confidence threshold
    # ---------------------------------------------------------

    confidence = request.args.get(
        "confidence",
        default=0.50,
        type=float
    )

    confidence = max(
        0.25,
        min(confidence, 0.90)
    )

    # ---------------------------------------------------------
    # YOLO detection
    # ---------------------------------------------------------

    try:
        raw_boxes = run_detection(
            file_path,
            confidence=confidence
        )

    except Exception as exc:
        detection.status = "failed"
        db.session.commit()

        return jsonify({
            "error": f"YOLO detection failed: {str(exc)}"
        }), 500

    # ---------------------------------------------------------
    # Remove previous pothole records if detection
    # is being re-run.
    # ---------------------------------------------------------

    Pothole.query.filter_by(
        detection_id=detection.id
    ).delete()

    # ---------------------------------------------------------
    # Automatic depth + severity estimation
    # ---------------------------------------------------------

    severity_results = []

    if raw_boxes:

        try:
            severity_results = analyze_image(
                file_path,
                raw_boxes
            )

        except Exception as exc:
            detection.status = "failed"
            db.session.commit()

            return jsonify({
                "error": (
                    "Depth-based severity estimation "
                    f"failed: {str(exc)}"
                )
            }), 500

    # Make sure there is one result for every YOLO box.
    while len(severity_results) < len(raw_boxes):

        severity_results.append({
            "severity": "undetermined",
            "residual_90": None,
            "positive_fraction": None,
        })

    confidences = []
    severities = []

    # ---------------------------------------------------------
    # Store potholes
    # ---------------------------------------------------------

    for box, severity_result in zip(
        raw_boxes,
        severity_results
    ):

        width = (
            box["x_max"]
            - box["x_min"]
        )

        height = (
            box["y_max"]
            - box["y_min"]
        )

        size = width * height

        severity = severity_result.get(
            "severity",
            "undetermined"
        )

        if severity not in (
            "low",
            "medium",
            "high",
            "undetermined"
        ):
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

            # We intentionally do NOT put the model's
            # residual into depth_mm because residual
            # is not a calibrated physical depth measurement.
            depth_mm=None,

            severity=severity,
        )

        db.session.add(pothole)

        confidences.append(
            box["confidence"]
        )

        severities.append(
            severity
        )

    # ---------------------------------------------------------
    # Update overall detection information
    # ---------------------------------------------------------

    detection.pothole_count = len(
        raw_boxes
    )

    detection.confidence = (
        round(
            sum(confidences)
            / len(confidences),
            4
        )
        if confidences
        else 0.0
    )

    if raw_boxes:
        detection.severity = (
            get_overall_severity(
                severities
            )
        )
    else:
        detection.severity = "none"

    detection.status = "processed"

    db.session.commit()

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------

    return jsonify({
        "message": (
            "Detection and automatic "
            "severity estimation complete"
        ),
        "detection": detection.to_dict(
            include_potholes=True
        ),
    }), 200


@detection_bp.route(
    "/<int:detection_id>",
    methods=["GET"]
)
@jwt_required()
def get_detection(detection_id):
    """Get a previously processed detection."""

    user_id = int(
        get_jwt_identity()
    )

    detection = Detection.query.get(
        detection_id
    )

    if not detection:
        return jsonify({
            "error": "Detection not found"
        }), 404

    if str(detection.user_id) != str(user_id):
        return jsonify({
            "error": (
                "Not authorized to access "
                "this detection"
            )
        }), 403

    return jsonify({
        "detection": detection.to_dict(
            include_potholes=True
        )
    }), 200