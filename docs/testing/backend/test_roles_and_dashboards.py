from conftest import auth_headers


def test_list_cooks_public(client):
    response = client.get('/api/cooks')
    assert response.status_code == 200
    cooks = response.get_json()
    assert isinstance(cooks, list)


def test_cook_jobs_and_earnings(client, cook_token):
    jobs = client.get('/api/cooks/jobs', headers=auth_headers(cook_token))
    assert jobs.status_code == 200

    earnings = client.get('/api/cooks/earnings', headers=auth_headers(cook_token))
    assert earnings.status_code == 200
    data = earnings.get_json()
    assert 'total_earned' in data


def test_update_cook_location(client, cook_token):
    response = client.post(
        '/api/cooks/location',
        headers=auth_headers(cook_token),
        json={'latitude': 19.12, 'longitude': 72.88},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['latitude'] == 19.12


def test_manager_verification_and_complaints(client, manager_token):
    pending = client.get('/api/manager/verifications/pending', headers=auth_headers(manager_token))
    assert pending.status_code == 200

    complaints = client.get('/api/manager/complaints', headers=auth_headers(manager_token))
    assert complaints.status_code == 200


def test_admin_stats_analytics_and_policies(client, admin_token):
    stats = client.get('/api/admin/stats', headers=auth_headers(admin_token))
    assert stats.status_code == 200
    assert 'total_users' in stats.get_json()

    analytics = client.get('/api/admin/analytics', headers=auth_headers(admin_token))
    assert analytics.status_code == 200
    assert 'total_bookings' in analytics.get_json()

    policies = client.get('/api/admin/policies', headers=auth_headers(admin_token))
    assert policies.status_code == 200


def test_admin_disputes_endpoint(client, admin_token):
    disputes = client.get('/api/admin/disputes', headers=auth_headers(admin_token))
    assert disputes.status_code == 200
