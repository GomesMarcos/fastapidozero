from http import HTTPStatus

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse

from .schemas import (
    Message,
    UserDb,
    UserList,
    UserNotFound,
    UserPublic,
    UserSchema,
)

app = FastAPI(title='FastAPI do Zero', version='0.1.0')

fake_db = []


@app.get('/', response_model=Message, status_code=HTTPStatus.OK)
def read_root():
    return Message(message='Olá, Mundo!')


@app.get('/html', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_html():
    return '<h1>Olá, Mundo!</h1>'


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    user_with_id = UserDb(**user.model_dump(), id=len(fake_db) + 1)
    fake_db.append(user_with_id)
    return user_with_id


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def get_all_users():
    return {'users': fake_db}


@app.get(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={HTTPStatus.NOT_FOUND: {'model': UserNotFound}},
)
def get_user_by_id(user_id: int):
    user = next((user for user in fake_db if user.id == user_id), None)
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )
    return user


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={HTTPStatus.NOT_FOUND: {'model': UserNotFound}},
)
def update_user(user_id: int, user: UserSchema):
    existing_user = next(
        (user for user in fake_db if user.id == user_id), None
    )
    if existing_user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )
    updated_user = existing_user.copy(update=user.model_dump())
    fake_db[fake_db.index(existing_user)] = updated_user
    return updated_user


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={HTTPStatus.NOT_FOUND: {'model': UserNotFound}},
)
def delete_user(user_id: int):
    existing_user = next(
        (user for user in fake_db if user.id == user_id), None
    )
    if existing_user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )
    fake_db.remove(existing_user)
    return {'message': f'Usuário {existing_user.id} deletado com sucesso'}
