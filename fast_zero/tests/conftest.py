import pytest
from fastapi.testclient import TestClient

from fast_zero.app import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_get_user(monkeypatch):
    class MockUser:
        id = 1
        username = 'testuser'

    def fake_get_user_by_id(user_id):
        return MockUser() if user_id == 1 else None

    # Mockando retorno de get_user_by_id
    monkeypatch.setattr('fast_zero.app.get_user_by_id', fake_get_user_by_id)
