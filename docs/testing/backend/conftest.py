import pytest

from bootstrap_data import seed
from app import create_app


@pytest.fixture(scope='session')
def app():
    seed()
    test_app = create_app()
    test_app.config.update(TESTING=True)
    return test_app


@pytest.fixture
def client(app):
    return app.test_client()


def login_and_get_token(client, email, password):
    response = client.post('/api/auth/login', json={'email': email, 'password': password})
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    return data['token']


@pytest.fixture
def customer_token(client):
    return login_and_get_token(client, 'customer@sizzzle.com', 'customer123')


@pytest.fixture
def cook_token(client):
    return login_and_get_token(client, 'cook@sizzzle.com', 'cook123')


@pytest.fixture
def manager_token(client):
    return login_and_get_token(client, 'manager@sizzzle.com', 'manager123')


@pytest.fixture
def admin_token(client):
    return login_and_get_token(client, 'admin@sizzzle.com', 'admin123')


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}
