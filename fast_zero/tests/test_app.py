from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_root_must_return_200():
    client = TestClient(app)
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá, Mundo!'}


def test_root_html_must_return_an_html_response():
    client = TestClient(app)
    response = client.get('/html')

    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'] == 'text/html; charset=utf-8'
    assert response.text == '<h1>Olá, Mundo!</h1>'
