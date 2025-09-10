from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123',
    }
    user = User(**user_data)
    session.add(user)
    session.commit()

    query = session.scalar(
        select(User).where(User.email == 'testuser@example.com')
    )

    assert query.id == 1
    assert query.username == user_data['username']
    assert query.email == user_data['email']
    assert query.password == user_data['password']
    assert query.created_at is not None
