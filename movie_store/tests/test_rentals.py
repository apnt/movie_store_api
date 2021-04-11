import pytest
from common.tests import data
from common.tests.utils import get_random_string
from .utils import get_random_movies

auth_url = '/iam/auth/'
rentals_url = '/store/rentals/'
rental_url = '/store/rentals/{rental_uuid}/'

# post/patch default arguments
request_args = {'content_type': 'application/json'}

# mark all tests as needing database access
pytestmark = pytest.mark.django_db


# rentals tests
def test_create_rental__unauthenticated(client):
    # get some random movies and try to rent them
    random_movies = get_random_movies(number_of_movies=3)
    for movie in random_movies:
        response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
        assert response.status_code == 401


def test_create_rental__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    # get some random movies and try to rent them
    random_movies = get_random_movies(number_of_movies=3)
    for movie in random_movies:
        response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
        assert response.status_code == 201


def test_create_rental__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    # get some random movies and try to rent them
    random_movies = get_random_movies(number_of_movies=3)
    for movie in random_movies:
        response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
        assert response.status_code == 201


def test_create_rental_of_already_rented_movie__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    # get a random movie and rent it
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    assert rental_response.status_code == 201

    # then try to rent it again
    rerental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    assert rerental_response.status_code == 400


def test_list_rentals__unauthenticated(client):
    response = client.get(rentals_url)
    assert response.status_code == 401


def test_list_rentals__user(client):
    # login as user 1
    client.post(auth_url, data.user1_credentials, **request_args)

    # rent some movies and then list them
    user_1_movies = get_random_movies(number_of_movies=3)
    for movie in user_1_movies:
        client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)

    response_1 = client.get(rentals_url)
    user_1_rentals = response_1.json()['results']
    assert response_1.status_code == 200
    assert len(user_1_rentals) == len(user_1_movies)
    assert all(r['user']['email'] == data.user1_credentials['email'] for r in user_1_rentals)
    assert set(r['movie']['title'] for r in user_1_rentals) == set(m.title for m in user_1_movies)

    # login as user 2
    client.post(auth_url, data.user2_credentials, **request_args)

    # ensure that the first users rentals are not visible
    empty_response = client.get(rentals_url)
    assert empty_response.status_code == 200
    assert len(empty_response.json()['results']) == 0

    # rent some movies for the second user and then list them (different number of movies from the first user)
    user_2_movies = get_random_movies(number_of_movies=5)
    for movie in user_2_movies:
        client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)

    response_2 = client.get(rentals_url)
    user_2_rentals = response_2.json()['results']
    assert response_2.status_code == 200
    assert len(user_2_rentals) == len(user_2_movies)
    assert all(r['user']['email'] == data.user2_credentials['email'] for r in user_2_rentals)
    assert set(m['movie']['title'] for m in user_2_rentals) == set(m.title for m in user_2_movies)


def test_list_rentals__admin(client):
    # login as user 1 and rent some movies
    client.post(auth_url, data.user1_credentials, **request_args)
    user_1_movies = get_random_movies(number_of_movies=3)
    for movie in user_1_movies:
        client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)

    # login as user 2 and rent some movies
    client.post(auth_url, data.user2_credentials, **request_args)
    user_2_movies = get_random_movies(number_of_movies=5)
    for movie in user_2_movies:
        client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)

    # login as admin rent some movies and ensure all rentals can be listed
    client.post(auth_url, data.admin_credentials, **request_args)
    admin_movies = get_random_movies(number_of_movies=1)
    for movie in admin_movies:
        client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)

    response = client.get(rentals_url)
    all_rentals = response.json()['results']
    assert response.status_code == 200
    assert len(all_rentals) == len(user_1_movies) + len(user_2_movies) + len(admin_movies)


def test_retrieve_rental__unauthenticated(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # logout and try to retrieve the rental
    client.delete(auth_url)
    response = client.get(new_rental_url)
    assert response.status_code == 401


def test_retrieve_rental__user(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # retrieve the rental
    response = client.get(new_rental_url)
    assert response.status_code == 200
    assert response.json()['user']['email'] == data.user1_credentials['email']
    assert response.json()['movie']['title'] == movie.title

    # login as user 2 and try to retrieve the rental
    client.post(auth_url, data.user2_credentials, **request_args)
    response = client.get(new_rental_url)
    assert response.status_code == 404


def test_retrieve_rental__admin(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # login as admin and retrieve the rental
    client.post(auth_url, data.admin_credentials, **request_args)
    response = client.get(new_rental_url)
    assert response.status_code == 200
    assert response.json()['user']['email'] == data.user1_credentials['email']
    assert response.json()['movie']['title'] == movie.title


# partial update tests - since the only update can be to return the rental, these tests are named accordingly
def test_return_rental__unauthenticated(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # logout and try to return the rental
    client.delete(auth_url)
    response = client.patch(new_rental_url, {'returned': True}, **request_args)
    assert response.status_code == 401


def test_return_rental__user(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # return the rental
    response = client.patch(new_rental_url, {'returned': True}, **request_args)
    assert response.status_code == 200
    assert response.json()['payment'] is not None and response.json()['return_date'] is not None
    assert 'fee' not in response.json()


def test_return_rental_again__user(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # return the rental
    return_response = client.patch(new_rental_url, {'returned': True}, **request_args)
    assert return_response.status_code == 200

    # try to return again
    rereturn_response = client.patch(new_rental_url, {'returned': True}, **request_args)
    assert rereturn_response.status_code == 400


def test_ractivate_rental__user(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # return the rental
    return_response = client.patch(new_rental_url, {'returned': True}, **request_args)
    assert return_response.status_code == 200

    # try to reactivate
    rereturn_response = client.patch(new_rental_url, {'returned': False}, **request_args)
    assert rereturn_response.status_code == 400


def test_return_other_user_rental__user(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # login as user 2 and try to return the rental
    client.post(auth_url, data.user2_credentials, **request_args)
    response = client.patch(new_rental_url, {'returned': True}, **request_args)
    assert response.status_code == 404


def test_return_other_user_rental__admin(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # login as admin and return the rental
    client.post(auth_url, data.admin_credentials, **request_args)
    response = client.patch(new_rental_url, {'returned': True}, **request_args)
    assert response.status_code == 200
    assert response.json()['payment'] is not None and response.json()['return_date'] is not None
    assert 'fee' not in response.json()


def test_delete_rental__unauthenticated(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # logout and try to delete the rental
    client.delete(auth_url)
    response = client.delete(new_rental_url)
    assert response.status_code == 401


def test_delete_rental__user(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # logout and try to delete the rental
    response = client.delete(new_rental_url)
    assert response.status_code == 403


def test_delete_other_user_rental__user(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # login as user 2 and try to delete the rental
    client.post(auth_url, data.user2_credentials, **request_args)
    response = client.delete(new_rental_url)
    assert response.status_code == 403


def test_delete_rental__admin(client):
    # login as admin and rent a movie
    client.post(auth_url, data.admin_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # delete the rental
    response = client.delete(new_rental_url)
    assert response.status_code == 204


def test_delete_other_user_rental__admin(client):
    # login as user 1 and rent a movie
    client.post(auth_url, data.user1_credentials, **request_args)
    movie = get_random_movies(number_of_movies=1)[0]
    rental_response = client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)
    new_rental_url = rental_response.json()['url']

    # login as admin and delete the rental
    client.post(auth_url, data.admin_credentials, **request_args)
    response = client.delete(new_rental_url)
    assert response.status_code == 204


def test_filter_rentals_by_user__user(client):
    # login as user 1 and rent some movies
    client.post(auth_url, data.user1_credentials, **request_args)
    user1_movies = get_random_movies(number_of_movies=3)
    for movie in user1_movies:
        client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)

    # list the rentals
    list_response = client.get(rentals_url)
    rentals = list_response.json()['results']
    assert list_response.status_code == 200
    assert len(rentals) == len(user1_movies)

    # when filtering by user as a simple user, we expect no change in any response
    # filter by self
    self_response = client.get(rentals_url, {'user': data.user1_uuid})
    assert self_response.status_code == 200
    assert len(self_response.json()['results']) == len(user1_movies)

    # filter by other user
    other_user_response = client.get(rentals_url, {'user': data.user2_uuid})
    assert other_user_response.status_code == 200
    assert len(other_user_response.json()['results']) == len(user1_movies)
    assert all(r['user']['email'] == data.user1_credentials['email'] for r in rentals)

    # filter by random string
    random_response = client.get(rentals_url, {'user': get_random_string(use_uppercase=False, use_punctuation=False)})
    assert random_response.status_code == 200
    assert len(random_response.json()['results']) == len(user1_movies)
    assert all(r['user']['email'] == data.user1_credentials['email'] for r in rentals)


def test_filter_rentals_by_user__admin(client):
    # login as user 1 and rent some movies
    client.post(auth_url, data.user1_credentials, **request_args)
    user1_movies = get_random_movies(number_of_movies=3)
    for movie in user1_movies:
        client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)

    # login as user 2 and rent some movies
    client.post(auth_url, data.user2_credentials, **request_args)
    user2_movies = get_random_movies(number_of_movies=5)
    for movie in user2_movies:
        client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)

    # login as admin
    client.post(auth_url, data.admin_credentials, **request_args)

    # list the rentals
    list_response = client.get(rentals_url)
    rentals = list_response.json()['results']
    assert list_response.status_code == 200
    assert len(rentals) == len(user1_movies) + len(user2_movies)

    # filter by self
    self_response = client.get(rentals_url, {'user': data.admin_uuid})
    assert self_response.status_code == 200
    assert len(self_response.json()['results']) == 0

    # filter by user 1
    user1_response = client.get(rentals_url, {'user': data.user1_uuid})
    user1_rentals = user1_response.json()['results']
    assert user1_response.status_code == 200
    assert len(user1_rentals) == len(user1_movies)

    # filter by user 2
    user2_response = client.get(rentals_url, {'user': data.user2_uuid})
    user2_rentals = user2_response.json()['results']
    assert user1_response.status_code == 200
    assert len(user2_rentals) == len(user2_movies)

    # filter by random string
    random_response = client.get(rentals_url, {'user': get_random_string(use_uppercase=False, use_punctuation=False)})
    assert random_response.status_code == 200
    assert len(random_response.json()['results']) == 0


def test_filter_rentals_by_movie__user(client):
    # login as user 1 and rent some movies
    client.post(auth_url, data.user1_credentials, **request_args)
    user1_movies = get_random_movies(number_of_movies=3)
    for movie in user1_movies:
        client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)

    # list the rentals
    list_response = client.get(rentals_url)
    rentals = list_response.json()['results']
    assert list_response.status_code == 200
    assert len(rentals) == len(user1_movies)

    # filter by movie
    movie_response = client.get(rentals_url, {'movie': str(user1_movies[0].uuid)})
    assert movie_response.status_code == 200
    assert len(movie_response.json()['results']) == 1

    # filter by random string
    random_response = client.get(rentals_url, {'movie': get_random_string(use_uppercase=False, use_punctuation=False)})
    assert random_response.status_code == 200
    assert len(random_response.json()['results']) == 0


def test_filter_rentals_by_status__user(client):
    # login as user 1 and rent some movies
    client.post(auth_url, data.user1_credentials, **request_args)
    number_of_rentals = 5
    user1_movies = get_random_movies(number_of_movies=number_of_rentals)
    for movie in user1_movies:
        client.post(rentals_url, {'movie': str(movie.uuid)}, **request_args)

    # list the rentals
    list_response = client.get(rentals_url)
    rentals = list_response.json()['results']
    assert list_response.status_code == 200
    assert len(rentals) == len(user1_movies)

    # return some of them
    number_of_returns = 2
    for i in range(0, number_of_returns):
        client.patch(rentals[i]['url'], {'returned': True}, **request_args)

    # filter by status
    active_response = client.get(rentals_url, {'status': 'active'})
    assert active_response.status_code == 200
    assert len(active_response.json()['results']) == number_of_rentals - number_of_returns

    # filter by random string
    random_response = client.get(rentals_url, {'status': 'returned'})
    assert random_response.status_code == 200
    assert len(random_response.json()['results']) == number_of_returns
