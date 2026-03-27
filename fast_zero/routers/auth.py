# fast_zero/routers/auth.py
from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.routers import (
    APIRouter,
    Depends,
    HTTPException,
    HTTPStatus,
    select,
)
from fast_zero.schemas import Token
from fast_zero.security import create_access_token, get_current_user, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])
T_Session = Annotated[AsyncSession, Depends(get_session)]
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
T_User = Annotated[User, Depends(get_current_user)]


@router.post('/token', response_model=Token)
async def get_access_token(
    form_data: T_OAuth2Form,
    session: T_Session,
):
    user = await session.scalar(select(User).where(User.email == form_data.username))

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Credenciais inválidas',
        )

    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.post('/refresh_token', response_model=Token)
async def refresh_access_token(user: T_User):
    new_access_token = create_access_token(data={'sub': user.email})

    return Token(access_token=new_access_token, token_type='bearer')
