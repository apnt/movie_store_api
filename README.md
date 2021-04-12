# Movie Store API

This is a simple movie store api. It is a django/django rest framework service. 
It includes the implementation in Django and Django Rest Framework and the 
configuration for deployment in a docker container. 

## Requirements

This api is implemented with **Python 3.9**.
All dependencies are included in the `requirements.txt` file within the root folder.

# Structure
* The `movie_store_api/` directory is the actual Python package containing the api. 
  Here we configure the settings, set the top level urls (endpoints) etc.
* The `movie_store/` directory contains the `movie_store` app where the most part of 
  the movie store's functionality is implemented.
* The `iam/` directory contains the `iam` app where the authentication and user 
  management is implemented.
* The `common/` directory contains utilities, views etc. that may be used from multiple 
  apps and in various parts of the project.
  
# Execution
In order to run the api locally, the following can be run:

```python3.9 manage.py runserver```

**Note**: The database settings in `movie_store_api/settings.py` file may need to be 
updated in order to run locally (for example the db host should probably be updated to
`localhost`)

# Testing
The tests are implemented using `pytest` and `pytest-django`. They can be run with the 
following command (run in the repository's root directory):

```pytest ./```

The configuration of the test suite can be found in the `conftest.py` and `pytest.ini` files.

**Note**: As in the case of running the api locally, the database settings in 
`movie_store_api/settings.py` file may need to be updated in order to run the 
tests (for example the db host should probably be updated to `localhost`)

# Docker Container
The configuration in order to deploy in a docker container can be found in the `dockerfile` 
and `docker-compose.yml` files. In order to run the api in a docker container the following 
steps should be followed:

Build the api into a docker image using the `dockerfile` with the following command (run in the 
root directory):

```docker build -t movie_store .```

It is important to use the above tag for the image, because it is used in the `docker-compose.yml`.

Then run ```docker-compose up -d``` in order to deploy the image in a container. This command will
setup a postgres database, create a new schema in it, run the api's migrations and load an initial
fixture with some users, in order to be able to use the api right away.

The credentials of the initial users are:
1. `{"email": "admin@moviestore.com", "password": "123admin"}` for the user with admin rights.
2. `{"email": "user1@test.com", "password": "123user1"}` for the first user.
3. `{"email": "user2@test.com", "password": "123user2"}` for the second user.

These credentials are also used in the test suite. Due to the over-engineering in various parts of
this implementation, and since it is a technical skills demo, these credentials are exposed this way 
in order to avoid the further complexity of using a key/password sharing platform. Likewise, the 
private and public keys used for authentication, are left exposed in the settings file for the same
reason. In a production environment, these credentials and keys should not be exposed in such a way.
