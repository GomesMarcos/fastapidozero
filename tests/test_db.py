from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(User) as time:
        user_data = {
            'username': 'testuser',
            'email': 'testuserqwe@example.com',
            'password': 'password123',
        }
        new_user = User(**user_data)
        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.email == 'testuserqwe@example.com'),
        )

    assert asdict(user) == {
        'id': 1,
        'username': 'testuser',
        'email': 'testuserqwe@example.com',
        'password': 'password123',
        'created_at': time,
        'updated_at': time,
    }
