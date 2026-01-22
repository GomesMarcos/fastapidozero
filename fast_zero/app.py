from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from fast_zero.database import get_session
from fast_zero.models import User

from .schemas import (
    Message,
    UserList,
    UserNotFound,
    UserPublic,
    UserSchema,
)

app = FastAPI(title='FastAPI do Zero', version='0.1.0')


@app.get('/', response_model=Message, status_code=HTTPStatus.OK)
def read_root():
    return Message(message='Olá, Mundo!')


@app.get('/html', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_html():
    return '<h1>Olá, Mundo!</h1>'


@app.post(
    '/users/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
    responses={HTTPStatus.CONFLICT: {'model': Message}},
)
def create_user(user: UserSchema, session=Depends(get_session)):
    db_user = session.scalar(
        select(User).where((User.email == user.email) | (User.username == user.username))
    )

    if db_user is not None:
        error_message = 'Usuário com este'
        if db_user.email == user.email:
            error_message += ' email já existe'
        if db_user.username == user.username:
            error_message += ' username já existe'
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=error_message,
        )

    db_user = User(**user.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def get_users(session=Depends(get_session), limit: int = 10, offset: int = 0):
    users = session.scalars(select(User).limit(limit).offset(offset)).all()
    return {'users': users}


@app.get(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={HTTPStatus.NOT_FOUND: {'model': UserNotFound}},
)
def get_user_by_id(user_id: int, session=Depends(get_session)):
    user = session.scalar(select(User).where(User.id == user_id))
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
def update_user(user_id: int, user: UserSchema, session=Depends(get_session)):
    existing_user = session.scalar(select(User).where(User.id == user_id))
    if existing_user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )

    # atualiza os campos do modelo SQLAlchemy com os dados do schema
    for field, value in user.model_dump().items():
        setattr(existing_user, field, value)

    session.commit()
    session.refresh(existing_user)
    return existing_user


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={HTTPStatus.NOT_FOUND: {'model': UserNotFound}},
)
def delete_user(user_id: int, session=Depends(get_session)):
    existing_user = session.scalar(select(User).where(User.id == user_id))
    if existing_user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )
    session.delete(existing_user)
    session.commit()
    return {'message': 'Usuário deletado com sucesso'}
