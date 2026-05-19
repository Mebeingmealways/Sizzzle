from conftest import auth_headers
from datetime import datetime, timedelta, timezone
from models import User, db


def test_login_customer_success(client):
    response = client.post('/api/auth/login', json={
        'email': 'customer@sizzzle.com',
        'password': 'customer123',
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['user']['role'] == 'customer'
    assert data.get('token')


def test_register_rejects_invalid_phone(client):
    response = client.post('/api/auth/register', json={
        'name': 'Invalid Phone User',
        'email': 'invalid-phone@example.com',
        'password': 'customer123',
        'phone': 'not-a-phone@example.com',
        'address': 'Test address',
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'Phone number must contain 7 to 15 digits' in data.get('error', '')


def test_register_cook_rejects_invalid_phone(client):
    response = client.post('/api/auth/register/cook', json={
        'name': 'Invalid Cook Phone',
        'email': 'invalid-cook-phone@example.com',
        'password': 'cook12345',
        'phone': 'cook-phone@example.com',
        'address': 'Test address',
        'aadhar_number': '123412341234',
        'bank_account': '123456789012',
        'ifsc_code': 'SBIN0001234',
        'pan_number': 'ABCDE1234F',
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'Phone number must contain 7 to 15 digits' in data.get('error', '')


def test_login_invalid_password(client):
    response = client.post('/api/auth/login', json={
        'email': 'customer@sizzzle.com',
        'password': 'wrong-password',
    })
    assert response.status_code == 401


def test_auth_me_returns_current_user(client, customer_token):
    response = client.get('/api/auth/me', headers=auth_headers(customer_token))
    assert response.status_code == 200
    data = response.get_json()
    assert data['email'] == 'customer@sizzzle.com'


def test_profile_get_returns_profile(client, customer_token):
    response = client.get('/api/profile', headers=auth_headers(customer_token))
    assert response.status_code == 200
    data = response.get_json()
    assert data['email'] == 'customer@sizzzle.com'


def test_profile_update_works(client, customer_token):
    response = client.put(
        '/api/profile',
        headers=auth_headers(customer_token),
        json={'name': 'Priya Updated', 'phone': '+91 99999 00000'},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Priya Updated'


def test_profile_notification_preferences_update(client, customer_token):
    response = client.put(
        '/api/profile',
        headers=auth_headers(customer_token),
        json={
            'notification_preferences': {
                'booking_confirmations': False,
                'cook_arrival_alerts': True,
                'promotional_offers': True
            }
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    prefs = data.get('notification_preferences', {})
    assert prefs['booking_confirmations'] is False
    assert prefs['cook_arrival_alerts'] is True
    assert prefs['promotional_offers'] is True


def test_taste_profile_update_and_get(client, customer_token):
    update = client.put(
        '/api/profile/taste',
        headers=auth_headers(customer_token),
        json={'dietary_preferences': ['Vegetarian'], 'allergies': ['Nuts'], 'spice_level': 2},
    )
    assert update.status_code == 200

    fetch = client.get('/api/profile/taste', headers=auth_headers(customer_token))
    assert fetch.status_code == 200
    taste = fetch.get_json()
    assert 'dietary_preferences' in taste


def test_kitchen_checklist_update_and_get(client, customer_token):
    update = client.put(
        '/api/profile/kitchen-checklist',
        headers=auth_headers(customer_token),
        json={'kitchen_equipment': ['Gas Stove', 'Microwave']},
    )
    assert update.status_code == 200

    fetch = client.get('/api/profile/kitchen-checklist', headers=auth_headers(customer_token))
    assert fetch.status_code == 200
    data = fetch.get_json()
    assert isinstance(data.get('kitchen_equipment', []), list)


def test_forgot_password_returns_generic_success(client):
    response = client.post('/api/auth/forgot-password', json={'email': 'customer@sizzzle.com'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data


def test_reset_password_with_valid_otp_works(client, app):
    with app.app_context():
        user = User.query.filter_by(email='customer@sizzzle.com').first()
        user.password_reset_code = '123456'
        user.password_reset_expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=5)
        db.session.commit()

    response = client.post('/api/auth/reset-password', json={
        'email': 'customer@sizzzle.com',
        'otp': '123456',
        'new_password': 'customer789',
    })
    assert response.status_code == 200

    login = client.post('/api/auth/login', json={
        'email': 'customer@sizzzle.com',
        'password': 'customer789',
    })
    assert login.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email='customer@sizzzle.com').first()
        user.set_password('customer123')
        db.session.commit()
