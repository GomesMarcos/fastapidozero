from http import HTTPStatus


async def test_root_must_return_200(async_client):
    response = await async_client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá, Mundo!'}


async def test_root_html_must_return_an_html_response(async_client):
    response = await async_client.get('/html')

    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'] == 'text/html; charset=utf-8'
    assert response.text == '<h1>Olá, Mundo!</h1>'
