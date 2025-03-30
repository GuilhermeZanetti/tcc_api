from pydantic import Field
from judge.contrib.schemas import Model
from judge.auth.models import UserType


class UserIn(Model):
    username: str = Field(title="Username")
    password: str = Field(title="Password")


class UserOut(Model):
    id: str = Field(title="User ID")
    username: str = Field(title="Username")
    user_type: UserType = Field(title="User Type")


class TokenResponse(Model):
    access_token: str = Field(title="Access Token")
    token_type: str = Field(default="bearer", title="Token Type")
