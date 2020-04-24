"""Model objects used to model data for the db.

Attributes:
    DATABASE_URL: A str representing the location of the db
    db: A SQLAlchemy service
    movie_actors: A SQLAlchemy association table to map the many-to-many
        relationship between movies and actors

Classes:
    Movie()
    Artist()
"""

import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

DATABASE_URL = os.environ["DATABASE_URL"]
db = SQLAlchemy()

movie_actors = db.Table(
    "movie_actors",
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("actor_id", Integer, ForeignKey("actors.id"), primary_key=True),
)


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
    db.create_all()


class Movie(db.Model):
    """A model representing a movie.

    Attributes:
        id: An int that serves as the unique identifier for a movie
        title: A str representing the title of the movie
        release_date: A date representing the release date of the movie
        poster: A str representing a url to an image of the movie's poster
        actors: A list of Actor objects representing the actors that play in
            the movie
    """

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(Date)
    poster = Column(String)
    actors = relationship("Actor", secondary=movie_actors, backref="movies")

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
            "release_date": str(self.release_date),
            "poster": self.poster,
            "actors": [
                {"id": actor.id, "name": actor.name} for actor in self.actors
            ],
        }

        return movie


class Actor(db.Model):
    """A model representing an actor.

    Attributes:
        id: An int that serves as the unique identifier for an actor
        name: A str representing the name of the actor
        birthdate: An date representing the birthdate of the actor
        gender: A str representing the gender of the actor
        image: A str representing a url to an image of the actor
    """

    __tablename__ = "actors"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    birthdate = Column(Date)
    gender = Column(String)
    image = Column(String)

    def insert(self):
        """Inserts a new actor object into the db."""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Updates an existing actor object in the db."""
        db.session.commit()

    def delete(self):
        """Deletes an existing actor object from the db."""
        db.session.delete(self)
        db.session.commit()

    def format(self):
        """Formats the actor object as a dict.

        Returns:
            actor: A dict representing the actor object
        """
        actor = {
            "id": self.id,
            "name": self.name,
            "birthdate": str(self.birthdate),
            "gender": self.gender,
            "image": self.image,
            "movies": [
                {
                    "id": movie.id,
                    "title": movie.title,
                    "release_date": str(movie.release_date),
                }
                for movie in self.movies
            ],
        }

        return actor
