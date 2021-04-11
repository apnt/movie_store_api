import pytest
from common.tests import data
from movie_store.models import Genre

auth_url = '/iam/auth/'
genres_url = '/store/genres/'
genre_url = '/store/genres/{genre_uuid}/'

# post/patch default arguments
request_args = {'content_type': 'application/json'}

# mark all tests as needing database access
pytestmark = pytest.mark.django_db


# genres tests
def test_list_genres__unauthenticated(client):
    response = client.get(genres_url)
    assert response.status_code == 401


def test_list_genres__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    response = client.get(genres_url)
    assert response.status_code == 200


def test_list_genres__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    response = client.get(genres_url)
    assert response.status_code == 200


def test_retrieve_genre__unauthenticated(client):
    genres = Genre.objects.all()
    for genre in genres:
        response = client.get(genre_url.format(genre_uuid=str(genre.uuid)))
        assert response.status_code == 401


def test_retrieve_genre__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    genres = Genre.objects.all()
    for genre in genres:
        response = client.get(genre_url.format(genre_uuid=str(genre.uuid)))
        assert response.status_code == 200
        assert response.json()['name'] == genre.name


def test_retrieve_genre__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    genres = Genre.objects.all()
    for genre in genres:
        response = client.get(genre_url.format(genre_uuid=str(genre.uuid)))
        assert response.status_code == 200
        assert response.json()['name'] == genre.name


def test_create_genre__unauthenticated(client):
    response = client.post(genres_url, {'name': 'Test'}, **request_args)
    assert response.status_code == 401


def test_create_genre__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    response = client.post(genres_url, {'name': 'Test'}, **request_args)
    assert response.status_code == 403


def test_create_genre__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    response = client.post(genres_url, {'name': 'Test'}, **request_args)
    assert response.status_code == 201


def test_create_already_existing_genre__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    response = client.post(genres_url, {'name': 'Crime'}, **request_args)
    assert response.status_code == 400


def test_partial_update_genre__unauthenticated(client):
    genres = Genre.objects.all()
    for genre in genres:
        new_name = 'Updated {}'.format(genre.name)
        response = client.patch(genre_url.format(genre_uuid=str(genre.uuid)), {'name': new_name}, **request_args)
        assert response.status_code == 401


def test_partial_update_genre__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    genres = Genre.objects.all()
    for genre in genres:
        new_name = 'Updated {}'.format(genre.name)
        response = client.patch(genre_url.format(genre_uuid=str(genre.uuid)), {'name': new_name}, **request_args)
        assert response.status_code == 403


def test_partial_update_genre__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    genres = Genre.objects.all()
    for genre in genres:
        new_name = 'Updated {}'.format(genre.name)
        response = client.patch(genre_url.format(genre_uuid=str(genre.uuid)), {'name': new_name}, **request_args)
        assert response.status_code == 200
        assert response.json()['name'] != genre.name
        assert response.json()['name'] == new_name


def test_destroy_genre__unauthenticated(client):
    genres = Genre.objects.all()
    for genre in genres:
        response = client.delete(genre_url.format(genre_uuid=str(genre.uuid)))
        assert response.status_code == 401


def test_destroy_genre__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    genres = Genre.objects.all()
    for genre in genres:
        response = client.delete(genre_url.format(genre_uuid=str(genre.uuid)))
        assert response.status_code == 403


def test_destroy_genre__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    genres = Genre.objects.all()
    for genre in genres:
        response = client.delete(genre_url.format(genre_uuid=str(genre.uuid)))
        assert response.status_code == 204
    remaining_genres = Genre.objects.all()
    assert len(remaining_genres) == 0
