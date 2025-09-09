from pydantic import BaseModel, EmailStr, PositiveInt


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: PositiveInt
    username: str


class UserDb(UserSchema):
    """Temporário"""

    id: PositiveInt


class UserList(BaseModel):
    users: list[UserPublic]


class UserNotFound(BaseModel):
    detail: str = 'Usuário não encontrado'
