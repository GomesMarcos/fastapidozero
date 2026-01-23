from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode
from jwt import encode as encode_jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.settings import Settings

settings = Settings()

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def get_password_hash(password: str):
    """Generate a secure hash for a plain text password.

    This function uses the recommended password hashing configuration to
    produce a hash that can be safely stored and later used for verification.

    Args:
        password: The plain text password to be hashed.

    Returns:
        A string containing the hashed representation of the password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """Verify that a plain text password matches a stored hash.

    This function compares a user-provided password against a hashed
    password to determine if they represent the same secret.

    Args:
        plain_password: The plain text password provided for verification.
        hashed_password: The previously stored hashed password.

    Returns:
        True if the plain password matches the hashed password, otherwise False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode['exp'] = expire

    return encode_jwt(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credential_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Não foi possível validar as credenciais',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        if not (subject_email := payload.get('sub')):
            raise credential_exception
    except DecodeError as e:
        raise credential_exception from e

    if user := session.scalar(select(User).where(User.email == subject_email)):
        return user

    raise credential_exception
