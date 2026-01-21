from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(User) as time:
        user_data = {
            'username': 'testuser',
            'email': 'testuserqwe@example.com',
            'password': 'password123',
        }
        user = User(**user_data)
        session.add(user)
        session.commit()

        query = session.scalar(
            select(User).where(User.email == 'testuserqwe@example.com'),
        )

        assert asdict(query) == {
            'id': 1,
            'username': 'testuser',
            'email': 'testuserqwe@example.com',
            'password': 'password123',
            'created_at': time,
            'updated_at': time,
        }
