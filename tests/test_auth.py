from http import HTTPStatus

from freezegun import freeze_time


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


async def test_token_expired_after_time(async_client, mock_create_user):
    # Generating token
    with freeze_time('2023-07-14 12:00'):
        response = await async_client.post(
            '/auth/token',
            data={
                'username': 'testuser@example.com',
                'password': mock_create_user.plain_password,
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    # Assert expired token
    with freeze_time('2023-07-14 12:40'):
        update_response = await async_client.put(
            f'/users/{mock_create_user.id}',
            headers={'Authorization': f'Bearer {token}'},
            data={
                'username': 'testuser@example.com',
                'password': mock_create_user.plain_password,
            },
        )
        assert update_response.status_code == HTTPStatus.UNAUTHORIZED
        assert update_response.json() == {
            'detail': 'Token expirado. Realize login novamente.'
        }


async def test_cant_refresh_token_expired(async_client, mock_create_user):
    # Generating token
    with freeze_time('2023-07-14 12:00'):
        response = await async_client.post(
            '/auth/token',
            data={
                'username': 'testuser@example.com',
                'password': mock_create_user.plain_password,
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    # Assert expired token
    with freeze_time('2023-07-14 12:40'):
        update_response = await async_client.put(
            f'/users/{mock_create_user.id}',
            headers={'Authorization': f'Bearer {token}'},
            data={
                'username': 'testuser@example.com',
                'password': mock_create_user.plain_password,
            },
        )
        assert update_response.status_code == HTTPStatus.UNAUTHORIZED
        assert update_response.json() == {
            'detail': 'Token expirado. Realize login novamente.'
        }

        new_token_response = await async_client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )
        data = new_token_response.json()
        assert data == {'detail': 'Token expirado. Realize login novamente.'}


async def test_refresh_token_expired_after_time(async_client, mock_create_user):
    # Generating token
    with freeze_time('2023-07-14 12:00'):
        response = await async_client.post(
            '/auth/token',
            data={
                'username': 'testuser@example.com',
                'password': mock_create_user.plain_password,
            },
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    # Assert expired token
    with freeze_time('2023-07-14 12:28'):
        new_token_response = await async_client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        data = new_token_response.json()

        new_token_response == HTTPStatus.OK
        assert 'access_token' in data
        assert 'token_type' in data
        assert data['token_type'] == 'bearer'


async def test_token_wrong_psw(session, mock_create_user, async_client):
    response = await async_client.post(
        '/auth/token',
        data={
            'username': mock_create_user.email,
            'password': 'qwe',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Credenciais inválidas'
