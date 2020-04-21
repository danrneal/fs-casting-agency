"""Model objects used to model data for the db.

Attributes:
    DATABASE_URL: A str representing the location of the db
    db: A SQLAlchemy service

Classes:
    Movie()
"""

import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Date

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


class Movie(db.Model):
    """A model representing a movie.

    Attributes:
        id: An int that serves as the unique identifier for a movie
        title: A str representing the title of the movie
        release_date: A date representing the release date of the movie
    """

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(Date)

    def insert(self):
        """Inserts a new movie object into the db."""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Updates an existing movie object in the db."""
        db.session.commit()

    def delete(self):
        """Deletes an existing movie object from the db."""
        db.session.delete(self)
        db.session.commit()

    def format(self):
        """Formats the movie object as a dict.

        Returns:
            movie: A dict representing the movie object
        """
        movie = {
            "id": self.id,
            "title": self.title,
            "release_date": self.release_date,
        }

        return movie
