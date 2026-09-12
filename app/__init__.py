import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Ensure project root is in the path for clean imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Config  # type: ignore

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure document upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    from .routes import main

    app.register_blueprint(main)

    with app.app_context():
        from . import models

        db.create_all()

    return app