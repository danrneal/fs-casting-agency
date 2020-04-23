"""Test objects used to test the behavior of endpoints in app.py.

Attributes:
    CASTING_ASSISTANT_TOKEN: An environmental variable representing a valid
        token belonging to a user with the 'Casting Assistant' role
    CASTING_DIRECTOR_TOKEN: An environmental variable representing a valid
        token belonging to a user with the 'Casting Director' role
    EXECUTIVE_PRODUCER_TOKEN: An environmental variable representing a valid
        token belonging to a user with the 'Executive Producer' role

Classes:
    PublicMovieTestCase()
    CastingAssistantMovieTestCase()
    CastingDirectorMovieTestCase()
    ExecutiveProducerMovieTestCase()
    PublicActorTestCase()
    CastingAssistantActorTestCase()
    CastingDirectorActorTestCase()
    ExecutiveProducerActorTestCase()
"""

import os
import unittest
from app import app, MOVIES_PER_PAGE, ACTORS_PER_PAGE
from models import setup_db, Movie, Actor

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

    def test_movie_get_method_not_allowed_fail(self):
        """Test that get method is not allowed at /movies/id endpoint."""
        response = self.client().get("/movies/1")

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "method_not_allowed")

    def test_movie_post_method_not_allowed_fail(self):
        """Test that post method is not allowed at /movies/id endpoint."""
        response = self.client().post("/movies/1")

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
        self.assertEqual(len(response.json.get("movies")), MOVIES_PER_PAGE)
        self.assertGreater(response.json.get("total_movies"), MOVIES_PER_PAGE)

    def test_get_paginated_movies_out_of_range_fail(self):
        """Test failed movie retrieval when page number is out of range."""
        total_pages = -(-Movie.query.count() // MOVIES_PER_PAGE)

        response = self.client().get(
            f"/movies?page={total_pages+1}", headers=self.headers
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "not_found")

    def test_movie_patch_auth_fail(self):
        """Test failed updating of a movie when unauthorized."""
        movie_id = Movie.query.order_by(Movie.id.desc()).first().id

        response = self.client().patch(
            f"/movies/{movie_id}", headers=self.headers
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "forbidden")


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
        """Test failed movie creation when unauthorized."""
        response = self.client().post("/movies", headers=self.headers)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "forbidden")

    def test_patch_movie_success(self):
        """Test successful update of a movie."""
        old_movie = Movie.query.order_by(Movie.id.desc()).first().format()
        movie_id = old_movie["id"]
        new_movie = {
            "title": "Iron Man",
            "release_date": "2008-05-02",
            "poster": (
                "https://m.media-amazon.com/images/M/MV5BMTczNTI2ODUwOF5BMl5Ba"
                "nBnXkFtZTcwMTU0NTIzMw@@._V1_SY1000_CR0,0,674,1000_AL_.jpg"
            ),
            "actors": ["Robert Downey Jr.", "Jeff Bridges"],
        }

        response = self.client().patch(
            f"/movies/{movie_id}", json=new_movie, headers=self.headers
        )

        movie = Movie.query.get(movie_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get("success"), True)
        self.assertEqual(response.json.get("updated_movie_id"), movie_id)
        self.assertEqual(response.json.get("old_movie"), old_movie)
        self.assertTrue(response.json.get("new_movie"))
        self.assertIsNotNone(movie)

    def test_patch_movie_unrecognized_actor_fail(self):
        """Test failed movie update when an actor doesn't exist in the db."""
        movie_id = Movie.query.order_by(Movie.id.desc()).first().id
        new_movie = {
            "title": "Iron Man",
            "release_date": "2008-05-02",
            "poster": (
                "https://m.media-amazon.com/images/M/MV5BMTczNTI2ODUwOF5BMl5Ba"
                "nBnXkFtZTcwMTU0NTIzMw@@._V1_SY1000_CR0,0,674,1000_AL_.jpg"
            ),
            "actors": [
                "Robert Downey Jr.",
                "Terrence Howard",
                "Jeff Bridges",
                "Gwyneth Paltrow",
            ],
        }

        response = self.client().patch(
            f"/movies/{movie_id}", json=new_movie, headers=self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "bad_request")

    def test_patch_movie_out_of_range_fail(self):
        """Test failed movie update when movie does not exist."""
        movie_id = Movie.query.order_by(Movie.id.desc()).first().id
        new_movie = {
            "title": "Iron Man",
            "release_date": "2008-05-02",
            "poster": (
                "https://m.media-amazon.com/images/M/MV5BMTczNTI2ODUwOF5BMl5Ba"
                "nBnXkFtZTcwMTU0NTIzMw@@._V1_SY1000_CR0,0,674,1000_AL_.jpg"
            ),
            "actors": ["Robert Downey Jr.", "Jeff Bridges"],
        }

        response = self.client().patch(
            f"/movies/{movie_id+1}", json=new_movie, headers=self.headers
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(
            response.json.get("error_code"), "unprocessable_entity"
        )

    def test_patch_movie_no_info_fail(self):
        """Test failed movie update when in info is given."""
        movie_id = Movie.query.order_by(Movie.id.desc()).first().id

        response = self.client().patch(
            f"/movies/{movie_id}", headers=self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "bad_request")

    def test_delete_movie_auth_fail(self):
        """Test failed movie deletion when unauthorized."""
        movie_id = Movie.query.order_by(Movie.id.desc()).first().id

        response = self.client().delete(
            f"/movies/{movie_id}", headers=self.headers
        )

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

    def test_delete_movie_success(self):
        """Test successful deletion of movie."""
        old_movie = Movie.query.order_by(Movie.id.desc()).first().format()
        movie_id = old_movie["id"]

        response = self.client().delete(
            f"/movies/{movie_id}", headers=self.headers
        )

        movie = Movie.query.get(movie_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get("success"), True)
        self.assertEqual(response.json.get("deleted_movie_id"), movie_id)
        self.assertEqual(response.json.get("old_movie"), old_movie)
        self.assertIsNone(response.json.get("new_movie"))
        self.assertIsNone(movie)

    def test_delete_movie_out_of_range_fail(self):
        """Test failed movie deletion when movie does not exist."""
        movie_id = Movie.query.order_by(Movie.id.desc()).first().id

        response = self.client().delete(
            f"/movies/{movie_id+1}", headers=self.headers
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(
            response.json.get("error_code"), "unprocessable_entity"
        )


class PublicActorTestCase(unittest.TestCase):
    """Contains the test cases for the public actor endpoints.

    Attributes:
        app: A flask app from app.py
        client: A test client for the flask app to use while testing
        database_url: A str representing the location of the db used for
            testing
    """

    def setUp(self):
        """Set-up for PublicActorTestCase."""
        self.app = app
        app.config["DEBUG"] = False
        self.client = self.app.test_client
        self.database_url = TEST_DATABASE_URL
        setup_db(self.app, self.database_url)

    def tearDown(self):
        """Executed after each test."""

    def test_get_paginated_actors_auth_fail(self):
        """Test failed retrieval of actors when not authenticated."""
        response = self.client().get("/actors")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(
            response.json.get("error_code"), "authorization_header_missing"
        )

    def test_actors_patch_method_not_allowed_fail(self):
        """Test that patch method is not allowed at /actors endpoint."""
        response = self.client().patch("/actors")

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "method_not_allowed")

    def test_actors_delete_method_not_allowed_fail(self):
        """Test that delete method is not allowed at /actors endpoint."""
        response = self.client().delete("/actors")

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "method_not_allowed")


class CastingAssistantActorTestCase(unittest.TestCase):
    """Contains the test cases for the casting assistant actor endpoints.

    Attributes:
        headers: A dict representing the auth headers to be sent with requests
        app: A flask app from app.py
        client: A test client for the flask app to use while testing
        database_url: A str representing the location of the db used for
            testing
    """

    def setUp(self):
        """Set-up for CastingAssistantActorTestCase."""
        self.headers = {"Authorization": f"Bearer {CASTING_ASSISTANT_TOKEN}"}
        self.app = app
        app.config["DEBUG"] = False
        self.client = self.app.test_client
        self.database_url = TEST_DATABASE_URL
        setup_db(self.app, self.database_url)

    def tearDown(self):
        """Executed after each test."""

    def test_get_paginated_actors_success(self):
        """Test successful retrieval of actors."""
        response = self.client().get("/actors", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get("success"), True)
        self.assertEqual(len(response.json.get("actors")), ACTORS_PER_PAGE)
        self.assertGreater(response.json.get("total_actors"), ACTORS_PER_PAGE)

    def test_get_paginated_actors_out_of_range_fail(self):
        """Test failed actor retrieval when page number is out of range."""
        total_pages = -(-Actor.query.count() // ACTORS_PER_PAGE)

        response = self.client().get(
            f"/actors?page={total_pages+1}", headers=self.headers
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "not_found")

    def test_create_actor_auth_fail(self):
        """Test failed actor creation when unauthorized."""
        response = self.client().post("/actors", headers=self.headers)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "forbidden")

    def test_actor_patch_auth_fail(self):
        """Test failed updating of an actor when unauthorized."""
        actor_id = Actor.query.order_by(Actor.id.desc()).first().id

        response = self.client().patch(
            f"/actors/{actor_id}", headers=self.headers
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "forbidden")


class CastingDirectorActorTestCase(unittest.TestCase):
    """Contains the test cases for the casting director actor endpoints.

    Attributes:
        headers: A dict representing the auth headers to be sent with requests
        app: A flask app from app.py
        client: A test client for the flask app to use while testing
        database_url: A str representing the location of the db used for
            testing
    """

    def setUp(self):
        """Set-up for CastingDirectorActorTestCase."""
        self.headers = {"Authorization": f"Bearer {CASTING_DIRECTOR_TOKEN}"}
        self.app = app
        app.config["DEBUG"] = False
        self.client = self.app.test_client
        self.database_url = TEST_DATABASE_URL
        setup_db(self.app, self.database_url)

    def tearDown(self):
        """Executed after each test."""

    def test_create_actor_success(self):
        """Test successful creation of a actor."""
        new_actor = {
            "name": "Jeremy Renner",
            "birthdate": "1971-01-07",
            "gender": "male",
            "image": (
                "https://image.tmdb.org/t/p/w500/ycFVAVMliCCf0zXsKWNLBG3Yxz"
                "K.jpg"
            ),
            "movies": ["Avengers: Endgame", "The Avengers"],
        }

        response = self.client().post(
            "/actors", json=new_actor, headers=self.headers
        )

        created_actor_id = response.json.get("created_actor_id")
        actor = Actor.query.get(created_actor_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get("success"), True)
        self.assertIsNone(response.json.get("old_actor"))
        self.assertTrue(response.json.get("new_actor"))
        self.assertIsNotNone(actor)

    def test_create_actor_unrecognized_movie_fail(self):
        """Test failed actor creation when a movie doesn't exist in the db."""
        new_actor = {
            "name": "Jeremy Renner",
            "birthdate": "1971-01-07",
            "gender": "male",
            "image": (
                "https://image.tmdb.org/t/p/w500/ycFVAVMliCCf0zXsKWNLBG3Yxz"
                "K.jpg"
            ),
            "movies": [
                "Avengers: Endgame",
                "Captain America: Civil War",
                "Avengers: Age of Ultron",
                "The Avengers",
                "Thor",
            ],
        }

        response = self.client().post(
            "/actors", json=new_actor, headers=self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "bad_request")

    def test_create_actor_no_info_fail(self):
        """Test failed actor creation when info is missing."""
        response = self.client().post("/actors", headers=self.headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "bad_request")

    def test_patch_actor_success(self):
        """Test successful update of an actor."""
        old_actor = Actor.query.order_by(Actor.id.desc()).first().format()
        actor_id = old_actor["id"]
        new_actor = {
            "name": "Tom Hiddleston	",
            "birthdate": "1981-02-09",
            "gender": "male",
            "image": (
                "https://image.tmdb.org/t/p/w500/qCoaGjDErox3MEsGrKeDAlRlZ1"
                "J.jpg"
            ),
            "movies": [
                "Avengers: Endgame",
                "Avengers: Infinity War",
                "The Avengers",
            ],
        }

        response = self.client().patch(
            f"/actors/{actor_id}", json=new_actor, headers=self.headers
        )

        actor = Actor.query.get(actor_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get("success"), True)
        self.assertEqual(response.json.get("updated_actor_id"), actor_id)
        self.assertEqual(response.json.get("old_actor"), old_actor)
        self.assertTrue(response.json.get("new_actor"))
        self.assertIsNotNone(actor)

    def test_patch_actor_unrecognized_actor_fail(self):
        """Test failed actor update when a movie doesn't exist in the db."""
        actor_id = Actor.query.order_by(Actor.id.desc()).first().id
        new_actor = {
            "name": "Tom Hiddleston	",
            "birthdate": "1981-02-09",
            "gender": "male",
            "image": (
                "https://image.tmdb.org/t/p/w500/qCoaGjDErox3MEsGrKeDAlRlZ1"
                "J.jpg"
            ),
            "movies": [
                "Avengers: Endgame",
                "Avengers: Infinity War",
                "Thor: Ragnarok",
                "Thor: The Dark World",
                "The Avengers",
                "Thor",
            ],
        }

        response = self.client().patch(
            f"/actors/{actor_id}", json=new_actor, headers=self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "bad_request")

    def test_patch_actor_out_of_range_fail(self):
        """Test failed actor update when actor does not exist."""
        actor_id = Actor.query.order_by(Actor.id.desc()).first().id
        new_actor = {
            "name": "Tom Hiddleston	",
            "birthdate": "1981-02-09",
            "gender": "male",
            "image": (
                "https://image.tmdb.org/t/p/w500/qCoaGjDErox3MEsGrKeDAlRlZ1"
                "J.jpg"
            ),
            "movies": [
                "Avengers: Endgame",
                "Avengers: Infinity War",
                "The Avengers",
            ],
        }

        response = self.client().patch(
            f"/actors/{actor_id+1}", json=new_actor, headers=self.headers
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(
            response.json.get("error_code"), "unprocessable_entity"
        )

    def test_patch_actor_no_info_fail(self):
        """Test failed actor update when in info is given."""
        actor_id = Actor.query.order_by(Actor.id.desc()).first().id

        response = self.client().patch(
            f"/actors/{actor_id}", headers=self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json.get("success"), False)
        self.assertEqual(response.json.get("error_code"), "bad_request")


if __name__ == "__main__":
    unittest.main()
