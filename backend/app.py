"""A flask-based casting agency API with Authorization and Authentication.

Usage: flask run

Attributes:
    app: A flask Flask object creating the flask app
"""

from flask import Flask, request, abort, jsonify, render_template
from flask_cors import CORS
from auth import (
    requires_auth,
    AuthError,
    AUTH0_DOMAIN,
    CLIENT_ID,
    API_IDENTIFIER,
)
from models import setup_db, Movie, Actor

app = Flask(__name__)
setup_db(app)
CORS(app)

MOVIES_PER_PAGE = 25
ACTORS_PER_PAGE = 25


def get_actors_from_names(actor_names):
    """Gets a list of actor objects from a list of actor names.

    Args:
        actor_names: A list of strs representing the names of actors

    Returns:
        actors: A list of actor objects corresponding to the actor names
            passed in
    """
    actors = []

    if actor_names is not None:
        for actor_name in actor_names:
            actor = Actor.query.filter_by(name=actor_name).first()

            if actor is None:
                raise AttributeError

            actors.append(actor)

    return actors


def get_movies_from_titles(movie_titles):
    """Gets a list of movie objects from a list of movie titles.

    Args:
        movie_titles: A list of strs representing the titles of movies

    Returns:
        movies: A list of movie objects corresponding to the movie titles
            passed in
    """
    movies = []

    if movie_titles is not None:
        for movie_title in movie_titles:
            movie = Movie.query.filter_by(title=movie_title).first()

            if movie is None:
                raise AttributeError

            movies.append(movie)

    return movies


@app.after_request
def after_request(response):
    """Adds response headers after request.

    Args:
        response: The response object to add headers to

    Returns:
        response: The response object that the headers were added to
    """
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type, Authorization, true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
    )

    return response


@app.route("/")
def index():
    """Route handler for the homepage.

    Returns:
        Template for the homepage
    """
    return render_template("index.html")


@app.route("/auth_config")
def auth_config():
    """Route handler for auth config variables.

    Returns:
        response: A json object representing the Auth0 Domain and Client ID of
            the Auth0 application
    """
    response = jsonify(
        {
            "domain": AUTH0_DOMAIN,
            "client_id": CLIENT_ID,
            "audience": API_IDENTIFIER,
        }
    )

    return response


@app.route("/movies", methods=["GET"])
@requires_auth("read:movies")
def get_movies():
    """Route handler for the endpoint showing paginated movies.

    Returns:
        response: A json object representing a page of movies
    """
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * MOVIES_PER_PAGE
    end = start + MOVIES_PER_PAGE
    movies = Movie.query.order_by(Movie.title).all()
    current_movies = [movie.format() for movie in movies][start:end]

    if len(current_movies) == 0:
        abort(404)

    response = jsonify(
        {
            "success": True,
            "movies": current_movies,
            "total_movies": len(movies),
        }
    )

    return response


@app.route("/movies", methods=["POST"])
@requires_auth("create:movies")
def create_movie():
    """Route handler for the endpoint for creating a new movie.

    Returns:
        response: A json object representing info about the created movie
    """
    try:

        movie = Movie(
            title=request.json.get("title"),
            release_date=request.json.get("release_date"),
            poster=request.json.get("poster"),
            actors=get_actors_from_names(request.json.get("actors")),
        )

        movie.insert()

        response = jsonify(
            {
                "success": True,
                "created_movie_id": movie.id,
                "old_movie": None,
                "new_movie": movie.format(),
            }
        )

    except AttributeError:
        abort(400)

    return response


@app.route("/movies/<int:movie_id>", methods=["PATCH"])
@requires_auth("update:movies")
def update_movie(movie_id):
    """Route handler for endpoint updating a single movie.

    Args:
        movie_id: An int representing the identifier for the movie to update

    Returns:
        response: A json object representing info about the updated movie
    """
    movie = Movie.query.get(movie_id)

    if movie is None:
        abort(422)

    try:
        old_movie = movie.format()
        title = request.json.get("title")
        release_date = request.json.get("release_date")
        poster = request.json.get("poster")
        actor_names = request.json.get("actors")

        if title is not None:
            movie.title = title

        if release_date is not None:
            movie.release_date = release_date

        if poster is not None:
            movie.poster = poster

        if actor_names is not None:
            movie.actors = get_actors_from_names(actor_names)

        movie.update()

        response = jsonify(
            {
                "success": True,
                "updated_movie_id": movie_id,
                "old_movie": old_movie,
                "new_movie": movie.format(),
            }
        )

    except AttributeError:
        abort(400)

    return response


@app.route("/movies/<int:movie_id>", methods=["DELETE"])
@requires_auth("delete:movies")
def delete_movie(movie_id):
    """Route handler for endpoint to delete a single movie.

    Args:
        movie_id: An int representing the identifier for the movie to delete

    Returns:
        response: A json object representing info about the deleted movie
    """
    movie = Movie.query.get(movie_id)

    if movie is None:
        abort(422)

    old_movie = movie.format()
    movie.delete()

    response = jsonify(
        {
            "success": True,
            "deleted_movie_id": movie_id,
            "old_movie": old_movie,
            "new_movie": None,
        }
    )

    return response


@app.route("/actors", methods=["GET"])
@requires_auth("read:actors")
def get_actors():
    """Route handler for the endpoint showing paginated actors.

    Returns:
        response: A json object representing a page of actors
    """
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * ACTORS_PER_PAGE
    end = start + ACTORS_PER_PAGE
    actors = Actor.query.order_by(Actor.name).all()
    current_actors = [actor.format() for actor in actors][start:end]

    if len(current_actors) == 0:
        abort(404)

    response = jsonify(
        {
            "success": True,
            "actors": current_actors,
            "total_actors": len(actors),
        }
    )

    return response


@app.route("/actors", methods=["POST"])
@requires_auth("create:actors")
def create_actor():
    """Route handler for the endpoint for creating a new actor.

    Returns:
        response: A json object representing info about the created actor
    """
    try:

        actor = Actor(
            name=request.json.get("name"),
            birthdate=request.json.get("birthdate"),
            gender=request.json.get("gender"),
            image=request.json.get("image"),
            movies=get_movies_from_titles(request.json.get("movies")),
        )

        actor.insert()

        response = jsonify(
            {
                "success": True,
                "created_actor_id": actor.id,
                "old_actor": None,
                "new_actor": actor.format(),
            }
        )

    except AttributeError:
        abort(400)

    return response


@app.route("/actors/<int:actor_id>", methods=["PATCH"])
@requires_auth("update:actors")
def update_actor(actor_id):
    """Route handler for endpoint updating a single actor.

    Args:
        actor_id: An int representing the identifier for the actor to update

    Returns:
        response: A json object representing info about the updated actor
    """
    actor = Actor.query.get(actor_id)

    if actor is None:
        abort(422)

    try:
        old_actor = actor.format()
        name = request.json.get("name")
        birthdate = request.json.get("birthdate")
        gender = request.json.get("gender")
        image = request.json.get("image")
        movie_titles = request.json.get("movies")

        if name is not None:
            actor.name = name

        if birthdate is not None:
            actor.birthdate = birthdate

        if gender is not None:
            actor.gender = gender

        if image is not None:
            actor.image = image

        if movie_titles is not None:
            actor.movies = get_movies_from_titles(movie_titles)

        actor.update()

        response = jsonify(
            {
                "success": True,
                "updated_actor_id": actor_id,
                "old_actor": old_actor,
                "new_actor": actor.format(),
            }
        )

    except AttributeError:
        abort(400)

    return response


@app.route("/actors/<int:actor_id>", methods=["DELETE"])
@requires_auth("delete:actors")
def delete_actor(actor_id):
    """Route handler for endpoint to delete a single actor.

    Args:
        actor_id: An int representing the identifier for the actor to delete

    Returns:
        response: A json object representing info about the deleted actor
    """
    actor = Actor.query.get(actor_id)

    if actor is None:
        abort(422)

    old_actor = actor.format()
    actor.delete()

    response = jsonify(
        {
            "success": True,
            "deleted_actor_id": actor_id,
            "old_actor": old_actor,
            "new_actor": None,
        }
    )

    return response


@app.errorhandler(400)
def bad_request(error):  # pylint: disable=unused-argument
    """Error handler for 400 bad request.

    Args:
        error: unused

    Returns:
        Response: A json object with the error code and message
    """
    response = jsonify(
        {
            "success": False,
            "error_code": "bad_request",
            "description": "The request was malformed in some way",
        }
    )
    return response, 400


@app.errorhandler(404)
def not_found(error):  # pylint: disable=unused-argument
    """Error handler for 404 not found.

    Args:
        error: unused

    Returns:
        Response: A json object with the error code and message
    """
    response = jsonify(
        {
            "success": False,
            "error_code": "not_found",
            "description": "The resource could not be found on the server",
        }
    )
    return response, 404


@app.errorhandler(405)
def method_not_allowed(error):  # pylint: disable=unused-argument
    """Error handler for 405 method not allowed.

    Args:
        error: unused

    Returns:
        Response: A json object with the error code and message
    """
    response = jsonify(
        {
            "success": False,
            "error_code": "method_not_allowed",
            "description": "Incorrect request method was specified",
        }
    )
    return response, 405


@app.errorhandler(422)
def unprocessable_entity(error):  # pylint: disable=unused-argument
    """Error handler for 422 unprocessable entity.

    Args:
        error: unused

    Returns:
        Response: A json object with the error code and message
    """
    response = jsonify(
        {
            "success": False,
            "error_code": "unprocessable_entity",
            "description": "The request was unable to be fulfilled",
        }
    )
    return response, 422


@app.errorhandler(500)
def internal_server_error(error):  # pylint: disable=unused-argument
    """Error handler for 500 internal server error.

    Args:
        error: unused

    Returns:
        Response: A json object with the error code and message
    """
    response = jsonify(
        {
            "success": False,
            "error_code": "internal_server_error",
            "description": "Something went wrong on the server",
        }
    )
    return response, 500


@app.errorhandler(AuthError)
def authorization_error(error):
    """Error handler for authorization error.

    Args:
        error: A dict representing the authorization error

    Returns:
        Response: A json object with the error code and message
    """
    error.error["success"] = False
    response = jsonify(error.error)
    response.status_code = error.status_code

    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
