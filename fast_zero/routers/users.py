from typing import Annotated

from sqlalchemy.orm import Session as SessionOrm

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.routers import (
    APIRouter,
    Depends,
    HTTPException,
    HTTPStatus,
    IntegrityError,
    Query,
    select,
)
from fast_zero.schemas import (
    FilterPage,
    Message,
    UserList,
    UserNotFound,
    UserPublic,
    UserSchema,
)
from fast_zero.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])
Session = Annotated[SessionOrm, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
FilterPageDep = Annotated[FilterPage, Query()]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
    responses={HTTPStatus.CONFLICT: {'model': Message}},
)
def create_user(user: UserSchema, session: Session):
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


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def get_users(
    session: Session,
    current_user: CurrentUser,
    filter_page: FilterPageDep,
):
    users = session.scalars(
        select(User).limit(filter_page.limit).offset(filter_page.offset)
    ).all()
    return {'users': users}


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={HTTPStatus.NOT_FOUND: {'model': UserNotFound}},
)
def get_user_by_id(user_id: int, session: Session):
    user = session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )
    return user


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={HTTPStatus.NOT_FOUND: {'model': UserNotFound}},
)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
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


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
    responses={HTTPStatus.NOT_FOUND: {'model': UserNotFound}},
)
def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Você não tem permissão para atualizar este usuário',
        )
    session.delete(current_user)
    session.commit()
    return {'message': 'Usuário deletado com sucesso'}
