from flask import Flask
from flask_cors import CORS
from models import setup_db

app = Flask(__name__)
setup_db(app)
CORS(app)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
