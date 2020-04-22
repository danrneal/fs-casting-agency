"""Test objects used to test the behavior of endpoints in app.py.

Attributes:
    CASTING_ASSISTANT_TOKEN: An environmental variable representing a valid
        token belonging to a user with the 'Casting Assistant' role
    CASTING_DIRECTOR_TOKEN: An environmental variable representing a valid
        token belonging to a user with the 'Casting Director' role
    EXECUTIVE_PRODUCER_TOKEN: An environmental variable representing a valid
        token belonging to a user with the 'Executive Producer' role

Classes:
    CastingAssistantMovieTestCase()
    CastingDirectorMovieTestCase()
    ExecutiveProducerMovieTestCase()
"""

import os
import unittest
from app import app, MOVIES_PER_PAGE
from models import setup_db, Movie

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]
CASTING_ASSISTANT_TOKEN = os.environ["CASTING_ASSISTANT_TOKEN"]
CASTING_DIRECTOR_TOKEN = os.environ["CASTING_DIRECTOR_TOKEN"]
EXECUTIVE_PRODUCER_TOKEN = os.environ["EXECUTIVE_PRODUCER_TOKEN"]


class PublicMovieTestCase(unittest.TestCase):
    """Contains the test cases for the public movie endpoints.

    Attributes:
        app: A flask app from app.py
        client: A test client for the flask app to use while testing
        database_url: A str representing the location of the db used for
            testing
    """

    def setUp(self):
        """Set-up for PublicMovieTestCase."""
        self.app = app
        app.config["DEBUG"] = False
        self.client = self.app.test_client
        self.database_url = TEST_DATABASE_URL
        setup_db(self.app, self.database_url)

    def tearDown(self):
        """Executed after each test."""

    def test_get_paginated_movies_auth_fail(self):
        """Test failed retrieval of movies when not authenticated."""
        response = self.client().get("/movies")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(
            response.json.get("error_code"), "authorization_header_missing"
        )

    def test_movies_patch_method_not_allowed_fail(self):
        """Test that patch method is not allowed at /movies endpoint."""
        response = self.client().patch("/movies")

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "method_not_allowed")

    def test_movies_delete_method_not_allowed_fail(self):
        """Test that delete method is not allowed at /movies endpoint."""
        response = self.client().delete("/movies")

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "method_not_allowed")


class CastingAssistantMovieTestCase(unittest.TestCase):
    """Contains the test cases for the casting assistant movie endpoints.

    Attributes:
        headers: A dict representing the auth headers to be sent with requests
        app: A flask app from app.py
        client: A test client for the flask app to use while testing
        database_url: A str representing the location of the db used for
            testing
    """

    def setUp(self):
        """Set-up for CastingAssistantMovieTestCase."""
        self.headers = {"Authorization": f"Bearer {CASTING_ASSISTANT_TOKEN}"}
        self.app = app
        app.config["DEBUG"] = False
        self.client = self.app.test_client
        self.database_url = TEST_DATABASE_URL
        setup_db(self.app, self.database_url)

    def tearDown(self):
        """Executed after each test."""

    def test_get_paginated_movies_success(self):
        """Test successful retrieval of movies."""
        response = self.client().get("/movies", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get("success"), True)
        self.assertTrue(response.json.get("movies"))
        self.assertTrue(response.json.get("total_movies"))

    def test_get_paginated_movies_out_of_range_fail(self):
        """Test failed movie retrieval when page number is out of range."""
        total_pages = -(-Movie.query.count() // MOVIES_PER_PAGE)

        response = self.client().get(
            f"/movies?page={total_pages+1}", headers=self.headers
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "not_found")


class CastingDirectorMovieTestCase(unittest.TestCase):
    """Contains the test cases for the casting director movie endpoints.

    Attributes:
        headers: A dict representing the auth headers to be sent with requests
        app: A flask app from app.py
        client: A test client for the flask app to use while testing
        database_url: A str representing the location of the db used for
            testing
    """

    def setUp(self):
        """Set-up for CastingDirectorMovieTestCase."""
        self.headers = {"Authorization": f"Bearer {CASTING_DIRECTOR_TOKEN}"}
        self.app = app
        app.config["DEBUG"] = False
        self.client = self.app.test_client
        self.database_url = TEST_DATABASE_URL
        setup_db(self.app, self.database_url)

    def tearDown(self):
        """Executed after each test."""

    def test_create_movie_auth_fail(self):
        """Test failed creation of movie when unauthorized."""
        response = self.client().post("/movies", headers=self.headers)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "forbidden")


class ExecutiveProducerMovieTestCase(unittest.TestCase):
    """Contains the test cases for the executive producer movie endpoints.

    Attributes:
        headers: A dict representing the auth headers to be sent with requests
        app: A flask app from app.py
        client: A test client for the flask app to use while testing
        database_url: A str representing the location of the db used for
            testing
    """

    def setUp(self):
        """Set-up for CastingDirectorMovieTestCase."""
        self.headers = {"Authorization": f"Bearer {EXECUTIVE_PRODUCER_TOKEN}"}
        self.app = app
        app.config["DEBUG"] = False
        self.client = self.app.test_client
        self.database_url = TEST_DATABASE_URL
        setup_db(self.app, self.database_url)

    def tearDown(self):
        """Executed after each test."""

    def test_create_movie_success(self):
        """Test successful creation of a movie."""
        new_movie = {
            "title": "Black Widow",
            "release_date": "2020-11-06",
            "poster": (
                "https://m.media-amazon.com/images/M/MV5BZGRlNTY3NGYtM2YzZS00N"
                "2YyLTg0ZDYtNmY2ZDg2NDM3N2JlXkEyXkFqcGdeQXVyNTI4MzE4MDU@._V1_S"
                "Y1000_CR0,0,675,1000_AL_.jpg"
            ),
            "actors": ["Scarlett Johansson", "Robert Downey Jr."],
        }

        response = self.client().post(
            "/movies", json=new_movie, headers=self.headers
        )

        created_movie_id = response.json.get("created_movie_id")
        movie = Movie.query.get(created_movie_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get("success"), True)
        self.assertIsNone(response.json.get("old_movie"))
        self.assertTrue(response.json.get("new_movie"))
        self.assertIsNotNone(movie)

    def test_create_movie_unrecognized_actor_fail(self):
        """Test failed movie creation when an actor doesn't exist in the db."""
        new_movie = {
            "title": "Black Widow",
            "release_date": "2020-11-06",
            "poster": (
                "https://m.media-amazon.com/images/M/MV5BZGRlNTY3NGYtM2YzZS00N"
                "2YyLTg0ZDYtNmY2ZDg2NDM3N2JlXkEyXkFqcGdeQXVyNTI4MzE4MDU@._V1_S"
                "Y1000_CR0,0,675,1000_AL_.jpg"
            ),
            "actors": [
                "Florence Pugh",
                "Scarlett Johansson",
                "Robert Downey Jr.",
                "Rachel Weisz",
            ],
        }

        response = self.client().post(
            "/movies", json=new_movie, headers=self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "bad_request")

    def test_create_movie_no_info_fail(self):
        """Test failed movie creation when info is missing."""
        response = self.client().post("/movies", headers=self.headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "bad_request")


if __name__ == "__main__":
    unittest.main()
