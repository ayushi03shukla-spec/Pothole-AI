"""
extensions.py
Single shared instances of db / jwt / cors so every module (models, routes,
scripts) imports the SAME object instead of creating circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
