from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'username': 'testuser', 'email': 'testuser@example.com'}


def test_create_user_existent_username(client, mock_create_user):
    # print(mock_create_user.__dict__)
    response = client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'testuserqwe@example.com',
            'password': 'password123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Usuário com este username já existe'}


def test_create_user_existent_email(client, mock_create_user):
    # print(mock_create_user.__dict__)
    response = client.post(
        '/users/',
        json={
            'username': 'testuserqwe',
            'email': 'testuser@example.com',
            'password': 'password123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Usuário com este email já existe'}


def test_create_user_existent_username_and_email(client, mock_create_user):
    # print(mock_create_user.__dict__)
    response = client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Usuário com este email já existe username já existe'
    }


def test_get_all_users(client, mock_create_user, token):
    """
    Até implementar o fakedb para testes, este teste depende
    do teste de criação de usuário."""

    user_schema = UserPublic.model_validate(mock_create_user.__dict__).model_dump()

    response = client.get('/users/', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, mock_create_user, token):
    response = client.put(
        f'/users/{mock_create_user.id}',
        json={
            'username': 'updateduser',
            'email': 'updateduser@example.com',
            'password': 'newpassword123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    user_schema = UserPublic.model_validate(mock_create_user.__dict__).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_delete_user(client, mock_create_user, token):
    response = client.delete(
        f'/users/{mock_create_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Usuário deletado com sucesso'}


def test_get_user_by_id(client, mock_create_user):
    response = client.get(f'/users/{mock_create_user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'username': 'testuser', 'email': 'testuser@example.com'}


# Testando usuário não encontrado
def test_update_different_user(client, token):
    response = client.put(
        '/users/12',
        json={
            'username': 'updateduser',
            'email': 'updateduser@example.com',
            'password': 'newpassword123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para atualizar este usuário'
    }


def test_update_user_to_an_existing_username(client, mock_create_user, token):
    client.post(
        '/users/',
        json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
        },
    )

    response = client.put(
        f'/users/{mock_create_user.id}',
        json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Usuário com este username ou email já existe'}


def test_delete_different_user(client, token, other_user):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Você não tem permissão para atualizar este usuário'
    }


def test_delete_with_invalid_token(client):
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer invalid-token'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Não foi possível validar as credenciais'}


def test_get_user_by_id_not_found(client):
    response = client.get('/users/123')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}
