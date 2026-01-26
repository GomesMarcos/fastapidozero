from http import HTTPStatus

import pytest
from fastapi import HTTPException
from jwt import decode

from fast_zero.security import create_access_token, get_current_user


def test_jwt(settings):
    data = {'test': 'test'}
    token = create_access_token(data)
    decoded = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded['test'] == 'test'
    assert 'exp' in decoded


def test_user_not_found_exception(session):
    data = {'test': 'test', 'sub': 'None@qwe.x'}
    token = create_access_token(data)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session, token)

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc_info.value.detail == 'Não foi possível validar as credenciais'


def test_token_without_sub(session):
    data = {'test': 'test'}
    token = create_access_token(data)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session, token)

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc_info.value.detail == 'Não foi possível validar as credenciais'
