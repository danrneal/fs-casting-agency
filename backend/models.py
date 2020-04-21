"""Model objects used to model data for the db.

Attributes:
    DATABASE_URL: A str representing the location of the db
    db: A SQLAlchemy service
"""

import os
from flask_sqlalchemy import SQLAlchemy

DATABASE_URL = os.getenv("DATABASE_URL")
db = SQLAlchemy()


def setup_db(app, database_url=DATABASE_URL):
    """Binds a flask application and a SQLAlchemy service.

    Args:
        app: A flask app
        database_url: A str representing the location of the db (default:
            global DATABASE_URL)
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
