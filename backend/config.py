"""
config.py
Central configuration for the Pothole AI backend.
Reads from .env so secrets never live in source control.
"""

import os
from datetime import timedelta

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    # python-dotenv not installed yet (e.g. before `pip install -r requirements.txt`
    # has been run). Fall back to whatever is already in the OS environment so the
    # app doesn't crash on import — it just won't read .env until the dep is added.
    pass

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Core Flask ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # --- Database ---
    USE_SQLITE = os.getenv("USE_SQLITE", "False") == "True"

    if USE_SQLITE:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'pothole_ai.db')}"
    else:
        DB_USER = os.getenv("DB_USER", "root")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "3306")
        DB_NAME = os.getenv("DB_NAME", "pothole_ai")
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Uploads ---
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    IMAGE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, "images")
    VIDEO_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, "videos")
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "avi"}
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", 50)) * 1024 * 1024

    # --- Reports ---
    REPORT_FOLDER = os.path.join(BASE_DIR, "static", "reports")

    # --- CORS: allow the frontend (Streamlit / React) to call the API ---
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
