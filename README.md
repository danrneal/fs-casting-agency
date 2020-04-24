# Casting Agency

## Set-up

Set-up a virtual environment and activate it:

```bash
python3 -m venv env
source env/bin/activate
```

You should see (env) before your command prompt now. (You can type `deactivate` to exit the virtual environment any time.)

Install the requirements:

```bash
pip install -U pip
pip install -r requirements.txt
```

set up an Auth0 domain at [Auth0](https://auth0.com/)

Set up your environment variables:

```bash
touch .env
echo AUTH0_DOMAIN="XXX.auth0.com" >> .env
echo API_IDENTIFIER="XXX" >> .env
echo DATABASE_URL="postgresql://XXX:5432/movies" >> .env
```

Initialize and set up the database:

```bash
dropdb movies
createdb movies
psql movies < movies.psql
```

## Usage

Make sure you are in the virtual environment (you should see (env) before your command prompt). If not `source /env/bin/activate` to enter it.

Make sure .env variables are set:

```bash
set -a; source .env; set +a
```

Then run the server:

```bash
Usage: app.py
```

<!-- ## Screenshots -->

## API Reference

### Base URL

When running locally with the built in flask server, the base url is as follows:

```bash
http://0.0.0.0:8080/
```

### Error Handling

Below are a list of errors that may be raised as part of the api

#### 400: Bad Request

This is returned when the requested is malformed in some way. (i.e. Required info is missing)

#### 401: Unauthorized

This is returned when accessing a non-public endpoint while unauthenticated. (i.e. User is not logged in)

##### authorization_header_missing

This is the error when there is no header for authorization included with the request.

##### invalid_header

This is the error when the authorization header is malformed in some way. (i.e. The token is in the incorrect format)

##### token_expired

This is the error when the provided token is expired and the user must re-login

##### invalid_claims

This is error if the token is invalid in any other way. (i.e. The token has been modified or the permissions object is missing)

#### 403: Forbidden

This is returned when accessing a resource you are not authorized to access. (i.e. User is logged in but does not have sufficient permissions to access the requested resource)

#### 404: Not Found

This is returned when the requested resource does not exist.

#### 405: Method Not Allowed

This is returned when the incorrect request method is specified at an endpoint. (i.e. Attempting to delete without specifying a specific movie or actor to delete)

#### 422: Unprocessable Entity

This is returned when the request is unable to be fulfilled in some way. (i.e. Attempting to update a movie or actor that has previously been deleted)

#### 500: Internal Server Error

This is returned when something there is a problem with the server.

### Endpoints

Movies:

#### GET /movies

Required Permissions: `read:movies`

Example Request:

```bash
curl -H "Authorization: Bearer <token>" http://0.0.0.0:8080/movies?page=1
```

Parameters:

- page (int) [optional]: Each page returns the next 25 results (default: 1)

Example Response:

```bash
{
  "success": true,
  "movies": [
    {
      "id": 55,
      "title": "Avengers: Endgame",
      "release_date": "2019-04-26",
      "poster": "https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_SX300.jpg",
      "actors": [
        {
          "id": 168,
          "name": "Robert Downey Jr."
        },
        {
          "id": 204,
          "name": "Chris Evans"
        },

        {
          "id": 194,
          "name": "Mark Ruffalo"
        },
        {
          "id": 137,
          "name": "Chris Hemsworth"
        }
      ]
    },
    {
      "id": 48,
      "title": "Avengers: Infinity War",
      "release_date": "2018-04-27",
      "poster": "https://m.media-amazon.com/images/M/MV5BMjMxNjY2MDU1OV5BMl5BanBnXkFtZTgwNzY1MTUwNTM@._V1_SX300.jpg",
      "actors": [
        {
          "id": 168,
          "name": "Robert Downey Jr."
        },
        {
          "id": 137,
          "name": "Chris Hemsworth"
        },
        {
          "id": 194,
          "name": "Mark Ruffalo"
        },
        {
          "id": 204,
          "name": "Chris Evans"
        }
      ]
    },
    {
      "id": 219,
      "title": "The Avengers",
      "release_date": "2012-05-04",
      "poster": "https://m.media-amazon.com/images/M/MV5BNDYxNjQyMjAtNTdiOS00NGYwLWFmNTAtNThmYjU5ZGI2YTI1XkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
      "actors": [
        {
          "id": 168,
          "name": "Robert Downey Jr."
        },
        {
          "id": 204,
          "name": "Chris Evans"
        },
        {
          "id": 194,
          "name": "Mark Ruffalo"
        },
        {
          "id": 137,
          "name": "Chris Hemsworth"
        }
      ]
    }
  ],
  "total_movies": 3
}
```

#### POST /movies

Required Permissions: `create:movies`

Example Request:

```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <token>" -d '{"title": "Black Widow", "release_date": "2020-11-06", "poster": "https://m.media-amazon.com/images/M/MV5BZGRlNTY3NGYtM2YzZS00N2YyLTg0ZDYtNmY2ZDg2NDM3N2JlXkEyXkFqcGdeQXVyNTI4MzE4MDU@._V1_SY1000_CR0,0,675,1000_AL_.jpg", "actors": ["Scarlett Johansson", "Robert Downey Jr."]}' http://0.0.0.0:8080/movies
```

Parameters:

- title (str): Title of the movie
- release_date (str): Release date of the movie "YYYY-MM-DD"
- poster (str): Url of the movie poster
- actors (list): A list of strs representing names of actors starring in the movie

Example Response:

```bash
{
  "success": true,
  "created_movie_id": 251,
  "old_movie": null,
  "new_movie": {
    "id": 251,
    "title": "Black Widow",
    "release_date": "2020-11-06",
    "poster": "https://m.media-amazon.com/images/M/MV5BZGRlNTY3NGYtM2YzZS00N2YyLTg0ZDYtNmY2ZDg2NDM3N2JlXkEyXkFqcGdeQXVyNTI4MzE4MDU@._V1_SY1000_CR0,0,675,1000_AL_.jpg",
    "actors": [
      {
        "id": 235,
        "name": "Scarlett Johansson"
      },
      {
        "id": 168,
        "name": "Robert Downey Jr."
      }
    ]
  }
}
```

#### PATCH /movies/<movie_id>

Required Permissions: `update:movies`

Example Request:

```bash
curl -X PATCH -H "Content-Type: application/json" -H "Authorization: Bearer <token>" -d '{"title": "Iron Man", "release_date": "2008-05-02", "poster": "https://m.media-amazon.com/images/M/MV5BMTczNTI2ODUwOF5BMl5BanBnXkFtZTcwMTU0NTIzMw@@._V1_SY1000_CR0,0,674,1000_AL_.jpg", "actors": ["Robert Downey Jr.", "Jeff Bridges"]}' http://0.0.0.0:8080/movies/251
```

Parameters:

- title (str) [optional]: Title of the movie
- release_date (str) [optional]: Release date of the movie "YYYY-MM-DD"
- poster (str) [optional]: Url of the movie poster
- actors (list) [optional]: A list of strs representing names of actors starring in the movie

Example Response:

```bash
{
  "success": true,
  "updated_movie_id": 251,
  "old_movie": {
    "id": 251,
    "title": "Black Widow",
    "release_date": "2020-11-06",
    "poster": "https://m.media-amazon.com/images/M/MV5BZGRlNTY3NGYtM2YzZS00N2YyLTg0ZDYtNmY2ZDg2NDM3N2JlXkEyXkFqcGdeQXVyNTI4MzE4MDU@._V1_SY1000_CR0,0,675,1000_AL_.jpg",
    "actors": [
      {
        "id": 235,
        "name": "Scarlett Johansson"
      },
      {
        "id": 168,
        "name": "Robert Downey Jr."
      }
    ]
  },
  "new_movie": {
    "id": 251,
    "title": "Iron Man",
    "release_date": "2008-05-02",
    "poster": "https://m.media-amazon.com/images/M/MV5BMTczNTI2ODUwOF5BMl5BanBnXkFtZTcwMTU0NTIzMw@@._V1_SY1000_CR0,0,674,1000_AL_.jpg",
    "actors": [
      {
        "id": 168,
        "name": "Robert Downey Jr."
      },
      {
        "id": 18,
        "name": "Jeff Bridges"
      }
    ]
  }
}
```

#### DELETE /movies/<movie_id>

Required Permissions: `delete:movies`

Example Request:

```bash
curl -X DELETE -H "Authorization: Bearer <token>" http://0.0.0.0:8080/movies/251
```

Example Response:

```bash
{
  "success": true,
  "deleted_movie_id": 251,
  "old_movie": {
    "title": "Iron Man",
    "id": 251,
    "release_date": "2008-05-02",
    "poster": "https://m.media-amazon.com/images/M/MV5BMTczNTI2ODUwOF5BMl5BanBnXkFtZTcwMTU0NTIzMw@@._V1_SY1000_CR0,0,674,1000_AL_.jpg",
    "actors": [
      {
        "id": 168,
        "name": "Robert Downey Jr."
      },
      {
        "id": 18,
        "name": "Jeff Bridges"
      }
    ]
  },
  "new_movie": null
}
```

Actors:

#### GET /actors

Required Permissions: `read:actors`

Example Request:

```bash
curl -H "Authorization: Bearer <token>" http://0.0.0.0:8080/actors?page=1
```

Parameters:

- page (int) [optional]: Each page returns the next 25 results (default: 1)

Example Response:

```bash
{
  "success": true,
  "actors": [
    {
      "id": 18,
      "name": "Jeff Bridges",
      "birthdate": "1949-12-04",
      "gender": "male",
      "image": "https://image.tmdb.org/t/p/w500/xms1RAY6q7Lzp7wNeRCB0kzhucn.jpg",
      "movies": [
        {
          "id": 145,
          "title": "The Big Lebowski",
          "release_date": "1998-03-06"
        },
        {
          "id": 239,
          "title": "The Last Picture Show",
          "release_date": "1971-10-22"
        }
      ]
    },
    {
      "id": 168,
      "name": "Robert Downey Jr.",
      "birthdate": "1965-04-04",
      "gender": "male",
      "image": "https://image.tmdb.org/t/p/w500/5qHNjhtjMD4YWH3UP0rm4tKwxCL.jpg",
      "movies": [
        {
          "id": 55,
          "title": "Avengers: Endgame",
          "release_date": "2019-04-26"
        },
        {
          "id": 48,
          "title": "Avengers: Infinity War",
          "release_date": "2018-04-27"
        },

        {
          "id": 219,
          "title": "The Avengers",
          "release_date": "2012-05-04"
        }
      ]
    },
    {
      "id": 235,
      "name": "Scarlett Johansson",
      "birthdate": "1984-11-22",
      "gender": "female",
      "image": "https://image.tmdb.org/t/p/w500/6NsMbJXRlDZuDzatN2akFdGuTvx.jpg",
      "movies": [
        {
          "id": 242,
          "title": "Marriage Story",
          "release_date": "2019-12-06"
        }
      ]
    }
  ],
  "total_actors": 3
}
```

#### POST /actors

Required Permissions: create:actors

Example Request:

```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <token>" -d '{"name": "Jeremy Renner", "birthdate": "1971-01-07", "gender": "male", "image": "https://image.tmdb.org/t/p/w500/ycFVAVMliCCf0zXsKWNLBG3YxzK.jpg", "movies": ["Avengers: Endgame", "The Avengers"]}' http://0.0.0.0:8080/actors
```

Parameters:

- name (str): Name of the actor
- birthdate (str): Birthdate of the actor "YYYY-MM-DD"
- gender (str): The actor's gender
- image (str): Url of an image of the actor
- movies (list): A list of strs representing titles of movies the actor has starred in

Example Response:

```bash
{
  "success": true,
  "created_actor_id": 621,
  "old_actor": null,
  "new_actor": {
    "id": 621,
    "name": "Jeremy Renner",
    "birthdate": "1971-01-07",
    "gender": "male",
    "image": "https://image.tmdb.org/t/p/w500/ycFVAVMliCCf0zXsKWNLBG3YxzK.jpg",
    "movies": [
      {
        "id": 55,
        "title": "Avengers: Endgame",
        "release_date": "2019-04-26"
      },
      {
        "id": 219,
        "title": "The Avengers",
        "release_date": "2012-05-04"
      }
    ]
  }
}
```

#### PATCH /actors/<actor_id>

Required Permissions: `update:actors`

Example Request:

```bash
curl -X PATCH -H "Content-Type: application/json" -H "Authorization: Bearer <token>" -d '{"name": "Tom Hiddleston", "birthdate": "1981-02-09", "gender": "male", "image": "https://image.tmdb.org/t/p/w500/qCoaGjDErox3MEsGrKeDAlRlZ1J.jpg", "movies": ["Avengers: Endgame", "Avengers: Infinity War", "The Avengers"]}' http://0.0.0.0:8080/actors/621
```

Parameters:

- name (str) [optional]: Name of the actor
- birthdate (str) [optional]: Birthdate of the actor "YYYY-MM-DD"
- gender (str) [optional]: The actor's gender
- image (str) [optional]: Url of an image of the actor
- movies (list) [optional]: A list of strs representing titles of movies the actor has starred in

Example Response:

```bash
{
  "success": true,
  "updated_actor_id": 621,
  "old_actor": {
    "id": 621,
    "name": "Jeremy Renner",
    "birthdate": "1971-01-07",
    "gender": "male",
    "image": "https://image.tmdb.org/t/p/w500/ycFVAVMliCCf0zXsKWNLBG3YxzK.jpg",
    "movies": [
      {
        "id": 55,
        "title": "Avengers: Endgame",
        "release_date": "2019-04-26"
      },
      {
        "id": 219,
        "title": "The Avengers",
        "release_date": "2012-05-04"
      }
    ]
  },
  "new_actor": {
    "id": 621,
    "name": "Tom Hiddleston",
    "birthdate": "1981-02-09",
    "gender": "male",
    "image": "https://image.tmdb.org/t/p/w500/qCoaGjDErox3MEsGrKeDAlRlZ1J.jpg",
    "movies": [
      {
        "id": 55,
        "title": "Avengers: Endgame",
        "release_date": "2019-04-26"
      },
      {
        "id": 48,
        "release_date": "2018-04-27",
        "title": "Avengers: Infinity War"
      },
      {
        "id": 219,
        "title": "The Avengers",
        "release_date": "2012-05-04"
      }
    ]
  }
}
```

#### DELETE /actors/<actor_id>

Required Permissions: `delete:actors`

Example Request:

```bash
curl -X DELETE -H "Authorization: Bearer <token>" http://0.0.0.0:8080/actors/621
```

Example Response:

```bash
{
  "success": true,
  "deleted_actor_id": 621,
  "old_actor": {
    "id": 621,
    "name": "Tom Hiddleston",
    "birthdate": "1981-02-09",
    "gender": "male",
    "image": "https://image.tmdb.org/t/p/w500/qCoaGjDErox3MEsGrKeDAlRlZ1J.jpg",
    "movies": [
      {
        "id": 55,
        "title": "Avengers: Endgame",
        "release_date": "2019-04-26"
      },
      {
        "id": 48,
        "title": "Avengers: Infinity War",
        "release_date": "2018-04-27"
      },
      {
        "id": 219,
        "release_date": "2012-05-04",
        "title": "The Avengers"
      }
    ]
  },
  "new_actor": null
}
```

## Testing Suite

The API has a testing suite to test all of the API endpoints.

To set up the test database:

```bash
dropdb movies_test
createdb movies_test
psql movies_test < movies.psql
```

Set the test database url and casting assistant, casting director, and executive producer tokens from Auth0 in your environmental variables:

```bash
echo TEST_DATABASE_URL="postgresql://XXX:5432/movies_test" >> .env
echo CASTING_ASSISTANT_TOKEN="XXX" >> .env
echo CASTING_DIRECTOR_TOKEN="XXX" >> .env
echo EXECUTIVE_PRODUCER_TOKEN="XXX" >> .env
set -a; source .env; set +a
```

To run all the tests:

```bash
Usage: test_flaskr.py
```

## Credit

[Udacity's Full Stack Web Developer Nanodegree Program](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044)

## License

Casting Agency is licensed under the [MIT license](https://github.com/danrneal/casting-agency/blob/master/LICENSE).
