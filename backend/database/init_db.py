"""
database/init_db.py
Creates all tables from the SQLAlchemy models.
Run once after setting up .env:  python database/init_db.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db
from models.user import User        # noqa: F401 (import needed to register table)
from models.detection import Detection  # noqa: F401
from models.pothole import Pothole      # noqa: F401


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully:")
        for table in db.metadata.tables:
            print(f"   - {table}")


if __name__ == "__main__":
    main()
