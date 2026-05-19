from datetime import date, timedelta

from conftest import auth_headers


def test_list_customer_bookings(client, customer_token):
    response = client.get('/api/bookings', headers=auth_headers(customer_token))
    assert response.status_code == 200
    bookings = response.get_json()
    assert isinstance(bookings, list)
    assert len(bookings) >= 1


def test_create_booking_success(client, customer_token):
    booking_date = (date.today() + timedelta(days=2)).isoformat()
    response = client.post(
        '/api/bookings',
        headers=auth_headers(customer_token),
        json={
            'cook_id': 1,
            'date': booking_date,
            'time_slot': '18:30',
            'num_people': 4,
            'tier': 'premium',
            'total_amount': 2500,
            'dish_ids': [1, 2],
        },
    )
    assert response.status_code == 201
    booking = response.get_json()
    assert booking['cook_id'] == 1
    assert booking['tier'] == 'premium'


def test_create_booking_missing_required_fields(client, customer_token):
    response = client.post('/api/bookings', headers=auth_headers(customer_token), json={'tier': 'standard'})
    assert response.status_code == 400


def test_verify_otp_invalid_value(client, cook_token):
    response = client.post('/api/bookings/1/verify-otp', headers=auth_headers(cook_token), json={'otp': '0000'})
    assert response.status_code == 400


def test_start_and_end_service(client, cook_token):
    start = client.post('/api/bookings/1/start', headers=auth_headers(cook_token))
    assert start.status_code == 200
    assert start.get_json()['status'] == 'in_progress'

    end = client.post('/api/bookings/1/end', headers=auth_headers(cook_token))
    assert end.status_code == 200
    assert end.get_json()['status'] == 'completed'


def test_rate_booking_success(client, customer_token):
    # Booking 3 is seeded as completed and belongs to the seeded customer.
    rate = client.post(
        '/api/bookings/3/rate',
        headers=auth_headers(customer_token),
        json={'rating': 5, 'comment': 'Excellent service'},
    )
    assert rate.status_code == 201
    data = rate.get_json()
    assert data['rating'] == 5


def test_get_cook_location(client, customer_token):
    client.patch(
        '/api/bookings/2/status',
        headers=auth_headers(customer_token),
        json={'status': 'accepted'},
    )
    response = client.get('/api/bookings/2/cook-location', headers=auth_headers(customer_token))
    assert response.status_code == 200
    data = response.get_json()
    assert 'latitude' in data
    assert 'longitude' in data


def test_cancel_booking_returns_charge_field(client, customer_token):
    response = client.post('/api/bookings/2/cancel', headers=auth_headers(customer_token))
    assert response.status_code == 200
    data = response.get_json()
    assert 'cancellation_charge' in data
