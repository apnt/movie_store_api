import pytest
from common.tests import data

auth_url = '/iam/auth/'
users_url = '/iam/users/'
user_url = '/iam/users/{user_uuid}/'

# post/patch default arguments
request_args = {'content_type': 'application/json'}

# mark all tests as needing database access
pytestmark = pytest.mark.django_db


# ----- users tests -----
def test_list_users__unauthenticated(client):
    response = client.get(users_url)
    assert response.status_code == 401


def test_list_users__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    response = client.get(users_url)
    assert response.status_code == 403


def test_list_users__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    response = client.get(users_url)
    assert response.status_code == 200


def test_retrieve_user__unauthenticated(client):
    response = client.get(user_url.format(user_uuid=data.user1_uuid))
    assert response.status_code == 401


def test_retrieve_user__user(client):
    client.post(auth_url, data.user1_credentials, **request_args)
    response = client.get(user_url.format(user_uuid=data.user1_uuid))
    assert response.status_code == 403


def test_retrieve_user__admin(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    response = client.get(user_url.format(user_uuid=data.user1_uuid))
    assert response.status_code == 200
