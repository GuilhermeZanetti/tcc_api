from pydantic import UUID4, BaseModel, Field
from judge.contrib.models.base import BaseModelMixin
from judge.contrib.schemas import Model
from judge.auth.models import UserType


class UserIn(BaseModel):
    username: str = Field(title="Username")
    password: str = Field(title="Password")


class UserOut(BaseModel):
    id: UUID4 = Field(title="User ID")
    username: str = Field(title="Username")
    user_type: UserType = Field(title="User Type")


class TokenResponse(BaseModelMixin):
    access_token: str = Field(title="Access Token")
    token_type: str = Field(default="bearer", title="Token Type")
