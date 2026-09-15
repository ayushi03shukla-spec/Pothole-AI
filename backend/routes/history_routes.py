"""
routes/history_routes.py
Powers Anamika's History Page / Dashboard AND Prashant's map pins
(latitude/longitude/severity come straight from here).
Supports filtering by severity and date range, and pagination.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.detection import Detection

history_bp = Blueprint("history", __name__, url_prefix="/api/history")


@history_bp.route("", methods=["GET"])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())

    query = Detection.query.filter_by(user_id=user_id)

    # --- Optional filters ---
    severity = request.args.get("severity")
    if severity:
        query = query.filter(Detection.severity == severity)

    date_from = request.args.get("date_from")  # expects YYYY-MM-DD
    if date_from:
        try:
            query = query.filter(Detection.detected_at >= datetime.fromisoformat(date_from))
        except ValueError:
            return jsonify({"error": "date_from must be in YYYY-MM-DD format"}), 400

    date_to = request.args.get("date_to")
    if date_to:
        try:
            query = query.filter(Detection.detected_at <= datetime.fromisoformat(date_to))
        except ValueError:
            return jsonify({"error": "date_to must be in YYYY-MM-DD format"}), 400

    # --- Pagination ---
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)

    query = query.order_by(Detection.detected_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "detections": [d.to_dict() for d in pagination.items],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "total_pages": pagination.pages,
    }), 200


@history_bp.route("/<int:detection_id>", methods=["DELETE"])
@jwt_required()
def delete_detection(detection_id):
    user_id = int(get_jwt_identity())
    detection = Detection.query.get(detection_id)

    if not detection:
        return jsonify({"error": "Detection not found"}), 404
    if str(detection.user_id) != str(user_id):
        return jsonify({"error": "Not authorized to delete this detection"}), 403

    db.session.delete(detection)
    db.session.commit()

    return jsonify({"message": "Detection deleted"}), 200


@history_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    """Quick summary numbers for the dashboard's stat cards."""
    user_id = int(get_jwt_identity())
    detections = Detection.query.filter_by(user_id=user_id).all()

    total = len(detections)
    total_potholes = sum(d.pothole_count or 0 for d in detections)
    severity_breakdown = {"low": 0, "medium": 0, "high": 0}
    for d in detections:
        if d.severity in severity_breakdown:
            severity_breakdown[d.severity] += 1

    return jsonify({
        "total_scans": total,
        "total_potholes_found": total_potholes,
        "severity_breakdown": severity_breakdown,
    }), 200
