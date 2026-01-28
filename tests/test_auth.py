from http import HTTPStatus


async def test_token(async_client, mock_create_user):
    response = await async_client.post(
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


async def test_token_invalid_credentials(async_client):
    response = await async_client.post(
        '/auth/token',
        data={
            'username': 'invaliduser@example.com',
            'password': 'wrongpassword',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Credenciais inválidas'}
