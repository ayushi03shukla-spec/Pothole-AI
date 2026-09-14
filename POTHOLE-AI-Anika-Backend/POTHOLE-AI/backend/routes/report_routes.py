"""
routes/report_routes.py
Download CSV / PDF of the logged-in user's detection history.
"""

from flask import Blueprint, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.detection import Detection
from models.user import User
from utils.csv_export import generate_csv_report
from utils.pdf_export import generate_pdf_report

report_bp = Blueprint("report", __name__, url_prefix="/api/report")


@report_bp.route("/csv", methods=["GET"])
@jwt_required()
def download_csv():
    user_id = int(get_jwt_identity())
    detections = Detection.query.filter_by(user_id=user_id) \
        .order_by(Detection.detected_at.desc()).all()

    if not detections:
        return jsonify({"error": "No detection history to export"}), 404

    file_path = generate_csv_report(
        [d.to_dict() for d in detections],
        current_app.config["REPORT_FOLDER"],
    )
    return send_file(
        file_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name="pothole_report.csv",
    )


@report_bp.route("/pdf", methods=["GET"])
@jwt_required()
def download_pdf():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    detections = Detection.query.filter_by(user_id=user_id) \
        .order_by(Detection.detected_at.desc()).all()

    if not detections:
        return jsonify({"error": "No detection history to export"}), 404

    file_path = generate_pdf_report(
        [d.to_dict() for d in detections],
        user.name if user else "Unknown User",
        current_app.config["REPORT_FOLDER"],
    )
    return send_file(
        file_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="pothole_report.pdf",
    )
