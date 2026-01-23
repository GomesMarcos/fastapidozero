from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

from .schemas import (
    Message,
    Token,
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

    user_data = user.model_dump()
    user_data['password'] = get_password_hash(user_data['password'])

    db_user = User(**user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def get_users(
    session=Depends(get_session),
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
):
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
def update_user(
    user_id: int,
    user: UserSchema,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Você não tem permissão para atualizar este usuário',
        )
    try:
        # atualiza os campos do modelo SQLAlchemy com os dados do schema
        user_data = user.model_dump()
        if 'password' in user_data and user_data['password'] is not None:
            user_data['password'] = get_password_hash(user_data['password'])

        for field, value in user_data.items():
            setattr(current_user, field, value)

        session.commit()
        session.refresh(current_user)
        return current_user
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Usuário com este username ou email já existe',
        ) from e


@app.delete(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={HTTPStatus.NOT_FOUND: {'model': UserNotFound}},
)
def delete_user(
    user_id: int,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Você não tem permissão para atualizar este usuário',
        )
    session.delete(current_user)
    session.commit()
    return {'message': 'Usuário deletado com sucesso'}


@app.post('/token', response_model=Token)
def get_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Credenciais inválidas',
        )

    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'Bearer'}
