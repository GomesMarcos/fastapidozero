from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_root_must_return_200(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá, Mundo!'}


def test_root_html_must_return_an_html_response(client):
    response = client.get('/html')

    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'] == 'text/html; charset=utf-8'
    assert response.text == '<h1>Olá, Mundo!</h1>'


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


def test_get_all_users(client, mock_create_user):
    """
    Até implementar o fakedb para testes, este teste depende
    do teste de criação de usuário."""

    user_schema = UserPublic.model_validate(mock_create_user.__dict__).model_dump()

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, mock_create_user):
    response = client.put(
        '/users/1',
        json={
            'username': 'updateduser',
            'email': 'updateduser@example.com',
            'password': 'newpassword123',
        },
    )
    user_schema = UserPublic.model_validate(mock_create_user.__dict__).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_delete_user(client, mock_create_user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Usuário deletado com sucesso'}


def test_get_user_by_id(client, mock_create_user):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'username': 'testuser', 'email': 'testuser@example.com'}


# Testando usuário não encontrado
def test_update_user_not_found(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'updateduser',
            'email': 'updateduser@example.com',
            'password': 'newpassword123',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}


def test_update_user_to_an_existing_username(client, mock_create_user):
    client.post(
        '/users/',
        json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
        },
    )

    response = client.put(
        '/users/1',
        json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Usuário com este username ou email já existe'}


def test_delete_user_not_found(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}


def test_get_user_by_id_not_found(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}
