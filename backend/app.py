from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from auth import requires_auth
from models import setup_db, Movie

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
