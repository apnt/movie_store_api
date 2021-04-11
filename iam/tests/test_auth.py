import pytest
from common.tests import data

auth_url = '/iam/auth/'

# post/patch default arguments
request_args = {'content_type': 'application/json'}

# mark all tests as needing database access
pytestmark = pytest.mark.django_db


# ----- auth tests -----
def test_login__invalid_credentials(client):
    response = client.post(auth_url, data.invalid_credentials, **request_args)
    assert response.status_code == 401


def test_login__valid_credentials(client):
    response = client.post(auth_url, data.admin_credentials, **request_args)
    assert response.status_code == 200


def test_refresh__unauthenticated(client):
    response = client.patch(auth_url)
    assert response.status_code == 401


def test_refresh__logged_in(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    response = client.patch(auth_url)
    assert response.status_code == 200


def test_logout__unauthenticated(client):
    response = client.delete(auth_url)
    assert response.status_code == 200


def test_logout__logged_in(client):
    client.post(auth_url, data.admin_credentials, **request_args)
    response = client.delete(auth_url)
    assert response.status_code == 200
