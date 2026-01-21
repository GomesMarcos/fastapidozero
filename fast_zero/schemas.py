from pydantic import BaseModel, ConfigDict, EmailStr, PositiveInt


class Message(BaseModel):
    message: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserSchema(UserPublic):
    password: str


class UserDb(UserSchema):
    """Temporário"""

    id: PositiveInt


class UserList(BaseModel):
    users: list[UserPublic]


class UserNotFound(BaseModel):
    detail: str = 'Usuário não encontrado'
