from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, PositiveInt


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


class Token(BaseModel):
    access_token: str
    token_type: str = 'Bearer'
    expires_in: Optional[int] = None


class FilterPage(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, default=10)
