import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app, fake_db
from fast_zero.schemas import UserDb


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_create_user():
    # Limpa a fake_db antes do teste
    fake_db.clear()

    # Cria o user e insere em fake_db
    user = UserDb(
        id=1,
        username='testuser',
        email='testuser@example.com',
        password='password123',
    )
    fake_db.append(user)

    yield user
    # Limpa a fake_db após o teste
    fake_db.clear()
