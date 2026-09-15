"""
tests/conftest.py
Shared pytest fixtures — spins up an in-memory SQLite app for fast,
isolated tests that never touch the real MySQL database.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db as _db
from config import Config


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    JWT_SECRET_KEY = "test-secret"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Registers a user and returns Authorization headers for it."""
    client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
    })
    resp = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
    })
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
