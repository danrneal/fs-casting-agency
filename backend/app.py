from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from auth import requires_auth, AuthError
from models import setup_db, Movie, Actor

app = Flask(__name__)
setup_db(app)
CORS(app)

MOVIES_PER_PAGE = 25


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
    movies = Movie.query.order_by(Movie.release_date).all()
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
        actor_names = request.json.get("actors")
        actors = []
        if actor_names is not None:
            for actor_name in actor_names:
                actor = Actor.query.filter_by(name=actor_name).first()

                if actor is None:
                    raise AttributeError

                actors.append(actor)

        movie = Movie(
            title=request.json.get("title"),
            release_date=request.json.get("release_date"),
            poster=request.json.get("poster"),
            actors=actors,
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
