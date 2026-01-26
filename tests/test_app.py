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
