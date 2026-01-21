from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry

# from fast_zero.schemas import UserDb


@pytest.fixture
def client(session):
    """Test client que usa a sessão de banco criada pelo fixture `session`."""

    def get_session_override():
        return session

    # sobrescreve a dependência antes de criar o TestClient
    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    # limpa as overrides depois dos testes
    app.dependency_overrides.clear()


# @pytest.fixture
# def mock_create_user():
#     # Limpa a fake_db antes do teste
#     fake_db.clear()

#     # Cria o user e insere em fake_db
#     user = UserDb(
#         id=1,
#         username='testuser',
#         email='testuser@example.com',
#         password='password123',
#     )
#     fake_db.append(user)

#     yield user
#     # Limpa a fake_db após o teste
#     fake_db.clear()


@pytest.fixture
def session():
    # Banco de testes em memória
    engine = create_engine('sqlite:///:memory:')

    # Garante que TODAS as tabelas mapeadas (incluindo users) são criadas
    table_registry.metadata.create_all(engine)
    with Session(autocommit=False, autoflush=False, bind=engine) as session:
        yield session

    # Limpa as tabelas após os testes
    table_registry.metadata.drop_all(engine)


@contextmanager
def _mock_db_time(model, time=datetime(2026, 1, 20, 12, 0, 0)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
