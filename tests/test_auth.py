from http import HTTPStatus


def test_token(client, mock_create_user):
    response = client.post(
        '/auth/token',
        data={
            'username': 'testuser@example.com',
            'password': mock_create_user.plain_password,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'Bearer'
    assert response.json()['expires_in'] is None


def test_token_invalid_credentials(client):
    response = client.post(
        '/auth/token',
        data={
            'username': 'invaliduser@example.com',
            'password': 'wrongpassword',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Credenciais inválidas'}
