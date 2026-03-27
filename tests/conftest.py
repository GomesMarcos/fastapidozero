from contextlib import contextmanager
from datetime import datetime
from typing import AsyncIterator

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash
from fast_zero.settings import Settings


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.sequence(lambda n: f'Test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username} qwe')


@pytest.fixture
def client(session: AsyncSession):
    """Test client que usa a sessão de banco criada pelo fixture `session`."""

    def get_session_override():
        return session

    # sobrescreve a dependência antes de criar o TestClient
    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    # limpa as overrides depois dos testes
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def mock_create_user(session: AsyncSession):
    """Cria um usuário no banco de testes."""

    PASSWORD = 'password123'

    user = User(
        username='testuser',
        email='testuser@example.com',
        password=get_password_hash(PASSWORD),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.plain_password = PASSWORD  # type: ignore

    yield user

    # Limpa o usuário após o teste
    await session.delete(user)
    await session.commit()
    await session.flush()
    await session.close()


@pytest_asyncio.fixture
async def other_user(session: AsyncSession):
    """Cria um usuário no banco de testes utilizando UserFactory"""

    user = UserFactory()
    session.add(user)
    await session.commit()
    await session.refresh(user)

    yield user

    # Limpa o usuário após o teste
    await session.delete(user)
    await session.commit()
    await session.flush()
    await session.close()


@pytest_asyncio.fixture
async def session():
    # Banco de testes em memória
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


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


@pytest.fixture
def token(client, mock_create_user):
    response = client.post(
        '/auth/token',
        data={
            'username': mock_create_user.email,
            'password': mock_create_user.plain_password,  # type: ignore
        },
    )

    return response.json()['access_token']


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
async def async_client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Test client assíncrono que usa a sessão de banco criada pelo fixture `session`."""

    async def get_session_override():
        return session

    # sobrescreve a dependência antes de criar o AsyncClient
    app.dependency_overrides[get_session] = get_session_override

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url='http://test') as client:
        yield client

    # limpa as overrides depois dos testes
    app.dependency_overrides.clear()
