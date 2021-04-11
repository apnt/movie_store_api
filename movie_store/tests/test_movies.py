import pytest
from common.tests import data
from movie_store.data.sample_data import genres, movies
from movie_store.models import Movie
from .utils import get_random_movies

auth_url = '/iam/auth/'
movies_url = '/store/movies/'
movie_url = '/store/movies/{movie_uuid}/'
library_url = '/store/movies/library/'
rentals_url = '/store/rentals/'

# post/patch default arguments
request_args = {'content_type': 'application/json'}

# mark all tests as needing database access
pytestmark = pytest.mark.django_db


# movies tests
def test_list_movies__unauthenticated(client):
    response = client.get(movies_url)
    assert response.status_code == 401


def test_list_movies__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    response = client.get(movies_url)
    assert response.status_code == 200


def test_list_movies__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    response = client.get(movies_url)
    assert response.status_code == 200


def test_retrieve_movie__unauthenticated(client):
    all_movies = Movie.objects.all()
    for movie in all_movies:
        response = client.get(movie_url.format(movie_uuid=str(movie.uuid)))
        assert response.status_code == 401


def test_retrieve_movie__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    all_movies = Movie.objects.all()
    for movie in all_movies:
        response = client.get(movie_url.format(movie_uuid=str(movie.uuid)))
        assert response.status_code == 200
        assert response.json()['title'] == movie.title


def test_retrieve_movie__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    all_movies = Movie.objects.all()
    for movie in all_movies:
        response = client.get(movie_url.format(movie_uuid=str(movie.uuid)))
        assert response.status_code == 200
        assert response.json()['title'] == movie.title


def test_create_movie__unauthenticated(client):
    response = client.post(movies_url, data.new_movie_data, **request_args)
    assert response.status_code == 401


def test_create_movie__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    response = client.post(movies_url, data.new_movie_data, **request_args)
    assert response.status_code == 403


def test_create_movie__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    response = client.post(movies_url, data.new_movie_data, **request_args)
    assert response.status_code == 201
    assert all(response.json()[k] == data.new_movie_data[k] for k in data.new_movie_data.keys())


def test_create_movie_genre_does_not_exist__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    new_movie_data = dict(data.new_movie_data, genres=['Test'])
    response = client.post(movies_url, new_movie_data, **request_args)
    assert response.status_code == 400


def test_partial_update_movie__unauthenticated(client):
    all_movies = Movie.objects.all()
    for movie in all_movies:
        updated_title = 'Updated {}'.format(movie.title)
        response = client.patch(movie_url.format(movie_uuid=str(movie.uuid)), {'title': updated_title}, **request_args)
        assert response.status_code == 401


def test_partial_update_movie__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    all_movies = Movie.objects.all()
    for movie in all_movies:
        updated_title = 'Updated {}'.format(movie.title)
        response = client.patch(movie_url.format(movie_uuid=str(movie.uuid)), {'title': updated_title}, **request_args)
        assert response.status_code == 403


def test_partial_update_movie__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    all_movies = Movie.objects.all()
    for movie in all_movies:
        updated_title = 'Updated {}'.format(movie.title)
        response = client.patch(movie_url.format(movie_uuid=str(movie.uuid)), {'title': updated_title}, **request_args)
        assert response.status_code == 200
        assert response.json()['title'] == updated_title


def test_delete_movie__unauthenticated(client):
    all_movies = Movie.objects.all()
    for movie in all_movies:
        response = client.delete(movie_url.format(movie_uuid=str(movie.uuid)))
        assert response.status_code == 401


def test_delete_movie__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    all_movies = Movie.objects.all()
    for movie in all_movies:
        response = client.delete(movie_url.format(movie_uuid=str(movie.uuid)))
        assert response.status_code == 403


def test_delete_movie__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    all_movies = Movie.objects.all()
    for movie in all_movies:
        response = client.delete(movie_url.format(movie_uuid=str(movie.uuid)))
        assert response.status_code == 204
    remaining_movies = Movie.objects.all()
    assert len(remaining_movies) == 0


def test_filter_movies_by_year__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    years = set([m['year'] for m in movies])
    for year in years:
        movies_released_that_year = [movie for movie in movies if movie['year'] == year]
        response = client.get(movies_url, {'year': year})
        assert response.status_code == 200
        assert len(response.json()['results']) == len(movies_released_that_year)


def test_filter_movies_by_director__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    directors = set([m['director'] for m in movies])
    for director in directors:
        movies_by_that_director = [movie for movie in movies if movie['director'] == director]
        response = client.get(movies_url, {'director': director})
        assert response.status_code == 200
        assert len(response.json()['results']) == len(movies_by_that_director)


def test_filter_movies_by_one_genre__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    for genre in genres:
        movies_of_this_genre = [movie for movie in movies if genre in movie['genres']]
        response = client.get(movies_url, {'genre': genre})
        assert response.status_code == 200
        assert len(response.json()['results']) == len(movies_of_this_genre)


def test_filter_movies_by_multiple_genres__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    # test specific combinations
    combination_1 = ['Adventure', 'Fantasy', 'Action']  # should return the 3 Lord of the Rings movies
    combination_2 = ['Action', 'Science Fiction']  # should return Alita, Guardians of the Galaxy and 2 Avengers movies

    movies_for_comb_1 = [movie for movie in movies if all(genre in movie['genres'] for genre in combination_1)]
    movies_for_comb_2 = [movie for movie in movies if all(genre in movie['genres'] for genre in combination_2)]

    response_1 = client.get(movies_url, {'genre': ','.join(combination_1)})
    response_1_movies = response_1.json()['results']
    assert response_1.status_code == 200
    assert len(response_1_movies) == len(movies_for_comb_1)
    assert set(m['title'] for m in response_1_movies) == set(m['title'] for m in movies_for_comb_1)

    response_2 = client.get(movies_url, {'genre': ','.join(combination_2)})
    response_2_movies = response_2.json()['results']
    assert response_2.status_code == 200
    assert len(response_2_movies) == len(movies_for_comb_2)
    assert set(m['title'] for m in response_2_movies) == set(m['title'] for m in movies_for_comb_2)


def test_list_library__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)

    # get some random movies and rent them
    number_of_rentals = 3
    random_movies = get_random_movies(number_of_movies=number_of_rentals)
    for movie in random_movies:
        client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)

    # get the user's library, should return the rented random movies
    response = client.get(library_url)
    response_movies = response.json()['results']
    assert response.status_code == 200
    assert len(response.json()['results']) == number_of_rentals
    assert set(m['title'] for m in response_movies) == set(m.title for m in random_movies)

    # login as another user - library should be empty
    client.post(auth_url, data.user2_credentials, **request_args)
    second_response = client.get(library_url)
    assert second_response.status_code == 200
    assert len(second_response.json()['results']) == 0
