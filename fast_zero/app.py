from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_zero.routers import auth, users
from fast_zero.schemas import Message

app = FastAPI(title='FastAPI do Zero', version='0.1.0')
app.include_router(auth.router)
app.include_router(users.router)


@app.get('/', response_model=Message, status_code=HTTPStatus.OK)
def read_root():
    return Message(message='Olá, Mundo!')


@app.get('/html', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_html():
    return '<h1>Olá, Mundo!</h1>'
