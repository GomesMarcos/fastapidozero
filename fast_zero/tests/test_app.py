from http import HTTPStatus


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
    assert response.json() == {'id': 1, 'username': 'testuser'}


def test_get_all_users(client):
    """
    Até implementar o fakedb para testes, este teste depende
    do teste de criação de usuário."""

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [{'id': 1, 'username': 'testuser'}]}


def test_update_user(client, mock_create_user):
    response = client.put(
        '/users/1',
        json={
            'username': 'updateduser',
            'email': 'updateduser@example.com',
            'password': 'newpassword123',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 'username': 'updateduser'}


def test_delete_user(client, mock_create_user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Usuário 1 deletado com sucesso'}


def test_get_user_by_id(client, mock_create_user):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': 1, 'username': 'testuser'}


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


def test_delete_user_not_found(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}


def test_get_user_by_id_not_found(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado'}
