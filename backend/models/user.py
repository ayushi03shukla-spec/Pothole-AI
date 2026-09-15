"""
models/user.py
Users table — matches the whiteboard ER diagram:
id (PK), name, email, password, role, created_at
"""

from datetime import datetime
import bcrypt
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)  # bcrypt hash, never plaintext
    role = db.Column(db.String(20), default="user", nullable=False)  # 'user' | 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One user -> many detections
    detections = db.relationship(
        "Detection", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, plain_password: str) -> None:
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
        self.password = hashed.decode("utf-8")

    def check_password(self, plain_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), self.password.encode("utf-8")
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.email}>"
