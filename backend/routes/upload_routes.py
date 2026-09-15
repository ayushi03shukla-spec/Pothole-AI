"""
routes/upload_routes.py
Handles image/video upload from Anamika's Upload Page.
Creates a 'pending' Detection row immediately, so the frontend gets a
detection_id to show in the UI right away, then calls /api/detect/<id>
to actually run the model (mock now, real YOLO after Phase 3).
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.detection import Detection
from utils.file_handler import save_upload

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")


@upload_bp.route("/image", methods=["POST"])
@jwt_required()
def upload_image():
    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return jsonify({"error": "No file part named 'file' in request"}), 400

    file = request.files["file"]
    latitude = request.form.get("latitude", type=float)
    longitude = request.form.get("longitude", type=float)

    try:
        path = save_upload(
            file,
            current_app.config["IMAGE_UPLOAD_FOLDER"],
            current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    detection = Detection(
        user_id=user_id,
        image_path=path,
        latitude=latitude,
        longitude=longitude,
        status="pending",
    )
    db.session.add(detection)
    db.session.commit()

    return jsonify({
        "message": "Image uploaded successfully. Call /api/detect/<id> to run detection.",
        "detection": detection.to_dict(),
    }), 201


@upload_bp.route("/video", methods=["POST"])
@jwt_required()
def upload_video():
    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return jsonify({"error": "No file part named 'file' in request"}), 400

    file = request.files["file"]
    latitude = request.form.get("latitude", type=float)
    longitude = request.form.get("longitude", type=float)

    try:
        path = save_upload(
            file,
            current_app.config["VIDEO_UPLOAD_FOLDER"],
            current_app.config["ALLOWED_VIDEO_EXTENSIONS"],
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    detection = Detection(
        user_id=user_id,
        video_path=path,
        latitude=latitude,
        longitude=longitude,
        status="pending",
    )
    db.session.add(detection)
    db.session.commit()

    return jsonify({
        "message": "Video uploaded successfully. Call /api/detect/<id> to run detection.",
        "detection": detection.to_dict(),
    }), 201
