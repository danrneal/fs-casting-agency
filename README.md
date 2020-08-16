# FS Casting Agency

This is an app for a casting agency that is responsible for creating movies and managing and assigning actors to those movies. The motivation for the app is to create a system to simplify and streamline the process. This flask-based app features a PostgreSQL database and uses role based access controls on Auth0 for authentication. Casting assistants can view actors and movies, casting directors can add, update, and delete actors as well as update movies, and finally executive producers can add and delete movies.

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

Set up an Auth0 domain at [Auth0](https://auth0.com/).

- Create a single page app
- Set "Allowed Callback URLs", "Allowed Logout URLs", and "Allowed Web Origins" to `http://127.0.0.1:5000`
- Create an API
- Check the options "Enable RBAC" and "Add Permissions in the Access Token"

Set up your environment variables:

```bash
touch .env
echo AUTH0_DOMAIN="XXX.auth0.com" >> .env
echo AUTH0_CLIENT_ID="XXX" >> .env
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

You can run this app either locally or deploy it to Heroku.

### Local

Make sure you are in the virtual environment (you should see (env) before your command prompt). If not `source /env/bin/activate` to enter it.

```bash
Usage: flask run
```

### Heroku

You will need the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed. On Ubuntu:

```bash
sudo snap install --classic heroku
```

Then you can setup PostgreSQL and deploy to Heroku.

```bash
heroku create fs-casting-agency
heroku addons:create heroku-postgresql:hobby-dev --app fs-casting-agency
heroku pg:push movies DATABASE_URL --app fs-casting-agency
git push heroku master
```

## Screenshots

![FS Casting Agency Home Page](https://i.imgur.com/8dMWCwG.png)

![FS Casting Agency Modal](https://i.imgur.com/DfeWQku.png)

![FS Casting Agency Update Form](https://i.imgur.com/VHw8Wwb.png)

## API Reference

The API reference documentation is available [here](https://documenter.getpostman.com/view/10868159/SzfDxQmn?version=latest).

## Example

There is currently an example running on Heroku [here](https://fs-casting-agency.herokuapp.com/). Below are a variety of test users with differing role-based permissions assigned.

```csv
email:password
casting_assistant@fscastingagency.com:CastingAssistant1
casting_director@fscastingagency.com:CastingDirector1
executive_producer@fscastingagency.com:ExecutiveProducer1
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
Usage: test_app.py
```

## Credit

[Udacity's Full Stack Web Developer Nanodegree Program](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044)

## License

FS Casting Agency is licensed under the [MIT license](https://github.com/danrneal/fs-casting-agency/blob/master/LICENSE).
