"""
app.py
Flask application factory. Registers extensions and all blueprints.
"""

from flask import Flask, jsonify

from config import Config
from extensions import db, jwt, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Init extensions ---
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    # --- Register blueprints ---
    from routes.auth_routes import auth_bp
    from routes.upload_routes import upload_bp
    from routes.detection_routes import detection_bp
    from routes.history_routes import history_bp
    from routes.report_routes import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(report_bp)

    # --- Health check (used by Render/Railway deployment monitoring) ---
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "pothole-ai-backend"}), 200

    # --- Friendly JSON error handlers ---
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "File too large"}), 413

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app
